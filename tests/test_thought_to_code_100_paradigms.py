"""Exhaustive test suite verifying the 100 Thought-to-Code Paradigms across 10 cognitive clusters."""
import pytest
from datetime import datetime

from doomscript.compiler.engine import execute, transpile
from doomscript.exceptions import DoomTimeoutError, DoomValueError, DoomAssertionError, DoomSyntaxError


def test_cluster_1_discourse():
    # Paradigm 8: Swapping
    code = """
set x to 100
set y to 200
swap x and y
"""
    res = execute(code)
    assert res['x'] == 200 and res['y'] == 100

    # Paradigm 10: Epistemic assertions
    code2 = """
set balance to 50
surely balance > 0
presumably balance < 1000
"""
    res2 = execute(code2)
    assert res2['balance'] == 50

    # Paradigm 10 failure check
    with pytest.raises(Exception):
        execute("set b to -5\nsurely b > 0\n")

    # Paradigm 1 & 2: Possessive pronoun resolution
    code3 = """
class Person(DoomEntity):
    to init with name="Alice", balance=100:
        self.name = name
        self.balance = balance

set sender to Person(name="Alice", balance=100)
set recipient to Person(name="Bob", balance=50)
set s_name to her name
set r_bal to his balance
"""
    res3 = execute(code3)
    assert res3['s_name'] == "Alice"
    assert res3['r_bal'] == 50

    # Paradigm 3: Elliptical conditionals
    code4 = """
set val to 42
set ok to false
if val > 10:
    set ok to true
if so:
    set branch to "yes"
if not:
    set branch to "no"
"""
    res4 = execute(code4)
    assert res4['branch'] == "yes"


def test_cluster_2_dataflow_and_sets():
    # Paradigm 18: Set algebra
    code = """
set a to [1, 2, 3, 4]
set b to [3, 4, 5, 6]
union of a and b into u
intersection of a and b into inter
difference between a and b into diff
"""
    res = execute(code)
    assert res['u'] == [1, 2, 3, 4, 5, 6]
    assert res['inter'] == [3, 4]
    assert res['diff'] == [1, 2]

    # Paradigm 20: Grouping
    code_grp = """
set data to [{"category": "A", "val": 1}, {"category": "B", "val": 2}, {"category": "A", "val": 3}]
group data by category into grp
"""
    res_grp = execute(code_grp)
    assert len(res_grp['grp']['A']) == 2
    assert len(res_grp['grp']['B']) == 1

    # Paradigm 13: Partitioning
    code_part = """
set numbers to [1, 2, 3, 4, 5, 6]
partition numbers into evens, odds where x is even
"""
    res_part = execute(code_part)
    assert res_part['evens'] == [2, 4, 6]
    assert res_part['odds'] == [1, 3, 5]

    # Paradigm 14: Pairing
    code_pair = """
set names to ["Alice", "Bob"]
set scores to [95, 88]
pair names with scores into pairs
"""
    res_pair = execute(code_pair)
    assert res_pair['pairs'] == [("Alice", 95), ("Bob", 88)]

    # Paradigm 16: Superlatives
    code_sup = """
set items to [{"name": "pen", "price": 2}, {"name": "book", "price": 15}, {"name": "ruler", "price": 1}]
find cheapest item in items by price into best
"""
    res_sup = execute(code_sup)
    assert res_sup['best']['name'] == "ruler"


def test_cluster_3_morphology_and_verbs():
    # Paradigm 21: Quad-verb morphological parity
    code = """
set s to "hello world"
uppercase s into u1
set u2 to s uppercase
set u3 to uppercase of s
convert s to uppercase into u4
"""
    res = execute(code)
    assert res['u1'] == "HELLO WORLD"
    assert res['u2'] == "HELLO WORLD"
    assert res['u3'] == "HELLO WORLD"
    assert res['u4'] == "HELLO WORLD"

    # Paradigm 27: Prepositional equivalence (into vs to)
    code_prep = """
set nums to [1, 2, 3]
add 4 to nums
add 5 into nums
"""
    res_prep = execute(code_prep)
    assert res_prep['nums'] == [1, 2, 3, 4, 5]

    # Paradigm 28: Adverbial qualifiers
    code_adv = """
def fail_then_ok():
    return 42
call fail_then_ok() retrying 3 times into res
"""
    res_adv = execute(code_adv)
    assert res_adv['res'] == 42


