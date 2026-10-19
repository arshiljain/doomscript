"""Bioinformatics and Computational Biology Domain Runtime for DoomScript.

Pure Python standard library implementation of genomic sequence analysis,
sequence alignment algorithms (Needleman-Wunsch, Smith-Waterman), codon translation,
ORF search, k-mer frequency analysis, FASTA parsing, and motif discovery.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


# Standard Genetic Code Codon Table
CODON_TABLE: Dict[str, str] = {
    "ATA": "I", "ATC": "I", "ATT": "I", "ATG": "M",
    "ACA": "T", "ACC": "T", "ACG": "T", "ACT": "T",
    "AAC": "N", "AAT": "N", "AAA": "K", "AAG": "K",
    "AGC": "S", "AGT": "S", "AGA": "R", "AGG": "R",
    "CTA": "L", "CTC": "L", "CTG": "L", "CTT": "L",
    "CCA": "P", "CCC": "P", "CCG": "P", "CCT": "P",
    "CAC": "H", "CAT": "H", "CAA": "Q", "CAG": "Q",
    "CGA": "R", "CGC": "R", "CGG": "R", "CGT": "R",
    "GTA": "V", "GTC": "V", "GTG": "V", "GTT": "V",
    "GCA": "A", "GCC": "A", "GCG": "A", "GCT": "A",
    "GAC": "D", "GAT": "D", "GAA": "E", "GAG": "E",
    "GGA": "G", "GGC": "G", "GGG": "G", "GGT": "G",
    "TCA": "S", "TCC": "S", "TCG": "S", "TCT": "S",
    "TTC": "F", "TTT": "F", "TTA": "L", "TTG": "L",
    "TAC": "Y", "TAT": "Y", "TAA": "*", "TAG": "*",
    "TGC": "C", "TGT": "C", "TGA": "*", "TGG": "W",
}

# Monoisotopic Molecular Weights of Amino Acids (Da)
AMINO_ACID_WEIGHTS: Dict[str, float] = {
    "A": 71.03711, "R": 156.10111, "N": 114.04293, "D": 115.02694,
    "C": 103.00919, "E": 129.04259, "Q": 128.05858, "G": 57.02146,
    "H": 137.05891, "I": 113.08406, "L": 113.08406, "K": 128.09496,
    "M": 131.04049, "F": 147.06841, "P": 97.05276,  "S": 87.03203,
    "T": 101.04768, "W": 186.07931, "Y": 163.06333, "V": 99.06841
}


class BioRuntime(DomainRuntime):
    """Runtime coordinator for bioinformatics routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def bio_gc_content(dna_seq: Any) -> float:
    """Calculate the GC percentage of a DNA/RNA sequence."""
    seq = str(dna_seq).upper().strip()
    if not seq:
        return 0.0
    gc_count = seq.count("G") + seq.count("C")
    return round((gc_count / len(seq)) * 100.0, 4)


def bio_transcribe_dna(dna_seq: Any) -> str:
    """Transcribe DNA into RNA by converting Thymine (T) to Uracil (U)."""
    seq = str(dna_seq).upper().strip()
    return seq.replace("T", "U")


def bio_reverse_complement(dna_seq: Any) -> str:
    """Return the reverse complement of a DNA sequence."""
    seq = str(dna_seq).upper().strip()
    trans_map = str.maketrans("ATCGNatcgn", "TAGCNtagcn")
    return seq.translate(trans_map)[::-1]


def bio_translate_rna(rna_or_dna_seq: Any) -> str:
    """Translate an RNA (or DNA) sequence into an amino acid sequence."""
    seq = str(rna_or_dna_seq).upper().strip().replace("U", "T")
    protein = []
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i:i + 3]
        amino = CODON_TABLE.get(codon, "?")
        if amino == "*":
            break
        protein.append(amino)
    return "".join(protein)


def bio_find_orfs(dna_seq: Any, min_length: int = 30) -> List[Dict[str, Any]]:
    """Identify Open Reading Frames (ORFs) from start codon ATG to stop codons (TAA, TAG, TGA)."""
    seq = str(dna_seq).upper().strip()
    orfs: List[Dict[str, Any]] = []
    stop_codons = {"TAA", "TAG", "TGA"}

    for frame in range(3):
        i = frame
        while i < len(seq) - 2:
            if seq[i:i + 3] == "ATG":
                for j in range(i + 3, len(seq) - 2, 3):
                    codon = seq[j:j + 3]
                    if codon in stop_codons:
                        orf_seq = seq[i:j + 3]
                        if len(orf_seq) >= min_length:
                            orfs.append({
                                "start": i,
                                "end": j + 3,
                                "length": len(orf_seq),
                                "dna": orf_seq,
                                "protein": bio_translate_rna(orf_seq)
                            })
                        i = j
                        break
            i += 3
    return sorted(orfs, key=lambda x: x["length"], reverse=True)


