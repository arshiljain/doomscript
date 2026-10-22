import pytest
from doomscript.compiler.engine import execute
from doomscript.core.record import Record


def test_pillar1_record_protection_and_polymorphic_add():
    # 1. Record __getattribute__ protects dict method names from shadowing
    r = Record({"name": "Hero", "items": ["sword", "shield"], "keys": [1, 2]})
    assert r.items == ["sword", "shield"]
    assert r.keys == [1, 2]

    # Non-shadowed records still have normal dict method access
    r2 = Record({"name": "Mage"})
    assert list(r2.items()) == [("name", "Mage")]

    # 2. Polymorphic add
    code = """
score = 100
add 50 to score
add 25 into score

bag = ["sword"]
add "shield" to bag
add "potion" into bag
"""
    ns = execute(code)
    assert ns["score"] == 175
    assert ns["bag"] == ["sword", "shield", "potion"]


def test_pillar2_expression_parity_and_prepositions():
    code = """
text = "  hello world  "
trim text
assert text == "hello world"

capitalize text
assert text == "Hello world"

words = split text by " "
assert words == ["Hello", "world"]

split_with = split "a,b,c" with ","
assert split_with == ["a", "b", "c"]

rejoined = join words by " "
assert rejoined == "Hello world"

rejoined_with = join words with "-"
assert rejoined_with == "Hello-world"

numbers = [10, 20, 30]
first_in = first item in numbers
last_in = last item in numbers
assert first_in == 10
assert last_in == 30

my_list = a list of squares from 1 to 5
assert my_list == [1, 4, 9, 16, 25]

my_nums is a list of 1, 2, 3
assert my_nums == [1, 2, 3]

change text to "DoomScript"
assert text == "DoomScript"
"""
    ns = execute(code)
    assert ns["text"] == "DoomScript"
    assert ns["my_list"] == [1, 4, 9, 16, 25]
    assert ns["my_nums"] == [1, 2, 3]


def test_pillar3_pure_english_object_model():
    code = """
a Person has name, age = 0, status = "active", role (default "adventurer")

create a Person with name "Alice", age 30 into p1
assert p1's name == "Alice"
assert p1's age == 30
assert p1's status == "active"
assert p1's role == "adventurer"

create a Person with name "Bob" into p2
assert p2's name == "Bob"
assert p2's age == 0
assert p2's status == "active"

action greet on Person:
    return "Hello, my name is " + self.name

action celebrate on Person with years:
    self.age += years
    return self.age

res_greet = tell p1 to greet
assert res_greet == "Hello, my name is Alice"

res_age = tell p1 to celebrate with 5
assert res_age == 35
assert p1's age == 35

tell p2 to celebrate with years=10
assert p2's age == 10
"""
    ns = execute(code)
    assert ns["p1"].age == 35
    assert ns["p2"].age == 10
    assert ns["res_greet"] == "Hello, my name is Alice"
