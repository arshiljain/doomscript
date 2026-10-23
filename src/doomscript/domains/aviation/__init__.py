"""Aviation Domain for DoomScript: Flight mechanics, aerodynamics, navigation, performance, and weight and balance."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.aviation.parser import AviationDomainParser
from doomscript.domains.aviation.runtime import (
    AviationRuntime,
    aviation_pressure_altitude,
    aviation_density_altitude,
    aviation_wind_components,
    aviation_turn_radius,
    aviation_banked_stall_speed,
    aviation_climb_gradient,
    aviation_tas_from_cas,
    aviation_glide_performance,
    aviation_holding_pattern_drift,
    aviation_weight_and_balance,
    aviation_critical_mach_drag_divergence,
    aviation_standard_rate_turn
)
from doomscript.domains.aviation.exporter import AviationASTExporter

class AviationDomain(DomainContract):
    name = "aviation"
    aliases = ["flight", "aero", "avionics"]
    description = "Flight mechanics, aerodynamics, navigation, performance, and weight and balance."
    parser = AviationDomainParser()
    runtime = AviationRuntime()
    exporter = AviationASTExporter()
    capabilities = [
        "pressure_altitude",
        "density_altitude",
        "wind_components",
        "turn_radius",
        "banked_stall_speed",
        "climb_gradient",
        "tas_from_cas",
        "glide_performance",
        "holding_pattern_drift",
        "weight_and_balance",
        "critical_mach_drag_divergence",
        "standard_rate_turn"
    ]
    verbs = [
        VerbSpec(pattern="calculate pressure altitude altimeter {alt:expr} elevation {elev:expr} into {target:ident}", description="Computes pressure altitude PA in feet"),
        VerbSpec(pattern="calculate density altitude pressure_alt {pa:expr} oat {oat:expr} into {target:ident}", description="Computes density altitude DA in feet"),
        VerbSpec(pattern="calculate wind components wind_speed {ws:expr} wind_dir {wd:expr} runway {rwy:expr} into {target:ident}", description="Computes crosswind and headwind components in knots"),
        VerbSpec(pattern="calculate turn radius tas {tas:expr} bank {bank:expr} into {target:ident}", description="Computes coordinated level turn radius in feet"),
        VerbSpec(pattern="calculate banked stall speed vs0 {vs0:expr} bank {bank:expr} into {target:ident}", description="Computes accelerated stall speed in a bank turn"),
        VerbSpec(pattern="calculate climb gradient roc {roc:expr} tas {tas:expr} into {target:ident}", description="Computes aircraft climb gradient percentage"),
        VerbSpec(pattern="calculate true airspeed cas {cas:expr} pressure_alt {pa:expr} oat {oat:expr} into {target:ident}", description="Computes TAS and Mach number from CAS"),
        VerbSpec(pattern="calculate glide performance ratio {gr:expr} altitude {alt:expr} into {target:ident}", description="Computes unpowered glide range in nautical miles"),
        VerbSpec(pattern="calculate holding pattern drift wind_speed {ws:expr} wind_dir {wd:expr} course {crs:expr} tas {tas:expr} into {target:ident}", description="Computes wind correction angles and outbound holding timer"),
        VerbSpec(pattern="calculate weight and balance empty_weight {ew:expr} empty_arm {ea:expr} stations {st:expr} into {target:ident}", description="Computes gross takeoff weight and CG position"),
        VerbSpec(pattern="calculate critical mach sweep {sweep:expr} thickness {tc:expr} into {target:ident}", description="Computes critical Mach and drag divergence Mach number"),
        VerbSpec(pattern="calculate standard rate turn tas {tas:expr} into {target:ident}", description="Computes bank angle and load factor for standard rate 3 deg/sec turn")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate pressure altitude ") or
            s.startswith("calculate density altitude ") or
            s.startswith("calculate wind components ") or
            s.startswith("calculate turn radius ") or
            s.startswith("calculate banked stall speed ") or
            s.startswith("calculate climb gradient ") or
            s.startswith("calculate true airspeed ") or
            s.startswith("calculate glide performance ") or
            s.startswith("calculate holding pattern drift ") or
            s.startswith("calculate weight and balance ") or
            s.startswith("calculate critical mach ") or
            s.startswith("calculate standard rate turn ")
        )

AVIATION_DOMAIN = AviationDomain()
get_domain_registry().register(AVIATION_DOMAIN)

__all__ = [
    "AVIATION_DOMAIN",
    "AviationDomain",
    "AviationRuntime",
    "aviation_pressure_altitude",
    "aviation_density_altitude",
    "aviation_wind_components",
    "aviation_turn_radius",
    "aviation_banked_stall_speed",
    "aviation_climb_gradient",
    "aviation_tas_from_cas",
    "aviation_glide_performance",
    "aviation_holding_pattern_drift",
    "aviation_weight_and_balance",
    "aviation_critical_mach_drag_divergence",
    "aviation_standard_rate_turn"
]
