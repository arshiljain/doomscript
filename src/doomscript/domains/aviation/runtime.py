"""Aviation Domain Runtime: Pressure & density altitude, crosswind components, turn radius, banked stall speed, climb gradient, TAS, glide performance, holding pattern, and W&B."""
import math
from typing import Dict, Any, List
from doomscript.domains.base import DomainRuntime

def aviation_pressure_altitude(altimeter_setting_inhg: float, field_elevation_ft: float) -> float:
    """Calculates pressure altitude PA = Elevation + (29.92 - Altimeter) * 1000 in feet."""
    alt = float(altimeter_setting_inhg)
    elev = float(field_elevation_ft)
    pa = elev + ((29.92 - alt) * 1000.0)
    return round(pa, 1)

def aviation_density_altitude(pressure_altitude_ft: float, outside_air_temp_c: float) -> float:
    """Calculates density altitude DA = PA + 120 * (OAT - ISA_temp)."""
    pa = float(pressure_altitude_ft)
    oat = float(outside_air_temp_c)
    isa_temp = 15.0 - (1.98 * (pa / 1000.0))
    da = pa + (120.0 * (oat - isa_temp))
    return round(da, 1)

def aviation_wind_components(wind_speed_kts: float, wind_dir_deg: float, runway_heading_deg: float) -> Dict[str, float]:
    """Calculates crosswind and headwind components in knots."""
    speed = float(wind_speed_kts)
    angle_rad = math.radians(float(wind_dir_deg) - float(runway_heading_deg))
    crosswind = abs(speed * math.sin(angle_rad))
    headwind = speed * math.cos(angle_rad)
    return {"crosswind_kts": round(crosswind, 1), "headwind_kts": round(headwind, 1)}

def aviation_turn_radius(true_airspeed_kts: float, bank_angle_deg: float) -> float:
    """Calculates coordinated level turn radius R = V^2 / (g * tan(theta)) in feet."""
    tas_fps = float(true_airspeed_kts) * 1.68781  # knots to ft/s
    bank_rad = math.radians(abs(float(bank_angle_deg)))
    if bank_rad == 0.0:
        return float('inf')
    g = 32.174  # ft/s^2
    radius = (tas_fps ** 2) / (g * math.tan(bank_rad))
    return round(radius, 1)

def aviation_banked_stall_speed(vs0_clean_stall_kts: float, bank_angle_deg: float) -> float:
    """Calculates stall speed in a coordinated bank turn Vs_bank = Vs0 * sqrt(1 / cos(theta))."""
    vs0 = float(vs0_clean_stall_kts)
    bank_rad = math.radians(abs(float(bank_angle_deg)))
    cos_theta = math.cos(bank_rad)
    if cos_theta <= 0.0:
        return float('inf')
    load_factor = 1.0 / cos_theta
    vs_bank = vs0 * math.sqrt(load_factor)
    return round(vs_bank, 1)

def aviation_climb_gradient(rate_of_climb_fpm: float, true_airspeed_kts: float) -> float:
    """Calculates aircraft climb gradient percentage = (ROC / (TAS * 101.27)) * 100."""
    roc = float(rate_of_climb_fpm)
    tas = float(true_airspeed_kts)
    if tas <= 0.0:
        return 0.0
    gradient_pct = (roc / (tas * 101.2686)) * 100.0
    return round(gradient_pct, 2)

def aviation_tas_from_cas(cas_kts: float, pressure_alt_ft: float, oat_c: float) -> Dict[str, float]:
    """Calculates True Airspeed (TAS) from Calibrated Airspeed (CAS) using density ratio."""
    cas = float(cas_kts)
    pa = float(pressure_alt_ft)
    oat = float(oat_c)
    t_kelvin = oat + 273.15
    # Standard atmosphere pressure ratio P / P0
    p_ratio = (1.0 - 6.8755856e-6 * pa) ** 5.25588 if pa < 36089 else 0.22336 * math.exp(-(pa - 36089) / 20806)
    # Density ratio sigma = (P / P0) * (T0 / T)
    sigma = p_ratio * (288.15 / t_kelvin) if t_kelvin > 0 else 1.0
    sigma = max(0.01, sigma)
    tas = cas / math.sqrt(sigma)
    # Speed of sound a = 38.967 * sqrt(T_kelvin) in knots
    sound_speed_kts = 38.967 * math.sqrt(t_kelvin)
    mach = tas / sound_speed_kts if sound_speed_kts > 0 else 0.0
    return {
        "tas_kts": round(tas, 1),
        "mach_number": round(mach, 3),
        "density_ratio": round(sigma, 4),
        "speed_of_sound_kts": round(sound_speed_kts, 1)
    }

def aviation_glide_performance(glide_ratio: float, altitude_agl_ft: float, wind_component_kts: float = 0.0, descent_speed_kts: float = 65.0) -> Dict[str, float]:
    """Calculates glide distance in nautical miles (unpowered descent) and flight time."""
    gr = float(glide_ratio)
    alt = float(altitude_agl_ft)
    wind = float(wind_component_kts)
    v_glide = float(descent_speed_kts)
    if gr <= 0.0 or alt <= 0.0:
        return {"still_air_distance_nm": 0.0, "ground_distance_nm": 0.0, "glide_time_min": 0.0}
    # 1 NM = 6076.12 ft
    still_air_ft = gr * alt
    still_air_nm = still_air_ft / 6076.12
    glide_time_hr = still_air_nm / v_glide if v_glide > 0 else 0.0
    glide_time_min = glide_time_hr * 60.0
    ground_speed = max(0.0, v_glide + wind)
    ground_nm = ground_speed * glide_time_hr
    return {
        "still_air_distance_nm": round(still_air_nm, 2),
        "ground_distance_nm": round(ground_nm, 2),
        "glide_time_min": round(glide_time_min, 1)
    }

