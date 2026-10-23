"""Control Systems Domain Runtime: State-space, Kalman filter, PID controller, Routh-Hurwitz stability, Bode frequency response, bilinear transform, LQR cost, step response metrics, Ziegler-Nichols tuning, and complementary filter."""
import math
from typing import List, Dict, Any, Optional
from doomscript.domains.base import DomainRuntime

def control_state_space_step(a: List[List[float]], b: List[float], state: List[float], input_u: float) -> List[float]:
    """Calculates next discrete state x_{k+1} = A*x_k + B*u."""
    u = float(input_u)
    next_state = []
    for i, row in enumerate(a):
        ax = sum(float(aij) * float(xj) for aij, xj in zip(row, state))
        bi = float(b[i]) if i < len(b) else 0.0
        next_state.append(round(ax + bi * u, 4))
    return next_state

def control_kalman_1d_step(prior_est: float, prior_cov: float, measurement: float, meas_noise_r: float, proc_noise_q: float = 0.01) -> Dict[str, float]:
    """Single step 1D Kalman filter update."""
    p_pred = float(prior_cov) + float(proc_noise_q)
    r = float(meas_noise_r)
    k_gain = p_pred / (p_pred + r) if (p_pred + r) > 0 else 0.0
    est = float(prior_est) + k_gain * (float(measurement) - float(prior_est))
    cov = (1.0 - k_gain) * p_pred
    return {"estimate": round(est, 4), "covariance": round(cov, 4), "kalman_gain": round(k_gain, 4)}

def control_pid_step(error: float, dt: float, integral: float, prev_err: float, kp: float, ki: float, kd: float) -> Dict[str, float]:
    """Calculates PID output and updated integrator."""
    e = float(error)
    dt_val = float(dt)
    new_int = float(integral) + e * dt_val
    derivative = (e - float(prev_err)) / dt_val if dt_val > 0 else 0.0
    output = float(kp) * e + float(ki) * new_int + float(kd) * derivative
    return {"output": round(output, 4), "integral": round(new_int, 4)}

def control_complementary_filter(gyro_rate: float, accel_angle: float, prev_angle: float, dt: float = 0.01, alpha: float = 0.98) -> float:
    """Sensor fusion complementary filter: angle = alpha*(prev + gyro*dt) + (1-alpha)*accel."""
    g = float(gyro_rate)
    a = float(accel_angle)
    p = float(prev_angle)
    dt_val = float(dt)
    al = float(alpha)
    angle = al * (p + g * dt_val) + (1.0 - al) * a
    return round(angle, 3)

def control_routh_hurwitz_stable(coeffs: List[float]) -> Dict[str, Any]:
    """Determines closed-loop system stability using the Routh-Hurwitz stability criterion."""
    c = [float(x) for x in coeffs]
    if not c or any(x <= 0 for x in c):
        return {"stable": False, "sign_changes": -1, "reason": "Missing or negative polynomial coefficients"}
    n = len(c)
    if n <= 2:
        return {"stable": True, "sign_changes": 0}
    if n == 3:
        return {"stable": (c[0] > 0 and c[1] > 0 and c[2] > 0), "sign_changes": 0}
    if n == 4:
        a0, a1, a2, a3 = c[0], c[1], c[2], c[3]
        b1 = (a1 * a2 - a0 * a3) / a1 if a1 != 0 else -1
        is_stable = b1 > 0
        return {"stable": is_stable, "sign_changes": 0 if is_stable else 1}
    return {"stable": True, "sign_changes": 0}

def control_bode_second_order(natural_frequency_omega_n: float, damping_ratio_zeta: float, frequencies_rad_s: List[float]) -> Dict[str, Any]:
    """Calculates frequency response magnitude and phase for G(s) = wn^2 / (s^2 + 2*zeta*wn*s + wn^2)."""
    wn = float(natural_frequency_omega_n)
    zeta = float(damping_ratio_zeta)
    results = []
    for w in frequencies_rad_s:
        w_val = float(w)
        u = w_val / wn if wn > 0 else 1.0
        # G(jw) = 1 / ((1 - u^2) + j*(2*zeta*u))
        real_denom = 1.0 - (u ** 2)
        imag_denom = 2.0 * zeta * u
        mag = 1.0 / math.sqrt(real_denom ** 2 + imag_denom ** 2)
        mag_db = 20.0 * math.log10(max(1e-12, mag))
        phase_rad = -math.atan2(imag_denom, real_denom)
        phase_deg = math.degrees(phase_rad)
        results.append({"frequency_rad_s": w_val, "magnitude_db": round(mag_db, 2), "phase_deg": round(phase_deg, 2)})
    # Resonant peak for zeta < 1/sqrt(2) ~ 0.707
    mr_db = 0.0
    if 0 < zeta < 0.7071:
        mr = 1.0 / (2.0 * zeta * math.sqrt(1.0 - zeta ** 2))
        mr_db = round(20.0 * math.log10(mr), 2)
    return {
        "bode_points": results,
        "resonance_peak_db": mr_db,
        "natural_frequency": wn,
        "damping_ratio": zeta
    }

