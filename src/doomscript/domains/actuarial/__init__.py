from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.actuarial.runtime import (
    ActuarialRuntime, actuarial_gompertz_mortality_rate,
    actuarial_makeham_mortality_rate, actuarial_annuity_present_value,
    actuarial_term_insurance_premium, actuarial_loss_reserve,
    actuarial_chain_ladder_projection, actuarial_chain_ladder_triangle,
    actuarial_curtate_life_expectancy, actuarial_cramer_lundberg_ruin
)
from doomscript.domains.actuarial.parser import ActuarialDomainParser
from doomscript.domains.actuarial.exporter import ActuarialASTExporter

class ActuarialDomain(DomainContract):
    name = "actuarial"
    aliases = ["actuary", "insurance_math", "mortality"]
    description = "Deepened Actuarial domain: Gompertz/Makeham mortality, life annuities, term insurance premiums, Chain Ladder loss reserving, and ruin theory"
    parser = ActuarialDomainParser()
    runtime = ActuarialRuntime()
    exporter = ActuarialASTExporter()
    capabilities = ["gompertz_mortality", "makeham_mortality", "annuity_pv", "term_insurance", "loss_reserve", "chain_ladder", "life_expectancy", "ruin_theory"]
    verbs = [
        VerbSpec(pattern="calculate gompertz mortality age {age:expr} base {b:expr} factor {c:expr} into {target:ident}", description="Gompertz mortality hazard rate"),
        VerbSpec(pattern="calculate makeham mortality age {age:expr} accident {a:expr} base {b:expr} factor {c:expr} into {target:ident}", description="Gompertz-Makeham mortality hazard rate"),
        VerbSpec(pattern="calculate annuity present value payment {p:expr} rate {r:expr} years {n:expr} into {target:ident}", description="Annuity present value"),
        VerbSpec(pattern="calculate term insurance premium benefit {b:expr} mortality {q:expr} rate {r:expr} term {n:expr} into {target:ident}", description="Term insurance net single premium"),
        VerbSpec(pattern="calculate loss reserve claims {c:expr} severity {s:expr} rate {r:expr} into {target:ident}", description="Discounted loss reserve"),
        VerbSpec(pattern="calculate chain ladder losses {l:expr} ratio {f:expr} into {target:ident}", description="Chain ladder ultimate loss projection"),
        VerbSpec(pattern="calculate life expectancy age {age:expr} into {target:ident}", description="Curtate life expectancy"),
        VerbSpec(pattern="calculate cramer lundberg ruin surplus {u:expr} premium {c:expr} frequency {lam:expr} mean_claim {mu:expr} into {target:ident}", description="Cramér-Lundberg ruin probability")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate gompertz mortality ") or
            s.startswith("calculate makeham mortality ") or
            s.startswith("calculate annuity present value ") or
            s.startswith("calculate term insurance premium ") or
            s.startswith("calculate loss reserve ") or
            s.startswith("calculate chain ladder ") or
            s.startswith("calculate life expectancy ") or
            s.startswith("calculate cramer lundberg ruin ")
        )

ACTUARIAL_DOMAIN = ActuarialDomain()
get_domain_registry().register(ACTUARIAL_DOMAIN)

__all__ = [
    "ACTUARIAL_DOMAIN", "ActuarialDomain", "ActuarialRuntime",
    "actuarial_gompertz_mortality_rate", "actuarial_makeham_mortality_rate",
    "actuarial_annuity_present_value", "actuarial_term_insurance_premium",
    "actuarial_loss_reserve", "actuarial_chain_ladder_projection",
    "actuarial_chain_ladder_triangle", "actuarial_curtate_life_expectancy",
    "actuarial_cramer_lundberg_ruin"
]
