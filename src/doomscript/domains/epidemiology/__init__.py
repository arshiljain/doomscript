from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.epidemiology.runtime import (
    epi_r0, epi_herd_immunity_threshold, epi_sir_step,
    epi_seir_step, epi_fatality_rates
)
from doomscript.domains.epidemiology.parser import EpidemiologyDomainParser
from doomscript.domains.epidemiology.exporter import EpidemiologyASTExporter

class EpidemiologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class EpidemiologyDomain(DomainContract):
    name = "epidemiology"
    aliases = ["disease_spread", "outbreak", "sir_model"]
    description = "Epidemiological modeling: R0, herd immunity, SIR/SEIR compartmental models, and CFR analysis"
    parser = EpidemiologyDomainParser()
    runtime = EpidemiologyRuntime()
    exporter = EpidemiologyASTExporter()
    capabilities = ["reproduction_number", "herd_immunity", "sir_step", "seir_step", "fatality_rates"]
    verbs = [
        VerbSpec(pattern="calculate reproduction number r0 for beta {b:expr} gamma {g:expr} into {target:ident}", description="R0 calculation"),
        VerbSpec(pattern="step sir model s {s:expr} i {i:expr} r {r:expr} beta {b:expr} gamma {g:expr} into {target:ident}", description="SIR step"),
        VerbSpec(pattern="step seir model s {s:expr} e {e:expr} i {i:expr} r {r:expr} beta {b:expr} sigma {sig:expr} gamma {g:expr} into {target:ident}", description="SEIR step")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate reproduction number ") or s.startswith("calculate herd immunity threshold ") or s.startswith("step sir model ") or s.startswith("step seir model ") or s.startswith("calculate cfr ")

EPIDEMIOLOGY_DOMAIN = EpidemiologyDomain()
get_domain_registry().register(EPIDEMIOLOGY_DOMAIN)

__all__ = [
    "EpidemiologyDomain", "EPIDEMIOLOGY_DOMAIN", "EpidemiologyRuntime",
    "epi_r0", "epi_herd_immunity_threshold", "epi_sir_step",
    "epi_seir_step", "epi_fatality_rates"
]