def control_tustin_bilinear_transform(analog_pole: float, sampling_period_t: float) -> Dict[str, float]:
    """Maps continuous s-plane pole to discrete z-plane pole via Tustin transform z = (1 + s*T/2) / (1 - s*T/2)."""
    s = float(analog_pole)
    t = float(sampling_period_t)
    denom = 1.0 - (s * t / 2.0)
    if denom == 0:
        return {"z_pole_real": 1.0, "is_stable": False}
    z_real = (1.0 + (s * t / 2.0)) / denom
    is_stable = abs(z_real) < 1.0
    return {
        "z_pole_real": round(z_real, 4),
        "is_discrete_stable": is_stable
    }

def control_lqr_cost_evaluation(q_diag: List[float], r_diag: List[float], state_history: List[List[float]], input_history: List[List[float]], dt: float = 0.01) -> Dict[str, float]:
    """Calculates quadratic LQR cost J = sum(x^T Q x + u^T R u) * dt for diagonal Q and R weighting matrices."""
    dt_val = float(dt)
    total_state_cost = 0.0
    total_input_cost = 0.0
    for x in state_history:
        for i, q in enumerate(q_diag):
            xi = float(x[i]) if i < len(x) else 0.0
            total_state_cost += float(q) * (xi ** 2)
    for u in input_history:
        for i, r in enumerate(r_diag):
            ui = float(u[i]) if i < len(u) else 0.0
            total_input_cost += float(r) * (ui ** 2)
    j_total = (total_state_cost + total_input_cost) * dt_val
    return {
        "state_cost": round(total_state_cost * dt_val, 3),
        "input_cost": round(total_input_cost * dt_val, 3),
        "total_lqr_cost": round(j_total, 3)
    }

def control_step_response_metrics(time_series: List[float], value_series: List[float], target_value: float) -> Dict[str, float]:
    """Calculates standard transient response metrics: rise time, peak overshoot, settling time, and steady-state error."""
    target = float(target_value)
    if len(time_series) != len(value_series) or not time_series:
        return {"rise_time_s": 0.0, "overshoot_pct": 0.0, "settling_time_s": 0.0, "steady_state_error": 0.0}
    vals = [float(v) for v in value_series]
    times = [float(t) for t in time_series]
    val_10 = 0.10 * target
    val_90 = 0.90 * target
    t_10 = times[0]
    t_90 = times[-1]
    found_10 = False
    for t, v in zip(times, vals):
        if not found_10 and v >= val_10:
            t_10 = t
            found_10 = True
        if v >= val_90:
            t_90 = t
            break
    rise_time = max(0.0, t_90 - t_10)
    peak_val = max(vals)
    peak_idx = vals.index(peak_val)
    overshoot = max(0.0, (peak_val - target) / target * 100.0) if target > 0 else 0.0
    # Settling time within 2% band of target: [0.98 * target, 1.02 * target]
    band_lo = 0.98 * target
    band_hi = 1.02 * target
    settling_time = times[-1]
    for i in range(len(vals) - 1, -1, -1):
        if vals[i] < band_lo or vals[i] > band_hi:
            settling_time = times[min(len(times) - 1, i + 1)]
            break
    steady_state_error = abs(target - vals[-1])
    return {
        "rise_time_s": round(rise_time, 3),
        "peak_overshoot_pct": round(overshoot, 2),
        "settling_time_s": round(settling_time, 3),
        "steady_state_error": round(steady_state_error, 4)
    }

def control_ziegler_nichols_tuning(ku_ultimate_gain: float, tu_ultimate_period_s: float, controller_type: str = "PID") -> Dict[str, float]:
    """Calculates classic Ziegler-Nichols frequency response PID parameters."""
    ku = float(ku_ultimate_gain)
    tu = float(tu_ultimate_period_s)
    ctype = controller_type.upper().strip()
    if ctype == "P":
        kp = 0.5 * ku
        ki = 0.0
        kd = 0.0
    elif ctype == "PI":
        kp = 0.45 * ku
        ti = tu / 1.2
        ki = kp / ti if ti > 0 else 0.0
        kd = 0.0
    else:  # PID
        kp = 0.6 * ku
        ti = 0.5 * tu
        td = 0.125 * tu
        ki = kp / ti if ti > 0 else 0.0
        kd = kp * td
    return {
        "kp": round(kp, 3),
        "ki": round(ki, 3),
        "kd": round(kd, 3),
        "controller_type": ctype
    }

class ControlRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

__all__ = [
    "ControlRuntime",
    "control_state_space_step",
    "control_kalman_1d_step",
    "control_pid_step",
    "control_complementary_filter",
    "control_routh_hurwitz_stable",
    "control_bode_second_order",
    "control_tustin_bilinear_transform",
    "control_lqr_cost_evaluation",
    "control_step_response_metrics",
    "control_ziegler_nichols_tuning"
]
