"""Optics Domain Runtime: Thin lens equation, Snell's law, Fresnel reflectance, Rayleigh resolution, Brewster angle, and Fiber NA."""
import math
from typing import Dict, Any

def optics_thin_lens(focal_length_mm: float, object_distance_mm: float) -> Dict[str, float]:
    """Calculates image distance d_i = (f * d_o) / (d_o - f) and magnification M = -d_i / d_o using thin lens equation."""
    f = float(focal_length_mm)
    do = float(object_distance_mm)
    if abs(do - f) < 1e-6:
        return {"image_distance_mm": float("inf"), "magnification": float("inf")}
    di = (f * do) / (do - f)
    mag = -di / do if do != 0.0 else 0.0
    return {"image_distance_mm": round(di, 2), "magnification": round(mag, 3)}

def optics_snell_refraction(n1: float, n2: float, incident_angle_deg: float) -> Dict[str, Any]:
    """Calculates angle of refraction using Snell's Law n1 * sin(theta1) = n2 * sin(theta2)."""
    n1_v = float(n1)
    n2_v = float(n2)
    theta1_rad = math.radians(float(incident_angle_deg))
    if n2_v <= 0.0:
        return {"refracted_angle_deg": 0.0, "total_internal_reflection": False}
    sin_theta2 = (n1_v / n2_v) * math.sin(theta1_rad)
    if sin_theta2 > 1.0:
        crit_angle = math.degrees(math.asin(n2_v / n1_v)) if n1_v >= n2_v else 0.0
        return {"refracted_angle_deg": 90.0, "total_internal_reflection": True, "critical_angle_deg": round(crit_angle, 2)}
    theta2_deg = math.degrees(math.asin(sin_theta2))
    return {"refracted_angle_deg": round(theta2_deg, 2), "total_internal_reflection": False}

def optics_fresnel_reflectance(n1: float, n2: float) -> float:
    """Calculates normal incidence Fresnel reflection coefficient R = ((n1 - n2) / (n1 + n2))^2."""
    n1_v = float(n1)
    n2_v = float(n2)
    denom = n1_v + n2_v
    if denom <= 0.0:
        return 0.0
    r = ((n1_v - n2_v) / denom) ** 2
    return round(r, 4)

def optics_rayleigh_resolution(wavelength_nm: float, numerical_aperture: float) -> float:
    """Calculates Abbe / Rayleigh optical diffraction resolution limit d = 0.61 * lambda / NA in nm."""
    lam = float(wavelength_nm)
    na = float(numerical_aperture)
    if na <= 0.0:
        return 0.0
    d = (0.61 * lam) / na
    return round(d, 2)

def optics_diffraction_grating(lines_per_mm: float, order_m: int, wavelength_nm: float) -> float:
    """Calculates diffraction angle theta = arcsin(m * lambda / d) in degrees for grating with spacing d."""
    lines = float(lines_per_mm)
    m = int(order_m)
    lam = float(wavelength_nm)
    if lines <= 0.0:
        return 0.0
    d_nm = (1.0 / lines) * 1e6  # mm to nm
    sin_theta = (m * lam) / d_nm
    if sin_theta > 1.0 or sin_theta < -1.0:
        return 0.0
    theta_deg = math.degrees(math.asin(sin_theta))
    return round(theta_deg, 2)

def optics_brewster_angle(n1: float, n2: float) -> float:
    """Calculates Brewster polarizing polarization angle theta_B = arctan(n2 / n1) in degrees."""
    n1_v = float(n1)
    n2_v = float(n2)
    if n1_v <= 0.0:
        return 0.0
    theta_rad = math.atan(n2_v / n1_v)
    return round(math.degrees(theta_rad), 2)

def optics_fiber_numerical_aperture(n_core: float, n_cladding: float) -> Dict[str, float]:
    """Calculates optical fiber Numerical Aperture NA = sqrt(n_core^2 - n_clad^2) and acceptance half-angle."""
    n1 = float(n_core)
    n2 = float(n_cladding)
    if n1 <= n2:
        return {"numerical_aperture": 0.0, "acceptance_half_angle_deg": 0.0}
    na = math.sqrt(n1**2 - n2**2)
    alpha_rad = math.asin(min(1.0, na))
    return {"numerical_aperture": round(na, 4), "acceptance_half_angle_deg": round(math.degrees(alpha_rad), 2)}
