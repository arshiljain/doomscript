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
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.sim.exporter import SimASTExporter
from doomscript.domains.registry import get_domain_registry


class SimDomain(DomainContract):
    """Simulation & Optimization domain pack providing discrete-event queueing, Monte Carlo, and Nelder-Mead."""

    name = "sim"
    aliases = ["simulation", "sim_opt"]
    description = "Simulation modeling, discrete-event queueing, Monte Carlo trials, Nelder-Mead optimization"
    parser = SimDomainParser()
    runtime = SimRuntime()
    exporter = SimASTExporter()
    capabilities = ["simulation", "monte_carlo", "queueing", "nelder_mead", "parameter_sweep"]
    optional_dependencies = ["numpy", "scipy"]

    verbs = [
        VerbSpec(
            name="inspect_simulation",
            pattern="inspect simulation {s_var:ident} [into {target:ident}]",
            arg_schema={"s_var": "ident", "target": "ident"},
            returns="Record",
            description="Inspect simulated queue metrics and summary stats",
        ),
        VerbSpec(
            name="summarize_metric",
            pattern="summarize [uncertainty of] {s_var:ident} [into {target:ident}]",
            arg_schema={"s_var": "ident", "target": "ident"},
            returns="Record",
            description="Compute confidence intervals and variance of trial metric",
        ),
        VerbSpec(
            name="sample_distribution",
            pattern="sample {count:int} from {dist:ident} [with {params:expr}] into {target:ident}",
            arg_schema={"count": "int", "dist": "ident", "target": "ident"},
            returns="Collection",
            description="Generate random samples from statistical distribution",
        ),
        VerbSpec(
            name="optimize",
            pattern="optimize {fn_name:ident} starting at {x0:expr} into {target:ident}",
            arg_schema={"fn_name": "ident", "x0": "expr", "target": "ident"},
            returns="Record",
            description="Find minimum of objective function via Nelder-Mead simplex",
        ),
        VerbSpec(
            name="run_trials",
            pattern="run {n:int} trials of {sim:ident} into {target:ident}",
            arg_schema={"n": "int", "sim": "ident", "target": "ident"},
            returns="Record",
            description="Execute repeated stochastic Monte Carlo trials",
        ),
        VerbSpec(
            name="sweep_parameter",
            pattern="sweep parameter {param:ident} from {start_val:expr} to {end_val:expr} [in {steps:int} steps] for {sim:ident} into {target:ident}",
            arg_schema={"param": "ident", "start_val": "expr", "end_val": "expr", "sim": "ident", "target": "ident"},
            defaults={"steps": 5},
            returns="Record",
            description="Evaluate simulation performance across parameter grid",
        ),
    ]

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
