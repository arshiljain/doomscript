"""Materials Science & Solid Mechanics Runtime: Stress-strain, Mohr's circle, fracture mechanics, composites, yield criteria (Tresca/von Mises), Ramberg-Osgood, Johnson-Cook, and DBTT."""
import math
from typing import Dict, Any, List
from doomscript.domains.base import DomainRuntime

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

def materials_tresca_von_mises_yield(sigma1: float, sigma2: float, sigma3: float, yield_strength_sy_mpa: float) -> Dict[str, Any]:
    """Evaluates Tresca and von Mises yield criteria and factors of safety."""
    s1 = float(sigma1)
    s2 = float(sigma2)
    s3 = float(sigma3)
    sy = float(yield_strength_sy_mpa)
    tresca = max(abs(s1 - s2), abs(s2 - s3), abs(s3 - s1))
    vm = math.sqrt(0.5 * ((s1 - s2) ** 2 + (s2 - s3) ** 2 + (s3 - s1) ** 2))
    fos_tresca = sy / tresca if tresca > 0 else float('inf')
    fos_vm = sy / vm if vm > 0 else float('inf')
    return {
        "tresca_stress_mpa": round(tresca, 2),
        "von_mises_stress_mpa": round(vm, 2),
        "fos_tresca": round(fos_tresca, 2),
        "fos_von_mises": round(fos_vm, 2),
        "has_yielded": vm >= sy
    }

def materials_ramberg_osgood_strain(stress_mpa: float, youngs_modulus_gpa: float, alpha: float, yield_offset_mpa: float, hardening_n: float) -> Dict[str, float]:
    """Calculates elastoplastic strain from Ramberg-Osgood power law: eps = sigma/E + alpha*(sigma0/E)*(sigma/sigma0)^n."""
    s = float(stress_mpa)
    e = float(youngs_modulus_gpa) * 1000.0  # GPa to MPa
    a = float(alpha)
    s0 = float(yield_offset_mpa)
    n = float(hardening_n)
    if e <= 0 or s0 <= 0:
        return {"total_strain": 0.0, "elastic_strain": 0.0, "plastic_strain": 0.0}
    eps_e = s / e
    ratio = max(0.0, s / s0)
    eps_p = a * (s0 / e) * (ratio ** n)
    eps_tot = eps_e + eps_p
    return {
        "total_strain": round(eps_tot, 6),
        "elastic_strain": round(eps_e, 6),
        "plastic_strain": round(eps_p, 6)
    }

def materials_johnson_cook_flow_stress(plastic_strain: float, strain_rate: float, temp_c: float,
                                       a_mpa: float, b_mpa: float, n_exp: float, c_rate: float, m_thermal: float,
                                       t_room_c: float = 20.0, t_melt_c: float = 1500.0, ref_rate: float = 1.0) -> Dict[str, float]:
    """Calculates dynamic flow stress using Johnson-Cook constitutive plasticity model."""
    ep = max(0.0, float(plastic_strain))
    edot = max(1e-6, float(strain_rate))
    t = float(temp_c)
    a = float(a_mpa)
    b = float(b_mpa)
    n = float(n_exp)
    c = float(c_rate)
    m = float(m_thermal)
    tr = float(t_room_c)
    tm = float(t_melt_c)
    edot0 = float(ref_rate)

    strain_hardening = a + b * (ep ** n)
    rate_sensitivity = 1.0 + c * math.log(max(1.0, edot / edot0))
    t_star = max(0.0, min(1.0, (t - tr) / (tm - tr))) if tm > tr else 0.0
    thermal_softening = 1.0 - (t_star ** m)
    flow_stress = strain_hardening * rate_sensitivity * thermal_softening
    return {
        "flow_stress_mpa": round(max(0.0, flow_stress), 2),
        "strain_hardening_term": round(strain_hardening, 2),
        "rate_term": round(rate_sensitivity, 3),
        "thermal_softening_term": round(thermal_softening, 3)
    }

def materials_charpy_dbtt_hyperbolic(temperatures_c: List[float], energies_j: List[float]) -> Dict[str, float]:
    """Fits Charpy V-Notch impact energy curve and estimates Ductile-to-Brittle Transition Temperature."""
    if len(temperatures_c) != len(energies_j) or not temperatures_c:
        return {"upper_shelf_energy_j": 0.0, "lower_shelf_energy_j": 0.0, "dbtt_c": 0.0}
    use = max(float(e) for e in energies_j)
    lse = min(float(e) for e in energies_j)
    mid_energy = (use + lse) / 2.0
    # Interpolate temperature closest to mid_energy
    best_temp = float(temperatures_c[0])
    min_diff = float('inf')
    for t, e in zip(temperatures_c, energies_j):
        diff = abs(float(e) - mid_energy)
        if diff < min_diff:
            min_diff = diff
            best_temp = float(t)
    return {
        "upper_shelf_energy_j": round(use, 1),
        "lower_shelf_energy_j": round(lse, 1),
        "mid_shelf_energy_j": round(mid_energy, 1),
        "estimated_dbtt_c": round(best_temp, 1)
    }

def materials_halpin_tsai_short_fiber(fiber_modulus_gpa: float, matrix_modulus_gpa: float, fiber_vol_fraction: float, aspect_ratio_l_over_d: float) -> Dict[str, float]:
    """Calculates Halpin-Tsai aligned short fiber composite longitudinal and transverse modulus."""
    ef = float(fiber_modulus_gpa)
    em = float(matrix_modulus_gpa)
    vf = float(fiber_vol_fraction)
    xi = 2.0 * float(aspect_ratio_l_over_d)  # For longitudinal modulus
    eta_l = (ef / em - 1.0) / (ef / em + xi) if (ef / em + xi) != 0 else 0.0
    e11 = em * (1.0 + xi * eta_l * vf) / (1.0 - eta_l * vf)
    # Transverse: xi = 2.0
    eta_t = (ef / em - 1.0) / (ef / em + 2.0) if (ef / em + 2.0) != 0 else 0.0
    e22 = em * (1.0 + 2.0 * eta_t * vf) / (1.0 - eta_t * vf)
    return {
        "longitudinal_modulus_gpa": round(e11, 2),
        "transverse_modulus_gpa": round(e22, 2)
    }

def materials_brinell_hardness_conversion(hb_value: float) -> Dict[str, float]:
    """Converts Brinell Hardness (HB) to Vickers (HV), Rockwell C (HRC), and estimated UTS (MPa)."""
    hb = float(hb_value)
    uts_mpa = 3.45 * hb
    # Empirical ASTM correlations
    hv = hb * 1.05
    hrc = (hb - 100.0) / 10.0 if hb >= 200 else 0.0
    return {
        "brinell_hb": round(hb, 1),
        "vickers_hv": round(hv, 1),
        "rockwell_hrc": round(max(0.0, hrc), 1),
        "estimated_uts_mpa": round(uts_mpa, 1)
    }

class MaterialsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "MaterialsRuntime",
    "materials_stress_strain",
    "materials_mohrs_circle",
    "materials_thermal_expansion",
    "materials_stress_intensity",
    "materials_rule_of_mixtures",
    "materials_tresca_von_mises_yield",
    "materials_ramberg_osgood_strain",
    "materials_johnson_cook_flow_stress",
    "materials_charpy_dbtt_hyperbolic",
    "materials_halpin_tsai_short_fiber",
    "materials_brinell_hardness_conversion"
]
