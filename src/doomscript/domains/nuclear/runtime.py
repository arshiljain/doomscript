"""Nuclear Physics Domain Runtime: Radioactive decay, decay constant, Q-value release, radiation shielding, Four-Factor Formula, and Half-Value Layer."""
import math
from typing import Dict, Any

def nuclear_radioactive_decay(initial_activity_a0: float, half_life_years: float, elapsed_years: float) -> float:
    """Calculates remaining radioactive activity A(t) = A0 * (0.5)^(t / t_half) in Becquerels or Curies."""
    a0 = float(initial_activity_a0)
    hl = float(half_life_years)
    t = float(elapsed_years)
    if hl <= 0.0 or a0 <= 0.0:
        return 0.0
    activity = a0 * (0.5 ** (t / hl))
    return round(activity, 4)

def nuclear_decay_constant(half_life_seconds: float) -> float:
    """Calculates decay constant lambda = ln(2) / t_half in s^-1."""
    hl = float(half_life_seconds)
    if hl <= 0.0:
        return 0.0
    lam = math.log(2) / hl
    return float(f"{lam:.6e}")

def nuclear_reaction_q_value(initial_mass_amu: float, final_mass_amu: float) -> float:
    """Calculates nuclear reaction energy Q = (m_initial - m_final) * 931.494 MeV."""
    mi = float(initial_mass_amu)
    mf = float(final_mass_amu)
    q = (mi - mf) * 931.494
    return round(q, 4)

def nuclear_radiation_shielding(i0_intensity: float, linear_attenuation_mu_cm: float, thickness_cm: float) -> float:
    """Calculates transmitted radiation intensity I = I_0 * exp(-mu * x)."""
    i0 = float(i0_intensity)
    mu = float(linear_attenuation_mu_cm)
    x = float(thickness_cm)
    if i0 <= 0.0 or mu < 0.0 or x < 0.0:
        return 0.0
    transmitted = i0 * math.exp(-mu * x)
    return round(transmitted, 4)

def nuclear_four_factor_formula(eta_reproduction: float, epsilon_fast_fission: float, p_resonance_escape: float, f_thermal_utilization: float) -> float:
    """Calculates infinite multiplication factor k_inf = eta * epsilon * p * f in a nuclear reactor lattice."""
    eta = float(eta_reproduction)
    eps = float(epsilon_fast_fission)
    p = float(p_resonance_escape)
    f = float(f_thermal_utilization)
    k_inf = eta * eps * p * f
    return round(k_inf, 4)

def nuclear_half_value_layer(linear_attenuation_mu_cm: float) -> float:
    """Calculates radiation Half-Value Layer HVL = ln(2) / mu in cm."""
    mu = float(linear_attenuation_mu_cm)
    if mu <= 0.0:
        return 0.0
    return round(math.log(2) / mu, 4)