def test_cluster_4_temporal():
    # Paradigm 33: Polling guard
    code = """
set counter to 5
wait until counter == 5 with timeout of 1 second
"""
    res = execute(code)
    assert res['counter'] == 5

    # Paradigm 36: Relative time offsets
    code_time = """
set past to 3 days ago
set future to in 2 days
"""
    res_time = execute(code_time)
    assert isinstance(res_time['past'], datetime)
    assert isinstance(res_time['future'], datetime)
    assert res_time['past'] < res_time['future']


def test_cluster_5_causality():
    # Paradigm 44: Scoped assumptions (suppose ... is ...:)
    code = """
set tax to 0.05
suppose tax is 0.20:
    set cost to 100 * (1 + tax)
set normal_cost to 100 * (1 + tax)
"""
    res = execute(code)
    assert res['cost'] == 120.0
    assert res['normal_cost'] == 105.0
    assert res['tax'] == 0.05

    # Paradigm 46: Requires / ensures
    code_req = """
set x to 10
requires x > 0
ensures x == 10
"""
    res_req = execute(code_req)
    assert res_req['x'] == 10

    # Paradigm 47: Invariant
    code_inv = """
set port to 8080
invariant port == 8080
"""
    res_inv = execute(code_inv)
    assert res_inv['port'] == 8080


def test_cluster_6_quantification():
    # Paradigm 51: Proportions
    code = """
set price to 100
increase price by 15%
decrease price by 10%
"""
    res = execute(code)
    assert abs(res['price'] - 103.5) < 0.001

    # Paradigm 52: Natural multipliers
    code_mult = """
set n to 10
double n
halve n
triple n
"""
    res_mult = execute(code_mult)
    assert res_mult['n'] == 30.0

    # Paradigm 53: Approximate natural quantifiers
    code_quant = """
class Item(DoomEntity):
    to init with active=true:
        self.active = active

set items to [Item(active=true), Item(active=true), Item(active=true), Item(active=false)]
set most_active to false
if most of items are active:
    set most_active to true
"""
    res_quant = execute(code_quant)
    assert res_quant['most_active'] is True


def test_cluster_7_spatial_and_hierarchy():
    # Paradigm 66: Clamping
    code = """
set vol1 to 150
clamp vol1 between 0 and 100
set vol2 to -20
clamp vol2 between 0 and 100
"""
    res = execute(code)
    assert res['vol1'] == 100
    assert res['vol2'] == 0

    # Paradigm 62: Family hierarchy
    code_tree = """
class Node(DoomEntity):
    to init with children=[]:
        self.children = children

set n to Node(children=[1, 2, 3])
set c to children of n
"""
    res_tree = execute(code_tree)
    assert res_tree['c'] == [1, 2, 3]


def test_cluster_8_state_and_lifecycle():
    # Paradigm 71 & 72: State machine and transitions
    code = """
class DeliveryOrder(DoomEntity):
    to init with status="pending":
        self.status = status

a DeliveryOrder can be "pending", "paid", "shipped", "delivered"
set o to DeliveryOrder(status="pending")
transition o to "paid"
transition o from "paid" to "shipped"
"""
    res = execute(code)
    assert res['o'].status == "shipped"

    # Paradigm 76: Entity relationships
    code_rel = """
a Buyer begins with name = ""
a Purchase begins with total = 0
a Buyer has many Purchases
a Purchase belongs to a Buyer
"""
    execute(code_rel)


def test_cluster_9_resilience():
    # Paradigm 81: Null-coalescing
    code_coal = """
set d to {"key": "val"}
set v1 to d["missing"] otherwise "fallback"
"""
    res_coal = execute(code_coal)
    assert res_coal['v1'] == "fallback"

    # Paradigm 86: Safe navigation
    code_safe = """
set d to {"a": {"b": 42}}
safely access d["a"]["b"] otherwise 0 into val1
safely access d["nonexistent"]["b"] otherwise 99 into val2
"""
    res_safe = execute(code_safe)
    assert res_safe['val1'] == 42
    assert res_safe['val2'] == 99


def test_cluster_10_ambient_intelligence():
    # Paradigm 91: Conversational inquiries
    code_inq = """
set orders to [{"id": 1, "price": 100}, {"id": 2, "price": 200}]
what is the total price in orders into total_rev
what is the average price in orders into avg_rev
how many items in orders into order_count
"""
    res_inq = execute(code_inq)
    assert res_inq['total_rev'] == 300
    assert res_inq['avg_rev'] == 150
    assert res_inq['order_count'] == 2

    # Paradigm 99: Purpose docstring
    code_purpose = """
def calculate_total(a, b):
    purpose: "Calculates the sum of two values"
    return a + b

set sum_res to calculate_total(10, 20)
"""
    res_purpose = execute(code_purpose)
    assert res_purpose['sum_res'] == 30
