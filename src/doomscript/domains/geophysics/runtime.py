"""Geophysics Domain Runtime: Seismology, seismic ray refraction, gravity anomalies, geomagnetic dipole, and electrical resistivity."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def geo_epicentral_distance(p_arrival_s: float, s_arrival_s: float, vp_kms: float = 6.0, vs_kms: float = 3.5) -> float:
    """Computes epicentral distance (km) using Wadati method from P and S arrival difference."""
    dt = float(s_arrival_s) - float(p_arrival_s)
    vp = float(vp_kms)
    vs = float(vs_kms)
    if dt <= 0.0 or vp <= vs or vs <= 0.0:
        return 0.0
    dist = dt / ((1.0 / vs) - (1.0 / vp))
    return round(dist, 2)

def geo_richter_magnitude(amplitude_microns: float, distance_km: float) -> float:
    """Computes local Richter magnitude ML = log10(A) + 3*log10(8*D) - 2.92."""
    a = float(amplitude_microns)
    d = float(distance_km)
    if a <= 0.0 or d <= 0.0:
        return 0.0
    ml = math.log10(a) + 3.0 * math.log10(8.0 * d) - 2.92
    return round(ml, 2)

def geo_moment_magnitude(rupture_area_sq_km: float, average_slip_m: float, shear_modulus_gpa: float = 32.0) -> Dict[str, float]:
    """Calculates seismic moment M0 = mu * A * D and Moment Magnitude Mw = (2/3)*log10(M0) - 10.7."""
    area_m2 = float(rupture_area_sq_km) * 1e6
    slip_m = float(average_slip_m)
    mu_pa = float(shear_modulus_gpa) * 1e9
    m0 = mu_pa * area_m2 * slip_m
    if m0 <= 0:
        return {"seismic_moment_nm": 0.0, "moment_magnitude_mw": 0.0}
    m0_dyne_cm = m0 * 1e7
    mw = (2.0 / 3.0) * math.log10(m0_dyne_cm) - 10.7
    return {"seismic_moment_nm": round(m0, 2), "moment_magnitude_mw": round(mw, 2)}

def geo_snell_refraction_angle(angle_inc_deg: float, v1: float, v2: float) -> float:
    """Computes refracted angle (degrees) using Snell Law."""
    i_rad = math.radians(float(angle_inc_deg))
    v1_val = float(v1)
    v2_val = float(v2)
    if v1_val <= 0.0:
        return 0.0
    sin_r = (v2_val / v1_val) * math.sin(i_rad)
    if sin_r > 1.0:
        return 90.0
    r_deg = math.degrees(math.asin(sin_r))
    return round(r_deg, 2)

def geo_bouguer_anomaly(observed_g_mgal: float, theoretical_g_mgal: float, elevation_m: float, density_gcc: float = 2.67) -> float:
    """Computes Simple Bouguer Anomaly Delta g_B = g_obs - g_theory + 0.3086*h - 0.04193*rho*h."""
    h = float(elevation_m)
    rho = 2.67 if density_gcc is None else float(density_gcc)
    c_fa = 0.3086 * h
    c_b = 0.04193 * rho * h
    anomaly = float(observed_g_mgal) - float(theoretical_g_mgal) + c_fa - c_b
    return round(anomaly, 3)

def geo_apparent_resistivity_wenner(electrode_spacing_a_m: float, measured_resistance_ohms: float) -> float:
    """Calculates apparent electrical resistivity rho_a = 2 * pi * a * R in Ohm*meters."""
    a = float(electrode_spacing_a_m)
    r = float(measured_resistance_ohms)
    return round(2.0 * math.pi * a * r, 2)

def geo_geothermal_heat_flow(thermal_conductivity: float, temp_gradient_c_per_km: float) -> float:
    """Computes terrestrial heat flow q = k * (dT/dz) in mW/m^2."""
    return round(float(thermal_conductivity) * float(temp_gradient_c_per_km), 2)

# ============================================================================
# 2. ADVANCED SEISMIC & GEOPHYSICAL ANALYSIS
# ============================================================================

def geo_seismic_refraction_layer(v1_km_s: float, v2_km_s: float, layer_depth_m: float) -> Dict[str, float]:
    """Calculates critical angle, crossover distance, and intercept time for 2-layer seismic refraction survey."""
    v1 = float(v1_km_s)
    v2 = float(v2_km_s)
    z1 = float(layer_depth_m) / 1000.0  # in km
    if v1 >= v2 or v1 <= 0.0:
        return {"critical_angle_deg": 0.0, "crossover_dist_km": 0.0, "intercept_time_s": 0.0}

    ic_rad = math.asin(v1 / v2)
    ic_deg = math.degrees(ic_rad)
    x_cross = 2.0 * z1 * math.sqrt((v2 + v1) / (v2 - v1))
    ti = (2.0 * z1 * math.sqrt(v2**2 - v1**2)) / (v1 * v2)
    return {
        "critical_angle_deg": round(ic_deg, 2),
        "crossover_dist_km": round(x_cross, 3),
        "intercept_time_s": round(ti, 3)
    }

def geo_geomagnetic_dipole(geomagnetic_latitude_deg: float, equatorial_field_microtesla: float = 31.0) -> Dict[str, float]:
    """Calculates Earth dipole magnetic inclination (dip angle) and total intensity B = B0 * sqrt(1 + 3*sin^2(lat))."""
    lat_rad = math.radians(float(geomagnetic_latitude_deg))
    b0 = float(equatorial_field_microtesla)
    # tan(I) = 2 * tan(lat)
    inc_rad = math.atan(2.0 * math.tan(lat_rad))
    inc_deg = math.degrees(inc_rad)
    b_total = b0 * math.sqrt(1.0 + 3.0 * (math.sin(lat_rad) ** 2))
    return {
        "inclination_deg": round(inc_deg, 2),
        "total_intensity_ut": round(b_total, 2)
    }

def geo_isostasy_root_thickness(topography_height_m: float, crust_density_gcc: float = 2.8, mantle_density_gcc: float = 3.3) -> float:
    """Calculates Airy-Heiskanen crustal root thickness t = h * rho_c / (rho_m - rho_c)."""
    h = float(topography_height_m)
    rc = float(crust_density_gcc)
    rm = float(mantle_density_gcc)
    if rm <= rc:
        return 0.0
    root = h * (rc / (rm - rc))
    return round(root, 1)

class GeophysicsRuntime(DomainRuntime):
    """Runtime engine for Geophysics domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def epicentral_distance(self, tp: float, ts: float, vp: float = 6.0, vs: float = 3.5) -> float:
        return geo_epicentral_distance(tp, ts, vp, vs)
    def richter(self, a: float, d: float) -> float:
        return geo_richter_magnitude(a, d)
    def moment_magnitude(self, area: float, slip: float, mu: float = 32.0) -> Dict[str, float]:
        return geo_moment_magnitude(area, slip, mu)
    def snell(self, inc: float, v1: float, v2: float) -> float:
        return geo_snell_refraction_angle(inc, v1, v2)
    def bouguer(self, obs: float, theo: float, h: float, rho: float = 2.67) -> float:
        return geo_bouguer_anomaly(obs, theo, h, rho)
    def resistivity(self, a: float, r: float) -> float:
        return geo_apparent_resistivity_wenner(a, r)
    def heat_flow(self, k: float, grad: float) -> float:
        return geo_geothermal_heat_flow(k, grad)
    def refraction_layer(self, v1: float, v2: float, z: float) -> Dict[str, float]:
        return geo_seismic_refraction_layer(v1, v2, z)
    def geomagnetism(self, lat: float, b0: float = 31.0) -> Dict[str, float]:
        return geo_geomagnetic_dipole(lat, b0)
    def isostasy(self, h: float, rc: float = 2.8, rm: float = 3.3) -> float:
        return geo_isostasy_root_thickness(h, rc, rm)
