"""Research Domain Pack bridging autograd, distributions, graphs, and stats into the Domain Registry."""

from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainIR,
)
from doomscript.domains.registry import get_domain_registry


class ResearchDomainParser(DomainParser):
    """Bridge parser for declarative research statements."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        from doomscript.research.registry import apply_research_normalization
        return apply_research_normalization(line)

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[DomainIR, str]:
        raise NotImplementedError("Research domain does not use block structures directly.")


class ResearchRuntime(DomainRuntime):
    """Bridge runtime for research operations."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        return ir


class ResearchDomain(DomainContract):
    """Research Domain Pack (Autograd, Graph, Distributions, Stats, Algorithms)."""

    name = "research"
    aliases = ["autograd", "stats", "graph", "math"]
    parser = ResearchDomainParser()
    runtime = ResearchRuntime()
    exporter = None

    def can_handle_line(self, line: str) -> bool:
        # Normalization handled when research mode is enabled
        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register singleton with registry
RESEARCH_DOMAIN = ResearchDomain()
get_domain_registry().register(RESEARCH_DOMAIN)

__all__ = [
    "ResearchDomain",
    "RESEARCH_DOMAIN",
    "ResearchDomainParser",
    "ResearchRuntime",
]
