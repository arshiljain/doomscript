"""
DoomScript Web Playground Server
Serves a responsive, zero-dependency browser IDE with live execution,
Python transpilation inspection, and line-by-line explanation.
"""

import http.server
import json
import os
import sys
import webbrowser
from io import StringIO
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from typing import Optional

PLAYGROUND_HTML_PATH = Path(__file__).parent.parent.parent / "playground" / "index.html"


class PlaygroundHandler(http.server.BaseHTTPRequestHandler):
    """Handles static assets and live DoomScript evaluation endpoints."""

    def log_message(self, format, *args):
        # Keep terminal clean
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            if PLAYGROUND_HTML_PATH.exists():
                content = PLAYGROUND_HTML_PATH.read_bytes()
            else:
                content = b"<h1>DoomScript Playground HTML not found.</h1>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        try:
            data = json.loads(body)
        except Exception:
            data = {"code": body}

        code = data.get("code", "")
        response_data = {}

        if self.path == "/api/run":
            from doomscript.compiler.engine import execute
            from doomscript.errors import translate_runtime_error, format_syntax_error

            out_buf = StringIO()
            err_buf = StringIO()
            error_message = None

            with redirect_stdout(out_buf), redirect_stderr(err_buf):
                try:
                    execute(code, filename="<playground>")
                except Exception as e:
                    from lark.exceptions import UnexpectedToken, UnexpectedCharacters, VisitError
                    from doomscript.exceptions import DoomError
                    if isinstance(e, (UnexpectedToken, UnexpectedCharacters, VisitError, DoomError)):
                        error_message = format_syntax_error(code, e, file_path="<playground>")
                    else:
                        error_message = f"Runtime Error: {translate_runtime_error(e)}"

            response_data = {
                "output": out_buf.getvalue(),
                "stderr": err_buf.getvalue(),
                "error": error_message,
                "ok": error_message is None
            }

        elif self.path == "/api/transpile":
            from doomscript.compiler.engine import transpile
            try:
                py_code = transpile(code)
                response_data = {"python": py_code, "ok": True}
            except Exception as e:
                response_data = {"python": "", "error": str(e), "ok": False}

        elif self.path == "/api/explain":
            from doomscript.explainer import explain_source
            try:
                steps = explain_source(code)
                response_data = {"steps": steps, "ok": True}
            except Exception as e:
                response_data = {"steps": [], "error": str(e), "ok": False}
        else:
            self.send_error(404, "Endpoint not found")
            return

        resp_bytes = json.dumps(response_data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(resp_bytes)))
        self.end_headers()
        self.wfile.write(resp_bytes)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def launch_playground(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    """Starts local HTTP server and opens web playground bound to 127.0.0.1 only."""
    server_address = (host, port)
    try:
        httpd = http.server.HTTPServer(server_address, PlaygroundHandler)
    except OSError:
        # Port in use, pick fallback port
        port = port + 1
        server_address = (host, port)
        httpd = http.server.HTTPServer(server_address, PlaygroundHandler)

    url = f"http://{host}:{port}"
    print(f"\n=======================================================")
    print(f" DoomScript Interactive Playground running at: {url}")
    print(f" Press Ctrl+C to stop.")
    print(f"=======================================================\n")

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping playground server.")
        httpd.server_close()
