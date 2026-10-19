"""Testing & Algorithm Analysis (DSA) Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.dsa.spec import BenchmarkSpec, ComplexityReport
from doomscript.domains.dsa.parser import DsaDomainParser
from doomscript.domains.dsa.runtime import (
    DsaRuntime,
    run_benchmark,
    fit_complexity,
    profile_memory_of_function,
)
from doomscript.domains.dsa.exporter import DsaASTExporter
from doomscript.domains.registry import get_domain_registry


class DsaDomain(DomainContract):
    """Testing & Algorithm Analysis domain pack providing empirical complexity fitting and benchmarking."""

    name = "dsa"
    aliases = ["algo", "algorithms", "benchmark", "analysis"]
    parser = DsaDomainParser()
    runtime = DsaRuntime()
    exporter = DsaASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("complexity of ")
            or s.startswith("empirical complexity of ")
            or s.startswith("profile memory of ")
            or s.startswith("benchmark ")
            and " with sizes " in s
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("benchmark ") and (":" in s)


# Register with central registry
DSA_DOMAIN = DsaDomain()
get_domain_registry().register(DSA_DOMAIN)

__all__ = [
    "DsaDomain",
    "DSA_DOMAIN",
    "BenchmarkSpec",
    "ComplexityReport",
    "DsaDomainParser",
    "DsaRuntime",
    "DsaASTExporter",
    "run_benchmark",
    "fit_complexity",
    "profile_memory_of_function",
]
