"""
Comprehensive Regression Suite for the 100 Natural English Syntax Paradigms in DoomScript.
Verifies all 10 clusters (Items 1 - 100) execute end-to-end without syntax errors or runtime regressions.
"""

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

# in-place filter <col> where
orders = [{"amt": 50}, {"amt": 150}]
filter orders where amt > 100
assert count of orders == 1
assert orders[0]["amt"] == 150

# sort it by prop descending
sort users by age descending
assert users[0].name == "Charlie"

# reverse it
nums = [1, 2, 3]
reverse it
assert nums == [3, 2, 1]

# shuffle it
items = [1, 2, 3, 4, 5]
shuffle it
assert count of items == 5

# unique it / deduplicate it
dup_nums = [1, 2, 2, 3, 3, 3]
unique it
assert dup_nums == [1, 2, 3]

# arithmetic mutation via pronoun
x = 10
increase it by 5
assert x == 15
decrease it by 3
assert x == 12
double it
assert x == 24
halve it
assert x == 12

# add/remove element via pronoun
lst = [10, 20]
add 30 to it
assert lst == [10, 20, 30]
remove 20 from it
assert lst == [10, 30]
"""
    env = execute(code)
    assert env["x"] == 12
    assert env["dup_nums"] == [1, 2, 3]
    assert env["lst"] == [10, 30]


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

flag_none = False
if none of items are expired:
    flag_none = True
assert flag_none is True

servers = [{"online": True}, {"online": True}, {"online": True}, {"online": False}]
flag_at_least = False
if at least 3 servers are online:
    flag_at_least = True
assert flag_at_least is True

flag_at_most = False
if at most 1 servers are online:
    flag_at_most = False
otherwise:
    flag_at_most = True
assert flag_at_most is True

flag_exactly = False
if exactly 3 servers are online:
    flag_exactly = True
assert flag_exactly is True

votes = [{"approved": True}, {"approved": True}, {"approved": False}]
flag_half = False
if more than half of votes are approved:
    flag_half = True
assert flag_half is True

flag_majority = False
if majority of votes are approved:
    flag_majority = True
assert flag_majority is True
"""
    env = execute(code)
    assert env["flag_any"] is True
    assert env["flag_every"] is True
    assert env["flag_no"] is True
    assert env["flag_majority"] is True


def test_cluster4_natural_math_and_stats():
    code = """
sq = square of 6
cb = cube of 4
sr = square root of 49
abs_val = absolute value of -15
assert sq == 36
assert cb == 64
assert sr == 7.0
assert abs_val == 15

nums = [10, 20, 30, 40, 50]
s = sum of nums
avg = average of nums
med = median of nums
mn = minimum of nums
mx = maximum of nums
assert s == 150
assert avg == 30.0
assert med == 30
assert mn == 10
assert mx == 50

mode_nums = [1, 2, 2, 3]
md = mode of mode_nums
assert md == 2
"""
    env = execute(code)
    assert env["sq"] == 36
    assert env["cb"] == 64
    assert env["md"] == 2


def test_cluster5_multiples_and_percentages():
    code = """
num = 21
flag_mult = False
if num is a multiple of 7:
    flag_mult = True
assert flag_mult is True

flag_div = False
if num is divisible by 3:
    flag_div = True
assert flag_div is True

flag_non_neg = False
z = 0
if z is non-negative:
    flag_non_neg = True
assert flag_non_neg is True

flag_non_pos = False
if z is non-positive:
    flag_non_pos = True
assert flag_non_pos is True

flag_strict_pos = False
p = 5
if p is strictly positive:
    flag_strict_pos = True
assert flag_strict_pos is True

flag_strict_neg = False
n = -5
if n is strictly negative:
    flag_strict_neg = True
assert flag_strict_neg is True

flag_within = False
val = 102
if val is within 5% of 100:
    flag_within = True
assert flag_within is True

flag_roughly = False
approx = 99.8
if approx is roughly 100:
    flag_roughly = True
assert flag_roughly is True

price = 200
increase price by 15%
assert price == 230.0
decrease price by 10%
assert price == 207.0
"""
    env = execute(code)
    assert env["flag_mult"] is True
    assert env["flag_within"] is True
    assert env["price"] == 207.0


def test_cluster6_string_transforms():
    code = """
capitalize "alice" into cap_name
assert cap_name == "Alice"

titlecase "doom script" into titled
assert titled == "Doom Script"

slugify "DoomScript 2026 Release!" into my_slug
assert my_slug == "doomscript-2026-release"

truncate "Supercalifragilistic" to 5 characters into short_str
assert short_str == "Super"

strip "  hello world  " into stripped
assert stripped == "hello world"

collapse whitespace in "  hello    world   " into collapsed
assert collapsed == "hello world"

w_cnt = word count of "the quick brown fox"
assert w_cnt == 4

c_cnt = character count of "abcdef"
assert c_cnt == 6

s_cnt = sentence count of "Hello world! This is DoomScript. Are you ready?"
assert s_cnt == 3

pad "42" with "0" to 5 characters into padded
assert padded == "00042"
"""
    env = execute(code)
    assert env["cap_name"] == "Alice"
    assert env["titled"] == "Doom Script"
    assert env["my_slug"] == "doomscript-2026-release"
    assert env["short_str"] == "Super"
    assert env["stripped"] == "hello world"
    assert env["collapsed"] == "hello world"
    assert env["w_cnt"] == 4
    assert env["c_cnt"] == 6
    assert env["s_cnt"] == 3
    assert env["padded"] == "00042"


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

