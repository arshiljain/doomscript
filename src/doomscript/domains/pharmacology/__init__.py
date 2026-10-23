from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.pharmacology.runtime import (
    PharmacologyRuntime, pharm_elimination_rate, pharm_steady_state_conc,
    pharm_volume_of_distribution, pharm_hill_equation,
    pharm_michaelis_menten_elimination_rate, pharm_loading_dose,
    pharm_cockcroft_gault_crcl, pharm_trapezoidal_auc,
    pharm_two_compartment_iv_bolus
)
from doomscript.domains.pharmacology.parser import PharmacologyDomainParser
from doomscript.domains.pharmacology.exporter import PharmacologyASTExporter

class PharmacologyDomain(DomainContract):
    name = "pharmacology"
    aliases = ["pharm", "pharmacokinetics", "pk_pd"]
    description = "Deepened Pharmacology domain: Elimination rates, steady-state plasma concentrations, volume of distribution, Hill dose-response, Michaelis-Menten kinetics, and Cockcroft-Gault CrCl"
    parser = PharmacologyDomainParser()
    runtime = PharmacologyRuntime()
    exporter = PharmacologyASTExporter()
    capabilities = ["elimination_rate", "steady_state_conc", "volume_distribution", "hill_response", "saturable_elimination", "loading_dose", "creatinine_clearance", "auc"]
    verbs = [
        VerbSpec(pattern="calculate elimination rate halflife {t:expr} into {target:ident}", description="Elimination rate constant ke"),
        VerbSpec(pattern="calculate steady state conc dose {d:expr} bioavailability {f:expr} clearance {cl:expr} interval {tau:expr} into {target:ident}", description="Average steady state concentration Css"),
        VerbSpec(pattern="calculate volume distribution dose {d:expr} c0 {c0:expr} into {target:ident}", description="Apparent volume of distribution Vd"),
        VerbSpec(pattern="calculate hill response conc {c:expr} emax {emax:expr} ec50 {ec50:expr} hill {n:expr} into {target:ident}", description="Hill pharmacodynamic sigmoid response"),
        VerbSpec(pattern="calculate saturable elimination vmax {vmax:expr} km {km:expr} conc {c:expr} into {target:ident}", description="Michaelis-Menten elimination rate"),
        VerbSpec(pattern="calculate loading dose vd {vd:expr} target {target_c:expr} bio {f:expr} into {target:ident}", description="Target loading dose"),
        VerbSpec(pattern="calculate creatinine clearance age {age:expr} weight {wt:expr} scr {scr:expr} into {target:ident}", description="Cockcroft-Gault creatinine clearance")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate elimination rate ") or
            s.startswith("calculate steady state conc ") or
            s.startswith("calculate volume distribution ") or
            s.startswith("calculate hill response ") or
            s.startswith("calculate saturable elimination ") or
            s.startswith("calculate loading dose ") or
            s.startswith("calculate creatinine clearance ")
        )

PHARMACOLOGY_DOMAIN = PharmacologyDomain()
get_domain_registry().register(PHARMACOLOGY_DOMAIN)

__all__ = [
    "PHARMACOLOGY_DOMAIN", "PharmacologyDomain", "PharmacologyRuntime",
    "pharm_elimination_rate", "pharm_steady_state_conc",
    "pharm_volume_of_distribution", "pharm_hill_equation",
    "pharm_michaelis_menten_elimination_rate", "pharm_loading_dose",
    "pharm_cockcroft_gault_crcl", "pharm_trapezoidal_auc",
    "pharm_two_compartment_iv_bolus"
]
