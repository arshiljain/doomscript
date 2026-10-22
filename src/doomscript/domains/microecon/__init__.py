from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.microecon.runtime import (
    microecon_price_elasticity, microecon_surplus, microecon_deadweight_loss,
    microecon_gini, microecon_cournot_duopoly, microecon_hhi_concentration
)
from doomscript.domains.microecon.parser import MicroeconDomainParser
from doomscript.domains.microecon.exporter import MicroeconASTExporter

class MicroeconRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class MicroeconDomain(DomainContract):
    name = "microecon"
    aliases = ["microeconomics", "supply_demand", "welfare_economics"]
    description = "Microeconomics: Price elasticity, welfare surplus, deadweight loss, Gini coefficient, Cournot duopoly, and HHI"
    parser = MicroeconDomainParser()
    runtime = MicroeconRuntime()
    exporter = MicroeconASTExporter()
    capabilities = ["price_elasticity", "surplus", "deadweight_loss", "gini", "cournot_duopoly", "hhi"]
    verbs = [
        VerbSpec(pattern="calculate price elasticity for q1 {q1:expr} q2 {q2:expr} p1 {p1:expr} p2 {p2:expr} into {target:ident}", description="Price elasticity"),
        VerbSpec(pattern="calculate cournot duopoly demand intercept {a:expr} slope {b:expr} marginal cost {c:expr} into {target:ident}", description="Cournot duopoly")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate price elasticity ") or s.startswith("calculate surplus ") or s.startswith("calculate deadweight loss ") or s.startswith("calculate gini coefficient ") or s.startswith("calculate cournot duopoly ") or s.startswith("calculate hhi ")

MICROECON_DOMAIN = MicroeconDomain()
get_domain_registry().register(MICROECON_DOMAIN)

__all__ = [
    "MicroeconDomain", "MICROECON_DOMAIN", "MicroeconRuntime",
    "microecon_price_elasticity", "microecon_surplus", "microecon_deadweight_loss",
    "microecon_gini", "microecon_cournot_duopoly", "microecon_hhi_concentration"
]
