from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.materials.runtime import (
    materials_stress_strain, materials_mohrs_circle, materials_thermal_expansion,
    materials_stress_intensity, materials_rule_of_mixtures
)
from doomscript.domains.materials.parser import MaterialsDomainParser
from doomscript.domains.materials.exporter import MaterialsASTExporter

class MaterialsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class MaterialsDomain(DomainContract):
    name = "materials"
    aliases = ["mechanics_of_materials", "solid_mechanics", "stress_strain"]
    description = "Materials science & mechanics: Stress-strain, Mohr's circle, thermal expansion, fracture mechanics, and composites"
    parser = MaterialsDomainParser()
    runtime = MaterialsRuntime()
    exporter = MaterialsASTExporter()
    capabilities = ["stress_strain", "mohrs_circle", "thermal_expansion", "stress_intensity", "rule_of_mixtures"]
    verbs = [
        VerbSpec(pattern="calculate engineering stress and strain for force {f:expr} area {a:expr} delta {dl:expr} initial length {l0:expr} into {target:ident}", description="Stress-strain"),
        VerbSpec(pattern="calculate stress intensity for stress {s:expr} crack {a:expr} into {target:ident}", description="Stress intensity")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate engineering stress ") or s.startswith("calculate mohrs circle ") or s.startswith("calculate thermal expansion ") or s.startswith("calculate stress intensity ") or s.startswith("calculate composite modulus ")

MATERIALS_DOMAIN = MaterialsDomain()
get_domain_registry().register(MATERIALS_DOMAIN)

__all__ = [
    "MaterialsDomain", "MATERIALS_DOMAIN", "MaterialsRuntime",
    "materials_stress_strain", "materials_mohrs_circle", "materials_thermal_expansion",
    "materials_stress_intensity", "materials_rule_of_mixtures"
]
