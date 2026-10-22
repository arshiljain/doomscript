"""Oceanography Domain Runtime: Seawater density, Coriolis parameter, wave dispersion, hydrostatic pressure, and Mackenzie sound speed."""
import math
from typing import Dict, Any

OMEGA_EARTH = 7.2921e-5  # rad/s

def ocean_seawater_density(temp_c: float, salinity_psu: float) -> float:
    """Calculates seawater density rho (kg/m^3) at atmospheric pressure using simplified UNESCO equation of state."""
    t = float(temp_c)
    s = float(salinity_psu)
    rho_fresh = 999.842594 + (6.793952e-2 * t) - (9.095290e-3 * (t**2)) + (1.001685e-4 * (t**3))
    density = rho_fresh + (0.824493 - 4.0899e-3 * t + 7.6438e-5 * (t**2)) * s - (5.72466e-3 - 1.0227e-4 * t) * (s**1.5) + (4.8314e-4 * (s**2))
    return round(density, 3)

def ocean_coriolis_parameter(latitude_deg: float) -> float:
    """Calculates planetary Coriolis frequency parameter f = 2 * Omega * sin(phi) in s^-1."""
    phi_rad = math.radians(float(latitude_deg))
    f = 2.0 * OMEGA_EARTH * math.sin(phi_rad)
    return float(f"{f:.7e}")

def ocean_gravity_wave_speed(wavelength_m: float, depth_m: float) -> Dict[str, float]:
    """Calculates surface gravity wave phase velocity c = sqrt((g * lambda / 2pi) * tanh(2pi * d / lambda))."""
    lam = float(wavelength_m)
    d = float(depth_m)
    g = 9.80665
    if lam <= 0.0 or d <= 0.0:
        return {"phase_velocity_m_s": 0.0, "regime": "invalid"}
    k = (2.0 * math.pi) / lam
    c = math.sqrt((g / k) * math.tanh(k * d))
    d_over_l = d / lam
    regime = "deep_water" if d_over_l > 0.5 else ("shallow_water" if d_over_l < 0.05 else "intermediate_water")
    return {"phase_velocity_m_s": round(c, 2), "regime": regime}

def ocean_hydrostatic_pressure(depth_m: float, avg_density_kg_m3: float = 1025.0) -> float:
    """Calculates hydrostatic gauge pressure P = rho * g * z in kiloPascals (kPa)."""
    z = float(depth_m)
    rho = float(avg_density_kg_m3)
    g = 9.80665
    p_kpa = (rho * g * z) / 1000.0
    return round(p_kpa, 2)

def ocean_sound_speed_mackenzie(temp_c: float, salinity_psu: float, depth_m: float) -> float:
    """Calculates speed of sound in seawater using Mackenzie (1981) empirical formulation."""
    t = float(temp_c)
    s = float(salinity_psu)
    d = float(depth_m)
    c = (1448.96 + 4.591 * t - 5.304e-2 * (t**2) + 2.374e-4 * (t**3) +
         1.340 * (s - 35.0) + 1.630e-2 * d + 1.675e-7 * (d**2) -
         1.025e-2 * t * (s - 35.0) - 7.139e-13 * t * (d**3))
    return round(c, 2)

def ocean_wind_stress(wind_speed_10m_m_s: float, drag_coeff: float = 0.0013, air_density_kg_m3: float = 1.22) -> float:
    """Calculates ocean surface wind shear stress tau = rho_air * C_d * U_10^2 in N/m^2."""
    u10 = float(wind_speed_10m_m_s)
    cd = float(drag_coeff)
    rho = float(air_density_kg_m3)
    tau = rho * cd * (u10 ** 2)
    return round(tau, 4)
