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


# ---------------------------------------------------------------------------
# Task 2: Conversational Hypotheses & Intent-Driven Definitions Tests (Pillar A)
# ---------------------------------------------------------------------------

def test_conversational_hypotheses():
    source = """
suppose total is 500
assume rate is 0.05
let's say discount is 10 percent of total
remember total - discount as net_total
"""
    env = execute(source)
    assert env["total"] == 500
    assert env["rate"] == 0.05
    assert env["discount"] == 50.0
    assert env["net_total"] == 450.0


def test_intentional_goal_definitions():
    source = """
how to calculate_tax with price, rate:
    return price * rate

in order to find_hypotenuse with a, b:
    return square root of (a squared + b squared)

the goal is to double_val with x:
    return x * 2

tax = calculate_tax(100, 0.15)
hyp = find_hypotenuse(3, 4)
db = double_val(21)
"""
    env = execute(source)
    assert env["tax"] == 15.0
    assert env["hyp"] == 5.0
    assert env["db"] == 42

