"""Simulation & Optimization Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.sim.spec import SimulationSpec, OptimizationSpec, TrialsSpec, SweepSpec
from doomscript.domains.sim.parser import SimDomainParser
from doomscript.domains.sim.runtime import (
    SimRuntime,
    summarize_metric,
    summarize_uncertainty,
    sample_distribution,
    DiscreteEventQueueEngine,
    NelderMeadOptimizer,
    run_trials,
    sweep_parameter,
)
from doomscript.domains.sim.exporter import SimASTExporter
from doomscript.domains.registry import get_domain_registry


class SimDomain(DomainContract):
    """Simulation & Optimization domain pack providing discrete-event queueing, Monte Carlo, and Nelder-Mead."""

    name = "sim"
    aliases = ["simulation", "optimize"]
    parser = SimDomainParser()
    runtime = SimRuntime()
    exporter = SimASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("inspect simulation ")
            or s.startswith("summarize ")
            or s.startswith("sample ")
            or s.startswith("optimize ")
            or (s.startswith("run ") and "trials of" in s)
            or s.startswith("sweep ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("simulate ") and (":" in s)


# Register with central registry
SIM_DOMAIN = SimDomain()
get_domain_registry().register(SIM_DOMAIN)

__all__ = [
    "SimDomain",
    "SIM_DOMAIN",
    "SimulationSpec",
    "TrialsSpec",
    "SweepSpec",
    "OptimizationSpec",
    "SimDomainParser",
    "SimRuntime",
    "SimASTExporter",
    "summarize_metric",
    "summarize_uncertainty",
    "sample_distribution",
    "DiscreteEventQueueEngine",
    "NelderMeadOptimizer",
    "run_trials",
    "sweep_parameter",
]
