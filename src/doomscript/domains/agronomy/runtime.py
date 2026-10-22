"""Agronomy Domain Runtime: Crop ETc, Growing Degree Days, fertilizer application rate, soil CEC, and bulk density porosity."""
import math
from typing import Dict, Any

def agronomy_crop_water_requirement(reference_et0_mm: float, crop_coefficient_kc: float) -> float:
    """Calculates crop water requirement ETc = Kc * ET0 in mm/day."""
    et0 = float(reference_et0_mm)
    kc = float(crop_coefficient_kc)
    return round(et0 * kc, 2)

def agronomy_growing_degree_days(t_max_c: float, t_min_c: float, t_base_c: float = 10.0, t_cutoff_c: float = 30.0) -> float:
    """Calculates daily Growing Degree Days GDD = max(0, (min(Tmax, Cutoff) + max(Tmin, Base)) / 2 - Base)."""
    tmax = min(float(t_cutoff_c), float(t_max_c))
    tmin = max(float(t_base_c), float(t_min_c))
    base = float(t_base_c)
    mean_temp = (tmax + tmin) / 2.0
    gdd = max(0.0, mean_temp - base)
    return round(gdd, 2)

def agronomy_fertilizer_rate(target_nutrient_kg_ha: float, nutrient_percentage: float) -> float:
    """Calculates required commercial bulk fertilizer application rate in kg/ha: bulk = target / (percent / 100)."""
    target = float(target_nutrient_kg_ha)
    pct = float(nutrient_percentage)
    if pct <= 0.0:
        return 0.0
    bulk = target / (pct / 100.0)
    return round(bulk, 2)

def agronomy_cation_exchange_capacity(ca_cmol_kg: float, mg_cmol_kg: float, k_cmol_kg: float, na_cmol_kg: float, h_al_cmol_kg: float = 0.0) -> Dict[str, float]:
    """Calculates effective Cation Exchange Capacity (CEC) and Base Saturation percentage."""
    ca = float(ca_cmol_kg)
    mg = float(mg_cmol_kg)
    k = float(k_cmol_kg)
    na = float(na_cmol_kg)
    acid = float(h_al_cmol_kg)

    base_sum = ca + mg + k + na
    total_cec = base_sum + acid
    base_sat = (base_sum / total_cec * 100.0) if total_cec > 0.0 else 0.0
    return {"cec_cmol_kg": round(total_cec, 2), "base_saturation_pct": round(base_sat, 1)}

def agronomy_soil_porosity(bulk_density_g_cm3: float, particle_density_g_cm3: float = 2.65) -> float:
    """Calculates total soil porosity fraction = 1 - (rho_bulk / rho_particle)."""
    pb = float(bulk_density_g_cm3)
    ps = float(particle_density_g_cm3)
    if ps <= 0.0 or pb < 0.0:
        return 0.0
    porosity = 1.0 - (pb / ps)
    return round(max(0.0, min(1.0, porosity)), 4)
