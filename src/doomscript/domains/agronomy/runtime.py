"""Agronomy Domain Runtime: Crop ETc, Growing Degree Days, fertilizer rate, soil CEC, bulk porosity, USLE soil erosion, available water capacity, nitrogen mineralization, irrigation scheduling, and leaf area index."""
import math
from typing import Dict, Any, List
from doomscript.domains.base import DomainRuntime

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

def agronomy_universal_soil_loss_equation(r_factor: float, k_factor: float, ls_factor: float, c_factor: float, p_factor: float) -> Dict[str, Any]:
    """Calculates annual soil erosion loss A = R * K * LS * C * P in t/ha/yr via USLE."""
    r = float(r_factor)
    k = float(k_factor)
    ls = float(ls_factor)
    c = float(c_factor)
    p = float(p_factor)
    loss = r * k * ls * c * p
    if loss < 5.0:
        severity = "Very Low / Tolerable"
    elif loss < 12.0:
        severity = "Moderate"
    elif loss < 25.0:
        severity = "High"
    else:
        severity = "Severe"
    return {
        "annual_soil_loss_t_ha_yr": round(loss, 2),
        "erosion_severity": severity
    }

def agronomy_available_water_capacity(field_capacity_pct: float, wilting_point_pct: float, root_depth_m: float) -> Dict[str, float]:
    """Calculates Plant Available Water Capacity AWC = (FC - PWP) * depth in mm."""
    fc = float(field_capacity_pct)
    pwp = float(wilting_point_pct)
    depth = float(root_depth_m)
    # AWC in mm = (FC% - PWP%) / 100 * depth_m * 1000 = (FC - PWP) * depth * 10
    awc_mm = max(0.0, (fc - pwp) * depth * 10.0)
    raw_mm = 0.5 * awc_mm  # Readily available water with MAD = 50%
    return {
        "awc_mm": round(awc_mm, 1),
        "readily_available_water_mm": round(raw_mm, 1),
        "root_depth_m": depth
    }

def agronomy_nitrogen_mineralization_balance(organic_matter_pct: float, crop_n_demand_kg_ha: float, bulk_density: float = 1.3, depth_cm: float = 30.0) -> Dict[str, float]:
    """Estimates annual soil N mineralization supply and net fertilizer N required."""
    om = float(organic_matter_pct)
    demand = float(crop_n_demand_kg_ha)
    bd = float(bulk_density)
    d = float(depth_cm)
    # Soil mass in kg/ha for layer: Area(10000 m^2) * depth(m) * density(kg/m^3)
    soil_mass_kg_ha = 10000.0 * (d / 100.0) * (bd * 1000.0)
    om_mass_kg_ha = soil_mass_kg_ha * (om / 100.0)
    # Soil OM is ~5% N, and ~2% of organic N is mineralized per growing season
    mineralized_n_kg_ha = om_mass_kg_ha * 0.05 * 0.02
    net_n_deficit = max(0.0, demand - mineralized_n_kg_ha)
    return {
        "mineralized_n_kg_ha": round(mineralized_n_kg_ha, 1),
        "crop_n_demand_kg_ha": round(demand, 1),
        "net_fertilizer_n_deficit_kg_ha": round(net_n_deficit, 1)
    }

def agronomy_irrigation_depth_schedule(soil_deficit_mm: float, application_efficiency_pct: float, irrigation_rate_mm_hr: float) -> Dict[str, float]:
    """Calculates gross irrigation water required, runtime in hours, and volumetric application."""
    deficit = float(soil_deficit_mm)
    eff = max(1.0, float(application_efficiency_pct)) / 100.0
    rate = max(0.1, float(irrigation_rate_mm_hr))
    gross_depth_mm = deficit / eff
    runtime_hr = gross_depth_mm / rate
    # 1 mm over 1 ha = 10 m^3
    volume_m3_ha = gross_depth_mm * 10.0
    return {
        "gross_irrigation_depth_mm": round(gross_depth_mm, 1),
        "system_runtime_hours": round(runtime_hr, 2),
        "volume_m3_per_hectare": round(volume_m3_ha, 1)
    }

def agronomy_leaf_area_index(foliage_area_m2: float, ground_area_m2: float, extinction_coeff_k: float = 0.6) -> Dict[str, float]:
    """Calculates Leaf Area Index (LAI) and canopy light interception fraction."""
    foliage = float(foliage_area_m2)
    ground = float(ground_area_m2)
    k = float(extinction_coeff_k)
    if ground <= 0.0:
        return {"lai": 0.0, "light_interception_pct": 0.0}
    lai = foliage / ground
    # Beer-Lambert law: fraction intercepted = 1 - exp(-k * LAI)
    interception = 1.0 - math.exp(-k * lai)
    return {
        "lai": round(lai, 2),
        "light_interception_pct": round(interception * 100.0, 1)
    }

def agronomy_sodium_adsorption_ratio(na_meq_l: float, ca_meq_l: float, mg_meq_l: float) -> Dict[str, Any]:
    """Calculates Sodium Adsorption Ratio SAR = [Na] / sqrt(([Ca] + [Mg]) / 2) and evaluates sodicity risk."""
    na = float(na_meq_l)
    ca = float(ca_meq_l)
    mg = float(mg_meq_l)
    denom = math.sqrt((ca + mg) / 2.0) if (ca + mg) > 0 else 0.0
    sar = na / denom if denom > 0 else 0.0
    if sar < 10.0:
        hazard = "Low Sodicity Hazard"
    elif sar < 18.0:
        hazard = "Medium Sodicity Hazard"
    elif sar < 26.0:
        hazard = "High Sodicity Hazard"
    else:
        hazard = "Very High Sodicity Hazard"
    return {
        "sar": round(sar, 2),
        "sodicity_hazard": hazard
    }

class AgronomyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "AgronomyRuntime",
    "agronomy_crop_water_requirement",
    "agronomy_growing_degree_days",
    "agronomy_fertilizer_rate",
    "agronomy_cation_exchange_capacity",
    "agronomy_soil_porosity",
    "agronomy_universal_soil_loss_equation",
    "agronomy_available_water_capacity",
    "agronomy_nitrogen_mineralization_balance",
    "agronomy_irrigation_depth_schedule",
    "agronomy_leaf_area_index",
    "agronomy_sodium_adsorption_ratio"
]
