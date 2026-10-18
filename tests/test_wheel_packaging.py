"""End-to-end test verifying wheel build, package data inclusion, and isolated venv execution."""

import os
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
import pytest


def test_wheel_contains_grammar_and_executes_in_clean_venv():
    repo_root = Path(__file__).parent.parent
    dist_dir = repo_root / "dist"
    wheels = sorted(list(dist_dir.glob("*.whl")), key=lambda p: p.stat().st_mtime, reverse=True)
    if not wheels:
        pytest.fail("No wheel found in dist/ directory. Run 'python -m build --wheel' first.")
    wheel_path = wheels[0]

    with tempfile.TemporaryDirectory() as tmp_dir:
        env_dir = Path(tmp_dir) / "test_venv"
        # 1. Create clean isolated virtualenv
        venv.create(env_dir, with_pip=True)

        if sys.platform == "win32":
            py_bin = env_dir / "Scripts" / "python.exe"
            pip_bin = env_dir / "Scripts" / "pip.exe"
        else:
            py_bin = env_dir / "bin" / "python"
            pip_bin = env_dir / "bin" / "pip"

        # 2. Install the wheel into clean isolated environment
        res_install = subprocess.run(
            [str(pip_bin), "install", str(wheel_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        assert res_install.returncode == 0, f"pip install failed:\n{res_install.stderr}"

        # 3. Verify that doom.lark was installed inside site-packages
        check_script = (
            "import doomscript, pathlib; "
            "p = pathlib.Path(doomscript.__file__).parent / 'grammar' / 'doom.lark'; "
            "assert p.exists(), f'Grammar file missing at {p}'; "
            "print('GRAMMAR_EXISTS')"
        )
        res_check = subprocess.run(
            [str(py_bin), "-c", check_script],
            capture_output=True,
            text=True,
            check=False,
        )
        assert res_check.returncode == 0, f"Grammar check failed:\n{res_check.stderr}"
        assert "GRAMMAR_EXISTS" in res_check.stdout

        # 4. Execute a real DoomScript program inside the clean environment
        doom_prog = (
            "set a to 10\n"
            "set b to 20\n"
            "say 'Sum is:', a + b\n"
        )
        run_script = (
            "from doomscript.compiler.engine import execute\n"
            f"execute('''{doom_prog}''')\n"
        )
        res_exec = subprocess.run(
            [str(py_bin), "-c", run_script],
            capture_output=True,
            text=True,
            check=False,
        )
        assert res_exec.returncode == 0, f"Execution failed:\n{res_exec.stderr}"
        assert "Sum is: 30" in res_exec.stdout
