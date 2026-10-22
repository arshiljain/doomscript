from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.materials.runtime import (
    materials_stress_strain, materials_mohrs_circle, materials_thermal_expansion,
    materials_vickers_hardness
)
from doomscript.domains.materials.parser import MaterialsDomainParser
from doomscript.domains.materials.exporter import MaterialsASTExporter

class MaterialsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class MaterialsDomain(DomainContract):
    name = "materials"
    aliases = ["solid_mechanics", "stress_strain", "metallurgy"]
    description = "Stress-strain tensors, Young's modulus, Mohr's circle, and thermal expansion"
    parser = MaterialsDomainParser()
    runtime = MaterialsRuntime()
    exporter = MaterialsASTExporter()
    capabilities = ["stress_strain", "mohrs_circle", "thermal_expansion"]
    verbs = [
        VerbSpec(pattern="calculate engineering stress and strain for force {f:expr} area {a:expr} delta {dl:expr} initial length {l0:expr} into {target:ident}", description="Stress and strain"),
        VerbSpec(pattern="calculate mohrs circle principal stresses for sigma x {sx:expr} sigma y {sy:expr} tau {txy:expr} into {target:ident}", description="Mohr's circle")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate engineering stress and strain ") or s.startswith("calculate mohrs circle ") or s.startswith("calculate thermal expansion ")

MATERIALS_DOMAIN = MaterialsDomain()
get_domain_registry().register(MATERIALS_DOMAIN)

__all__ = [
    "MaterialsDomain", "MATERIALS_DOMAIN", "MaterialsRuntime",
    "materials_stress_strain", "materials_mohrs_circle", "materials_thermal_expansion",
    "materials_vickers_hardness"
]
