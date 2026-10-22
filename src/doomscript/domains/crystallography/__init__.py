from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.crystallography.runtime import (
    crystal_bragg_angle, crystal_cubic_interplanar_spacing,
    crystal_atomic_packing_factor, crystal_density,
    crystal_scherrer_crystallite_size
)
from doomscript.domains.crystallography.parser import CrystallographyDomainParser
from doomscript.domains.crystallography.exporter import CrystallographyASTExporter

class CrystallographyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CrystallographyDomain(DomainContract):
    name = "crystallography"
    aliases = ["crystal", "xray_diffraction", "lattice"]
    description = "Crystallography: Bragg diffraction, interplanar spacing, atomic packing factors, theoretical density, and Scherrer crystallite size"
    parser = CrystallographyDomainParser()
    runtime = CrystallographyRuntime()
    exporter = CrystallographyASTExporter()
    capabilities = ["bragg_angle", "cubic_interplanar_spacing", "atomic_packing_factor", "crystal_density", "crystallite_size"]
    verbs = [
        VerbSpec(pattern="calculate bragg angle wavelength {w:expr} spacing {d:expr} order {n:expr} into {target:ident}", description="Bragg diffraction angle"),
        VerbSpec(pattern="calculate interplanar spacing lattice {a:expr} h {h:expr} k {k:expr} l {l:expr} into {target:ident}", description="Interplanar spacing"),
        VerbSpec(pattern="calculate atomic packing factor system {s:expr} into {target:ident}", description="Atomic packing factor"),
        VerbSpec(pattern="calculate crystal density atoms {n:expr} weight {a:expr} volume {v:expr} into {target:ident}", description="Crystal theoretical density"),
        VerbSpec(pattern="calculate crystallite size wavelength {w:expr} fwhm {f:expr} theta {t:expr} into {target:ident}", description="Scherrer crystallite domain size")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate bragg angle ") or s.startswith("calculate interplanar spacing ") or s.startswith("calculate atomic packing factor ") or s.startswith("calculate crystal density ") or s.startswith("calculate crystallite size ")

CRYSTALLOGRAPHY_DOMAIN = CrystallographyDomain()
get_domain_registry().register(CRYSTALLOGRAPHY_DOMAIN)

__all__ = [
    "CrystallographyDomain", "CRYSTALLOGRAPHY_DOMAIN", "CrystallographyRuntime",
    "crystal_bragg_angle", "crystal_cubic_interplanar_spacing",
    "crystal_atomic_packing_factor", "crystal_density",
    "crystal_scherrer_crystallite_size"
]
