"""Astrophysics Domain Runtime: Schwarzschild radius, Stefan-Boltzmann luminosity, Eddington limit, Hubble velocity, and Friedmann density."""
import math
from typing import Dict, Any

G_CONST = 6.67430e-11          # m^3 kg^-1 s^-2
SPEED_OF_LIGHT = 299792458.0   # m/s
SIGMA_SB = 5.670374419e-8      # W m^-2 K^-4
SOLAR_MASS_KG = 1.98847e30     # kg
SOLAR_LUMINOSITY_W = 3.828e26  # Watts

def astro_schwarzschild_radius(mass_kg: float) -> float:
    """Calculates gravitational event horizon radius Rs = 2 * G * M / c^2 in meters."""
    m = float(mass_kg)
    if m <= 0.0:
        return 0.0
    rs = (2.0 * G_CONST * m) / (SPEED_OF_LIGHT ** 2)
    return round(rs, 3)

def astro_stefan_boltzmann_luminosity(radius_m: float, effective_temp_k: float) -> float:
    """Calculates stellar luminosity L = 4 * pi * R^2 * sigma * T^4 in Watts."""
    r = float(radius_m)
    t = float(effective_temp_k)
    if r <= 0.0 or t <= 0.0:
        return 0.0
    area = 4.0 * math.pi * (r ** 2)
    lum = area * SIGMA_SB * (t ** 4)
    return float(f"{lum:.6e}")

def astro_eddington_luminosity(mass_solar_masses: float) -> float:
    """Calculates Eddington critical accretion luminosity L_Edd = 1.26e38 * (M / M_sun) in ergs/s or 1.26e31 W."""
    m_sun = float(mass_solar_masses)
    if m_sun <= 0.0:
        return 0.0
    l_edd_watts = 1.26e31 * m_sun
    return float(f"{l_edd_watts:.6e}")

def astro_hubble_velocity(distance_mpc: float, hubble_constant: float = 70.0) -> float:
    """Calculates cosmic recessional velocity v = H0 * d in km/s."""
    d = float(distance_mpc)
    h0 = float(hubble_constant)
    return round(h0 * d, 2)

def astro_jeans_mass(temp_k: float, number_density_m3: float, mean_molecular_weight: float = 2.3) -> float:
    """Calculates Jeans gravitational collapse critical mass M_J in Solar Masses (M_sun)."""
    t = float(temp_k)
    n = float(number_density_m3)
    mu = float(mean_molecular_weight)
    k_b = 1.380649e-23
    m_h = 1.6735575e-27
    if t <= 0.0 or n <= 0.0 or mu <= 0.0:
        return 0.0
    rho = n * mu * m_h
    sound_speed = math.sqrt((5.0 / 3.0) * k_b * t / (mu * m_h))
    mj_kg = (math.pi / 6.0) * rho * ((math.pi * sound_speed**2 / (G_CONST * rho)) ** 1.5)
    return round(mj_kg / SOLAR_MASS_KG, 2)

def astro_friedmann_critical_density(hubble_constant_km_s_mpc: float = 70.0) -> float:
    """Calculates cosmological Friedmann critical density rho_c = 3 * H^2 / (8 * pi * G) in kg/m^3."""
    h_km_s_mpc = float(hubble_constant_km_s_mpc)
    # 1 Mpc = 3.085677581e22 m, 1 km = 1000 m
    h_si = (h_km_s_mpc * 1000.0) / 3.085677581e22
    rho_c = (3.0 * (h_si ** 2)) / (8.0 * math.pi * G_CONST)
    return float(f"{rho_c:.6e}")
