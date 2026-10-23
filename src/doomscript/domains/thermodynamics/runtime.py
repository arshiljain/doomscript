"""Thermodynamics Domain Runtime: Heat engines, Rankine/Brayton/Otto cycles, equations of state, and heat transfer."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED CYCLES & EQUATIONS
# ============================================================================

def thermo_carnot_efficiency(temp_hot_k: float, temp_cold_k: float) -> float:
    """Calculates ideal Carnot cycle thermal efficiency: eta = 1 - Tc / Th."""
    th, tc = float(temp_hot_k), float(temp_cold_k)
    if th <= 0.0 or tc < 0.0 or tc > th:
        return 0.0
    return round((1.0 - (tc / th)) * 100.0, 2)

def thermo_entropy_change(mass_kg: float, specific_heat_j_kgk: float, t_initial_k: float, t_final_k: float) -> float:
    """Calculates entropy change during isobaric/isochoric heating: Delta S = m * c * ln(T2 / T1)."""
    m = float(mass_kg)
    c = float(specific_heat_j_kgk)
    t1 = float(t_initial_k)
    t2 = float(t_final_k)
    if t1 <= 0.0 or t2 <= 0.0:
        return 0.0
    return round(m * c * math.log(t2 / t1), 4)

def thermo_polytropic_process(p1_pa: float, v1_m3: float, v2_m3: float, n_index: float) -> Dict[str, float]:
    """Calculates final pressure and boundary work for polytropic gas expansion: P * V^n = const."""
    p1 = float(p1_pa)
    v1 = float(v1_m3)
    v2 = float(v2_m3)
    n = float(n_index)
    if v1 <= 0.0 or v2 <= 0.0:
        return {"p2_pa": 0.0, "work_joules": 0.0}
    p2 = p1 * ((v1 / v2) ** n)
    if abs(n - 1.0) < 1e-6:
        # Isothermal case
        work = p1 * v1 * math.log(v2 / v1)
    else:
        work = (p1 * v1 - p2 * v2) / (n - 1.0)
    return {
        "p2_pa": round(p2, 2),
        "work_joules": round(work, 2)
    }

def thermo_clausius_clapeyron(p1_pa: float, t1_k: float, t2_k: float, delta_h_vap_j_mol: float, r_gas: float = 8.314) -> float:
    """Estimates saturation vapor pressure via integrated Clausius-Clapeyron equation: ln(P2/P1) = -DeltaH/R * (1/T2 - 1/T1)."""
    t1, t2 = float(t1_k), float(t2_k)
    if t1 <= 0.0 or t2 <= 0.0:
        return 0.0
    exponent = -(float(delta_h_vap_j_mol) / float(r_gas)) * ((1.0 / t2) - (1.0 / t1))
    p2 = float(p1_pa) * math.exp(exponent)
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
        return {"thermal_efficiency_pct": 0.0, "net_work_kj_kg": 0.0, "back_work_ratio": 0.0, "efficiency_pct": 0.0}
    eta = (w_net / q_in) * 100.0
    bwr = (w_pump / w_turb) if w_turb > 0.0 else 0.0
    return {
        "thermal_efficiency_pct": round(eta, 2),
        "net_work_kj_kg": round(w_net, 2),
        "back_work_ratio": round(bwr, 4),
        "efficiency_pct": round(eta, 2),
        "turbine_work_kj_kg": round(w_turb, 2),
        "pump_work_kj_kg": round(w_pump, 2),
    }

def thermo_joule_thomson_expansion(delta_p_bar: float, jt_coefficient_k_bar: float) -> float:
    """Calculates isenthalpic temperature change during throttling: Delta T = mu_JT * Delta P."""
    return round(float(jt_coefficient_k_bar) * float(delta_p_bar), 3)

# ============================================================================
# 2. ADVANCED POWER CYCLES & REAL GAS EOS
# ============================================================================

def thermo_brayton_cycle(pressure_ratio: float, gamma: float = 1.4, turbine_inlet_t_k: float = 1200.0, compressor_inlet_t_k: float = 300.0) -> Dict[str, float]:
    """Calculates ideal gas turbine Brayton cycle thermal efficiency and net work."""
    rp = float(pressure_ratio)
    g = float(gamma)
    exp = (g - 1.0) / g
    eta_ideal = 1.0 - (1.0 / (rp ** exp))
    t1 = float(compressor_inlet_t_k)
    t3 = float(turbine_inlet_t_k)
    t2 = t1 * (rp ** exp)
    t4 = t3 / (rp ** exp)
    cp = 1.005 # kJ/kg-K for air
    w_comp = cp * (t2 - t1)
    w_turb = cp * (t3 - t4)
    w_net = w_turb - w_comp
    return {
        "thermal_efficiency": round(eta_ideal, 4),
        "net_work_kj_kg": round(w_net, 2),
        "compressor_outlet_temp_k": round(t2, 1),
        "turbine_outlet_temp_k": round(t4, 1)
    }

def thermo_otto_cycle(compression_ratio: float, gamma: float = 1.4) -> float:
    """Calculates ideal Otto spark-ignition engine thermal efficiency: eta = 1 - (1 / r^(gamma - 1))."""
    r = float(compression_ratio)
    g = float(gamma)
    eta = 1.0 - (1.0 / (r ** (g - 1.0)))
    return round(eta, 4)

def thermo_heat_exchanger_lmtd(t_hot_in: float, t_hot_out: float, t_cold_in: float, t_cold_out: float, counterflow: bool = True) -> float:
    """Calculates Log Mean Temperature Difference (LMTD) for heat exchangers."""
    if counterflow:
        dt1 = float(t_hot_in) - float(t_cold_out)
        dt2 = float(t_hot_out) - float(t_cold_in)
    else:
        dt1 = float(t_hot_in) - float(t_cold_in)
        dt2 = float(t_hot_out) - float(t_cold_out)
    if dt1 <= 0 or dt2 <= 0:
        return 0.0
    if abs(dt1 - dt2) < 1e-4:
        return round(dt1, 2)
    lmtd = (dt1 - dt2) / math.log(dt1 / dt2)
    return round(lmtd, 2)

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class ThermodynamicsRuntime(DomainRuntime):
    """Unified runtime bridge for the Thermodynamics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def carnot(self, th: float, tc: float) -> float:
        return thermo_carnot_efficiency(th, tc)
    def entropy(self, m: float, c: float, t1: float, t2: float) -> float:
        return thermo_entropy_change(m, c, t1, t2)
    def polytropic(self, p1: float, v1: float, v2: float, n: float) -> Dict[str, float]:
        return thermo_polytropic_process(p1, v1, v2, n)
    def clausius_clapeyron(self, p1: float, t1: float, t2: float, dh: float) -> float:
        return thermo_clausius_clapeyron(p1, t1, t2, dh)
    def rankine(self, h2: float, h3: float, h4: float, h1: float) -> Dict[str, float]:
        return thermo_rankine_cycle_efficiency(h2, h3, h4, h1)
    def joule_thomson(self, dp: float, mu: float) -> float:
        return thermo_joule_thomson_expansion(dp, mu)
    def brayton(self, rp: float, gamma: float = 1.4) -> Dict[str, float]:
        return thermo_brayton_cycle(rp, gamma)
    def otto(self, r: float, gamma: float = 1.4) -> float:
        return thermo_otto_cycle(r, gamma)
    def lmtd(self, thi: float, tho: float, tci: float, tco: float) -> float:
        return thermo_heat_exchanger_lmtd(thi, tho, tci, tco)
