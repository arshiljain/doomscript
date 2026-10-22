from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.aerospace.runtime import (
    aero_lift_drag, aero_mach_number, aero_breguet_range
)
from doomscript.domains.aerospace.parser import AerospaceDomainParser
from doomscript.domains.aerospace.exporter import AerospaceASTExporter

class AerospaceRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class AerospaceDomain(DomainContract):
    name = "aerospace"
    aliases = ["aero", "aerodynamics", "flight"]
    description = "Lift, drag, Mach number, and Breguet aircraft range"
    parser = AerospaceDomainParser()
    runtime = AerospaceRuntime()
    exporter = AerospaceASTExporter()
    capabilities = ["lift_drag", "mach_number", "breguet_range"]
    verbs = [
        VerbSpec(pattern="calculate lift and drag for density {rho:expr} velocity {v:expr} area {s:expr} cl {cl:expr} cd {cd:expr} into {target:ident}", description="Lift and drag"),
        VerbSpec(pattern="calculate mach number for velocity {v:expr} into {target:ident}", description="Mach number")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate lift and drag ") or s.startswith("calculate mach number ") or s.startswith("calculate breguet range ")

AEROSPACE_DOMAIN = AerospaceDomain()
get_domain_registry().register(AEROSPACE_DOMAIN)

__all__ = [
    "AerospaceDomain", "AEROSPACE_DOMAIN", "AerospaceRuntime",
    "aero_lift_drag", "aero_mach_number", "aero_breguet_range"
]
