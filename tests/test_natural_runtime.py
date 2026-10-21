"""
Tests for Phase 1 Runtime Integrity:
- Safe possessive field access avoiding Python dict method collisions (items, keys, values)
- Reentrant compilation_context preserving domain activations and specs
- Active-domain isolation preventing 2,600+ domain exports from polluting execution globals
"""

import pytest
import textwrap
from doomscript.compiler.engine import execute, compile_to_ast
from doomscript.domains.registry import get_domain_registry
from doomscript.runtime import get_field
from doomscript.core.record import Record


def test_possessive_field_access_dict_methods():
    """Possessive access on a Record with fields named 'items' or 'keys' returns data, not methods."""
    code = textwrap.dedent("""
    player = {"name": "Hero", "items": ["sword", "shield"], "keys": [101, 102]}
    player_items = player's items
    player_keys = player's keys
    """).strip()
    env = execute(code)
    assert env["player_items"] == ["sword", "shield"]
    assert env["player_keys"] == [101, 102]


def test_get_field_fallback_to_object_attributes():
    """get_field returns field if present in dict, else falls back to object attribute."""
    rec = Record({"items": [1, 2, 3]})
    assert get_field(rec, "items") == [1, 2, 3]
    # 'keys' is not in dict, so falls back to dict.keys method
    assert callable(get_field(rec, "keys"))


def test_reentrant_compilation_context():
    """compilation_context is reentrant: inner calls do not wipe outer state or active domains."""
    reg = get_domain_registry()
    with reg.compilation_context() as outer:
        reg.activate("data")
        assert reg.is_active("data")
        with reg.compilation_context() as inner:
            assert inner is outer
            assert reg.is_active("data")
        # Exiting inner context did not wipe active domains
        assert reg.is_active("data")
    # Exiting outer resets
    assert not reg.is_active("data")


def test_no_global_domain_export_pollution():
    """Basic scripts without 'use' statements do not have unactivated domain internals injected."""
    code = "x = 42"
    env = execute(code)
    assert "x" in env
    assert env["x"] == 42
    # Inactive domain internal exports must not be present
    assert "AudioSaveSpec" not in env
    assert "RoboticsASTExporter" not in env
    assert "FinanceRuntime" not in env

