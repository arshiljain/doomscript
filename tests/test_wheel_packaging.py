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
        dist_dir.mkdir(parents=True, exist_ok=True)
        # Attempt to build wheel automatically on fresh clones
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(dist_dir), str(repo_root)],
                capture_output=True,
                check=False,
            )
        except Exception:
            pass
        wheels = sorted(list(dist_dir.glob("*.whl")), key=lambda p: p.stat().st_mtime, reverse=True)

    if not wheels:
        pytest.skip("No wheel found in dist/ and unable to build wheel automatically in current environment.")
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

        # 4. Execute a real DoomScript program with domain operations inside the clean environment
        doom_prog = (
            "set a to 10\n"
            "set b to 20\n"
            "say 'Sum is:', a + b\n"
            "use geo\n"
            "point at 10.0, 20.0 into p1\n"
            "point at 10.0, 21.0 into p2\n"
            "distance between p1 and p2 in km into d\n"
            "use nlp\n"
            "clean text in 'Hello World from Isolated Venv' into c\n"
            "say c\n"
        )
        run_script = (
            "from doomscript.compiler.engine import execute\n"
            f"env = execute('''{doom_prog}''')\n"
            "assert 'p1' in env\n"
            "assert 'd' in env\n"
            "assert env['c'] == 'hello world from isolated venv'\n"
            "print('ISOLATED_DOMAINS_SUCCESS')\n"
        )
        res_exec = subprocess.run(
            [str(py_bin), "-c", run_script],
            capture_output=True,
            text=True,
            check=False,
        )
        assert res_exec.returncode == 0, f"Execution failed:\n{res_exec.stderr}"
        assert "Sum is: 30" in res_exec.stdout
        assert "ISOLATED_DOMAINS_SUCCESS" in res_exec.stdout

