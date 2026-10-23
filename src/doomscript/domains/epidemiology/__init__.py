"""Epidemiology Domain for DoomScript: Compartmental epidemic modeling, reproduction numbers, and outbreak investigations."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.epidemiology.parser import EpidemiologyDomainParser
from doomscript.domains.epidemiology.runtime import (
    EpidemiologyRuntime,
    epi_r0,
    epi_herd_immunity_threshold,
    epi_sir_step,
    epi_seir_step,
    epi_fatality_rates,
    epi_effective_reproduction_rt,
    epi_final_size_relation,
    epi_vaccination_critical_coverage,
    epi_generation_time_doubling,
    epi_attack_rate_odds_ratio,
    epi_secondary_attack_rate
)
from doomscript.domains.epidemiology.exporter import EpidemiologyASTExporter

class EpidemiologyDomain(DomainContract):
    name = "epidemiology"
    aliases = ["disease_spread", "outbreak", "sir_model"]
    description = "Compartmental epidemic modeling, reproduction numbers, herd immunity, and outbreak analytics."
    parser = EpidemiologyDomainParser()
    runtime = EpidemiologyRuntime()
    exporter = EpidemiologyASTExporter()
    capabilities = [
        "reproduction_number",
        "herd_immunity",
        "sir_step",
        "seir_step",
        "fatality_rates",
        "effective_rt",
        "final_size",
        "vaccination_threshold",
        "doubling_time",
        "attack_rate_odds_ratio",
        "secondary_attack_rate"
    ]
    verbs = [
        VerbSpec(pattern="calculate reproduction number r0 for beta {b:expr} gamma {g:expr} into {target:ident}", description="Calculates Basic Reproduction Number R0"),
        VerbSpec(pattern="calculate herd immunity threshold for r0 {r0:expr} into {target:ident}", description="Calculates Herd Immunity Threshold percentage"),
        VerbSpec(pattern="step sir model s {s:expr} i {i:expr} r {r:expr} beta {b:expr} gamma {g:expr} into {target:ident}", description="Single step of SIR compartmental model"),
        VerbSpec(pattern="step seir model s {s:expr} e {e:expr} i {i:expr} r {r:expr} beta {b:expr} sigma {sig:expr} gamma {g:expr} into {target:ident}", description="Single step of SEIR model with latency"),
        VerbSpec(pattern="calculate cfr for cases {c:expr} deaths {d:expr} into {target:ident}", description="Calculates Case Fatality Rate percentage"),
        VerbSpec(pattern="calculate effective rt r0 {r0:expr} susceptible {s:expr} into {target:ident}", description="Calculates time-varying effective reproduction number Rt"),
        VerbSpec(pattern="calculate final epidemic size r0 {r0:expr} into {target:ident}", description="Solves final epidemic attack rate relation"),
        VerbSpec(pattern="calculate vaccination threshold r0 {r0:expr} efficacy {e:expr} into {target:ident}", description="Calculates required population vaccination coverage"),
        VerbSpec(pattern="calculate epidemic doubling time r0 {r0:expr} generation {tg:expr} into {target:ident}", description="Calculates epidemic exponential doubling time"),
        VerbSpec(pattern="calculate outbreak odds ratio exp_cases {a:expr} exp_healthy {b:expr} unexp_cases {c:expr} unexp_healthy {d:expr} into {target:ident}", description="Calculates Relative Risk and Odds Ratio in 2x2 table"),
        VerbSpec(pattern="calculate secondary attack rate cases {sc:expr} contacts {k:expr} into {target:ident}", description="Calculates Secondary Attack Rate SAR")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate reproduction number ") or
            s.startswith("calculate herd immunity threshold ") or
            s.startswith("step sir model ") or
            s.startswith("step seir model ") or
            s.startswith("calculate cfr ") or
            s.startswith("calculate effective rt ") or
            s.startswith("calculate final epidemic size ") or
            s.startswith("calculate vaccination threshold ") or
            s.startswith("calculate epidemic doubling time ") or
            s.startswith("calculate outbreak odds ratio ") or
            s.startswith("calculate secondary attack rate ")
        )

EPIDEMIOLOGY_DOMAIN = EpidemiologyDomain()
get_domain_registry().register(EPIDEMIOLOGY_DOMAIN)

__all__ = [
    "EPIDEMIOLOGY_DOMAIN",
    "EpidemiologyDomain",
    "EpidemiologyRuntime",
    "epi_r0",
    "epi_herd_immunity_threshold",
    "epi_sir_step",
    "epi_seir_step",
    "epi_fatality_rates",
    "epi_effective_reproduction_rt",
    "epi_final_size_relation",
    "epi_vaccination_critical_coverage",
    "epi_generation_time_doubling",
    "epi_attack_rate_odds_ratio",
    "epi_secondary_attack_rate"
]
