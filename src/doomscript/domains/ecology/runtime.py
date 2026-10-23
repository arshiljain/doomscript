"""Ecology Domain Runtime: Biodiversity indices, MacArthur-Wilson island biogeography, Lotka-Volterra dynamics, mark-recapture, and metapopulation models."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

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
    """Calculates Pielou Evenness Index J' = H' / ln(S)."""
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
    est = ((n1 + 1) * (n2 + 1) / (m2 + 1)) - 1.0
    var = ((n1 + 1) * (n2 + 1) * (n1 - m2) * (n2 - m2)) / (((m2 + 1) ** 2) * (m2 + 2))
    return {"estimated_population": round(est, 1), "std_error": round(math.sqrt(max(0.0, var)), 2)}

# ============================================================================
# 2. DEEPENED METAPOPULATION, NICHE OVERLAP & TROPHIC FLOWS
# ============================================================================

def ecology_levins_metapopulation(colonization_c: float, extinction_e: float, initial_fraction_p0: float, time_steps: int = 50, dt: float = 0.1) -> Dict[str, Any]:
    """Simulates Levins patch occupancy metapopulation dynamics dp/dt = c * p * (1 - p) - e * p."""
    c = float(colonization_c)
    e = float(extinction_e)
    p = float(initial_fraction_p0)
    dt_val = float(dt)
    trajectory = [round(p, 4)]
    p_star = max(0.0, 1.0 - (e / c)) if c > 0 else 0.0

    for _ in range(int(time_steps)):
        dp = (c * p * (1.0 - p) - e * p) * dt_val
        p = min(1.0, max(0.0, p + dp))
        trajectory.append(round(p, 4))

    return {
        "equilibrium_occupancy": round(p_star, 4),
        "final_occupancy": round(p, 4),
        "persistence": p > 0.01,
        "trajectory": trajectory
    }

def ecology_pianka_niche_overlap(resource_use_species_a: List[float], resource_use_species_b: List[float]) -> float:
    """Calculates Pianka symmetric niche overlap index O_jk between two species across resource bins."""
    a = [float(x) for x in resource_use_species_a]
    b = [float(x) for x in resource_use_species_b]
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    sum_a = sum(a[:n])
    sum_b = sum(b[:n])
    if sum_a <= 0 or sum_b <= 0:
        return 0.0
    pa = [x / sum_a for x in a[:n]]
    pb = [x / sum_b for x in b[:n]]
    dot = sum(pa[i] * pb[i] for i in range(n))
    norm_a = math.sqrt(sum(x**2 for x in pa))
    norm_b = math.sqrt(sum(x**2 for x in pb))
    if norm_a * norm_b <= 0:
        return 0.0
    overlap = dot / (norm_a * norm_b)
    return round(min(1.0, max(0.0, overlap)), 4)

class EcologyRuntime(DomainRuntime):
    """Runtime engine for Ecology domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def shannon(self, abundances: List[int]) -> float:
        return ecology_shannon_diversity(abundances)
    def simpson(self, abundances: List[int]) -> float:
        return ecology_simpson_diversity(abundances)
    def pielou(self, abundances: List[int]) -> float:
        return ecology_pielou_evenness(abundances)
    def island(self, a: float, c: float = 10.0, z: float = 0.25) -> float:
        return ecology_island_biogeography(a, c, z)
    def lotka_volterra(self, x: float, y: float, a: float, b: float, g: float, d: float, dt: float = 0.1) -> Dict[str, float]:
        return ecology_lotka_volterra_step(x, y, a, b, g, d, dt)
    def logistic(self, n0: float, r: float, k: float, t: float) -> float:
        return ecology_logistic_growth(n0, r, k, t)
    def mark_recapture(self, n1: int, n2: int, m2: int) -> Dict[str, float]:
        return ecology_lincoln_petersen_estimate(n1, n2, m2)
    def metapopulation(self, c: float, e: float, p0: float, steps: int = 50, dt: float = 0.1) -> Dict[str, Any]:
        return ecology_levins_metapopulation(c, e, p0, steps, dt)
    def niche_overlap(self, a: List[float], b: List[float]) -> float:
        return ecology_pianka_niche_overlap(a, b)
