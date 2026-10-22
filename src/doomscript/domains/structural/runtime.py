"""Structural Engineering Domain Runtime: Beam bending moments, elastic deflections, Euler column buckling, section modulus, Mohr's circle, and slenderness ratio."""
import math
from typing import Dict, Any

def structural_beam_max_moment(distributed_load_kn_m: float, span_length_m: float) -> float:
    """Calculates maximum bending moment M = (w * L^2) / 8 for simply supported beam under uniform load in kN*m."""
    w = float(distributed_load_kn_m)
    l = float(span_length_m)
    m = (w * (l ** 2)) / 8.0
    return round(m, 2)

def structural_beam_max_deflection(distributed_load_kn_m: float, span_length_m: float, elasticity_gpa: float, inertia_m4: float) -> float:
    """Calculates maximum deflection delta = (5 * w * L^4) / (384 * E * I) in millimeters."""
    w = float(distributed_load_kn_m) * 1000.0  # N/m
    l = float(span_length_m)
    e = float(elasticity_gpa) * 1e9            # Pa (N/m^2)
    i = float(inertia_m4)
    if e <= 0.0 or i <= 0.0:
        return 0.0
    delta_m = (5.0 * w * (l ** 4)) / (384.0 * e * i)
    return round(delta_m * 1000.0, 3)  # mm

def structural_euler_buckling_load(elasticity_gpa: float, inertia_m4: float, length_m: float, effective_length_factor_k: float = 1.0) -> float:
    """Calculates Euler critical column buckling load Pcr = (pi^2 * E * I) / (K * L)^2 in kiloNewtons (kN)."""
    e = float(elasticity_gpa) * 1e9  # Pa
    i = float(inertia_m4)
    l = float(length_m)
    k = float(effective_length_factor_k)
    effective_length = k * l
    if effective_length <= 0.0:
        return 0.0
    pcr_n = (math.pi ** 2 * e * i) / (effective_length ** 2)
    return round(pcr_n / 1000.0, 2)  # kN

def structural_section_modulus_rectangular(width_mm: float, height_mm: float) -> float:
    """Calculates elastic section modulus S = (b * h^2) / 6 in mm^3."""
    b = float(width_mm)
    h = float(height_mm)
    s = (b * (h ** 2)) / 6.0
    return round(s, 1)

def structural_mohr_circle_principal_stresses(sigma_x_mpa: float, sigma_y_mpa: float, tau_xy_mpa: float) -> Dict[str, float]:
    """Calculates 2D state of stress Mohr's circle principal stresses sigma_1, sigma_2 and max in-plane shear stress tau_max in MPa."""
    sx = float(sigma_x_mpa)
    sy = float(sigma_y_mpa)
    txy = float(tau_xy_mpa)
    avg = (sx + sy) / 2.0
    radius = math.sqrt(((sx - sy) / 2.0) ** 2 + (txy ** 2))
    return {
        "sigma_1_mpa": round(avg + radius, 2),
        "sigma_2_mpa": round(avg - radius, 2),
        "tau_max_mpa": round(radius, 2)
    }

def structural_slenderness_ratio(effective_length_m: float, radius_of_gyration_m: float) -> float:
    """Calculates column slenderness ratio lambda = (K * L) / r."""
    l = float(effective_length_m)
    r = float(radius_of_gyration_m)
    if r <= 0.0:
        return 0.0
    return round(l / r, 2)
