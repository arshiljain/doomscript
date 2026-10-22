"""Combustion Domain Runtime: Equivalence ratio, Arrhenius kinetics, heat release rate, adiabatic flame temp, Le Chatelier limits, and Zeldovich NOx."""
import math
from typing import List, Dict, Any

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
    # Activation energy for N2 + O -> NO + N is ~318 kJ/mol
    rate_index = math.sqrt(xo2) * math.exp(-38400.0 / t)
    return float(f"{rate_index:.6e}")
