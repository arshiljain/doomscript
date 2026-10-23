"""Petroleum Domain Runtime: Reservoir engineering, multiphase fluid flow, rock physics, decline curves, and PVT analysis."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def petro_darcy_radial_flow(permeability_md: float, net_pay_ft: float, p_reservoir_psi: float, p_wellbore_psi: float, viscosity_cp: float, re_ft: float, rw_ft: float, skin_factor: float = 0.0) -> float:
    """Calculates steady-state radial oil flow rate (STB/day) via Darcy law: q = (0.00708 * k * h * dP) / (mu * B * (ln(re/rw) + s))."""
    k = float(permeability_md)
    h = float(net_pay_ft)
    pr = float(p_reservoir_psi)
    pw = float(p_wellbore_psi)
    mu = float(viscosity_cp)
    re = float(re_ft)
    rw = float(rw_ft)
    s = float(skin_factor)

    if rw <= 0.0 or re <= rw or mu <= 0.0:
        return 0.0
    dp = max(0.0, pr - pw)
    log_term = math.log(re / rw) + s
    if log_term <= 0.0:
        return 0.0
    q = (0.00708 * k * h * dp) / (mu * 1.15 * log_term)
    return round(q, 2)

def petro_archie_water_saturation(porosity: float, resistivity_true_ohmm: float, resistivity_water_ohmm: float, a: float = 1.0, m: float = 2.0, n: float = 2.0) -> float:
    """Calculates water saturation Sw via Archie equation: Sw = ((a * Rw) / (phi^m * Rt))^(1/n)."""
    phi = float(porosity)
    rt = float(resistivity_true_ohmm)
    rw = float(resistivity_water_ohmm)
    if phi <= 0.0 or rt <= 0.0 or rw <= 0.0 or n <= 0.0:
        return 1.0
    f = float(a) / (phi ** float(m))
    ri = (f * rw) / rt
    if ri < 0.0:
        return 0.0
    sw = ri ** (1.0 / float(n))
    return round(min(1.0, max(0.0, sw)), 4)

def petro_api_gravity(specific_gravity_60f: float) -> float:
    """Converts oil specific gravity (relative to water at 60F) to API gravity degrees: API = (141.5 / SG) - 131.5."""
    sg = float(specific_gravity_60f)
    if sg <= 0.0:
        return 0.0
    return round((141.5 / sg) - 131.5, 2)

def petro_solution_gor(gas_rate_mscfd: float, oil_rate_bopd: float) -> float:
    """Calculates Gas-Oil Ratio (scf/STB): GOR = (Qg_mscfd * 1000) / Qo_bopd."""
    qo = float(oil_rate_bopd)
    qg = float(gas_rate_mscfd)
    if qo <= 0.0:
        return 0.0
    return round((qg * 1000.0) / qo, 2)

def petro_standing_bubble_point(solution_gor_scf_stb: float, gas_gravity: float, api_gravity: float, temp_f: float) -> float:
    """Calculates bubble point pressure Pb (psi) via Standing correlation."""
    rs = float(solution_gor_scf_stb)
    gg = float(gas_gravity)
    api = float(api_gravity)
    t = float(temp_f)
    if rs <= 0.0 or gg <= 0.0:
        return 0.0
    val = (rs / gg) ** 0.83 * (10.0 ** (0.00091 * t - 0.0125 * api))
    pb = 18.2 * (val - 1.4)
    return round(max(0.0, pb), 2)

def petro_sutton_pseudocritical(gas_specific_gravity: float) -> Dict[str, float]:
    """Calculates pseudocritical pressure Ppc (psia) and temperature Tpc (deg R) via Sutton empirical correlations."""
    g = float(gas_specific_gravity)
    if g <= 0.0:
        return {"ppc_psia": 0.0, "tpc_r": 0.0}
    ppc = 756.8 - 131.0 * g - 3.6 * (g ** 2)
    tpc = 169.2 + 349.5 * g - 74.0 * (g ** 2)
    return {"ppc_psia": round(ppc, 2), "tpc_r": round(tpc, 2)}

# ============================================================================
# 2. DEEPENED ADVANCED RESERVOIR & PRODUCTION ENGINEERING
# ============================================================================

def petro_arps_decline(q_initial: float, nominal_decline: float, time_months: float, b_factor: float = 0.0) -> Dict[str, float]:
    """Calculates Arps production decline rate q(t) and cumulative production Np(t).
    b = 0: Exponential decline
    0 < b < 1: Hyperbolic decline
    b = 1: Harmonic decline
    """
    qi = float(q_initial)
    d = float(nominal_decline)
    t = float(time_months)
    b = float(b_factor)

    if qi <= 0.0 or t <= 0.0:
        return {"q_rate": qi, "cumulative": 0.0, "decline_type": "exponential"}

    if abs(b) < 1e-4:
        # Exponential
        q_t = qi * math.exp(-d * t)
        np_t = (qi - q_t) / d if d > 0 else 0.0
        dec_type = "exponential"
    elif abs(b - 1.0) < 1e-4:
        # Harmonic
        q_t = qi / (1.0 + d * t)
        np_t = (qi / d) * math.log(1.0 + d * t) if d > 0 else 0.0
        dec_type = "harmonic"
    else:
        # Hyperbolic
        denom = (1.0 + b * d * t) ** (1.0 / b)
        q_t = qi / denom if denom > 0 else 0.0
        np_t = (qi / ((1.0 - b) * d)) * (1.0 - ((1.0 + b * d * t) ** ((b - 1.0) / b))) if d > 0 and abs(b - 1.0) > 1e-4 else 0.0
        dec_type = "hyperbolic"

    return {
        "q_rate": round(q_t, 2),
        "cumulative": round(np_t, 2),
        "decline_type": dec_type
    }

def petro_vogel_ipr(q_max: float, p_reservoir: float, p_wellbore: float) -> Dict[str, float]:
    """Calculates Vogel Inflow Performance Relationship for two-phase reservoir below bubble point:
    q / q_max = 1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr)^2.
    """
    qm = float(q_max)
    pr = float(p_reservoir)
    pwf = float(p_wellbore)
    if pr <= 0.0:
        return {"flow_rate": 0.0, "drawdown": 0.0, "efficiency_ratio": 0.0}
    pwf_ratio = min(1.0, max(0.0, pwf / pr))
    ratio = 1.0 - 0.2 * pwf_ratio - 0.8 * (pwf_ratio ** 2)
    q = qm * ratio
    return {
        "flow_rate": round(max(0.0, q), 2),
        "drawdown_psi": round(pr - pwf, 2),
        "ipr_ratio": round(ratio, 4)
    }

def petro_dranchuk_z_factor(p_pseudo_reduced: float, t_pseudo_reduced: float) -> float:
    """Calculates natural gas compressibility factor Z via Dranchuk-Abou-Kassem (DAK) EOS approximation."""
    ppr = float(p_pseudo_reduced)
    tpr = float(t_pseudo_reduced)
    if tpr <= 1.0 or ppr <= 0.0:
        return 1.0
    # Hall-Yarborough empirical correlation for Z
    t_inv = 1.0 / tpr
    # Reduced density approximation
    y = 0.0125 * ppr * t_inv * math.exp(-1.2 * ((1.0 - t_inv) ** 2))
    # Iterative Newton-Raphson solve for reduced density y
    for _ in range(10):
        f = -0.06125 * ppr * t_inv * math.exp(-1.2 * ((1.0 - t_inv) ** 2)) + (y + y**2 + y**3 - y**4) / ((1 - y)**3)
        df = (1 + 4*y + 4*y**2 - 4*y**3 + y**4) / ((1 - y)**4)
        if abs(df) < 1e-6:
            break
        y_new = y - f / df
        if y_new <= 0 or y_new >= 1:
            break
        y = y_new
    z = (0.06125 * ppr * t_inv * math.exp(-1.2 * ((1.0 - t_inv) ** 2))) / y if y > 0 else 1.0
    return round(min(2.0, max(0.2, z)), 4)

def petro_material_balance_havlena_odeh(cumulative_oil_stb: float, oil_formation_volume_factor: float, gas_formation_volume_factor: float, solution_gor: float, cumulative_gor: float) -> Dict[str, float]:
    """Evaluates Havlena-Odeh tank reservoir material balance expansion parameters (F = N * (Eo + m*Eg))."""
    np = float(cumulative_oil_stb)
    bo = float(oil_formation_volume_factor)
    bg = float(gas_formation_volume_factor)
    rs = float(solution_gor)
    rp = float(cumulative_gor)
    underground_withdrawal_f = np * (bo + (rp - rs) * bg)
    return {
        "underground_withdrawal_bbl": round(underground_withdrawal_f, 2),
        "net_voidage": round(underground_withdrawal_f, 2)
    }

class PetroleumRuntime(DomainRuntime):
    """Runtime manager for Petroleum domain operations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def __init__(self):
        super().__init__()

    def darcy_flow(self, k: float, h: float, pr: float, pw: float, mu: float, re: float, rw: float, s: float = 0.0) -> float:
        return petro_darcy_radial_flow(k, h, pr, pw, mu, re, rw, s)

    def water_sat(self, phi: float, rt: float, rw: float, a: float = 1.0, m: float = 2.0, n: float = 2.0) -> float:
        return petro_archie_water_saturation(phi, rt, rw, a, m, n)

    def api(self, sg: float) -> float:
        return petro_api_gravity(sg)

    def gor(self, qg: float, qo: float) -> float:
        return petro_solution_gor(qg, qo)

    def bubble_point(self, rs: float, gg: float, api: float, t: float) -> float:
        return petro_standing_bubble_point(rs, gg, api, t)

    def pseudocritical(self, sg: float) -> Dict[str, float]:
        return petro_sutton_pseudocritical(sg)

    def arps(self, qi: float, d: float, t: float, b: float = 0.0) -> Dict[str, float]:
        return petro_arps_decline(qi, d, t, b)

    def vogel(self, qmax: float, pr: float, pwf: float) -> Dict[str, float]:
        return petro_vogel_ipr(qmax, pr, pwf)

    def z_factor(self, ppr: float, tpr: float) -> float:
        return petro_dranchuk_z_factor(ppr, tpr)
