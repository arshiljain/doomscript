from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.genomics.runtime import (
    GenomicsRuntime, genomics_gc_content, genomics_reverse_complement,
    genomics_transcribe, genomics_translate, genomics_local_alignment,
    genomics_global_alignment, genomics_find_cpg_islands, genomics_melting_temp,
    genomics_parse_vcf_line, genomics_kmer_spectrum, genomics_bwt,
    genomics_fm_index_count, genomics_debruijn_assembly, genomics_calculate_ti_tv,
    genomics_hardy_weinberg_test, genomics_gc_skew, genomics_find_orfs
)
from doomscript.domains.genomics.parser import GenomicsDomainParser
from doomscript.domains.genomics.exporter import GenomicsASTExporter

class GenomicsDomain(DomainContract):
    name = "genomics"
    aliases = ["dna", "rna", "genomic_analysis"]
    description = "Genomics & bioinformatics: Local/global alignment, CpG islands, melting temp, VCF parsing, BWT, and Hardy-Weinberg"
    parser = GenomicsDomainParser()
    runtime = GenomicsRuntime()
    exporter = GenomicsASTExporter()
    capabilities = [
        "gc_content", "local_alignment", "global_alignment", "cpg_islands",
        "melting_temp", "vcf_parsing", "kmer_spectrum", "bwt", "fm_index",
        "debruijn_assembly", "ti_tv_ratio", "hardy_weinberg", "gc_skew", "orfs"
    ]
    verbs = [
        VerbSpec(pattern="calculate gc content for sequence {seq:expr} into {target:ident}", description="GC content"),
        VerbSpec(pattern="align sequences local {s1:expr} and {s2:expr} into {target:ident}", description="Local alignment"),
        VerbSpec(pattern="align sequences global {s1:expr} and {s2:expr} into {target:ident}", description="Global alignment"),
        VerbSpec(pattern="calculate melting temp for sequence {seq:expr} into {target:ident}", description="Melting temperature"),
        VerbSpec(pattern="calculate hardy weinberg for AA {AA:expr} Aa {Aa:expr} aa {aa:expr} into {target:ident}", description="Hardy-Weinberg equilibrium test")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate gc content ") or
            s.startswith("align sequences local ") or
            s.startswith("align sequences global ") or
            s.startswith("find cpg islands ") or
            s.startswith("calculate melting temp ") or
            s.startswith("parse vcf variant record ") or
            s.startswith("calculate kmer spectrum ") or
            s.startswith("calculate hardy weinberg ")
        )

GENOMICS_DOMAIN = GenomicsDomain()
get_domain_registry().register(GENOMICS_DOMAIN)

__all__ = [
    "GenomicsDomain", "GENOMICS_DOMAIN", "GenomicsRuntime",
    "genomics_gc_content", "genomics_reverse_complement", "genomics_transcribe",
    "genomics_translate", "genomics_local_alignment", "genomics_global_alignment",
    "genomics_find_cpg_islands", "genomics_melting_temp", "genomics_parse_vcf_line",
    "genomics_kmer_spectrum", "genomics_bwt", "genomics_fm_index_count",
    "genomics_debruijn_assembly", "genomics_calculate_ti_tv",
    "genomics_hardy_weinberg_test", "genomics_gc_skew", "genomics_find_orfs"
]
