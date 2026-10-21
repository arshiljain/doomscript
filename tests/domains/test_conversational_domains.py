"""Unit tests for Track 1: Conversational Domain Vocabularies ("Talking to the Tools")."""

import http.server
import json
import socketserver
import threading
import pytest
from doomscript.compiler.engine import execute
from doomscript.core.record import Record


class ConversationalMockHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            payload = json.dumps({
                "status": "success",
                "data": {
                    "items": [
                        {"id": 101, "name": "Widget A", "price": 25.5},
                        {"id": 102, "name": "Widget B", "price": 40.0},
                    ],
                    "total": 2
                }
            }).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/submit":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            received_data = json.loads(body) if body else {}
            payload = json.dumps({
                "status": "ok",
                "received": received_data,
                "message": "Created successfully"
            }).encode("utf-8")
            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


@pytest.fixture(scope="module")
def mock_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), ConversationalMockHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


# ---------------------------------------------------------------------------
# Task 1: Web & APIs Conversational Tests
# ---------------------------------------------------------------------------

def test_web_conversational_get_request(mock_server):
    code = f"""
send a get request to "{mock_server}/data" and wait for response into res
extract json field "data.items" from res into items
extract json field "status" from res into st
"""
    env = execute(code)
    assert "res" in env
    assert env["res"]["status"] == 200
    assert "items" in env
    assert len(env["items"]) == 2
    assert env["items"][0]["name"] == "Widget A"
    assert env["st"] == "success"


def test_web_conversational_post_request(mock_server):
    code = f"""
payload = {{"item": "DoomBook", "qty": 3}}
send a post request to "{mock_server}/submit" with payload into res
extract json field "received.item" from res into item_name
"""
    env = execute(code)
    assert "res" in env
    assert env["res"]["status"] == 201
    assert env["item_name"] == "DoomBook"


def test_web_conversational_post_shorthand(mock_server):
    code = f"""
payload = {{"code": "XYZ"}}
post payload to "{mock_server}/submit" into res
extract json field "received.code" from res into code_val
"""
    env = execute(code)
    assert "res" in env
    assert env["res"]["status"] == 201
    assert env["code_val"] == "XYZ"


def test_extract_json_field_from_dict_and_string():
    code = """
raw = '{"user": {"profile": {"name": "Alice", "score": 98}}}'
extract json field "user.profile.name" from raw into user_name
extract field "user.profile.score" from raw into user_score
"""
    env = execute(code)
    assert env["user_name"] == "Alice"
    assert env["user_score"] == 98
