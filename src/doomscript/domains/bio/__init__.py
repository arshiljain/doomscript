"""Bioinformatics & Computational Biology Domain Pack for DoomScript.

Enables native spoken-English genome analysis, sequence alignment, codon translation,
FASTA reading, and motif discovery via 'use bio'.
"""

from typing import List, Optional
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.bio.runtime import (
    BioRuntime,
    bio_gc_content,
    bio_transcribe_dna,
    bio_reverse_complement,
    bio_translate_rna,
    bio_find_orfs,
    bio_count_kmers,
    bio_find_motif,
    bio_molecular_weight,
    bio_needleman_wunsch,
    bio_smith_waterman,
    bio_parse_fasta,
    SequenceAligner,
    FMIndexBWT,
    PhylogeneticTreeNJ,
    bio_affine_align,
    bio_fm_index_search,
    bio_neighbor_joining_tree,
    NussinovRNA,
    RestrictionEnzymeDigest,
    CodonAdaptationIndex,
    bio_predict_rna_structure,
    bio_digest_dna,
    bio_calculate_cai,
)
from doomscript.domains.bio.parser import BioDomainParser
from doomscript.domains.bio.exporter import BioASTExporter


class BioDomain(DomainContract):
    """Domain contract for Bioinformatics & Computational Biology."""

    name = "bio"
    aliases = ["genomics", "bioinformatics"]
    description = "Bioinformatics, sequence alignment, genomics, and computational biology"
    parser = BioDomainParser()
    runtime = BioRuntime()
    exporter = BioASTExporter()
    capabilities = ["dna", "alignment", "translation", "fasta", "kmers"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="calculate gc content of {seq:expr} into {target:ident}",
            description="Calculates GC percentage of a DNA or RNA sequence",
        ),
        VerbSpec(
            pattern="transcribe dna {seq:expr} into {target:ident}",
            description="Transcribes DNA to RNA",
        ),
        VerbSpec(
            pattern="reverse complement of {seq:expr} into {target:ident}",
            description="Generates reverse complement of DNA sequence",
        ),
        VerbSpec(
            pattern="translate rna {seq:expr} into {target:ident}",
            description="Translates nucleotide sequence into amino acid protein chain",
        ),
        VerbSpec(
            pattern="align sequences {s1:expr} and {s2:expr} using needleman wunsch into {target:ident}",
            description="Performs global Needleman-Wunsch or local Smith-Waterman sequence alignment",
        ),
        VerbSpec(
            pattern="parse fasta [string] {text:expr} into {target:ident}",
            description="Parses multi-record FASTA strings into structured records",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("calculate gc content of ")
            or s.startswith("transcribe dna ")
            or s.startswith("reverse complement of ")
            or s.startswith("calculate reverse complement of ")
            or s.startswith("translate rna ")
            or s.startswith("translate dna ")
            or s.startswith("translate ")
            or s.startswith("find open reading frames in ")
            or s.startswith("count kmers in ")
            or s.startswith("find motif ")
            or s.startswith("calculate molecular weight of ")
            or s.startswith("align sequences ")
            or s.startswith("parse fasta ")
            or s.startswith("predict rna structure of ")
            or s.startswith("digest dna ")
            or s.startswith("calculate cai of ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


BIO_DOMAIN = BioDomain()
get_domain_registry().register(BIO_DOMAIN)

__all__ = [
    "BioDomain",
    "BIO_DOMAIN",
    "BioRuntime",
    "BioDomainParser",
    "BioASTExporter",
    "bio_gc_content",
    "bio_transcribe_dna",
    "bio_reverse_complement",
    "bio_translate_rna",
    "bio_find_orfs",
    "bio_count_kmers",
    "bio_find_motif",
    "bio_molecular_weight",
    "bio_needleman_wunsch",
    "bio_smith_waterman",
    "bio_parse_fasta",
    "SequenceAligner",
    "FMIndexBWT",
    "PhylogeneticTreeNJ",
    "bio_affine_align",
    "bio_fm_index_search",
    "bio_neighbor_joining_tree",
    "NussinovRNA",
    "RestrictionEnzymeDigest",
    "CodonAdaptationIndex",
    "bio_predict_rna_structure",
    "bio_digest_dna",
    "bio_calculate_cai",
]
