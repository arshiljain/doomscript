"""
Tests for Phase 4: Natural Comprehensions and Grammar-Level Ranges.
Ensures that English ranges (from a to b [by c]) and list expressions
(a list of x, y, z | a list of squares... | for each x from a to b:) work seamlessly.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute


def run(code: str):
    return execute(textwrap.dedent(code).strip())


def test_natural_list_comprehensions():
    code = """
    sq1 = [x * x for each x from 1 to 5]
    sq2 = [x * x for x from 1 to 5 by 2]
    sq3 = a list of x * x for each x from 1 to 5
    sq4 = a list of x * x from 1 to 5
    """
    env = run(code)
    assert env["sq1"] == [1, 4, 9, 16, 25]
    assert env["sq2"] == [1, 9, 25]
    assert env["sq3"] == [1, 4, 9, 16, 25]
    assert env["sq4"] == [1, 4, 9, 16, 25]


def test_natural_list_values():
    code = """
    nums = a list of 10, 20, 30
    words = a list of "alpha", "beta"
    """
    env = run(code)
    assert env["nums"] == [10, 20, 30]
    assert env["words"] == ["alpha", "beta"]


def test_for_range_loops():
    code = """
    collected = []
    for each i from 1 to 5:
        add i to collected

    evens = []
    for n from 1 to 10 by 2:
        add n to evens

    filtered = []
    for each x from 1 to 6 where x is even:
        add x to filtered
    """
    env = run(code)
    assert env["collected"] == [1, 2, 3, 4, 5]
    assert env["evens"] == [1, 3, 5, 7, 9]
    assert env["filtered"] == [2, 4, 6]
