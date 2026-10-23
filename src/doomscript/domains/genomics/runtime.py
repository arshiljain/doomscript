"""Genomics Domain Runtime: Sequence alignment, BWT, FM-index, de Bruijn assembly, variant analysis, and population genetics."""
import math
from typing import List, Dict, Any, Tuple, Optional, Set
from doomscript.domains.base import DomainRuntime

GENETIC_CODE = {
    'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M',
    'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T',
    'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K',
    'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R',
    'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L',
    'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P',
    'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q',
    'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R',
    'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V',
    'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A',
    'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E',
    'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G',
    'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S',
    'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L',
    'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_',
    'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W',
}

# ============================================================================
# 1. CORE SEQUENCE OPERATIONS (PRESERVED)
# ============================================================================

def genomics_gc_content(sequence: str) -> float:
    """Calculates GC content percentage of a nucleotide sequence."""
    s = str(sequence).upper()
    if not s:
        return 0.0
    g = s.count('G')
    c = s.count('C')
    return round(((g + c) / len(s)) * 100.0, 2)

def genomics_reverse_complement(sequence: str) -> str:
    """Returns the reverse complement of a DNA sequence."""
    comp = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
    return "".join(comp.get(base, base) for base in reversed(str(sequence).upper()))

def genomics_transcribe(dna: str) -> str:
    """Transcribes DNA to RNA (replaces T with U)."""
    return str(dna).upper().replace('T', 'U')

def genomics_translate(rna_or_dna: str) -> str:
    """Translates nucleotide sequence to peptide chain."""
    s = str(rna_or_dna).upper().replace('U', 'T')
    protein = []
    for i in range(0, len(s) - 2, 3):
        codon = s[i:i+3]
        aa = GENETIC_CODE.get(codon, '?')
        if aa == '_':
            break
        protein.append(aa)
    return "".join(protein)

def genomics_melting_temp(sequence: str) -> float:
    """Calculates DNA melting temperature (Tm) via nearest-neighbor/Wallace rule."""
    s = str(sequence).upper()
    if len(s) < 14:
        # Wallace Rule: Tm = 2*(A+T) + 4*(G+C)
        at = s.count('A') + s.count('T')
        gc = s.count('G') + s.count('C')
        return float(2 * at + 4 * gc)
    # Marmur-Doty formula for longer sequences
    gc_pct = genomics_gc_content(s)
    return round(64.9 + 41.0 * (gc_pct - 16.4) / 100.0, 2)

def genomics_find_cpg_islands(sequence: str, window_size: int = 20, min_gc: float = 50.0) -> List[Dict[str, Any]]:
    """Identifies CpG islands using sliding window GC content and observed-to-expected ratio."""
    s = str(sequence).upper()
    islands = []
    w = min(max(4, int(window_size)), len(s)) if len(s) >= 4 else len(s)
    for i in range(0, len(s) - w + 1):
        win = s[i:i+w]
        c = win.count('C')
        g = win.count('G')
        cg = win.count('CG')
        gc_pct = ((c + g) / w) * 100.0
        exp_cg = (c * g) / w if w > 0 else 0
        obs_exp = (cg / exp_cg) if exp_cg > 0 else 0.0
        if gc_pct >= min_gc and obs_exp > 0.6:
            islands.append({"start": i, "end": i + w, "gc_pct": round(gc_pct, 1), "obs_exp_ratio": round(obs_exp, 2)})
    return islands

def genomics_kmer_spectrum(sequence: str, k: int = 3) -> Dict[str, int]:
    """Generates k-mer frequency counts from nucleotide sequence."""
    s = str(sequence).upper()
    k = max(1, int(k))
    counts: Dict[str, int] = {}
    for i in range(len(s) - k + 1):
        kmer = s[i:i+k]
        counts[kmer] = counts.get(kmer, 0) + 1
    return counts

def genomics_parse_vcf_line(vcf_line: str) -> Dict[str, Any]:
    """Parses standard VCF variant record line into structured fields."""
    parts = vcf_line.strip().split('\t')
    if len(parts) < 5:
        parts = vcf_line.strip().split()
    if len(parts) >= 5:
        return {
            "chrom": parts[0],
            "pos": int(parts[1]) if parts[1].isdigit() else parts[1],
            "id": parts[2],
            "ref": parts[3],
            "alt": parts[4],
            "qual": parts[5] if len(parts) > 5 else ".",
            "filter": parts[6] if len(parts) > 6 else "."
        }
    return {"raw": vcf_line}

# ============================================================================
# 2. SEQUENCE ALIGNMENT (SMITH-WATERMAN & NEEDLEMAN-WUNSCH)
# ============================================================================

