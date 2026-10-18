"""
Phase 7 Tests: Capability Benchmark and Standalone Python Exporter
Tests 'doom export <file.doom> -o <file.py>', runs the exported script with Python,
and verifies identical behavior and 40/40 coursework capability benchmark execution.
"""

import sys
import subprocess
from pathlib import Path
import pytest
from typer.testing import CliRunner
from doomscript.cli import app
from doomscript.compiler.engine import export_to_python, execute

runner = CliRunner()


def test_export_to_python_api(tmp_path):
    """export_to_python emits runnable Python with runtime imports."""
    source = (
        "items = [1, 2, 3, 4, 5]\n"
        "m = mean(items)\n"
        "say \"Mean:\", m\n"
    )
    py_code = export_to_python(source)
    assert "from doomscript.runtime import *" in py_code
    assert "mean" in py_code

    py_file = tmp_path / "test_api_script.py"
    py_file.write_text(py_code, encoding="utf-8")

    # Run with standard python interpreter directly
    res = subprocess.run([sys.executable, str(py_file)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Mean: 3.0" in res.stdout or "Mean: 3" in res.stdout


def test_doom_export_cli(tmp_path):
    """doom export input.doom -o output.py creates an executable python script."""
    doom_file = tmp_path / "hello.doom"
    doom_file.write_text('names = ["Alice", "Bob", "Charlie"]\nfor each name in names:\n    say "Hello,", name\n', encoding="utf-8")

    py_file = tmp_path / "hello.py"
    result = runner.invoke(app, ["export", str(doom_file), "-o", str(py_file)])
    assert result.exit_code == 0
    assert py_file.exists()

    # Run exported Python script
    res = subprocess.run([sys.executable, str(py_file)], capture_output=True, text=True)
    assert res.returncode == 0
    assert "Hello, Alice" in res.stdout
    assert "Hello, Bob" in res.stdout
    assert "Hello, Charlie" in res.stdout


def test_capability_benchmarks_exist():
    """Verify all 40 coursework benchmark programs exist across 4 categories."""
    base_dir = Path(__file__).resolve().parent / "capability"
    assert base_dir.exists(), "tests/capability directory must exist"

    categories = ["cs1", "cs2", "datascience", "ml_math"]
    for cat in categories:
        cat_dir = base_dir / cat
        assert cat_dir.exists(), f"tests/capability/{cat} directory must exist"
        doom_files = list(cat_dir.glob("*.doom"))
        assert len(doom_files) == 10, f"Expected 10 benchmark programs in {cat}, found {len(doom_files)}"


def test_capability_runner_executes_all():
    """Run capability test runner script and verify 100% pass rate."""
    import run_capability
    results = run_capability.run_all_benchmarks()
    assert results["total"] == 40
    assert results["passed"] == 40
    assert results["pass_rate"] == 100.0
