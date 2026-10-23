"""Climate Domain Runtime: Meteorology, atmospheric thermodynamics, energy balance models, and radiative forcing."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED METEOROLOGY & ATMOSPHERIC METRICS
# ============================================================================

def climate_dew_point(temp_c: float, relative_humidity: float) -> float:
    """Calculates dew point temperature via Magnus-Tetens approximation."""
    a, b = 17.27, 237.7
    rh = max(0.01, min(100.0, float(relative_humidity)))
    alpha = ((a * float(temp_c)) / (b + float(temp_c))) + math.log(rh / 100.0)
    dp = (b * alpha) / (a - alpha)
    return round(dp, 2)

def climate_heat_index(temp_c: float, relative_humidity: float) -> float:
    """Calculates Steadman/Rothfusz Heat Index in Celsius."""
    t_f = float(temp_c) * 9.0 / 5.0 + 32.0
    rh = float(relative_humidity)
    if t_f < 80.0:
        hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))
    else:
        hi_f = (-42.379 + 2.04901523 * t_f + 10.14333127 * rh
                - 0.22475541 * t_f * rh - 0.00683783 * (t_f ** 2)
                - 0.05481717 * (rh ** 2) + 0.00122874 * (t_f ** 2) * rh
                + 0.00085282 * t_f * (rh ** 2) - 0.00000199 * (t_f ** 2) * (rh ** 2))
    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    return round(hi_c, 2)

def climate_wind_chill(temp_c: float, wind_kmh: float) -> float:
    """Calculates Environment Canada / NOAA Wind Chill index in Celsius."""
    t = float(temp_c)
    v = float(wind_kmh)
    if t > 10.0 or v < 4.8:
        return round(t, 2)
    wc = 13.12 + 0.6215 * t - 11.37 * (v ** 0.16) + 0.3965 * t * (v ** 0.16)
    return round(wc, 2)

def climate_vapor_pressure_deficit(temp_c: float, relative_humidity: float) -> float:
    """Calculates Vapor Pressure Deficit (VPD) in kilopascals (kPa)."""
    t = float(temp_c)
    rh = float(relative_humidity)
    # Tetens equation for saturation vapor pressure es (kPa)
    es = 0.61078 * math.exp((17.27 * t) / (t + 237.3))
    ea = es * (rh / 100.0)
    vpd = es - ea
    return round(vpd, 3)

def climate_barometric_altitude(altitude_m: float) -> float:
    """Estimates atmospheric pressure in hPa at given altitude using standard barometric formula."""
    p0 = 1013.25
    t0 = 288.15
    l = 0.0065
    g = 9.80665
    m = 0.0289644
    r = 8.3144598
    h = float(altitude_m)
    p = p0 * ((1.0 - (l * h) / t0) ** ((g * m) / (r * l)))
    return round(p, 2)

def climate_co2_equivalent(amount: float, gas_name: str) -> float:
    """Converts greenhouse gas mass into CO2-equivalent mass based on IPCC 100-year GWP."""
    gwp_100 = {
        "co2": 1.0,
        "ch4": 28.0,
        "n2o": 273.0,
        "sf6": 25200.0,
        "hfc-134a": 1530.0,
        "cf4": 7380.0
    }
    gas = gas_name.lower().strip()
    factor = gwp_100.get(gas, 1.0)
    return round(float(amount) * factor, 3)

def climate_radiative_forcing(co2_ppm: float, reference_ppm: float = 280.0, climate_sensitivity: float = 3.0) -> Dict[str, float]:
    """Calculates greenhouse gas radiative forcing (W/m2) and equilibrium temperature anomaly."""
    c = float(co2_ppm)
    c0 = float(reference_ppm)
    # Myhre et al. (1998) simplified expression: Delta F = 5.35 * ln(C / C0)
    delta_f = 5.35 * math.log(max(1.0, c) / max(1.0, c0))
    # Equilibrium climate sensitivity Delta T = lambda * Delta F where lambda = ECS / (5.35 * ln(2))
    lambda_param = climate_sensitivity / (5.35 * math.log(2.0))
    temp_anomaly = delta_f * lambda_param
    return {
        "co2_ppm": c,
        "radiative_forcing_w_m2": round(delta_f, 3),
        "temp_anomaly_c": round(temp_anomaly, 3)
    }

# ============================================================================
# 2. ADVANCED MODELS: ENERGY BALANCE & GEOSTROPHIC WINDS
# ============================================================================

def climate_energy_balance_step(temp_k: float, solar_constant: float = 1361.0, albedo: float = 0.30, emissivity: float = 0.612, heat_capacity: float = 4.0e8, dt_sec: float = 86400.0) -> float:
    """Euler integration step for 0-D planetary energy balance model: C * dT/dt = S0/4*(1-alpha) - epsilon*sigma*T^4."""
    sigma = 5.670374e-8
    absorbed = (solar_constant / 4.0) * (1.0 - albedo)
    emitted = emissivity * sigma * (temp_k ** 4)
    net_flux = absorbed - emitted
    new_t = temp_k + (net_flux / heat_capacity) * dt_sec
    return round(new_t, 3)

def climate_geostrophic_wind(pressure_gradient_pa_m: float, latitude_deg: float, air_density: float = 1.225) -> float:
    """Calculates geostrophic wind velocity balance between Coriolis and pressure gradient forces."""
    omega = 7.2921e-5 # Earth angular velocity rad/s
    phi = math.radians(abs(float(latitude_deg)))
    f_coriolis = 2.0 * omega * math.sin(phi)
    if f_coriolis == 0.0:
        return float("inf")
    vg = abs(pressure_gradient_pa_m) / (float(air_density) * f_coriolis)
    return round(vg, 2)

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class ClimateRuntime(DomainRuntime):
    """Unified runtime bridge for the Climate computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def dew_point(self, t: float, rh: float) -> float:
        return climate_dew_point(t, rh)
    def heat_index(self, t: float, rh: float) -> float:
        return climate_heat_index(t, rh)
    def wind_chill(self, t: float, w: float) -> float:
        return climate_wind_chill(t, w)
    def vpd(self, t: float, rh: float) -> float:
        return climate_vapor_pressure_deficit(t, rh)
    def pressure(self, alt: float) -> float:
        return climate_barometric_altitude(alt)
    def co2_eq(self, amount: float, gas: str) -> float:
        return climate_co2_equivalent(amount, gas)
    def forcing(self, ppm: float, ref_ppm: float = 280.0) -> Dict[str, float]:
        return climate_radiative_forcing(ppm, ref_ppm)
    def ebm_step(self, t_k: float, s0: float = 1361.0, albedo: float = 0.3) -> float:
        return climate_energy_balance_step(t_k, s0, albedo)
    def geostrophic_wind(self, grad: float, lat: float) -> float:
        return climate_geostrophic_wind(grad, lat)
