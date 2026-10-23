from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.thermodynamics.runtime import (
    ThermodynamicsRuntime, thermo_carnot_efficiency, thermo_entropy_change,
    thermo_polytropic_process, thermo_clausius_clapeyron,
    thermo_rankine_cycle_efficiency, thermo_joule_thomson_expansion,
    thermo_brayton_cycle, thermo_otto_cycle, thermo_heat_exchanger_lmtd
)
from doomscript.domains.thermodynamics.parser import ThermodynamicsDomainParser
from doomscript.domains.thermodynamics.exporter import ThermodynamicsASTExporter

class ThermodynamicsDomain(DomainContract):
    name = "thermodynamics"
    aliases = ["heat_transfer", "thermal_physics", "thermo"]
    description = "Thermodynamics & heat cycles: Carnot, Rankine, Brayton, Otto cycles, entropy change, polytropic processes, and Joule-Thomson"
    parser = ThermodynamicsDomainParser()
    runtime = ThermodynamicsRuntime()
    exporter = ThermodynamicsASTExporter()
    capabilities = ["carnot_efficiency", "entropy_change", "polytropic_process", "clausius_clapeyron", "rankine_cycle", "joule_thomson", "brayton_cycle", "otto_cycle", "lmtd"]
    verbs = [
        VerbSpec(pattern="calculate carnot efficiency hot {th:expr} cold {tc:expr} into {target:ident}", description="Carnot efficiency"),
        VerbSpec(pattern="calculate entropy change mass {m:expr} specific heat {c:expr} t1 {t1:expr} t2 {t2:expr} into {target:ident}", description="Entropy change"),
        VerbSpec(pattern="step polytropic p1 {p1:expr} v1 {v1:expr} v2 {v2:expr} index {n:expr} into {target:ident}", description="Polytropic gas expansion"),
        VerbSpec(pattern="calculate rankine cycle boiler {h2:expr} turbine {h3:expr} condenser {h4:expr} pump {h1:expr} into {target:ident}", description="Rankine cycle efficiency"),
        VerbSpec(pattern="calculate joule thomson drop pressure {dp:expr} coefficient {mu:expr} into {target:ident}", description="Joule-Thomson temperature change")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate carnot efficiency ") or
            s.startswith("calculate entropy change ") or
            s.startswith("step polytropic ") or
            s.startswith("calculate vapor pressure ") or
            s.startswith("calculate rankine cycle ") or
            s.startswith("calculate joule thomson drop ")
        )

THERMODYNAMICS_DOMAIN = ThermodynamicsDomain()
get_domain_registry().register(THERMODYNAMICS_DOMAIN)

__all__ = [
    "ThermodynamicsDomain", "THERMODYNAMICS_DOMAIN", "ThermodynamicsRuntime",
    "thermo_carnot_efficiency", "thermo_entropy_change",
    "thermo_polytropic_process", "thermo_clausius_clapeyron",
    "thermo_rankine_cycle_efficiency", "thermo_joule_thomson_expansion",
    "thermo_brayton_cycle", "thermo_otto_cycle", "thermo_heat_exchanger_lmtd"
]
