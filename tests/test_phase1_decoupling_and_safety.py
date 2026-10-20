"""Regression tests for Phase 1: Decoupling Record and Exporter Safety."""

import pytest
from doomscript.core.record import Record as CoreRecord
from doomscript.runtime import Record as RuntimeRecord
from doomscript.exceptions import DoomCompilationError, DoomCompilerWarning
from doomscript.compiler.engine import export_to_python


def test_record_identity_and_leaf_import():
    """Verify that Record is imported from leaf core module and re-exported seamlessly."""
    assert CoreRecord is RuntimeRecord
    r = CoreRecord(name="Alice", score=100)
    assert r.name == "Alice"
    assert r["score"] == 100
    r.nested = {"level": 2}
    assert isinstance(r.nested, CoreRecord)
    assert r.nested.level == 2


def test_export_to_python_raises_compilation_error_on_fatal_failure(monkeypatch):
    """Verify that AST exporter failures raise DoomCompilationError instead of silent swallowing."""
    import doomscript.domains.exporter as dom_exporter

    def broken_transform(py_ast):
        raise ValueError("Simulated AST transformation corruption")

    monkeypatch.setattr(dom_exporter, "transform_domains_ast", broken_transform)

    with pytest.raises(DoomCompilationError, match="Domain AST export transformation failed"):
        export_to_python("x = 10")
