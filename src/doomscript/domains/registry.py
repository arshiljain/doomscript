from __future__ import annotations
from typing import Dict, List, Optional, Set
from doomscript.domains.base import DomainContract, DomainIR


class DomainRegistry:
    """Registry coordinating available domain packs, namespaces, and dispatch."""

    def __init__(self):
        self._domains: Dict[str, DomainContract] = {}
        self._alias_map: Dict[str, str] = {}
        self._active_domains: Set[str] = set()
        self._specs: Dict[str, DomainIR] = {}
        self._spec_counter: int = 0

    def register(self, domain: DomainContract) -> None:
        """Registers a domain pack and its aliases."""
        primary_name = domain.name.lower()
        self._domains[primary_name] = domain
        self._alias_map[primary_name] = primary_name

        for alias in domain.aliases:
            self._alias_map[alias.lower()] = primary_name

    def has_domain(self, name: str) -> bool:
        """Checks if a domain or alias is registered."""
        return name.lower() in self._alias_map

    def get_domain(self, name: str) -> Optional[DomainContract]:
        """Resolves a domain contract by name or alias."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        if primary and primary in self._domains:
            return self._domains[primary]
        return None

    def activate(self, name: str) -> bool:
        """Activates a domain namespace for the current compilation unit."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        if primary:
            self._active_domains.add(primary)
            return True
        return False

    def is_active(self, name: str) -> bool:
        """Checks if a domain is currently active."""
        norm_name = name.lower()
        primary = self._alias_map.get(norm_name)
        return primary in self._active_domains if primary else False

    def reset_active(self) -> None:
        """Resets active domains between compilation runs."""
        self._active_domains.clear()

    def store_spec(self, ir: DomainIR) -> str:
        """Stores a validated DomainIR spec and returns a unique spec identifier."""
        self._spec_counter += 1
        spec_id = f"ds_spec_{self._spec_counter}"
        self._specs[spec_id] = ir
        return spec_id

    def get_spec(self, spec_id: str) -> Optional[DomainIR]:
        """Retrieves a DomainIR spec by its unique identifier."""
        return self._specs.get(spec_id)

    @property
    def specs(self) -> Dict[str, DomainIR]:
        """Returns dictionary of stored specs."""
        return self._specs

    def get_spec_by_name(self, name: str) -> Optional[DomainIR]:
        """Retrieves a spec by its human-assigned name attribute."""
        for s in self._specs.values():
            if hasattr(s, "name") and s.name == name:
                return s
        return None

    def clear_specs(self) -> None:
        """Clears stored DomainIR specs."""
        self._specs.clear()

    def get_active_domains(self) -> List[DomainContract]:
        """Returns all currently active domain instances."""
        return [self._domains[name] for name in self._active_domains if name in self._domains]

    def find_domain_for_line(self, line: str) -> Optional[DomainContract]:
        """Finds a domain capable of handling the line. Checks active domains first, then all registered."""
        # 1. Check active domains
        for name in self._active_domains:
            domain = self._domains.get(name)
            if domain and domain.can_handle_line(line):
                if domain.parser.parse_inspect(line, 0) is not None or domain.parser.parse_operation(line, 0) is not None:
                    return domain

        # 2. Check all registered domains (for auto-activation / fallback)
        for domain in self._domains.values():
            if domain.can_handle_line(line):
                if domain.parser.parse_inspect(line, 0) is not None or domain.parser.parse_operation(line, 0) is not None:
                    return domain

        return None

    def find_domain_for_block(self, header: str) -> Optional[DomainContract]:
        """Finds a domain capable of handling the block header."""
        for name in self._active_domains:
            domain = self._domains.get(name)
            if domain and domain.can_handle_block(header):
                return domain

        for domain in self._domains.values():
            if domain.can_handle_block(header):
                return domain

        return None


# Global registry singleton
_GLOBAL_DOMAIN_REGISTRY = DomainRegistry()


def get_domain_registry() -> DomainRegistry:
    """Returns the process-wide global DomainRegistry instance."""
    return _GLOBAL_DOMAIN_REGISTRY
