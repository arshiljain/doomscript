from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.nuclear.runtime import (
    nuclear_radioactive_decay, nuclear_decay_constant,
    nuclear_reaction_q_value, nuclear_radiation_shielding,
    nuclear_four_factor_formula, nuclear_half_value_layer
)
from doomscript.domains.nuclear.parser import NuclearDomainParser
from doomscript.domains.nuclear.exporter import NuclearASTExporter

class NuclearRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class NuclearDomain(DomainContract):
    name = "nuclear"
    aliases = ["radioactive", "atomic", "radiation_physics"]
    description = "Nuclear physics & engineering: radioactive decay, decay constant, reaction Q-value, radiation shielding, Four-Factor Formula, and Half-Value Layer"
    parser = NuclearDomainParser()
    runtime = NuclearRuntime()
    exporter = NuclearASTExporter()
    capabilities = ["radioactive_decay", "decay_constant", "nuclear_q_value", "radiation_shielding", "four_factor", "half_value_layer"]
    verbs = [
        VerbSpec(pattern="calculate radioactive decay initial {a0:expr} halflife {hl:expr} time {t:expr} into {target:ident}", description="Radioactive decay"),
        VerbSpec(pattern="calculate decay constant halflife {hl:expr} into {target:ident}", description="Decay constant"),
        VerbSpec(pattern="calculate nuclear q value mass_in {mi:expr} mass_out {mf:expr} into {target:ident}", description="Reaction Q-value"),
        VerbSpec(pattern="calculate radiation shielding initial {i0:expr} attenuation {mu:expr} thickness {x:expr} into {target:ident}", description="Radiation shielding attenuation"),
        VerbSpec(pattern="calculate four factor eta {eta:expr} epsilon {eps:expr} p {p:expr} f {f:expr} into {target:ident}", description="Four-factor formula"),
        VerbSpec(pattern="calculate half value layer attenuation {mu:expr} into {target:ident}", description="Half-Value Layer")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate radioactive decay ") or s.startswith("calculate decay constant ") or s.startswith("calculate nuclear q value ") or s.startswith("calculate radiation shielding ") or s.startswith("calculate four factor ") or s.startswith("calculate half value layer ")

NUCLEAR_DOMAIN = NuclearDomain()
get_domain_registry().register(NUCLEAR_DOMAIN)

__all__ = [
    "NuclearDomain", "NUCLEAR_DOMAIN", "NuclearRuntime",
    "nuclear_radioactive_decay", "nuclear_decay_constant",
    "nuclear_reaction_q_value", "nuclear_radiation_shielding",
    "nuclear_four_factor_formula", "nuclear_half_value_layer"
]
