"""
Tests for Phase 3: First-Class Grammar Adjective Predicates.
Ensures that predicates (is even, is odd, is positive, is negative, is zero)
and their negations work natively in the grammar with correct arithmetic precedence.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute


def run(code: str):
    return execute(textwrap.dedent(code).strip())


def test_even_odd_predicates_and_precedence():
    code = """
    x = 4
    e1 = x is even
    e2 = x + 1 is odd
    e3 = x + 1 is not even
    e4 = x isn't odd
    e5 = (x * 2) is even
    e6 = 2 * 3 + 1 is odd
    """
    env = run(code)
    assert env["e1"] is True
    assert env["e2"] is True
    assert env["e3"] is True
    assert env["e4"] is True
    assert env["e5"] is True
    assert env["e6"] is True


def test_positive_negative_zero_predicates():
    code = """
    p = 10
    n = -5
    z = 0

    p_check = p is positive
    p_neg_check = p is not negative
    n_check = n is negative
    n_pos_check = n is not positive
    z_check = z is zero
    z_nonzero = z is not zero

    calc_p = 5 - 2 is positive
    calc_n = 2 - 5 is negative
    calc_z = 5 - 5 is zero
    """
    env = run(code)
    assert env["p_check"] is True
    assert env["p_neg_check"] is True
    assert env["n_check"] is True
    assert env["n_pos_check"] is True
    assert env["z_check"] is True
    assert env["z_nonzero"] is False
    assert env["calc_p"] is True
    assert env["calc_n"] is True
    assert env["calc_z"] is True


def test_predicates_in_control_flow():
    code = """
    evens = []
    odds = []
    
    for each n in [1, 2, 3, 4, 5, 6]:
        if n is even:
            add n to evens
        if n is odd:
            add n to odds
    """
    env = run(code)
    assert env["evens"] == [2, 4, 6]
    assert env["odds"] == [1, 3, 5]
