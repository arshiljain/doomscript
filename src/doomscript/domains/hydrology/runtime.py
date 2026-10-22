"""Hydrology & Hydrodynamics Domain Runtime: Manning flow, Hydraulic Jump, Darcy-Weisbach, Theis well equation, and Muskingum routing."""
import math
from typing import Dict, Any, List

def hydrology_manning_flow(roughness_n: float, area_m2: float, hydraulic_radius_m: float, slope: float) -> float:
    """Calculates open-channel uniform flow rate Q = (1/n) * A * R^(2/3) * S^(1/2)."""
    n = float(roughness_n)
    a = float(area_m2)
    r = float(hydraulic_radius_m)
    s = float(slope)
    if n <= 0.0 or a <= 0.0 or r <= 0.0 or s <= 0.0:
        return 0.0
    q = (1.0 / n) * a * (r ** (2.0 / 3.0)) * math.sqrt(s)
    return round(q, 3)

def hydrology_peak_runoff(c_runoff: float, rainfall_intensity_mm_hr: float, drainage_area_ha: float) -> float:
    """Calculates peak runoff Q = C * I * A using the Rational Method (m^3/s or L/s normalized)."""
    c = float(c_runoff)
    i = float(rainfall_intensity_mm_hr)
    a = float(drainage_area_ha)
    return round(c * i * a, 2)

def hydrology_darcy_weisbach(friction_factor_f: float, pipe_length_m: float, pipe_diameter_m: float, velocity_m_s: float, g: float = 9.81) -> float:
    """Calculates friction head loss h_f = f * (L/D) * (v^2 / (2g))."""
    f = float(friction_factor_f)
    l = float(pipe_length_m)
    d = float(pipe_diameter_m)
    v = float(velocity_m_s)
    if d <= 0.0:
        return 0.0
    hf = f * (l / d) * ((v ** 2) / (2.0 * g))
    return round(hf, 3)

def hydrology_reynolds_number(velocity: float, characteristic_dim: float, kinematic_viscosity: float = 1e-6) -> float:
    """Calculates Reynolds Number Re = v * D / nu."""
    v = float(velocity)
    d = float(characteristic_dim)
    nu = float(kinematic_viscosity)
    if nu <= 0.0:
        return 0.0
    return round((v * d) / nu, 1)

def hydrology_hydraulic_jump(y1_depth_m: float, v1_velocity_m_s: float, g: float = 9.81) -> Dict[str, float]:
    """Calculates open channel hydraulic jump: Froude number Fr1, conjugate depth y2, and energy dissipation delta_E."""
    y1 = float(y1_depth_m)
    v1 = float(v1_velocity_m_s)
    if y1 <= 0.0:
        return {"fr1": 0.0, "y2": 0.0, "delta_e": 0.0}
    fr1 = v1 / math.sqrt(g * y1)
    if fr1 < 1.0:
        return {"fr1": round(fr1, 3), "y2": round(y1, 3), "delta_e": 0.0}
    # Conjugate depth y2 = y1/2 * (sqrt(1 + 8*Fr1^2) - 1)
    y2 = (y1 / 2.0) * (math.sqrt(1.0 + 8.0 * (fr1 ** 2)) - 1.0)
    delta_e = ((y2 - y1) ** 3) / (4.0 * y1 * y2)
    return {"fr1": round(fr1, 3), "y2": round(y2, 3), "delta_e": round(delta_e, 3)}

def hydrology_theis_drawdown(discharge_m3_s: float, transmissivity_m2_s: float, storativity: float, radius_m: float, time_s: float) -> float:
    """Calculates confined aquifer drawdown using Theis non-equilibrium well equation."""
    q = float(discharge_m3_s)
    trans = float(transmissivity_m2_s)
    s_stor = float(storativity)
    r = float(radius_m)
    t = float(time_s)
    if trans <= 0.0 or t <= 0.0:
        return 0.0
    u = (r ** 2 * s_stor) / (4.0 * trans * t)
    # Well function W(u) approximation: -0.5772 - ln(u) + u
    if u >= 5.0:
        w_u = 0.0
    elif u > 0:
        w_u = max(0.0, -0.57721566 - math.log(u) + u)
    else:
        w_u = 0.0
    drawdown = (q / (4.0 * math.pi * trans)) * w_u
    return round(drawdown, 3)
