"""Materials Science & Solid Mechanics Runtime: Stress-strain, Young's modulus, Mohr's circle, and thermal expansion."""
import math
from typing import Dict, Any

def materials_stress_strain(force_n: float, area_m2: float, delta_l: float, initial_l: float) -> Dict[str, float]:
    """Calculates engineering stress (Pa), strain (unitless), and Young's Modulus (Pa)."""
    f = float(force_n)
    a = float(area_m2)
    dl = float(delta_l)
    l0 = float(initial_l)
    stress = f / a if a != 0.0 else 0.0
    strain = dl / l0 if l0 != 0.0 else 0.0
    modulus = stress / strain if strain != 0.0 else 0.0
    return {
        "stress_pa": round(stress, 2),
        "strain": round(strain, 6),
        "youngs_modulus_gpa": round(modulus / 1e9, 3)
    }

def materials_mohrs_circle(sigma_x: float, sigma_y: float, tau_xy: float) -> Dict[str, float]:
    """Calculates 2D Mohr's Circle principal stresses (sigma1, sigma2) and maximum shear stress."""
    sx = float(sigma_x)
    sy = float(sigma_y)
    txy = float(tau_xy)
    center = (sx + sy) / 2.0
    radius = math.sqrt(((sx - sy) / 2.0) ** 2 + (txy ** 2))
    sigma1 = center + radius
    sigma2 = center - radius
    return {
        "center": round(center, 2),
        "radius": round(radius, 2),
        "sigma1": round(sigma1, 2),
        "sigma2": round(sigma2, 2),
        "tau_max": round(radius, 2)
    }

def materials_thermal_expansion(initial_length: float, linear_coeff: float, delta_temp_c: float) -> float:
    """Calculates change in length delta_L = L0 * alpha * delta_T."""
    l0 = float(initial_length)
    alpha = float(linear_coeff)
    dt = float(delta_temp_c)
    return round(l0 * alpha * dt, 6)

def materials_vickers_hardness(force_kgf: float, mean_diagonal_mm: float) -> float:
    """Calculates Vickers Hardness Number (HV) = 1.8544 * F / d^2."""
    f = float(force_kgf)
    d = float(mean_diagonal_mm)
    if d == 0.0:
        return 0.0
    return round(1.8544 * f / (d ** 2), 2)
