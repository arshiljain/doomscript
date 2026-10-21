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


def stem_verb(verb: str) -> str:
    """Stems present participle (-ing) or 3rd-person (-s) verb to base form."""
    v = verb.lower()
    if v.endswith("eiving"):
        return v[:-6] + "eive"
    if v.endswith("ing"):
        s = v[:-3]
        if len(s) > 2 and s[-1] == s[-2]:
            return s[:-1]
        if s.endswith(("v", "c", "z", "th", "clos", "creat", "plac", "sav", "updat")):
            return s + "e"
        return s
    if v.endswith("s") and not v.endswith("ss"):
        return v[:-1]
    return v


_PENDING_RELATIONS: List[Tuple[str, str, str, str, str]] = []
_ENTITY_REGISTRY: Dict[str, type] = {}


def _apply_has_many(owner_cls: type, col_name: str, target_cls: type, inv_name: str) -> None:
    if "_relations_has_many" not in owner_cls.__dict__:
        owner_cls._relations_has_many = dict(owner_cls._relations_has_many)
    owner_cls._relations_has_many[col_name] = inv_name

    if "_relations_belongs_to" not in target_cls.__dict__:
        target_cls._relations_belongs_to = dict(target_cls._relations_belongs_to)
    target_cls._relations_belongs_to[inv_name] = col_name


def _apply_has_one(owner_cls: type, prop_name: str, target_cls: type, inv_name: str) -> None:
    if "_relations_has_one" not in owner_cls.__dict__:
        owner_cls._relations_has_one = dict(owner_cls._relations_has_one)
    owner_cls._relations_has_one[prop_name] = inv_name

    if "_relations_has_one" not in target_cls.__dict__:
        target_cls._relations_has_one = dict(target_cls._relations_has_one)
    target_cls._relations_has_one[inv_name] = prop_name


def _resolve_pending_relations() -> None:
    global _PENDING_RELATIONS
    remaining = []
    for rel_type, owner, a, target, b in _PENDING_RELATIONS:
        o_cls = _ENTITY_REGISTRY.get(owner) if isinstance(owner, str) else owner
        t_cls = _ENTITY_REGISTRY.get(target) if isinstance(target, str) else target
        if o_cls is not None and t_cls is not None:
            if rel_type == "has_many":
                _apply_has_many(o_cls, a, t_cls, b)
            elif rel_type == "has_one":
                _apply_has_one(o_cls, a, t_cls, b)
            elif rel_type == "belongs_to":
                _apply_has_many(t_cls, b, o_cls, a)
        else:
            remaining.append((rel_type, owner, a, target, b))
    _PENDING_RELATIONS = remaining


