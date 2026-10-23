"""
Tests for DoomScript Multi-Clause Sentence Chaining ('and', 'then').
Verifies that compound English statements execute sequentially while
preserving conditionals, lists, and expression operands.
"""

import pytest
from doomscript.compiler.engine import execute


def test_chaining_into_and_verb(tmp_path):
    test_file = tmp_path / "data.csv"
    test_file.write_text("alpha,beta,gamma", encoding="utf-8")
    test_file_posix = str(test_file).replace("\\", "/")

    source = f"""
read file "{test_file_posix}" into raw and split raw by "," into lines
"""
    env = execute(source)
    assert env["lines"] == ["alpha", "beta", "gamma"]


def test_chaining_entity_creation_and_access():
    source = """
a Person has name, age
create a Person with name "Bob", age 25 into p and set p_name to p's name
"""
    env = execute(source)
    assert env["p_name"] == "Bob"
    assert env["p"].age == 25


def test_chaining_then():
    source = """
set x to 10 then set y to 20
"""
    env = execute(source)
    assert env["x"] == 10
    assert env["y"] == 20


def test_chaining_and_then():
    source = """
set x to 100 and then set y to 200
"""
    env = execute(source)
    assert env["x"] == 100
    assert env["y"] == 200


def test_chaining_set_and_set():
    source = """
set x to 42 and set y to 84
"""
    env = execute(source)
    assert env["x"] == 42
    assert env["y"] == 84


def test_chaining_three_statements():
    source = """
set a to 1 and set b to 2 and set c to 3
"""
    env = execute(source)
    assert env["a"] == 1
    assert env["b"] == 2
    assert env["c"] == 3


def test_chaining_assignments():
    source = """
x = 10 and y = 20
"""
    env = execute(source)
    assert env["x"] == 10
    assert env["y"] == 20


def test_chaining_inside_loop():
    source = """
x = 0
y = 0
repeat 3 times:
    set x to x + 1 and set y to y + 2
"""
    env = execute(source)
    assert env["x"] == 3
    assert env["y"] == 6


def test_protects_conditional_and():
    source = """
x = 15
y = 25
result = "no"
if x > 10 and y > 20:
    result = "yes"
"""
    env = execute(source)
    assert env["result"] == "yes"


def test_protects_between_and():
    source = """
score = 85
passed = false
if score is between 80 and 90:
    passed = true
"""
    env = execute(source)
    assert env["passed"] is True


def test_protects_boolean_expression_and():
    source = """
flag_a = true
flag_b = false
combined = flag_a and flag_b
"""
    env = execute(source)
    assert env["combined"] is False
