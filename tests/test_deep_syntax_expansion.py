"""
Tests for DoomScript Deep Syntax Expansion.
Covers:
- Task 1: Runtime primitives (ds_median, ds_stdev, ds_variance, ds_enumerate, ds_take, ds_drop)
- Task 2: Math, powers, percentages, roots, statistical aggregates
- Task 3: Pattern matching (match ... when ... otherwise)
- Task 4: Slicing, take/drop, and spoken pipelines
- Task 5: Looping with index, down-to ranges, and English quantifiers
"""

import math
import pytest
from doomscript.compiler.engine import execute


# ---------------------------------------------------------------------------
# Task 1: Runtime Helpers Tests
# ---------------------------------------------------------------------------

def test_runtime_helpers_import():
    from doomscript.runtime import (
        ds_median,
        ds_stdev,
        ds_variance,
        ds_enumerate,
        ds_take,
        ds_drop,
    )

    data = [10, 20, 30, 40, 50]
    assert ds_median(data) == 30
    assert math.isclose(ds_stdev([1, 2, 3, 4, 5]), 1.5811388300841898)
    assert math.isclose(ds_variance([1, 2, 3, 4, 5]), 2.5)

    # 1-based indexing default for ds_enumerate
    enumerated = list(ds_enumerate(["alpha", "beta", "gamma"]))
    assert enumerated == [(1, "alpha"), (2, "beta"), (3, "gamma")]

    # ds_take and ds_drop
    assert ds_take([1, 2, 3, 4, 5], 3) == [1, 2, 3]
    assert ds_take([1, 2], 5) == [1, 2]
    assert ds_drop([1, 2, 3, 4, 5], 2) == [3, 4, 5]
    assert ds_drop([1, 2], 5) == []


# ---------------------------------------------------------------------------
# Task 2: Math, Exponents, Roots, Percentages & Statistics Tests
# ---------------------------------------------------------------------------

def test_powers_squared_cubed():
    source = """
x = 5
sq = x squared
cb = x cubed
p = 2 to the power of 4
r = 3 raised to 3
"""
    env = execute(source)
    assert env["sq"] == 25
    assert env["cb"] == 125
    assert env["p"] == 16
    assert env["r"] == 27


def test_roots():
    source = """
r1 = square root of 144
r2 = cube root of 27
"""
    env = execute(source)
    assert env["r1"] == 12.0
    assert math.isclose(env["r2"], 3.0)


def test_percentage_expressions():
    source = """
total = 200
tax = 15 percent of total
tip = 20 % of 50
"""
    env = execute(source)
    assert env["tax"] == 30.0
    assert env["tip"] == 10.0


def test_statistical_aggregates():
    source = """
numbers = [10, 20, 30, 40, 50]
med = median of numbers
var = variance of numbers
std = stdev of numbers
prod = product of [2, 3, 4]
"""
    env = execute(source)
    assert env["med"] == 30
    assert math.isclose(env["var"], 250.0)
    assert math.isclose(env["std"], 15.811388300841896)
    assert env["prod"] == 24

