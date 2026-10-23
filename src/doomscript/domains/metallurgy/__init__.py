from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.metallurgy.runtime import (
    MetallurgyRuntime, metal_hall_petch_yield_strength,
    metal_hollomon_true_stress, metal_lever_rule,
    metal_scheil_solidification, metal_jmak_recrystallization,
    metal_arrhenius_diffusion, metal_zener_hollomon,
    metal_koistinen_marburger_martensite, metal_paris_crack_growth
)
from doomscript.domains.metallurgy.parser import MetallurgyDomainParser
from doomscript.domains.metallurgy.exporter import MetallurgyASTExporter

class MetallurgyDomain(DomainContract):
    name = "metallurgy"
    aliases = ["metal", "alloys", "materials_science"]
    description = "Deepened Metallurgy domain: Hall-Petch strength, Hollomon strain hardening, Lever rule, Scheil solidification, JMAK recrystallization, and martensitic transformations"
    parser = MetallurgyDomainParser()
    runtime = MetallurgyRuntime()
    exporter = MetallurgyASTExporter()
    capabilities = ["hall_petch", "hollomon_stress", "lever_rule", "scheil_solidification", "jmak_recrystallization", "arrhenius_diffusion", "zener_hollomon", "martensite_fraction"]
    verbs = [
        VerbSpec(pattern="calculate hall petch strength friction {s0:expr} locking {ky:expr} grain {d:expr} into {target:ident}", description="Hall-Petch grain boundary strengthening"),
        VerbSpec(pattern="calculate hollomon true stress k {k:expr} strain {eps:expr} n {n:expr} into {target:ident}", description="Hollomon strain hardening law"),
        VerbSpec(pattern="calculate lever rule overall {c0:expr} alpha {ca:expr} beta {cb:expr} into {target:ident}", description="Binary lever rule phase fractions"),
        VerbSpec(pattern="calculate scheil composition initial {c0:expr} partition {k:expr} solid {fs:expr} into {target:ident}", description="Scheil non-equilibrium solidification"),
        VerbSpec(pattern="calculate jmak recrystallization time {t:expr} k {k:expr} exponent {n:expr} into {target:ident}", description="JMAK recrystallization kinetics"),
        VerbSpec(pattern="calculate arrhenius diffusion d0 {d0:expr} q {q:expr} temp {t:expr} into {target:ident}", description="Arrhenius atomic diffusion coefficient")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate hall petch strength ") or
            s.startswith("calculate hollomon true stress ") or
            s.startswith("calculate lever rule ") or
            s.startswith("calculate scheil composition ") or
            s.startswith("calculate jmak recrystallization ") or
            s.startswith("calculate arrhenius diffusion ") or s.startswith("calculate metal diffusion ") or
            s.startswith("calculate martensite fraction ")
        )

METALLURGY_DOMAIN = MetallurgyDomain()
get_domain_registry().register(METALLURGY_DOMAIN)

__all__ = [
    "METALLURGY_DOMAIN", "MetallurgyDomain", "MetallurgyRuntime",
    "metal_hall_petch_yield_strength", "metal_hollomon_true_stress",
    "metal_lever_rule", "metal_scheil_solidification",
    "metal_jmak_recrystallization", "metal_arrhenius_diffusion",
    "metal_zener_hollomon", "metal_koistinen_marburger_martensite",
    "metal_paris_crack_growth"
]