class DoomEntity(Record):
    """
    Base class for all story-driven domain entities in DoomScript.
    Inherits Record attribute-style access and adds relationship sync and state lifecycle.
    """

    _relations_belongs_to: Dict[str, str] = {}
    _relations_has_many: Dict[str, str] = {}
    _relations_has_one: Dict[str, str] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _ENTITY_REGISTRY[cls.__name__] = cls
        _resolve_pending_relations()

    def __init__(self, initial_data: Optional[Dict[str, Any]] = None, **kwargs):
        _resolve_pending_relations()
        object.__setattr__(self, "_in_sync", False)
        # Ensure relation dictionaries are per-class
        if "_relations_belongs_to" not in self.__class__.__dict__:
            self.__class__._relations_belongs_to = dict(self.__class__._relations_belongs_to)
        if "_relations_has_many" not in self.__class__.__dict__:
            self.__class__._relations_has_many = dict(self.__class__._relations_has_many)
        if "_relations_has_one" not in self.__class__.__dict__:
            self.__class__._relations_has_one = dict(self.__class__._relations_has_one)

        super().__init__()

        # Auto-initialize relationship attributes
        for col_name, inv_name in self.__class__._relations_has_many.items():
            self[col_name] = RelationshipList(owner=self, inverse_attr=inv_name)
        for prop_name in self.__class__._relations_belongs_to.keys():
            self[prop_name] = None
        for prop_name in self.__class__._relations_has_one.keys():
            self[prop_name] = None

        data = initial_data or {}
        if isinstance(data, dict):
            for k, v in data.items():
                self[k] = v
        for k, v in kwargs.items():
            self[k] = v

    def __getattr__(self, key: str) -> Any:
        if key.startswith("_"):
            raise AttributeError(f"DoomEntity has no field '{key}'")

        try:
            return super().__getattr__(key)
        except AttributeError:
            has_many_map = getattr(self.__class__, "_relations_has_many", {})
            if key in has_many_map:
                inv_name = has_many_map[key]
                col = RelationshipList(owner=self, inverse_attr=inv_name)
                self[key] = col
                return col
            belongs_to_map = getattr(self.__class__, "_relations_belongs_to", {})
            if key in belongs_to_map:
                self[key] = None
                return None
            has_one_map = getattr(self.__class__, "_relations_has_one", {})
            if key in has_one_map:
                self[key] = None
                return None

            cls = self.__class__
            # Common banking/workflow action synonyms (e.g. deposit <-> receive)
            common_synonyms = {
                "deposit": "receive",
                "depositing": "receive",
                "receive": "deposit",
                "receiving": "deposit",
                "spend": "withdraw",
                "spending": "withdraw",
            }
            if key in common_synonyms:
                syn = common_synonyms[key]
                if hasattr(cls, syn):
                    return getattr(self, syn)

            # Automatic verb participle alias resolution (e.g. acc.receiving -> acc.receive)
            stem = stem_verb(key)
            if stem != key and hasattr(cls, stem):
                return getattr(self, stem)
            if hasattr(cls, key + "ing"):
                return getattr(self, key + "ing")

            raise

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


def ds_register_relation_has_many(owner_cls, col_name: str, target_cls, inv_name: str) -> None:
    """Registers a one-to-many relationship between owner_cls and target_cls (order-independent)."""
    o_name = owner_cls.__name__ if isinstance(owner_cls, type) else str(owner_cls)
    t_name = target_cls.__name__ if isinstance(target_cls, type) else str(target_cls)
    if isinstance(owner_cls, type):
        _ENTITY_REGISTRY[o_name] = owner_cls
    if isinstance(target_cls, type):
        _ENTITY_REGISTRY[t_name] = target_cls
    _PENDING_RELATIONS.append(("has_many", o_name, col_name, t_name, inv_name))
    _resolve_pending_relations()


def ds_register_relation_belongs_to(owner_cls, inv_name: str, target_cls, col_name: str) -> None:
    """Registers a belongs-to relationship between owner_cls and target_cls (order-independent)."""
    o_name = owner_cls.__name__ if isinstance(owner_cls, type) else str(owner_cls)
    t_name = target_cls.__name__ if isinstance(target_cls, type) else str(target_cls)
    if isinstance(owner_cls, type):
        _ENTITY_REGISTRY[o_name] = owner_cls
    if isinstance(target_cls, type):
        _ENTITY_REGISTRY[t_name] = target_cls
    _PENDING_RELATIONS.append(("belongs_to", o_name, inv_name, t_name, col_name))
    _resolve_pending_relations()


def ds_register_relation_has_one(owner_cls, prop_name: str, target_cls, inv_name: str) -> None:
    """Registers a one-to-one relationship between owner_cls and target_cls (order-independent)."""
    o_name = owner_cls.__name__ if isinstance(owner_cls, type) else str(owner_cls)
    t_name = target_cls.__name__ if isinstance(target_cls, type) else str(target_cls)
    if isinstance(owner_cls, type):
        _ENTITY_REGISTRY[o_name] = owner_cls
    if isinstance(target_cls, type):
        _ENTITY_REGISTRY[t_name] = target_cls
    _PENDING_RELATIONS.append(("has_one", o_name, prop_name, t_name, inv_name))
    _resolve_pending_relations()