def bio_count_kmers(seq: Any, k: int = 3) -> Dict[str, int]:
    """Calculate the frequency distribution of k-mers across a sequence."""
    s = str(seq).upper().strip()
    k = max(1, int(k))
    counts: Dict[str, int] = {}
    for i in range(len(s) - k + 1):
        kmer = s[i:i + k]
        counts[kmer] = counts.get(kmer, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def bio_find_motif(seq: Any, motif: Any) -> List[int]:
    """Find all 0-based starting positions of a motif in a nucleotide sequence."""
    s = str(seq).upper().strip()
    m = str(motif).upper().strip()
    if not m or not s:
        return []
    positions: List[int] = []
    pos = s.find(m)
    while pos != -1:
        positions.append(pos)
        pos = s.find(m, pos + 1)
    return positions


def bio_molecular_weight(protein_seq: Any) -> float:
    """Calculate the monoisotopic molecular weight of an amino acid sequence in Daltons."""
    seq = str(protein_seq).upper().strip()
    water_weight = 18.01528
    weight = water_weight
    for aa in seq:
        weight += AMINO_ACID_WEIGHTS.get(aa, 110.0)
    return round(weight, 4)


def bio_needleman_wunsch(seq1: Any, seq2: Any, match_score: int = 1, mismatch_penalty: int = -1, gap_penalty: int = -2) -> Dict[str, Any]:
    """Global sequence alignment using Needleman-Wunsch algorithm with full traceback."""
    s1 = str(seq1).upper().strip()
    s2 = str(seq2).upper().strip()
    n, m = len(s1), len(s2)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i * gap_penalty
    for j in range(m + 1):
        dp[0][j] = j * gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            score_diag = dp[i - 1][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty)
            score_up = dp[i - 1][j] + gap_penalty
            score_left = dp[i][j - 1] + gap_penalty
            dp[i][j] = max(score_diag, score_up, score_left)

    align1, align2 = [], []
    i, j = n, m
    while i > 0 and j > 0:
        score = dp[i][j]
        diag = dp[i - 1][j - 1]
        up = dp[i - 1][j]
        left = dp[i][j - 1]

        if score == diag + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty):
            align1.append(s1[i - 1])
            align2.append(s2[j - 1])
            i -= 1
            j -= 1
        elif score == up + gap_penalty:
            align1.append(s1[i - 1])
            align2.append("-")
            i -= 1
        else:
            align1.append("-")
            align2.append(s2[j - 1])
            j -= 1

    while i > 0:
        align1.append(s1[i - 1])
        align2.append("-")
        i -= 1
    while j > 0:
        align1.append("-")
        align2.append(s2[j - 1])
        j -= 1

    return {
        "score": dp[n][m],
        "alignment1": "".join(reversed(align1)),
        "alignment2": "".join(reversed(align2)),
    }


def bio_smith_waterman(seq1: Any, seq2: Any, match_score: int = 2, mismatch_penalty: int = -1, gap_penalty: int = -1) -> Dict[str, Any]:
    """Local sequence alignment using Smith-Waterman algorithm."""
    s1 = str(seq1).upper().strip()
    s2 = str(seq2).upper().strip()
    n, m = len(s1), len(s2)

    dp = [[0] * (m + 1) for _ in range(n + 1)]
    max_score = 0
    max_pos = (0, 0)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = dp[i - 1][j - 1] + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty)
            delete = dp[i - 1][j] + gap_penalty
            insert = dp[i][j - 1] + gap_penalty
            cell_val = max(0, match, delete, insert)
            dp[i][j] = cell_val
            if cell_val > max_score:
                max_score = cell_val
                max_pos = (i, j)

    align1, align2 = [], []
    i, j = max_pos
    while i > 0 and j > 0 and dp[i][j] > 0:
        score = dp[i][j]
        diag = dp[i - 1][j - 1]
        up = dp[i - 1][j]

        if score == diag + (match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty):
            align1.append(s1[i - 1])
            align2.append(s2[j - 1])
            i -= 1
            j -= 1
        elif score == up + gap_penalty:
            align1.append(s1[i - 1])
            align2.append("-")
            i -= 1
        else:
            align1.append("-")
            align2.append(s2[j - 1])
            j -= 1

    return {
        "score": max_score,
        "alignment1": "".join(reversed(align1)),
        "alignment2": "".join(reversed(align2)),
    }


def bio_parse_fasta(fasta_text: str) -> List[Dict[str, str]]:
    """Parse multi-record FASTA formatted text into header and sequence records."""
    records = []
    current_header = ""
    current_seq: List[str] = []

    normalized = str(fasta_text).replace("\\n", "\n")
    for line in normalized.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if current_header:
                records.append({
                    "id": current_header,
                    "sequence": "".join(current_seq)
                })
                current_seq = []
            current_header = line[1:].strip()
        else:
            current_seq.append(line.upper())

    if current_header:
        records.append({
            "id": current_header,
            "sequence": "".join(current_seq)
        })
    return records


# Ergonomic aliases
bio_transcribe = bio_transcribe_dna
bio_translate = bio_translate_rna
bio_kmer_counts = bio_count_kmers


def execute_bio_ir(spec_id: str) -> Any:
    """Executes a stored Bio IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown bio spec: {spec_id}")
    return BioRuntime().execute_ir(spec, {})
