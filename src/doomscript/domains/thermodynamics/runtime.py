"""Thermodynamics Domain Runtime: Carnot efficiency, Entropy, Enthalpy, Polytropic gas processes, Rankine cycle, and Joule-Thomson effect."""
import math
from typing import Dict, Any

def thermo_carnot_efficiency(temp_hot_k: float, temp_cold_k: float) -> float:
    """Calculates maximum theoretical Carnot heat engine efficiency eta = 1 - (Tc / Th)."""
    th = float(temp_hot_k)
    tc = float(temp_cold_k)
    if th <= 0.0 or tc <= 0.0 or tc > th:
        return 0.0
    return round((1.0 - (tc / th)) * 100.0, 2)

def thermo_entropy_change(mass_kg: float, specific_heat_j_kgk: float, t_initial_k: float, t_final_k: float) -> float:
    """Calculates entropy change delta_S = m * c * ln(T2 / T1) in J/K."""
    m = float(mass_kg)
    c = float(specific_heat_j_kgk)
    t1 = float(t_initial_k)
    t2 = float(t_final_k)
    if t1 <= 0.0 or t2 <= 0.0 or m <= 0.0 or c <= 0.0:
        return 0.0
    return round(m * c * math.log(t2 / t1), 3)

def thermo_polytropic_process(p1_pa: float, v1_m3: float, v2_m3: float, n_index: float) -> Dict[str, float]:
    """Calculates final pressure P2 = P1 * (V1/V2)^n and work done W = (P1*V1 - P2*V2) / (n - 1)."""
    p1 = float(p1_pa)
    v1 = float(v1_m3)
    v2 = float(v2_m3)
    n = float(n_index)
    if v1 <= 0.0 or v2 <= 0.0:
        return {"p2_pa": 0.0, "work_joules": 0.0}
    p2 = p1 * ((v1 / v2) ** n)
    if abs(n - 1.0) < 1e-5:
        w = p1 * v1 * math.log(v2 / v1)
    else:
        w = (p1 * v1 - p2 * v2) / (n - 1.0)
    return {"p2_pa": round(p2, 2), "work_joules": round(w, 2)}

def thermo_clausius_clapeyron(p1_pa: float, t1_k: float, t2_k: float, delta_h_vap_j_mol: float, r_gas: float = 8.314) -> float:
    """Calculates vapor pressure P2 at temperature T2 using Clausius-Clapeyron equation: ln(P2/P1) = -(delta_H/R) * (1/T2 - 1/T1)."""
    p1 = float(p1_pa)
    t1 = float(t1_k)
    t2 = float(t2_k)
    dh = float(delta_h_vap_j_mol)
    r = float(r_gas)
    if t1 <= 0.0 or t2 <= 0.0 or p1 <= 0.0:
        return 0.0
    exponent = -(dh / r) * ((1.0 / t2) - (1.0 / t1))
    p2 = p1 * math.exp(exponent)
    return round(p2, 2)

def thermo_rankine_cycle_efficiency(h_boiler_in_kj_kg: float, h_turbine_in_kj_kg: float, h_condenser_in_kj_kg: float, h_pump_in_kj_kg: float) -> Dict[str, float]:
    """Calculates ideal Rankine vapor power cycle thermal efficiency: eta = (W_turbine - W_pump) / Q_in."""
    h1 = float(h_pump_in_kj_kg)
    h2 = float(h_boiler_in_kj_kg)
    h3 = float(h_turbine_in_kj_kg)
    h4 = float(h_condenser_in_kj_kg)
    q_in = h3 - h2
    w_turb = h3 - h4
    w_pump = h2 - h1
    w_net = w_turb - w_pump
    if q_in <= 0.0:
        return {"thermal_efficiency_pct": 0.0, "net_work_kj_kg": 0.0, "back_work_ratio": 0.0}
    eta = (w_net / q_in) * 100.0
    bwr = (w_pump / w_turb) if w_turb > 0.0 else 0.0
    return {
        "thermal_efficiency_pct": round(eta, 2),
        "net_work_kj_kg": round(w_net, 2),
        "back_work_ratio": round(bwr, 4)
    }

def thermo_joule_thomson_expansion(delta_p_bar: float, jt_coefficient_k_bar: float) -> float:
    """Calculates isenthalpic temperature change delta_T = mu_JT * delta_P across throttle valve."""
    dp = float(delta_p_bar)
    mu_jt = float(jt_coefficient_k_bar)
    return round(mu_jt * dp, 3)
