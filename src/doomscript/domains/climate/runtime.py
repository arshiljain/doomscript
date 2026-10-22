"""Climate Science Domain Runtime: Dew point, Heat index, Barometric pressure, and GHG GWP conversion."""
import math

def climate_dew_point(temp_c: float, rel_humidity: float) -> float:
    """Calculates dew point temperature in Celsius via the Magnus-Tetens approximation."""
    t = float(temp_c)
    rh = float(rel_humidity)
    if rh <= 0.0:
        return t
    a = 17.27
    b = 237.7
    alpha = ((a * t) / (b + t)) + math.log(rh / 100.0)
    return round((b * alpha) / (a - alpha), 2)

def climate_heat_index(temp_c: float, rel_humidity: float) -> float:
    """Calculates apparent temperature / heat index in Celsius using the NOAA regression."""
    t_f = float(temp_c) * 9.0 / 5.0 + 32.0
    rh = float(rel_humidity)
    if t_f < 80.0:
        hi_f = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))
    else:
        hi_f = (-42.379 + 2.04901523 * t_f + 10.14333127 * rh
                - 0.22475541 * t_f * rh - 0.00683783 * (t_f ** 2)
                - 0.05481717 * (rh ** 2) + 0.00122874 * (t_f ** 2) * rh
                + 0.00085282 * t_f * (rh ** 2) - 0.00000199 * (t_f ** 2) * (rh ** 2))
    hi_c = (hi_f - 32.0) * 5.0 / 9.0
    return round(hi_c, 2)

def climate_barometric_pressure(altitude_m: float, sea_level_pa: float = 101325.0) -> float:
    """Estimates atmospheric pressure (Pascals) at altitude (meters) via barometric formula."""
    h = float(altitude_m)
    p0 = float(sea_level_pa)
    # P = P0 * (1 - L*h/T0) ^ (g*M / (R*L))
    # Approximation for troposphere:
    return round(p0 * math.pow(1.0 - 0.0065 * h / 288.15, 5.25588), 2)

GWP_FACTORS = {
    "co2": 1.0,
    "carbon dioxide": 1.0,
    "ch4": 28.0,
    "methane": 28.0,
    "n2o": 265.0,
    "nitrous oxide": 265.0,
    "sf6": 23500.0,
    "sulfur hexafluoride": 23500.0
}

def climate_co2_equivalent(amount_kg: float, gas_name: str) -> float:
    """Converts mass of a greenhouse gas to CO2-equivalent kilograms using 100-year GWP."""
    amt = float(amount_kg)
    gas = str(gas_name).lower().strip()
    factor = GWP_FACTORS.get(gas, 1.0)
    return round(amt * factor, 2)
