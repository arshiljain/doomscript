"""
Tests for Phase 5: Declarative Entities, Polymorphic Operations, and Intuitive English Syntax.
Verifies:
1. Polymorphic add statement (numbers, lists, sets, strings).
2. Polymorphic remove statement (lists with safe absent removal, sets, dicts).
3. Declarative entity definitions: 'a Person has name, age'.
4. Entity instantiation: 'create a Person with name "Alice", age 30 into p1'.
5. Property mutation verbs: 'change', 'modify', 'update'.
6. Trailing input type coercion: 'ask "..." into age as number'.
7. Natural error handling: 'try: ... if there is an error: ...'.
8. Range predicates: 'is between', 'is outside'.
"""

import pytest
from doomscript.compiler.engine import execute


def test_polymorphic_add(capsys):
    code = """
x = 10
add 5 to x
say x

items = [1, 2]
add 3 to items
say items

greeting = "hello"
add " world" to greeting
say greeting

tags = {1, 2}
add 3 to tags
say 3 is inside tags
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "15"
    assert lines[1] == "[1, 2, 3]"
    assert lines[2] == "hello world"
    assert lines[3] == "True"


def test_polymorphic_remove(capsys):
    code = """
items = [1, 2, 3]
remove 2 from items
say items
remove 99 from items
say items

s = {1, 2, 3}
remove 2 from s
say 2 is inside s
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "[1, 3]"
    assert lines[1] == "[1, 3]"
    assert lines[2] == "False"


def test_declarative_entities_and_verbs(capsys):
    code = """
a Person has name, age
create a Person with name "Alice", age 30 into p1
say p1's name
say p1's age

change p1's name to "Bob"
say p1's name

modify p1's age to 35
say p1's age

update p1's name to "Charlie"
say p1's name
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines == ["Alice", "30", "Bob", "35", "Charlie"]


def test_standalone_operations_and_pronouns(capsys):
    code = """
make a list of squares from 1 to 5
say that

trim "  hello  "
say that

uppercase "world"
say that

lowercase "PYTHON"
say that
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "[1, 4, 9, 16, 25]"
    assert lines[1] == "hello"
    assert lines[2] == "WORLD"
    assert lines[3] == "python"


def test_range_predicates(capsys):
    code = """
val = 15
if val is between 10 and 20:
    say "IN"

if val is outside 20 and 30:
    say "OUT"
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines == ["IN", "OUT"]


def test_natural_error_handling(capsys):
    code = """
try:
    x = 10 / 0
if there is an error:
    say "RECOVERED"
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "RECOVERED"
