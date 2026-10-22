"""Aviation Domain Runtime: Pressure & density altitude, crosswind components, turn radius, banked stall speed, and climb gradient."""
import math
from typing import Dict, Any

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
