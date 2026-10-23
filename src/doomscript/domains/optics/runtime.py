"""Optics Domain Runtime: Geometrical and wave optics, ray transfer matrices, thin films, Gaussian beams, and aberrations."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED GEOMETRICAL & WAVE OPTICS
# ============================================================================

def optics_thin_lens(focal_length_mm: float, object_distance_mm: float) -> Dict[str, float]:
    """Calculates thin lens image distance and transverse magnification via Gaussian lens formula."""
    f = float(focal_length_mm)
    do = float(object_distance_mm)
    if do == f:
        return {"image_distance_mm": float("inf"), "magnification": float("inf"), "is_real": False}
    di = (f * do) / (do - f)
    mag = -di / do
    return {
        "image_distance_mm": round(di, 2),
        "magnification": round(mag, 3),
        "is_real": di > 0
    }

def optics_snell_refraction(n1: float, n2: float, incident_angle_deg: float) -> Dict[str, Any]:
    """Calculates angle of refraction via Snell's Law and checks for total internal reflection."""
    n1 = float(n1)
    n2 = float(n2)
    theta1_rad = math.radians(float(incident_angle_deg))
    sin_theta2 = (n1 / n2) * math.sin(theta1_rad)
    if abs(sin_theta2) > 1.0:
        crit_angle = math.degrees(math.asin(n2 / n1)) if n1 > n2 else 0.0
        return {
            "total_internal_reflection": True,
            "refracted_angle_deg": None,
            "critical_angle_deg": round(crit_angle, 2)
        }
    theta2_rad = math.asin(sin_theta2)
    return {
        "total_internal_reflection": False,
        "refracted_angle_deg": round(math.degrees(theta2_rad), 2)
    }

def optics_fresnel_reflectance(n1: float, n2: float) -> float:
    """Calculates Fresnel normal-incidence reflectance R = ((n1 - n2) / (n1 + n2))^2."""
    n1, n2 = float(n1), float(n2)
    r = ((n1 - n2) / (n1 + n2)) ** 2
    return round(r, 4)

def optics_rayleigh_resolution(wavelength_nm: float, numerical_aperture: float) -> float:
    """Calculates Rayleigh optical diffraction resolution limit d = 0.61 * lambda / NA."""
    return round(0.61 * float(wavelength_nm) / float(numerical_aperture), 2)

def optics_diffraction_grating(lines_per_mm: float, order_m: int, wavelength_nm: float) -> float:
    """Calculates diffraction grating deflection angle in degrees: d * sin(theta) = m * lambda."""
    d_nm = (1.0 / float(lines_per_mm)) * 1e6
    sin_theta = (int(order_m) * float(wavelength_nm)) / d_nm
    if abs(sin_theta) > 1.0:
        return float("nan")
    return round(math.degrees(math.asin(sin_theta)), 2)

def optics_brewster_angle(n1: float, n2: float) -> float:
    """Calculates Brewster polarizing angle: theta_B = arctan(n2 / n1)."""
    return round(math.degrees(math.atan(float(n2) / float(n1))), 2)

def optics_fiber_numerical_aperture(n_core: float, n_cladding: float) -> Dict[str, float]:
    """Calculates optical fiber numerical aperture (NA) and maximum acceptance half-angle."""
    na = math.sqrt(max(0.0, float(n_core)**2 - float(n_cladding)**2))
    theta_max = math.degrees(math.asin(min(1.0, na)))
    return {
        "numerical_aperture": round(na, 4),
        "acceptance_angle_deg": round(theta_max, 2)
    }

# ============================================================================
# 2. RAY TRANSFER MATRIX ANALYSIS (ABCD MATRIX)
# ============================================================================

def optics_abcd_free_space(d_mm: float) -> List[List[float]]:
    """Generates ABCD matrix for free-space propagation of distance d: [[1, d], [0, 1]]."""
    return [[1.0, float(d_mm)], [0.0, 1.0]]

def optics_abcd_thin_lens(f_mm: float) -> List[List[float]]:
    """Generates ABCD matrix for thin lens with focal length f: [[1, 0], [-1/f, 1]]."""
    return [[1.0, 0.0], [-1.0 / float(f_mm), 1.0]]

