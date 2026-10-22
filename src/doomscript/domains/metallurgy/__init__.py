from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.metallurgy.runtime import (
    metal_hall_petch_yield_strength, metal_hollomon_true_stress,
    metal_lever_rule, metal_scheil_solidification,
    metal_jmak_recrystallization, metal_arrhenius_diffusion
)
from doomscript.domains.metallurgy.parser import MetallurgyDomainParser
from doomscript.domains.metallurgy.exporter import MetallurgyASTExporter

class MetallurgyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class MetallurgyDomain(DomainContract):
    name = "metallurgy"
    aliases = ["metal", "alloys", "materials_science"]
    description = "Physical metallurgy: Hall-Petch strength, Hollomon strain hardening, lever rule, Scheil solidification, JMAK recrystallization, and Arrhenius diffusion"
    parser = MetallurgyDomainParser()
    runtime = MetallurgyRuntime()
    exporter = MetallurgyASTExporter()
    capabilities = ["hall_petch_strength", "hollomon_stress", "lever_rule", "scheil_solidification", "jmak_recrystallization", "arrhenius_diffusion"]
    verbs = [
        VerbSpec(pattern="calculate hall petch strength friction {s0:expr} locking {ky:expr} grain {d:expr} into {target:ident}", description="Hall-Petch strength"),
        VerbSpec(pattern="calculate hollomon true stress k {k:expr} strain {eps:expr} n {n:expr} into {target:ident}", description="Hollomon true stress"),
        VerbSpec(pattern="calculate lever rule overall {c0:expr} alpha {ca:expr} beta {cb:expr} into {target:ident}", description="Lever rule phase weights"),
        VerbSpec(pattern="calculate scheil composition initial {c0:expr} partition {k:expr} solid {fs:expr} into {target:ident}", description="Scheil solidification"),
        VerbSpec(pattern="calculate jmak recrystallization time {t:expr} k {k:expr} exponent {n:expr} into {target:ident}", description="JMAK recrystallization fraction"),
        VerbSpec(pattern="calculate metal diffusion d0 {d0:expr} energy {q:expr} temp {t:expr} into {target:ident}", description="Arrhenius atomic diffusion")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate hall petch strength ") or s.startswith("calculate hollomon true stress ") or s.startswith("calculate lever rule ") or s.startswith("calculate scheil composition ") or s.startswith("calculate jmak recrystallization ") or s.startswith("calculate metal diffusion ")

METALLURGY_DOMAIN = MetallurgyDomain()
get_domain_registry().register(METALLURGY_DOMAIN)

__all__ = [
    "MetallurgyDomain", "METALLURGY_DOMAIN", "MetallurgyRuntime",
    "metal_hall_petch_yield_strength", "metal_hollomon_true_stress",
    "metal_lever_rule", "metal_scheil_solidification",
    "metal_jmak_recrystallization", "metal_arrhenius_diffusion"
]
