"""
Tests for Phase 1: Normalization & Phrase Layer
Verifies filler words, synonym tables, sentence endings, flexible assignment,
pronouns, possessive articles, and scope safety.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute, transpile
from doomscript.grammar.phrases import normalize, VERB_SYNONYMS, COMPARISON_SYNONYMS
from doomscript.exceptions import DoomScopeError


def run(source: str):
    env = {}
    execute(textwrap.dedent(source).strip(), custom_globals=env)
    return env


def test_filler_words_please_and_just():
    code = """
    items = [1, 2, 3]
    please add 4 to items
    just add 5 to items
    total = sum of items
    """
    env = run(code)
    assert env["items"] == [1, 2, 3, 4, 5]
    assert env["total"] == 15


def test_ignorable_articles_the():
    code = """
    total = 50
    items = ["a", "b"]
    please add "c" to the items
    the_count = count of the items
    """
    env = run(code)
    assert env["items"] == ["a", "b", "c"]
    assert env["the_count"] == 3


def test_verb_synonyms_output(capsys):
    code = """
    show "Testing show"
    print "Testing print"
    tell "Testing tell"
    display "Testing display"
    """
    run(code)
    captured = capsys.readouterr()
    assert "Testing show" in captured.out
    assert "Testing print" in captured.out
    assert "Testing tell" in captured.out
    assert "Testing display" in captured.out


def test_verb_synonyms_return():
    code = """
    to calculate_area with width, height
        give back width * height

    to calculate_perimeter with width, height
        hand back (width + height) * 2

    area = calculate_area(5, 10)
    perim = calculate_perimeter(5, 10)
    """
    env = run(code)
    assert env["area"] == 50
    assert env["perim"] == 30


def test_comparison_synonyms():
    code = """
    val = 20

    gt1 = val is bigger than 10
    gt2 = val is more than 10
    gt3 = val exceeds 10
    gte = val is no less than 20
    lte = val is no more than 20
    lt = val is smaller than 30
    eq = val is equal to 20
    neq = val is different from 99
    """
    env = run(code)
    assert env["gt1"] is True
    assert env["gt2"] is True
    assert env["gt3"] is True
    assert env["gte"] is True
    assert env["lte"] is True
    assert env["lt"] is True
    assert env["eq"] is True
    assert env["neq"] is True


def test_sentence_endings_and_chaining():
    code = """
    x = 10.
    y = 20.
    total = x + y.
    
    a is 5 and then b is 15 and then sum_ab is a + b
    """
    env = run(code)
    assert env["total"] == 30
    assert env["sum_ab"] == 20


def test_flexible_assignment_variations():
    code = """
    x is 10
    y = 20
    set z to 30
    let a be 40
    make b 50
    make c be 60
    put 70 into d
    """
    env = run(code)
    assert env["x"] == 10
    assert env["y"] == 20
    assert env["z"] == 30
    assert env["a"] == 40
    assert env["b"] == 50
    assert env["c"] == 60
    assert env["d"] == 70


def test_pronoun_it_and_that():
    code = """
    score = 100
    increase it by 50
    bonus = 25
    increase that by 5
    """
    env = run(code)
    assert env["score"] == 150
    assert env["bonus"] == 30


def test_call_it_alias_assignment():
    code = """
    result = 42
    call it answer
    increase answer by 8
    """
    env = run(code)
    assert env["result"] == 42
    assert env["answer"] == 50


def test_pronoun_unresolved_scope_error():
    code = """
    increase it by 10
    """
    with pytest.raises(DoomScopeError) as exc_info:
        run(code)
    assert "Cannot resolve pronoun" in str(exc_info.value)


def test_possessives_and_articles_length():
    code = """
    name = "DoomSlayer"
    len1 = the length of name
    len2 = length of name
    len3 = name's length
    len4 = name's count
    """
    env = run(code)
    assert env["len1"] == 10
    assert env["len2"] == 10
    assert env["len3"] == 10
    assert env["len4"] == 10


def test_strings_protected_from_normalization():
    code = """
    msg = "please show the length of this and then stop."
    """
    env = run(code)
    # The string content must NOT be modified or stripped by normalizer
    assert env["msg"] == "please show the length of this and then stop."
