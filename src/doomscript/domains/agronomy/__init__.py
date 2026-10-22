from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.agronomy.runtime import (
    agronomy_crop_water_requirement, agronomy_growing_degree_days,
    agronomy_fertilizer_rate, agronomy_cation_exchange_capacity,
    agronomy_soil_porosity
)
from doomscript.domains.agronomy.parser import AgronomyDomainParser
from doomscript.domains.agronomy.exporter import AgronomyASTExporter

class AgronomyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class AgronomyDomain(DomainContract):
    name = "agronomy"
    aliases = ["agri", "crop_science", "soil_science"]
    description = "Agronomy and soil science: crop evapotranspiration, growing degree days, fertilizer rates, cation exchange capacity, and soil porosity"
    parser = AgronomyDomainParser()
    runtime = AgronomyRuntime()
    exporter = AgronomyASTExporter()
    capabilities = ["crop_water_requirement", "growing_degree_days", "fertilizer_rate", "cation_exchange_capacity", "soil_porosity"]
    verbs = [
        VerbSpec(pattern="calculate crop water requirement et0 {et0:expr} kc {kc:expr} into {target:ident}", description="Crop water requirement"),
        VerbSpec(pattern="calculate growing degree days tmax {tmax:expr} tmin {tmin:expr} tbase {tbase:expr} into {target:ident}", description="Growing degree days"),
        VerbSpec(pattern="calculate fertilizer rate nutrient {n:expr} percent {p:expr} into {target:ident}", description="Fertilizer application rate"),
        VerbSpec(pattern="calculate cation exchange ca {ca:expr} mg {mg:expr} k {k:expr} na {na:expr} into {target:ident}", description="Cation exchange capacity"),
        VerbSpec(pattern="calculate soil porosity bulk {pb:expr} into {target:ident}", description="Soil bulk porosity")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate crop water requirement ") or s.startswith("calculate growing degree days ") or s.startswith("calculate fertilizer rate ") or s.startswith("calculate cation exchange ") or s.startswith("calculate soil porosity ")

AGRONOMY_DOMAIN = AgronomyDomain()
get_domain_registry().register(AGRONOMY_DOMAIN)

__all__ = [
    "AgronomyDomain", "AGRONOMY_DOMAIN", "AgronomyRuntime",
    "agronomy_crop_water_requirement", "agronomy_growing_degree_days",
    "agronomy_fertilizer_rate", "agronomy_cation_exchange_capacity",
    "agronomy_soil_porosity"
]
