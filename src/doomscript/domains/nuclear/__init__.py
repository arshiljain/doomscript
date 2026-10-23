"""Nuclear Physics Domain for DoomScript: Radioactive decay, reactor kinetics, radiation protection, and nuclear reactions."""
from typing import Any, Dict
from doomscript.domains.base import DomainContract, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.nuclear.parser import NuclearDomainParser
from doomscript.domains.nuclear.runtime import (
    NuclearRuntime,
    nuclear_radioactive_decay,
    nuclear_decay_constant,
    nuclear_reaction_q_value,
    nuclear_radiation_shielding,
    nuclear_four_factor_formula,
    nuclear_half_value_layer,
    nuclear_critical_slab_thickness,
    nuclear_inhour_equation,
    nuclear_secular_equilibrium,
    nuclear_binding_energy_weizsacker,
    nuclear_dose_rate_gamma,
    nuclear_thermal_neutron_flux
)
from doomscript.domains.nuclear.exporter import NuclearASTExporter

class NuclearDomain(DomainContract):
    name = "nuclear"
    aliases = ["radioactive", "atomic", "radiation_physics"]
    description = "Radioactive decay, reactor kinetics, radiation protection, and nuclear reactions."
    parser = NuclearDomainParser()
    runtime = NuclearRuntime()
    exporter = NuclearASTExporter()
    capabilities = [
        "radioactive_decay",
        "decay_constant",
        "nuclear_q_value",
        "radiation_shielding",
        "four_factor",
        "half_value_layer",
        "critical_slab_thickness",
        "inhour_equation",
        "secular_equilibrium",
        "binding_energy_weizsacker",
        "dose_rate_gamma",
        "thermal_neutron_flux"
    ]
    verbs = [
        VerbSpec(pattern="calculate radioactive decay initial {a0:expr} halflife {hl:expr} time {t:expr} into {target:ident}", description="Calculates remaining radioactive activity"),
        VerbSpec(pattern="calculate decay constant halflife {hl:expr} into {target:ident}", description="Calculates decay constant lambda"),
        VerbSpec(pattern="calculate nuclear q value mass_in {mi:expr} mass_out {mf:expr} into {target:ident}", description="Calculates nuclear reaction Q-value in MeV"),
        VerbSpec(pattern="calculate radiation shielding initial {i0:expr} attenuation {mu:expr} thickness {x:expr} into {target:ident}", description="Calculates transmitted radiation through shielding"),
        VerbSpec(pattern="calculate four factor eta {eta:expr} epsilon {eps:expr} p {p:expr} f {f:expr} into {target:ident}", description="Calculates Fermi four-factor k_inf"),
        VerbSpec(pattern="calculate half value layer attenuation {mu:expr} into {target:ident}", description="Calculates radiation Half-Value Layer in cm"),
        VerbSpec(pattern="calculate critical slab d {d:expr} sigma_a {sa:expr} nu_sigma_f {nsf:expr} into {target:ident}", description="Calculates critical slab reactor thickness"),
        VerbSpec(pattern="calculate inhour period prompt {l:expr} beta {b:expr} lambda {lam:expr} rho {rho:expr} into {target:ident}", description="Calculates reactor period using the inhour relation"),
        VerbSpec(pattern="calculate secular equilibrium t_parent {t1:expr} t_daughter {t2:expr} activity {a1:expr} time {t:expr} into {target:ident}", description="Calculates Bateman parent-daughter decay activities"),
        VerbSpec(pattern="calculate binding energy protons {z:expr} neutrons {n:expr} into {target:ident}", description="Calculates Bethe-Weizsacker SEMF binding energy"),
        VerbSpec(pattern="calculate gamma dose activity {a:expr} energy {e:expr} distance {r:expr} into {target:ident}", description="Calculates gamma dose rate in air and tissue"),
        VerbSpec(pattern="calculate neutron flux power {p:expr} volume {v:expr} into {target:ident}", description="Estimates reactor thermal neutron flux")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate radioactive decay ") or
            s.startswith("calculate decay constant ") or
            s.startswith("calculate nuclear q value ") or
            s.startswith("calculate radiation shielding ") or
            s.startswith("calculate four factor ") or
            s.startswith("calculate half value layer ") or
            s.startswith("calculate critical slab ") or
            s.startswith("calculate inhour period ") or
            s.startswith("calculate secular equilibrium ") or
            s.startswith("calculate binding energy ") or
            s.startswith("calculate gamma dose ") or
            s.startswith("calculate neutron flux ")
        )

NUCLEAR_DOMAIN = NuclearDomain()
get_domain_registry().register(NUCLEAR_DOMAIN)

__all__ = [
    "NUCLEAR_DOMAIN",
    "NuclearDomain",
    "NuclearRuntime",
    "nuclear_radioactive_decay",
    "nuclear_decay_constant",
    "nuclear_reaction_q_value",
    "nuclear_radiation_shielding",
    "nuclear_four_factor_formula",
    "nuclear_half_value_layer",
    "nuclear_critical_slab_thickness",
    "nuclear_inhour_equation",
    "nuclear_secular_equilibrium",
    "nuclear_binding_energy_weizsacker",
    "nuclear_dose_rate_gamma",
    "nuclear_thermal_neutron_flux"
]
