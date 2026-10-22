"""
Tests verifying Principle 3: Conformance Equivalence Test Suite.
Asserts that equivalent English phrasings evaluate to identical results and behavior.
"""

import pytest
from doomscript.compiler.engine import execute


def test_equivalence_collection_filtering():
    """Principle 1 & 2: Form A vs Form B for filtering collections."""
    code = """
items = [{'amount': 10}, {'amount': 60}, {'amount': 80}, {'amount': 40}]

# Form A: Postfix query filter
items where amount is over 50 into res_a

# Form B: Prefix keep only
keep only items where amount is over 50 into res_b

# Form C: Explicit comparator
items where amount > 50 into res_c

# Form D: Phrase comparator
items where amount is greater than 50 into res_d
"""
    env = execute(code)
    expected = [{'amount': 60}, {'amount': 80}]
    assert env['res_a'] == expected
    assert env['res_b'] == expected
    assert env['res_c'] == expected
    assert env['res_d'] == expected
    assert env['res_a'] == env['res_b'] == env['res_c'] == env['res_d']


def test_equivalence_pipeline_filter_comparisons():
    """Principle 1: 'is' vs 'equals' vs '==' in data pipelines."""
    code = """
use data
records = [
    {'status': 'active', 'val': 100},
    {'status': 'inactive', 'val': 200},
    {'status': 'active', 'val': 300}
]

pipeline 'p_is' from records into out_is:
    filter where status is 'active'

pipeline 'p_equals' from records into out_equals:
    filter where status equals 'active'

pipeline 'p_equal_to' from records into out_equal_to:
    filter where status is equal to 'active'

pipeline 'p_eq' from records into out_eq:
    filter where status == 'active'
"""
    env = execute(code)
    expected = [{'status': 'active', 'val': 100}, {'status': 'active', 'val': 300}]
    assert env['out_is'] == expected
    assert env['out_equals'] == expected
    assert env['out_equal_to'] == expected
    assert env['out_eq'] == expected
    assert env['out_is'] == env['out_equals'] == env['out_equal_to'] == env['out_eq']


def test_equivalence_expression_composition():
    """Principle 2: Composed expression vs multi-statement decomposition."""
    code = """
words = ["delta", "gamma", "beta", "alpha"]

# Composed form: Slicing + joining in a single expression
set label_composed to first 2 items of words joined with " / "

# Multi-statement form: Slicing into temp, then joining
first 2 items of words into short_words
set label_split to short_words joined with " / "

# Last items composed vs split
set label_last_comp to last 2 items of words joined with " - "
last 2 items of words into end_words
set label_last_split to end_words joined with " - "
"""
    env = execute(code)
    assert env['label_composed'] == "delta / gamma"
    assert env['label_split'] == "delta / gamma"
    assert env['label_composed'] == env['label_split']

    assert env['label_last_comp'] == "beta - alpha"
    assert env['label_last_split'] == "beta - alpha"
    assert env['label_last_comp'] == env['label_last_split']


def test_equivalence_quantifiers_predicates():
    """Principle 2: English quantifiers resolving record attributes vs values."""
    code = """
registrations = [
    {'guest': 'Alice', 'paid': True, 'status': 'confirmed'},
    {'guest': 'Bob', 'paid': True, 'status': 'confirmed'},
    {'guest': 'Charlie', 'paid': True, 'status': 'confirmed'}
]

if every guest in registrations is paid:
    all_paid_is = True
else:
    all_paid_is = False

if every guest in registrations has paid:
    all_paid_has = True
else:
    all_paid_has = False

if every guest in registrations has status equal to "confirmed":
    all_status_confirmed = True
else:
    all_status_confirmed = False

numbers = [2, 4, 6, 8]
if every n in numbers is even:
    all_even = True
else:
    all_even = False
"""
    env = execute(code)
    assert env['all_paid_is'] is True
    assert env['all_paid_has'] is True
    assert env['all_status_confirmed'] is True
    assert env['all_even'] is True


def test_equivalence_quantifiers_negative():
    """Verify that quantifiers evaluate to False when condition fails."""
    code = """
registrations = [
    {'guest': 'Alice', 'paid': True},
    {'guest': 'Bob', 'paid': False}
]

if every guest in registrations is paid:
    paid_ok = True
else:
    paid_ok = False

if any guest in registrations is paid:
    any_paid = True
else:
    any_paid = False

if no guest in registrations is paid:
    none_paid = True
else:
    none_paid = False
"""
    env = execute(code)
    assert env['paid_ok'] is False
    assert env['any_paid'] is True
    assert env['none_paid'] is False


def test_equivalence_all_equality_synonyms():
    """Principle 1: All equality synonyms evaluate to exact same truth table."""
    code = """
target_val = 42

eq1 = (target_val is 42)
eq2 = (target_val equals 42)
eq3 = (target_val equal to 42)
eq4 = (target_val is equal to 42)
eq5 = (target_val is identical to 42)
eq6 = (target_val is the same as 42)
eq7 = (target_val == 42)

neq1 = (target_val is not 99)
neq2 = (target_val isn't 99)
neq3 = (target_val does not equal 99)
neq4 = (target_val is not equal to 99)
neq5 = (target_val != 99)
"""
    env = execute(code)
    assert env['eq1'] == env['eq2'] == env['eq3'] == env['eq4'] == env['eq5'] == env['eq6'] == env['eq7'] is True
    assert env['neq1'] == env['neq2'] == env['neq3'] == env['neq4'] == env['neq5'] is True


def test_equivalence_ordering_synonyms():
    """Principle 1: All relational ordering synonyms evaluate identically."""
    code = """
x = 75

gt1 = (x is over 50)
gt2 = (x is above 50)
gt3 = (x is greater than 50)
gt4 = (x > 50)

gte1 = (x is at least 75)
gte2 = (x is greater than or equal to 75)
gte3 = (x >= 75)

lt1 = (x is under 100)
lt2 = (x is below 100)
lt3 = (x is less than 100)
lt4 = (x < 100)

lte1 = (x is at most 75)
lte2 = (x is less than or equal to 75)
lte3 = (x <= 75)
"""
    env = execute(code)
    assert env['gt1'] == env['gt2'] == env['gt3'] == env['gt4'] is True
    assert env['gte1'] == env['gte2'] == env['gte3'] is True
    assert env['lt1'] == env['lt2'] == env['lt3'] == env['lt4'] is True
    assert env['lte1'] == env['lte2'] == env['lte3'] is True


def test_equivalence_aggregations():
    """Principle 1: Aggregation phrasings evaluate identically."""
    code = """
vals = [10, 20, 30, 40]

c1 = count of vals
c2 = length of vals
c3 = len(vals)

s1 = sum of vals
s2 = total of vals

h1 = highest in vals
h2 = maximum in vals

l1 = lowest in vals
l2 = minimum in vals
"""
    env = execute(code)
    assert env['c1'] == env['c2'] == env['c3'] == 4
    assert env['s1'] == env['s2'] == 100
    assert env['h1'] == env['h2'] == 40
    assert env['l1'] == env['l2'] == 10
