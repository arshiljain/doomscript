"""Metallurgy Domain Runtime: Hall-Petch strength, Hollomon strain hardening, Lever rule, Scheil solidification, JMAK recrystallization, Arrhenius diffusion, and fatigue kinetics."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

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
        return {"weight_alpha": 0.5, "weight_beta": 0.5, "alpha_pct": 50.0, "beta_pct": 50.0}
    w_alpha = (cb - c0) / (cb - ca)
    w_beta = (c0 - ca) / (cb - ca)
    wa_clamped = min(1.0, max(0.0, w_alpha))
    wb_clamped = min(1.0, max(0.0, w_beta))
    return {
        "weight_alpha": round(wa_clamped, 4),
        "weight_beta": round(wb_clamped, 4),
        "alpha_pct": round(wa_clamped * 100.0, 2),
        "beta_pct": round(wb_clamped * 100.0, 2)
    }

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

# ============================================================================
# 2. DEEPENED PHYSICAL METALLURGY & TRANSFORMATION KINETICS
# ============================================================================

def metal_zener_hollomon(strain_rate_s_1: float, activation_energy_j_mol: float, temp_k: float, r_gas: float = 8.314) -> float:
    """Calculates temperature-compensated strain rate (Zener-Hollomon parameter) Z = eps_dot * exp(Q / (R * T))."""
    eps_dot = float(strain_rate_s_1)
    q = float(activation_energy_j_mol)
    t = float(temp_k)
    if t <= 0.0 or eps_dot <= 0.0:
        return 0.0
    z = eps_dot * math.exp(q / (r_gas * t))
    return float(f"{z:.4e}")

def metal_koistinen_marburger_martensite(ms_temp_c: float, current_temp_c: float, alpha: float = 0.011) -> float:
    """Calculates volume fraction of athermal martensite formed during quenching: f_M = 1 - exp(-alpha * (Ms - T))."""
    ms = float(ms_temp_c)
    t = float(current_temp_c)
    if t >= ms:
        return 0.0
    fm = 1.0 - math.exp(-float(alpha) * (ms - t))
    return round(min(1.0, max(0.0, fm)), 4)

def metal_paris_crack_growth(delta_k_mpa_sqrt_m: float, c_constant: float = 1e-11, m_exponent: float = 3.0) -> float:
    """Calculates fatigue crack growth rate da/dN = C * (Delta K)^m in m/cycle."""
    dk = float(delta_k_mpa_sqrt_m)
    c = float(c_constant)
    m = float(m_exponent)
    if dk <= 0.0:
        return 0.0
    rate = c * (dk ** m)
    return float(f"{rate:.6e}")

class MetallurgyRuntime(DomainRuntime):
    """Runtime engine for metallurgy domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def hall_petch(self, s0: float, ky: float, d: float) -> float:
        return metal_hall_petch_yield_strength(s0, ky, d)
    def hollomon(self, k: float, eps: float, n: float) -> float:
        return metal_hollomon_true_stress(k, eps, n)
    def lever_rule(self, c0: float, ca: float, cb: float) -> Dict[str, float]:
        return metal_lever_rule(c0, ca, cb)
    def scheil(self, c0: float, k: float, fs: float) -> float:
        return metal_scheil_solidification(c0, k, fs)
    def jmak(self, t: float, k: float, n: float) -> float:
        return metal_jmak_recrystallization(t, k, n)
    def diffusion(self, d0: float, q: float, t: float, r: float = 8.314) -> float:
        return metal_arrhenius_diffusion(d0, q, t, r)
    def zener_hollomon(self, eps_dot: float, q: float, t: float) -> float:
        return metal_zener_hollomon(eps_dot, q, t)
    def martensite(self, ms: float, t: float, alpha: float = 0.011) -> float:
        return metal_koistinen_marburger_martensite(ms, t, alpha)
    def paris_law(self, dk: float, c: float = 1e-11, m: float = 3.0) -> float:
        return metal_paris_crack_growth(dk, c, m)
