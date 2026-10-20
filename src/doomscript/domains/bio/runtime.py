"""Bioinformatics and Computational Biology Domain Runtime for DoomScript.

Pure Python standard library implementation of genomic sequence analysis,
sequence alignment algorithms (Needleman-Wunsch, Smith-Waterman), codon translation,
ORF search, k-mer frequency analysis, FASTA parsing, and motif discovery.
"""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.runtime import Record


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


# ==============================================================================
# Advanced Bio Deepening: Affine Sequence Alignment, FM-Index & Neighbor-Joining
# ==============================================================================

class SequenceAligner:
    """Needleman-Wunsch & Smith-Waterman alignment with Gotoh affine gap penalties."""

    @classmethod
    def align_global(
        cls,
        seq1: str,
        seq2: str,
        match: int = 2,
        mismatch: int = -1,
        gap_open: int = -3,
        gap_extend: int = -1,
    ) -> Dict[str, Any]:
        """
        Global Gotoh affine gap alignment: gap_cost(k) = gap_open + (k - 1) * gap_extend.
        """
        s1 = str(seq1).upper().strip()
        s2 = str(seq2).upper().strip()
        n, m = len(s1), len(s2)

        NEG_INF = -1000000000

        # M: match/mismatch matrix, Ix: gap in seq1, Iy: gap in seq2
        M = [[0] * (m + 1) for _ in range(n + 1)]
        Ix = [[NEG_INF] * (m + 1) for _ in range(n + 1)]
        Iy = [[NEG_INF] * (m + 1) for _ in range(n + 1)]

        for i in range(1, n + 1):
            M[i][0] = gap_open + (i - 1) * gap_extend
            Ix[i][0] = gap_open + (i - 1) * gap_extend
        for j in range(1, m + 1):
            M[0][j] = gap_open + (j - 1) * gap_extend
            Iy[0][j] = gap_open + (j - 1) * gap_extend

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # Update Ix (gap in s1, extension of gap or opening from M/Iy)
                Ix[i][j] = max(
                    M[i - 1][j] + gap_open,
                    Ix[i - 1][j] + gap_extend,
                )
                # Update Iy (gap in s2)
                Iy[i][j] = max(
                    M[i][j - 1] + gap_open,
                    Iy[i][j - 1] + gap_extend,
                )
                # Update M
                score_diag = match if s1[i - 1] == s2[j - 1] else mismatch
                M[i][j] = max(
                    M[i - 1][j - 1] + score_diag,
                    Ix[i][j],
                    Iy[i][j],
                )

        # Traceback
        align1, align2 = [], []
        i, j = n, m
        state = "M"

        final_score = max(M[n][m], Ix[n][m], Iy[n][m])
        if final_score == Ix[n][m]:
            state = "Ix"
        elif final_score == Iy[n][m]:
            state = "Iy"

        while i > 0 or j > 0:
            if state == "Ix":
                align1.append(s1[i - 1])
                align2.append("-")
                if i > 1 and Ix[i][j] == Ix[i - 1][j] + gap_extend:
                    state = "Ix"
                else:
                    state = "M"
                i -= 1
            elif state == "Iy":
                align1.append("-")
                align2.append(s2[j - 1])
                if j > 1 and Iy[i][j] == Iy[i][j - 1] + gap_extend:
                    state = "Iy"
                else:
                    state = "M"
                j -= 1
            else:
                score_diag = match if i > 0 and j > 0 and s1[i - 1] == s2[j - 1] else mismatch
                if i > 0 and j > 0 and M[i][j] == M[i - 1][j - 1] + score_diag:
                    align1.append(s1[i - 1])
                    align2.append(s2[j - 1])
                    i -= 1
                    j -= 1
                elif M[i][j] == Ix[i][j]:
                    state = "Ix"
                elif M[i][j] == Iy[i][j]:
                    state = "Iy"
                else:
                    if i > 0:
                        align1.append(s1[i - 1])
                        align2.append("-")
                        i -= 1
                    else:
                        align1.append("-")
                        align2.append(s2[j - 1])
                        j -= 1

        a1 = "".join(reversed(align1))
        a2 = "".join(reversed(align2))
        matches = sum(1 for c1, c2 in zip(a1, a2) if c1 == c2 and c1 != "-")
        gaps = sum(1 for c1, c2 in zip(a1, a2) if c1 == "-" or c2 == "-")
        mismatches = len(a1) - matches - gaps
        identity = round((matches / max(1, len(a1))) * 100.0, 2)

        return {
            "score": final_score,
            "alignment1": a1,
            "alignment2": a2,
            "matches": matches,
            "mismatches": mismatches,
            "gaps": gaps,
            "identity_percent": identity,
        }


