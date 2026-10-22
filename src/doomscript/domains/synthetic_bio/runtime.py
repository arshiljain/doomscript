"""Synthetic Biology Domain Runtime: Hill kinetics, Toggle Switch, Repressilator, Michaelis-Menten enzyme kinetics, Gibson assembly, and CAI."""
import math
from typing import Dict, Any

def synbio_hill_activation(conc: float, k_half: float, n_hill: float, v_max: float = 1.0) -> float:
    """Computes transcription activation via Hill equation: Vmax * (X^n) / (K^n + X^n)."""
    x = float(conc)
    k = float(k_half)
    n = float(n_hill)
    v = float(v_max)
    if x <= 0.0 or k <= 0.0:
        return 0.0
    x_n = x ** n
    k_n = k ** n
    return round((v * x_n) / (k_n + x_n), 4)

def synbio_hill_repression(conc: float, k_half: float, n_hill: float, v_max: float = 1.0) -> float:
    """Computes transcription repression via Hill equation: Vmax / (1 + (X / K)^n)."""
    x = float(conc)
    k = float(k_half)
    n = float(n_hill)
    v = float(v_max)
    if k <= 0.0:
        return 0.0
    if x <= 0.0:
        return round(v, 4)
    denom = 1.0 + (x / k) ** n
    return round(v / denom, 4)

def synbio_michaelis_menten(substrate_conc: float, v_max: float, km: float, inhibitor_conc: float = 0.0, ki: float = 1.0) -> float:
    """Calculates enzyme reaction rate v = (Vmax * [S]) / (Km * (1 + [I]/Ki) + [S]) with competitive inhibition."""
    s = float(substrate_conc)
    vmax = float(v_max)
    km_val = float(km)
    i_conc = float(inhibitor_conc)
    ki_val = float(ki)
    if s <= 0.0 or vmax <= 0.0:
        return 0.0
    apparent_km = km_val * (1.0 + (i_conc / ki_val)) if ki_val > 0 else km_val
    rate = (vmax * s) / (apparent_km + s)
    return round(rate, 4)

def synbio_gibson_assembly_overlap(frag1: str, frag2: str, min_overlap: int = 10) -> Dict[str, Any]:
    """Scans for matching terminal overlapping homologous regions between two DNA fragments."""
    s1 = str(frag1).upper().strip()
    s2 = str(frag2).upper().strip()
    min_len = int(min_overlap)
    best_overlap = ""
    for length in range(min_len, min(len(s1), len(s2)) + 1):
        suffix = s1[-length:]
        if s2.startswith(suffix):
            best_overlap = suffix
    has_match = len(best_overlap) >= min_len
    # Tm of overlap
    gc = sum(1 for c in best_overlap if c in "GC")
    tm = (64.9 + 41.0 * (gc - 16.4) / len(best_overlap)) if best_overlap else 0.0
    return {"compatible": has_match, "overlap_length": len(best_overlap), "sequence": best_overlap, "overlap_tm": round(tm, 2)}

def synbio_toggle_switch_step(u: float, v: float, alpha1: float = 10.0, alpha2: float = 10.0, beta: float = 2.0, gamma: float = 2.0, dt: float = 0.05) -> Dict[str, float]:
    """Single Euler integration step for Gardner bistable toggle switch."""
    u_val = float(u)
    v_val = float(v)
    dt_val = float(dt)
    du = (float(alpha1) / (1.0 + (v_val ** float(beta))) - u_val) * dt_val
    dv = (float(alpha2) / (1.0 + (u_val ** float(gamma))) - v_val) * dt_val
    return {"u": round(max(0.0, u_val + du), 4), "v": round(max(0.0, v_val + dv), 4)}

def synbio_repressilator_step(p1: float, p2: float, p3: float, alpha: float = 10.0, n_hill: float = 2.0, dt: float = 0.05) -> Dict[str, float]:
    """Single Euler integration step for Elowitz 3-node ring repressilator."""
    p1_v = float(p1)
    p2_v = float(p2)
    p3_v = float(p3)
    dt_v = float(dt)
    a = float(alpha)
    n = float(n_hill)
    dp1 = (a / (1.0 + p3_v ** n) - p1_v) * dt_v
    dp2 = (a / (1.0 + p1_v ** n) - p2_v) * dt_v
    dp3 = (a / (1.0 + p2_v ** n) - p3_v) * dt_v
    return {"p1": round(max(0.0, p1_v + dp1), 4), "p2": round(max(0.0, p2_v + dp2), 4), "p3": round(max(0.0, p3_v + dp3), 4)}

def synbio_codon_adaptation_index(sequence: str, weights_table: Dict[str, float]) -> float:
    """Computes Codon Adaptation Index (CAI) as geometric mean of relative synonymous codon weights."""
    seq = str(sequence).upper().replace("U", "T").strip()
    codons = [seq[i:i+3] for i in range(0, len(seq) - 2, 3) if len(seq[i:i+3]) == 3]
    if not codons:
        return 0.0
    log_sum = 0.0
    valid_count = 0
    for c in codons:
        w = float(weights_table.get(c, 0.5))
        if w > 0.0:
            log_sum += math.log(w)
            valid_count += 1
    if valid_count == 0:
        return 0.0
    cai = math.exp(log_sum / valid_count)
    return round(cai, 4)
