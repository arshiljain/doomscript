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