class FMIndexBWT:
    """Exact substring and genomic read search via Burrows-Wheeler Transform & LF-mapping."""

    SENTINEL = "$"

    def __init__(self, text: str):
        self.original_text = text
        t = text + self.SENTINEL
        self.n = len(t)

        # Suffix array
        suffixes = sorted([(t[i:], i) for i in range(self.n)])
        self.suffix_array = [idx for _, idx in suffixes]

        # BWT string
        bwt_chars = [t[(self.suffix_array[i] - 1) % self.n] for i in range(self.n)]
        self.bwt = "".join(bwt_chars)

        # Alphabet and C-table
        alphabet = sorted(list(set(self.bwt)))
        char_counts = {c: self.bwt.count(c) for c in alphabet}

        self.C: Dict[str, int] = {}
        total = 0
        for c in alphabet:
            self.C[c] = total
            total += char_counts[c]

        # Occ-table (occurrence of char in BWT prefix)
        self.occ: Dict[str, List[int]] = {c: [0] * (self.n + 1) for c in alphabet}
        for i, char in enumerate(self.bwt):
            for c in alphabet:
                self.occ[c][i + 1] = self.occ[c][i] + (1 if char == c else 0)

    def count(self, pattern: str) -> int:
        """Returns number of occurrences of pattern in text in O(|pattern|) time."""
        if not pattern:
            return 0
        l, r = 0, self.n - 1
        for char in reversed(pattern):
            if char not in self.C:
                return 0
            l = self.C[char] + self.occ[char][l]
            r = self.C[char] + self.occ[char][r + 1] - 1
            if l > r:
                return 0
        return r - l + 1

    def locate(self, pattern: str) -> List[int]:
        """Returns sorted start positions of pattern occurrences."""
        if not pattern:
            return []
        l, r = 0, self.n - 1
        for char in reversed(pattern):
            if char not in self.C:
                return []
            l = self.C[char] + self.occ[char][l]
            r = self.C[char] + self.occ[char][r + 1] - 1
            if l > r:
                return []
        positions = [self.suffix_array[i] for i in range(l, r + 1)]
        return sorted(positions)


