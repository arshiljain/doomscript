from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.ergonomics.runtime import (
    ergo_niosh_rwl, ergo_rula_score, ergo_metabolic_expenditure,
    ergo_reba_score, ergo_strain_index
)
from doomscript.domains.ergonomics.parser import ErgonomicsDomainParser
from doomscript.domains.ergonomics.exporter import ErgonomicsASTExporter

class ErgonomicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ErgonomicsDomain(DomainContract):
    name = "ergonomics"
    aliases = ["ergo", "human_factors", "workplace_safety"]
    description = "Ergonomics and human factors: NIOSH lifting equation, RULA assessment, metabolic expenditure, REBA scoring, and Moore-Garg Strain Index"
    parser = ErgonomicsDomainParser()
    runtime = ErgonomicsRuntime()
    exporter = ErgonomicsASTExporter()
    capabilities = ["niosh_rwl", "rula_score", "metabolic_expenditure", "reba_score", "strain_index"]
    verbs = [
        VerbSpec(pattern="calculate niosh lifting limit load {lc:expr} horiz {h:expr} vert {v:expr} dist {d:expr} angle {a:expr} freq {f:expr} coupling {c:expr} into {target:ident}", description="NIOSH lifting limit"),
        VerbSpec(pattern="calculate rula score upper {u:expr} lower {l:expr} wrist {w:expr} neck {n:expr} trunk {t:expr} load {load:expr} into {target:ident}", description="RULA posture score"),
        VerbSpec(pattern="calculate metabolic expenditure weight {w:expr} met {m:expr} minutes {t:expr} into {target:ident}", description="Metabolic expenditure"),
        VerbSpec(pattern="calculate reba score trunk {t:expr} neck {n:expr} legs {l:expr} uarm {ua:expr} larm {la:expr} wrist {w:expr} into {target:ident}", description="REBA entire body score"),
        VerbSpec(pattern="calculate strain index intensity {im:expr} duration {dm:expr} efforts {em:expr} posture {pm:expr} into {target:ident}", description="Moore-Garg Strain Index")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate niosh lifting limit ") or s.startswith("calculate rula score ") or s.startswith("calculate metabolic expenditure ") or s.startswith("calculate reba score ") or s.startswith("calculate strain index ")

ERGONOMICS_DOMAIN = ErgonomicsDomain()
get_domain_registry().register(ERGONOMICS_DOMAIN)

__all__ = [
    "ErgonomicsDomain", "ERGONOMICS_DOMAIN", "ErgonomicsRuntime",
    "ergo_niosh_rwl", "ergo_rula_score", "ergo_metabolic_expenditure",
    "ergo_reba_score", "ergo_strain_index"
]