def aviation_holding_pattern_drift(wind_speed_kts: float, wind_dir_deg: float, inbound_course_deg: float, tas_kts: float) -> Dict[str, Any]:
    """Calculates holding pattern drift angles, outbound heading, and outbound timing."""
    ws = float(wind_speed_kts)
    wd = float(wind_dir_deg)
    crs = float(inbound_course_deg)
    tas = float(tas_kts)
    if tas <= 0:
        return {"inbound_wca_deg": 0.0, "outbound_heading_deg": round((crs + 180) % 360, 1), "outbound_timer_s": 60.0}
    # Crosswind component relative to inbound course
    angle_rad = math.radians(wd - crs)
    crosswind = ws * math.sin(angle_rad)
    headwind = ws * math.cos(angle_rad)
    # WCA = arcsin(crosswind / TAS)
    ratio = max(-1.0, min(1.0, crosswind / tas))
    inbound_wca = math.degrees(math.asin(ratio))
    # Outbound leg is opposite course with triple drift compensation
    reciprocal = (crs + 180.0) % 360.0
    outbound_wca = -3.0 * inbound_wca
    outbound_heading = (reciprocal + outbound_wca) % 360.0
    # Outbound timing adjustment for headwind/tailwind on inbound
    outbound_gs = tas - headwind
    outbound_timer = 60.0 * (tas / outbound_gs) if outbound_gs > 10 else 60.0
    return {
        "inbound_wca_deg": round(inbound_wca, 1),
        "outbound_heading_deg": round(outbound_heading, 1),
        "outbound_timer_s": round(outbound_timer, 1)
    }

def aviation_weight_and_balance(empty_weight_lbs: float, empty_arm_in: float, stations: List[Dict[str, float]]) -> Dict[str, Any]:
    """Calculates aircraft gross weight, total moment, and CG location."""
    ew = float(empty_weight_lbs)
    ea = float(empty_arm_in)
    tot_weight = ew
    tot_moment = ew * ea
    for st in stations:
        w = float(st.get("weight_lbs", st.get("weight", 0.0)))
        a = float(st.get("arm_in", st.get("arm", 0.0)))
        tot_weight += w
        tot_moment += (w * a)
    cg = tot_moment / tot_weight if tot_weight > 0 else 0.0
    return {
        "gross_weight_lbs": round(tot_weight, 1),
        "total_moment_lb_in": round(tot_moment, 1),
        "cg_inches": round(cg, 2)
    }

def aviation_critical_mach_drag_divergence(sweep_angle_deg: float, thickness_to_chord_ratio: float, design_cl: float = 0.3) -> Dict[str, float]:
    """Estimates drag divergence Mach number M_dd and critical Mach M_crit using Korn formula."""
    sweep_rad = math.radians(float(sweep_angle_deg))
    tc = float(thickness_to_chord_ratio)
    cl = float(design_cl)
    cos_sweep = math.cos(sweep_rad)
    if cos_sweep <= 0:
        return {"m_crit": 0.0, "m_dd": 0.0}
    # Korn formula: M_dd = (kappa_A / cos(sweep)) - (t/c / cos^2(sweep)) - (CL / (10 * cos^3(sweep)))
    kappa_a = 0.95  # typical modern supercritical airfoil technology factor
    m_dd = (kappa_a / cos_sweep) - (tc / (cos_sweep ** 2)) - (cl / (10.0 * (cos_sweep ** 3)))
    m_crit = m_dd - 0.08
    return {
        "m_crit": round(m_crit, 3),
        "m_drag_divergence": round(m_dd, 3)
    }

def aviation_standard_rate_turn(tas_kts: float) -> Dict[str, float]:
    """Calculates required bank angle and load factor for standard rate 3 deg/sec turn."""
    tas = float(tas_kts)
    # Omega = 3 deg/s = 0.05236 rad/s
    # tan(bank) = (V * omega) / g
    v_fps = tas * 1.68781
    g = 32.174
    tan_bank = (v_fps * 0.05236) / g
    bank_deg = math.degrees(math.atan(tan_bank))
    load_factor = 1.0 / math.cos(math.radians(bank_deg)) if math.cos(math.radians(bank_deg)) > 0 else 1.0
    return {
        "bank_angle_deg": round(bank_deg, 1),
        "load_factor_g": round(load_factor, 2)
    }

class AviationRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "AviationRuntime",
    "aviation_pressure_altitude",
    "aviation_density_altitude",
    "aviation_wind_components",
    "aviation_turn_radius",
    "aviation_banked_stall_speed",
    "aviation_climb_gradient",
    "aviation_tas_from_cas",
    "aviation_glide_performance",
    "aviation_holding_pattern_drift",
    "aviation_weight_and_balance",
    "aviation_critical_mach_drag_divergence",
    "aviation_standard_rate_turn"
]
