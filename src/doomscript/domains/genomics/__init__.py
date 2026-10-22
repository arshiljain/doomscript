from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.genomics.runtime import (
    genomics_gc_content, genomics_smith_waterman, genomics_find_cpg_islands,
    genomics_parse_vcf_line
)
from doomscript.domains.genomics.parser import GenomicsDomainParser
from doomscript.domains.genomics.exporter import GenomicsASTExporter

class GenomicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class GenomicsDomain(DomainContract):
    name = "genomics"
    aliases = ["genomic", "variant_calling", "alignment"]
    description = "Smith-Waterman sequence alignment, GC content, and variant analysis"
    parser = GenomicsDomainParser()
    runtime = GenomicsRuntime()
    exporter = GenomicsASTExporter()
    capabilities = ["gc_content", "smith_waterman", "cpg_islands", "vcf_parse"]
    verbs = [
        VerbSpec(pattern="calculate gc content for sequence {seq:expr} into {target:ident}", description="Calculate GC percentage"),
        VerbSpec(pattern="align sequences local {s1:expr} and {s2:expr} into {target:ident}", description="Local sequence alignment")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate gc content ") or s.startswith("align sequences local ") or s.startswith("find cpg islands ") or s.startswith("parse vcf variant ")

GENOMICS_DOMAIN = GenomicsDomain()
get_domain_registry().register(GENOMICS_DOMAIN)

__all__ = [
    "GenomicsDomain", "GENOMICS_DOMAIN", "GenomicsRuntime",
    "genomics_gc_content", "genomics_smith_waterman", "genomics_find_cpg_islands",
    "genomics_parse_vcf_line"
]
