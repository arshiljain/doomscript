"""
Tests for newly added Natural English Syntax enhancements in DoomScript.
Covers bare splits, reverse expressions, clamping directives, descriptive rounding,
random sampling & picking, natural ranges in assignments & loops, and expression shuffling.
"""

import pytest
from doomscript.compiler.engine import execute


def test_bare_whitespace_split():
    code = """
text = "hello   world from  doomscript"
split text into words
assert words == ["hello", "world", "from", "doomscript"]

words2 = split text
assert words2 == ["hello", "world", "from", "doomscript"]
"""
    env = execute(code)
    assert env["words"] == ["hello", "world", "from", "doomscript"]
    assert env["words2"] == ["hello", "world", "from", "doomscript"]


def test_reverse_expressions():
    code = """
numbers = [1, 2, 3]
r1 = reverse numbers
r2 = reversed numbers
r3 = reverse of numbers
r4 = reversed of numbers
assert r1 == [3, 2, 1]
assert r2 == [3, 2, 1]
assert r3 == [3, 2, 1]
assert r4 == [3, 2, 1]
"""
    env = execute(code)
    assert env["r1"] == [3, 2, 1]
    assert env["r2"] == [3, 2, 1]


def test_boundary_clamping_directives():
    code = """
score1 = 150
clamp score1 between 0 and 100 into c1
assert c1 == 100

c2 = clamp -20 between 0 and 100
assert c2 == 0

score3 = 45
clamp score3 between 10 and 50
assert score3 == 45

score4 = 75
clamp score4 within 10 to 50
assert score4 == 50
"""
    env = execute(code)
    assert env["c1"] == 100
    assert env["c2"] == 0
    assert env["score3"] == 45
    assert env["score4"] == 50


def test_descriptive_rounding():
    code = """
price = 19.9567
round price to 2 decimal places into r1
assert r1 == 19.96

r2 = round price to 2 decimals
assert r2 == 19.96

r3 = round price to 1 decimal place
assert r3 == 20.0
"""
    env = execute(code)
    assert env["r1"] == 19.96
    assert env["r2"] == 19.96
    assert env["r3"] == 20.0


def test_sampling_and_random_picking():
    code = """
numbers = [10, 20, 30, 40, 50]
pick 2 items from numbers into picked
assert len(picked) == 2
assert picked[0] in numbers
assert picked[1] in numbers

sampled = sample 3 items from numbers
assert len(sampled) == 3
assert sampled[0] in numbers

cards = ["Ace", "King", "Queen"]
pick a random item from cards into card1
assert card1 in cards

card2 = pick a random item from cards
assert card2 in cards
"""
    env = execute(code)
    assert len(env["picked"]) == 2
    assert len(env["sampled"]) == 3
    assert env["card1"] in ["Ace", "King", "Queen"]
    assert env["card2"] in ["Ace", "King", "Queen"]


def test_natural_ranges():
    code = """
nums = 1 to 5
assert nums == [1, 2, 3, 4, 5]

letters = "a" to "e"
assert letters == ["a", "b", "c", "d", "e"]

total = 0
for i in 1 to 5:
    total += i
assert total == 15
"""
    env = execute(code)
    assert env["nums"] == [1, 2, 3, 4, 5]
    assert env["letters"] == ["a", "b", "c", "d", "e"]
    assert env["total"] == 15


def test_shuffle_expressions():
    code = """
numbers = [1, 2, 3, 4, 5]
s1 = shuffle numbers
assert len(s1) == 5
assert s1[0] in numbers

s2 = shuffled numbers
assert len(s2) == 5

shuffle numbers into s3
assert len(s3) == 5
"""
    env = execute(code)
    assert len(env["s1"]) == 5
    assert len(env["s2"]) == 5
    assert len(env["s3"]) == 5


def test_take_and_drop_expressions():
    code = """
numbers = [1, 2, 3, 4, 5]
top3 = take 3 items from numbers
assert top3 == [1, 2, 3]

rest = drop 2 items from numbers
assert rest == [3, 4, 5]
"""
    env = execute(code)
    assert env["top3"] == [1, 2, 3]
    assert env["rest"] == [3, 4, 5]


def test_multi_subject_agreement():
    code = """
a = 10
b = 20
c = 30
flag_all = False
if all of [a, b, c] are positive:
    flag_all = True
assert flag_all is True

x = 5
y = 10
flag_none = False
if none of [x, y] are zero:
    flag_none = True
assert flag_none is True
"""
    env = execute(code)
    assert env["flag_all"] is True
    assert env["flag_none"] is True
