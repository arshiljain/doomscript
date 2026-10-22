from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.ecology.runtime import (
    ecology_shannon_diversity, ecology_simpson_diversity,
    ecology_lotka_volterra_step, ecology_logistic_growth
)
from doomscript.domains.ecology.parser import EcologyDomainParser
from doomscript.domains.ecology.exporter import EcologyASTExporter

class EcologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class EcologyDomain(DomainContract):
    name = "ecology"
    aliases = ["biodiversity", "population_dynamics", "ecosystems"]
    description = "Shannon/Simpson biodiversity indices and Lotka-Volterra predator-prey dynamics"
    parser = EcologyDomainParser()
    runtime = EcologyRuntime()
    exporter = EcologyASTExporter()
    capabilities = ["shannon_diversity", "simpson_diversity", "lotka_volterra", "logistic_growth"]
    verbs = [
        VerbSpec(pattern="calculate shannon diversity for abundances {counts:expr} into {target:ident}", description="Shannon index"),
        VerbSpec(pattern="calculate logistic growth for n0 {n0:expr} r {r:expr} k {k:expr} time {t:expr} into {target:ident}", description="Logistic growth")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate shannon diversity ") or s.startswith("calculate simpson diversity ") or s.startswith("step lotka volterra ") or s.startswith("calculate logistic growth ")

ECOLOGY_DOMAIN = EcologyDomain()
get_domain_registry().register(ECOLOGY_DOMAIN)

__all__ = [
    "EcologyDomain", "ECOLOGY_DOMAIN", "EcologyRuntime",
    "ecology_shannon_diversity", "ecology_simpson_diversity",
    "ecology_lotka_volterra_step", "ecology_logistic_growth"
]
