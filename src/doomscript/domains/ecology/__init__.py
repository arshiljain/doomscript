from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.ecology.runtime import (
    ecology_shannon_diversity, ecology_simpson_diversity, ecology_pielou_evenness,
    ecology_island_biogeography, ecology_lotka_volterra_step, ecology_logistic_growth,
    ecology_lincoln_petersen_estimate
)
from doomscript.domains.ecology.parser import EcologyDomainParser
from doomscript.domains.ecology.exporter import EcologyASTExporter

class EcologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class EcologyDomain(DomainContract):
    name = "ecology"
    aliases = ["biodiversity", "population_dynamics", "ecosystems"]
    description = "Ecology & population dynamics: Shannon/Simpson biodiversity, Pielou evenness, Lotka-Volterra, and mark-recapture"
    parser = EcologyDomainParser()
    runtime = EcologyRuntime()
    exporter = EcologyASTExporter()
    capabilities = ["shannon_diversity", "simpson_diversity", "pielou_evenness", "lotka_volterra", "logistic_growth", "mark_recapture"]
    verbs = [
        VerbSpec(pattern="calculate shannon diversity for abundances {counts:expr} into {target:ident}", description="Shannon index"),
        VerbSpec(pattern="calculate pielou evenness for abundances {counts:expr} into {target:ident}", description="Pielou evenness"),
        VerbSpec(pattern="estimate population marked {n1:expr} captured {n2:expr} recaptured {m2:expr} into {target:ident}", description="Lincoln-Petersen estimate")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate shannon diversity ") or s.startswith("calculate simpson diversity ") or s.startswith("calculate pielou evenness ") or s.startswith("step lotka volterra ") or s.startswith("calculate logistic growth ") or s.startswith("estimate population ")

ECOLOGY_DOMAIN = EcologyDomain()
get_domain_registry().register(ECOLOGY_DOMAIN)

__all__ = [
    "EcologyDomain", "ECOLOGY_DOMAIN", "EcologyRuntime",
    "ecology_shannon_diversity", "ecology_simpson_diversity", "ecology_pielou_evenness",
    "ecology_island_biogeography", "ecology_lotka_volterra_step", "ecology_logistic_growth",
    "ecology_lincoln_petersen_estimate"
]
