from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.combustion.runtime import (
    combust_equivalence_ratio, combust_arrhenius_rate,
    combust_heat_release_rate, combust_adiabatic_flame_temp,
    combust_le_chatelier_flammability_limit, combust_zeldovich_nox_scaling
)
from doomscript.domains.combustion.parser import CombustionDomainParser
from doomscript.domains.combustion.exporter import CombustionASTExporter

class CombustionRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CombustionDomain(DomainContract):
    name = "combustion"
    aliases = ["flame", "thermal_combustion", "reaction_kinetics"]
    description = "Combustion engineering: equivalence ratio, Arrhenius kinetics, heat release, adiabatic flame temperature, Le Chatelier flammability limits, and Zeldovich thermal NOx"
    parser = CombustionDomainParser()
    runtime = CombustionRuntime()
    exporter = CombustionASTExporter()
    capabilities = ["equivalence_ratio", "arrhenius_rate", "heat_release_rate", "adiabatic_flame_temp", "flammability_limit", "thermal_nox"]
    verbs = [
        VerbSpec(pattern="calculate equivalence ratio fuel {f:expr} air {a:expr} stoich {s:expr} into {target:ident}", description="Equivalence ratio"),
        VerbSpec(pattern="calculate arrhenius rate preexp {a:expr} ea {ea:expr} temp {t:expr} into {target:ident}", description="Arrhenius rate"),
        VerbSpec(pattern="calculate heat release rate flow {m:expr} lhv {lhv:expr} eff {eff:expr} into {target:ident}", description="Heat release rate"),
        VerbSpec(pattern="calculate adiabatic flame temp t0 {t0:expr} lhv {lhv:expr} cp {cp:expr} afr {afr:expr} into {target:ident}", description="Adiabatic flame temperature"),
        VerbSpec(pattern="calculate mixture flammability fractions {y:expr} limits {lfl:expr} into {target:ident}", description="Le Chatelier mixture flammability limit"),
        VerbSpec(pattern="calculate thermal nox temp {t:expr} oxygen {o2:expr} into {target:ident}", description="Zeldovich thermal NOx scaling")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate equivalence ratio ") or s.startswith("calculate arrhenius rate ") or s.startswith("calculate heat release rate ") or s.startswith("calculate adiabatic flame temp ") or s.startswith("calculate mixture flammability ") or s.startswith("calculate thermal nox ")

COMBUSTION_DOMAIN = CombustionDomain()
get_domain_registry().register(COMBUSTION_DOMAIN)

__all__ = [
    "CombustionDomain", "COMBUSTION_DOMAIN", "CombustionRuntime",
    "combust_equivalence_ratio", "combust_arrhenius_rate",
    "combust_heat_release_rate", "combust_adiabatic_flame_temp",
    "combust_le_chatelier_flammability_limit", "combust_zeldovich_nox_scaling"
]
