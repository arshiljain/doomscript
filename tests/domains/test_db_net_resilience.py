"""Unit and integration tests for Database transactions/parameterized queries
and Network resilience (timeouts, retries, auth, mutating permission gates).
"""

import http.server
import json
import socketserver
import threading
import pytest
from doomscript.compiler.engine import execute
from doomscript.domains.db.runtime import get_db_runtime
from doomscript.domains.net.runtime import (
    set_mutating_requests_allowed,
    is_mutating_requests_allowed,
)


class ResilientMockHandler(http.server.BaseHTTPRequestHandler):
    attempts_seen = 0

    def do_GET(self):
        auth = self.headers.get("Authorization", "")
        if self.path == "/secure":
            if auth == "Bearer secret-token-123":
                payload = json.dumps({"status": "authorized"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_response(401)
                self.end_headers()
        elif self.path == "/flaky":
            ResilientMockHandler.attempts_seen += 1
            if ResilientMockHandler.attempts_seen < 3:
                self.send_response(500)
                self.end_headers()
            else:
                payload = json.dumps({"recovered": True}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        self.send_response(201)
        self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def resilient_server():
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", 0), ResilientMockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def test_parameterized_db_query_and_transaction():
    source = """use db

execute sql "CREATE TABLE accounts (name TEXT, balance INTEGER)"
execute sql "INSERT INTO accounts VALUES ('Alice', 100)"
execute sql "INSERT INTO accounts VALUES ('Bob', 50)"

query db "SELECT * FROM accounts WHERE balance >= ?" with [80] into high_bal

# Successful transaction
transaction db:
    execute sql "UPDATE accounts SET balance = balance - 20 WHERE name = 'Alice'"
    execute sql "UPDATE accounts SET balance = balance + 20 WHERE name = 'Bob'"

query db "SELECT balance FROM accounts WHERE name = 'Alice'" into alice_res
query db "SELECT balance FROM accounts WHERE name = 'Bob'" into bob_res
"""
    env = execute(source)
    assert len(env["high_bal"]) == 1
    assert env["high_bal"][0]["name"] == "Alice"
    assert env["alice_res"][0]["balance"] == 80
    assert env["bob_res"][0]["balance"] == 70


def test_db_transaction_rollback_on_error():
    source = """use db

execute sql "CREATE TABLE safe_table (id INTEGER PRIMARY KEY, val TEXT)"
execute sql "INSERT INTO safe_table VALUES (1, 'initial')"

try:
    transaction db:
        execute sql "UPDATE safe_table SET val = 'changed' WHERE id = 1"
        execute sql "INSERT INTO safe_table VALUES (1, 'conflict')"
if it fails:
    err_caught = true

query db "SELECT val FROM safe_table WHERE id = 1" into check_res
"""
    env = execute(source)
    assert env["check_res"][0]["val"] == "initial"


def test_net_timeout_retries_and_bearer_auth(resilient_server):
    ResilientMockHandler.attempts_seen = 0
    source = f"""use net

request GET "{resilient_server}/secure" with timeout 5 seconds with bearer token "secret-token-123" into secure_resp
parse secure_resp as JSON into secure_data

request GET "{resilient_server}/flaky" with timeout 5 seconds retry 3 times into flaky_resp
parse flaky_resp as JSON into flaky_data
"""
    env = execute(source)
    assert env["secure_resp"].status_code == 200
    assert env["secure_data"]["status"] == "authorized"
    assert env["flaky_resp"].status_code == 200
    assert env["flaky_data"]["recovered"] is True


def test_net_mutating_permission_boundary(resilient_server):
    set_mutating_requests_allowed(False)
    try:
        source = f"""use net

request POST "{resilient_server}/orders" into post_resp
"""
        with pytest.raises(PermissionError, match="Mutating HTTP request POST is blocked"):
            execute(source)
    finally:
        set_mutating_requests_allowed(True)


def test_db_net_export_parity():
    from doomscript.compiler.engine import export_to_python

    db_src = """use db

query users into adult_users:
    select name, age
    where age is over 18
"""
    py_db = export_to_python(db_src)
    assert "sqlite3" in py_db
    assert "SELECT name, age FROM users" in py_db

    net_src = """use net

api "orders_client":
    base_url: "https://api.example.com"
    timeout: 5
    request GET "/orders" into orders
"""
    py_net = export_to_python(net_src)
    assert "urllib" in py_net
    assert "https://api.example.com/orders" in py_net
