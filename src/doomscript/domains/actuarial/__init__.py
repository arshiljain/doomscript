from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.actuarial.runtime import (
    actuarial_gompertz_mortality_rate, actuarial_makeham_mortality_rate,
    actuarial_annuity_present_value, actuarial_term_insurance_premium,
    actuarial_loss_reserve, actuarial_chain_ladder_projection
)
from doomscript.domains.actuarial.parser import ActuarialDomainParser
from doomscript.domains.actuarial.exporter import ActuarialASTExporter

class ActuarialRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ActuarialDomain(DomainContract):
    name = "actuarial"
    aliases = ["actuary", "insurance_math", "mortality"]
    description = "Actuarial science: Gompertz and Makeham mortality laws, annuity present value, term life premium, loss reserves, and Chain Ladder development"
    parser = ActuarialDomainParser()
    runtime = ActuarialRuntime()
    exporter = ActuarialASTExporter()
    capabilities = ["gompertz_mortality", "makeham_mortality", "annuity_present_value", "term_insurance_premium", "loss_reserve", "chain_ladder"]
    verbs = [
        VerbSpec(pattern="calculate gompertz mortality age {a:expr} base {b:expr} factor {c:expr} into {target:ident}", description="Gompertz mortality"),
        VerbSpec(pattern="calculate makeham mortality age {a:expr} accident {acc:expr} base {b:expr} factor {c:expr} into {target:ident}", description="Gompertz-Makeham mortality"),
        VerbSpec(pattern="calculate annuity present value payment {p:expr} rate {r:expr} years {n:expr} into {target:ident}", description="Annuity present value"),
        VerbSpec(pattern="calculate term insurance premium benefit {b:expr} mortality {q:expr} rate {r:expr} term {n:expr} into {target:ident}", description="Term insurance net single premium"),
        VerbSpec(pattern="calculate loss reserve claims {c:expr} severity {s:expr} rate {r:expr} into {target:ident}", description="Loss reserve"),
        VerbSpec(pattern="calculate chain ladder losses {l:expr} ratio {r:expr} into {target:ident}", description="Chain ladder ultimate loss projection")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate gompertz mortality ") or s.startswith("calculate makeham mortality ") or s.startswith("calculate annuity present value ") or s.startswith("calculate term insurance premium ") or s.startswith("calculate loss reserve ") or s.startswith("calculate chain ladder ")

ACTUARIAL_DOMAIN = ActuarialDomain()
get_domain_registry().register(ACTUARIAL_DOMAIN)

__all__ = [
    "ActuarialDomain", "ACTUARIAL_DOMAIN", "ActuarialRuntime",
    "actuarial_gompertz_mortality_rate", "actuarial_makeham_mortality_rate",
    "actuarial_annuity_present_value", "actuarial_term_insurance_premium",
    "actuarial_loss_reserve", "actuarial_chain_ladder_projection"
]
