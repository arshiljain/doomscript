"""Optimization & Operations Research Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec
from doomscript.domains.opt.parser import OptDomainParser
from doomscript.domains.opt.runtime import (
    OptRuntime,
    SimplexSolver,
    parse_linear_expression,
    parse_constraint,
    solve_linear_program,
)
from doomscript.domains.opt.exporter import OptASTExporter
from doomscript.domains.registry import get_domain_registry


class OptDomain(DomainContract):
    """Optimization & Operations Research domain pack providing linear programming and Simplex solving."""

    name = "opt"
    aliases = ["optimization", "operations_research", "lp"]
    parser = OptDomainParser()
    runtime = OptRuntime()
    exporter = OptASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("solve linear program ") or s.startswith("solve ")

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return (
            (
                s.startswith("linear program ")
                or s.startswith("optimize ")
                or s.startswith("maximize ")
                or s.startswith("minimize ")
            )
            and (":" in s)
        )


# Register with central registry
OPT_DOMAIN = OptDomain()
get_domain_registry().register(OPT_DOMAIN)

__all__ = [
    "OptDomain",
    "OPT_DOMAIN",
    "LinearProgramSpec",
    "SolveLPSpec",
    "OptDomainParser",
    "OptRuntime",
    "OptASTExporter",
    "SimplexSolver",
    "parse_linear_expression",
    "parse_constraint",
    "solve_linear_program",
]
