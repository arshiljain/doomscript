"""Visualization Domain Pack bridging Grammar-of-Graphics into the Domain Registry."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    DomainIR,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.viz.spec import PlotSpec
from doomscript.viz.builder import PlotBuilder


class VizDomainParser(DomainParser):
    """Bridge parser for visualization domain."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[DomainIR, str]:
        raise NotImplementedError("Viz blocks are parsed by the specialized visual grammar.")


class VizRuntime(DomainRuntime):
    """Bridge runtime for visualization execution."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if isinstance(ir, PlotBuilder):
            return ir.build()
        return ir


class VizASTExporter(DomainASTExporter):
    """Bridge exporter translating PlotSpec into native Lets-Plot AST."""

    def to_ast(self, ir: DomainIR, target_var: str = "p") -> Tuple[Set[str], List[ast.stmt]]:
        from doomscript.viz.exporter import LetsPlotExporter
        if isinstance(ir, PlotSpec):
            exporter = LetsPlotExporter()
            imports, assign_node = exporter.to_ast(ir, var_name=target_var)
            return imports, [assign_node]
        return set(), []


class VizDomain(DomainContract):
    """Visualization Domain Pack (Grammar of Graphics, Lets-Plot)."""

    name = "viz"
    aliases = ["visualization", "graphics", "plots", "plot"]
    parser = VizDomainParser()
    runtime = VizRuntime()
    exporter = VizASTExporter()

    def can_handle_line(self, line: str) -> bool:
        # Handled by phrase normalizer
        return False

    def can_handle_block(self, header: str) -> bool:
        # Handled by phrase normalizer
        return False


# Register singleton with registry
VIZ_DOMAIN = VizDomain()
get_domain_registry().register(VIZ_DOMAIN)

__all__ = [
    "VizDomain",
    "VIZ_DOMAIN",
    "VizDomainParser",
    "VizRuntime",
    "VizASTExporter",
]
