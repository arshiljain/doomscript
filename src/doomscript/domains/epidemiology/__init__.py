from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.epidemiology.runtime import (
    epi_r0, epi_herd_immunity_threshold, epi_sir_step
)
from doomscript.domains.epidemiology.parser import EpidemiologyDomainParser
from doomscript.domains.epidemiology.exporter import EpidemiologyASTExporter

class EpidemiologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class EpidemiologyDomain(DomainContract):
    name = "epidemiology"
    aliases = ["epidemic", "sir_model", "disease_modeling"]
    description = "SIR epidemic model simulation, basic reproduction number R0, and herd immunity"
    parser = EpidemiologyDomainParser()
    runtime = EpidemiologyRuntime()
    exporter = EpidemiologyASTExporter()
    capabilities = ["r0", "herd_immunity", "sir_step"]
    verbs = [
        VerbSpec(pattern="calculate reproduction number r0 for beta {b:expr} gamma {g:expr} into {target:ident}", description="Basic reproduction number"),
        VerbSpec(pattern="calculate herd immunity threshold for r0 {r:expr} into {target:ident}", description="Herd immunity threshold")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate reproduction number ") or s.startswith("calculate herd immunity ") or s.startswith("step sir model ")

EPIDEMIOLOGY_DOMAIN = EpidemiologyDomain()
get_domain_registry().register(EPIDEMIOLOGY_DOMAIN)

__all__ = [
    "EpidemiologyDomain", "EPIDEMIOLOGY_DOMAIN", "EpidemiologyRuntime",
    "epi_r0", "epi_herd_immunity_threshold", "epi_sir_step"
]
