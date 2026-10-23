"""Aerospace Domain Runtime: Lift/drag, Mach number, Breguet range, Hohmann transfers, Kepler orbits, Tsiolkovsky rocketry, and normal shock waves."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

G_CONST = 6.67430e-11
G0_STANDARD = 9.80665  # m/s^2 standard gravity

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def aero_lift_drag(density: float, velocity: float, wing_area: float, cl: float, cd: float) -> Dict[str, float]:
    """Calculates aerodynamic lift and drag forces in Newtons."""
    rho = float(density)
    v = float(velocity)
    s = float(wing_area)
    q = 0.5 * rho * (v ** 2)
    lift = q * s * float(cl)
    drag = q * s * float(cd)
    return {"dynamic_pressure_pa": round(q, 2), "lift_n": round(lift, 2), "drag_n": round(drag, 2)}

def aero_mach_number(velocity: float, temperature_k: float = 288.15, gamma: float = 1.4, r: float = 287.05) -> float:
    """Calculates Mach number M = v / a, where a = sqrt(gamma * R * T)."""
    speed_of_sound = math.sqrt(gamma * r * float(temperature_k))
    return round(float(velocity) / speed_of_sound, 3)

def aero_breguet_range(lift_over_drag: float, velocity: float, sfc: float, w_initial: float, w_final: float) -> float:
    """Calculates Breguet flight range for jet aircraft R = (V / SFC) * (L/D) * ln(W0 / W1)."""
    c = float(sfc)
    w1 = float(w_final)
    if c <= 0.0 or w1 <= 0.0:
        return 0.0
    return round((float(velocity) / c) * float(lift_over_drag) * math.log(float(w_initial) / w1), 2)

def aerospace_orbital_velocity(altitude_km: float, celestial_mass: float = 5.972e24, radius_km: float = 6371.0) -> float:
    """Calculates circular orbit velocity v = sqrt(G*M / r) in m/s."""
    r_meters = (float(radius_km) + float(altitude_km)) * 1000.0
    if r_meters <= 0:
        return 0.0
    v = math.sqrt((G_CONST * float(celestial_mass)) / r_meters)
    return round(v, 2)

def aerospace_hohmann_transfer(r1_km: float, r2_km: float, celestial_mass: float = 5.972e24) -> Dict[str, float]:
    """Calculates Hohmann transfer orbit velocity changes delta_v1, delta_v2, total delta_v (m/s), and transfer time (hours)."""
    mu = G_CONST * float(celestial_mass)
    r1 = float(r1_km) * 1000.0
    r2 = float(r2_km) * 1000.0
    v1_circ = math.sqrt(mu / r1)
    v2_circ = math.sqrt(mu / r2)
    a_trans = (r1 + r2) / 2.0
    v_trans_1 = math.sqrt(mu * (2.0 / r1 - 1.0 / a_trans))
    v_trans_2 = math.sqrt(mu * (2.0 / r2 - 1.0 / a_trans))
    dv1 = abs(v_trans_1 - v1_circ)
    dv2 = abs(v2_circ - v_trans_2)
    t_sec = math.pi * math.sqrt((a_trans ** 3) / mu)
    return {
        "delta_v1": round(dv1, 2),
        "delta_v2": round(dv2, 2),
        "total_delta_v": round(dv1 + dv2, 2),
        "transfer_time_hours": round(t_sec / 3600.0, 2)
    }

def aerospace_kepler_orbit(periapsis_km: float, apoapsis_km: float, celestial_mass: float = 5.972e24, radius_km: float = 6371.0) -> Dict[str, float]:
    """Calculates orbital eccentricity, semi-major axis, and orbital period for Keplerian orbit."""
    mu = G_CONST * float(celestial_mass)
    rp = (float(radius_km) + float(periapsis_km)) * 1000.0
    ra = (float(radius_km) + float(apoapsis_km)) * 1000.0
    a = (rp + ra) / 2.0
    e = (ra - rp) / (ra + rp)
    period_sec = 2.0 * math.pi * math.sqrt((a ** 3) / mu)
    return {
        "semi_major_axis_km": round(a / 1000.0, 2),
        "eccentricity": round(e, 4),
        "period_minutes": round(period_sec / 60.0, 2)
    }

# ============================================================================
# 2. DEEPENED ROCKET PROPULSION & COMPRESSIBLE AERODYNAMICS
# ============================================================================

def aerospace_tsiolkovsky_rocket(isp_seconds: float, m_initial_kg: float, m_final_kg: float) -> Dict[str, float]:
    """Calculates ideal delta-V via Tsiolkovsky rocket equation: Delta V = Isp * g0 * ln(m0 / mf)."""
    isp = float(isp_seconds)
    m0 = float(m_initial_kg)
    mf = float(m_final_kg)
    if mf <= 0 or m0 < mf or isp <= 0:
        return {"delta_v_m_s": 0.0, "mass_ratio": 1.0}
    mass_ratio = m0 / mf
    dv = isp * G0_STANDARD * math.log(mass_ratio)
    return {
        "delta_v_m_s": round(dv, 2),
        "mass_ratio": round(mass_ratio, 3)
    }

def aerospace_normal_shock(mach_1: float, gamma: float = 1.4) -> Dict[str, float]:
    """Calculates downstream Mach number M2, static pressure ratio p2/p1, and temperature ratio T2/T1 across normal shock wave."""
    m1 = float(mach_1)
    g = float(gamma)
    if m1 <= 1.0:
        return {"mach_2": round(m1, 3), "pressure_ratio": 1.0, "temperature_ratio": 1.0}

    # Downstream Mach M2
    num_m2 = 2.0 + (g - 1.0) * (m1 ** 2)
    den_m2 = 2.0 * g * (m1 ** 2) - (g - 1.0)
    m2 = math.sqrt(num_m2 / den_m2)

    # Static pressure ratio p2/p1
    p_ratio = 1.0 + ((2.0 * g) / (g + 1.0)) * ((m1 ** 2) - 1.0)

    # Temperature ratio T2/T1
    t_ratio = (1.0 + ((2.0 * g) / (g + 1.0)) * ((m1 ** 2) - 1.0)) * (num_m2 / ((g + 1.0) * (m1 ** 2)))

    return {
        "mach_2": round(m2, 4),
        "pressure_ratio": round(p_ratio, 3),
        "temperature_ratio": round(t_ratio, 3)
    }

class AerospaceRuntime(DomainRuntime):
    """Runtime engine for Aerospace domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def lift_drag(self, rho: float, v: float, s: float, cl: float, cd: float) -> Dict[str, float]:
        return aero_lift_drag(rho, v, s, cl, cd)
    def mach(self, v: float, t: float = 288.15) -> float:
        return aero_mach_number(v, t)
    def breguet(self, ld: float, v: float, sfc: float, w0: float, w1: float) -> float:
        return aero_breguet_range(ld, v, sfc, w0, w1)
    def orbital_velocity(self, alt: float, m: float = 5.972e24, r: float = 6371.0) -> float:
        return aerospace_orbital_velocity(alt, m, r)
    def hohmann(self, r1: float, r2: float, m: float = 5.972e24) -> Dict[str, float]:
        return aerospace_hohmann_transfer(r1, r2, m)
    def kepler(self, rp: float, ra: float, m: float = 5.972e24, r: float = 6371.0) -> Dict[str, float]:
        return aerospace_kepler_orbit(rp, ra, m, r)
    def rocket_equation(self, isp: float, m0: float, mf: float) -> Dict[str, float]:
        return aerospace_tsiolkovsky_rocket(isp, m0, mf)
    def normal_shock(self, m1: float, gamma: float = 1.4) -> Dict[str, float]:
        return aerospace_normal_shock(m1, gamma)

aero_lift_drag_forces = aero_lift_drag
