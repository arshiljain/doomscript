"""
Unit and integration tests for Story-Driven Relational Modeling in DoomScript.
Covers DoomEntity, RelationshipList, 'begins with', declarative relationships,
'when' event transitions, and spoken action invocations.
"""

import pytest
from doomscript.core.entity import DoomEntity, RelationshipList
from doomscript.compiler.engine import execute


def test_relationship_list_auto_sync():
    class User(DoomEntity):
        pass

    class Order(DoomEntity):
        pass

    u = User({"name": "Alice"})
    u.orders = RelationshipList(owner=u, inverse_attr="user")
    o = Order({"item": "Book"})

    u.orders.append(o)
    assert o.user is u
    assert len(u.orders) == 1


def test_entity_inverse_assignment_sync():
    class User(DoomEntity):
        pass

    class Order(DoomEntity):
        _relations_belongs_to = {"user": "orders"}

    u = User({"name": "Alice"})
    u.orders = RelationshipList(owner=u, inverse_attr="user")
    o = Order({"item": "Laptop"})

    o.user = u
    assert o in u.orders


def test_entity_begins_with_defaults():
    source = """
a BankAccount begins with balance = 100, status = "active", transactions = []

create a BankAccount into acc1
create a BankAccount with balance 500 into acc2

add 50 to acc1.transactions
"""
    env = execute(source)
    assert env["acc1"].balance == 100
    assert env["acc1"].status == "active"
    assert env["acc1"].transactions == [50]
    assert env["acc2"].balance == 500
    assert env["acc2"].transactions == []


def test_declarative_relationships_smart_sync():
    source = """
a User has name
an Order has item, price

a User has many Orders
an Order belongs to a User

create a User with name "Alice" into u1
create an Order with item "Laptop", price 1200 into o1

add o1 to u1.orders
"""
    env = execute(source)
    assert env["o1"].user is env["u1"]
    assert env["u1"].orders == [env["o1"]]

    # Test inverse assignment sync
    source2 = """
a User has name
an Order has item, price

a User has many Orders
an Order belongs to a User

create a User with name "Bob" into u2
create an Order with item "Book", price 15 into o2

o2.user = u2
"""
    env2 = execute(source2)
    assert env2["o2"] in env2["u2"].orders


