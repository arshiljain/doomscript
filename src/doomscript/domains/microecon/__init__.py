from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.microecon.runtime import (
    micro_price_elasticity, micro_surplus, micro_deadweight_loss, micro_gini_coefficient
)
from doomscript.domains.microecon.parser import MicroeconDomainParser
from doomscript.domains.microecon.exporter import MicroeconASTExporter

class MicroeconRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class MicroeconDomain(DomainContract):
    name = "microecon"
    aliases = ["economics", "market_equilibrium", "surplus"]
    description = "Price elasticity, consumer/producer surplus, deadweight loss, and Gini coefficient"
    parser = MicroeconDomainParser()
    runtime = MicroeconRuntime()
    exporter = MicroeconASTExporter()
    capabilities = ["price_elasticity", "market_surplus", "deadweight_loss", "gini_coefficient"]
    verbs = [
        VerbSpec(pattern="calculate price elasticity for q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}", description="Elasticity"),
        VerbSpec(pattern="calculate deadweight loss for tax {t:expr} quantity reduction {dq:expr} into {target:ident}", description="Deadweight loss")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate price elasticity ") or s.startswith("calculate surplus ") or s.startswith("calculate deadweight loss ") or s.startswith("calculate gini coefficient ")

MICROECON_DOMAIN = MicroeconDomain()
get_domain_registry().register(MICROECON_DOMAIN)

__all__ = [
    "MicroeconDomain", "MICROECON_DOMAIN", "MicroeconRuntime",
    "micro_price_elasticity", "micro_surplus", "micro_deadweight_loss", "micro_gini_coefficient"
]
