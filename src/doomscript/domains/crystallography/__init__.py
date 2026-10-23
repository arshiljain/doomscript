from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.crystallography.runtime import (
    CrystallographyRuntime, crystal_bragg_angle,
    crystal_cubic_interplanar_spacing, crystal_atomic_packing_factor,
    crystal_density, crystal_scherrer_crystallite_size,
    crystal_systematic_extinction_allowed, crystal_hexagonal_interplanar_spacing
)
from doomscript.domains.crystallography.parser import CrystallographyDomainParser
from doomscript.domains.crystallography.exporter import CrystallographyASTExporter

class CrystallographyDomain(DomainContract):
    name = "crystallography"
    aliases = ["crystal", "xray_diffraction", "lattice"]
    description = "Deepened Crystallography domain: Bragg diffraction, cubic/hexagonal lattice interplanar spacing, atomic packing factor, unit cell density, Scherrer size, and selection rules"
    parser = CrystallographyDomainParser()
    runtime = CrystallographyRuntime()
    exporter = CrystallographyASTExporter()
    capabilities = ["bragg_angle", "interplanar_spacing", "atomic_packing_factor", "crystal_density", "scherrer_crystallite_size", "extinction_check", "hexagonal_spacing"]
    verbs = [
        VerbSpec(pattern="calculate bragg angle wavelength {lam:expr} spacing {d:expr} order {n:expr} into {target:ident}", description="Bragg diffraction angle"),
        VerbSpec(pattern="calculate interplanar spacing lattice {a:expr} h {h:expr} k {k:expr} l {l:expr} into {target:ident}", description="Cubic interplanar spacing"),
        VerbSpec(pattern="calculate atomic packing factor system {sys:expr} into {target:ident}", description="Atomic packing factor APF"),
        VerbSpec(pattern="calculate crystal density atoms {n:expr} weight {a:expr} volume {vc:expr} into {target:ident}", description="Theoretical crystal density"),
        VerbSpec(pattern="calculate crystallite size wavelength {lam:expr} fwhm {beta:expr} theta {theta:expr} into {target:ident}", description="Scherrer crystallite domain size"),
        VerbSpec(pattern="check reflection allowed lattice {lat:expr} h {h:expr} k {k:expr} l {l:expr} into {target:ident}", description="Systematic extinction selection rules")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate bragg angle ") or
            s.startswith("calculate interplanar spacing ") or
            s.startswith("calculate atomic packing factor ") or
            s.startswith("calculate crystal density ") or
            s.startswith("calculate crystallite size ") or
            s.startswith("check reflection allowed ")
        )

CRYSTALLOGRAPHY_DOMAIN = CrystallographyDomain()
get_domain_registry().register(CRYSTALLOGRAPHY_DOMAIN)

__all__ = [
    "CRYSTALLOGRAPHY_DOMAIN", "CrystallographyDomain", "CrystallographyRuntime",
    "crystal_bragg_angle", "crystal_cubic_interplanar_spacing",
    "crystal_atomic_packing_factor", "crystal_density",
    "crystal_scherrer_crystallite_size", "crystal_systematic_extinction_allowed",
    "crystal_hexagonal_interplanar_spacing"
]
