"""Crystallography Domain Runtime: Bragg diffraction, cubic interplanar spacing, APF, density, Scherrer crystallite size, and FCC selection rules."""
import math
from typing import Dict, Any

AVOGADRO_CONSTANT = 6.02214076e23

def crystal_bragg_angle(wavelength_nm: float, d_spacing_nm: float, diffraction_order_n: int = 1) -> float:
    """Calculates Bragg diffraction glancing angle theta = arcsin(n * lambda / (2 * d)) in degrees."""
    lam = float(wavelength_nm)
    d = float(d_spacing_nm)
    n = int(diffraction_order_n)
    if d <= 0.0:
        return 0.0
    sin_theta = (n * lam) / (2.0 * d)
    if sin_theta > 1.0 or sin_theta < -1.0:
        return 0.0
    theta_rad = math.asin(sin_theta)
    return round(math.degrees(theta_rad), 3)

def crystal_cubic_interplanar_spacing(lattice_parameter_a_nm: float, h: int, k: int, l: int) -> float:
    """Calculates interplanar d-spacing for cubic lattice d_hkl = a / sqrt(h^2 + k^2 + l^2) in nm."""
    a = float(lattice_parameter_a_nm)
    denom = math.sqrt(int(h)**2 + int(k)**2 + int(l)**2)
    if denom == 0.0:
        return 0.0
    return round(a / denom, 5)

def crystal_atomic_packing_factor(crystal_system: str) -> float:
    """Returns standard Atomic Packing Factor (APF) for common unit cell geometries."""
    sys_clean = crystal_system.strip().lower()
    apf_map = {
        "sc": 0.524,
        "simple_cubic": 0.524,
        "bcc": 0.680,
        "body_centered_cubic": 0.680,
        "fcc": 0.740,
        "face_centered_cubic": 0.740,
        "hcp": 0.740,
        "hexagonal_close_packed": 0.740,
        "diamond": 0.340,
    }
    return apf_map.get(sys_clean, 0.0)

def crystal_density(atoms_per_unit_cell: float, atomic_weight_g_mol: float, unit_cell_volume_cm3: float) -> float:
    """Calculates theoretical crystal density rho = (n * A) / (Vc * Na) in g/cm^3."""
    n = float(atoms_per_unit_cell)
    a = float(atomic_weight_g_mol)
    vc = float(unit_cell_volume_cm3)
    if vc <= 0.0:
        return 0.0
    rho = (n * a) / (vc * AVOGADRO_CONSTANT)
    return round(rho, 3)

def crystal_scherrer_crystallite_size(wavelength_nm: float, fwhm_rad: float, theta_deg: float, shape_factor_k: float = 0.9) -> float:
    """Calculates mean crystallite domain size tau = (K * lambda) / (beta * cos(theta)) in nm."""
    lam = float(wavelength_nm)
    beta = float(fwhm_rad)
    theta_rad = math.radians(float(theta_deg))
    k = float(shape_factor_k)
    denom = beta * math.cos(theta_rad)
    if denom <= 0.0:
        return 0.0
    tau = (k * lam) / denom
    return round(tau, 2)
