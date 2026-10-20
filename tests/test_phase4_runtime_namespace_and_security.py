"""Regression tests for Phase 4: Runtime namespace pruning and clean execution environment."""

import types
import pytest
from doomscript.runtime import get_runtime_exports
from doomscript.compiler.engine import execute


def test_get_runtime_exports_contains_no_modules_or_typing():
    """Verify get_runtime_exports produces a curated API without leaked stdlib modules."""
    exports = get_runtime_exports()
    leaked_modules = [k for k, v in exports.items() if isinstance(v, types.ModuleType)]
    assert leaked_modules == [], f"Modules leaked in get_runtime_exports: {leaked_modules}"

    assert "Record" in exports
    assert "sleep" in exports
    assert "write_file" in exports
    assert "read_file" in exports
    assert "percent_of" in exports
    assert "explain" in exports


def test_execute_globals_pruning_and_no_module_leak():
    """Verify execute() globals contain only curated helpers and no raw stdlib modules (except built-in math)."""
    env = execute("val = 42")
    assert env["val"] == 42

    leaked = [k for k, v in env.items() if isinstance(v, types.ModuleType) and k != "math"]
    assert leaked == [], f"Modules leaked in execute() globals: {leaked}"


def test_script_variables_do_not_collide_with_stdlib_names():
    """Verify that user scripts can use common names like time, os, date without collision."""
    source = """time = 100
os = "solaris"
date = "2026-10-21"
result = time + 50
"""
    env = execute(source)
    assert env["time"] == 100
    assert env["os"] == "solaris"
    assert env["date"] == "2026-10-21"
    assert env["result"] == 150
