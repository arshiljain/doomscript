import pytest
from doomscript.compiler.engine import execute

def test_cluster1_discourse_pipelines_and_pronouns():
    code = """
a User has name, age
users = [a User with name "Charlie", age 35, a User with name "Alice", age 30, a User with name "Bob", age 18]
filter it where age > 20
sort it by name
assert count of users == 2
assert users[0].name == "Alice"
assert users[1].name == "Charlie"

x = 10
increase it by 5
assert x == 15
decrease it by 3
assert x == 12
double it
assert x == 24
halve it
assert x == 12
"""
    env = execute(code)
    assert env["x"] == 12


def test_cluster2_soft_keyword_bare_assignments():
    code = """
group = "admin"
order = 42
table = [1, 2, 3]
matrix = [[1, 0], [0, 1]]
model = "gpt-4"
text = "hello world"
message = "ready"
error = "none"
status = 200
key = "auth"
value = "secret"
column = "age"
row = {"id": 1}
field = "email"

assert group == "admin"
assert order == 42
assert table == [1, 2, 3]
assert matrix == [[1, 0], [0, 1]]
assert model == "gpt-4"
assert text == "hello world"
assert message == "ready"
assert error == "none"
assert status == 200
assert key == "auth"
assert value == "secret"
assert column == "age"
assert row["id"] == 1
assert field == "email"
"""
    env = execute(code)
    assert env["group"] == "admin"
    assert env["status"] == 200


def test_cluster3_collective_quantifiers():
    code = """
orders = [{"amount": 500}, {"amount": 1500}]
flag_any = False
if any order has amount > 1000:
    flag_any = True
assert flag_any is True

users = [{"name": "A", "verified": True}, {"name": "B", "verified": True}]
flag_every = False
if every user is verified:
    flag_every = True
assert flag_every is True

items = [{"expired": False}, {"expired": False}]
flag_no = False
if no item is expired:
    flag_no = True
assert flag_no is True

flag_all = False
if all users are verified:
    flag_all = True
assert flag_all is True
"""
    env = execute(code)
    assert env["flag_any"] is True
    assert env["flag_every"] is True
    assert env["flag_no"] is True


def test_cluster4_natural_math_and_stats():
    code = """
sq = square of 5
cb = cube of 3
assert sq == 25
assert cb == 27
abs_val = absolute value of -42
assert abs_val == 42
"""
    env = execute(code)
    assert env["sq"] == 25
    assert env["cb"] == 27
    assert env["abs_val"] == 42


def test_cluster5_multiples_and_percentages():
    code = """
num = 15
flag_mult = False
if num is a multiple of 5:
    flag_mult = True
assert flag_mult is True

price = 100
increase price by 15%
assert price == 115.0
decrease price by 10%
assert price == 103.5
"""
    env = execute(code)
    assert env["price"] == 103.5


def test_cluster6_string_transforms():
    code = """
slugify "DoomScript 2026 Release!" into my_slug
assert my_slug == "doomscript-2026-release"

truncate "Supercalifragilistic" to 5 characters into short_str
assert short_str == "Super"

collapse whitespace in "  hello    world   " into collapsed
assert collapsed == "hello world"

capitalize "alice" into cap_name
assert cap_name == "Alice"

titlecase "hello world" into titled
assert titled == "Hello World"

w_cnt = word count of "the quick brown fox"
assert w_cnt == 4
"""
    env = execute(code)
    assert env["my_slug"] == "doomscript-2026-release"
    assert env["short_str"] == "Super"
    assert env["collapsed"] == "hello world"
    assert env["cap_name"] == "Alice"
    assert env["titled"] == "Hello World"
    assert env["w_cnt"] == 4


def test_cluster7_collection_slicing_and_restructuring():
    code = """
nums = [1, 2, 3, 4, 5, 6]
take first 3 items from nums into top3
assert top3 == [1, 2, 3]

take last 2 items from nums into tail2
assert tail2 == [5, 6]

drop first 2 items from nums into rest4
assert rest4 == [3, 4, 5, 6]

drop last 2 items from nums into front4
assert front4 == [1, 2, 3, 4]

chunk nums into groups of 2 into chunked
assert chunked == [[1, 2], [3, 4], [5, 6]]

zip [1, 2] and ["a", "b"] into zipped
assert zipped == [[1, "a"], [2, "b"]]
"""
    env = execute(code)
    assert env["top3"] == [1, 2, 3]
    assert env["tail2"] == [5, 6]
    assert env["rest4"] == [3, 4, 5, 6]
    assert env["chunked"] == [[1, 2], [3, 4], [5, 6]]
    assert env["zipped"] == [[1, "a"], [2, "b"]]


def test_cluster8_conversational_control_flow():
    code = """
flag_unless = False
unless 5 > 10:
    flag_unless = True
assert flag_unless is True

count_rep = 0
repeat until count_rep == 3:
    count_rep = count_rep + 1
assert count_rep == 3

flag_given = False
x = 10
given that x == 10:
    flag_given = True
assert flag_given is True
"""
    env = execute(code)
    assert env["flag_unless"] is True
    assert env["count_rep"] == 3
    assert env["flag_given"] is True


def test_cluster9_dictionary_and_records():
    code = """
r1 = {"a": 1, "b": 2}
r2 = {"c": 3}
merge r1 and r2 into r3
assert r3 == {"a": 1, "b": 2, "c": 3}

invert {"x": 10, "y": 20} into r_inv
assert r_inv[10] == "x"

flag_has_key = False
if r3 has key "a":
    flag_has_key = True
assert flag_has_key is True

remove key "b" from r3
assert "b" not in r3
"""
    env = execute(code)
    assert env["r3"] == {"a": 1, "c": 3}
    assert env["r_inv"][10] == "x"


def test_cluster10_date_and_temporal():
    code = """
today into cur_day
yesterday into prev_day
tomorrow into next_day
assert cur_day != ""
assert prev_day != ""
assert next_day != ""

diff_days = days between "2026-10-01" and "2026-10-10"
assert diff_days == 9
"""
    env = execute(code)
    assert env["diff_days"] == 9
