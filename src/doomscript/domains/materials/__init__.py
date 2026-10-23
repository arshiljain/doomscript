"""Materials Science Domain for DoomScript: Solid mechanics, elasticity, plasticity, fracture mechanics, composites, and hardness."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.materials.parser import MaterialsDomainParser
from doomscript.domains.materials.runtime import (
    MaterialsRuntime,
    materials_stress_strain,
    materials_mohrs_circle,
    materials_thermal_expansion,
    materials_stress_intensity,
    materials_rule_of_mixtures,
    materials_tresca_von_mises_yield,
    materials_ramberg_osgood_strain,
    materials_johnson_cook_flow_stress,
    materials_charpy_dbtt_hyperbolic,
    materials_halpin_tsai_short_fiber,
    materials_brinell_hardness_conversion
)
from doomscript.domains.materials.exporter import MaterialsASTExporter

class MaterialsDomain(DomainContract):
    name = "materials"
    aliases = ["mechanics_of_materials", "solid_mechanics", "stress_strain"]
    description = "Materials science & solid mechanics: Stress-strain, Mohr's circle, fracture mechanics, composites, yield criteria, and hardness."
    parser = MaterialsDomainParser()
    runtime = MaterialsRuntime()
    exporter = MaterialsASTExporter()
    capabilities = [
        "stress_strain",
        "mohrs_circle",
        "thermal_expansion",
        "stress_intensity",
        "rule_of_mixtures",
        "tresca_von_mises",
        "ramberg_osgood",
        "johnson_cook",
        "charpy_dbtt",
        "halpin_tsai",
        "hardness_conversion"
    ]
    verbs = [
        VerbSpec(pattern="calculate engineering stress and strain for force {f:expr} area {a:expr} delta {dl:expr} initial length {l0:expr} into {target:ident}", description="Calculates stress, strain, and Young's modulus"),
        VerbSpec(pattern="calculate mohrs circle principal stresses for sigma x {sx:expr} sigma y {sy:expr} tau {txy:expr} into {target:ident}", description="Calculates Mohr's circle principal stresses"),
        VerbSpec(pattern="calculate thermal expansion for length {l:expr} coeff {alpha:expr} delta temp {dt:expr} into {target:ident}", description="Calculates linear thermal expansion"),
        VerbSpec(pattern="calculate stress intensity for stress {s:expr} crack {a:expr} into {target:ident}", description="Calculates Mode I stress intensity factor K_I"),
        VerbSpec(pattern="calculate composite modulus fiber {ef:expr} matrix {em:expr} fraction {vf:expr} into {target:ident}", description="Calculates Voigt and Reuss composite modulus"),
        VerbSpec(pattern="evaluate yield criteria s1 {s1:expr} s2 {s2:expr} s3 {s3:expr} sy {sy:expr} into {target:ident}", description="Evaluates Tresca and von Mises yield criteria"),
        VerbSpec(pattern="calculate ramberg osgood stress {s:expr} modulus {e:expr} alpha {a:expr} sigma0 {s0:expr} n {n:expr} into {target:ident}", description="Calculates Ramberg-Osgood nonlinear elastoplastic strain"),
        VerbSpec(pattern="calculate johnson cook strain {ep:expr} rate {edot:expr} temp {t:expr} a {a:expr} b {b:expr} n {n:expr} c {c:expr} m {m:expr} into {target:ident}", description="Calculates dynamic viscoplastic flow stress"),
        VerbSpec(pattern="calculate dbtt temps {t:expr} energies {e:expr} into {target:ident}", description="Fits Charpy transition temperature"),
        VerbSpec(pattern="calculate halpin tsai fiber {ef:expr} matrix {em:expr} fraction {vf:expr} aspect {ar:expr} into {target:ident}", description="Calculates Halpin-Tsai short fiber modulus"),
        VerbSpec(pattern="convert hardness hb {hb:expr} into {target:ident}", description="Converts Brinell hardness to HV, HRC, and UTS")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate engineering stress ") or
            s.startswith("calculate mohrs circle ") or
            s.startswith("calculate thermal expansion ") or
            s.startswith("calculate stress intensity ") or
            s.startswith("calculate composite modulus ") or
            s.startswith("evaluate yield criteria ") or
            s.startswith("calculate ramberg osgood ") or
            s.startswith("calculate johnson cook ") or
            s.startswith("calculate dbtt ") or
            s.startswith("calculate halpin tsai ") or
            s.startswith("convert hardness ")
        )

MATERIALS_DOMAIN = MaterialsDomain()
get_domain_registry().register(MATERIALS_DOMAIN)

__all__ = [
    "MATERIALS_DOMAIN",
    "MaterialsDomain",
    "MaterialsRuntime",
    "materials_stress_strain",
    "materials_mohrs_circle",
    "materials_thermal_expansion",
    "materials_stress_intensity",
    "materials_rule_of_mixtures",
    "materials_tresca_von_mises_yield",
    "materials_ramberg_osgood_strain",
    "materials_johnson_cook_flow_stress",
    "materials_charpy_dbtt_hyperbolic",
    "materials_halpin_tsai_short_fiber",
    "materials_brinell_hardness_conversion"
]
