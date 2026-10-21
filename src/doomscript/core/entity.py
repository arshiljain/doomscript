"""Core entity and relationship runtime structures for DoomScript.

Provides DoomEntity and RelationshipList to support story-driven domain entities,
declarative relationships (has many, belongs to, has one), and bidirectional sync.
"""

from typing import Any, Dict, List, Optional
import copy

from doomscript.core.record import Record


class RelationshipList(list):
    """
    A list managing a one-to-many relationship collection.
    Automatically assigns inverse references when items are appended.
    """

    def __init__(self, owner: Any, inverse_attr: str, iterable=None):
        super().__init__(iterable or [])
        self.owner = owner
        self.inverse_attr = inverse_attr

    def append(self, item: Any) -> None:
        if item not in self:
            super().append(item)
        if item is not None and self.inverse_attr:
            if getattr(item, self.inverse_attr, None) is not self.owner:
                in_sync = getattr(item, "_in_sync", False)
                if not in_sync:
                    object.__setattr__(item, "_in_sync", True)
                    try:
                        setattr(item, self.inverse_attr, self.owner)
                    finally:
                        object.__setattr__(item, "_in_sync", False)

    def extend(self, items) -> None:
        for it in items:
            self.append(it)


class DoomEntity(Record):
    """
    Base class for all story-driven domain entities in DoomScript.
    Inherits Record attribute-style access and adds relationship sync and state lifecycle.
    """

    _relations_belongs_to: Dict[str, str] = {}
    _relations_has_many: Dict[str, str] = {}
    _relations_has_one: Dict[str, str] = {}

    def __init__(self, initial_data: Optional[Dict[str, Any]] = None, **kwargs):
        object.__setattr__(self, "_in_sync", False)
        # Ensure relation dictionaries are per-class
        if "_relations_belongs_to" not in self.__class__.__dict__:
            self.__class__._relations_belongs_to = dict(self.__class__._relations_belongs_to)
        if "_relations_has_many" not in self.__class__.__dict__:
            self.__class__._relations_has_many = dict(self.__class__._relations_has_many)
        if "_relations_has_one" not in self.__class__.__dict__:
            self.__class__._relations_has_one = dict(self.__class__._relations_has_one)

        super().__init__()
        data = initial_data or {}
        if isinstance(data, dict):
            for k, v in data.items():
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("_in_sync",):
            object.__setattr__(self, key, value)
            return

        # Check belongs_to inverse sync
        belongs_to_map = getattr(self.__class__, "_relations_belongs_to", {})
        if key in belongs_to_map and not getattr(self, "_in_sync", False):
            inverse_collection_name = belongs_to_map[key]
            if value is not None and hasattr(value, inverse_collection_name):
                col = getattr(value, inverse_collection_name)
                if isinstance(col, list) and self not in col:
                    object.__setattr__(self, "_in_sync", True)
                    try:
                        col.append(self)
                    finally:
                        object.__setattr__(self, "_in_sync", False)

        # Check has_one inverse sync
        has_one_map = getattr(self.__class__, "_relations_has_one", {})
        if key in has_one_map and not getattr(self, "_in_sync", False):
            inverse_attr = has_one_map[key]
            if value is not None and hasattr(value, inverse_attr) and getattr(value, inverse_attr) is not self:
                object.__setattr__(self, "_in_sync", True)
                try:
                    setattr(value, inverse_attr, self)
                finally:
                    object.__setattr__(self, "_in_sync", False)

        super().__setattr__(key, value)
