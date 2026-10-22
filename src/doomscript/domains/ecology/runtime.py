"""Ecology Domain Runtime: Shannon/Simpson biodiversity, Pielou evenness, Lotka-Volterra, and Mark-Recapture."""
import math
from typing import List, Dict, Any

def ecology_shannon_diversity(abundances: List[int]) -> float:
    """Calculates Shannon-Wiener Diversity Index H' = -sum(p_i * ln(p_i))."""
    total = sum(abundances)
    if total <= 0:
        return 0.0
    h_prime = 0.0
    for count in abundances:
        if count > 0:
            p = count / total
            h_prime -= p * math.log(p)
    return round(h_prime, 4)

def ecology_simpson_diversity(abundances: List[int]) -> float:
    """Calculates Gini-Simpson Index 1 - D, where D = sum(p_i^2)."""
    total = sum(abundances)
    if total <= 0:
        return 0.0
    d = sum((c / total) ** 2 for c in abundances)
    return round(1.0 - d, 4)

def ecology_pielou_evenness(abundances: List[int]) -> float:
    """Calculates Pielou's Evenness Index J' = H' / ln(S)."""
    s = sum(1 for c in abundances if c > 0)
    if s <= 1:
        return 1.0
    h_prime = ecology_shannon_diversity(abundances)
    return round(h_prime / math.log(s), 4)

def ecology_island_biogeography(area_sq_km: float, constant_c: float = 10.0, z_exponent: float = 0.25) -> float:
    """MacArthur-Wilson species-area relationship S = C * A^z."""
    a = float(area_sq_km)
    if a <= 0:
        return 0.0
    s = float(constant_c) * (a ** float(z_exponent))
    return round(s, 2)

def ecology_lotka_volterra_step(prey: float, pred: float, alpha: float, beta: float, gamma: float, delta: float, dt: float = 0.1) -> Dict[str, float]:
    """Single Euler integration step for Lotka-Volterra predator-prey dynamics."""
    x = float(prey)
    y = float(pred)
    dt_val = float(dt)
    dx = (float(alpha) * x - float(beta) * x * y) * dt_val
    dy = (float(delta) * x * y - float(gamma) * y) * dt_val
    return {"prey": round(max(0.0, x + dx), 2), "predator": round(max(0.0, y + dy), 2)}

def ecology_logistic_growth(n0: float, r: float, k: float, time_t: float) -> float:
    """Calculates population size N(t) under logistic growth with carrying capacity K."""
    n0_val = float(n0)
    k_val = float(k)
    r_val = float(r)
    t = float(time_t)
    if n0_val <= 0.0 or k_val <= 0.0:
        return 0.0
    exp_term = math.exp(-r_val * t)
    return round((k_val * n0_val) / (n0_val + (k_val - n0_val) * exp_term), 2)

def ecology_lincoln_petersen_estimate(n1_marked: int, n2_captured: int, m2_recaptured: int) -> Dict[str, float]:
    """Chapman-corrected Lincoln-Petersen mark-recapture population estimator."""
    n1 = int(n1_marked)
    n2 = int(n2_captured)
    m2 = int(m2_recaptured)
    # Chapman modification: ((n1 + 1)(n2 + 1) / (m2 + 1)) - 1
    est = ((n1 + 1) * (n2 + 1) / (m2 + 1)) - 1.0
    var = ((n1 + 1) * (n2 + 1) * (n1 - m2) * (n2 - m2)) / (((m2 + 1) ** 2) * (m2 + 2))
    return {"estimated_population": round(est, 1), "std_error": round(math.sqrt(max(0.0, var)), 2)}
