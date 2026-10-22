from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.pharmacology.runtime import (
    pharm_elimination_rate, pharm_steady_state_conc,
    pharm_volume_of_distribution, pharm_hill_equation,
    pharm_michaelis_menten_elimination_rate, pharm_loading_dose
)
from doomscript.domains.pharmacology.parser import PharmacologyDomainParser
from doomscript.domains.pharmacology.exporter import PharmacologyASTExporter

class PharmacologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class PharmacologyDomain(DomainContract):
    name = "pharmacology"
    aliases = ["pharm", "pharmacokinetics", "pk_pd"]
    description = "Pharmacology and PK/PD: elimination kinetics, steady state, volume of distribution, Hill dose-response, Michaelis-Menten clearance, and loading dose"
    parser = PharmacologyDomainParser()
    runtime = PharmacologyRuntime()
    exporter = PharmacologyASTExporter()
    capabilities = ["elimination_rate", "steady_state_conc", "volume_of_distribution", "hill_equation", "michaelis_menten", "loading_dose"]
    verbs = [
        VerbSpec(pattern="calculate elimination rate halflife {hl:expr} into {target:ident}", description="Elimination rate constant"),
        VerbSpec(pattern="calculate steady state conc dose {d:expr} bioavailability {f:expr} clearance {cl:expr} interval {tau:expr} into {target:ident}", description="Steady state plasma concentration"),
        VerbSpec(pattern="calculate volume distribution dose {d:expr} c0 {c0:expr} into {target:ident}", description="Volume of distribution"),
        VerbSpec(pattern="calculate hill response conc {c:expr} emax {emax:expr} ec50 {ec50:expr} hill {n:expr} into {target:ident}", description="Hill dose-response"),
        VerbSpec(pattern="calculate saturable elimination vmax {vm:expr} km {km:expr} conc {c:expr} into {target:ident}", description="Michaelis-Menten elimination rate"),
        VerbSpec(pattern="calculate loading dose vd {vd:expr} target {ct:expr} bio {f:expr} into {target:ident}", description="Target loading dose")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate elimination rate ") or s.startswith("calculate steady state conc ") or s.startswith("calculate volume distribution ") or s.startswith("calculate hill response ") or s.startswith("calculate saturable elimination ") or s.startswith("calculate loading dose ")

PHARMACOLOGY_DOMAIN = PharmacologyDomain()
get_domain_registry().register(PHARMACOLOGY_DOMAIN)

__all__ = [
    "PharmacologyDomain", "PHARMACOLOGY_DOMAIN", "PharmacologyRuntime",
    "pharm_elimination_rate", "pharm_steady_state_conc",
    "pharm_volume_of_distribution", "pharm_hill_equation",
    "pharm_michaelis_menten_elimination_rate", "pharm_loading_dose"
]
