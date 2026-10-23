"""Astrophysics Domain Runtime: Black holes, stellar physics, Eddington limits, Jeans gravitational collapse, Hawking radiation, and cosmology."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

G_CONST = 6.67430e-11          # m^3 kg^-1 s^-2
SPEED_OF_LIGHT = 299792458.0   # m/s
SIGMA_SB = 5.670374419e-8      # W m^-2 K^-4
H_BAR = 1.054571817e-34        # J s
K_BOLTZMANN = 1.380649e-23     # J/K
SOLAR_MASS_KG = 1.98847e30     # kg
SOLAR_LUMINOSITY_W = 3.828e26  # Watts

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

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
    m_h = 1.6735575e-27
    if t <= 0.0 or n <= 0.0 or mu <= 0.0:
        return 0.0
    rho = n * mu * m_h
    sound_speed = math.sqrt((5.0 / 3.0) * K_BOLTZMANN * t / (mu * m_h))
    mj_kg = (math.pi / 6.0) * rho * ((math.pi * sound_speed**2 / (G_CONST * rho)) ** 1.5)
    return round(mj_kg / SOLAR_MASS_KG, 2)

def astro_friedmann_critical_density(hubble_constant_km_s_mpc: float = 70.0) -> float:
    """Calculates cosmological Friedmann critical density rho_c = 3 * H^2 / (8 * pi * G) in kg/m^3."""
    h_km_s_mpc = float(hubble_constant_km_s_mpc)
    h_si = (h_km_s_mpc * 1000.0) / 3.085677581e22
    rho_c = (3.0 * (h_si ** 2)) / (8.0 * math.pi * G_CONST)
    return float(f"{rho_c:.6e}")

# ============================================================================
# 2. DEEPENED RELATIVISTIC ASTROPHYSICS & QUANTUM BLACK HOLES
# ============================================================================

def astro_hawking_radiation(black_hole_mass_kg: float) -> Dict[str, float]:
    """Calculates Hawking radiation temperature T_H (K) and evaporation power (W)."""
    m = float(black_hole_mass_kg)
    if m <= 0:
        return {"hawking_temp_k": 0.0, "luminosity_watts": 0.0, "lifetime_years": 0.0}
    t_h = (H_BAR * (SPEED_OF_LIGHT ** 3)) / (8.0 * math.pi * G_CONST * m * K_BOLTZMANN)
    p_w = (H_BAR * (SPEED_OF_LIGHT ** 6)) / (15360.0 * math.pi * (G_CONST ** 2) * (m ** 2))
    t_evap_s = (5120.0 * math.pi * (G_CONST ** 2) * (m ** 3)) / (H_BAR * (SPEED_OF_LIGHT ** 4))
    t_evap_yr = t_evap_s / (365.25 * 86400.0)
    return {
        "hawking_temp_k": float(f"{t_h:.6e}"),
        "luminosity_watts": float(f"{p_w:.6e}"),
        "lifetime_years": float(f"{t_evap_yr:.6e}")
    }

def astro_einstein_radius(mass_kg: float, d_lens_kpc: float, d_source_kpc: float) -> float:
    """Calculates gravitational lensing angular Einstein radius theta_E in arcseconds."""
    m = float(mass_kg)
    dl = float(d_lens_kpc) * 3.085677581e19  # kpc to meters
    ds = float(d_source_kpc) * 3.085677581e19
    dls = ds - dl
    if dl <= 0 or ds <= dl or dls <= 0:
        return 0.0
    c = SPEED_OF_LIGHT
    theta_rad = math.sqrt((4.0 * G_CONST * m / (c ** 2)) * (dls / (dl * ds)))
    theta_arcsec = math.degrees(theta_rad) * 3600.0
    return round(theta_arcsec, 4)

def astro_stellar_lifetime_years(mass_solar: float) -> float:
    """Estimates main-sequence stellar nuclear burning lifetime tau ~ 10^10 * (M / M_sun)^(-2.5) in years."""
    m = float(mass_solar)
    if m <= 0:
        return 0.0
    tau = 1e10 * (m ** -2.5)
    return float(f"{tau:.4e}")

class AstrophysicsRuntime(DomainRuntime):
    """Runtime engine for Astrophysics domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def schwarzschild(self, m: float) -> float:
        return astro_schwarzschild_radius(m)
    def luminosity(self, r: float, t: float) -> float:
        return astro_stefan_boltzmann_luminosity(r, t)
    def eddington(self, m_sun: float) -> float:
        return astro_eddington_luminosity(m_sun)
    def hubble(self, d: float, h0: float = 70.0) -> float:
        return astro_hubble_velocity(d, h0)
    def jeans(self, t: float, n: float, mu: float = 2.3) -> float:
        return astro_jeans_mass(t, n, mu)
    def friedmann(self, h0: float = 70.0) -> float:
        return astro_friedmann_critical_density(h0)
    def hawking(self, m: float) -> Dict[str, float]:
        return astro_hawking_radiation(m)
    def einstein_radius(self, m: float, dl: float, ds: float) -> float:
        return astro_einstein_radius(m, dl, ds)
    def stellar_lifetime(self, m: float) -> float:
        return astro_stellar_lifetime_years(m)
