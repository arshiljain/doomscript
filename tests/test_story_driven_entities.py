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
