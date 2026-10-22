"""Electromagnetics Domain Runtime: Biot-Savart, skin depth, Poynting vector, coax impedance, plane wave attenuation, and Faraday induced EMF."""
import math
from typing import Dict, Any

MU_0 = 4.0 * math.pi * 1e-7
EPS_0 = 8.854187817e-12

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
