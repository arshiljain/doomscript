from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.hydrology.runtime import (
    hydrology_manning_flow, hydrology_peak_runoff, hydrology_darcy_weisbach,
    hydrology_reynolds_number, hydrology_hydraulic_jump, hydrology_theis_drawdown
)
from doomscript.domains.hydrology.parser import HydrologyDomainParser
from doomscript.domains.hydrology.exporter import HydrologyASTExporter

class HydrologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class HydrologyDomain(DomainContract):
    name = "hydrology"
    aliases = ["water", "fluid_mechanics", "open_channel"]
    description = "Hydrology & hydraulic engineering: Manning flow, Darcy-Weisbach head loss, hydraulic jumps, and Theis drawdown"
    parser = HydrologyDomainParser()
    runtime = HydrologyRuntime()
    exporter = HydrologyASTExporter()
    capabilities = ["manning_flow", "peak_runoff", "darcy_weisbach", "reynolds_number", "hydraulic_jump", "theis_drawdown"]
    verbs = [
        VerbSpec(pattern="calculate manning flow for roughness {n:expr} area {a:expr} radius {r:expr} slope {s:expr} into {target:ident}", description="Manning flow"),
        VerbSpec(pattern="calculate hydraulic jump for depth {y:expr} velocity {v:expr} into {target:ident}", description="Hydraulic jump")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate manning flow ") or s.startswith("calculate peak runoff ") or s.startswith("calculate darcy weisbach head loss ") or s.startswith("calculate reynolds number ") or s.startswith("calculate hydraulic jump ") or s.startswith("calculate theis drawdown ")

HYDROLOGY_DOMAIN = HydrologyDomain()
get_domain_registry().register(HYDROLOGY_DOMAIN)

__all__ = [
    "HydrologyDomain", "HYDROLOGY_DOMAIN", "HydrologyRuntime",
    "hydrology_manning_flow", "hydrology_peak_runoff", "hydrology_darcy_weisbach",
    "hydrology_reynolds_number", "hydrology_hydraulic_jump", "hydrology_theis_drawdown"
]
