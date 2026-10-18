"""
DoomScript Interactive Kernel & Cell Runner
Provides Jupyter Kernel support and interactive cell execution with captured stdout/stderr.
"""

import sys
import io
import contextlib
from typing import Dict, Any, Tuple
from doomscript.compiler.engine import execute


import textwrap

def run_cell(code: str, env: Dict[str, Any] = None) -> Tuple[str, Dict[str, Any]]:
    """
    Executes a cell of DoomScript code within a persistent environment dict,
    capturing standard output. Returns (captured_output, updated_env).
    """
    if env is None:
        env = {}

    clean_code = textwrap.dedent(code).strip()
    stdout_buf = io.StringIO()
    with contextlib.redirect_stdout(stdout_buf):
        execute(clean_code, custom_globals=env)

    return stdout_buf.getvalue(), env


try:
    from ipykernel.kernelbase import Kernel

    class DoomScriptKernel(Kernel):
        """Jupyter Kernel for executing DoomScript (.doom) code interactively."""
        implementation = "DoomScript"
        implementation_version = "0.6.0"
        language = "doom"
        language_version = "0.6.0"
        language_info = {
            "name": "doom",
            "mimetype": "text/x-doomscript",
            "file_extension": ".doom"
        }
        banner = "DoomScript - The English-First Programming Language"

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.session_env = {}

        def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
            if not code.strip():
                return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}

            try:
                output, self.session_env = run_cell(code, env=self.session_env)
                if not silent and output:
                    self.send_response(self.iopub_socket, "stream", {"name": "stdout", "text": output})
                return {"status": "ok", "execution_count": self.execution_count, "payload": [], "user_expressions": {}}
            except Exception as e:
                err_msg = f"{type(e).__name__}: {e}\n"
                if not silent:
                    self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": err_msg})
                return {"status": "error", "execution_count": self.execution_count, "ename": type(e).__name__, "evalue": str(e), "traceback": [err_msg]}

except ImportError:
    # ipykernel is optional
    DoomScriptKernel = None


def is_block_continuation_needed(code: str) -> bool:
    """
    Determines whether interactive REPL needs additional lines to complete a block.
    Checks unclosed braces, brackets, block keywords (if, for each, to, repeat, try).
    """
    lines = [l for l in code.splitlines() if l.strip()]
    if not lines:
        return False

    last_line = lines[-1].strip()
    # If ends with colon
    if last_line.endswith(":"):
        return True

    # Check unclosed quotes or brackets
    brackets = {"(": 0, "[": 0, "{": 0}
    in_str = None
    for char in code:
        if char in ('"', "'") and in_str is None:
            in_str = char
        elif char == in_str:
            in_str = None
        elif in_str is None:
            if char in ("(", "[", "{"):
                brackets[char] += 1
            elif char == ")" and brackets["("] > 0:
                brackets["("] -= 1
            elif char == "]" and brackets["["] > 0:
                brackets["["] -= 1
            elif char == "}" and brackets["{"] > 0:
                brackets["{"] -= 1

    if in_str is not None or any(v > 0 for v in brackets.values()):
        return True

    # If starts with a block header keyword and has no dedented closing line
    block_starters = ("if ", "unless ", "repeat ", "for each ", "to ", "try", "attempt")
    if any(last_line.startswith(bs) for bs in block_starters):
        return True

    return False
