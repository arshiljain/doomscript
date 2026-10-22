"""Leaf module providing shared Record and primitive core data structures.

Decoupled from high-level runtime and domain packages to prevent circular imports.
"""

from typing import Any, Dict


class Record(dict):
    """
    A dictionary that allows attribute-style access (e.g. record's field).
    Allows player's health = 100 and player['health'] interchangeably.
    Prioritizes dictionary keys over dict methods (e.g. player.items returns the field).
    """

    def __getattribute__(self, key: str) -> Any:
        if not key.startswith("__") and key in self:
            val = self[key]
            if isinstance(val, dict) and not isinstance(val, Record):
                val = Record(val)
                self[key] = val
            return val
        return super().__getattribute__(key)

    def __getattr__(self, key: str) -> Any:
        try:
            val = self[key]
            if isinstance(val, dict) and not isinstance(val, Record):
                val = Record(val)
                self[key] = val
            return val
        except KeyError:
            raise AttributeError(f"Record has no field '{key}'") from None

    def __setattr__(self, key: str, value: Any) -> None:
        self[key] = value

    def __delattr__(self, key: str) -> None:
        try:
            del self[key]
        except KeyError:
            raise AttributeError(f"Record has no field '{key}'") from None
