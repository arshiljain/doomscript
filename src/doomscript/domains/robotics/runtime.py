"""Robotics Forward/Inverse Kinematics, Trajectory Planning, and Kalman Filter for DoomScript."""

import math
from typing import List, Dict, Any, Tuple, Optional


class DHParameter:
    """Denavit-Hartenberg (DH) parameter specification for a single link."""

    def __init__(self, theta: float, d: float, a: float, alpha: float):
        self.theta = float(theta)  # Joint angle (radians)
        self.d = float(d)          # Link offset
        self.a = float(a)          # Link length
        self.alpha = float(alpha)  # Link twist (radians)

    def transformation_matrix(self) -> List[List[float]]:
        ct, st = math.cos(self.theta), math.sin(self.theta)
        ca, sa = math.cos(self.alpha), math.sin(self.alpha)
        return [
            [ct, -st * ca, st * sa, self.a * ct],
            [st, ct * ca, -ct * sa, self.a * st],
            [0.0, sa, ca, self.d],
            [0.0, 0.0, 0.0, 1.0],
        ]


def mat4_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    C = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            C[i][j] = sum(A[i][k] * B[k][j] for k in range(4))
    return C


class ForwardKinematicsChain:
    """Multi-link serial manipulator forward kinematics."""

    def __init__(self, links: List[DHParameter]):
        self.links = links

    def compute(self) -> Dict[str, Any]:
        T = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
        joint_positions = [[0.0, 0.0, 0.0]]
        for link in self.links:
            Ti = link.transformation_matrix()
            T = mat4_mul(T, Ti)
            joint_positions.append([T[0][3], T[1][3], T[2][3]])

        end_effector = [T[0][3], T[1][3], T[2][3]]
        return {
            "end_effector": end_effector,
            "joint_positions": joint_positions,
            "transformation": T,
        }


class InverseKinematics2D:
    """Analytic and numerical IK for planar 2-link / 3-link arms."""

    @staticmethod
    def solve_2link(l1: float, l2: float, target_x: float, target_y: float) -> Optional[Dict[str, float]]:
        r_sq = target_x * target_x + target_y * target_y
        cos_theta2 = (r_sq - l1 * l1 - l2 * l2) / (2.0 * l1 * l2)
        if cos_theta2 < -1.0 or cos_theta2 > 1.0:
            return None  # Target unreachable

        sin_theta2 = math.sqrt(max(0.0, 1.0 - cos_theta2 * cos_theta2))
        theta2 = math.atan2(sin_theta2, cos_theta2)

        k1 = l1 + l2 * cos_theta2
        k2 = l2 * sin_theta2
        theta1 = math.atan2(target_y, target_x) - math.atan2(k2, k1)

        return {
            "theta1": theta1,
            "theta2": theta2,
            "theta1_deg": math.degrees(theta1),
            "theta2_deg": math.degrees(theta2),
        }


class TrajectoryPlanner:
    """Polynomial trajectory generator with velocity and acceleration constraints."""

    @staticmethod
    def cubic(q0: float, q1: float, v0: float, v1: float, t0: float, t1: float, t: float) -> float:
        dt = t1 - t0
        if dt <= 0:
            return q0
        tau = max(0.0, min(1.0, (t - t0) / dt))
        a0 = q0
        a1 = v0 * dt
        a2 = 3.0 * (q1 - q0) - (2.0 * v0 + v1) * dt
        a3 = -2.0 * (q1 - q0) + (v0 + v1) * dt
        return a0 + a1 * tau + a2 * (tau ** 2) + a3 * (tau ** 3)

    @staticmethod
    def quintic(q0: float, q1: float, v0: float, v1: float, a0: float, a1: float, t0: float, t1: float, t: float) -> float:
        dt = t1 - t0
        if dt <= 0:
            return q0
        tau = max(0.0, min(1.0, (t - t0) / dt))
        c0 = q0
        c1 = v0 * dt
        c2 = 0.5 * a0 * (dt ** 2)
        c3 = 10.0 * (q1 - q0) - (6.0 * v0 + 4.0 * v1) * dt - (1.5 * a0 - 0.5 * a1) * (dt ** 2)
        c4 = -15.0 * (q1 - q0) + (8.0 * v0 + 7.0 * v1) * dt + (1.5 * a0 - a1) * (dt ** 2)
        c5 = 6.0 * (q1 - q0) - 3.0 * (v0 + v1) * dt - 0.5 * (a0 - a1) * (dt ** 2)
        return c0 + c1 * tau + c2 * (tau ** 2) + c3 * (tau ** 3) + c4 * (tau ** 4) + c5 * (tau ** 5)


class ExtendedKalmanFilter2D:
    """2D Position and Velocity EKF tracker."""

    def __init__(self, init_x: float = 0.0, init_y: float = 0.0, process_noise: float = 0.1, measurement_noise: float = 1.0):
        # State: [x, y, vx, vy]
        self.state = [float(init_x), float(init_y), 0.0, 0.0]
        # Covariance P (4x4)
        self.P = [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 10.0, 0.0],
            [0.0, 0.0, 0.0, 10.0],
        ]
        self.Q = process_noise
        self.R = measurement_noise

    def predict(self, dt: float):
        # State extrapolation: x = x + vx * dt
        self.state[0] += self.state[2] * dt
        self.state[1] += self.state[3] * dt
        # Add process noise
        for i in range(4):
            self.P[i][i] += self.Q * dt

    def update(self, meas_x: float, meas_y: float):
        # Measurement residual y = z - Hx
        res_x = meas_x - self.state[0]
        res_y = meas_y - self.state[1]

        # S = H P H^T + R
        s_x = self.P[0][0] + self.R
        s_y = self.P[1][1] + self.R

        # Kalman Gain K = P H^T S^-1
        k_x0 = self.P[0][0] / s_x
        k_x2 = self.P[2][0] / s_x
        k_y1 = self.P[1][1] / s_y
        k_y3 = self.P[3][1] / s_y

        # Update state
        self.state[0] += k_x0 * res_x
        self.state[2] += k_x2 * res_x
        self.state[1] += k_y1 * res_y
        self.state[3] += k_y3 * res_y

        # Update covariance P = (I - KH) P
        self.P[0][0] *= (1.0 - k_x0)
        self.P[2][2] *= (1.0 - k_x0)
        self.P[1][1] *= (1.0 - k_y1)
        self.P[3][3] *= (1.0 - k_y1)

    def get_estimate(self) -> Dict[str, float]:
        return {
            "x": self.state[0],
            "y": self.state[1],
            "vx": self.state[2],
            "vy": self.state[3],
        }


def robotics_forward_kinematics(dh_params_list: List[List[float]]) -> Dict[str, Any]:
    links = [DHParameter(p[0], p[1], p[2], p[3]) for p in dh_params_list]
    chain = ForwardKinematicsChain(links)
    return chain.compute()


def robotics_inverse_kinematics_2link(l1: float, l2: float, x: float, y: float) -> Optional[Dict[str, float]]:
    return InverseKinematics2D.solve_2link(l1, l2, x, y)


def robotics_cubic_trajectory(q0: float, q1: float, v0: float, v1: float, t0: float, t1: float, t: float) -> float:
    return TrajectoryPlanner.cubic(q0, q1, v0, v1, t0, t1, t)


def robotics_create_ekf(init_x: float, init_y: float, process_noise: float = 0.1, meas_noise: float = 1.0) -> ExtendedKalmanFilter2D:
    return ExtendedKalmanFilter2D(init_x, init_y, process_noise, meas_noise)
