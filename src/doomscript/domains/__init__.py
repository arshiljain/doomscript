"""DoomScript Domain Extensions System."""

from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainIR,
    DomainRuntime,
    DomainASTExporter,
)
from doomscript.domains.registry import DomainRegistry, get_domain_registry
from doomscript.domains.data import DATA_DOMAIN

__all__ = [
    "DomainContract",
    "DomainParser",
    "DomainIR",
    "DomainRuntime",
    "DomainASTExporter",
    "DomainRegistry",
    "get_domain_registry",
    "DATA_DOMAIN",
]
