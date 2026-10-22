"""Biomechanics Domain Runtime: Joint torque, COM, GRF impulse, muscle tendon force, Hill muscle force-velocity, and moment of inertia."""
import math
from typing import List, Dict, Any

def biomech_joint_moment(force_n: float, moment_arm_m: float, angle_deg: float = 90.0) -> float:
    """Calculates joint torque/moment M = F * r * sin(theta) in N*m."""
    f = float(force_n)
    r = float(moment_arm_m)
    theta = math.radians(float(angle_deg))
    return round(f * r * math.sin(theta), 3)

def biomech_center_of_mass(segment_masses: List[float], segment_positions: List[float]) -> float:
    """Calculates 1D center of mass COM = sum(m_i * x_i) / sum(m_i)."""
    if len(segment_masses) != len(segment_positions) or not segment_masses:
        return 0.0
    total_mass = sum(float(m) for m in segment_masses)
    if total_mass <= 0.0:
        return 0.0
    weighted_sum = sum(float(m) * float(x) for m, x in zip(segment_masses, segment_positions))
    return round(weighted_sum / total_mass, 4)

def biomech_grf_impulse(force_samples_n: List[float], dt_seconds: float) -> float:
    """Calculates ground reaction force linear impulse J = sum(F_i * dt) in N*s."""
    dt = float(dt_seconds)
    if not force_samples_n or dt <= 0.0:
        return 0.0
    total = sum(float(f) * dt for f in force_samples_n)
    return round(total, 3)

def biomech_muscle_tendon_force(muscle_force_n: float, pennation_angle_deg: float) -> float:
    """Calculates effective force transmitted to tendon F_t = F_m * cos(alpha)."""
    fm = float(muscle_force_n)
    alpha = math.radians(float(pennation_angle_deg))
    return round(fm * math.cos(alpha), 2)

def biomech_hills_muscle_force_velocity(concentric_velocity_m_s: float, f0_isometric_force_n: float, a_param: float, b_param: float) -> float:
    """Calculates muscle contractile force under Hill's characteristic equation: (F + a) * (v + b) = (F0 + a) * b."""
    v = float(concentric_velocity_m_s)
    f0 = float(f0_isometric_force_n)
    a = float(a_param)
    b = float(b_param)
    if (v + b) <= 0.0:
        return 0.0
    f = (((f0 + a) * b) / (v + b)) - a
    return round(max(0.0, f), 2)

def biomech_segment_moment_of_inertia_cylinder(mass_kg: float, radius_m: float) -> float:
    """Calculates solid cylindrical limb segment moment of inertia I = 0.5 * m * r^2 in kg*m^2."""
    m = float(mass_kg)
    r = float(radius_m)
    return round(0.5 * m * (r ** 2), 5)
