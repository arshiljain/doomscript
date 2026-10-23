from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.combustion.runtime import (
    CombustionRuntime, combust_equivalence_ratio, combust_arrhenius_rate,
    combust_heat_release_rate, combust_adiabatic_flame_temp,
    combust_le_chatelier_flammability_limit, combust_zeldovich_nox_scaling,
    combust_damkohler_number, combust_wobbe_index
)
from doomscript.domains.combustion.parser import CombustionDomainParser
from doomscript.domains.combustion.exporter import CombustionASTExporter

class CombustionDomain(DomainContract):
    name = "combustion"
    aliases = ["flame", "thermal_combustion", "reaction_kinetics"]
    description = "Deepened Combustion domain: Equivalence ratio, Arrhenius reaction kinetics, heat release, adiabatic flame temperature, Le Chatelier flammability limits, and NOx scaling"
    parser = CombustionDomainParser()
    runtime = CombustionRuntime()
    exporter = CombustionASTExporter()
    capabilities = ["equivalence_ratio", "arrhenius_rate", "heat_release_rate", "adiabatic_flame_temp", "flammability_limit", "zeldovich_nox", "damkohler", "wobbe_index"]
    verbs = [
        VerbSpec(pattern="calculate equivalence ratio fuel {f:expr} air {a:expr} stoich {stoich:expr} into {target:ident}", description="Fuel-air equivalence ratio"),
        VerbSpec(pattern="calculate arrhenius rate preexp {a:expr} ea {ea:expr} temp {t:expr} into {target:ident}", description="Arrhenius reaction rate constant"),
        VerbSpec(pattern="calculate heat release rate flow {m:expr} lhv {lhv:expr} eff {eff:expr} into {target:ident}", description="Thermal heat release rate (MW)"),
        VerbSpec(pattern="calculate adiabatic flame temp t0 {t0:expr} lhv {lhv:expr} cp {cp:expr} afr {afr:expr} into {target:ident}", description="Adiabatic flame temperature (K)"),
        VerbSpec(pattern="calculate mixture flammability fractions {y:expr} limits {limits:expr} into {target:ident}", description="Le Chatelier mixture flammability limit"),
        VerbSpec(pattern="calculate thermal nox temp {t:expr} oxygen {xo2:expr} into {target:ident}", description="Thermal Zeldovich NOx forward rate index"),
        VerbSpec(pattern="calculate wobbe index hhv {hhv:expr} gravity {sg:expr} into {target:ident}", description="Wobbe index for fuel gas interchangeability")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate equivalence ratio ") or
            s.startswith("calculate arrhenius rate ") or
            s.startswith("calculate heat release rate ") or
            s.startswith("calculate adiabatic flame temp ") or
            s.startswith("calculate mixture flammability ") or
            s.startswith("calculate thermal nox ") or
            s.startswith("calculate wobbe index ")
        )

COMBUSTION_DOMAIN = CombustionDomain()
get_domain_registry().register(COMBUSTION_DOMAIN)

__all__ = [
    "COMBUSTION_DOMAIN", "CombustionDomain", "CombustionRuntime",
    "combust_equivalence_ratio", "combust_arrhenius_rate",
    "combust_heat_release_rate", "combust_adiabatic_flame_temp",
    "combust_le_chatelier_flammability_limit", "combust_zeldovich_nox_scaling",
    "combust_damkohler_number", "combust_wobbe_index"
]
