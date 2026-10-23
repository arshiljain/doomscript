"""Epidemiology Domain Runtime: Basic Reproduction Number R0, Herd immunity, SIR/SEIR models, CFR, Rt effective reproduction, final size, vaccination threshold, doubling time, and odds ratio."""
import math
from typing import Dict, Any, List
from doomscript.domains.base import DomainRuntime

def epi_r0(contact_rate_beta: float, recovery_rate_gamma: float) -> float:
    """Calculates Basic Reproduction Number R0 = beta / gamma."""
    gamma = float(recovery_rate_gamma)
    if gamma <= 0.0:
        return 0.0
    return round(float(contact_rate_beta) / gamma, 2)

def epi_herd_immunity_threshold(r0: float) -> float:
    """Calculates Herd Immunity Threshold HIT = (1 - 1/R0) as percentage."""
    r0_val = float(r0)
    if r0_val <= 1.0:
        return 0.0
    return round((1.0 - (1.0 / r0_val)) * 100.0, 2)

def epi_sir_step(s: float, i: float, r: float, beta: float, gamma: float, dt: float = 0.1) -> Dict[str, float]:
    """Single Euler integration step for standard SIR compartmental disease model."""
    s_val = float(s)
    i_val = float(i)
    r_val = float(r)
    n = max(1.0, s_val + i_val + r_val)
    dt_val = float(dt)
    new_inf = (float(beta) * s_val * i_val / n) * dt_val
    new_rec = (float(gamma) * i_val) * dt_val
    return {
        "s": round(max(0.0, s_val - new_inf), 2),
        "i": round(max(0.0, i_val + new_inf - new_rec), 2),
        "r": round(r_val + new_rec, 2)
    }

def epi_seir_step(s: float, e: float, i: float, r: float, beta: float, sigma_incubation: float, gamma: float, dt: float = 0.1) -> Dict[str, float]:
    """Single Euler integration step for SEIR compartmental disease model (with latent exposed state)."""
    s_v = float(s)
    e_v = float(e)
    i_v = float(i)
    r_v = float(r)
    n = max(1.0, s_v + e_v + i_v + r_v)
    dt_v = float(dt)
    new_exposed = (float(beta) * s_v * i_v / n) * dt_v
    new_infectious = (float(sigma_incubation) * e_v) * dt_v
    new_recovered = (float(gamma) * i_v) * dt_v
    return {
        "s": round(max(0.0, s_v - new_exposed), 2),
        "e": round(max(0.0, e_v + new_exposed - new_infectious), 2),
        "i": round(max(0.0, i_v + new_infectious - new_recovered), 2),
        "r": round(r_v + new_recovered, 2)
    }

def epi_fatality_rates(confirmed_cases: int, deaths: int) -> Dict[str, float]:
    """Calculates Case Fatality Rate (CFR) percentage."""
    c = int(confirmed_cases)
    d = int(deaths)
    cfr = (d / c) * 100.0 if c > 0 else 0.0
    return {"cfr_percent": round(cfr, 2)}

def epi_effective_reproduction_rt(r0: float, susceptible_fraction: float, intervention_reduction: float = 0.0) -> Dict[str, float]:
    """Calculates effective time-varying reproduction number Rt = R0 * (S / N) * (1 - reduction)."""
    r0_v = float(r0)
    s_frac = max(0.0, min(1.0, float(susceptible_fraction)))
    reduct = max(0.0, min(1.0, float(intervention_reduction)))
    rt = r0_v * s_frac * (1.0 - reduct)
    return {
        "rt": round(rt, 3),
        "epidemic_trend": "Expanding" if rt > 1.0 else ("Contracting" if rt < 1.0 else "Stable"),
        "transmission_suppressed": rt < 1.0
    }

