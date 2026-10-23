"""
Tests for Natural English Classes and Object-Oriented Syntax in DoomScript.
Verifies removal of mandatory self and Python-centric __init__ boilerplate.
"""

import pytest
from doomscript.compiler.engine import execute


def test_init_without_self_parameter(capsys):
    code = """
define a Counter:
    to init with initial:
        my count = initial

    to increment:
        my count += 1

    to get_count:
        return my count

c = Counter(10)
c.increment()
c.increment()
say c.get_count()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "12"


def test_init_with_explicit_self(capsys):
    code = """
class Point:
    to init with self, x, y:
        self.x = x
        self.y = y

    to coords with self:
        return (self.x, self.y)

p = Point(3, 4)
say p.coords()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "(3, 4)"


def test_constructor_keyword_syntax(capsys):
    code = """
class Book:
    constructor with title, author:
        my title = title
        my author = author

    to summary:
        return my title + " by " + my author

b = Book("The Hobbit", "J.R.R. Tolkien")
say b.summary()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "The Hobbit by J.R.R. Tolkien"


def test_alternative_constructor_names(capsys):
    code = """
class User:
    to create with username:
        my username = username

class Profile:
    to initialize with bio:
        my bio = bio

class Config:
    to setup with mode:
        my mode = mode

u = User("alice")
p = Profile("coder")
c = Config("debug")

say u.username
say p.bio
say c.mode
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["alice", "coder", "debug"]


def test_inheritance_and_super_constructors(capsys):
    code = """
define an Animal:
    to init with name:
        my name = name

    to speak with sound:
        return my name + " says " + sound

define a Dog that is an Animal:
    to init with name, breed:
        base init with name
        my breed = breed

    to bark:
        return my speak("woof")

define a Cat that is an Animal:
    to init with name:
        super init with name

    to meow:
        return my speak("meow")

d = Dog("Rex", "Shepherd")
c = Cat("Whiskers")

say d.bark()
say d.breed
say c.meow()
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "Rex says woof",
        "Shepherd",
        "Whiskers says meow"
    ]


def test_top_level_function_named_create_is_not_init(capsys):
    # Top-level 'to create' must remain a normal function, not converted to __init__
    code = """
to create with val:
    return val * 2

result = create(21)
say result
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "42"


def test_natural_entity_assignment_and_construction():
    code = """
a Customer has name, email, balance = 100.0

# 1. c1 = a Customer with ...
c1 = a Customer with name "Alice", email "a@a.com"
assert c1's name == "Alice"
assert c1's balance == 100.0

# 2. c2 = new Customer with ...
c2 = new Customer with name "Bob", balance 150.0
assert c2's name == "Bob"
assert c2's balance == 150.0

# 3. c3 = Customer with ...
c3 = Customer with name "Charlie", balance 250.0
assert c3's balance == 250.0

# 4. set c4 to a Customer with ...
set c4 to a Customer with name "Dave"
assert c4's name == "Dave"
assert c4's balance == 100.0

# 5. c5 is a Customer with ...
c5 is a Customer with name "Eve"
assert c5's name == "Eve"

# 6. c6 = a Customer (empty / schema defaults)
c6 = a Customer
assert c6's balance == 100.0

# 7. add a Customer with ... to collection
customers = []
add a Customer with name "Frank", balance 50 to customers
add new Customer with name "Grace", balance 75 to customers
add a Customer to customers
assert len(customers) == 3
assert customers[0]'s name == "Frank"
assert customers[1]'s balance == 75
assert customers[2]'s balance == 100.0

# 8. return entity from function
to build_vip with n:
    return a Customer with name n, balance 5000.0

vip = build_vip("Heidi")
assert vip's name == "Heidi"
assert vip's balance == 5000.0
"""
    env = execute(code)
    assert env["vip"].name == "Heidi"
    assert len(env["customers"]) == 3

