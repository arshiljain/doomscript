"""Biomechanics Domain Runtime: Joint torque, COM, GRF impulse, muscle tendon force, Hill muscle force-velocity, moment of inertia, 2D inverse dynamics, joint power, vertical loading rate, pennation geometry, and gait Froude number."""
import math
from typing import List, Dict, Any
from doomscript.domains.base import DomainRuntime

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

def biomech_inverse_dynamics_2d_segment(distal_fx: float, distal_fy: float, distal_m: float,
                                        segment_mass_kg: float, segment_length_m: float,
                                        r_com_proximal_m: float, segment_angle_deg: float,
                                        acc_com_x: float, acc_com_y: float,
                                        alpha_rad_s2: float, moi_com: float) -> Dict[str, float]:
    """Calculates proximal joint reaction forces and moment using 2D Newton-Euler inverse dynamics."""
    dfx = float(distal_fx)
    dfy = float(distal_fy)
    dm = float(distal_m)
    m = float(segment_mass_kg)
    l = float(segment_length_m)
    r_prox = float(r_com_proximal_m)
    r_dist = l - r_prox
    th = math.radians(float(segment_angle_deg))
    ax = float(acc_com_x)
    ay = float(acc_com_y)
    alpha = float(alpha_rad_s2)
    i_com = float(moi_com)
    g = 9.80665

    # Sum Fx = m * ax => F_px - F_dx = m * ax => F_px = F_dx + m * ax
    p_fx = dfx + m * ax
    # Sum Fy = m * ay => F_py - F_dy - m*g = m * ay => F_py = F_dy + m*(ay + g)
    p_fy = dfy + m * (ay + g)

    # Moments about COM:
    # Proximal joint position relative to COM: -r_prox * [cos(th), sin(th)]
    # Distal joint position relative to COM: +r_dist * [cos(th), sin(th)]
    # Sum M_com = I_com * alpha
    # M_p + M_d + (r_prox * sin(th) * F_px - r_prox * cos(th) * F_py) + (-r_dist * sin(th) * F_dx + r_dist * cos(th) * F_dy) = I * alpha
    lever_p = (-r_prox * math.cos(th) * p_fy + r_prox * math.sin(th) * p_fx)
    lever_d = (r_dist * math.cos(th) * dfy - r_dist * math.sin(th) * dfx)
    p_m = (i_com * alpha) - dm - lever_p - lever_d
    return {
        "proximal_fx_n": round(p_fx, 2),
        "proximal_fy_n": round(p_fy, 2),
        "proximal_moment_nm": round(p_m, 2)
    }

def biomech_muscle_mechanical_work_power(joint_moment_nm: float, angular_velocity_rad_s: float, dt_s: float = 0.01) -> Dict[str, float]:
    """Calculates instantaneous joint mechanical power P = M * omega and incremental work W = P * dt."""
    m = float(joint_moment_nm)
    w = float(angular_velocity_rad_s)
    dt = float(dt_s)
    power = m * w
    work = power * dt
    return {
        "power_watts": round(power, 2),
        "work_joules": round(work, 3),
        "contraction_mode": "concentric" if power > 0 else ("eccentric" if power < 0 else "isometric")
    }

def biomech_vertical_loading_rate(grf_time_series_n: List[float], sample_rate_hz: float, body_weight_n: float) -> Dict[str, float]:
    """Calculates vertical average (VALR) and instantaneous (VILR) loading rates in BW/s."""
    bw = float(body_weight_n) if body_weight_n > 0 else 700.0
    sr = float(sample_rate_hz) if sample_rate_hz > 0 else 1000.0
    dt = 1.0 / sr
    if len(grf_time_series_n) < 3:
        return {"valr_bw_s": 0.0, "vilr_bw_s": 0.0, "peak_grf_bw": 0.0}
    forces_bw = [float(f) / bw for f in grf_time_series_n]
    peak_grf = max(forces_bw)
    # Find 20% and 80% of impact peak
    f_20 = 0.20 * peak_grf
    f_80 = 0.80 * peak_grf
    idx_20 = 0
    idx_80 = 0
    for i, f in enumerate(forces_bw):
        if f >= f_20 and idx_20 == 0:
            idx_20 = i
        if f >= f_80 and idx_80 == 0:
            idx_80 = i
            break
    if idx_80 > idx_20:
        valr = (forces_bw[idx_80] - forces_bw[idx_20]) / ((idx_80 - idx_20) * dt)
    else:
        valr = 0.0
    # Maximum instantaneous slope
    vilr = 0.0
    for i in range(len(forces_bw) - 1):
        slope = (forces_bw[i+1] - forces_bw[i]) / dt
        if slope > vilr:
            vilr = slope
    return {
        "valr_bw_s": round(valr, 2),
        "vilr_bw_s": round(vilr, 2),
        "peak_grf_bw": round(peak_grf, 2)
    }

def biomech_pennate_muscle_aponeurosis(muscle_thickness_mm: float, fascicle_length_mm: float) -> Dict[str, float]:
    """Calculates muscle architectural pennation angle and aponeurosis gear ratio."""
    t = float(muscle_thickness_mm)
    l = float(fascicle_length_mm)
    if l <= 0 or t > l:
        return {"pennation_angle_deg": 0.0, "tendon_force_multiplier": 1.0}
    sin_alpha = t / l
    alpha_rad = math.asin(sin_alpha)
    alpha_deg = math.degrees(alpha_rad)
    cos_alpha = math.cos(alpha_rad)
    return {
        "pennation_angle_deg": round(alpha_deg, 2),
        "tendon_force_multiplier": round(cos_alpha, 4)
    }

def biomech_joint_contact_force(joint_moment_nm: float, moment_arm_m: float, joint_reaction_force_n: float) -> Dict[str, float]:
    """Calculates total compressive joint contact force F_contact = (M_joint / r_muscle) + F_reaction."""
    m = abs(float(joint_moment_nm))
    r = float(moment_arm_m)
    rx = float(joint_reaction_force_n)
    if r <= 0:
        return {"muscle_force_n": 0.0, "joint_contact_force_n": 0.0}
    f_muscle = m / r
    f_contact = f_muscle + rx
    return {
        "muscle_force_n": round(f_muscle, 2),
        "joint_contact_force_n": round(f_contact, 2)
    }

def biomech_gait_froude_number(velocity_m_s: float, leg_length_m: float) -> Dict[str, Any]:
    """Calculates Froude number Fr = v^2 / (g * L) and classifies dynamic gait regime."""
    v = float(velocity_m_s)
    l = float(leg_length_m)
    g = 9.80665
    if l <= 0:
        return {"froude_number": 0.0, "gait_regime": "unknown"}
    fr = (v ** 2) / (g * l)
    regime = "Walking" if fr < 0.5 else "Running / Galloping"
    return {
        "froude_number": round(fr, 3),
        "gait_regime": regime
    }

class BiomechanicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "BiomechanicsRuntime",
    "biomech_joint_moment",
    "biomech_center_of_mass",
    "biomech_grf_impulse",
    "biomech_muscle_tendon_force",
    "biomech_hills_muscle_force_velocity",
    "biomech_segment_moment_of_inertia_cylinder",
    "biomech_inverse_dynamics_2d_segment",
    "biomech_muscle_mechanical_work_power",
    "biomech_vertical_loading_rate",
    "biomech_pennate_muscle_aponeurosis",
    "biomech_joint_contact_force",
    "biomech_gait_froude_number"
]
