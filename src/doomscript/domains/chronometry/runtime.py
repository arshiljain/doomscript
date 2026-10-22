"""Chronometry Domain Runtime: Julian Day Number, GMST, Equation of Time, Special & General Relativistic time dilation, and Solar declination."""
import math
from typing import Dict, Any

SPEED_OF_LIGHT = 299792458.0  # m/s
G_CONST = 6.67430e-11

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
