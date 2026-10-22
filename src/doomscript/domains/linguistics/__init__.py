from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.linguistics.runtime import (
    ling_levenshtein_distance, ling_jaro_winkler, ling_soundex,
    ling_count_syllables, ling_flesch_reading_ease, ling_gunning_fog,
    ling_type_token_ratio
)
from doomscript.domains.linguistics.parser import LinguisticsDomainParser
from doomscript.domains.linguistics.exporter import LinguisticsASTExporter

class LinguisticsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class LinguisticsDomain(DomainContract):
    name = "linguistics"
    aliases = ["nlp_metrics", "text_linguistics", "readability"]
    description = "Computational linguistics: Levenshtein, Jaro-Winkler, Soundex, Flesch, Gunning Fog, and TTR"
    parser = LinguisticsDomainParser()
    runtime = LinguisticsRuntime()
    exporter = LinguisticsASTExporter()
    capabilities = ["levenshtein_distance", "jaro_winkler", "soundex", "syllable_count", "flesch_reading_ease", "gunning_fog", "type_token_ratio"]
    verbs = [
        VerbSpec(pattern="calculate edit distance for word1 {w1:expr} word2 {w2:expr} into {target:ident}", description="Edit distance"),
        VerbSpec(pattern="calculate jaro winkler for word1 {w1:expr} word2 {w2:expr} into {target:ident}", description="Jaro-Winkler"),
        VerbSpec(pattern="calculate gunning fog for text {text:expr} into {target:ident}", description="Gunning Fog")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate edit distance ") or s.startswith("calculate jaro winkler ") or s.startswith("calculate soundex ") or s.startswith("calculate syllables ") or s.startswith("calculate flesch readability ") or s.startswith("calculate gunning fog ") or s.startswith("calculate lexical diversity ")

LINGUISTICS_DOMAIN = LinguisticsDomain()
get_domain_registry().register(LINGUISTICS_DOMAIN)

__all__ = [
    "LinguisticsDomain", "LINGUISTICS_DOMAIN", "LinguisticsRuntime",
    "ling_levenshtein_distance", "ling_jaro_winkler", "ling_soundex",
    "ling_count_syllables", "ling_flesch_reading_ease", "ling_gunning_fog",
    "ling_type_token_ratio"
]
