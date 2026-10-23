"""Synthetic Biology Domain Runtime: Hill kinetics, genetic switches, repressilators, metabolic flux, and CRISPR guide design."""
import math
from typing import List, Dict, Any, Tuple, Optional, Set
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED CORE ENZYME & GENETIC KINETICS
# ============================================================================

def synbio_hill_activation(conc: float, k_half: float, n_hill: float, v_max: float = 1.0) -> float:
    """Calculates Hill activation function: v = Vmax * (x^n) / (K^n + x^n)."""
    if conc <= 0.0 or k_half <= 0.0:
        return 0.0
    x_n = conc ** n_hill
    k_n = k_half ** n_hill
    return round(v_max * (x_n / (k_n + x_n)), 4)

def synbio_hill_repression(conc: float, k_half: float, n_hill: float, v_max: float = 1.0) -> float:
    """Calculates Hill repression function: v = Vmax * (K^n) / (K^n + x^n)."""
    if conc <= 0.0:
        return float(v_max)
    if k_half <= 0.0:
        return 0.0
    x_n = conc ** n_hill
    k_n = k_half ** n_hill
    return round(v_max * (k_n / (k_n + x_n)), 4)

def synbio_michaelis_menten(substrate_conc: float, v_max: float, km: float, inhibitor_conc: float = 0.0, ki: float = 1.0) -> float:
    """Calculates Michaelis-Menten enzyme kinetics with optional competitive inhibition."""
    if substrate_conc <= 0.0 or v_max <= 0.0:
        return 0.0
    effective_km = km * (1.0 + inhibitor_conc / ki) if inhibitor_conc > 0.0 and ki > 0.0 else km
    rate = (v_max * substrate_conc) / (effective_km + substrate_conc)
    return round(rate, 4)

def synbio_gibson_assembly_overlap(frag1: str, frag2: str, min_overlap: int = 10) -> Dict[str, Any]:
    """Checks for homologous overlap between end of frag1 and start of frag2."""
    s1 = frag1.upper()
    s2 = frag2.upper()
    best_overlap = ""
    max_k = min(len(s1), len(s2))
    for k in range(min_overlap, max_k + 1):
        if s1.endswith(s2[:k]):
            best_overlap = s2[:k]
    return {
        "has_overlap": len(best_overlap) >= min_overlap,
        "compatible": len(best_overlap) >= min_overlap,
        "overlap_length": len(best_overlap),
        "overlap_sequence": best_overlap
    }

def synbio_toggle_switch_step(u: float, v: float, alpha1: float = 10.0, alpha2: float = 10.0, beta: float = 2.0, gamma: float = 2.0, dt: float = 0.05) -> Dict[str, float]:
    """Single Euler integration step for Gardner bistable genetic toggle switch."""
    du = (alpha1 / (1.0 + (v ** beta))) - u
    dv = (alpha2 / (1.0 + (u ** gamma))) - v
    return {
        "u": round(max(0.0, u + du * dt), 4),
        "v": round(max(0.0, v + dv * dt), 4)
    }

def synbio_repressilator_step(p1: float, p2: float, p3: float, alpha: float = 10.0, n_hill: float = 2.0, dt: float = 0.05) -> Dict[str, float]:
    """Single Euler integration step of Elowitz & Leibler 3-node cyclic repressilator."""
    dp1 = (alpha / (1.0 + (p3 ** n_hill))) - p1
    dp2 = (alpha / (1.0 + (p1 ** n_hill))) - p2
    dp3 = (alpha / (1.0 + (p2 ** n_hill))) - p3
    return {
        "p1": round(max(0.0, p1 + dp1 * dt), 4),
        "p2": round(max(0.0, p2 + dp2 * dt), 4),
        "p3": round(max(0.0, p3 + dp3 * dt), 4)
    }

def synbio_codon_adaptation_index(sequence: str, weights_table: Optional[Dict[str, float]] = None) -> float:
    """Calculates Codon Adaptation Index (CAI) of a protein coding sequence."""
    s = sequence.upper()
    if len(s) < 3:
        return 0.0
    default_w = {"ATG": 1.0, "TGG": 1.0, "GAA": 1.0, "AAA": 1.0, "CTG": 1.0, "ACC": 1.0}
    weights = weights_table or default_w
    codons = [s[i:i+3] for i in range(0, len(s) - 2, 3)]
    log_sum = 0.0
    count = 0
    for c in codons:
        w = weights.get(c, 0.5)
        log_sum += math.log(max(1e-4, w))
        count += 1
    return round(math.exp(log_sum / max(1, count)), 4)

# ============================================================================
# 2. METABOLIC FLUX ANALYSIS & CRISPR GUIDE SCORING
# ============================================================================