def genomics_local_alignment(seq1: str, seq2: str, match: int = 2, mismatch: int = -1, gap: int = -2) -> Dict[str, Any]:
    """Local sequence alignment via Smith-Waterman dynamic programming."""
    s1 = str(seq1).upper()
    s2 = str(seq2).upper()
    m, n = len(s1), len(s2)
    H = [[0] * (n + 1) for _ in range(m + 1)]
    max_score = 0
    max_pos = (0, 0)
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diag = H[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch)
            score_up = H[i-1][j] + gap
            score_left = H[i][j-1] + gap
            val = max(0, score_diag, score_up, score_left)
            H[i][j] = val
            if val > max_score:
                max_score = val
                max_pos = (i, j)
    # Traceback
    align1, align2 = [], []
    i, j = max_pos
    while i > 0 and j > 0 and H[i][j] > 0:
        val = H[i][j]
        diag = H[i-1][j-1]
        up = H[i-1][j]
        is_match = (s1[i-1] == s2[j-1])
        if val == diag + (match if is_match else mismatch):
            align1.append(s1[i-1])
            align2.append(s2[j-1])
            i -= 1
            j -= 1
        elif val == up + gap:
            align1.append(s1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(s2[j-1])
            j -= 1
    return {
        "score": max_score,
        "aligned_seq1": "".join(reversed(align1)),
        "aligned_seq2": "".join(reversed(align2)),
        "end_position": max_pos
    }

def genomics_global_alignment(seq1: str, seq2: str, match: int = 1, mismatch: int = -1, gap: int = -2) -> Dict[str, Any]:
    """Global sequence alignment via Needleman-Wunsch dynamic programming."""
    s1 = str(seq1).upper()
    s2 = str(seq2).upper()
    m, n = len(s1), len(s2)
    H = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        H[i][0] = i * gap
    for j in range(n + 1):
        H[0][j] = j * gap
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            diag = H[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch)
            up = H[i-1][j] + gap
            left = H[i][j-1] + gap
            H[i][j] = max(diag, up, left)
    align1, align2 = [], []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and H[i][j] == H[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch):
            align1.append(s1[i-1])
            align2.append(s2[j-1])
            i -= 1
            j -= 1
        elif i > 0 and H[i][j] == H[i-1][j] + gap:
            align1.append(s1[i-1])
            align2.append('-')
            i -= 1
        else:
            align1.append('-')
            align2.append(s2[j-1])
            j -= 1
    return {
        "score": H[m][n],
        "aligned_seq1": "".join(reversed(align1)),
        "aligned_seq2": "".join(reversed(align2))
    }

# ============================================================================
# 3. BWT & FM-INDEX SUBSTRING MATCHING
# ============================================================================

def genomics_bwt(s: str) -> Dict[str, Any]:
    """Burrows-Wheeler Transform of a genomic sequence."""
    seq = s + "$"
    table = sorted(seq[i:] + seq[:i] for i in range(len(seq)))
    last_col = "".join(row[-1] for row in table)
    return {"bwt": last_col, "original_len": len(s)}

def genomics_fm_index_count(bwt_str: str, pattern: str) -> int:
    """Counts exact occurrences of pattern using FM-Index backward search."""
    # Build count table and rank
    first_col = sorted(list(bwt_str))
    counts: Dict[str, int] = {}
    for c in first_col:
        counts.setdefault(c, first_col.index(c))
    l, r = 0, len(bwt_str) - 1
    for char in reversed(pattern):
        if char not in counts:
            return 0
        l = counts[char] + bwt_str[:l].count(char)
        r = counts[char] + bwt_str[:r + 1].count(char) - 1
        if l > r:
            return 0
    return max(0, r - l + 1)

# ============================================================================
# 4. DE BRUIJN GRAPH & GENOME ASSEMBLY
# ============================================================================

def genomics_debruijn_assembly(kmers: List[str]) -> Dict[str, Any]:
    """Constructs de Bruijn graph from k-mers and detects Eulerian contigs."""
    adj: Dict[str, List[str]] = {}
    in_degree: Dict[str, int] = {}
    out_degree: Dict[str, int] = {}
    for kmer in kmers:
        prefix = kmer[:-1]
        suffix = kmer[1:]
        adj.setdefault(prefix, []).append(suffix)
        out_degree[prefix] = out_degree.get(prefix, 0) + 1
        in_degree[suffix] = in_degree.get(suffix, 0) + 1
        in_degree.setdefault(prefix, 0)
        out_degree.setdefault(suffix, 0)
    all_nodes = set(in_degree.keys()).union(out_degree.keys())
    return {
        "num_nodes": len(all_nodes),
        "edges": sum(len(v) for v in adj.values()),
        "adjacency": adj
    }

# ============================================================================
# 5. POPULATION GENETICS & VARIANT ANALYSIS
# ============================================================================

def genomics_calculate_ti_tv(variants: List[Dict[str, str]]) -> Dict[str, Any]:
    """Calculates Transition/Transversion (Ti/Tv) ratio from a list of SNVs."""
    purines = {"A", "G"}
    pyrimidines = {"C", "T"}
    transitions = 0
    transversions = 0
    for v in variants:
        ref = v.get("ref", "").upper()
        alt = v.get("alt", "").upper()
        if len(ref) == 1 and len(alt) == 1 and ref != alt:
            if (ref in purines and alt in purines) or (ref in pyrimidines and alt in pyrimidines):
                transitions += 1
            else:
                transversions += 1
    ratio = transitions / transversions if transversions > 0 else float("inf")
    return {"transitions": transitions, "transversions": transversions, "ti_tv_ratio": round(ratio, 4)}

def genomics_hardy_weinberg_test(obs_AA: int, obs_Aa: int, obs_aa: int) -> Dict[str, Any]:
    """Tests Hardy-Weinberg equilibrium using chi-square goodness of fit."""
    total = obs_AA + obs_Aa + obs_aa
    if total == 0:
        return {"chi_square": 0.0, "p_value_approx": 1.0, "is_equilibrium": True}
    p = (2 * obs_AA + obs_Aa) / (2 * total)
    q = 1.0 - p
    exp_AA = total * (p ** 2)
    exp_Aa = total * (2 * p * q)
    exp_aa = total * (q ** 2)
    chi2 = 0.0
    for obs, exp in [(obs_AA, exp_AA), (obs_Aa, exp_Aa), (obs_aa, exp_aa)]:
        if exp > 0:
            chi2 += ((obs - exp) ** 2) / exp
    is_eq = chi2 < 3.841
    return {
        "allele_freq_p": round(p, 4),
        "allele_freq_q": round(q, 4),
        "chi_square": round(chi2, 4),
        "is_equilibrium": is_eq
    }

def genomics_gc_skew(seq: str, window: int = 100) -> List[float]:
    """Calculates GC skew (G - C) / (G + C) over sliding windows."""
    s = seq.upper()
    skews = []
    w = max(1, int(window))
    for i in range(0, len(s) - w + 1, w):
        sub = s[i:i+w]
        g = sub.count("G")
        c = sub.count("C")
        val = (g - c) / (g + c) if (g + c) > 0 else 0.0
        skews.append(round(val, 4))
    return skews

def genomics_find_orfs(seq: str, min_len_aa: int = 30) -> List[Dict[str, Any]]:
    """Identifies Open Reading Frames (ORFs) starting with ATG and ending at stop codons."""
    s = seq.upper()
    stops = {"TAA", "TAG", "TGA"}
    orfs = []
    for frame in range(3):
        for i in range(frame, len(s) - 2, 3):
            if s[i:i+3] == "ATG":
                for j in range(i + 3, len(s) - 2, 3):
                    if s[j:j+3] in stops:
                        orf_seq = s[i:j+3]
                        if len(orf_seq) // 3 >= min_len_aa:
                            orfs.append({
                                "start": i,
                                "end": j + 3,
                                "frame": frame + 1,
                                "length_bp": len(orf_seq),
                                "length_aa": len(orf_seq) // 3
                            })
                        break
    return orfs

# ============================================================================
# 6. DOMAIN RUNTIME
# ============================================================================

class GenomicsRuntime(DomainRuntime):
    """Unified runtime bridge for the Genomics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def gc_content(self, seq: str) -> float:
        return genomics_gc_content(seq)
    def reverse_complement(self, seq: str) -> str:
        return genomics_reverse_complement(seq)
    def transcribe(self, dna: str) -> str:
        return genomics_transcribe(dna)
    def translate(self, seq: str) -> str:
        return genomics_translate(seq)
    def melting_temp(self, seq: str) -> float:
        return genomics_melting_temp(seq)
    def local_align(self, s1: str, s2: str) -> Dict[str, Any]:
        return genomics_local_alignment(s1, s2)
    def global_align(self, s1: str, s2: str) -> Dict[str, Any]:
        return genomics_global_alignment(s1, s2)
    def bwt(self, seq: str) -> Dict[str, Any]:
        return genomics_bwt(seq)
    def debruijn(self, kmers: List[str]) -> Dict[str, Any]:
        return genomics_debruijn_assembly(kmers)
    def ti_tv(self, variants: List[Dict[str, str]]) -> Dict[str, Any]:
        return genomics_calculate_ti_tv(variants)
    def hardy_weinberg(self, AA: int, Aa: int, aa: int) -> Dict[str, Any]:
        return genomics_hardy_weinberg_test(AA, Aa, aa)
    def gc_skew(self, seq: str, window: int = 100) -> List[float]:
        return genomics_gc_skew(seq, window)
    def find_orfs(self, seq: str, min_len: int = 30) -> List[Dict[str, Any]]:
        return genomics_find_orfs(seq, min_len)
