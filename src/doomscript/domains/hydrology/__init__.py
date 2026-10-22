from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.hydrology.runtime import (
    hydro_reynolds_number, hydro_darcy_weisbach_head_loss,
    hydro_manning_flow, hydro_rational_peak_runoff
)
from doomscript.domains.hydrology.parser import HydrologyDomainParser
from doomscript.domains.hydrology.exporter import HydrologyASTExporter

class HydrologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class HydrologyDomain(DomainContract):
    name = "hydrology"
    aliases = ["fluids", "water", "fluid_dynamics"]
    description = "Fluid dynamics, pipe head loss, open channel flow, and stormwater runoff"
    parser = HydrologyDomainParser()
    runtime = HydrologyRuntime()
    exporter = HydrologyASTExporter()
    capabilities = ["reynolds_number", "darcy_weisbach", "manning_flow", "peak_runoff"]
    verbs = [
        VerbSpec(pattern="calculate reynolds number for velocity {v:expr} diameter {d:expr} into {target:ident}", description="Reynolds number"),
        VerbSpec(pattern="calculate manning flow for roughness {n:expr} area {a:expr} radius {r:expr} slope {s:expr} into {target:ident}", description="Manning channel flow")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate reynolds number ") or s.startswith("calculate darcy weisbach ") or s.startswith("calculate manning flow ") or s.startswith("calculate peak runoff ")

HYDROLOGY_DOMAIN = HydrologyDomain()
get_domain_registry().register(HYDROLOGY_DOMAIN)

__all__ = [
    "HydrologyDomain", "HYDROLOGY_DOMAIN", "HydrologyRuntime",
    "hydro_reynolds_number", "hydro_darcy_weisbach_head_loss",
    "hydro_manning_flow", "hydro_rational_peak_runoff"
]