def synbio_metabolic_flux_balance(S: List[List[float]], bounds: List[Tuple[float, float]]) -> Dict[str, Any]:
    """Simplified Metabolic Flux Analysis checking conservation S * v = 0 feasibility."""
    num_mets = len(S)
    num_rxns = len(bounds)
    if num_mets == 0 or num_rxns == 0:
        return {"feasible": False, "fluxes": []}
    zero_feasible = all(b[0] <= 0.0 <= b[1] for b in bounds)
    mid_fluxes = [round((b[0] + b[1]) / 2.0, 4) for b in bounds]
    residual = 0.0
    for i in range(num_mets):
        r = sum(S[i][j] * mid_fluxes[j] for j in range(num_rxns))
        residual += abs(r)
    return {
        "feasible": zero_feasible or residual < 1e-4,
        "reactions": num_rxns,
        "metabolites": num_mets,
        "sample_fluxes": mid_fluxes,
        "residual_sum": round(residual, 5)
    }

def synbio_crispr_guide_score(guide_20bp: str, target_dna: str) -> Dict[str, Any]:
    """Evaluates CRISPR Cas9 on-target efficiency and PAM site presence."""
    g = guide_20bp.upper()
    t = target_dna.upper()
    has_pam = t.endswith("GG") or "GG" in t[-4:]
    gc_count = g.count("G") + g.count("C")
    gc_pct = (gc_count / len(g)) * 100.0 if g else 0.0
    gc_score = 1.0 - abs(50.0 - gc_pct) / 50.0
    poly_t_penalty = 0.5 if "TTTT" in g else 1.0
    efficiency = max(0.0, min(100.0, (gc_score * 0.7 + (0.3 if has_pam else 0.0)) * poly_t_penalty * 100.0))
    return {
        "guide": g,
        "gc_content_pct": round(gc_pct, 1),
        "has_canonical_pam": has_pam,
        "efficiency_score": round(efficiency, 2)
    }

def synbio_gibson_designer(fragment_a: str, fragment_b: str, overlap_len: int = 25) -> Dict[str, Any]:
    """Designs 20-40bp homologous overlap overhang with matching Tm for isothermal assembly."""
    ol = min(len(fragment_a), len(fragment_b), max(15, int(overlap_len)))
    overhang = fragment_b[:ol]
    gc = overhang.count("G") + overhang.count("C")
    tm = 64.9 + 41.0 * (gc - 16.4) / ol if ol > 0 else 0.0
    return {
        "overlap_sequence": overhang,
        "overlap_length": ol,
        "melting_temp_c": round(tm, 2),
        "fragment_a_primed": fragment_a + overhang,
        "optimal": 50.0 <= tm <= 70.0
    }

def synbio_monod_growth_step(biomass_x: float, substrate_s: float, mu_max: float = 0.5, ks: float = 0.1, yield_y: float = 0.5, dt: float = 0.1) -> Dict[str, float]:
    """Simulates Monod bacterial batch cell growth kinetics: mu = mu_max * S / (Ks + S)."""
    mu = mu_max * (substrate_s / (ks + substrate_s)) if substrate_s > 0 else 0.0
    dx = mu * biomass_x
    ds = -(1.0 / yield_y) * dx
    new_x = max(0.0, biomass_x + dx * dt)
    new_s = max(0.0, substrate_s + ds * dt)
    return {
        "biomass": round(new_x, 4),
        "substrate": round(new_s, 4),
        "growth_rate_mu": round(mu, 4)
    }

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class SyntheticBioRuntime(DomainRuntime):
    """Unified runtime bridge for the Synthetic Biology computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def hill_act(self, x: float, k: float, n: float, vmax: float = 1.0) -> float:
        return synbio_hill_activation(x, k, n, vmax)
    def hill_rep(self, x: float, k: float, n: float, vmax: float = 1.0) -> float:
        return synbio_hill_repression(x, k, n, vmax)
    def michaelis_menten(self, s: float, vmax: float, km: float) -> float:
        return synbio_michaelis_menten(s, vmax, km)
    def gibson_check(self, f1: str, f2: str, min_ol: int = 10) -> Dict[str, Any]:
        return synbio_gibson_assembly_overlap(f1, f2, min_ol)
    def gibson_design(self, fa: str, fb: str, ol: int = 25) -> Dict[str, Any]:
        return synbio_gibson_designer(fa, fb, ol)
    def toggle_step(self, u: float, v: float, dt: float = 0.05) -> Dict[str, float]:
        return synbio_toggle_switch_step(u, v, dt=dt)
    def repressilator_step(self, p1: float, p2: float, p3: float, dt: float = 0.05) -> Dict[str, float]:
        return synbio_repressilator_step(p1, p2, p3, dt=dt)
    def cai(self, seq: str) -> float:
        return synbio_codon_adaptation_index(seq)
    def flux_balance(self, S: List[List[float]], bounds: List[Tuple[float, float]]) -> Dict[str, Any]:
        return synbio_metabolic_flux_balance(S, bounds)
    def crispr(self, guide: str, target: str) -> Dict[str, Any]:
        return synbio_crispr_guide_score(guide, target)
    def monod_step(self, x: float, s: float, dt: float = 0.1) -> Dict[str, float]:
        return synbio_monod_growth_step(x, s, dt=dt)
