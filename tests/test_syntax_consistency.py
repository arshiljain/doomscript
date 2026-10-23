"""Tests for Universal Syntax Consistency (Statement vs Expression Duality, Synonyms, Nesting, Quantifiers)."""

import pytest
from doomscript.compiler.engine import execute


def test_split_statement_and_expression_duality():
    stmt = execute('split "a,b" by "," into res')
    expr_inline = execute('set res to split "a,b" by ","')
    expr_suffix = execute('set res to "a,b" split by ","')
    assert stmt["res"] == expr_inline["res"] == expr_suffix["res"] == ["a", "b"]


def test_join_statement_and_expression_duality():
    stmt = execute('set w to ["a","b"]\njoin w with "-" into res')
    expr_inline = execute('set w to ["a","b"]\nset res to join w with "-"')
    expr_suffix = execute('set w to ["a","b"]\nset res to w joined with "-"')
    assert stmt["res"] == expr_inline["res"] == expr_suffix["res"] == "a-b"


def test_sort_statement_and_expression_duality():
    stmt = execute('set n to [3, 1]\nsort n into res')
    expr_inline = execute('set n to [3, 1]\nset res to sorted n')
    assert stmt["res"] == expr_inline["res"] == [1, 3]

    stmt_by = execute('set items to [{"v": 2}, {"v": 1}]\nsort items by v into res')
    expr_by = execute('set items to [{"v": 2}, {"v": 1}]\nset res to sorted items by v')
    assert stmt_by["res"] == expr_by["res"] == [{"v": 1}, {"v": 2}]


def test_unique_statement_and_expression_duality():
    stmt = execute('set n to [1, 2, 2]\nunique n into res')
    expr_inline = execute('set n to [1, 2, 2]\nset res to unique n')
    expr_of = execute('set n to [1, 2, 2]\nset res to unique items of n')
    assert stmt["res"] == expr_inline["res"] == expr_of["res"] == [1, 2]


def test_take_and_drop_statement_and_expression_duality():
    t_stmt = execute('set n to [1, 2, 3]\ntake 2 from n into res')
    t_expr = execute('set n to [1, 2, 3]\nset res to take 2 from n')
    t_first = execute('set n to [1, 2, 3]\nset res to first 2 items of n')
    assert t_stmt["res"] == t_expr["res"] == t_first["res"] == [1, 2]

    d_stmt = execute('set n to [1, 2, 3]\ndrop 1 from n into res')
    d_expr = execute('set n to [1, 2, 3]\nset res to drop 1 from n')
    assert d_stmt["res"] == d_expr["res"] == [2, 3]


def test_filter_statement_and_expression_duality():
    canonical = execute('set items to [{"a": 10}, {"a": 2}]\nitems where a > 5 into res')
    leading_filt = execute('set items to [{"a": 10}, {"a": 2}]\nfilter items where a > 5 into res')
    set_expr = execute('set items to [{"a": 10}, {"a": 2}]\nset res to items where a > 5')
    keep_only = execute('set items to [{"a": 10}, {"a": 2}]\nkeep only items where a > 5 into res')
    assert canonical["res"] == leading_filt["res"] == set_expr["res"] == keep_only["res"] == [{"a": 10}]


def test_nested_composition():
    r1 = execute('set w to ["hi", "there"]\nset res to uppercase of first item of w')
    assert r1["res"] == "HI"

    r2 = execute('set w to ["HI", "THERE"]\nset res to lowercase of last item of w')
    assert r2["res"] == "there"

    r3 = execute('set res to trim of uppercase of "  hello  "')
    assert r3["res"] == "HELLO"

    r4 = execute('set items to [{"p": 10}, {"p": 20}]\nset res to sum of p of items')
    assert r4["res"] == 30


def test_quantifiers_and_plural_agreement():
    q1 = execute('set g to [{"role": "admin"}, {"role": "admin"}]\nset res to false\nif every x in g has role "admin": set res to true')
    assert q1["res"] is True

    q2 = execute('set g to [{"paid": true}, {"paid": true}]\nset res to false\nif all of g have paid: set res to true')
    assert q2["res"] is True


def test_mutation_synonyms():
    m1_a = execute('set n to [1]\nadd 2 to n\nset res to n')
    m1_b = execute('set n to [1]\nappend 2 to n\nset res to n')
    m1_c = execute('set n to [1]\npush 2 into n\nset res to n')
    assert m1_a["res"] == m1_b["res"] == m1_c["res"] == [1, 2]

    m2_a = execute('set n to [1, 2]\nremove 2 from n\nset res to n')
    m2_b = execute('set n to [1, 2]\ndelete 2 from n\nset res to n')
    assert m2_a["res"] == m2_b["res"] == [1]

    m3_a = execute('set x to 10\nincrease x by 2\nset res to x')
    m3_b = execute('set x to 10\nincrement x by 2\nset res to x')
    assert m3_a["res"] == m3_b["res"] == 12

    m4_a = execute('set x to 10\ndecrease x by 2\nset res to x')
    m4_b = execute('set x to 10\ndecrement x by 2\nset res to x')
    m4_c = execute('set x to 10\nsubtract 2 from x\nset res to x')
    assert m4_a["res"] == m4_b["res"] == m4_c["res"] == 8


def test_collection_literals():
    l_lit = execute('set res to []')
    l_emp = execute('set res to an empty list')
    l_new = execute('set res to a new list')
    assert l_lit["res"] == l_emp["res"] == l_new["res"] == []

    d_lit = execute('set res to {}')
    d_emp = execute('set res to an empty dictionary')
    d_new = execute('set res to a new dictionary')
    d_rec = execute('set res to an empty record')
    assert d_lit["res"] == d_emp["res"] == d_new["res"] == d_rec["res"] == {}


def test_membership_and_math_synonyms():
    mem1 = execute('set n to [1, 5, 10]\nset res to false\nif n has 5: set res to true')
    assert mem1["res"] is True

    sq1 = execute('set x to 4\nset res to square of x')
    sq2 = execute('set x to 4\nset res to x squared')
    assert sq1["res"] == sq2["res"] == 16

    sqrt1 = execute('set x to 16\nset res to square root of x')
    sqrt2 = execute('set x to 16\nset res to sqrt of x')
    assert sqrt1["res"] == sqrt2["res"] == 4.0
