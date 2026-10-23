"""Combustion Domain Runtime: Equivalence ratios, Arrhenius chemical kinetics, heat release, adiabatic flame temperature, flammability limits, and NOx scaling."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def combust_equivalence_ratio(fuel_mass: float, air_mass: float, stoich_fuel_air_ratio: float) -> float:
    """Calculates fuel-air equivalence ratio phi = (fuel / air) / stoich_ratio."""
    f = float(fuel_mass)
    a = float(air_mass)
    stoich = float(stoich_fuel_air_ratio)
    if a <= 0.0 or stoich <= 0.0:
        return 0.0
    phi = (f / a) / stoich
    return round(phi, 3)

def combust_arrhenius_rate(pre_exponential_a: float, activation_energy_j_mol: float, temp_k: float, r_gas: float = 8.314) -> float:
    """Calculates reaction rate constant k = A * exp(-Ea / (R * T))."""
    a = float(pre_exponential_a)
    ea = float(activation_energy_j_mol)
    t = float(temp_k)
    r = float(r_gas)
    if t <= 0.0:
        return 0.0
    k = a * math.exp(-ea / (r * t))
    return float(f"{k:.6e}")

def combust_heat_release_rate(fuel_mass_flow_kg_s: float, lower_heating_value_mj_kg: float, combustion_efficiency: float = 1.0) -> float:
    """Calculates thermal heat release rate Q_dot = m_dot * LHV * eta in Megawatts (MW)."""
    m = float(fuel_mass_flow_kg_s)
    lhv = float(lower_heating_value_mj_kg)
    eff = float(combustion_efficiency)
    return round(m * lhv * eff, 3)

def combust_adiabatic_flame_temp(t_initial_k: float, lhv_j_kg: float, cp_products_j_kgk: float, air_fuel_ratio: float) -> float:
    """Calculates approximate adiabatic flame temperature Tad = T0 + LHV / ((1 + AFR) * Cp) in Kelvin."""
    t0 = float(t_initial_k)
    lhv = float(lhv_j_kg)
    cp = float(cp_products_j_kgk)
    afr = float(air_fuel_ratio)
    denom = (1.0 + afr) * cp
    if denom <= 0.0:
        return t0
    tad = t0 + (lhv / denom)
    return round(tad, 1)

def combust_le_chatelier_flammability_limit(mole_fractions: List[float], flammability_limits: List[float]) -> float:
    """Calculates combustible gas mixture lower or upper flammability limit LFL_mix = 100 / sum(y_i / LFL_i)."""
    if len(mole_fractions) != len(flammability_limits) or not mole_fractions:
        return 0.0
    weighted_sum = sum(float(y) / float(lfl) for y, lfl in zip(mole_fractions, flammability_limits) if float(lfl) > 0.0)
    if weighted_sum <= 0.0:
        return 0.0
    total_y = sum(float(y) for y in mole_fractions)
    return round(total_y / weighted_sum, 2)

def combust_zeldovich_nox_scaling(temp_k: float, oxygen_mole_fraction: float) -> float:
    """Calculates normalized thermal NOx forward rate index under extended Zeldovich mechanism."""
    t = float(temp_k)
    xo2 = float(oxygen_mole_fraction)
    if t <= 0.0 or xo2 <= 0.0:
        return 0.0
    rate_index = math.sqrt(xo2) * math.exp(-38400.0 / t)
    return float(f"{rate_index:.6e}")

# ============================================================================
# 2. DEEPENED TURBULENT COMBUSTION & FUEL GAS METRICS
# ============================================================================

def combust_damkohler_number(flow_timescale_s: float, reaction_timescale_s: float) -> Dict[str, Any]:
    """Calculates Damköhler number Da = tau_flow / tau_chem and identifies combustion regime."""
    t_flow = float(flow_timescale_s)
    t_chem = float(reaction_timescale_s)
    if t_chem <= 0:
        return {"damkohler_number": float("inf"), "regime": "fast chemistry (flamelet)"}
    da = t_flow / t_chem
    if da > 10.0:
        regime = "laminar flamelet regime (fast chemistry)"
    elif da >= 1.0:
        regime = "thin reaction zones"
    else:
        regime = "well-stirred reactor (distributed reaction)"
    return {
        "damkohler_number": round(da, 3),
        "regime": regime
    }

def combust_wobbe_index(higher_heating_value_mj_m3: float, specific_gravity: float) -> float:
    """Calculates Wobbe Index Iw = HHV / sqrt(SG) for fuel gas interchangeability."""
    hhv = float(higher_heating_value_mj_m3)
    sg = float(specific_gravity)
    if sg <= 0:
        return 0.0
    iw = hhv / math.sqrt(sg)
    return round(iw, 2)

class CombustionRuntime(DomainRuntime):
    """Runtime engine for Combustion domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def equivalence_ratio(self, f: float, a: float, stoich: float) -> float:
        return combust_equivalence_ratio(f, a, stoich)
    def arrhenius(self, a: float, ea: float, t: float, r: float = 8.314) -> float:
        return combust_arrhenius_rate(a, ea, t, r)
    def heat_release(self, m: float, lhv: float, eff: float = 1.0) -> float:
        return combust_heat_release_rate(m, lhv, eff)
    def adiabatic_temp(self, t0: float, lhv: float, cp: float, afr: float) -> float:
        return combust_adiabatic_flame_temp(t0, lhv, cp, afr)
    def flammability(self, y: List[float], limits: List[float]) -> float:
        return combust_le_chatelier_flammability_limit(y, limits)
    def nox(self, t: float, xo2: float) -> float:
        return combust_zeldovich_nox_scaling(t, xo2)
    def damkohler(self, tf: float, tc: float) -> Dict[str, Any]:
        return combust_damkohler_number(tf, tc)
    def wobbe(self, hhv: float, sg: float) -> float:
        return combust_wobbe_index(hhv, sg)
