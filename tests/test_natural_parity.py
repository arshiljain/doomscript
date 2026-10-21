"""
Tests for Phase 2: Grammar-First Expression-Statement Parity and Keyword Safety.
Ensures that data operations can be used symmetrically as statements and expressions,
and that former keyword tokens can be used as identifiers and function call arguments.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute


def run(code: str):
    return execute(textwrap.dedent(code).strip())


def test_split_statement_and_expression_parity():
    code = """
    text = "the quick brown fox"
    split text by " " into w_stmt
    set w_expr to split text by " "
    w_assign = split text by " "
    """
    env = run(code)
    expected = ["the", "quick", "brown", "fox"]
    assert env["w_stmt"] == expected
    assert env["w_expr"] == expected
    assert env["w_assign"] == expected


def test_join_statement_and_expression_parity():
    code = """
    words = ["red", "green", "blue"]
    join words with ", " into s_stmt
    set s_expr to join words with ", "
    s_assign = join words with ", "
    """
    env = run(code)
    assert env["s_stmt"] == "red, green, blue"
    assert env["s_expr"] == "red, green, blue"
    assert env["s_assign"] == "red, green, blue"


def test_replace_statement_and_expression_parity():
    code = """
    sentence = "I love cats and cats"
    replace "cats" with "dogs" in sentence into r_stmt
    set r_expr to replace "cats" with "dogs" in sentence
    """
    env = run(code)
    assert env["r_stmt"] == "I love dogs and dogs"
    assert env["r_expr"] == "I love dogs and dogs"


def test_trim_and_case_parity():
    code = """
    raw = "  hello world  "
    trim raw into t_stmt
    set t_expr to trim raw

    uppercase "doom" into u_stmt
    set u_expr to uppercase "doom"

    lowercase "DOOM" into l_stmt
    set l_expr to lowercase "DOOM"

    capitalize "world" into c_stmt
    set c_expr to capitalize "world"
    """
    env = run(code)
    assert env["t_stmt"] == "hello world"
    assert env["t_expr"] == "hello world"
    assert env["u_stmt"] == "DOOM"
    assert env["u_expr"] == "DOOM"
    assert env["l_stmt"] == "doom"
    assert env["l_expr"] == "doom"
    assert env["c_stmt"] == "World"
    assert env["c_expr"] == "World"


def test_sort_reverse_unique_parity():
    code = """
    nums = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    sort nums into s_stmt
    set s_expr to sorted of nums

    reverse [1, 2, 3] into r_stmt
    set r_expr to reversed of [1, 2, 3]

    unique items of nums into u_stmt
    set u_expr to unique items of nums
    """
    env = run(code)
    assert env["s_stmt"] == sorted(env["nums"])
    assert env["s_expr"] == sorted(env["nums"])
    assert env["r_stmt"] == [3, 2, 1]
    assert env["r_expr"] == [3, 2, 1]
    assert env["u_stmt"] == [3, 1, 4, 5, 9, 2, 6]
    assert env["u_expr"] == [3, 1, 4, 5, 9, 2, 6]


def test_keyword_call_arguments_and_variables():
    code = """
    text = "hello"
    count = 42
    items = [1, 2, 3]
    words = ["a", "b"]

    l1 = len(text)
    l2 = len(items)
    l3 = len(words)
    total = count + 8

    s_rev = sorted([3, 1, 2], reverse=True)
    s_key = sorted(["apple", "banana", "pear"], key=len)
    """
    env = run(code)
    assert env["l1"] == 5
    assert env["l2"] == 3
    assert env["l3"] == 2
    assert env["total"] == 50
    assert env["s_rev"] == [3, 2, 1]
    assert env["s_key"] == ["pear", "apple", "banana"]
