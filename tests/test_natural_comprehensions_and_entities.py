import pytest
from doomscript.compiler.engine import execute

def test_inline_entity_instantiations():
    code = """
a Profile has bio
a User has name, age, tags, profile

# 1. Inline entities in lists
users = [a User with name "Alice", age 30, a User with name "Bob", age 25]
assert count of users == 2
assert users[0].name == "Alice"
assert users[1].age == 25

# 2. Inline entities in function calls
to greet with user:
    return "Hello, " + user's name

msg = greet(a User with name "Charlie", age 40)
assert msg == "Hello, Charlie"

# 3. Inline bare entities in lists
roles = [a User, a Profile]
assert count of roles == 2

# 4. Nested inline entities
u_nested = a User with name "Frank", profile (a Profile with bio "Dev")
assert u_nested.profile.bio == "Dev"
"""
    env = execute(code)
    assert env["msg"] == "Hello, Charlie"


def test_prose_comprehensions():
    code = """
a User has name, age
users = [a User with name "Alice", age 30, a User with name "Bob", age 25]

# 1. Bracketed prose comprehension
names1 = [the name of each user in users]
assert names1 == ["Alice", "Bob"]

# 2. Bracketed with condition
older_names1 = [the name of each user in users where user's age > 26]
assert older_names1 == ["Alice"]

# 3. Without 'the'
ages1 = [age of each user in users]
assert ages1 == [30, 25]

# 4. Statement assignment
user_names is the name of each user in users
assert user_names == ["Alice", "Bob"]

# 5. Statement assignment with condition
older_user_names is the name of each user in users where user's age > 26
assert older_user_names == ["Alice"]
"""
    env = execute(code)
    assert env["older_user_names"] == ["Alice"]


def test_comprehension_natural_ranges():
    code = """
squares = a list of x * x for each x in 1 to 5
assert squares == [1, 4, 9, 16, 25]

evens = [x for each x in 1 to 10 where x is even]
assert evens == [2, 4, 6, 8, 10]

odds = [x for each x in 1 through 5 where x is odd]
assert odds == [1, 3, 5]

acc = 0
for i in 1 to 5:
    acc = acc + i
assert acc == 15
"""
    env = execute(code)
    assert env["squares"] == [1, 4, 9, 16, 25]
    assert env["evens"] == [2, 4, 6, 8, 10]
    assert env["odds"] == [1, 3, 5]
    assert env["acc"] == 15
