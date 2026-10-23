"""Hydrology Domain Runtime: Open channel hydraulics, pipe networks, aquifer drawdown, SCS curve numbers, Muskingum routing, and evapotranspiration."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

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

# ============================================================================
# 2. ADVANCED HYDROLOGICAL MODELING & CHANNEL ROUTING
# ============================================================================

def hydrology_scs_curve_number(curve_number: float, precipitation_mm: float) -> Dict[str, float]:
    """Calculates SCS Curve Number runoff depth: S = 25400/CN - 254, Ia = 0.2*S, Q = (P - Ia)^2 / (P - Ia + S)."""
    cn = float(curve_number)
    p = float(precipitation_mm)
    if cn <= 0.0 or cn > 100.0:
        return {"runoff_mm": 0.0, "retention_s_mm": 0.0, "initial_abstraction_mm": 0.0}
    s = (25400.0 / cn) - 254.0
    ia = 0.2 * s
    if p <= ia:
        q = 0.0
    else:
        q = ((p - ia) ** 2) / (p - ia + s)
    return {
        "runoff_mm": round(max(0.0, q), 2),
        "retention_s_mm": round(s, 2),
        "initial_abstraction_mm": round(ia, 2)
    }

def hydrology_muskingum_routing(inflows: List[float], k_travel_time_hrs: float, x_weight: float, delta_t_hrs: float, initial_outflow: Optional[float] = None) -> List[float]:
    """Routes a flood hydrograph through a river reach using the Muskingum storage method."""
    k = float(k_travel_time_hrs)
    x = float(x_weight)
    dt = float(delta_t_hrs)
    denom = 2.0 * k * (1.0 - x) + dt
    if denom <= 0.0 or not inflows:
        return inflows[:]

    c0 = (dt - 2.0 * k * x) / denom
    c1 = (dt + 2.0 * k * x) / denom
    c2 = (2.0 * k * (1.0 - x) - dt) / denom

    outflows = [inflows[0] if initial_outflow is None else float(initial_outflow)]
    for i in range(1, len(inflows)):
        i_curr = float(inflows[i])
        i_prev = float(inflows[i - 1])
        o_prev = outflows[-1]
        o_next = c0 * i_curr + c1 * i_prev + c2 * o_prev
        outflows.append(round(max(0.0, o_next), 2))
    return outflows

def hydrology_fao_penman_monteith(net_radiation_mj_m2_day: float, temp_c: float, wind_speed_2m_m_s: float, rel_humidity_pct: float, elevation_m: float = 0.0) -> float:
    """Calculates FAO-56 Penman-Monteith daily reference crop evapotranspiration ET0 (mm/day)."""
    rn = float(net_radiation_mj_m2_day)
    t = float(temp_c)
    u2 = float(wind_speed_2m_m_s)
    rh = float(rel_humidity_pct)
    z = float(elevation_m)

    # Atmospheric pressure P (kPa)
    p = 101.3 * (((293.0 - 0.0065 * z) / 293.0) ** 5.26)
    # Psychrometric constant gamma (kPa/C)
    gamma = 0.000665 * p
    # Saturation vapor pressure es (kPa)
    es = 0.6108 * math.exp((17.27 * t) / (t + 237.3))
    ea = es * (rh / 100.0)
    # Slope of saturation vapor pressure curve delta (kPa/C)
    delta = (4098.0 * es) / ((t + 237.3) ** 2)

    # FAO-56 ET0 equation (G ~ 0 for daily steps)
    num = 0.408 * delta * rn + gamma * (900.0 / (t + 273.0)) * u2 * (es - ea)
    den = delta + gamma * (1.0 + 0.34 * u2)
    et0 = num / den if den > 0 else 0.0
    return round(max(0.0, et0), 2)

class HydrologyRuntime(DomainRuntime):
    """Runtime engine for hydrology domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def manning(self, n: float, a: float, r: float, s: float) -> float:
        return hydrology_manning_flow(n, a, r, s)
    def peak_runoff(self, c: float, i: float, a: float) -> float:
        return hydrology_peak_runoff(c, i, a)
    def head_loss(self, f: float, l: float, d: float, v: float, g: float = 9.81) -> float:
        return hydrology_darcy_weisbach(f, l, d, v, g)
    def reynolds(self, v: float, d: float, nu: float = 1e-6) -> float:
        return hydrology_reynolds_number(v, d, nu)
    def jump(self, y1: float, v1: float, g: float = 9.81) -> Dict[str, float]:
        return hydrology_hydraulic_jump(y1, v1, g)
    def theis(self, q: float, t: float, s: float, r: float, time: float) -> float:
        return hydrology_theis_drawdown(q, t, s, r, time)
    def scs_curve_number(self, cn: float, p: float) -> Dict[str, float]:
        return hydrology_scs_curve_number(cn, p)
    def muskingum(self, inflows: List[float], k: float, x: float, dt: float) -> List[float]:
        return hydrology_muskingum_routing(inflows, k, x, dt)
    def et0(self, rn: float, t: float, u2: float, rh: float, z: float = 0.0) -> float:
        return hydrology_fao_penman_monteith(rn, t, u2, rh, z)
