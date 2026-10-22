"""Epidemiology Domain Runtime: Basic Reproduction Number R0, Herd immunity, SIR/SEIR models, and Case Fatality Rate."""
from typing import Dict, Any, List

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
