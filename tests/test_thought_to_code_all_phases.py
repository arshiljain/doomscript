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


# ---------------------------------------------------------------------------
# Phase 1, Task 1.4: Universal, Existential & Negative Set Quantifiers
# ---------------------------------------------------------------------------

def test_set_quantifiers_execution():
    from doomscript.compiler.engine import execute

    code = """
numbers = [2, 4, 6, 8]
all_even = False
if all numbers are even:
    all_even = True

all_positive = False
if every n in numbers is positive:
    all_positive = True

mixed = [1, 2, 3]
has_odd = False
if any n in mixed is odd:
    has_odd = True

clean_list = [10, 20, 30]
no_negatives = False
if no x in clean_list is negative:
    no_negatives = True
"""
    env = execute(code)
    assert env["all_even"] is True
    assert env["all_positive"] is True
    assert env["has_odd"] is True
    assert env["no_negatives"] is True


# ---------------------------------------------------------------------------
# Phase 2, Task 2.1: Runtime Attribute & Superlatives
# ---------------------------------------------------------------------------

def test_runtime_attr_and_superlatives():
    from doomscript.runtime import ds_attr, ds_find_superlative

    d = {"price": 100}
    class Item: price = 200
    assert ds_attr(d, "price") == 100
    assert ds_attr(Item(), "price") == 200
    assert ds_attr(d, "missing", default=0) == 0

    catalog = [
        {"name": "Widget A", "price": 20},
        {"name": "Widget B", "price": 50},
        {"name": "Widget C", "price": 10},
    ]
    cheapest = ds_find_superlative(catalog, order="min", key="price")
    assert cheapest["name"] == "Widget C"

    largest = ds_find_superlative(catalog, order="max", key="price")
    assert largest["name"] == "Widget B"


# ---------------------------------------------------------------------------
# Phase 2, Task 2.2: Contextual Attribute Binding in Thought Queries
# ---------------------------------------------------------------------------

def test_contextual_attribute_query():
    from doomscript.compiler.engine import execute

    code = """
orders = [
    {"id": 1, "price": 50},
    {"id": 2, "price": 150},
    {"id": 3, "price": 250}
]
keep only orders where price > 100 into expensive_orders
discard from orders where price >= 200 into affordable_orders
"""
    env = execute(code)
    assert len(env["expensive_orders"]) == 2
    assert env["expensive_orders"][0]["id"] == 2
    assert len(env["affordable_orders"]) == 2
    assert env["affordable_orders"][1]["id"] == 2


# ---------------------------------------------------------------------------
# Phase 2, Task 2.3: Relative Clauses in Loops
# ---------------------------------------------------------------------------

def test_relative_clause_loop():
    from doomscript.compiler.engine import execute

    code = """
users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "guest"},
    {"name": "Charlie", "role": "admin"}
]
admins = []
for each user in users whose role is "admin":
    add user["name"] to admins
"""
    env = execute(code)
    assert env["admins"] == ["Alice", "Charlie"]
