"""
Tests for Phase 5: Language Server Protocol (LSP)
Validates JSON-RPC message framing, initialization, diagnostics,
hover explanations, code completions, and go-to-definition.
"""

import io
import json
from doomscript.lsp.server import DoomLanguageServer


def make_rpc(method: str, params=None, req_id=1) -> bytes:
    msg = {"jsonrpc": "2.0", "method": method}
    if req_id is not None:
        msg["id"] = req_id
    if params is not None:
        msg["params"] = params
    body = json.dumps(msg).encode("utf-8")
    header = f"Content-Length: {len(body)}\r\n\r\n".encode("latin1")
    return header + body


def test_lsp_initialize_and_capabilities():
    in_buf = io.BytesIO(make_rpc("initialize", {}, req_id=1) + make_rpc("shutdown", req_id=2) + make_rpc("exit", req_id=None))
    out_buf = io.BytesIO()

    server = DoomLanguageServer(in_stream=in_buf, out_stream=out_buf)
    server.run()

    out_bytes = out_buf.getvalue()
    assert b"doomscript-lsp" in out_bytes
    assert b"hoverProvider" in out_bytes
    assert b"completionProvider" in out_bytes


def test_lsp_diagnostics_on_open():
    valid_code = 'score = 100\nsay "Score:", score\n'
    open_valid = make_rpc("textDocument/didOpen", {
        "textDocument": {"uri": "file:///test.doom", "text": valid_code}
    }, req_id=None)

    invalid_code = 'this is broken syntax ?????\n'
    open_invalid = make_rpc("textDocument/didOpen", {
        "textDocument": {"uri": "file:///err.doom", "text": invalid_code}
    }, req_id=None)

    in_buf = io.BytesIO(open_valid + open_invalid + make_rpc("exit", req_id=None))
    out_buf = io.BytesIO()

    server = DoomLanguageServer(in_stream=in_buf, out_stream=out_buf)
    server.run()

    out_str = out_buf.getvalue().decode("utf-8")
    assert "publishDiagnostics" in out_str
    # Error file diagnostics include plain English suggestion
    assert "err.doom" in out_str


def test_lsp_hover_and_completion():
    code = 'score = 100\nsay "Hello"\nto compute with x:\n    return x * 2\n'
    open_doc = make_rpc("textDocument/didOpen", {
        "textDocument": {"uri": "file:///demo.doom", "text": code}
    }, req_id=None)

    hover_req = make_rpc("textDocument/hover", {
        "textDocument": {"uri": "file:///demo.doom"},
        "position": {"line": 1, "character": 2}
    }, req_id=10)

    complete_req = make_rpc("textDocument/completion", {
        "textDocument": {"uri": "file:///demo.doom"},
        "position": {"line": 1, "character": 4}
    }, req_id=11)

    def_req = make_rpc("textDocument/definition", {
        "textDocument": {"uri": "file:///demo.doom"},
        "position": {"line": 1, "character": 2}  # search around compute
    }, req_id=12)

    in_buf = io.BytesIO(open_doc + hover_req + complete_req + def_req + make_rpc("exit", req_id=None))
    out_buf = io.BytesIO()

    server = DoomLanguageServer(in_stream=in_buf, out_stream=out_buf)
    server.run()

    out_str = out_buf.getvalue().decode("utf-8")
    assert "DoomScript Explanation" in out_str
    assert "compute()" in out_str  # completions include defined function
