"""Genomics Domain Runtime: Sequence alignment (Smith-Waterman, Needleman-Wunsch), ORF finding, Melting Temp, and VCF parsing."""
import math
from typing import Dict, Any, List

def genomics_gc_content(sequence: str) -> float:
    """Calculates GC percentage of a DNA/RNA sequence."""
    seq = str(sequence).upper().strip()
    if not seq:
        return 0.0
    gc = sum(1 for b in seq if b in ("G", "C"))
    return round((gc / len(seq)) * 100.0, 2)

def genomics_reverse_complement(sequence: str) -> str:
    """Generates the reverse complement of a DNA sequence."""
    trans = str.maketrans("ATCGNatcgn", "TAGCNtagcn")
    return str(sequence).translate(trans)[::-1]

def genomics_transcribe(dna: str) -> str:
    """Transcribes DNA to RNA (T -> U)."""
    return str(dna).upper().replace("T", "U")

def genomics_translate(rna_or_dna: str) -> str:
    """Translates an RNA or DNA sequence into an amino acid peptide."""
    rna = str(rna_or_dna).upper().replace("T", "U")
    codon_table = {
        "AUG": "M", "UUU": "F", "UUC": "F", "UUA": "L", "UUG": "L",
        "UCU": "S", "UCC": "S", "UCA": "S", "UCG": "S", "UAU": "Y", "UAC": "Y",
        "UAA": "*", "UAG": "*", "UGA": "*", "UGU": "C", "UGC": "C", "UGG": "W",
        "CUU": "L", "CUC": "L", "CUA": "L", "CUG": "L", "CCU": "P", "CCC": "P",
        "CCA": "P", "CCG": "P", "CAU": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
        "CGU": "R", "CGC": "R", "CGA": "R", "CGG": "R", "AUU": "I", "AUC": "I",
        "AUA": "I", "ACU": "T", "ACC": "T", "ACA": "T", "ACG": "T", "AAU": "N",
        "AAC": "N", "AAA": "K", "AAG": "K", "AGU": "S", "AGC": "S", "AGA": "R",
        "AGG": "R", "GUU": "V", "GUC": "V", "GUA": "V", "GUG": "V", "GCU": "A",
        "GCC": "A", "GCA": "A", "GCG": "A", "GAU": "D", "GAC": "D", "GAA": "E",
        "GAG": "E", "GGU": "G", "GGC": "G", "GGA": "G", "GGG": "G"
    }
    peptide = []
    for i in range(0, len(rna) - 2, 3):
        codon = rna[i:i+3]
        aa = codon_table.get(codon, "X")
        peptide.append(aa)
        if aa == "*":
            break
    return "".join(peptide)

def genomics_local_alignment(seq1: str, seq2: str, match: int = 2, mismatch: int = -1, gap: int = -2) -> Dict[str, Any]:
    """Computes Smith-Waterman optimal local sequence alignment score."""
    s1, s2 = str(seq1).upper(), str(seq2).upper()
    m, n = len(s1), len(s2)
    score_matrix = [[0] * (n + 1) for _ in range(m + 1)]
    max_score = 0
    max_pos = (0, 0)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            diag = score_matrix[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch)
            up = score_matrix[i-1][j] + gap
            left = score_matrix[i][j-1] + gap
            sc = max(0, diag, up, left)
            score_matrix[i][j] = sc
            if sc > max_score:
                max_score = sc
                max_pos = (i, j)
    return {"score": max_score, "max_pos": max_pos}

def genomics_global_alignment(seq1: str, seq2: str, match: int = 1, mismatch: int = -1, gap: int = -2) -> Dict[str, Any]:
    """Computes Needleman-Wunsch optimal global sequence alignment score."""
    s1, s2 = str(seq1).upper(), str(seq2).upper()
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i * gap
    for j in range(n + 1):
        dp[0][j] = j * gap
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diag = dp[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch)
            score_up = dp[i-1][j] + gap
            score_left = dp[i][j-1] + gap
            dp[i][j] = max(score_diag, score_up, score_left)
    return {"score": dp[m][n], "alignment_length": max(m, n)}

def genomics_find_cpg_islands(sequence: str, window_size: int = 20, min_gc: float = 50.0) -> List[Dict[str, Any]]:
    """Identifies CpG islands in a genomic DNA sequence."""
    seq = str(sequence).upper().strip()
    islands = []
    w = max(4, int(window_size))
    for i in range(0, max(1, len(seq) - w + 1), max(1, w // 2)):
        window = seq[i:i+w]
        gc = genomics_gc_content(window)
        cpg_count = window.count("CG")
        if gc >= min_gc and cpg_count >= 2:
            islands.append({"start": i, "end": i + len(window), "gc_content": gc, "cpg_count": cpg_count})
    return islands

def genomics_melting_temp(sequence: str) -> float:
    """Calculates DNA melting temperature (Tm) in Celsius using basic Wallace / thermodynamic approximation."""
    seq = str(sequence).upper().strip()
    if not seq:
        return 0.0
    a = seq.count("A")
    t = seq.count("T")
    c = seq.count("C")
    g = seq.count("G")
    if len(seq) < 14:
        # Wallace rule: Tm = 2*(A+T) + 4*(G+C)
        return float(2 * (a + t) + 4 * (g + c))
    else:
        # Marmur-Doty formula adjusted: 64.9 + 41*(G+C - 16.4) / (A+T+G+C)
        tm = 64.9 + 41.0 * (g + c - 16.4) / len(seq)
        return round(tm, 2)

def genomics_parse_vcf_line(vcf_line: str) -> Dict[str, Any]:
    """Parses a standard VCF variant text line into structured variant fields."""
    parts = str(vcf_line).strip().split()
    if len(parts) < 5:
        return {"error": "Invalid VCF format"}
    return {
        "chrom": parts[0],
        "pos": int(parts[1]) if parts[1].isdigit() else parts[1],
        "id": parts[2],
        "ref": parts[3],
        "alt": parts[4],
        "qual": float(parts[5]) if len(parts) > 5 and parts[5] != "." else None,
        "filter": parts[6] if len(parts) > 6 else "PASS"
    }

def genomics_kmer_spectrum(sequence: str, k: int = 3) -> Dict[str, int]:
    """Calculates k-mer frequency distribution for a nucleotide sequence."""
    seq = str(sequence).upper().strip()
    k_val = max(1, int(k))
    counts = {}
    for i in range(len(seq) - k_val + 1):
        kmer = seq[i:i+k_val]
        counts[kmer] = counts.get(kmer, 0) + 1
    return counts