def epi_final_size_relation(r0: float, s0_fraction: float = 0.999) -> Dict[str, float]:
    """Solves transcendental final size equation 1 - s_inf = 1 - s0 * exp(-R0 * (1 - s_inf))."""
    r0_v = float(r0)
    s0 = float(s0_fraction)
    if r0_v <= 1.0:
        return {"final_attack_rate_pct": 0.0, "total_infected_fraction": 0.0}
    # Fixed-point iteration for z = 1 - s_inf
    z = 0.5
    for _ in range(50):
        z_next = 1.0 - s0 * math.exp(-r0_v * z)
        if abs(z_next - z) < 1e-6:
            z = z_next
            break
        z = z_next
    return {
        "final_attack_rate_pct": round(z * 100.0, 2),
        "total_infected_fraction": round(z, 4)
    }

def epi_vaccination_critical_coverage(r0: float, vaccine_efficacy: float) -> Dict[str, float]:
    """Calculates critical vaccination coverage V_c = (1 - 1/R0) / E_v to achieve herd immunity."""
    r0_v = float(r0)
    ev = float(vaccine_efficacy)
    if r0_v <= 1.0:
        return {"critical_coverage_pct": 0.0, "achievable": True}
    if ev <= 0.0:
        return {"critical_coverage_pct": 100.0, "achievable": False}
    hit = 1.0 - (1.0 / r0_v)
    vc = hit / ev
    achievable = vc <= 1.0
    vc_pct = min(100.0, vc * 100.0)
    return {
        "critical_coverage_pct": round(vc_pct, 2),
        "herd_immunity_threshold_pct": round(hit * 100.0, 2),
        "achievable": achievable
    }

def epi_generation_time_doubling(r0: float, generation_time_days: float) -> Dict[str, float]:
    """Calculates intrinsic growth rate r and doubling time T_d in days."""
    r0_v = float(r0)
    tg = float(generation_time_days)
    if r0_v <= 1.0 or tg <= 0:
        return {"growth_rate_per_day": 0.0, "doubling_time_days": float('inf')}
    r = (r0_v - 1.0) / tg
    t_double = math.log(2) / r if r > 0 else float('inf')
    return {
        "growth_rate_per_day": round(r, 4),
        "doubling_time_days": round(t_double, 2)
    }

def epi_attack_rate_odds_ratio(exp_cases: int, exp_healthy: int, unexp_cases: int, unexp_healthy: int) -> Dict[str, Any]:
    """Calculates attack rates, relative risk, and odds ratio in an outbreak 2x2 contingency cohort."""
    a = float(exp_cases)
    b = float(exp_healthy)
    c = float(unexp_cases)
    d = float(unexp_healthy)
    ar_exp = (a / (a + b)) if (a + b) > 0 else 0.0
    ar_unexp = (c / (c + d)) if (c + d) > 0 else 0.0
    rr = (ar_exp / ar_unexp) if ar_unexp > 0 else 0.0
    odds_ratio = ((a * d) / (b * c)) if (b * c) > 0 else 0.0
    return {
        "exposed_attack_rate_pct": round(ar_exp * 100.0, 2),
        "unexposed_attack_rate_pct": round(ar_unexp * 100.0, 2),
        "relative_risk": round(rr, 3),
        "odds_ratio": round(odds_ratio, 3)
    }

def epi_secondary_attack_rate(secondary_cases: int, susceptible_contacts: int) -> Dict[str, float]:
    """Calculates Secondary Attack Rate (SAR) percentage among household/close contacts."""
    sec = float(secondary_cases)
    contacts = float(susceptible_contacts)
    sar = (sec / contacts * 100.0) if contacts > 0 else 0.0
    return {
        "secondary_attack_rate_pct": round(sar, 2)
    }

class EpidemiologyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "EpidemiologyRuntime",
    "epi_r0",
    "epi_herd_immunity_threshold",
    "epi_sir_step",
    "epi_seir_step",
    "epi_fatality_rates",
    "epi_effective_reproduction_rt",
    "epi_final_size_relation",
    "epi_vaccination_critical_coverage",
    "epi_generation_time_doubling",
    "epi_attack_rate_odds_ratio",
    "epi_secondary_attack_rate"
]
