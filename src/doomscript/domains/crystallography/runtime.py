"""Crystallography Domain Runtime: Bragg diffraction, Miller indices, atomic packing factors, Scherrer size, systematic extinctions, and reciprocal lattices."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

AVOGADRO_CONSTANT = 6.02214076e23

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

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
        "sc": 0.52,
        "simple_cubic": 0.52,
        "bcc": 0.68,
        "body_centered_cubic": 0.68,
        "fcc": 0.74,
        "face_centered_cubic": 0.74,
        "hcp": 0.74,
        "hexagonal_close_packed": 0.74,
        "diamond": 0.34,
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

# ============================================================================
# 2. DEEPENED DIFFRACTION SELECTION RULES & NON-CUBIC LATTICES
# ============================================================================

def crystal_systematic_extinction_allowed(lattice_type: str, h: int, k: int, l: int) -> Dict[str, Any]:
    """Checks whether Bragg reflection (hkl) is allowed or systematically extinguished for BCC, FCC, or Diamond."""
    lt = lattice_type.strip().lower()
    hi, ki, li = int(h), int(k), int(l)
    allowed = False
    rule = ""

    if lt in ("sc", "primitive"):
        allowed = True
        rule = "All (h, k, l) allowed"
    elif lt in ("bcc", "body_centered"):
        allowed = ((hi + ki + li) % 2 == 0)
        rule = "h + k + l must be even"
    elif lt in ("fcc", "face_centered"):
        parities = [hi % 2, ki % 2, li % 2]
        allowed = (sum(parities) == 0 or sum(parities) == 3)
        rule = "h, k, l must be all unmixed (all even or all odd)"
    elif lt in ("diamond", "diamond_cubic"):
        parities = [hi % 2, ki % 2, li % 2]
        if sum(parities) == 3:
            allowed = True
        elif sum(parities) == 0:
            allowed = ((hi + ki + li) % 4 == 0)
        else:
            allowed = False
        rule = "All odd, or all even with h+k+l = 4n"
    else:
        allowed = True
        rule = "Unknown lattice type, assumed allowed"

    return {
        "allowed": allowed,
        "reflection": (hi, ki, li),
        "rule": rule
    }

def crystal_hexagonal_interplanar_spacing(a_nm: float, c_nm: float, h: int, k: int, l: int) -> float:
    """Calculates interplanar d-spacing for hexagonal crystal system 1/d^2 = 4/3 * (h^2 + hk + k^2)/a^2 + l^2/c^2."""
    a = float(a_nm)
    c = float(c_nm)
    hi, ki, li = int(h), int(k), int(l)
    if a <= 0 or c <= 0:
        return 0.0
    inv_d2 = (4.0 / 3.0) * ((hi**2 + hi*ki + ki**2) / (a**2)) + ((li**2) / (c**2))
    if inv_d2 <= 0:
        return 0.0
    return round(1.0 / math.sqrt(inv_d2), 5)

class CrystallographyRuntime(DomainRuntime):
    """Runtime engine for Crystallography domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def bragg(self, lam: float, d: float, n: int = 1) -> float:
        return crystal_bragg_angle(lam, d, n)
    def cubic_d(self, a: float, h: int, k: int, l: int) -> float:
        return crystal_cubic_interplanar_spacing(a, h, k, l)
    def apf(self, system: str) -> float:
        return crystal_atomic_packing_factor(system)
    def density(self, n: float, a: float, vc: float) -> float:
        return crystal_density(n, a, vc)
    def crystallite_size(self, lam: float, fwhm: float, theta: float, k: float = 0.9) -> float:
        return crystal_scherrer_crystallite_size(lam, fwhm, theta, k)
    def extinction_check(self, lattice: str, h: int, k: int, l: int) -> Dict[str, Any]:
        return crystal_systematic_extinction_allowed(lattice, h, k, l)
    def hex_d(self, a: float, c: float, h: int, k: int, l: int) -> float:
        return crystal_hexagonal_interplanar_spacing(a, c, h, k, l)
