"""
Tests for DoomScript Stream-of-Thought Programming (Thoughts into Code).
Covers:
- Task 1: ds_find_first runtime helper
- Task 2: Conversational hypotheses and intentional definitions (Pillar A)
- Task 3: Stream-of-thought control flow and natural guards (Pillar B)
- Task 4: Thought queries and intuitive filtering (Pillar C)
- Task 5: Interrogative questions and collaborative output (Pillar D)
"""

import pytest
from doomscript.compiler.engine import execute


# ---------------------------------------------------------------------------
# Task 1: ds_find_first Runtime Helper Tests
# ---------------------------------------------------------------------------

def test_find_first_runtime_helper():
    from doomscript.runtime import ds_find_first

    items = [
        {"name": "Alice", "age": 16},
        {"name": "Bob", "age": 22},
        {"name": "Charlie", "age": 25},
    ]

    found = ds_find_first(items, lambda u: u["age"] >= 18)
    assert found == {"name": "Bob", "age": 22}

    not_found = ds_find_first(items, lambda u: u["age"] > 50)
    assert not_found is None
