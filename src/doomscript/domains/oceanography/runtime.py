"""Oceanography Domain Runtime: Seawater density, Coriolis parameter, wave dispersion, hydrostatic pressure, Mackenzie sound speed, Ekman depth, Brunt-Vaisala frequency, and Sverdrup transport."""
import math
from typing import Dict, Any, List, Optional
from doomscript.domains.base import DomainRuntime

OMEGA_EARTH = 7.2921e-5  # rad/s
R_EARTH = 6.371e6  # meters

def ocean_seawater_density(temp_c: float, salinity_psu: float) -> float:
    """Calculates seawater density rho (kg/m^3) at atmospheric pressure using simplified UNESCO equation of state."""
    t = float(temp_c)
    s = float(salinity_psu)
    rho_fresh = 999.842594 + (6.793952e-2 * t) - (9.095290e-3 * (t**2)) + (1.001685e-4 * (t**3))
    density = rho_fresh + (0.824493 - 4.0899e-3 * t + 7.6438e-5 * (t**2)) * s - (5.72466e-3 - 1.0227e-4 * t) * (s**1.5) + (4.8314e-4 * (s**2))
    return round(density, 3)

def ocean_coriolis_parameter(latitude_deg: float) -> float:
    """Calculates planetary Coriolis frequency parameter f = 2 * Omega * sin(phi) in s^-1."""
    phi_rad = math.radians(float(latitude_deg))
    f = 2.0 * OMEGA_EARTH * math.sin(phi_rad)
    return float(f"{f:.7e}")

def ocean_gravity_wave_speed(wavelength_m: float, depth_m: float) -> Dict[str, float]:
    """Calculates surface gravity wave phase velocity c = sqrt((g * lambda / 2pi) * tanh(2pi * d / lambda))."""
    lam = float(wavelength_m)
    d = float(depth_m)
    g = 9.80665
    if lam <= 0.0 or d <= 0.0:
        return {"phase_velocity_m_s": 0.0, "regime": "invalid"}
    k = (2.0 * math.pi) / lam
    c = math.sqrt((g / k) * math.tanh(k * d))
    d_over_l = d / lam
    regime = "deep_water" if d_over_l > 0.5 else ("shallow_water" if d_over_l < 0.05 else "intermediate_water")
    return {"phase_velocity_m_s": round(c, 2), "regime": regime}

def ocean_hydrostatic_pressure(depth_m: float, avg_density_kg_m3: float = 1025.0) -> float:
    """Calculates hydrostatic gauge pressure P = rho * g * z in kiloPascals (kPa)."""
    z = float(depth_m)
    rho = float(avg_density_kg_m3)
    g = 9.80665
    p_kpa = (rho * g * z) / 1000.0
    return round(p_kpa, 2)

def ocean_sound_speed_mackenzie(temp_c: float, salinity_psu: float, depth_m: float) -> float:
    """Calculates speed of sound in seawater using Mackenzie (1981) empirical formulation."""
    t = float(temp_c)
    s = float(salinity_psu)
    d = float(depth_m)
    c = (1448.96 + 4.591 * t - 5.304e-2 * (t**2) + 2.374e-4 * (t**3) +
         1.340 * (s - 35.0) + 1.630e-2 * d + 1.675e-7 * (d**2) -
         1.025e-2 * t * (s - 35.0) - 7.139e-13 * t * (d**3))
    return round(c, 2)

def ocean_wind_stress(wind_speed_10m_m_s: float, drag_coeff: float = 0.0013, air_density_kg_m3: float = 1.22) -> float:
    """Calculates ocean surface wind shear stress tau = rho_air * C_d * U_10^2 in N/m^2."""
    u10 = float(wind_speed_10m_m_s)
    cd = float(drag_coeff)
    rho = float(air_density_kg_m3)
    tau = rho * cd * (u10 ** 2)
    return round(tau, 4)

def ocean_ekman_depth(wind_speed_10m: float, lat_deg: float, eddy_viscosity: float = 0.05) -> Dict[str, float]:
    """Calculates Ekman boundary layer depth D_E = pi * sqrt(2 * A_z / |f|) and surface drift velocity."""
    u10 = float(wind_speed_10m)
    lat = float(lat_deg)
    az = max(1e-4, float(eddy_viscosity))
    f = abs(2.0 * OMEGA_EARTH * math.sin(math.radians(lat)))
    if f < 1e-8:
        f = 1e-8
    d_e = math.pi * math.sqrt(2.0 * az / f)
    tau = 1.22 * 0.0013 * (u10 ** 2)
    rho_w = 1025.0
    v0 = tau / (rho_w * math.sqrt(f * az))
    angle = 45.0 if lat >= 0 else -45.0
    return {
        "ekman_depth_m": round(d_e, 2),
        "surface_drift_speed_m_s": round(v0, 4),
        "drift_angle_deg": angle,
        "coriolis_parameter": float(f"{f:.7e}")
    }

