from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.aviation.runtime import (
    aviation_pressure_altitude, aviation_density_altitude,
    aviation_wind_components, aviation_turn_radius,
    aviation_banked_stall_speed, aviation_climb_gradient
)
from doomscript.domains.aviation.parser import AviationDomainParser
from doomscript.domains.aviation.exporter import AviationASTExporter

class AviationRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class AviationDomain(DomainContract):
    name = "aviation"
    aliases = ["flight", "aero", "avionics"]
    description = "Aeronautics and flight physics: pressure & density altitude, crosswind components, turn radius, banked stall speed, and climb gradient"
    parser = AviationDomainParser()
    runtime = AviationRuntime()
    exporter = AviationASTExporter()
    capabilities = ["pressure_altitude", "density_altitude", "wind_components", "turn_radius", "banked_stall_speed", "climb_gradient"]
    verbs = [
        VerbSpec(pattern="calculate pressure altitude altimeter {alt:expr} elevation {elev:expr} into {target:ident}", description="Pressure altitude"),
        VerbSpec(pattern="calculate density altitude pressure_alt {pa:expr} oat {oat:expr} into {target:ident}", description="Density altitude"),
        VerbSpec(pattern="calculate wind components wind_speed {ws:expr} wind_dir {wd:expr} runway {rw:expr} into {target:ident}", description="Crosswind and headwind components"),
        VerbSpec(pattern="calculate turn radius tas {tas:expr} bank {bank:expr} into {target:ident}", description="Turn radius"),
        VerbSpec(pattern="calculate banked stall speed vs0 {vs:expr} bank {b:expr} into {target:ident}", description="Stall speed in bank turn"),
        VerbSpec(pattern="calculate climb gradient roc {roc:expr} tas {tas:expr} into {target:ident}", description="Aircraft climb gradient percentage")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate pressure altitude ") or s.startswith("calculate density altitude ") or s.startswith("calculate wind components ") or s.startswith("calculate turn radius ") or s.startswith("calculate banked stall speed ") or s.startswith("calculate climb gradient ")

AVIATION_DOMAIN = AviationDomain()
get_domain_registry().register(AVIATION_DOMAIN)

__all__ = [
    "AviationDomain", "AVIATION_DOMAIN", "AviationRuntime",
    "aviation_pressure_altitude", "aviation_density_altitude",
    "aviation_wind_components", "aviation_turn_radius",
    "aviation_banked_stall_speed", "aviation_climb_gradient"
]