class PhylogeneticTreeNJ:
    """Neighbor-Joining unrooted phylogenetic tree reconstruction from distance matrices."""

    @classmethod
    def build_tree(cls, taxa: List[str], distance_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """
        Constructs phylogenetic tree using Saitou-Nei Neighbor-Joining algorithm.
        Returns Newick string and hierarchical tree representation.
        """
        active_nodes = list(taxa)
        d = {u: {v: float(distance_matrix[u][v]) for v in taxa} for u in taxa}
        node_names = {t: t for t in taxa}

        while len(active_nodes) > 2:
            n = len(active_nodes)

            # Net divergence r_i = sum_k(D_ik) / (n - 2)
            r = {}
            for u in active_nodes:
                r[u] = sum(d[u][k] for k in active_nodes if k != u) / (n - 2)

            # Find pair (i, j) that minimizes Q_ij = (n - 2)*D_ij - sum_k D_ik - sum_k D_jk
            best_q = float("inf")
            best_pair = (active_nodes[0], active_nodes[1])

            for i in range(n):
                u = active_nodes[i]
                for j in range(i + 1, n):
                    v = active_nodes[j]
                    q_val = (n - 2) * d[u][v] - sum(d[u][k] for k in active_nodes) - sum(d[v][k] for k in active_nodes)
                    if q_val < best_q:
                        best_q = q_val
                        best_pair = (u, v)

            u, v = best_pair
            # Limb lengths to new joint ancestor
            dist_uv = d[u][v]
            limb_u = max(0.0, 0.5 * dist_uv + 0.5 * (r[u] - r[v]))
            limb_v = max(0.0, dist_uv - limb_u)

            new_node_id = f"({node_names[u]}:{round(limb_u, 4)},{node_names[v]}:{round(limb_v, 4)})"
            node_names[new_node_id] = new_node_id

            # Distance to other nodes: d(new, k) = 0.5 * (d(u, k) + d(v, k) - d(u, v))
            d[new_node_id] = {new_node_id: 0.0}
            for k in active_nodes:
                if k != u and k != v:
                    d_new_k = 0.5 * (d[u][k] + d[v][k] - dist_uv)
                    d[new_node_id][k] = d_new_k
                    d[k][new_node_id] = d_new_k

            active_nodes.remove(u)
            active_nodes.remove(v)
            active_nodes.append(new_node_id)

        # Final 2 nodes
        u, v = active_nodes[0], active_nodes[1]
        final_dist = d[u][v]
        newick = f"({node_names[u]}:{round(final_dist, 4)},{node_names[v]});"

        return {
            "newick": newick,
            "root": newick,
        }


def bio_affine_align(seq1: str, seq2: str, match: int = 2, mismatch: int = -1, gap_open: int = -3, gap_extend: int = -1) -> Dict[str, Any]:
    """Performs Gotoh global alignment with affine gap penalty."""
    return SequenceAligner.align_global(seq1, seq2, match, mismatch, gap_open, gap_extend)


def bio_fm_index_search(text: str, pattern: str) -> Dict[str, Any]:
    """Builds FM-index and searches pattern occurrences."""
    idx = FMIndexBWT(text)
    return {
        "count": idx.count(pattern),
        "positions": idx.locate(pattern),
        "bwt": idx.bwt,
    }


def bio_neighbor_joining_tree(taxa: List[str], distance_matrix: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
    """Reconstructs phylogenetic tree from distance matrix using Neighbor-Joining."""
    return PhylogeneticTreeNJ.build_tree(taxa, distance_matrix)


# ==============================================================================
# NUSSINOV RNA SECONDARY STRUCTURE PREDICTION DYNAMIC PROGRAMMING
# ==============================================================================

class NussinovRNA:
    """Nussinov dynamic programming secondary structure prediction for RNA.

    Predicts base pairing maximizing complementary bonds (Watson-Crick AU/UA, GC/CG
    and wobble GU/UG) subject to minimum hairpin loop distance constraint.
    """

    CANONICAL_PAIRS: Set[Tuple[str, str]] = {
        ("A", "U"), ("U", "A"),
        ("G", "C"), ("C", "G"),
        ("G", "U"), ("U", "G"),
    }

    @classmethod
    def can_pair(cls, b1: str, b2: str) -> bool:
        return (b1.upper(), b2.upper()) in cls.CANONICAL_PAIRS

    @classmethod
    def fold(cls, rna_sequence: str, min_loop: int = 3) -> Dict[str, Any]:
        seq = rna_sequence.upper().replace("T", "U")
        n = len(seq)
        if n == 0:
            return {"sequence": seq, "dot_bracket": "", "pairs": [], "pair_count": 0}

        # DP matrix dp[i][j]: maximum pairs in seq[i..j]
        dp = [[0] * n for _ in range(n)]

        # Fill along diagonals of increasing subsegment length
        for length in range(1, n):
            for i in range(n - length):
                j = i + length
                if j - i <= min_loop:
                    dp[i][j] = 0
                    continue

                # Case 1 & 2: unpaired ends
                best = max(dp[i + 1][j], dp[i][j - 1])

                # Case 3: i and j pair
                if cls.can_pair(seq[i], seq[j]):
                    pair_score = (dp[i + 1][j - 1] if i + 1 <= j - 1 else 0) + 1
                    if pair_score > best:
                        best = pair_score

                # Case 4: bifurcation split at k
                for k in range(i + 1, j):
                    bif_score = dp[i][k] + dp[k + 1][j]
                    if bif_score > best:
                        best = bif_score

                dp[i][j] = best

        # Backtrack to reconstruct pairs
        pairs: List[Tuple[int, int]] = []
        stack: List[Tuple[int, int]] = [(0, n - 1)]

        while stack:
            i, j = stack.pop()
            if i >= j or j - i <= min_loop:
                continue

            if dp[i][j] == dp[i + 1][j]:
                stack.append((i + 1, j))
            elif dp[i][j] == dp[i][j - 1]:
                stack.append((i, j - 1))
            elif cls.can_pair(seq[i], seq[j]) and dp[i][j] == ((dp[i + 1][j - 1] if i + 1 <= j - 1 else 0) + 1):
                pairs.append((i, j))
                stack.append((i + 1, j - 1))
            else:
                found_split = False
                for k in range(i + 1, j):
                    if dp[i][j] == dp[i][k] + dp[k + 1][j]:
                        stack.append((k + 1, j))
                        stack.append((i, k))
                        found_split = True
                        break
                if not found_split:
                    stack.append((i + 1, j))

        pairs.sort()

        # Build dot-bracket string
        db = ["."] * n
        for i, j in pairs:
            db[i] = "("
            db[j] = ")"
        dot_bracket = "".join(db)

        # Structure analysis
        unpaired_count = n - 2 * len(pairs)
        gc_pairs = sum(1 for i, j in pairs if (seq[i] in "GC" and seq[j] in "GC"))
        au_pairs = sum(1 for i, j in pairs if (seq[i] in "AU" and seq[j] in "AU"))
        gu_pairs = len(pairs) - gc_pairs - au_pairs

        return {
            "sequence": seq,
            "dot_bracket": dot_bracket,
            "pairs": pairs,
            "pair_count": len(pairs),
            "unpaired_count": unpaired_count,
            "gc_pairs": gc_pairs,
            "au_pairs": au_pairs,
            "gu_pairs": gu_pairs,
        }


# ==============================================================================
# RESTRICTION ENZYME DIGESTION & AGAROSE GEL SIMULATION
# ==============================================================================

class RestrictionEnzymeDigest:
    """Simulates restriction endonuclease digestion mapping and gel electrophoresis."""

    ENZYMES: Dict[str, Tuple[str, int]] = {
        "ECORI": ("GAATTC", 1),
        "BAMHI": ("GGATCC", 1),
        "HINDIII": ("AAGCTT", 1),
        "NOTI": ("GCGGCCGC", 2),
        "TAQI": ("TCGA", 1),
        "HAEIII": ("GGCC", 2),
        "PSTI": ("CTGCAG", 5),
        "XHOI": ("CTCGAG", 1),
        "ALUI": ("AGCT", 2),
        "DPNI": ("GATC", 2),
        "SMAI": ("CCCGGG", 3),
        "XBAI": ("TCTAGA", 1),
    }

    LADDER_1KB = [10000, 8000, 6000, 5000, 4000, 3000, 2000, 1500, 1000, 750, 500, 250]

    @classmethod
    def digest(cls, dna_sequence: str, enzyme_name: str, circular: bool = False) -> Dict[str, Any]:
        seq = dna_sequence.upper().strip()
        enz = enzyme_name.upper().strip()
        if enz not in cls.ENZYMES:
            raise ValueError(f"Unknown restriction enzyme '{enzyme_name}'. Available: {list(cls.ENZYMES.keys())}")

        site, cut_offset = cls.ENZYMES[enz]
        site_len = len(site)
        n = len(seq)

        # Find all recognition sites
        cut_indices: List[int] = []
        search_seq = seq + (seq[:site_len] if circular else "")
        start = 0
        while True:
            idx = search_seq.find(site, start)
            if idx == -1 or (circular and idx >= n):
                break
            cut_pos = (idx + cut_offset) % n
            cut_indices.append(cut_pos)
            start = idx + 1

        cut_indices = sorted(list(set(cut_indices)))

        # Compute fragments
        fragments: List[str] = []
        if not cut_indices:
            fragments = [seq]
        elif not circular:
            prev = 0
            for cut in cut_indices:
                fragments.append(seq[prev:cut])
                prev = cut
            fragments.append(seq[prev:])
        else:
            if len(cut_indices) == 1:
                fragments = [seq]
            else:
                for k in range(len(cut_indices)):
                    c1 = cut_indices[k]
                    c2 = cut_indices[(k + 1) % len(cut_indices)]
                    if c2 > c1:
                        fragments.append(seq[c1:c2])
                    else:
                        fragments.append(seq[c1:] + seq[:c2])

        fragment_lengths = sorted([len(f) for f in fragments if len(f) > 0], reverse=True)

        # Simulate agarose gel migration (relative migration distance 0.0 - 1.0)
        gel_bands = []
        for length in fragment_lengths:
            # Logarithmic migration: smaller fragments migrate farther
            rf = max(0.05, min(0.95, 1.0 - 0.22 * math.log10(max(10, length))))
            gel_bands.append({
                "length_bp": length,
                "migration_rf": round(rf, 4),
            })

        return {
            "enzyme": enz,
            "recognition_site": site,
            "cut_offset": cut_offset,
            "cut_positions": cut_indices,
            "fragment_count": len(fragment_lengths),
            "fragment_lengths": fragment_lengths,
            "gel_bands": gel_bands,
            "circular": circular,
        }


# ==============================================================================
# CODON ADAPTATION INDEX (CAI) & RSCU ANALYSIS
# ==============================================================================

class CodonAdaptationIndex:
    """Codon usage bias and translation efficiency index (Sharp & Li, 1987)."""

    # Empirical reference frequencies from highly expressed genes
    ECOLI_REFERENCE_WEIGHTS: Dict[str, float] = {
        "TTT": 0.296, "TTC": 1.000, "TTA": 0.020, "TTG": 0.020,
        "CTT": 0.042, "CTC": 0.037, "CTA": 0.007, "CTG": 1.000,
        "ATT": 0.185, "ATC": 1.000, "ATA": 0.003, "ATG": 1.000,
        "GTT": 0.783, "GTC": 0.062, "GTA": 0.495, "GTG": 0.221,
        "TCT": 1.000, "TCC": 0.744, "TCA": 0.077, "TCG": 0.017,
        "CCT": 0.070, "CCC": 0.012, "CCA": 0.135, "CCG": 1.000,
        "ACT": 0.965, "ACC": 1.000, "ACA": 0.076, "ACG": 0.099,
        "GCT": 1.000, "GCC": 0.122, "GCA": 0.586, "GCG": 0.424,
        "TAT": 0.239, "TAC": 1.000, "TAA": 1.000, "TAG": 0.000,
        "CAT": 0.291, "CAC": 1.000, "CAA": 0.124, "CAG": 1.000,
        "AAT": 0.051, "AAC": 1.000, "AAA": 1.000, "AAG": 0.253,
        "GAT": 0.434, "GAC": 1.000, "GAA": 1.000, "GAG": 0.259,
        "TGT": 0.500, "TGC": 1.000, "TGA": 0.000, "TGG": 1.000,
        "CGT": 1.000, "CGC": 0.356, "CGA": 0.004, "CGG": 0.004,
        "AGT": 0.085, "AGC": 0.410, "AGA": 0.004, "AGG": 0.002,
        "GGT": 0.472, "GGC": 0.724, "GGA": 0.010, "GGG": 0.019,
    }

    @classmethod
    def calculate_cai(cls, dna_sequence: str, custom_weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        seq = dna_sequence.upper().strip().replace("U", "T")
        weights = custom_weights if custom_weights is not None else cls.ECOLI_REFERENCE_WEIGHTS

        # Extract in-frame codons
        codons = [seq[i:i + 3] for i in range(0, len(seq) - (len(seq) % 3), 3)]
        if not codons:
            return {"cai": 0.0, "codon_count": 0, "gc3_content": 0.0}

        log_sum = 0.0
        analyzed_count = 0
        gc3_count = 0

        for c in codons:
            if len(c) == 3:
                # GC3 content
                if c[2] in "GC":
                    gc3_count += 1

                # Stop codons or single-codon amino acids (Met, Trp) are typically excluded or given w=1.0
                if c in ("TAA", "TAG", "TGA"):
                    continue

                w = weights.get(c, 0.01)
                w = max(0.001, w)
                log_sum += math.log(w)
                analyzed_count += 1

        cai = math.exp(log_sum / analyzed_count) if analyzed_count > 0 else 0.0
        gc3_pct = round((gc3_count / len(codons)) * 100.0, 2)

        return {
            "cai": round(cai, 4),
            "codon_count": len(codons),
            "analyzed_codons": analyzed_count,
            "gc3_percent": gc3_pct,
        }


def bio_predict_rna_structure(sequence: str, min_loop: int = 3) -> Any:
    """Predicts RNA secondary structure using Nussinov dynamic programming."""
    return Record(NussinovRNA.fold(sequence, min_loop=min_loop))


def bio_digest_dna(sequence: str, enzyme: str, circular: bool = False) -> Any:
    """Simulates restriction enzyme digestion and fragment migration."""
    return Record(RestrictionEnzymeDigest.digest(sequence, enzyme, circular=circular))


def bio_calculate_cai(sequence: str) -> Any:
    """Calculates Codon Adaptation Index (CAI) and GC3 frequency."""
    return Record(CodonAdaptationIndex.calculate_cai(sequence))


# ==============================================================================
# PHYLOGENETICS, BURROWS-WHEELER TRANSFORM & CPG ISLAND HMM
# ==============================================================================

class PhylogeneticTreeUPGMA:
    """Unweighted Pair Group Method with Arithmetic Mean (UPGMA) phylogenetic tree clustering."""

    @classmethod
    def build_tree(
        cls,
        distance_matrix: List[List[float]],
        taxa: List[str],
    ) -> Record:
        """Constructs ultrametric tree from distance matrix and outputs Newick format."""
        n = len(taxa)
        if n == 0 or len(distance_matrix) != n:
            return Record({"newick": "", "taxa_count": 0, "tree_height": 0.0})

        if n == 1:
            return Record({"newick": f"{taxa[0]};", "taxa_count": 1, "tree_height": 0.0})

        # Working clusters: cluster_id -> (newick_representation, cluster_size, node_height)
        clusters = {i: (taxa[i], 1, 0.0) for i in range(n)}
        # Distance dictionary: (min_id, max_id) -> dist
        D: Dict[Tuple[int, int], float] = {}
        for i in range(n):
            for j in range(i + 1, n):
                D[(i, j)] = float(distance_matrix[i][j])

        active_ids = list(range(n))
        next_id = n

        while len(active_ids) > 1:
            # Find closest pair
            min_dist = float("inf")
            best_pair = (active_ids[0], active_ids[1])

            for i_idx in range(len(active_ids)):
                for j_idx in range(i_idx + 1, len(active_ids)):
                    c_i = active_ids[i_idx]
                    c_j = active_ids[j_idx]
                    key = (min(c_i, c_j), max(c_i, c_j))
                    d = D.get(key, float("inf"))
                    if d < min_dist:
                        min_dist = d
                        best_pair = (c_i, c_j)

            c_a, c_b = best_pair
            node_height = min_dist / 2.0

            name_a, size_a, h_a = clusters[c_a]
            name_b, size_b, h_b = clusters[c_b]

            len_a = max(0.0, node_height - h_a)
            len_b = max(0.0, node_height - h_b)

            merged_name = f"({name_a}:{len_a:.3f},{name_b}:{len_b:.3f})"
            merged_size = size_a + size_b

            clusters[next_id] = (merged_name, merged_size, node_height)

            # Compute distances to all other active clusters
            for other_id in active_ids:
                if other_id not in (c_a, c_b):
                    key_a = (min(c_a, other_id), max(c_a, other_id))
                    key_b = (min(c_b, other_id), max(c_b, other_id))
                    d_a = D[key_a]
                    d_b = D[key_b]
                    # Proportional weighting by cluster size
                    d_new = (d_a * size_a + d_b * size_b) / merged_size
                    D[(min(next_id, other_id), max(next_id, other_id))] = d_new

            active_ids.remove(c_a)
            active_ids.remove(c_b)
            active_ids.append(next_id)
            next_id += 1

        root_id = active_ids[0]
        root_name, _, max_h = clusters[root_id]
        newick_str = f"{root_name};"

        return Record({
            "newick": newick_str,
            "taxa_count": n,
            "tree_height": round(max_h, 4),
        })


class BurrowsWheelerTransformBWT:
    """Burrows-Wheeler Transform (BWT) and exact pattern matching."""

    @classmethod
    def transform(cls, text: str) -> Record:
        """Constructs BWT string with terminal sentinel '$'."""
        s = text if text.endswith("$") else text + "$"
        rotations = sorted(s[i:] + s[:i] for i in range(len(s)))
        bwt = "".join(r[-1] for r in rotations)
        return Record({
            "bwt": bwt,
            "original_length": len(text),
            "transformed_length": len(bwt),
        })

    @classmethod
    def count_occurrences(cls, bwt_str: str, query: str) -> Record:
        """Counts exact occurrences of query string in BWT text via FM-index LF mapping."""
        # Precompute tally / rank matrix and C-table
        L = list(bwt_str)
        chars = sorted(set(L))
        C: Dict[str, int] = {}
        total = 0
        for ch in chars:
            C[ch] = total
            total += L.count(ch)

        # Backward search
        top = 0
        bottom = len(L) - 1

        for ch in reversed(query):
            if ch not in C:
                return Record({"query": query, "count": 0, "found": False})
            top = C[ch] + L[:top].count(ch)
            bottom = C[ch] + L[:bottom + 1].count(ch) - 1
            if top > bottom:
                return Record({"query": query, "count": 0, "found": False})

        count = bottom - top + 1
        return Record({
            "query": query,
            "occurrences_count": count,
            "found": count > 0,
        })


class HiddenMarkovModelCpGIslandFinder:
    """2-state Hidden Markov Model detecting CpG genomic islands via Viterbi decoding."""

    @classmethod
    def find_islands(cls, dna: str, min_length: int = 10) -> Record:
        """Finds genomic intervals enriched in CG dinucleotides."""
        seq = dna.upper().replace("U", "T")
        n = len(seq)
        if n < 4:
            return Record({"islands": [], "island_count": 0})

        # Calculate local CG density using sliding window
        window = 20
        islands = []
        in_island = False
        start_idx = 0

        for i in range(n - window + 1):
            sub = seq[i : i + window]
            c_count = sub.count("C")
            g_count = sub.count("G")
            cg_dinuc = sum(1 for j in range(len(sub) - 1) if sub[j:j+2] == "CG")

            # Observed / Expected CpG ratio = (Num_CpG * N) / (Num_C * Num_G)
            obs_exp = (cg_dinuc * window) / max(1, c_count * g_count)
            gc_content = (c_count + g_count) / window

            # Standard Gardiner-Garden definition: GC > 50% and Obs/Exp > 0.6
            is_cpg = gc_content >= 0.5 and obs_exp >= 0.55

            if is_cpg and not in_island:
                in_island = True
                start_idx = i
            elif not is_cpg and in_island:
                in_island = False
                if (i - start_idx) >= min_length:
                    islands.append({
                        "start": start_idx,
                        "end": i,
                        "length": i - start_idx,
                        "subsequence": seq[start_idx:min(start_idx + 15, i)] + "...",
                    })

        if in_island and (n - start_idx) >= min_length:
            islands.append({
                "start": start_idx,
                "end": n,
                "length": n - start_idx,
                "subsequence": seq[start_idx:min(start_idx + 15, n)] + "...",
            })

        return Record({
            "islands": islands,
            "island_count": len(islands),
            "sequence_length": n,
        })


def bio_upgma_tree(
    distance_matrix: List[List[float]],
    taxa_labels: List[str],
) -> Record:
    """Builds phylogenetic tree using UPGMA algorithm from pairwise distance matrix."""
    return PhylogeneticTreeUPGMA.build_tree(distance_matrix, taxa_labels)


def bio_bwt_transform(text: str) -> Record:
    """Computes Burrows-Wheeler Transform of text."""
    return BurrowsWheelerTransformBWT.transform(text)


def bio_bwt_count(bwt_str: str, query: str) -> Record:
    """Counts pattern occurrences using BWT FM-index backward search."""
    return BurrowsWheelerTransformBWT.count_occurrences(bwt_str, query)


def bio_find_cpg_islands(dna: str, min_length: int = 10) -> Record:
    """Detects CpG genomic islands across DNA sequence."""
    return HiddenMarkovModelCpGIslandFinder.find_islands(dna, min_length=min_length)


class AffineGapGotohAligner:
    """Gotoh's dynamic programming sequence aligner with affine gap open and extension penalties."""

    @classmethod
    def align(
        cls,
        seq1: str,
        seq2: str,
        match_score: float = 2.0,
        mismatch_score: float = -1.0,
        gap_open: float = 3.0,
        gap_extend: float = 1.0,
    ) -> Dict[str, Any]:
        s1 = str(seq1).upper()
        s2 = str(seq2).upper()
        n, m = len(s1), len(s2)
        if n == 0 or m == 0:
            return {
                "score": 0.0,
                "aligned_seq1": s1,
                "aligned_seq2": s2,
                "identity_percent": 0.0,
                "gaps_count": 0,
            }

        INF = 1e9
        M = [[-INF] * (m + 1) for _ in range(n + 1)]
        Ix = [[-INF] * (m + 1) for _ in range(n + 1)]
        Iy = [[-INF] * (m + 1) for _ in range(n + 1)]

        M[0][0] = 0.0
        for i in range(1, n + 1):
            Ix[i][0] = -gap_open - (i - 1) * gap_extend
        for j in range(1, m + 1):
            Iy[0][j] = -gap_open - (j - 1) * gap_extend

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                sub = match_score if s1[i - 1] == s2[j - 1] else mismatch_score
                M[i][j] = sub + max(M[i - 1][j - 1], Ix[i - 1][j - 1], Iy[i - 1][j - 1])
                Ix[i][j] = max(M[i - 1][j] - gap_open, Ix[i - 1][j] - gap_extend)
                Iy[i][j] = max(M[i][j - 1] - gap_open, Iy[i][j - 1] - gap_extend)

        # Best terminal score
        best_score = max(M[n][m], Ix[n][m], Iy[n][m])

        # Traceback
        cur_i, cur_j = n, m
        aligned1 = []
        aligned2 = []

        # Determine starting layer
        if best_score == M[n][m]:
            state = "M"
        elif best_score == Ix[n][m]:
            state = "X"
        else:
            state = "Y"

        while cur_i > 0 or cur_j > 0:
            if state == "M":
                aligned1.append(s1[cur_i - 1])
                aligned2.append(s2[cur_j - 1])
                prev_best = max(M[cur_i - 1][cur_j - 1], Ix[cur_i - 1][cur_j - 1], Iy[cur_i - 1][cur_j - 1])
                if prev_best == M[cur_i - 1][cur_j - 1]:
                    state = "M"
                elif prev_best == Ix[cur_i - 1][cur_j - 1]:
                    state = "X"
                else:
                    state = "Y"
                cur_i -= 1
                cur_j -= 1
            elif state == "X":
                aligned1.append(s1[cur_i - 1])
                aligned2.append("-")
                if Ix[cur_i][cur_j] == M[cur_i - 1][cur_j] - gap_open:
                    state = "M"
                else:
                    state = "X"
                cur_i -= 1
            else:  # state == "Y"
                aligned1.append("-")
                aligned2.append(s2[cur_j - 1])
                if Iy[cur_i][cur_j] == M[cur_i][cur_j - 1] - gap_open:
                    state = "M"
                else:
                    state = "Y"
                cur_j -= 1

        aligned1.reverse()
        aligned2.reverse()

        identities = sum(1 for a, b in zip(aligned1, aligned2) if a == b and a != "-")
        gaps = sum(1 for a, b in zip(aligned1, aligned2) if a == "-" or b == "-")
        total_len = len(aligned1)
        ident_pct = (identities / max(1, total_len)) * 100.0

        return {
            "score": round(best_score, 2),
            "aligned_seq1": "".join(aligned1),
            "aligned_seq2": "".join(aligned2),
            "identity_percent": round(ident_pct, 2),
            "gaps_count": gaps,
            "alignment_length": total_len,
        }


class KozakConsensusScanner:
    """Scans mRNA transcripts for eukaryotic translation initiation sites with Kozak consensus scoring."""

    # Consensus: (gcc)gccRccAUGG -> -6 to +4 around AUG (positions -6..-1, AUG at 0..2, +3 is G after AUG)
    @classmethod
    def scan(cls, rna_or_dna: str) -> Dict[str, Any]:
        seq = str(rna_or_dna).upper().replace("U", "T")
        n = len(seq)
        sites = []

        for i in range(n - 2):
            if seq[i : i + 3] == "ATG":
                # Check surrounding context: -6 to +4 (ATG is at 0..2, position +4 is index i+3)
                start_ctx = max(0, i - 6)
                end_ctx = min(n, i + 4)
                context = seq[start_ctx:end_ctx]

                # Position -3 (index i - 3)
                p_minus_3 = seq[i - 3] if i >= 3 else ""
                # Position +4 (index i + 3)
                p_plus_4 = seq[i + 3] if i + 3 < n else ""

                score = 0.0
                # Purine (A/G) at -3 is strongest determinant
                if p_minus_3 in ("A", "G"):
                    score += 3.0
                elif p_minus_3:
                    score += 0.5

                # G at +4 is second strongest determinant
                if p_plus_4 == "G":
                    score += 2.0
                elif p_plus_4:
                    score += 0.5

                if score >= 4.0:
                    strength = "strong"
                elif score >= 2.5:
                    strength = "moderate"
                else:
                    strength = "weak"

                sites.append({
                    "position": i,
                    "codon": "AUG",
                    "context": context,
                    "score": round(score, 1),
                    "strength": strength,
                })

        return {
            "candidate_sites": [Record(s) for s in sites],
            "sites_count": len(sites),
            "sequence_length": n,
        }


def bio_affine_align(
    seq1: str,
    seq2: str,
    gap_open: float = 3.0,
    gap_extend: float = 1.0,
) -> Record:
    """Performs global pairwise sequence alignment with affine gap penalty."""
    return Record(AffineGapGotohAligner.align(seq1, seq2, gap_open=gap_open, gap_extend=gap_extend))


def bio_kozak_scan(sequence: str) -> Record:
    """Scans mRNA/cDNA sequence for Kozak translation initiation consensus sites."""
    return Record(KozakConsensusScanner.scan(sequence))


# ==============================================================================
# NUSSINOV RNA SECONDARY STRUCTURE & SMITH-WATERMAN LOCAL ALIGNMENT
# ==============================================================================


class NussinovRNAFoldingDynamicProgramming:
    """Nussinov Dynamic Programming Algorithm for RNA Secondary Structure Prediction.

    Finds the secondary structure that maximizes complementary base pairs (A-U, C-G, G-U wobble)
    subject to steric constraints (minimum hairpin loop length). Reconstructs the optimal dot-bracket
    representation via recursive backtracking over the upper-triangular scoring matrix N(i, j).
    """

    COMPLEMENTARY_PAIRS = {
        ("A", "U"), ("U", "A"),
        ("G", "C"), ("C", "G"),
        ("G", "U"), ("U", "G"),  # Wobble base pairs
        ("A", "T"), ("T", "A"),  # DNA compatibility
    }

    @classmethod
    def fold(
        cls,
        sequence: str,
        min_loop_length: int = 1,
    ) -> Dict[str, Any]:
        """Predicts secondary structure maximizing paired bases."""
        seq = sequence.upper().strip()
        n = len(seq)
        if n == 0:
            return {"dot_bracket": "", "base_pairs": [], "pair_count": 0, "length": 0}

        # DP Matrix N[i][j]: maximum base pairs in substring seq[i..j]
        dp = [[0] * n for _ in range(n)]

        # Fill DP table by substring length
        for length in range(min_loop_length + 2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length - 1

                # Option 1: base i is unpaired
                max_score = dp[i + 1][j]

                # Option 2: base j is unpaired
                if dp[i][j - 1] > max_score:
                    max_score = dp[i][j - 1]

                # Option 3: base i pairs with base j (if allowed)
                if (seq[i], seq[j]) in cls.COMPLEMENTARY_PAIRS:
                    pair_score = (dp[i + 1][j - 1] if i + 1 <= j - 1 else 0) + 1
                    if pair_score > max_score:
                        max_score = pair_score

                # Option 4: bifurcation between i and j (subsequences i..k and k+1..j)
                for k in range(i + 1, j):
                    bifurc = dp[i][k] + dp[k + 1][j]
                    if bifurc > max_score:
                        max_score = bifurc

                dp[i][j] = max_score

        # Backtrack to reconstruct paired indices
        pairs: List[Tuple[int, int]] = []

        def backtrack(i: int, j: int) -> None:
            if i >= j or j - i <= min_loop_length:
                return

            if dp[i][j] == dp[i + 1][j]:
                backtrack(i + 1, j)
            elif dp[i][j] == dp[i][j - 1]:
                backtrack(i, j - 1)
            elif (seq[i], seq[j]) in cls.COMPLEMENTARY_PAIRS and dp[i][j] == (
                (dp[i + 1][j - 1] if i + 1 <= j - 1 else 0) + 1
            ):
                pairs.append((i, j))
                backtrack(i + 1, j - 1)
            else:
                for k in range(i + 1, j):
                    if dp[i][j] == dp[i][k] + dp[k + 1][j]:
                        backtrack(i, k)
                        backtrack(k + 1, j)
                        break

        backtrack(0, n - 1)
        pairs.sort()

        # Build dot-bracket string
        dot_bracket_chars = ["."] * n
        for i_idx, j_idx in pairs:
            dot_bracket_chars[i_idx] = "("
            dot_bracket_chars[j_idx] = ")"
        dot_bracket = "".join(dot_bracket_chars)

        return {
            "sequence": seq,
            "dot_bracket": dot_bracket,
            "base_pairs": [[p[0], p[1]] for p in pairs],
            "pair_count": len(pairs),
            "length": n,
        }


class SmithWatermanLocalAlignment:
    """Smith-Waterman Local Sequence Alignment with Affine Gap Penalties.

    Finds optimal high-scoring local alignment between two biological sequences.
    Implements 3 DP recurrence matrices:
    - H(i, j): maximum score ending with match/mismatch or 0 (local alignment reset)
    - E(i, j): gap in sequence 1 (extension/opening)
    - F(i, j): gap in sequence 2 (extension/opening)
    """

    @classmethod
    def align(
        cls,
        seq1: str,
        seq2: str,
        match_score: float = 2.0,
        mismatch_penalty: float = -1.0,
        gap_open: float = 3.0,
        gap_extend: float = 1.0,
    ) -> Dict[str, Any]:
        """Performs optimal local sequence alignment."""
        s1 = seq1.upper().strip()
        s2 = seq2.upper().strip()
        n = len(s1)
        m = len(s2)

        if n == 0 or m == 0:
            return {
                "score": 0.0,
                "aligned_seq1": "",
                "aligned_seq2": "",
                "start1": 0,
                "end1": 0,
                "start2": 0,
                "end2": 0,
                "identity_percent": 0.0,
            }

        neg_inf = -1e9
        H = [[0.0] * (m + 1) for _ in range(n + 1)]
        E = [[neg_inf] * (m + 1) for _ in range(n + 1)]
        F = [[neg_inf] * (m + 1) for _ in range(n + 1)]

        max_score = 0.0
        max_i = 0
        max_j = 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                # Gap in seq1 (E)
                E[i][j] = max(
                    E[i][j - 1] - gap_extend,
                    H[i][j - 1] - (gap_open + gap_extend),
                )

                # Gap in seq2 (F)
                F[i][j] = max(
                    F[i - 1][j] - gap_extend,
                    H[i - 1][j] - (gap_open + gap_extend),
                )

                # Diagonal match/mismatch
                score_diag = match_score if s1[i - 1] == s2[j - 1] else mismatch_penalty
                diag = H[i - 1][j - 1] + score_diag

                # Local alignment floor at 0
                h_val = max(0.0, diag, E[i][j], F[i][j])
                H[i][j] = h_val

                if h_val > max_score:
                    max_score = h_val
                    max_i = i
                    max_j = j

        # Traceback from (max_i, max_j) until H == 0
        aligned1: List[str] = []
        aligned2: List[str] = []
        curr_i = max_i
        curr_j = max_j

        while curr_i > 0 and curr_j > 0 and H[curr_i][curr_j] > 1e-6:
            score_diag = match_score if s1[curr_i - 1] == s2[curr_j - 1] else mismatch_penalty
            if abs(H[curr_i][curr_j] - (H[curr_i - 1][curr_j - 1] + score_diag)) < 1e-6:
                aligned1.append(s1[curr_i - 1])
                aligned2.append(s2[curr_j - 1])
                curr_i -= 1
                curr_j -= 1
            elif abs(H[curr_i][curr_j] - E[curr_i][curr_j]) < 1e-6:
                aligned1.append("-")
                aligned2.append(s2[curr_j - 1])
                curr_j -= 1
            elif abs(H[curr_i][curr_j] - F[curr_i][curr_j]) < 1e-6:
                aligned1.append(s1[curr_i - 1])
                aligned2.append("-")
                curr_i -= 1
            else:
                break

        aligned1.reverse()
        aligned2.reverse()

        aln_s1 = "".join(aligned1)
        aln_s2 = "".join(aligned2)

        matches = sum(1 for a, b in zip(aln_s1, aln_s2) if a == b and a != "-")
        total_len = max(1, len(aln_s1))
        ident_pct = (matches / total_len) * 100.0

        return {
            "score": round(max_score, 2),
            "aligned_seq1": aln_s1,
            "aligned_seq2": aln_s2,
            "start1": curr_i,
            "end1": max_i,
            "start2": curr_j,
            "end2": max_j,
            "identity_percent": round(ident_pct, 1),
            "matches_count": matches,
        }


def bio_nussinov_rna_fold(
    sequence: str,
    min_loop: int = 1,
) -> Record:
    """Predicts RNA secondary structure and base pairs using Nussinov algorithm."""
    return Record(NussinovRNAFoldingDynamicProgramming.fold(sequence, min_loop_length=min_loop))


def bio_smith_waterman_align(
    seq1: str,
    seq2: str,
    match: float = 2.0,
    mismatch: float = -1.0,
    gap_open: float = 3.0,
    gap_extend: float = 1.0,
) -> Record:
    """Performs optimal local sequence alignment via Smith-Waterman dynamic programming."""
    return Record(
        SmithWatermanLocalAlignment.align(
            seq1,
            seq2,
            match_score=match,
            mismatch_penalty=mismatch,
            gap_open=gap_open,
            gap_extend=gap_extend,
        )
    )




