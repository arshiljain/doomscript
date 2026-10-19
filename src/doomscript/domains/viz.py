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


from doomscript.domains.matcher import VerbSpec


class VizDomain(DomainContract):
    """Visualization Domain Pack (Grammar of Graphics, Lets-Plot)."""

    name = "viz"
    aliases = ["visualization", "graphics", "plots", "plot"]
    description = "Grammar of Graphics data visualization with layers, scales, themes, and facets"
    parser = VizDomainParser()
    runtime = VizRuntime()
    exporter = VizASTExporter()
    capabilities = ["plots", "charts", "facets", "themes", "layers", "scales"]
    optional_dependencies = ["lets_plot"]

    verbs = [
        VerbSpec(
            name="explore",
            pattern="explore {dataset:ident} [to understand {focus:expr}] [into {target:ident}]",
            arg_schema={"dataset": "ident", "focus": "expr", "target": "ident"},
            returns="Record",
            description="Automated exploratory visualization and statistical insights",
        ),
        VerbSpec(
            name="show_plot",
            pattern="show {target_var:ident}",
            arg_schema={"target_var": "ident"},
            returns="None",
            description="Display interactive plot figure",
        ),
        VerbSpec(
            name="save_plot",
            pattern="save {target_var:ident} to {path_str:expr}",
            arg_schema={"target_var": "ident", "path_str": "expr"},
            returns="str",
            description="Save plot figure to PNG, SVG, or HTML file",
        ),
        VerbSpec(
            name="plot",
            pattern="plot {dataset:ident} as {geom:ident} with {params:expr} [into {target:ident}]",
            arg_schema={"dataset": "ident", "geom": "ident", "params": "expr", "target": "ident"},
            returns="Plot",
            description="Construct single-layer plot figure",
        ),
    ]

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
