"""Geophysics Domain Runtime: Wadati epicentral distance, Richter magnitude, Moment magnitude, Snell refraction, Bouguer anomaly, and Wenner resistivity."""
import math
from typing import Dict, Any

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
    # Mw = (2/3) * log10(M0 in dyne*cm) - 10.7 where 1 N*m = 1e7 dyne*cm
    m0_dyne_cm = m0 * 1e7
    mw = (2.0 / 3.0) * math.log10(m0_dyne_cm) - 10.7
    return {"seismic_moment_nm": round(m0, 2), "moment_magnitude_mw": round(mw, 2)}

def geo_snell_refraction_angle(angle_inc_deg: float, v1: float, v2: float) -> float:
    """Computes refracted angle (degrees) using Snell's Law."""
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
    rho = float(density_gcc)
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
