"""
Tests for Expression vs Statement Parity in DoomScript.
Verifies that natural operations (split, length of, sum of, highest in, lowest in, reversed of, count of)
and English comprehensions/ranges behave identically in both expression and statement forms.
"""

import pytest
from doomscript.compiler.engine import execute


def test_split_statement_and_expression_parity():
    code = """
text = "alpha beta gamma delta"

# Expression forms
set words_expr to split text by " "
words_assign = split text by " "

# Statement form
split text by " " into words_stmt

# Expression directly in loop
collected = []
for each w in split text by " ":
    add w to collected
"""
    env = execute(code)
    expected = ["alpha", "beta", "gamma", "delta"]
    assert env["words_expr"] == expected
    assert env["words_assign"] == expected
    assert env["words_stmt"] == expected
    assert env["collected"] == expected


def test_length_and_count_parity():
    code = """
items = [10, 20, 30, 40, 50]

# Expression forms
set len_expr to length of items
set count_expr to count of items

# Statement forms
length of items into len_stmt
count of items into count_stmt
"""
    env = execute(code)
    assert env["len_expr"] == 5
    assert env["count_expr"] == 5
    assert env["len_stmt"] == 5
    assert env["count_stmt"] == 5


def test_sum_parity():
    code = """
nums = [1, 2, 3, 4, 5]

# Expression form
set sum_expr to sum of nums

# Statement form
sum of nums into sum_stmt
"""
    env = execute(code)
    assert env["sum_expr"] == 15
    assert env["sum_stmt"] == 15


def test_highest_and_lowest_parity():
    code = """
values = [14, 88, 3, 42, 99, 1]

# Highest
set max_expr to highest in values
highest in values into max_stmt
set max_of_expr to highest of values
highest of values into max_of_stmt

# Lowest
set min_expr to lowest in values
lowest in values into min_stmt
set min_of_expr to lowest of values
lowest of values into min_of_stmt
"""
    env = execute(code)
    assert env["max_expr"] == 99
    assert env["max_stmt"] == 99
    assert env["max_of_expr"] == 99
    assert env["max_of_stmt"] == 99

    assert env["min_expr"] == 1
    assert env["min_stmt"] == 1
    assert env["min_of_expr"] == 1
    assert env["min_of_stmt"] == 1


def test_reversed_parity():
    code = """
original = [1, 2, 3, 4]

# Expression forms
set rev_expr to reversed of original
set rev_in_expr to reversed in original

# Statement forms
reverse original into rev_stmt
reversed of original into rev_stmt2
"""
    env = execute(code)
    expected = [4, 3, 2, 1]
    assert env["rev_expr"] == expected
    assert env["rev_in_expr"] == expected
    assert env["rev_stmt"] == expected
    assert env["rev_stmt2"] == expected


def test_comprehension_and_ranges_parity():
    code = """
# Expression form
set squares_expr to make a list of squares from 1 to 5

# Statement form
make a list of squares from 1 to 5 into squares_stmt

# Formula comprehension
set formula_expr to make a list of x * x for each x from 1 to 5
make a list of x * x for each x from 1 to 5 into formula_stmt

# Number range
set nums_expr to make a list from 1 to 5
make a list from 1 to 5 into nums_stmt

# Sum of squares
set sum_sq_expr to sum of squares from 1 to 5
"""
    env = execute(code)
    expected_sq = [1, 4, 9, 16, 25]
    expected_nums = [1, 2, 3, 4, 5]

    assert env["squares_expr"] == expected_sq
    assert env["squares_stmt"] == expected_sq
    assert env["formula_expr"] == expected_sq
    assert env["formula_stmt"] == expected_sq
    assert env["nums_expr"] == expected_nums
    assert env["nums_stmt"] == expected_nums
    assert env["sum_sq_expr"] == 55
