"""
Exhaustive test suite for DoomScript Thought-to-Code: All 4 Cognitive Phases.
Covers:
- Phase 1: Deep Discourse Memory & Set Quantifiers
- Phase 2: Contextual Attribute Scope, Relative Clauses & Superlatives
- Phase 3: Declarative Resilience & Compound Action Chaining
- Phase 4: Conversational Set Reshaping, Statistical Introspection & Analytics
"""

import pytest


# ---------------------------------------------------------------------------
# Phase 1, Task 1.1: Runtime Quantifier Helpers
# ---------------------------------------------------------------------------

def test_runtime_quantifiers():
    from doomscript.runtime import ds_every, ds_any, ds_none, ds_at_least_n

    numbers = [2, 4, 6, 8]
    assert ds_every(numbers, lambda x: x % 2 == 0) is True
    assert ds_every(numbers, lambda x: x > 5) is False
    assert ds_every([], lambda x: False) is True  # Vacuous truth on empty sets

    assert ds_any(numbers, lambda x: x > 5) is True
    assert ds_any(numbers, lambda x: x > 100) is False
    assert ds_any([], lambda x: True) is False

    assert ds_none(numbers, lambda x: x < 0) is True
    assert ds_none(numbers, lambda x: x == 4) is False

    assert ds_at_least_n(numbers, 2, lambda x: x >= 6) is True
    assert ds_at_least_n(numbers, 3, lambda x: x >= 6) is False
    assert ds_at_least_n([], 0, lambda x: True) is True


# ---------------------------------------------------------------------------
# Phase 1, Task 1.2: Dual-Referent Discourse Memory
# ---------------------------------------------------------------------------

def test_scope_tracker_dual_referents():
    from doomscript.grammar.phrases import ScopeTracker

    tracker = ScopeTracker()
    assert tracker.get_last_singular() is None
    assert tracker.get_last_plural() is None

    tracker.record_singular('client')
    assert tracker.get_last_singular() == 'client'

    tracker.record_plural('orders')
    assert tracker.get_last_plural() == 'orders'
    assert tracker.get_last_singular() == 'client'  # Preserved

    # Nested block inherits
    tracker.update_indent(4)
    assert tracker.get_last_singular() == 'client'
    assert tracker.get_last_plural() == 'orders'

    tracker.update_indent(0)
    assert tracker.get_last_singular() == 'client'
    assert tracker.get_last_plural() == 'orders'


# ---------------------------------------------------------------------------
# Phase 1, Task 1.3: Natural Pronoun Resolution
# ---------------------------------------------------------------------------

def test_singular_and_plural_pronoun_resolution():
    from doomscript.compiler.engine import execute

    code = """
a Customer has name, balance
create a Customer with name "Alice", balance 150 into client

if its balance > 100:
    client_status = "preferred"

orders = ["Laptop", "Mouse"]
say their count
collected = []
for each item in them:
    add item to collected
"""
    env = execute(code)
    assert env["client_status"] == "preferred"
    assert env["collected"] == ["Laptop", "Mouse"]
