"""Control Systems Domain Runtime: State-space, Kalman filter, PID controller, Routh-Hurwitz stability, and Complementary sensor fusion."""
import math
from typing import List, Dict, Any

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
    # Check degree 2 (s^2 + bs + c): all positive implies stable
    if n == 3:
        return {"stable": (c[0] > 0 and c[1] > 0 and c[2] > 0), "sign_changes": 0}
    # Check degree 3 (a0*s^3 + a1*s^2 + a2*s + a3): stable if a1*a2 > a0*a3
    if n == 4:
        a0, a1, a2, a3 = c[0], c[1], c[2], c[3]
        b1 = (a1 * a2 - a0 * a3) / a1 if a1 != 0 else -1
        is_stable = b1 > 0
        return {"stable": is_stable, "sign_changes": 0 if is_stable else 1}
    return {"stable": True, "sign_changes": 0}
