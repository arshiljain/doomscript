"""Chronometry Domain Runtime: Julian Day Numbers, GMST, Equation of Time, Special & General Relativistic time dilation, GPS clock corrections, and celestial mechanics."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

SPEED_OF_LIGHT = 299792458.0  # m/s
G_CONST = 6.67430e-11

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def chrono_julian_day_number(year: int, month: int, day: int) -> float:
    """Calculates Julian Day Number (JDN) for Gregorian date at noon UTC."""
    y = int(year)
    m = int(month)
    d = int(day)
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100.0)
    b = 2 - a + math.floor(a / 4.0)
    jdn = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
    return round(jdn, 2)

def chrono_greenwich_mean_sidereal_time(jdn: float) -> float:
    """Calculates Greenwich Mean Sidereal Time (GMST) in hours for given JDN."""
    t = (float(jdn) - 2451545.0) / 36525.0
    gmst_sec = 24110.54841 + 8640184.812866 * t + 0.093104 * (t ** 2) - 6.2e-6 * (t ** 3)
    gmst_hours = (gmst_sec / 3600.0) % 24.0
    if gmst_hours < 0:
        gmst_hours += 24.0
    return round(gmst_hours, 4)

def chrono_equation_of_time(day_of_year: int) -> float:
    """Calculates Equation of Time (difference between solar and mean solar time) in minutes."""
    d = int(day_of_year)
    b = (2.0 * math.pi * (d - 81)) / 365.0
    eot = 9.87 * math.sin(2.0 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return round(eot, 2)

def chrono_relativistic_time_dilation(proper_time_seconds: float, velocity_m_s: float) -> float:
    """Calculates dilated time t = t0 / sqrt(1 - v^2/c^2) under special relativity."""
    t0 = float(proper_time_seconds)
    v = float(velocity_m_s)
    c = SPEED_OF_LIGHT
    if abs(v) >= c:
        return float('inf')
    factor = math.sqrt(1.0 - (v / c) ** 2)
    return round(t0 / factor, 8)

def chrono_gravitational_time_dilation(proper_time_seconds: float, mass_kg: float, radius_m: float) -> float:
    """Calculates gravitational time dilation t_f = t0 * sqrt(1 - 2*G*M / (r * c^2)) under General Relativity."""
    t0 = float(proper_time_seconds)
    m = float(mass_kg)
    r = float(radius_m)
    c = SPEED_OF_LIGHT
    if r <= 0.0:
        return 0.0
    term = (2.0 * G_CONST * m) / (r * (c ** 2))
    if term >= 1.0:
        return 0.0
    tf = t0 * math.sqrt(1.0 - term)
    return round(tf, 9)

def chrono_solar_declination(day_of_year: int) -> float:
    """Calculates solar declination angle delta in degrees for day of year (1-365)."""
    n = int(day_of_year)
    angle_rad = math.radians((360.0 / 365.0) * (n + 10))
    declination_deg = -23.44 * math.cos(angle_rad)
    return round(declination_deg, 2)

# ============================================================================
# 2. DEEPENED PRECISION RELATIVITY & CELESTIAL EPHEMERIS
# ============================================================================

def chrono_gps_relativistic_drift(altitude_km: float = 20180.0, orbital_speed_km_s: float = 3.874, earth_mass_kg: float = 5.972e24, earth_radius_km: float = 6371.0) -> Dict[str, float]:
    """Calculates daily net relativistic clock drift for satellite positioning (Special + General Relativity in microseconds/day)."""
    r_ground = earth_radius_km * 1000.0
    r_sat = (earth_radius_km + altitude_km) * 1000.0
    v_sat = orbital_speed_km_s * 1000.0
    c = SPEED_OF_LIGHT
    gm = G_CONST * earth_mass_kg

    # Special relativistic kinematic slowdown: -0.5 * (v/c)^2
    sr_fractional = -0.5 * ((v_sat / c) ** 2)
    # General relativistic gravitational blueshift: delta_Phi / c^2 = GM/c^2 * (1/r_ground - 1/r_sat)
    gr_fractional = (gm / (c ** 2)) * ((1.0 / r_ground) - (1.0 / r_sat))

    sec_per_day = 86400.0
    sr_us_day = sr_fractional * sec_per_day * 1e6
    gr_us_day = gr_fractional * sec_per_day * 1e6
    net_us_day = (sr_fractional + gr_fractional) * sec_per_day * 1e6

    return {
        "kinematic_drift_us_day": round(sr_us_day, 2),
        "gravitational_drift_us_day": round(gr_us_day, 2),
        "net_drift_us_day": round(net_us_day, 2)
    }

def chrono_sunrise_sunset_hours(day_of_year: int, latitude_deg: float) -> Dict[str, float]:
    """Estimates local solar sunrise and sunset hour angles and daylight duration in hours."""
    n = int(day_of_year)
    lat_rad = math.radians(float(latitude_deg))
    delta_deg = chrono_solar_declination(n)
    delta_rad = math.radians(delta_deg)

    # Solar zenith angle for standard atmospheric refraction = 90.833 deg
    cos_zenith = math.cos(math.radians(90.833))
    cos_omega = (cos_zenith - math.sin(lat_rad) * math.sin(delta_rad)) / (math.cos(lat_rad) * math.cos(delta_rad))
    if cos_omega > 1.0:
        # Polar night
        return {"sunrise_solar_hr": 12.0, "sunset_solar_hr": 12.0, "daylight_hours": 0.0}
    elif cos_omega < -1.0:
        # Midnight sun
        return {"sunrise_solar_hr": 0.0, "sunset_solar_hr": 24.0, "daylight_hours": 24.0}

    omega_deg = math.degrees(math.acos(cos_omega))
    daylight_hrs = (2.0 * omega_deg) / 15.0
    sunrise = 12.0 - (omega_deg / 15.0)
    sunset = 12.0 + (omega_deg / 15.0)
    return {
        "sunrise_solar_hr": round(sunrise, 2),
        "sunset_solar_hr": round(sunset, 2),
        "daylight_hours": round(daylight_hrs, 2)
    }

class ChronometryRuntime(DomainRuntime):
    """Runtime engine for Chronometry domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def jdn(self, y: int, m: int, d: int) -> float:
        return chrono_julian_day_number(y, m, d)
    def gmst(self, jdn: float) -> float:
        return chrono_greenwich_mean_sidereal_time(jdn)
    def eot(self, d: int) -> float:
        return chrono_equation_of_time(d)
    def special_relativity(self, t0: float, v: float) -> float:
        return chrono_relativistic_time_dilation(t0, v)
    def general_relativity(self, t0: float, m: float, r: float) -> float:
        return chrono_gravitational_time_dilation(t0, m, r)
    def solar_declination(self, d: int) -> float:
        return chrono_solar_declination(d)
    def gps_drift(self, alt: float = 20180.0, v: float = 3.874) -> Dict[str, float]:
        return chrono_gps_relativistic_drift(alt, v)
    def daylight(self, d: int, lat: float) -> Dict[str, float]:
        return chrono_sunrise_sunset_hours(d, lat)
