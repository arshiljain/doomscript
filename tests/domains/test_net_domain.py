"""Unit and integration tests for the Web & API Automation domain pack (use net)."""

import http.server
import json
import socketserver
import threading
import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.net.spec import ApiWorkflowSpec, RequestStep


class MockAPIHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/orders":
            payload = json.dumps([{"id": 101, "item": "DoomBook", "price": 49.99}]).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress logging to keep test output clean


@pytest.fixture(scope="module")
def mock_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), MockAPIHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


def test_api_spec_validation():
    spec = ApiWorkflowSpec(name="test_api", base_url="https://api.example.com", timeout=10.0, retries=3)
    assert len(spec.validate()) == 0

    bad_spec = ApiWorkflowSpec(name="", timeout=-1.0, retries=-2)
    assert len(bad_spec.validate()) == 3


def test_net_single_line_request_and_json_parsing(mock_server):
    source = f"""use net

request GET "{mock_server}/orders" into resp
parse resp as JSON into orders
inspect response resp into info
"""
    env = execute(source)
    assert "resp" in env
    resp = env["resp"]
    assert resp.status_code == 200
    assert resp.ok is True

    assert "orders" in env
    orders = env["orders"]
    assert len(orders) == 1
    assert orders[0]["id"] == 101
    assert orders[0]["item"] == "DoomBook"

    assert "info" in env
    info = env["info"]
    assert info["status_code"] == 200
    assert "application/json" in info["content_type"]


def test_net_api_block_workflow(mock_server):
    source = f"""use net

api "orders_client":
    base_url: "{mock_server}"
    timeout: 5 seconds
    retries: 2 times
    get "/orders" into order_resp
    parse order_resp as JSON into order_data
"""
    env = execute(source)
    assert "orders_client" in env
    assert "order_data" in env
    data = env["order_data"]
    assert len(data) == 1
    assert data[0]["item"] == "DoomBook"


def test_net_ast_export():
    source = """use net

api "client":
    base_url: "https://api.example.com"
    timeout: 5
    get "/items" into r
    parse r as JSON into items
"""
    py_code = export_to_python(source)
    assert "urllib.request" in py_code or "urlopen" in py_code
    assert "items" in py_code
