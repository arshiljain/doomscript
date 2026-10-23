from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.hydrology.runtime import (
    HydrologyRuntime, hydrology_manning_flow, hydrology_peak_runoff,
    hydrology_darcy_weisbach, hydrology_reynolds_number,
    hydrology_hydraulic_jump, hydrology_theis_drawdown,
    hydrology_scs_curve_number, hydrology_muskingum_routing,
    hydrology_fao_penman_monteith
)
from doomscript.domains.hydrology.parser import HydrologyDomainParser
from doomscript.domains.hydrology.exporter import HydrologyASTExporter

class HydrologyDomain(DomainContract):
    name = "hydrology"
    aliases = ["water", "fluid_mechanics", "open_channel"]
    description = "Deepened Hydrology domain: Manning open channel, Darcy-Weisbach head loss, hydraulic jumps, Theis aquifer drawdown, SCS curve numbers, and Muskingum flood routing"
    parser = HydrologyDomainParser()
    runtime = HydrologyRuntime()
    exporter = HydrologyASTExporter()
    capabilities = ["manning_flow", "peak_runoff", "darcy_weisbach", "reynolds_number", "hydraulic_jump", "theis_drawdown", "scs_curve_number", "muskingum_routing", "penman_monteith"]
    verbs = [
        VerbSpec(pattern="calculate manning flow for roughness {n:expr} area {a:expr} radius {r:expr} slope {s:expr} into {target:ident}", description="Manning flow rate"),
        VerbSpec(pattern="calculate peak runoff c {c:expr} intensity {i:expr} area {a:expr} into {target:ident}", description="Rational peak runoff"),
        VerbSpec(pattern="calculate darcy weisbach head loss friction {f:expr} length {l:expr} diameter {d:expr} velocity {v:expr} into {target:ident}", description="Darcy-Weisbach friction head loss"),
        VerbSpec(pattern="calculate reynolds number velocity {v:expr} diameter {d:expr} into {target:ident}", description="Reynolds number"),
        VerbSpec(pattern="calculate hydraulic jump for depth {y:expr} velocity {v:expr} into {target:ident}", description="Open channel hydraulic jump"),
        VerbSpec(pattern="calculate theis drawdown discharge {q:expr} transmissivity {t:expr} storativity {s:expr} radius {r:expr} time {time:expr} into {target:ident}", description="Theis well drawdown"),
        VerbSpec(pattern="calculate scs runoff curve cn {cn:expr} precipitation {p:expr} into {target:ident}", description="SCS runoff curve number"),
        VerbSpec(pattern="calculate evapotranspiration rn {rn:expr} temp {t:expr} wind {w:expr} humidity {rh:expr} into {target:ident}", description="FAO Penman-Monteith evapotranspiration")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate manning flow ") or
            s.startswith("calculate peak runoff ") or
            s.startswith("calculate darcy weisbach ") or
            s.startswith("calculate reynolds number ") or
            s.startswith("calculate hydraulic jump ") or
            s.startswith("calculate theis drawdown ") or
            s.startswith("calculate scs runoff curve ") or
            s.startswith("calculate evapotranspiration ")
        )

HYDROLOGY_DOMAIN = HydrologyDomain()
get_domain_registry().register(HYDROLOGY_DOMAIN)

__all__ = [
    "HydrologyDomain", "HYDROLOGY_DOMAIN", "HydrologyRuntime",
    "hydrology_manning_flow", "hydrology_peak_runoff", "hydrology_darcy_weisbach",
    "hydrology_reynolds_number", "hydrology_hydraulic_jump", "hydrology_theis_drawdown",
    "hydrology_scs_curve_number", "hydrology_muskingum_routing",
    "hydrology_fao_penman_monteith"
]