def ocean_brunt_vaisala_frequency(density_profile: List[float], depth_profile: List[float]) -> Dict[str, Any]:
    """Calculates Brunt-Vaisala buoyancy frequency N^2 = -(g / rho_0) * (drho / dz) across vertical depth levels."""
    if len(density_profile) < 2 or len(depth_profile) < 2 or len(density_profile) != len(depth_profile):
        return {"frequencies_rad_s": [], "max_buoyancy_frequency_rad_s": 0.0, "water_column_stable": True, "pycnocline_depth_m": 0.0}
    g = 9.80665
    rho0 = float(density_profile[0]) if density_profile[0] > 0 else 1025.0
    n2_list = []
    mid_depths = []
    stable = True
    for i in range(len(density_profile) - 1):
        d_rho = float(density_profile[i+1]) - float(density_profile[i])
        dz = abs(float(depth_profile[i+1]) - float(depth_profile[i]))
        if dz == 0:
            dz = 1e-6
        n2 = (g / rho0) * (d_rho / dz)
        n2_list.append(round(n2, 6))
        mid_depths.append((float(depth_profile[i]) + float(depth_profile[i+1])) / 2.0)
        if n2 < 0:
            stable = False
    max_n2 = max(n2_list) if n2_list else 0.0
    max_idx = n2_list.index(max_n2) if n2_list else 0
    max_n = math.sqrt(max(0.0, max_n2))
    pycnocline_depth = mid_depths[max_idx] if mid_depths else 0.0
    return {
        "n_squared_layers": n2_list,
        "max_buoyancy_frequency_rad_s": round(max_n, 4),
        "pycnocline_depth_m": round(pycnocline_depth, 2),
        "water_column_stable": stable
    }

def ocean_sverdrup_transport(wind_stress_curl: float, lat_deg: float, basin_width_km: float = 5000.0) -> Dict[str, float]:
    """Calculates Sverdrup wind-driven meridional transport M_y = curl(tau) / beta and total volume transport in Sverdrups (Sv)."""
    curl_tau = float(wind_stress_curl)
    lat_rad = math.radians(float(lat_deg))
    cos_lat = math.cos(lat_rad)
    beta = (2.0 * OMEGA_EARTH * cos_lat) / R_EARTH
    if beta == 0:
        beta = 1e-12
    my = curl_tau / beta
    width_m = float(basin_width_km) * 1000.0
    rho0 = 1025.0
    vol_transport_m3_s = (my * width_m) / rho0
    transport_sv = vol_transport_m3_s / 1e6
    return {
        "beta_parameter": float(f"{beta:.7e}"),
        "meridional_transport_kg_m_s": round(my, 2),
        "transport_sverdrups": round(transport_sv, 2)
    }

def ocean_sound_channel_sofar(surface_temp_c: float, surface_salinity: float, depth_levels: List[float]) -> Dict[str, Any]:
    """Evaluates SOFAR channel acoustic ducting minimum sound speed depth profile."""
    t0 = float(surface_temp_c)
    s0 = float(surface_salinity)
    speeds = []
    for d in depth_levels:
        d_val = float(d)
        temp_at_d = max(2.5, t0 * math.exp(-d_val / 400.0) + 3.0 * (1.0 - math.exp(-d_val / 1000.0)))
        c = ocean_sound_speed_mackenzie(temp_at_d, s0, d_val)
        speeds.append({"depth_m": d_val, "sound_speed_m_s": c})
    min_speed_entry = min(speeds, key=lambda x: x["sound_speed_m_s"]) if speeds else {"depth_m": 0.0, "sound_speed_m_s": 0.0}
    return {
        "sofar_axis_depth_m": min_speed_entry["depth_m"],
        "minimum_sound_speed_m_s": min_speed_entry["sound_speed_m_s"],
        "sound_speed_profile": speeds
    }

def ocean_ts_diagram_analysis(temp_c: float, salinity_psu: float) -> Dict[str, Any]:
    """Calculates potential density sigma_theta and identifies oceanic water mass type."""
    t = float(temp_c)
    s = float(salinity_psu)
    rho = ocean_seawater_density(t, s)
    sigma_t = round(rho - 1000.0, 3)
    if t < 0.0 and s >= 34.6:
        w_class = "Antarctic Bottom Water (AABW)"
    elif 1.0 <= t <= 4.0 and 34.8 <= s <= 35.0:
        w_class = "North Atlantic Deep Water (NADW)"
    elif 3.0 <= t <= 7.0 and 34.0 <= s <= 34.6:
        w_class = "Antarctic Intermediate Water (AAIW)"
    elif t > 18.0 and s > 35.5:
        w_class = "Subtropical Surface Water (STW)"
    elif t > 24.0:
        w_class = "Tropical Surface Water (TSW)"
    else:
        w_class = "Central Water (CW)"
    return {
        "potential_density_kg_m3": rho,
        "sigma_theta": sigma_t,
        "water_mass_classification": w_class
    }

def ocean_tidal_form_factor(m2_amp: float, s2_amp: float, k1_amp: float, o1_amp: float) -> Dict[str, Any]:
    """Calculates tidal form factor F = (K1 + O1) / (M2 + S2) and classifies tidal regime."""
    m2 = float(m2_amp)
    s2 = float(s2_amp)
    k1 = float(k1_amp)
    o1 = float(o1_amp)
    semi = m2 + s2
    if semi == 0.0:
        return {"form_factor": 0.0, "regime": "unknown", "mean_spring_range_m": 0.0}
    f = (k1 + o1) / semi
    if f < 0.25:
        regime = "Semidiurnal"
    elif f < 1.5:
        regime = "Mixed (predominantly semidiurnal)"
    elif f < 3.0:
        regime = "Mixed (predominantly diurnal)"
    else:
        regime = "Diurnal"
    mean_spring_range = 2.0 * (m2 + s2)
    return {
        "form_factor": round(f, 3),
        "regime": regime,
        "mean_spring_range_m": round(mean_spring_range, 2)
    }

class OceanographyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "ocean_seawater_density",
    "ocean_coriolis_parameter",
    "ocean_gravity_wave_speed",
    "ocean_hydrostatic_pressure",
    "ocean_sound_speed_mackenzie",
    "ocean_wind_stress",
    "ocean_ekman_depth",
    "ocean_brunt_vaisala_frequency",
    "ocean_sverdrup_transport",
    "ocean_sound_channel_sofar",
    "ocean_ts_diagram_analysis",
    "ocean_tidal_form_factor",
    "OceanographyRuntime"
]
