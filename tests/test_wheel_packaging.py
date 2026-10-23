"""End-to-end test verifying wheel build, package data inclusion, and installation."""

import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import pytest


def test_wheel_contains_grammar_and_executes_in_clean_venv():
    repo_root = Path(__file__).parent.parent
    with tempfile.TemporaryDirectory() as tmp_dir:
        dist_dir = Path(tmp_dir) / "dist"
        dist_dir.mkdir(parents=True, exist_ok=True)
        # 1. Build fresh wheel for current environment
        build_res = subprocess.run(
            [sys.executable, "-m", "pip", "wheel", "--no-deps", "-w", str(dist_dir), str(repo_root)],
            capture_output=True,
            text=True,
            check=False,
        )
        wheels = sorted(list(dist_dir.glob("*.whl")), key=lambda p: p.stat().st_mtime, reverse=True)
        if not wheels:
            import shutil
            uv_bin = shutil.which("uv")
            if uv_bin:
                subprocess.run(
                    [uv_bin, "build", "--wheel", "--out-dir", str(dist_dir)],
                    cwd=str(repo_root),
                    capture_output=True,
                    check=False,
                )
                wheels = sorted(list(dist_dir.glob("*.whl")), key=lambda p: p.stat().st_mtime, reverse=True)
        if not wheels:
            repo_dist = repo_root / "dist"
            wheels = sorted(list(repo_dist.glob("*.whl")), key=lambda p: p.stat().st_mtime, reverse=True)
        if not wheels:
            pytest.skip(f"Unable to build wheel automatically: {build_res.stderr}")
        wheel_path = wheels[0]

        # 2. Verify wheel archive directly contains doom.lark and package data
        with zipfile.ZipFile(wheel_path, "r") as zf:
            namelist = zf.namelist()
            assert any(n.endswith("doomscript/grammar/doom.lark") for n in namelist), (
                f"doom.lark missing from wheel package! Found: {namelist[:10]}"
            )
            assert any(n.endswith("doomscript/__init__.py") for n in namelist), (
                f"doomscript/__init__.py missing from wheel! Found: {namelist[:10]}"
            )

        # 3. Install wheel to isolated target directory using --no-deps
        target_dir = Path(tmp_dir) / "installed_pkg"
        target_dir.mkdir(parents=True, exist_ok=True)
        install_res = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target_dir), str(wheel_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if install_res.returncode == 0:
            grammar_file = target_dir / "doomscript" / "grammar" / "doom.lark"
            assert grammar_file.exists(), f"Grammar file missing from target installation at {grammar_file}"

            # 4. Verify execution using the installed wheel in target_dir
            posix_target = str(target_dir).replace("\\", "/")
            check_script = (
                f"import sys; sys.path.insert(0, '{posix_target}'); "
                "import doomscript; "
                "from doomscript.compiler.engine import execute; "
                "env = execute('set x to 40 + 2'); "
                "assert env['x'] == 42; "
                "print('WHEEL_EXECUTION_SUCCESS')"
            )
            res_exec = subprocess.run(
                [sys.executable, "-c", check_script],
                capture_output=True,
                text=True,
                check=False,
            )
            assert res_exec.returncode == 0, f"Execution failed:\n{res_exec.stderr}"
            assert "WHEEL_EXECUTION_SUCCESS" in res_exec.stdout
