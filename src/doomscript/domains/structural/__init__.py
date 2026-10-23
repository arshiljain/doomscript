from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.structural.runtime import (
    StructuralRuntime, structural_beam_max_moment,
    structural_beam_max_deflection, structural_euler_buckling_load,
    structural_section_modulus_rectangular,
    structural_mohr_circle_principal_stresses,
    structural_slenderness_ratio, structural_von_mises_stress,
    structural_torsion_shaft
)
from doomscript.domains.structural.parser import StructuralDomainParser
from doomscript.domains.structural.exporter import StructuralASTExporter

class StructuralDomain(DomainContract):
    name = "structural"
    aliases = ["civil_structures", "structural_analysis", "beams"]
    description = "Deepened Structural Engineering domain: Beam bending moments, elastic deflections, Euler column buckling, section modulus, Mohr principal stresses, and slenderness"
    parser = StructuralDomainParser()
    runtime = StructuralRuntime()
    exporter = StructuralASTExporter()
    capabilities = ["beam_moment", "beam_deflection", "column_buckling", "section_modulus", "mohr_stresses", "slenderness_ratio", "von_mises_stress"]
    verbs = [
        VerbSpec(pattern="calculate beam max moment load {w:expr} span {l:expr} into {target:ident}", description="Simply supported beam max moment"),
        VerbSpec(pattern="calculate beam max deflection load {w:expr} span {l:expr} modulus {e:expr} inertia {i:expr} into {target:ident}", description="Simply supported beam max deflection"),
        VerbSpec(pattern="calculate column buckling load modulus {e:expr} inertia {i:expr} length {l:expr} factor {k:expr} into {target:ident}", description="Euler critical buckling load"),
        VerbSpec(pattern="calculate section modulus width {b:expr} height {h:expr} into {target:ident}", description="Rectangular section modulus"),
        VerbSpec(pattern="calculate mohr principal stresses sx {sx:expr} sy {sy:expr} txy {txy:expr} into {target:ident}", description="Mohr circle principal stresses"),
        VerbSpec(pattern="calculate slenderness ratio length {l:expr} radius {r:expr} into {target:ident}", description="Column slenderness ratio")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate beam max moment ") or
            s.startswith("calculate beam max deflection ") or
            s.startswith("calculate column buckling load ") or
            s.startswith("calculate section modulus ") or
            s.startswith("calculate mohr principal stresses ") or
            s.startswith("calculate slenderness ratio ") or
            s.startswith("calculate von mises stress ")
        )

STRUCTURAL_DOMAIN = StructuralDomain()
get_domain_registry().register(STRUCTURAL_DOMAIN)

__all__ = [
    "STRUCTURAL_DOMAIN", "StructuralDomain", "StructuralRuntime",
    "structural_beam_max_moment", "structural_beam_max_deflection",
    "structural_euler_buckling_load", "structural_section_modulus_rectangular",
    "structural_mohr_circle_principal_stresses", "structural_slenderness_ratio",
    "structural_von_mises_stress", "structural_torsion_shaft"
]
