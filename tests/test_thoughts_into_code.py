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


# ---------------------------------------------------------------------------
# Task 3: Stream-of-Thought Control Flow & Natural Guards Tests (Pillar B)
# ---------------------------------------------------------------------------

def test_conversational_loops_and_conditions():
    source = """
queue = [1, 2, 3]
emptied = []
as long as queue is not empty:
    val = queue.pop(0)
    add val to emptied

collected = []
for every x in [10, 20]:
    add x to collected

for each and every y in [30, 40]:
    add y to collected

balance = -15
status = ""
in case balance is negative:
    status = "overdrawn"
in the worst case:
    status = "ok"

attempts = 4
flagged = False
if it turns out that attempts > 3:
    flagged = True
"""
    env = execute(source)
    assert env["emptied"] == [1, 2, 3]
    assert env["collected"] == [10, 20, 30, 40]
    assert env["status"] == "overdrawn"
    assert env["flagged"] is True


def test_conversational_guards_and_try():
    source = """
age = 20
make sure that age >= 18 otherwise "Too young"

captured_err = ""
try to:
    zero_div = 10 / 0
if it goes wrong as problem:
    captured_err = "handled"
"""
    env = execute(source)
    assert env["captured_err"] == "handled"


# ---------------------------------------------------------------------------
# Task 4: Thought Queries & Intuitive Filtering Tests (Pillar C)
# ---------------------------------------------------------------------------

def test_thought_filtering_keep_and_discard():
    source = """
numbers = [10, 25, 5, 80, 42]
keep only numbers where x >= 20 into high_nums
discard from numbers where x < 20 into filtered_high
"""
    env = execute(source)
    assert env["high_nums"] == [25, 80, 42]
    assert env["filtered_high"] == [25, 80, 42]


def test_thought_find_first_and_check():
    source = """
scores = [45, 78, 92, 88, 99]
find first in scores where x > 90 into top_score

score = 95
check whether score >= 90 into is_honors

blacklist = ["192.168.1.1", "10.0.0.1"]
target_ip = "10.0.0.1"
check if blacklist contains target_ip into is_blocked
"""
    env = execute(source)
    assert env["top_score"] == 92
    assert env["is_honors"] is True
    assert env["is_blocked"] is True


# ---------------------------------------------------------------------------
# Task 5: Interrogative Inquiries & Collaborative Outputs Tests (Pillar D)
# ---------------------------------------------------------------------------

def test_interrogative_questions_and_output(capsys):
    source = """
scores = [10, 20, 30]
what is 15 percent of 200
what is the average of scores
tell me "All good"
show me scores
"""
    env = execute(source)
    captured = capsys.readouterr().out
    assert "30.0" in captured
    assert "20.0" in captured
    assert "All good" in captured
    assert "[10, 20, 30]" in captured


def test_conversational_inquiries_into_variables():
    source = """
orders = ["order1", "order2", "order3"]
how many items in orders into total_orders

catalog = ["SKU-01", "SKU-99", "SKU-42"]
does catalog contain "SKU-99" into has_item
does catalog contain "SKU-00" into missing_item
"""
    env = execute(source)
    assert env["total_orders"] == 3
    assert env["has_item"] is True
    assert env["missing_item"] is False




