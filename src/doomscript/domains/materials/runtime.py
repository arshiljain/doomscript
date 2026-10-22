"""Materials Science & Solid Mechanics Runtime: Stress-strain, Mohr's circle, fracture mechanics, fatigue, and composite rule of mixtures."""
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
    return {
        "center": round(center, 2),
        "radius": round(radius, 2),
        "sigma1": round(center + radius, 2),
        "sigma2": round(center - radius, 2),
        "tau_max": round(radius, 2)
    }

def materials_thermal_expansion(initial_length: float, linear_coeff: float, delta_temp_c: float) -> float:
    """Calculates change in length delta_L = L0 * alpha * delta_T."""
    return round(float(initial_length) * float(linear_coeff) * float(delta_temp_c), 6)

def materials_stress_intensity(stress_mpa: float, crack_length_mm: float, geometry_y: float = 1.12) -> float:
    """Calculates Mode I stress intensity factor K_I = Y * sigma * sqrt(pi * a) in MPa*sqrt(m)."""
    s = float(stress_mpa)
    a_m = float(crack_length_mm) / 1000.0
    y = float(geometry_y)
    if a_m <= 0.0:
        return 0.0
    k1 = y * s * math.sqrt(math.pi * a_m)
    return round(k1, 3)

def materials_rule_of_mixtures(fiber_modulus_gpa: float, matrix_modulus_gpa: float, fiber_volume_fraction: float) -> Dict[str, float]:
    """Calculates composite longitudinal (E1) and transverse (E2) Young's modulus via Rule of Mixtures."""
    ef = float(fiber_modulus_gpa)
    em = float(matrix_modulus_gpa)
    vf = float(fiber_volume_fraction)
    vm = 1.0 - vf
    e1 = vf * ef + vm * em
    e2 = (ef * em) / (vm * ef + vf * em) if (vm * ef + vf * em) > 0 else 0.0
    return {"longitudinal_modulus_gpa": round(e1, 2), "transverse_modulus_gpa": round(e2, 2)}
