"""
DoomScript Language Server Protocol (LSP) Server
Implements standard Language Server Protocol (LSP v3.16) over stdio.
Zero external dependencies (pure Python standard library).
Provides real-time syntax diagnostics, context-aware completions,
hover explanations, and go-to-definition.
"""

import sys
import json
import re
from typing import Dict, Any, List, Optional
from doomscript.compiler.engine import compile_to_ast
from doomscript.errors import translate_lark_error, find_closest_phrasings
from doomscript.explainer import explain_source
from doomscript.errors import CANONICAL_TEMPLATES


class DoomLanguageServer:
    def __init__(self, in_stream=None, out_stream=None):
        self.in_stream = in_stream or sys.stdin.buffer
        self.out_stream = out_stream or sys.stdout.buffer
        self.documents: Dict[str, str] = {}
        self.running = True

    def read_message(self) -> Optional[Dict[str, Any]]:
        """Reads a JSON-RPC message with Content-Length header from stdio."""
        content_length = None
        while True:
            line = self.in_stream.readline()
            if not line:
                return None
            line_str = line.decode("latin1").strip()
            if not line_str:
                break
            if line_str.lower().startswith("content-length:"):
                parts = line_str.split(":", 1)
                content_length = int(parts[1].strip())

        if content_length is None:
            return None

        body = self.in_stream.read(content_length)
        if not body:
            return None
        return json.loads(body.decode("utf-8"))

    def send_message(self, message: Dict[str, Any]):
        """Encodes and writes a JSON-RPC response with Content-Length header."""
        body = json.dumps(message, ensure_ascii=False).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("latin1")
        self.out_stream.write(header + body)
        self.out_stream.flush()

    def send_response(self, req_id: Any, result: Any):
        self.send_message({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        })

    def send_notification(self, method: str, params: Any):
        self.send_message({
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        })

    def run(self):
        """Main server event loop."""
        while self.running:
            try:
                msg = self.read_message()
                if msg is None:
                    break
                self.handle_message(msg)
            except Exception as e:
                # Log to stderr and keep server running
                sys.stderr.write(f"[DoomLSP Error] {e}\n")
                sys.stderr.flush()

    def handle_message(self, msg: Dict[str, Any]):
        method = msg.get("method")
        req_id = msg.get("id")
        params = msg.get("params", {})

        if method == "initialize":
            self.handle_initialize(req_id, params)
        elif method == "initialized":
            pass
        elif method == "shutdown":
            self.send_response(req_id, None)
        elif method == "exit":
            self.running = False
        elif method == "textDocument/didOpen":
            doc = params.get("textDocument", {})
            uri = doc.get("uri")
            text = doc.get("text", "")
            self.documents[uri] = text
            self.validate_document(uri, text)
        elif method == "textDocument/didChange":
            doc = params.get("textDocument", {})
            uri = doc.get("uri")
            changes = params.get("contentChanges", [])
            if changes:
                text = changes[-1].get("text", "")
                self.documents[uri] = text
                self.validate_document(uri, text)
        elif method == "textDocument/didClose":
            uri = params.get("textDocument", {}).get("uri")
            self.documents.pop(uri, None)
        elif method == "textDocument/hover":
            self.handle_hover(req_id, params)
        elif method == "textDocument/completion":
            self.handle_completion(req_id, params)
        elif method == "textDocument/definition":
            self.handle_definition(req_id, params)
        elif req_id is not None:
            # Unsupported request fallback
            self.send_response(req_id, None)

    def handle_initialize(self, req_id: Any, params: Dict[str, Any]):
        capabilities = {
            "textDocumentSync": 1,  # Full sync
            "hoverProvider": True,
            "completionProvider": {
                "resolveProvider": False,
                "triggerCharacters": [" ", ".", ":", "'"]
            },
            "definitionProvider": True
        }
        self.send_response(req_id, {
            "capabilities": capabilities,
            "serverInfo": {
                "name": "doomscript-lsp",
                "version": "0.6.0"
            }
        })

    def validate_document(self, uri: str, text: str):
        """Validates DoomScript syntax and publishes diagnostics."""
        diagnostics = []
        try:
            compile_to_ast(text)
        except Exception as e:
            line = getattr(e, "line", 1) - 1
            col = getattr(e, "column", 1) - 1
            line = max(0, line)
            col = max(0, col)

            lines = text.splitlines()
            source_line = lines[line] if 0 <= line < len(lines) else ""
            explanation, suggestion = translate_lark_error(e, source_line)
            if not suggestion and source_line.strip():
                closest = find_closest_phrasings(source_line, n=1)
                if closest:
                    suggestion = closest[0]

            msg = f"DoomScript: {explanation}"
            if suggestion:
                msg += f" (Did you mean: {suggestion}?)"

            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 1}
                },
                "severity": 1,  # Error
                "source": "doomscript",
                "message": msg
            })

        self.send_notification("textDocument/publishDiagnostics", {
            "uri": uri,
            "diagnostics": diagnostics
        })

    def handle_hover(self, req_id: Any, params: Dict[str, Any]):
        uri = params.get("textDocument", {}).get("uri")
        position = params.get("position", {})
        line_idx = position.get("line", 0)

        text = self.documents.get(uri, "")
        lines = text.splitlines()
        if not (0 <= line_idx < len(lines)):
            self.send_response(req_id, None)
            return

        target_line = lines[line_idx]
        if not target_line.strip() or target_line.strip().startswith("#"):
            self.send_response(req_id, None)
            return

        items = explain_source(target_line)
        if items and items[0]["is_code"]:
            item = items[0]
            markdown = (
                f"### DoomScript Explanation\n\n"
                f"**Meaning:** {item['explanation']}\n\n"
                f"**Transpiled Python:**\n```python\n{item['python']}\n```"
            )
            self.send_response(req_id, {
                "contents": {
                    "kind": "markdown",
                    "value": markdown
                }
            })
        else:
            self.send_response(req_id, None)

    def handle_completion(self, req_id: Any, params: Dict[str, Any]):
        uri = params.get("textDocument", {}).get("uri")
        position = params.get("position", {})
        text = self.documents.get(uri, "")
        lines = text.splitlines()
        line_idx = position.get("line", 0)
        curr_line = lines[line_idx] if 0 <= line_idx < len(lines) else ""

        items = []

        # 1. Canonical sentence completions
        for tmpl in CANONICAL_TEMPLATES[:25]:
            items.append({
                "label": tmpl,
                "kind": 15,  # Snippet
                "insertText": tmpl,
                "detail": "DoomScript English Template"
            })

        # 2. Extract defined functions in document
        func_matches = re.findall(r"^\s*to\s+([A-Za-z_]\w*)", text, re.MULTILINE)
        for fn in set(func_matches):
            items.append({
                "label": f"{fn}()",
                "kind": 3,  # Function
                "insertText": f"{fn}($0)",
                "detail": "User Defined Function"
            })

        # 3. Common keywords
        keywords = [
            "say", "set", "increase", "decrease", "repeat with", "repeat 5 times",
            "for each", "where", "if", "otherwise if", "otherwise", "unless",
            "read csv file", "write csv", "parse json", "convert to json",
            "combine", "extract text from html", "extract links from html",
            "now in", "next business day from", "today is weekend", "send email to"
        ]
        for kw in keywords:
            items.append({
                "label": kw,
                "kind": 14,  # Keyword
                "insertText": kw,
                "detail": "DoomScript Keyword"
            })

        self.send_response(req_id, {"isIncomplete": False, "items": items})

    def handle_definition(self, req_id: Any, params: Dict[str, Any]):
        uri = params.get("textDocument", {}).get("uri")
        position = params.get("position", {})
        text = self.documents.get(uri, "")
        lines = text.splitlines()
        line_idx = position.get("line", 0)
        char_idx = position.get("character", 0)

        if not (0 <= line_idx < len(lines)):
            self.send_response(req_id, None)
            return

        line = lines[line_idx]
        word_match = re.search(r"\b([A-Za-z_]\w*)\b", line[max(0, char_idx - 15) : min(len(line), char_idx + 15)])
        if not word_match:
            self.send_response(req_id, None)
            return

        target_word = word_match.group(1)
        # Search for 'to target_word'
        for idx, l in enumerate(lines):
            m = re.match(rf"^\s*to\s+{target_word}\b", l)
            if m:
                col = l.index(target_word)
                self.send_response(req_id, {
                    "uri": uri,
                    "range": {
                        "start": {"line": idx, "character": col},
                        "end": {"line": idx, "character": col + len(target_word)}
                    }
                })
                return

        self.send_response(req_id, None)


def start_lsp_server():
    """Starts the DoomScript Language Server over stdio."""
    server = DoomLanguageServer()
    server.run()
