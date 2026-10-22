"""Epidemiology Domain Runtime: Compartmental disease spread (SIR/SEIR) and reproduction number."""
from typing import Dict, Any, List

def epi_r0(contact_rate_beta: float, recovery_rate_gamma: float) -> float:
    """Calculates Basic Reproduction Number R0 = beta / gamma."""
    gamma = float(recovery_rate_gamma)
    if gamma <= 0.0:
        return 0.0
    return round(float(contact_rate_beta) / gamma, 2)

def epi_herd_immunity_threshold(r0: float) -> float:
    """Calculates Herd Immunity Threshold HIT = (1 - 1/R0) * 100%."""
    r0_val = float(r0)
    if r0_val <= 1.0:
        return 0.0
    return round((1.0 - (1.0 / r0_val)) * 100.0, 2)

def epi_sir_step(s: float, i: float, r: float, beta: float, gamma: float, dt: float = 1.0) -> Dict[str, float]:
    """Single discrete Euler step of the SIR compartmental model."""
    s_val = float(s)
    i_val = float(i)
    r_val = float(r)
    n = s_val + i_val + r_val
    if n <= 0.0:
        return {"s": 0.0, "i": 0.0, "r": 0.0}
    dt_val = float(dt)
    new_infections = float(beta) * s_val * i_val / n * dt_val
    new_recoveries = float(gamma) * i_val * dt_val
    return {
        "s": round(max(0.0, s_val - new_infections), 2),
        "i": round(max(0.0, i_val + new_infections - new_recoveries), 2),
        "r": round(r_val + new_recoveries, 2)
    }