def optics_abcd_multiply(m1: List[List[float]], m2: List[List[float]]) -> List[List[float]]:
    """Multiplies two 2x2 ray transfer matrices: M = M1 * M2."""
    return [
        [m1[0][0]*m2[0][0] + m1[0][1]*m2[1][0], m1[0][0]*m2[0][1] + m1[0][1]*m2[1][1]],
        [m1[1][0]*m2[0][0] + m1[1][1]*m2[1][0], m1[1][0]*m2[0][1] + m1[1][1]*m2[1][1]]
    ]

def optics_ray_propagate(y0: float, theta0: float, abcd: List[List[float]]) -> Tuple[float, float]:
    """Propagates ray vector [y, theta] through an optical system ABCD matrix."""
    y = abcd[0][0] * y0 + abcd[0][1] * theta0
    theta = abcd[1][0] * y0 + abcd[1][1] * theta0
    return round(y, 4), round(theta, 6)

# ============================================================================
# 3. GAUSSIAN BEAM PROPAGATION & POLARIZATION
# ============================================================================

def optics_gaussian_beam(wavelength_nm: float, waist_radius_w0_um: float, distance_z_mm: float) -> Dict[str, float]:
    """Calculates Gaussian beam waist w(z), Rayleigh range zR, and wavefront curvature R(z)."""
    lam_mm = float(wavelength_nm) * 1e-6
    w0_mm = float(waist_radius_w0_um) * 1e-3
    z_mm = float(distance_z_mm)
    zr_mm = (math.pi * (w0_mm ** 2)) / lam_mm
    w_z_mm = w0_mm * math.sqrt(1.0 + (z_mm / zr_mm) ** 2)
    r_z_mm = z_mm * (1.0 + (zr_mm / z_mm) ** 2) if z_mm != 0 else float("inf")
    divergence_mrad = (lam_mm / (math.pi * w0_mm)) * 1000.0
    return {
        "rayleigh_range_mm": round(zr_mm, 2),
        "beam_radius_um": round(w_z_mm * 1000.0, 2),
        "wavefront_radius_mm": round(r_z_mm, 2) if r_z_mm != float("inf") else float("inf"),
        "divergence_mrad": round(divergence_mrad, 2)
    }

def optics_malus_law(initial_intensity: float, angle_deg: float) -> float:
    """Calculates transmitted light intensity through polarizer via Malus's Law: I = I0 * cos^2(theta)."""
    rad = math.radians(float(angle_deg))
    return round(float(initial_intensity) * (math.cos(rad) ** 2), 4)

def optics_thin_film_anti_reflective(n_substrate: float, n_ambient: float = 1.0, wavelength_nm: float = 550.0) -> Dict[str, float]:
    """Calculates optimal refractive index and quarter-wave thickness for single-layer AR coating."""
    n_opt = math.sqrt(float(n_substrate) * float(n_ambient))
    thickness_nm = float(wavelength_nm) / (4.0 * n_opt)
    return {
        "coating_refractive_index": round(n_opt, 3),
        "coating_thickness_nm": round(thickness_nm, 2),
        "design_wavelength_nm": wavelength_nm
    }

# ============================================================================
# 4. DOMAIN RUNTIME
# ============================================================================

class OpticsRuntime(DomainRuntime):
    """Unified runtime bridge for the Optics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def thin_lens(self, f: float, do: float) -> Dict[str, float]:
        return optics_thin_lens(f, do)
    def snell(self, n1: float, n2: float, theta: float) -> Dict[str, Any]:
        return optics_snell_refraction(n1, n2, theta)
    def fresnel(self, n1: float, n2: float) -> float:
        return optics_fresnel_reflectance(n1, n2)
    def rayleigh(self, lam: float, na: float) -> float:
        return optics_rayleigh_resolution(lam, na)
    def grating(self, lines: float, m: int, lam: float) -> float:
        return optics_diffraction_grating(lines, m, lam)
    def brewster(self, n1: float, n2: float) -> float:
        return optics_brewster_angle(n1, n2)
    def fiber_na(self, n1: float, n2: float) -> Dict[str, float]:
        return optics_fiber_numerical_aperture(n1, n2)
    def gaussian(self, lam: float, w0: float, z: float) -> Dict[str, float]:
        return optics_gaussian_beam(lam, w0, z)
    def malus(self, i0: float, theta: float) -> float:
        return optics_malus_law(i0, theta)
    def ar_coating(self, n_sub: float, n_amb: float = 1.0, lam: float = 550.0) -> Dict[str, float]:
        return optics_thin_film_anti_reflective(n_sub, n_amb, lam)
