"""Synthetic Biology Domain Runtime: Hill kinetics, Genetic Toggle Switch, Repressilator, and Codon Adaptation Index."""
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

def synbio_toggle_switch_step(u: float, v: float, alpha1: float = 10.0, alpha2: float = 10.0, beta: float = 2.0, gamma: float = 2.0, dt: float = 0.05) -> Dict[str, float]:
    """Single Euler integration step for Gardner bistable toggle switch."""
    u_val = float(u)
    v_val = float(v)
    dt_val = float(dt)
    # du/dt = alpha1 / (1 + v^beta) - u
    # dv/dt = alpha2 / (1 + u^gamma) - v
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
    # p1 is repressed by p3, p2 by p1, p3 by p2
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
