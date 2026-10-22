"""Aerospace & Aerodynamics Runtime: Lift, drag, Mach number, standard atmosphere, and Breguet range."""
import math
from typing import Dict, Any

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
    v = float(velocity)
    t = float(temperature_k)
    speed_of_sound = math.sqrt(gamma * r * t)
    return round(v / speed_of_sound, 3)

def aero_breguet_range(lift_over_drag: float, velocity: float, sfc: float, w_initial: float, w_final: float) -> float:
    """Calculates Breguet flight range for jet aircraft R = (V / SFC) * (L/D) * ln(W0 / W1)."""
    lod = float(lift_over_drag)
    v = float(velocity)
    c = float(sfc)
    w0 = float(w_initial)
    w1 = float(w_final)
    if c <= 0.0 or w1 <= 0.0:
        return 0.0
    return round((v / c) * lod * math.log(w0 / w1), 2)
