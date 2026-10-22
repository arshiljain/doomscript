"""Metallurgy Domain Runtime: Hall-Petch strength, Hollomon strain hardening, lever rule, Scheil solidification, JMAK recrystallization, and Arrhenius diffusion."""
import math
from typing import Dict, Any

def metal_hall_petch_yield_strength(sigma_0_mpa: float, ky_mpa_sqrt_m: float, grain_diameter_um: float) -> float:
    """Calculates yield strength using Hall-Petch relation: sigma_y = sigma_0 + k_y / sqrt(d)."""
    s0 = float(sigma_0_mpa)
    ky = float(ky_mpa_sqrt_m)
    d_um = float(grain_diameter_um)
    if d_um <= 0.0:
        return 0.0
    d_m = d_um * 1e-6
    sigma_y = s0 + (ky / math.sqrt(d_m))
    return round(sigma_y, 2)

def metal_hollomon_true_stress(strength_coefficient_k_mpa: float, true_strain: float, strain_hardening_n: float) -> float:
    """Calculates true flow stress using Hollomon equation: sigma = K * epsilon^n."""
    k = float(strength_coefficient_k_mpa)
    eps = float(true_strain)
    n = float(strain_hardening_n)
    if eps < 0.0 or k < 0.0:
        return 0.0
    return round(k * (eps ** n), 2)

def metal_lever_rule(composition_overall: float, composition_alpha: float, composition_beta: float) -> Dict[str, float]:
    """Calculates phase mass fractions using the Lever Rule: W_alpha = (C_beta - C_0) / (C_beta - C_alpha), W_beta = 1 - W_alpha."""
    c0 = float(composition_overall)
    ca = float(composition_alpha)
    cb = float(composition_beta)
    if abs(cb - ca) < 1e-7:
        return {"weight_alpha": 0.5, "weight_beta": 0.5}
    w_alpha = (cb - c0) / (cb - ca)
    w_beta = (c0 - ca) / (cb - ca)
    return {"weight_alpha": round(min(1.0, max(0.0, w_alpha)), 4), "weight_beta": round(min(1.0, max(0.0, w_beta)), 4)}

def metal_scheil_solidification(c_initial: float, partition_coeff_k: float, fraction_solid: float) -> float:
    """Calculates instantaneous liquid solute composition during non-equilibrium solidification: C_L = C_0 * (1 - f_s)^(k - 1)."""
    c0 = float(c_initial)
    k = float(partition_coeff_k)
    fs = float(fraction_solid)
    if fs >= 1.0:
        fs = 0.999
    if fs < 0.0:
        fs = 0.0
    c_l = c0 * ((1.0 - fs) ** (k - 1.0))
    return round(c_l, 4)

def metal_jmak_recrystallization(time_seconds: float, rate_constant_k: float, avrami_exponent_n: float) -> float:
    """Calculates recrystallized volume fraction X(t) = 1 - exp(-k * t^n) using Johnson-Mehl-Avrami-Kolmogorov (JMAK) kinetics."""
    t = float(time_seconds)
    k = float(rate_constant_k)
    n = float(avrami_exponent_n)
    if t <= 0.0 or k <= 0.0:
        return 0.0
    x = 1.0 - math.exp(-k * (t ** n))
    return round(min(1.0, max(0.0, x)), 4)

def metal_arrhenius_diffusion(d0_m2_s: float, activation_energy_j_mol: float, temp_k: float, r_gas: float = 8.314) -> float:
    """Calculates solid-state atomic diffusion coefficient D = D0 * exp(-Q / (R * T)) in m^2/s."""
    d0 = float(d0_m2_s)
    q = float(activation_energy_j_mol)
    t = float(temp_k)
    r = float(r_gas)
    if t <= 0.0:
        return 0.0
    d = d0 * math.exp(-q / (r * t))
    return float(f"{d:.6e}")
