"""
DoomScript Research Engine: Postgraduate & PhD Scientific Computing Package
"""

from .backend import (
    ResearchRNG,
    ResearchSession,
    get_active_session,
    set_active_session,
    UnsupportedBackendOperationError,
)

__all__ = [
    "ResearchRNG",
    "ResearchSession",
    "get_active_session",
    "set_active_session",
    "UnsupportedBackendOperationError",
]
