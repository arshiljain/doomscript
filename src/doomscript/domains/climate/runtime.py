"""Climate & Meteorology Domain Runtime: Dew point, Heat index, Wind chill, Solar radiation, and GHG accounting."""
import math
from typing import Dict, Any, List

def climate_dew_point(temp_c: float, relative_humidity: float) -> float:
    """Calculates dew point (Celsius) using Magnus-Tetens approximation."""
    t = float(temp_c)
    rh = max(0.01, min(100.0, float(relative_humidity)))
    a = 17.27
    b = 237.7
    alpha = ((a * t) / (b + t)) + math.log(rh / 100.0)
    return round((b * alpha) / (a - alpha), 2)

def climate_heat_index(temp_c: float, relative_humidity: float) -> float:
    """Calculates Steadman Heat Index ('feels like') temperature in Celsius."""
    t_f = float(temp_c) * 9.0 / 5.0 + 32.0
    rh = float(relative_humidity)
    if t_f < 80.0:
        return round(float(temp_c), 2)
    hi = -42.379 + 2.04901523*t_f + 10.14333127*rh - 0.22475541*t_f*rh          - 0.00683783*(t_f**2) - 0.05481717*(rh**2) + 0.00122874*(t_f**2)*rh          + 0.00085282*t_f*(rh**2) - 0.00000199*(t_f**2)*(rh**2)
    return round((hi - 32.0) * 5.0 / 9.0, 2)

def climate_wind_chill(temp_c: float, wind_kmh: float) -> float:
    """Calculates Wind Chill equivalent temperature (NWS formula) in Celsius."""
    t = float(temp_c)
    v = float(wind_kmh)
    if t > 10.0 or v < 4.8:
        return round(t, 2)
    wc = 13.12 + 0.6215 * t - 11.37 * (v ** 0.16) + 0.3965 * t * (v ** 0.16)
    return round(wc, 2)

def climate_vapor_pressure_deficit(temp_c: float, relative_humidity: float) -> float:
    """Calculates Vapor Pressure Deficit (VPD) in kPa: SVP - AVP."""
    t = float(temp_c)
    rh = float(relative_humidity)
    # Saturated vapor pressure (Tetens formula in kPa)
    svp = 0.61078 * math.exp((17.27 * t) / (t + 237.3))
    avp = svp * (rh / 100.0)
    return round(svp - avp, 3)

def climate_barometric_altitude(altitude_m: float) -> float:
    """Calculates barometric atmospheric pressure (Pa) at given altitude using standard lapse rate."""
    h = float(altitude_m)
    p0 = 101325.0
    t0 = 288.15
    l = 0.0065
    return round(p0 * ((1.0 - (l * h) / t0) ** 5.25588), 2)

def climate_co2_equivalent(amount: float, gas_name: str) -> float:
    """Converts mass of a greenhouse gas to CO2 equivalent (IPCC AR6 100-year GWP)."""
    gwp_map = {
        "co2": 1.0, "carbon_dioxide": 1.0,
        "ch4": 28.0, "methane": 28.0,
        "n2o": 265.0, "nitrous_oxide": 265.0,
        "sf6": 23500.0,
        "hfc-134a": 1300.0
    }
    gwp = gwp_map.get(str(gas_name).lower(), 1.0)
    return round(float(amount) * gwp, 2)

def climate_radiative_forcing(co2_ppm: float, reference_ppm: float = 280.0, climate_sensitivity: float = 3.0) -> Dict[str, float]:
    """Calculates radiative forcing delta_F (W/m^2) and projected equilibrium surface warming delta_T (C)."""
    c = float(co2_ppm)
    c0 = float(reference_ppm)
    if c <= 0 or c0 <= 0:
        return {"radiative_forcing_w_m2": 0.0, "temp_anomaly_c": 0.0}
    # delta_F = 5.35 * ln(C / C0)
    delta_f = 5.35 * math.log(c / c0)
    # 3.7 W/m^2 corresponds to doubling of CO2
    lambda_param = float(climate_sensitivity) / 3.7
    delta_t = delta_f * lambda_param
    return {"radiative_forcing_w_m2": round(delta_f, 2), "temp_anomaly_c": round(delta_t, 2)}
