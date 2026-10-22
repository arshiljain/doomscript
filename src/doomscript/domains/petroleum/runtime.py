"""Petroleum Engineering Domain Runtime: Darcy flow, Archie saturation, API gravity, GOR, Standing bubble point, and Sutton pseudocritical properties."""
import math
from typing import Dict, Any

def petro_darcy_radial_flow(permeability_md: float, net_pay_ft: float, p_reservoir_psi: float, p_wellbore_psi: float, viscosity_cp: float, re_ft: float, rw_ft: float, skin_factor: float = 0.0) -> float:
    """Calculates steady-state radial flow rate to wellbore (STB/day): q = 0.00708 * k * h * (Pr - Pw) / (mu * (ln(re/rw) + s))."""
    k = float(permeability_md)
    h = float(net_pay_ft)
    pr = float(p_reservoir_psi)
    pw = float(p_wellbore_psi)
    mu = float(viscosity_cp)
    re = float(re_ft)
    rw = float(rw_ft)
    s = float(skin_factor)
    if k <= 0.0 or h <= 0.0 or mu <= 0.0 or rw <= 0.0 or re <= rw:
        return 0.0
    denom = mu * (math.log(re / rw) + s)
    if denom <= 0.0:
        return 0.0
    q = (0.00708 * k * h * (pr - pw)) / denom
    return round(max(0.0, q), 2)

def petro_archie_water_saturation(porosity: float, resistivity_true_ohmm: float, resistivity_water_ohmm: float, a: float = 1.0, m: float = 2.0, n: float = 2.0) -> float:
    """Calculates water saturation Sw = ((a * Rw) / (phi^m * Rt))^(1/n)."""
    phi = float(porosity)
    rt = float(resistivity_true_ohmm)
    rw = float(resistivity_water_ohmm)
    a_f = float(a)
    m_f = float(m)
    n_f = float(n)
    if phi <= 0.0 or rt <= 0.0 or rw <= 0.0 or n_f <= 0.0:
        return 0.0
    f = a_f / (phi ** m_f)
    ro = f * rw
    sw = (ro / rt) ** (1.0 / n_f)
    return round(min(1.0, max(0.0, sw)), 4)

def petro_api_gravity(specific_gravity_60f: float) -> float:
    """Calculates API gravity: API = (141.5 / SG) - 131.5."""
    sg = float(specific_gravity_60f)
    if sg <= 0.0:
        return 0.0
    return round((141.5 / sg) - 131.5, 2)

def petro_solution_gor(gas_rate_mscfd: float, oil_rate_bopd: float) -> float:
    """Calculates Gas-Oil Ratio in scf/STB: GOR = (gas_mscfd * 1000) / oil_bopd."""
    gas = float(gas_rate_mscfd)
    oil = float(oil_rate_bopd)
    if oil <= 0.0:
        return 0.0
    return round((gas * 1000.0) / oil, 2)

def petro_standing_bubble_point(solution_gor_scf_stb: float, gas_gravity: float, api_gravity: float, temp_f: float) -> float:
    """Calculates bubble-point pressure Pb (psia) using Standing's empirical PVT correlation."""
    rs = float(solution_gor_scf_stb)
    gamma_g = float(gas_gravity)
    api = float(api_gravity)
    t = float(temp_f)
    if rs <= 0.0 or gamma_g <= 0.0:
        return 0.0
    a = 0.00091 * t - 0.0125 * api
    term = (rs / gamma_g) ** 0.83
    pb = 18.2 * ((term * (10 ** a)) - 1.4)
    return round(max(14.7, pb), 1)

def petro_sutton_pseudocritical(gas_specific_gravity: float) -> Dict[str, float]:
    """Calculates pseudocritical pressure Ppc (psia) and temperature Tpc (deg R) for natural gas using Sutton correlation."""
    g = float(gas_specific_gravity)
    if g <= 0.0:
        return {"ppc_psia": 0.0, "tpc_r": 0.0}
    ppc = 756.8 - (131.0 * g) - (3.6 * (g ** 2))
    tpc = 169.2 + (349.5 * g) - (74.0 * (g ** 2))
    return {"ppc_psia": round(ppc, 1), "tpc_r": round(tpc, 1)}
