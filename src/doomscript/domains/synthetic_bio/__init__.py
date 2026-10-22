from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.synthetic_bio.runtime import (
    synbio_hill_activation, synbio_hill_repression, synbio_michaelis_menten,
    synbio_gibson_assembly_overlap, synbio_toggle_switch_step,
    synbio_repressilator_step, synbio_codon_adaptation_index
)
from doomscript.domains.synthetic_bio.parser import Synthetic_bioDomainParser
from doomscript.domains.synthetic_bio.exporter import SyntheticBioASTExporter

class SyntheticBioRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class SyntheticBioDomain(DomainContract):
    name = "synthetic_bio"
    aliases = ["synbio", "genetic_circuits", "bio_engineering"]
    description = "Synthetic biology: Hill kinetics, Gardner toggle switch, Repressilator, Michaelis-Menten, and Gibson assembly"
    parser = Synthetic_bioDomainParser()
    runtime = SyntheticBioRuntime()
    exporter = SyntheticBioASTExporter()
    capabilities = ["hill_activation", "hill_repression", "michaelis_menten", "gibson_assembly", "toggle_switch", "repressilator", "codon_adaptation_index"]
    verbs = [
        VerbSpec(pattern="calculate hill activation for conc {x:expr} k {k:expr} n {n:expr} into {target:ident}", description="Hill activation"),
        VerbSpec(pattern="calculate enzyme rate substrate {s:expr} vmax {v:expr} km {km:expr} into {target:ident}", description="Michaelis-Menten rate"),
        VerbSpec(pattern="check gibson overlap frag1 {f1:expr} frag2 {f2:expr} into {target:ident}", description="Gibson overlap")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate hill activation ") or s.startswith("calculate hill repression ") or s.startswith("calculate enzyme rate ") or s.startswith("check gibson overlap ") or s.startswith("step toggle switch ") or s.startswith("step repressilator ") or s.startswith("calculate codon adaptation index ")

SYNTHETIC_BIO_DOMAIN = SyntheticBioDomain()
get_domain_registry().register(SYNTHETIC_BIO_DOMAIN)

__all__ = [
    "SyntheticBioDomain", "SYNTHETIC_BIO_DOMAIN", "SyntheticBioRuntime",
    "synbio_hill_activation", "synbio_hill_repression", "synbio_michaelis_menten",
    "synbio_gibson_assembly_overlap", "synbio_toggle_switch_step",
    "synbio_repressilator_step", "synbio_codon_adaptation_index"
]
