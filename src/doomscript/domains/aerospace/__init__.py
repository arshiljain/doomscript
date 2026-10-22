from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.aerospace.runtime import (
    aero_lift_drag, aero_mach_number, aero_breguet_range,
    aerospace_orbital_velocity, aerospace_hohmann_transfer, aerospace_kepler_orbit
)
from doomscript.domains.aerospace.parser import AerospaceDomainParser
from doomscript.domains.aerospace.exporter import AerospaceASTExporter

class AerospaceRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class AerospaceDomain(DomainContract):
    name = "aerospace"
    aliases = ["orbital_mechanics", "rocketry", "astronautics"]
    description = "Aerospace & flight dynamics: Lift/drag, Mach number, Breguet range, orbital velocity, and Hohmann transfers"
    parser = AerospaceDomainParser()
    runtime = AerospaceRuntime()
    exporter = AerospaceASTExporter()
    capabilities = ["lift_drag", "mach_number", "breguet_range", "orbital_velocity", "hohmann_transfer", "kepler_orbit"]
    verbs = [
        VerbSpec(pattern="calculate lift and drag for density {rho:expr} velocity {v:expr} area {a:expr} cl {cl:expr} cd {cd:expr} into {target:ident}", description="Lift and drag"),
        VerbSpec(pattern="calculate orbital velocity for altitude {alt:expr} into {target:ident}", description="Orbital velocity"),
        VerbSpec(pattern="calculate hohmann transfer r1 {r1:expr} r2 {r2:expr} into {target:ident}", description="Hohmann transfer")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate lift and drag ") or s.startswith("calculate mach number ") or s.startswith("calculate breguet range ") or s.startswith("calculate orbital velocity ") or s.startswith("calculate hohmann transfer ") or s.startswith("calculate kepler orbit ")

AEROSPACE_DOMAIN = AerospaceDomain()
get_domain_registry().register(AEROSPACE_DOMAIN)

__all__ = [
    "AerospaceDomain", "AEROSPACE_DOMAIN", "AerospaceRuntime",
    "aero_lift_drag", "aero_mach_number", "aero_breguet_range",
    "aerospace_orbital_velocity", "aerospace_hohmann_transfer", "aerospace_kepler_orbit"
]
