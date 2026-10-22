from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.structural.runtime import (
    structural_beam_max_moment, structural_beam_max_deflection,
    structural_euler_buckling_load, structural_section_modulus_rectangular,
    structural_mohr_circle_principal_stresses, structural_slenderness_ratio
)
from doomscript.domains.structural.parser import StructuralDomainParser
from doomscript.domains.structural.exporter import StructuralASTExporter

class StructuralRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class StructuralDomain(DomainContract):
    name = "structural"
    aliases = ["civil_structures", "structural_analysis", "beams"]
    description = "Structural engineering: beam bending moment, elastic deflection, Euler buckling, section modulus, Mohr's circle principal stresses, and slenderness ratio"
    parser = StructuralDomainParser()
    runtime = StructuralRuntime()
    exporter = StructuralASTExporter()
    capabilities = ["beam_max_moment", "beam_max_deflection", "euler_buckling_load", "section_modulus", "mohr_principal_stresses", "slenderness_ratio"]
    verbs = [
        VerbSpec(pattern="calculate beam max moment load {w:expr} span {l:expr} into {target:ident}", description="Beam maximum bending moment"),
        VerbSpec(pattern="calculate beam max deflection load {w:expr} span {l:expr} modulus {e:expr} inertia {i:expr} into {target:ident}", description="Beam elastic deflection"),
        VerbSpec(pattern="calculate column buckling load modulus {e:expr} inertia {i:expr} length {l:expr} factor {k:expr} into {target:ident}", description="Euler column buckling load"),
        VerbSpec(pattern="calculate section modulus width {b:expr} height {h:expr} into {target:ident}", description="Elastic section modulus"),
        VerbSpec(pattern="calculate mohr principal stresses sx {sx:expr} sy {sy:expr} txy {txy:expr} into {target:ident}", description="Mohr circle principal stresses"),
        VerbSpec(pattern="calculate slenderness ratio length {l:expr} radius {r:expr} into {target:ident}", description="Column slenderness ratio")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate beam max moment ") or s.startswith("calculate beam max deflection ") or s.startswith("calculate column buckling load ") or s.startswith("calculate section modulus ") or s.startswith("calculate mohr principal stresses ") or s.startswith("calculate slenderness ratio ")

STRUCTURAL_DOMAIN = StructuralDomain()
get_domain_registry().register(STRUCTURAL_DOMAIN)

__all__ = [
    "StructuralDomain", "STRUCTURAL_DOMAIN", "StructuralRuntime",
    "structural_beam_max_moment", "structural_beam_max_deflection",
    "structural_euler_buckling_load", "structural_section_modulus_rectangular",
    "structural_mohr_circle_principal_stresses", "structural_slenderness_ratio"
]