x_top = first 2 items of nums
assert x_top == [1, 2]

x_last = last 2 items of nums
assert x_last == [5, 6]

chunk nums into groups of 2 into chunked
assert chunked == [[1, 2], [3, 4], [5, 6]]

flatten [[1, 2], [3, 4]] into flat
assert flat == [1, 2, 3, 4]

zip [1, 2] and ["a", "b"] into zipped
assert zipped == [[1, "a"], [2, "b"]]

interleave [1, 2] and [10, 20] into interleaved
assert interleaved == [1, 10, 2, 20]
"""
    env = execute(code)
    assert env["top3"] == [1, 2, 3]
    assert env["tail2"] == [5, 6]
    assert env["chunked"] == [[1, 2], [3, 4], [5, 6]]
    assert env["flat"] == [1, 2, 3, 4]
    assert env["zipped"] == [[1, "a"], [2, "b"]]
    assert env["interleaved"] == [1, 10, 2, 20]


def test_cluster8_conversational_control_flow():
    code = """
flag_unless = False
x = 5
unless x > 10:
    flag_unless = True
assert flag_unless is True

if True:
    do nothing

c = 0
for each i in [1, 2, 3]:
    c = i
    if i == 2:
        stop loop
assert c == 2

s = 0
for each i in [1, 2, 3]:
    if i == 2:
        skip to next
    s = s + i
assert s == 4

count_rep = 0
repeat until count_rep == 3:
    count_rep = count_rep + 1
assert count_rep == 3

flag_given = False
val = 10
given that val == 10:
    flag_given = True
assert flag_given is True

flag_provided = False
provided that val == 10:
    flag_provided = True
assert flag_provided is True

err_handled = "no"
try:
    z = 1 / 0
in case of error:
    err_handled = "yes"
assert err_handled == "yes"

w_count = 0
whenever w_count < 3:
    w_count = w_count + 1
assert w_count == 3

to test_exit with arg:
    if arg == 1:
        exit function
    return 100

res = test_exit(1)
assert res is None
"""
    env = execute(code)
    assert env["flag_unless"] is True
    assert env["c"] == 2
    assert env["s"] == 4
    assert env["count_rep"] == 3
    assert env["err_handled"] == "yes"
    assert env["w_count"] == 3


def test_cluster9_dictionary_and_records():
    code = """
r1 = {"a": 1, "b": 2}
r2 = {"c": 3}
merge r1 and r2 into r3
assert r3 == {"a": 1, "b": 2, "c": 3}

invert {"x": 10, "y": 20} into r_inv
assert r_inv[10] == "x"

ks = keys of r3
vs = values of r3
assert "a" in ks and "b" in ks and "c" in ks
assert 1 in vs and 2 in vs and 3 in vs

flag_has_key = False
if r3 has key "a":
    flag_has_key = True
assert flag_has_key is True

flag_has_field = False
if r3 has field "b":
    flag_has_field = True
assert flag_has_field is True

remove key "b" from r3
assert "b" not in r3

remove field "c" from r3
assert "c" not in r3

r_named = {"old_name": "DoomScript"}
rename key "old_name" to "new_name" in r_named
assert "new_name" in r_named
assert "old_name" not in r_named

data = {"id": 1, "title": "Audit", "secret": "xyz"}
pick fields ["id", "title"] from data into public_data
assert public_data["id"] == 1
assert public_data["title"] == "Audit"
assert "secret" not in public_data
"""
    env = execute(code)
    assert env["r3"] == {"a": 1}
    assert env["r_inv"][10] == "x"
    assert env["public_data"]["id"] == 1


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

diff_hours = hours between "2026-10-01 12:00:00" and "2026-10-01 15:30:00"
assert diff_hours == 3.5

flag_weekend = False
if "2026-10-24" is weekend:
    flag_weekend = True
assert flag_weekend is True

flag_weekday = False
if "2026-10-23" is weekday:
    flag_weekday = True
assert flag_weekday is True

fut = 5 days from now
pst = 5 days ago
assert fut is not None
assert pst is not None

formatted = format date "2026-10-23" as "%B %d, %Y"
assert "October" in formatted
"""
    env = execute(code)
    assert env["diff_days"] == 9
    assert env["diff_hours"] == 3.5
    assert env["flag_weekend"] is True
    assert env["flag_weekday"] is True
    assert "October" in env["formatted"]
