"""Genomics Domain Runtime: Sequence alignment (Smith-Waterman, Needleman-Wunsch), GC content, and CpG detection."""
from typing import Dict, Any, List, Tuple

def genomics_gc_content(sequence: str) -> float:
    """Calculates GC percentage in a DNA/RNA nucleotide sequence."""
    seq = str(sequence).upper().strip()
    if not seq:
        return 0.0
    gc_count = seq.count("G") + seq.count("C")
    return round((gc_count / len(seq)) * 100.0, 2)

def genomics_smith_waterman(s1: str, s2: str, match: int = 2, mismatch: int = -1, gap: int = -1) -> Dict[str, Any]:
    """Performs Smith-Waterman local sequence alignment algorithm."""
    s1 = str(s1).upper().strip()
    s2 = str(s2).upper().strip()
    m, n = len(s1), len(s2)
    h = [[0] * (n + 1) for _ in range(m + 1)]
    max_score = 0
    max_pos = (0, 0)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            score_diag = h[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch)
            score_up = h[i-1][j] + gap
            score_left = h[i][j-1] + gap
            val = max(0, score_diag, score_up, score_left)
            h[i][j] = val
            if val > max_score:
                max_score = val
                max_pos = (i, j)

    # Traceback
    align1, align2 = [], []
    i, j = max_pos
    while i > 0 and j > 0 and h[i][j] > 0:
        val = h[i][j]
        diag = h[i-1][j-1] + (match if s1[i-1] == s2[j-1] else mismatch)
        if val == diag:
            align1.append(s1[i-1])
            align2.append(s2[j-1])
            i -= 1
            j -= 1
        elif val == h[i-1][j] + gap:
            align1.append(s1[i-1])
            align2.append("-")
            i -= 1
        else:
            align1.append("-")
            align2.append(s2[j-1])
            j -= 1

    return {
        "score": max_score,
        "alignment1": "".join(reversed(align1)),
        "alignment2": "".join(reversed(align2))
    }

def genomics_find_cpg_islands(sequence: str, window_size: int = 200, min_gc: float = 50.0) -> List[Dict[str, Any]]:
    """Detects potential CpG islands across a sliding window."""
    seq = str(sequence).upper().strip()
    islands = []
    w = int(window_size)
    for i in range(0, max(1, len(seq) - w + 1), w // 2):
        window = seq[i:i+w]
        gc = genomics_gc_content(window)
        cpg_count = window.count("CG")
        if gc >= min_gc and cpg_count >= 3:
            islands.append({"start": i, "end": i + len(window), "gc_content": gc, "cpg_count": cpg_count})
    return islands

def genomics_parse_vcf_line(vcf_line: str) -> Dict[str, Any]:
    """Parses a standard VCF variant text line."""
    parts = str(vcf_line).strip().split("\t")
    if len(parts) < 8:
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
