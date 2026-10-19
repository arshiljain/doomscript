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
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.dsa.exporter import DsaASTExporter
from doomscript.domains.registry import get_domain_registry


class DsaDomain(DomainContract):
    """Testing & Algorithm Analysis domain pack providing empirical complexity fitting and benchmarking."""

    name = "dsa"
    aliases = ["algo", "algorithms", "dsa_benchmark", "analysis"]
    description = "Data structures, algorithm benchmarking, empirical Big-O fitting, and memory profiling"
    parser = DsaDomainParser()
    runtime = DsaRuntime()
    exporter = DsaASTExporter()
    capabilities = ["complexity", "benchmarking", "profiling", "heaps", "queues"]
    optional_dependencies = ["matplotlib", "scipy"]

    verbs = [
        VerbSpec(
            name="complexity_of",
            pattern="[empirical] complexity of {fn_name:ident} [on sizes {sizes:expr}] into {target:ident}",
            arg_schema={"fn_name": "ident", "sizes": "expr", "target": "ident"},
            returns="Record",
            description="Empirical curve fitting for Big-O asymptotic runtime complexity",
        ),
        VerbSpec(
            name="profile_memory",
            pattern="profile memory of {fn_name:ident} [with {arg:expr}] into {target:ident}",
            arg_schema={"fn_name": "ident", "target": "ident"},
            returns="Record",
            description="Measure peak memory consumption and allocation",
        ),
        VerbSpec(
            name="benchmark_sizes",
            pattern="benchmark {fn_name:ident} (with|on) sizes {sizes:expr} into {target:ident}",
            arg_schema={"fn_name": "ident", "sizes": "expr", "target": "ident"},
            returns="Table",
            description="Measure execution time across input problem sizes",
        ),
        VerbSpec(
            name="pop_from",
            pattern="pop (min|max|left|first) from {coll:ident} into {target:ident}",
            arg_schema={"coll": "ident", "target": "ident"},
            returns="Any",
            description="Remove and retrieve extreme element from heap or queue",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("complexity of ")
            or s.startswith("empirical complexity of ")
            or s.startswith("profile memory of ")
            or s.startswith("trace ")
            or (s.startswith("benchmark ") and (" with sizes " in s or " on sizes " in s))
            or s.startswith("push ")
            or s.startswith("pop min from ")
            or s.startswith("pop max from ")
            or s.startswith("pop left from ")
            or s.startswith("pop first from ")
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
