"""Geophysics Domain Runtime: Earthquake magnitude, Seismic refraction, Bouguer anomaly, and Heat flow."""
import math
from typing import Dict, Any

def geo_epicentral_distance(p_arrival_s: float, s_arrival_s: float, vp_kms: float = 6.0, vs_kms: float = 3.5) -> float:
    """Computes epicentral distance (km) using Wadati method from P and S wave arrival time difference."""
    dt = float(s_arrival_s) - float(p_arrival_s)
    vp = float(vp_kms)
    vs = float(vs_kms)
    if dt <= 0.0 or vp <= vs or vs <= 0.0:
        return 0.0
    # D = dt / (1/Vs - 1/Vp)
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

def geo_snell_refraction_angle(angle_inc_deg: float, v1: float, v2: float) -> float:
    """Computes refracted angle (degrees) using Snell's Law: v1 / sin(i) = v2 / sin(r)."""
    i_rad = math.radians(float(angle_inc_deg))
    v1_val = float(v1)
    v2_val = float(v2)
    if v1_val <= 0.0:
        return 0.0
    sin_r = (v2_val / v1_val) * math.sin(i_rad)
    if sin_r > 1.0:
        # Total internal reflection: critical angle exceeded
        return 90.0
    r_deg = math.degrees(math.asin(sin_r))
    return round(r_deg, 2)

def geo_bouguer_anomaly(observed_g_mgal: float, theoretical_g_mgal: float, elevation_m: float, density_gcc: float = 2.67) -> float:
    """Computes Simple Bouguer Anomaly Delta g_B = g_obs - g_theory + 0.3086*h - 0.04193*rho*h."""
    g_obs = float(observed_g_mgal)
    g_th = float(theoretical_g_mgal)
    h = float(elevation_m)
    rho = float(density_gcc)
    # Free-air correction: +0.3086 * h
    # Bouguer slab correction: -0.04193 * rho * h
    c_fa = 0.3086 * h
    c_b = 0.04193 * rho * h
    anomaly = g_obs - g_th + c_fa - c_b
    return round(anomaly, 3)

def geo_geothermal_heat_flow(thermal_conductivity: float, temp_gradient_c_per_km: float) -> float:
    """Computes terrestrial heat flow q = k * (dT/dz) in mW/m^2."""
    k = float(thermal_conductivity) # W/(m*K)
    grad = float(temp_gradient_c_per_km) # C/km -> C/m is grad / 1000
    # q = k * (grad / 1000) * 1000 mW/m^2 = k * grad
    q = k * grad
    return round(q, 2)
