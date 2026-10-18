"""
Tests for Phase 0: Safety and Spec Integrity
- Playground binds to 127.0.0.1 only
- Subprocess run_command uses shell=False by default (no shell injection)
- Explicit 'using shell' activates shell mode
"""

import sys
import subprocess
import pytest
from doomscript.compiler.engine import execute
from doomscript.playground import launch_playground, PlaygroundHandler


def test_playground_binds_to_localhost_only(monkeypatch):
    """Assert that the playground server binds exclusively to 127.0.0.1 and not all interfaces."""
    bound_addresses = []

    class DummyServer:
        def __init__(self, server_address, RequestHandlerClass):
            bound_addresses.append(server_address)
            self.server_address = server_address

        def serve_forever(self):
            pass

        def server_close(self):
            pass

    import http.server
    monkeypatch.setattr(http.server, "HTTPServer", DummyServer)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    launch_playground(port=8123, open_browser=False)

    assert len(bound_addresses) >= 1
    host, port = bound_addresses[0]
    assert host == "127.0.0.1", f"Expected binding to '127.0.0.1', found '{host}'"
    assert port == 8123


def test_run_command_shell_false_by_default_metacharacters():
    """Verify that shell metacharacters in arguments are NOT interpreted by a shell by default."""
    # Running python to echo argv[1]; if shell=False, the semicolon is an argument, not a command separator.
    code = f'''
run command '{sys.executable} -c "import sys; print(sys.argv[1])" "hello; world"' into output
'''
    env = execute(code)
    # The output should literally contain 'hello; world', NOT fail or split into a second command
    assert env["output"] == "hello; world"


def test_run_command_explicit_using_shell():
    """Verify that 'run command ... using shell' explicitly enables shell execution."""
    if sys.platform == "win32":
        code = 'run command "echo shell_active" using shell into output'
    else:
        code = 'run command "echo shell_active" using shell into output'
    env = execute(code)
    assert "shell_active" in env["output"]
