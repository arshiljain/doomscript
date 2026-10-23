from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.aerospace.runtime import (
    AerospaceRuntime, aero_lift_drag, aero_lift_drag_forces, aero_mach_number,
    aero_breguet_range, aerospace_orbital_velocity,
    aerospace_hohmann_transfer, aerospace_kepler_orbit,
    aerospace_tsiolkovsky_rocket, aerospace_normal_shock
)
from doomscript.domains.aerospace.parser import AerospaceDomainParser
from doomscript.domains.aerospace.exporter import AerospaceASTExporter

class AerospaceDomain(DomainContract):
    name = "aerospace"
    aliases = ["orbital_mechanics", "rocketry", "astronautics"]
    description = "Deepened Aerospace domain: Aerodynamic lift/drag, Mach numbers, Breguet range, orbital velocities, Hohmann transfers, Kepler orbits, and rocket propulsion"
    parser = AerospaceDomainParser()
    runtime = AerospaceRuntime()
    exporter = AerospaceASTExporter()
    capabilities = ["lift_drag", "mach_number", "breguet_range", "orbital_velocity", "hohmann_transfer", "kepler_orbit", "tsiolkovsky_rocket", "normal_shock"]
    verbs = [
        VerbSpec(pattern="calculate lift drag density {rho:expr} velocity {v:expr} wing {s:expr} cl {cl:expr} cd {cd:expr} into {target:ident}", description="Lift and drag forces"),
        VerbSpec(pattern="calculate mach number velocity {v:expr} temp {t:expr} into {target:ident}", description="Mach flight speed"),
        VerbSpec(pattern="calculate breguet range ld {ld:expr} velocity {v:expr} sfc {sfc:expr} w0 {w0:expr} w1 {w1:expr} into {target:ident}", description="Breguet aircraft range"),
        VerbSpec(pattern="calculate orbital velocity altitude {alt:expr} mass {m:expr} radius {r:expr} into {target:ident}", description="Circular orbit velocity"),
        VerbSpec(pattern="calculate hohmann transfer r1 {r1:expr} r2 {r2:expr} into {target:ident}", description="Hohmann transfer orbit delta-v"),
        VerbSpec(pattern="calculate kepler orbit periapsis {rp:expr} apoapsis {ra:expr} into {target:ident}", description="Keplerian orbital parameters"),
        VerbSpec(pattern="calculate rocket delta v isp {isp:expr} m0 {m0:expr} mf {mf:expr} into {target:ident}", description="Tsiolkovsky rocket equation"),
        VerbSpec(pattern="calculate normal shock mach {m1:expr} into {target:ident}", description="Normal shock wave properties")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate lift drag ") or
            s.startswith("calculate mach number ") or
            s.startswith("calculate breguet range ") or
            s.startswith("calculate orbital velocity ") or
            s.startswith("calculate hohmann transfer ") or
            s.startswith("calculate kepler orbit ") or
            s.startswith("calculate rocket delta v ") or
            s.startswith("calculate normal shock ")
        )

AEROSPACE_DOMAIN = AerospaceDomain()
get_domain_registry().register(AEROSPACE_DOMAIN)

__all__ = [
    "AEROSPACE_DOMAIN", "AerospaceDomain", "AerospaceRuntime",
    "aero_lift_drag", "aero_lift_drag_forces", "aero_mach_number", "aero_breguet_range",
    "aerospace_orbital_velocity", "aerospace_hohmann_transfer",
    "aerospace_kepler_orbit", "aerospace_tsiolkovsky_rocket",
    "aerospace_normal_shock"
]
