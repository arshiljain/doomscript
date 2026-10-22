"""Control Systems Domain Runtime: State-Space models, Kalman filter 1D step, and PID step."""
from typing import Dict, Any, List

def control_state_space_step(a: List[List[float]], b: List[float], state: List[float], input_u: float) -> List[float]:
    """Calculates next state x_{k+1} = A*x_k + B*u."""
    u = float(input_u)
    new_state = []
    for row, b_val in zip(a, b):
        val = sum(aij * xj for aij, xj in zip(row, state)) + b_val * u
        new_state.append(round(val, 4))
    return new_state

def control_kalman_step_1d(x_prior: float, p_prior: float, measurement_z: float, r_noise: float, q_noise: float = 0.0) -> Dict[str, float]:
    """Executes a 1D Kalman filter state and covariance update step."""
    x_pred = float(x_prior)
    p_pred = float(p_prior) + float(q_noise)
    r = float(r_noise)
    z = float(measurement_z)
    k_gain = p_pred / (p_pred + r) if (p_pred + r) != 0.0 else 0.0
    x_post = x_pred + k_gain * (z - x_pred)
    p_post = (1.0 - k_gain) * p_pred
    return {
        "estimate": round(x_post, 4),
        "covariance": round(p_post, 6),
        "kalman_gain": round(k_gain, 4)
    }

def control_pid_step(error: float, dt: float, integral_prev: float, error_prev: float, kp: float, ki: float, kd: float) -> Dict[str, float]:
    """Executes a discrete PID controller step."""
    e = float(error)
    dt_val = float(dt)
    integral = float(integral_prev) + e * dt_val
    derivative = (e - float(error_prev)) / dt_val if dt_val > 0.0 else 0.0
    u = float(kp) * e + float(ki) * integral + float(kd) * derivative
    return {
        "output": round(u, 4),
        "integral": round(integral, 4),
        "derivative": round(derivative, 4)
    }
