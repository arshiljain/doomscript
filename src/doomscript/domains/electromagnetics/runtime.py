"""Electromagnetics Domain Runtime: Maxwell equations, Biot-Savart, skin depth, Poynting vectors, RF coax impedance, plane wave attenuation, Faraday EMF, and transmission lines."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

MU_0 = 4.0 * math.pi * 1e-7
EPS_0 = 8.854187817e-12
SPEED_OF_LIGHT = 299792458.0

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def em_biot_savart_wire(current_amps: float, distance_m: float) -> float:
    """Calculates magnetic flux density B = (mu_0 * I) / (2 * pi * r) in Tesla."""
    i = float(current_amps)
    r = float(distance_m)
    if r <= 0.0:
        return 0.0
    b = (MU_0 * i) / (2.0 * math.pi * r)
    return float(f"{b:.6e}")

def em_skin_depth(frequency_hz: float, conductivity_s_m: float, rel_permeability: float = 1.0) -> float:
    """Calculates conductor skin depth delta = sqrt(1 / (pi * f * mu * sigma)) in meters."""
    f = float(frequency_hz)
    sigma = float(conductivity_s_m)
    ur = float(rel_permeability)
    if f <= 0.0 or sigma <= 0.0:
        return 0.0
    mu = MU_0 * ur
    delta = math.sqrt(1.0 / (math.pi * f * mu * sigma))
    return float(f"{delta:.6e}")

def em_poynting_vector_magnitude(e_field_v_m: float, h_field_a_m: float) -> float:
    """Calculates magnitude of instantaneous Poynting power flow vector S = E * H in W/m^2."""
    e = float(e_field_v_m)
    h = float(h_field_a_m)
    return round(e * h, 3)

def em_coaxial_characteristic_impedance(inner_radius_a: float, outer_radius_b: float, rel_permittivity_eps_r: float = 1.0) -> float:
    """Calculates coaxial cable characteristic impedance Z0 = (60 / sqrt(eps_r)) * ln(b / a) in Ohms."""
    a = float(inner_radius_a)
    b = float(outer_radius_b)
    eps_r = float(rel_permittivity_eps_r)
    if a <= 0.0 or b <= a or eps_r <= 0.0:
        return 0.0
    z0 = (60.0 / math.sqrt(eps_r)) * math.log(b / a)
    return round(z0, 2)

def em_plane_wave_attenuation(frequency_hz: float, conductivity_s_m: float, rel_permittivity: float = 1.0, rel_permeability: float = 1.0) -> float:
    """Calculates lossy dielectric plane wave attenuation constant alpha in Nepers/meter."""
    f = float(frequency_hz)
    sigma = float(conductivity_s_m)
    eps = EPS_0 * float(rel_permittivity)
    mu = MU_0 * float(rel_permeability)
    omega = 2.0 * math.pi * f
    if omega <= 0.0 or eps <= 0.0:
        return 0.0
    loss_factor = math.sqrt(1.0 + (sigma / (omega * eps)) ** 2)
    alpha = omega * math.sqrt(0.5 * mu * eps * (loss_factor - 1.0))
    return round(alpha, 4)

def em_faraday_induced_emf(n_turns: int, delta_flux_webers: float, delta_time_s: float) -> float:
    """Calculates Faraday-Lenz induced electromotive force EMF = -N * (dPhi / dt) in Volts."""
    n = int(n_turns)
    dphi = float(delta_flux_webers)
    dt = float(delta_time_s)
    if dt <= 0.0:
        return 0.0
    emf = -float(n) * (dphi / dt)
    return round(emf, 2)

# ============================================================================
# 2. DEEPENED RF TRANSMISSION LINES & PLASMA GYROKINETICS
# ============================================================================

def em_vswr_reflection(load_impedance_z_l: float, char_impedance_z_0: float = 50.0) -> Dict[str, float]:
    """Calculates voltage reflection coefficient gamma and Voltage Standing Wave Ratio (VSWR)."""
    zl = float(load_impedance_z_l)
    z0 = float(char_impedance_z_0)
    if (zl + z0) == 0.0:
        return {"reflection_coefficient": 1.0, "vswr": float("inf"), "return_loss_db": 0.0}
    gamma = abs((zl - z0) / (zl + z0))
    if gamma >= 0.9999:
        vswr = float("inf")
        rl = 0.0
    else:
        vswr = (1.0 + gamma) / (1.0 - gamma)
        rl = -20.0 * math.log10(gamma) if gamma > 0 else 100.0
    return {
        "reflection_coefficient": round(gamma, 4),
        "vswr": round(vswr, 3),
        "return_loss_db": round(rl, 2)
    }

def em_cyclotron_resonance(magnetic_field_tesla: float, charge_coulombs: float = 1.602e-19, mass_kg: float = 9.109e-31, velocity_m_s: float = 1e6) -> Dict[str, float]:
    """Calculates relativistic cyclotron gyrofrequency omega_c = q*B/m (rad/s) and Larmor radius r_L (m)."""
    b = float(magnetic_field_tesla)
    q = float(charge_coulombs)
    m = float(mass_kg)
    v = float(velocity_m_s)
    if m <= 0.0 or b <= 0.0:
        return {"gyrofrequency_rad_s": 0.0, "gyrofrequency_mhz": 0.0, "larmor_radius_mm": 0.0}
    omega = (abs(q) * b) / m
    freq_hz = omega / (2.0 * math.pi)
    r_larmor = (m * v) / (abs(q) * b)
    return {
        "gyrofrequency_rad_s": round(omega, 2),
        "gyrofrequency_mhz": round(freq_hz / 1e6, 3),
        "larmor_radius_mm": round(r_larmor * 1000.0, 4)
    }

def em_solenoid_inductance(n_turns: int, length_m: float, radius_m: float, rel_permeability: float = 1.0) -> float:
    """Calculates ideal long solenoid self-inductance L = (mu_0 * mu_r * N^2 * A) / l in Henries."""
    n = int(n_turns)
    l = float(length_m)
    r = float(radius_m)
    ur = float(rel_permeability)
    if l <= 0.0:
        return 0.0
    area = math.pi * (r ** 2)
    inductance = (MU_0 * ur * (n ** 2) * area) / l
    return float(f"{inductance:.6e}")

class ElectromagneticsRuntime(DomainRuntime):
    """Runtime engine for Electromagnetics domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def wire_b(self, i: float, r: float) -> float:
        return em_biot_savart_wire(i, r)
    def skin(self, f: float, sigma: float, ur: float = 1.0) -> float:
        return em_skin_depth(f, sigma, ur)
    def poynting(self, e: float, h: float) -> float:
        return em_poynting_vector_magnitude(e, h)
    def coax_z0(self, a: float, b: float, eps_r: float = 1.0) -> float:
        return em_coaxial_characteristic_impedance(a, b, eps_r)
    def wave_attenuation(self, f: float, sigma: float, eps_r: float = 1.0, ur: float = 1.0) -> float:
        return em_plane_wave_attenuation(f, sigma, eps_r, ur)
    def faraday(self, n: int, flux: float, dt: float) -> float:
        return em_faraday_induced_emf(n, flux, dt)
    def vswr(self, zl: float, z0: float = 50.0) -> Dict[str, float]:
        return em_vswr_reflection(zl, z0)
    def cyclotron(self, b: float, q: float = 1.602e-19, m: float = 9.109e-31, v: float = 1e6) -> Dict[str, float]:
        return em_cyclotron_resonance(b, q, m, v)
    def solenoid(self, n: int, l: float, r: float, ur: float = 1.0) -> float:
        return em_solenoid_inductance(n, l, r, ur)
