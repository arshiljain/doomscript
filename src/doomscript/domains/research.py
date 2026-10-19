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


from doomscript.domains.matcher import VerbSpec


class ResearchDomain(DomainContract):
    """Research Domain Pack (Autograd, Graph, Distributions, Stats, Algorithms)."""

    name = "research"
    aliases = ["autograd", "stats", "graph_research", "math"]
    description = "Research mathematical toolkit, automatic differentiation, statistical distributions, and hypothesis testing"
    parser = ResearchDomainParser()
    runtime = ResearchRuntime()
    exporter = None
    capabilities = ["autograd", "differentiation", "distributions", "hypothesis_testing"]
    optional_dependencies = ["numpy", "scipy", "torch"]

    verbs = [
        VerbSpec(
            name="gradient_of",
            pattern="gradient of {fn_name:ident} at {x_expr:expr} into {target:ident}",
            arg_schema={"fn_name": "ident", "x_expr": "expr", "target": "ident"},
            returns="float",
            description="Evaluate numerical or reverse-mode automatic differentiation gradient",
        ),
        VerbSpec(
            name="differentiate",
            pattern="differentiate {expr:expr} with respect to {var:ident} into {target:ident}",
            arg_schema={"expr": "expr", "var": "ident", "target": "ident"},
            returns="Any",
            description="Symbolic differentiation with respect to target variable",
        ),
        VerbSpec(
            name="simulate_distribution",
            pattern="simulate distribution {dist:ident} with {params:expr} into {target:ident}",
            arg_schema={"dist": "ident", "params": "expr", "target": "ident"},
            returns="Collection",
            description="Generate random variables from named distribution",
        ),
        VerbSpec(
            name="confidence_interval",
            pattern="confidence interval of {data:ident} [at {level:expr}] into {target:ident}",
            arg_schema={"data": "ident", "level": "expr", "target": "ident"},
            defaults={"level": 0.95},
            returns="Record",
            description="Compute Student-t or normal confidence intervals",
        ),
    ]

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
