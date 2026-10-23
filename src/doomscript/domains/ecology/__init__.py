from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.ecology.runtime import (
    EcologyRuntime, ecology_shannon_diversity, ecology_simpson_diversity,
    ecology_pielou_evenness, ecology_island_biogeography,
    ecology_lotka_volterra_step, ecology_logistic_growth,
    ecology_lincoln_petersen_estimate, ecology_levins_metapopulation,
    ecology_pianka_niche_overlap
)
from doomscript.domains.ecology.parser import EcologyDomainParser
from doomscript.domains.ecology.exporter import EcologyASTExporter

class EcologyDomain(DomainContract):
    name = "ecology"
    aliases = ["biodiversity", "population_dynamics", "ecosystems"]
    description = "Deepened Ecology domain: Shannon/Simpson biodiversity, island biogeography, Lotka-Volterra dynamics, mark-recapture, and metapopulation models"
    parser = EcologyDomainParser()
    runtime = EcologyRuntime()
    exporter = EcologyASTExporter()
    capabilities = ["shannon_diversity", "simpson_diversity", "pielou_evenness", "island_biogeography", "lotka_volterra", "logistic_growth", "mark_recapture", "metapopulation", "niche_overlap"]
    verbs = [
        VerbSpec(pattern="calculate shannon diversity abundances {abundances:expr} into {target:ident}", description="Shannon-Wiener diversity index"),
        VerbSpec(pattern="calculate simpson diversity abundances {abundances:expr} into {target:ident}", description="Gini-Simpson diversity index"),
        VerbSpec(pattern="calculate pielou evenness abundances {abundances:expr} into {target:ident}", description="Pielou species evenness"),
        VerbSpec(pattern="calculate island biogeography area {a:expr} constant {c:expr} exponent {z:expr} into {target:ident}", description="MacArthur-Wilson species-area law"),
        VerbSpec(pattern="step lotka volterra prey {x:expr} pred {y:expr} alpha {a:expr} beta {b:expr} gamma {g:expr} delta {d:expr} dt {dt:expr} into {target:ident}", description="Lotka-Volterra predator-prey step"),
        VerbSpec(pattern="calculate logistic growth n0 {n0:expr} rate {r:expr} capacity {k:expr} time {t:expr} into {target:ident}", description="Logistic population growth"),
        VerbSpec(pattern="estimate population mark recapture n1 {n1:expr} n2 {n2:expr} m2 {m2:expr} into {target:ident}", description="Chapman mark-recapture estimation")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate shannon diversity ") or
            s.startswith("calculate simpson diversity ") or
            s.startswith("calculate pielou evenness ") or
            s.startswith("calculate island biogeography ") or
            s.startswith("step lotka volterra ") or
            s.startswith("calculate logistic growth ") or
            s.startswith("estimate population mark recapture ")
        )

ECOLOGY_DOMAIN = EcologyDomain()
get_domain_registry().register(ECOLOGY_DOMAIN)

__all__ = [
    "ECOLOGY_DOMAIN", "EcologyDomain", "EcologyRuntime",
    "ecology_shannon_diversity", "ecology_simpson_diversity",
    "ecology_pielou_evenness", "ecology_island_biogeography",
    "ecology_lotka_volterra_step", "ecology_logistic_growth",
    "ecology_lincoln_petersen_estimate", "ecology_levins_metapopulation",
    "ecology_pianka_niche_overlap"
]
