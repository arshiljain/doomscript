"""Robotics Forward/Inverse Kinematics, Trajectory Planning, and Kalman Filter for DoomScript."""

import math
import random
from typing import List, Dict, Any, Tuple, Optional
from doomscript.core.record import Record


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


# ===========================================================================
# RAPIDLY-EXPLORING RANDOM TREE (RRT & RRT*) 2D PATH PLANNING
# ===========================================================================

class RRTNode:
    """Node in RRT motion planning tree."""

    def __init__(self, x: float, y: float, parent: Optional["RRTNode"] = None, cost: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.parent = parent
        self.cost = float(cost)


class RRTPlanner2D:
    """RRT and RRT* obstacle-aware path planner in 2D Euclidean space."""

    def __init__(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
        bounds: Tuple[float, float, float, float],  # (min_x, max_x, min_y, max_y)
        obstacles: Optional[List[Dict[str, float]]] = None,  # [{"x": 5.0, "y": 5.0, "r": 1.5}, ...]
        step_size: float = 1.0,
        goal_bias: float = 0.1,
        max_iterations: int = 1000,
    ):
        self.start = RRTNode(start[0], start[1], None, 0.0)
        self.goal = RRTNode(goal[0], goal[1], None, 0.0)
        self.bounds = bounds
        self.obstacles = obstacles or []
        self.step_size = float(step_size)
        self.goal_bias = float(goal_bias)
        self.max_iterations = int(max_iterations)
        self.nodes: List[RRTNode] = [self.start]

    def _distance(self, n1: RRTNode, n2: RRTNode) -> float:
        return math.hypot(n1.x - n2.x, n1.y - n2.y)

    def _is_collision_free(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        dist = math.hypot(x2 - x1, y2 - y1)
        steps = max(2, int(dist / (self.step_size * 0.25)))
        for s in range(steps + 1):
            t = s / steps
            px = x1 + t * (x2 - x1)
            py = y1 + t * (y2 - y1)
            for obs in self.obstacles:
                ox = obs.get("x", 0.0)
                oy = obs.get("y", 0.0)
                r = obs.get("r", 1.0)
                if math.hypot(px - ox, py - oy) <= r:
                    return False
        return True

    def plan(self, seed: Optional[int] = 42) -> Optional[List[List[float]]]:
        """Plans collision-free path from start to goal."""
        import random
        rng = random.Random(seed)
        min_x, max_x, min_y, max_y = self.bounds

        for _ in range(self.max_iterations):
            if rng.random() < self.goal_bias:
                rand_x, rand_y = self.goal.x, self.goal.y
            else:
                rand_x = rng.uniform(min_x, max_x)
                rand_y = rng.uniform(min_y, max_y)

            # Nearest node
            nearest = min(self.nodes, key=lambda n: math.hypot(n.x - rand_x, n.y - rand_y))
            dist = math.hypot(rand_x - nearest.x, rand_y - nearest.y)
            if dist < 1e-6:
                continue

            theta = math.atan2(rand_y - nearest.y, rand_x - nearest.x)
            step = min(self.step_size, dist)
            new_x = nearest.x + step * math.cos(theta)
            new_y = nearest.y + step * math.sin(theta)

            if not (min_x <= new_x <= max_x and min_y <= new_y <= max_y):
                continue

            if self._is_collision_free(nearest.x, nearest.y, new_x, new_y):
                new_node = RRTNode(new_x, new_y, parent=nearest, cost=nearest.cost + step)
                self.nodes.append(new_node)

                # Check goal reachability
                if math.hypot(new_x - self.goal.x, new_y - self.goal.y) <= self.step_size:
                    if self._is_collision_free(new_x, new_y, self.goal.x, self.goal.y):
                        self.goal.parent = new_node
                        self.goal.cost = new_node.cost + math.hypot(new_x - self.goal.x, new_y - self.goal.y)
                        self.nodes.append(self.goal)
                        # Reconstruct path
                        path = []
                        curr: Optional[RRTNode] = self.goal
                        while curr:
                            path.append([round(curr.x, 4), round(curr.y, 4)])
                            curr = curr.parent
                        path.reverse()
                        return path

        return None

    def plan_star(self, search_radius: float = 2.5, seed: Optional[int] = 42) -> Optional[List[List[float]]]:
        """RRT* implementation with neighborhood rewiring for path cost optimization."""
        import random
        rng = random.Random(seed)
        min_x, max_x, min_y, max_y = self.bounds
        best_goal_node: Optional[RRTNode] = None

        for _ in range(self.max_iterations):
            if rng.random() < self.goal_bias:
                rand_x, rand_y = self.goal.x, self.goal.y
            else:
                rand_x = rng.uniform(min_x, max_x)
                rand_y = rng.uniform(min_y, max_y)

            nearest = min(self.nodes, key=lambda n: math.hypot(n.x - rand_x, n.y - rand_y))
            dist = math.hypot(rand_x - nearest.x, rand_y - nearest.y)
            if dist < 1e-6:
                continue

            theta = math.atan2(rand_y - nearest.y, rand_x - nearest.x)
            step = min(self.step_size, dist)
            new_x = nearest.x + step * math.cos(theta)
            new_y = nearest.y + step * math.sin(theta)

            if not (min_x <= new_x <= max_x and min_y <= new_y <= max_y):
                continue

            if not self._is_collision_free(nearest.x, nearest.y, new_x, new_y):
                continue

            # Find near neighbors within search_radius
            near_nodes = [
                n for n in self.nodes
                if math.hypot(n.x - new_x, n.y - new_y) <= search_radius
                and self._is_collision_free(n.x, n.y, new_x, new_y)
            ]

            min_cost_node = nearest
            min_cost = nearest.cost + math.hypot(nearest.x - new_x, nearest.y - new_y)
            for n in near_nodes:
                c = n.cost + math.hypot(n.x - new_x, n.y - new_y)
                if c < min_cost:
                    min_cost = c
                    min_cost_node = n

            new_node = RRTNode(new_x, new_y, parent=min_cost_node, cost=min_cost)
            self.nodes.append(new_node)

            # Rewire tree
            for n in near_nodes:
                dist_new_to_n = math.hypot(new_x - n.x, new_y - n.y)
                if new_node.cost + dist_new_to_n < n.cost:
                    if self._is_collision_free(new_x, new_y, n.x, n.y):
                        n.parent = new_node
                        n.cost = new_node.cost + dist_new_to_n

            # Check goal connection
            dist_to_goal = math.hypot(new_x - self.goal.x, new_y - self.goal.y)
            if dist_to_goal <= self.step_size and self._is_collision_free(new_x, new_y, self.goal.x, self.goal.y):
                goal_cost = new_node.cost + dist_to_goal
                if best_goal_node is None or goal_cost < best_goal_node.cost:
                    best_goal_node = RRTNode(self.goal.x, self.goal.y, parent=new_node, cost=goal_cost)

        if best_goal_node:
            path = []
            curr: Optional[RRTNode] = best_goal_node
            while curr:
                path.append([round(curr.x, 4), round(curr.y, 4)])
                curr = curr.parent
            path.reverse()
            return path
        return None


# ===========================================================================
# ARTIFICIAL POTENTIAL FIELD (APF) REAL-TIME NAVIGATION
# ===========================================================================

class ArtificialPotentialField2D:
    """Artificial Potential Field algorithm for reactive mobile robot navigation."""

    def __init__(
        self,
        goal: Tuple[float, float],
        obstacles: Optional[List[Dict[str, float]]] = None,
        k_att: float = 1.0,
        k_rep: float = 100.0,
        influence_radius: float = 3.0,
    ):
        self.goal = goal
        self.obstacles = obstacles or []
        self.k_att = float(k_att)
        self.k_rep = float(k_rep)
        self.d0 = float(influence_radius)

    def compute_force(self, position: Tuple[float, float]) -> Dict[str, float]:
        """Computes net attractive and repulsive force vector at given position."""
        px, py = position
        gx, gy = self.goal

        # Attractive force F_att = -k_att * (p - goal)
        dist_goal = math.hypot(gx - px, gy - py)
        if dist_goal > 0:
            f_att_x = self.k_att * (gx - px)
            f_att_y = self.k_att * (gy - py)
        else:
            f_att_x, f_att_y = 0.0, 0.0

        # Repulsive force sum over obstacles
        f_rep_x, f_rep_y = 0.0, 0.0
        for obs in self.obstacles:
            ox, oy = obs.get("x", 0.0), obs.get("y", 0.0)
            d = math.hypot(px - ox, py - oy)
            if 0 < d < self.d0:
                # F_rep = k_rep * (1/d - 1/d0) * (1/d^2) * ( (p - obs) / d )
                scale = self.k_rep * (1.0 / d - 1.0 / self.d0) * (1.0 / (d * d))
                f_rep_x += scale * (px - ox) / d
                f_rep_y += scale * (py - oy) / d

        fx = f_att_x + f_rep_x
        fy = f_att_y + f_rep_y
        magnitude = math.hypot(fx, fy)
        heading = math.atan2(fy, fx) if magnitude > 1e-6 else 0.0

        return {
            "fx": round(fx, 4),
            "fy": round(fy, 4),
            "f_att_x": round(f_att_x, 4),
            "f_att_y": round(f_att_y, 4),
            "f_rep_x": round(f_rep_x, 4),
            "f_rep_y": round(f_rep_y, 4),
            "magnitude": round(magnitude, 4),
            "heading": round(heading, 4),
            "heading_deg": round(math.degrees(heading), 2),
        }

    def simulate_path(
        self,
        start: Tuple[float, float],
        max_steps: int = 500,
        step_size: float = 0.1,
        goal_tolerance: float = 0.2,
    ) -> Dict[str, Any]:
        """Simulates path following gradient descent of potential field."""
        curr = list(start)
        path = [[round(curr[0], 4), round(curr[1], 4)]]
        reached = False

        for _ in range(max_steps):
            dist_goal = math.hypot(self.goal[0] - curr[0], self.goal[1] - curr[1])
            if dist_goal <= goal_tolerance:
                reached = True
                break

            forces = self.compute_force((curr[0], curr[1]))
            mag = forces["magnitude"]
            if mag < 1e-6:
                # Local minimum or saddle point reached
                break

            curr[0] += step_size * (forces["fx"] / mag)
            curr[1] += step_size * (forces["fy"] / mag)
            path.append([round(curr[0], 4), round(curr[1], 4)])

        return {
            "path": path,
            "steps": len(path) - 1,
            "reached_goal": reached,
            "final_distance": round(math.hypot(self.goal[0] - curr[0], self.goal[1] - curr[1]), 4),
        }


# ===========================================================================
# DIFFERENTIAL DRIVE & UNICYCLE ODOMETRY & PURE PURSUIT TRACKING
# ===========================================================================

class DifferentialDriveKinematics:
    """Forward & Inverse kinematics for 2-wheeled differential drive mobile robots."""

    def __init__(self, wheel_radius: float = 0.05, wheel_base: float = 0.2):
        self.r = float(wheel_radius)
        self.L = float(wheel_base)

    def forward(self, omega_left: float, omega_right: float) -> Tuple[float, float]:
        """Calculates linear velocity v (m/s) and angular velocity w (rad/s) from wheel speeds."""
        v = (self.r / 2.0) * (omega_right + omega_left)
        w = (self.r / self.L) * (omega_right - omega_left)
        return round(v, 4), round(w, 4)

    def inverse(self, v: float, w: float) -> Tuple[float, float]:
        """Calculates wheel angular speeds (left, right) required for desired (v, w)."""
        omega_left = (v - (self.L * w / 2.0)) / self.r
        omega_right = (v + (self.L * w / 2.0)) / self.r
        return round(omega_left, 4), round(omega_right, 4)

    def integrate_odometry(
        self,
        pose: Tuple[float, float, float],  # (x, y, theta_rad)
        v: float,
        w: float,
        dt: float,
    ) -> Tuple[float, float, float]:
        """Integrates 2nd-order Runge-Kutta odometry over time step dt."""
        x, y, theta = pose
        if abs(w) < 1e-6:
            new_x = x + v * math.cos(theta) * dt
            new_y = y + v * math.sin(theta) * dt
            new_theta = theta
        else:
            # Exact circular arc integration
            new_theta = theta + w * dt
            new_x = x + (v / w) * (math.sin(new_theta) - math.sin(theta))
            new_y = y - (v / w) * (math.cos(new_theta) - math.cos(theta))

        # Normalize theta to [-pi, pi]
        new_theta = (new_theta + math.pi) % (2.0 * math.pi) - math.pi
        return round(new_x, 4), round(new_y, 4), round(new_theta, 4)


class PurePursuitController:
    """Geometric Pure Pursuit path tracking algorithm for unicycle mobile robots."""

    def __init__(self, lookahead_distance: float = 1.0, max_steering_angle: float = math.pi / 4):
        self.ld = float(lookahead_distance)
        self.max_steer = float(max_steering_angle)

    def compute_steering(
        self,
        robot_pose: Tuple[float, float, float],  # (x, y, theta_rad)
        path: List[List[float]],
    ) -> Dict[str, float]:
        """Computes path-tracking steering curvature and target lookahead point."""
        rx, ry, rtheta = robot_pose

        # Find lookahead target along path
        target = path[-1]
        for pt in path:
            dist = math.hypot(pt[0] - rx, pt[1] - ry)
            if dist >= self.ld:
                target = pt
                break

        # Transform target to robot frame
        dx = target[0] - rx
        dy = target[1] - ry
        # Angle from robot heading to target
        alpha = math.atan2(dy, dx) - rtheta
        # Normalize alpha to [-pi, pi]
        alpha = (alpha + math.pi) % (2.0 * math.pi) - math.pi

        # Curvature kappa = 2 * sin(alpha) / ld
        curvature = 2.0 * math.sin(alpha) / self.ld
        steer_angle = math.atan(curvature * self.ld)
        steer_angle = max(-self.max_steer, min(self.max_steer, steer_angle))

        return {
            "curvature": round(curvature, 4),
            "steering_angle": round(steer_angle, 4),
            "steering_angle_deg": round(math.degrees(steer_angle), 2),
            "lookahead_x": round(target[0], 4),
            "lookahead_y": round(target[1], 4),
            "alpha": round(alpha, 4),
        }


# ===========================================================================
# STEWART PLATFORM (6-DOF PARALLEL HEXAPOD MANIPULATOR) INVERSE KINEMATICS
# ===========================================================================

class StewartPlatformIK:
    """Computes exact actuator leg lengths for a 6-DOF Stewart-Gough parallel platform."""

    def __init__(
        self,
        base_radius: float = 1.0,
        platform_radius: float = 0.5,
        base_angles_deg: Optional[List[float]] = None,
        platform_angles_deg: Optional[List[float]] = None,
    ):
        self.rb = float(base_radius)
        self.rp = float(platform_radius)

        # Standard 6-joint attachment angle distributions (hexagonal paired layout)
        if base_angles_deg is None:
            base_angles_deg = [10.0, 50.0, 130.0, 170.0, 250.0, 290.0]
        if platform_angles_deg is None:
            platform_angles_deg = [30.0, 30.0, 150.0, 150.0, 270.0, 270.0]

        self.base_anchors: List[List[float]] = []
        for a in base_angles_deg:
            rad = math.radians(a)
            self.base_anchors.append([self.rb * math.cos(rad), self.rb * math.sin(rad), 0.0])

        self.plat_anchors: List[List[float]] = []
        for a in platform_angles_deg:
            rad = math.radians(a)
            self.plat_anchors.append([self.rp * math.cos(rad), self.rp * math.sin(rad), 0.0])

    def solve_leg_lengths(
        self,
        translation: Tuple[float, float, float],  # (tx, ty, tz)
        rotation_deg: Tuple[float, float, float],  # (roll_x, pitch_y, yaw_z)
    ) -> List[float]:
        """Calculates Euclidean lengths of all 6 actuator legs for given 6-DOF pose."""
        tx, ty, tz = translation
        rx = math.radians(rotation_deg[0])
        ry = math.radians(rotation_deg[1])
        rz = math.radians(rotation_deg[2])

        # Euler Z-Y-X Rotation Matrix R
        cx, sx = math.cos(rx), math.sin(rx)
        cy, sy = math.cos(ry), math.sin(ry)
        cz, sz = math.cos(rz), math.sin(rz)

        R = [
            [cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
            [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
            [-sy, cy * sx, cy * cx],
        ]

        leg_lengths: List[float] = []
        for i in range(6):
            p = self.plat_anchors[i]
            b = self.base_anchors[i]

            # Transformed platform anchor: q_i = T + R * p_i
            qx = tx + (R[0][0] * p[0] + R[0][1] * p[1] + R[0][2] * p[2])
            qy = ty + (R[1][0] * p[0] + R[1][1] * p[1] + R[1][2] * p[2])
            qz = tz + (R[2][0] * p[0] + R[2][1] * p[1] + R[2][2] * p[2])

            # Leg vector L_i = q_i - b_i
            lx = qx - b[0]
            ly = qy - b[1]
            lz = qz - b[2]
            length = math.sqrt(lx * lx + ly * ly + lz * lz)
            leg_lengths.append(round(length, 4))

        return leg_lengths


# ===========================================================================
# TRAPEZOIDAL VELOCITY PROFILE MOTION CONTROLLER
# ===========================================================================

class TrapezoidalVelocityProfile:
    """1D and multi-axis trapezoidal velocity trajectory profile generator."""

    def __init__(self, max_velocity: float, max_acceleration: float):
        self.v_max = float(max_velocity)
        self.a_max = float(max_acceleration)

    def plan(self, distance: float) -> Dict[str, Any]:
        """Calculates acceleration time, cruise time, deceleration time, and total duration."""
        d = abs(float(distance))
        if d < 1e-9:
            return {"total_time": 0.0, "t_acc": 0.0, "t_cruise": 0.0, "v_peak": 0.0, "triangular": True}

        # Distance to reach v_max from rest: d_acc = v_max^2 / (2 * a_max)
        d_acc = (self.v_max ** 2) / (2.0 * self.a_max)

        if 2.0 * d_acc > d:
            # Triangular profile: v_max is not reached
            v_peak = math.sqrt(d * self.a_max)
            t_acc = v_peak / self.a_max
            t_cruise = 0.0
            total_time = 2.0 * t_acc
            triangular = True
        else:
            # Standard trapezoidal profile
            v_peak = self.v_max
            t_acc = self.v_max / self.a_max
            d_cruise = d - 2.0 * d_acc
            t_cruise = d_cruise / self.v_max
            total_time = 2.0 * t_acc + t_cruise
            triangular = False

        return {
            "total_time": round(total_time, 4),
            "t_acc": round(t_acc, 4),
            "t_cruise": round(t_cruise, 4),
            "v_peak": round(v_peak, 4),
            "triangular": triangular,
        }

    def sample(self, distance: float, t: float) -> Dict[str, float]:
        """Evaluates position, velocity, and acceleration at time t."""
        plan = self.plan(distance)
        t_acc = plan["t_acc"]
        t_cruise = plan["t_cruise"]
        v_peak = plan["v_peak"]
        total_t = plan["total_time"]
        sign = 1.0 if distance >= 0 else -1.0

        if t <= 0.0:
            return {"position": 0.0, "velocity": 0.0, "acceleration": 0.0}
        elif t >= total_t:
            return {"position": float(distance), "velocity": 0.0, "acceleration": 0.0}

        if t < t_acc:
            # Acceleration phase
            pos = 0.5 * self.a_max * (t ** 2)
            vel = self.a_max * t
            acc = self.a_max
        elif t < t_acc + t_cruise:
            # Cruise phase
            d_acc = 0.5 * self.a_max * (t_acc ** 2)
            pos = d_acc + v_peak * (t - t_acc)
            vel = v_peak
            acc = 0.0
        else:
            # Deceleration phase
            t_dec = t - (t_acc + t_cruise)
            d_acc = 0.5 * self.a_max * (t_acc ** 2)
            d_cruise = v_peak * t_cruise
            pos = d_acc + d_cruise + v_peak * t_dec - 0.5 * self.a_max * (t_dec ** 2)
            vel = v_peak - self.a_max * t_dec
            acc = -self.a_max

        return {
            "position": round(sign * pos, 4),
            "velocity": round(sign * vel, 4),
            "acceleration": round(sign * acc, 4),
        }


# High-level domain entrypoints
def robotics_rrt_plan(
    start: List[float],
    goal: List[float],
    bounds: List[float],
    obstacles: Optional[List[Dict[str, float]]] = None,
    step_size: float = 1.0,
    seed: int = 42,
) -> Optional[List[List[float]]]:
    planner = RRTPlanner2D((start[0], start[1]), (goal[0], goal[1]), (bounds[0], bounds[1], bounds[2], bounds[3]), obstacles, step_size)
    return planner.plan(seed=seed)


def robotics_rrt_star_plan(
    start: List[float],
    goal: List[float],
    bounds: List[float],
    obstacles: Optional[List[Dict[str, float]]] = None,
    step_size: float = 1.0,
    search_radius: float = 2.5,
    seed: int = 42,
) -> Optional[List[List[float]]]:
    planner = RRTPlanner2D((start[0], start[1]), (goal[0], goal[1]), (bounds[0], bounds[1], bounds[2], bounds[3]), obstacles, step_size)
    return planner.plan_star(search_radius=search_radius, seed=seed)


def robotics_apf_forces(
    position: List[float],
    goal: List[float],
    obstacles: Optional[List[Dict[str, float]]] = None,
    k_att: float = 1.0,
    k_rep: float = 100.0,
    influence_radius: float = 3.0,
) -> Any:
    apf = ArtificialPotentialField2D((goal[0], goal[1]), obstacles, k_att, k_rep, influence_radius)
    return Record(apf.compute_force((position[0], position[1])))


def robotics_diff_drive_forward(omega_left: float, omega_right: float, wheel_radius: float = 0.05, wheel_base: float = 0.2) -> Tuple[float, float]:
    dd = DifferentialDriveKinematics(wheel_radius, wheel_base)
    return dd.forward(omega_left, omega_right)


def robotics_diff_drive_odometry(pose: List[float], v: float, w: float, dt: float, wheel_radius: float = 0.05, wheel_base: float = 0.2) -> Tuple[float, float, float]:
    dd = DifferentialDriveKinematics(wheel_radius, wheel_base)
    return dd.integrate_odometry((pose[0], pose[1], pose[2]), v, w, dt)


def robotics_pure_pursuit(pose: List[float], path: List[List[float]], lookahead: float = 1.0) -> Any:
    pp = PurePursuitController(lookahead_distance=lookahead)
    return Record(pp.compute_steering((pose[0], pose[1], pose[2]), path))


def robotics_stewart_platform_ik(translation: List[float], rotation_deg: List[float], base_radius: float = 1.0, platform_radius: float = 0.5) -> List[float]:
    sp = StewartPlatformIK(base_radius, platform_radius)
    return sp.solve_leg_lengths((translation[0], translation[1], translation[2]), (rotation_deg[0], rotation_deg[1], rotation_deg[2]))


def robotics_trapezoidal_profile(distance: float, max_v: float, max_a: float) -> Any:
    prof = TrapezoidalVelocityProfile(max_v, max_a)
    return Record(prof.plan(distance))


# ==============================================================================
# DUBINS NON-HOLONOMIC TRAJECTORY PLANNING & OCCUPANCY GRID MAPPING
# ==============================================================================

def _mod2pi(theta: float) -> float:
    return theta - 2.0 * math.pi * math.floor(theta / (2.0 * math.pi))


class DubinsCarShortestPath:
    """Exact analytical Dubins path generator for non-holonomic vehicles with minimum turning radius."""

    @classmethod
    def _lsl(cls, alpha: float, beta: float, d: float) -> Tuple[bool, float, float, float]:
        ca, sa = math.cos(alpha), math.sin(alpha)
        cb, sb = math.cos(beta), math.sin(beta)
        tmp = 2.0 + d * d - (2.0 * (ca * cb + sa * sb - d * (sa - sb)))
        if tmp < 0:
            return False, 0.0, 0.0, 0.0
        theta = math.atan2(cb - ca, d + sa - sb)
        t = _mod2pi(-alpha + theta)
        p = math.sqrt(max(0.0, tmp))
        q = _mod2pi(beta - theta)
        return True, t, p, q

    @classmethod
    def _rsr(cls, alpha: float, beta: float, d: float) -> Tuple[bool, float, float, float]:
        ca, sa = math.cos(alpha), math.sin(alpha)
        cb, sb = math.cos(beta), math.sin(beta)
        tmp = 2.0 + d * d - (2.0 * (ca * cb + sa * sb - d * (sb - sa)))
        if tmp < 0:
            return False, 0.0, 0.0, 0.0
        theta = math.atan2(ca - cb, d - sa + sb)
        t = _mod2pi(alpha - theta)
        p = math.sqrt(max(0.0, tmp))
        q = _mod2pi(-beta + theta)
        return True, t, p, q

    @classmethod
    def _lsr(cls, alpha: float, beta: float, d: float) -> Tuple[bool, float, float, float]:
        ca, sa = math.cos(alpha), math.sin(alpha)
        cb, sb = math.cos(beta), math.sin(beta)
        tmp = -2.0 + d * d + (2.0 * (ca * cb + sa * sb + d * (sa + sb)))
        if tmp < 0:
            return False, 0.0, 0.0, 0.0
        p = math.sqrt(max(0.0, tmp))
        theta = math.atan2(-ca - cb, d + sa + sb) - math.atan2(-2.0, p)
        t = _mod2pi(-alpha + theta)
        q = _mod2pi(-_mod2pi(beta) + theta)
        return True, t, p, q

    @classmethod
    def _rsl(cls, alpha: float, beta: float, d: float) -> Tuple[bool, float, float, float]:
        ca, sa = math.cos(alpha), math.sin(alpha)
        cb, sb = math.cos(beta), math.sin(beta)
        tmp = d * d - 2.0 + (2.0 * (ca * cb + sa * sb - d * (sa + sb)))
        if tmp < 0:
            return False, 0.0, 0.0, 0.0
        p = math.sqrt(max(0.0, tmp))
        theta = math.atan2(ca + cb, d - sa - sb) - math.atan2(2.0, p)
        t = _mod2pi(alpha - theta)
        q = _mod2pi(beta - theta)
        return True, t, p, q

    @classmethod
    def plan(
        cls,
        start: Tuple[float, float, float],
        goal: Tuple[float, float, float],
        turning_radius: float = 1.0,
        step_size: float = 0.2,
    ) -> Record:
        """Finds minimum length Dubins path connecting start and goal poses (x, y, heading_rad)."""
        x1, y1, th1 = float(start[0]), float(start[1]), float(start[2])
        x2, y2, th2 = float(goal[0]), float(goal[1]), float(goal[2])
        R = max(0.01, float(turning_radius))

        dx = x2 - x1
        dy = y2 - y1
        D = math.hypot(dx, dy)
        d = D / R

        # Angle of line of sight
        theta_los = math.atan2(dy, dx)
        alpha = _mod2pi(th1 - theta_los)
        beta = _mod2pi(th2 - theta_los)

        planners = [
            ("LSL", cls._lsl),
            ("RSR", cls._rsr),
            ("LSR", cls._lsr),
            ("RSL", cls._rsl),
        ]

        best_cost = float("inf")
        best_type = "LSL"
        best_lengths = (0.0, 0.0, 0.0)

        for name, solver in planners:
            ok, t, p, q = solver(alpha, beta, d)
            if ok:
                cost = (t + p + q) * R
                if cost < best_cost:
                    best_cost = cost
                    best_type = name
                    best_lengths = (t * R, p * R, q * R)

        # Generate interpolated waypoint trajectory
        waypoints = [[round(x1, 4), round(y1, 4), round(th1, 4)]]
        curr_x, curr_y, curr_th = x1, y1, th1

        def _step_segment(seg_type: str, seg_len: float):
            nonlocal curr_x, curr_y, curr_th
            n_pts = max(1, int(seg_len / step_size))
            dt = seg_len / n_pts
            for _ in range(n_pts):
                if seg_type == "L":
                    curr_th += dt / R
                    curr_x += dt * math.cos(curr_th)
                    curr_y += dt * math.sin(curr_th)
                elif seg_type == "R":
                    curr_th -= dt / R
                    curr_x += dt * math.cos(curr_th)
                    curr_y += dt * math.sin(curr_th)
                else:  # 'S'
                    curr_x += dt * math.cos(curr_th)
                    curr_y += dt * math.sin(curr_th)
                waypoints.append([round(curr_x, 4), round(curr_y, 4), round(curr_th, 4)])

        _step_segment(best_type[0], best_lengths[0])
        _step_segment(best_type[1], best_lengths[1])
        _step_segment(best_type[2], best_lengths[2])

        return Record({
            "path_type": best_type,
            "total_length": round(best_cost, 4),
            "segment_lengths": [round(l, 4) for l in best_lengths],
            "waypoints": waypoints,
            "path": waypoints,
            "waypoints_count": len(waypoints),
            "turning_radius": R,
        })


class OccupancyGridMap2D:
    """2D Log-Odds Occupancy Grid Mapping with Bresenham Ray-Casting."""

    def __init__(
        self,
        width: int = 50,
        height: int = 50,
        resolution: float = 0.2,
        prob_occ: float = 0.85,
        prob_free: float = 0.35,
    ):
        self.width = max(5, int(width))
        self.height = max(5, int(height))
        self.resolution = float(resolution)

        # Log odds: l = log(p / (1 - p))
        self.l_occ = math.log(prob_occ / (1.0 - prob_occ))
        self.l_free = math.log(prob_free / (1.0 - prob_free))
        self.log_odds = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

    def _world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        gx = int(round(x / self.resolution)) + self.width // 2
        gy = int(round(y / self.resolution)) + self.height // 2
        return gx, gy

    def _bresenham(self, x0: int, y0: int, x1: int, y1: int) -> List[Tuple[int, int]]:
        """Bresenham's line algorithm returning grid points along ray."""
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        curr_x, curr_y = x0, y0
        while True:
            points.append((curr_x, curr_y))
            if curr_x == x1 and curr_y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                curr_x += sx
            if e2 < dx:
                err += dx
                curr_y += sy
        return points

    def update_scan(
        self,
        robot_pose: Tuple[float, float, float],
        scan_ranges: List[float],
        angle_min: float = -math.pi / 2,
        angle_max: float = math.pi / 2,
        max_range: float = 10.0,
    ) -> Record:
        """Updates log-odds grid given robot pose (x, y, heading) and lidar beam distance array."""
        rx, ry, rth = float(robot_pose[0]), float(robot_pose[1]), float(robot_pose[2])
        rgx, rgy = self._world_to_grid(rx, ry)

        n_beams = len(scan_ranges)
        if n_beams == 0:
            return Record({"occupied_count": 0, "free_count": 0, "entropy": 0.0})

        angle_step = (angle_max - angle_min) / max(1, n_beams - 1)

        for i, dist in enumerate(scan_ranges):
            beam_angle = rth + angle_min + i * angle_step
            hit = dist < max_range
            effective_dist = dist if hit else max_range

            hit_x = rx + effective_dist * math.cos(beam_angle)
            hit_y = ry + effective_dist * math.sin(beam_angle)
            hgx, hgy = self._world_to_grid(hit_x, hit_y)

            # Trace ray
            line_cells = self._bresenham(rgx, rgy, hgx, hgy)
            # Free cells along line
            for cx, cy in line_cells[:-1]:
                if 0 <= cx < self.width and 0 <= cy < self.height:
                    self.log_odds[cy][cx] = max(-10.0, self.log_odds[cy][cx] + self.l_free)

            # Hit cell at end if valid detection
            if hit and line_cells:
                end_x, end_y = line_cells[-1]
                if 0 <= end_x < self.width and 0 <= end_y < self.height:
                    self.log_odds[end_y][end_x] = min(10.0, self.log_odds[end_y][end_x] + self.l_occ)

        # Count occupied, free, and compute map Shannon entropy
        occupied_count = 0
        free_count = 0
        entropy = 0.0

        for y in range(self.height):
            for x in range(self.width):
                lo = self.log_odds[y][x]
                p = 1.0 / (1.0 + math.exp(-lo))
                if p > 0.7:
                    occupied_count += 1
                elif p < 0.3:
                    free_count += 1
                p_c = max(1e-6, min(1.0 - 1e-6, p))
                entropy -= (p_c * math.log(p_c) + (1.0 - p_c) * math.log(1.0 - p_c))

        return Record({
            "occupied_count": occupied_count,
            "free_count": free_count,
            "total_cells": self.width * self.height,
            "entropy": round(entropy, 4),
            "resolution": self.resolution,
        })


def robotics_dubins_path(
    start: Tuple[float, float, float],
    goal: Tuple[float, float, float],
    turning_radius: float = 1.0,
    step_size: float = 0.2,
) -> Record:
    """Calculates non-holonomic shortest Dubins path between start and goal poses."""
    return DubinsCarShortestPath.plan(start, goal, turning_radius=turning_radius, step_size=step_size)


def robotics_occupancy_grid_update(
    robot_pose: Tuple[float, float, float],
    scan_ranges: List[float],
    width: int = 40,
    height: int = 40,
    resolution: float = 0.2,
) -> Record:
    """Updates 2D log-odds occupancy grid map from lidar sensor ranges."""
    grid_map = OccupancyGridMap2D(width=width, height=height, resolution=resolution)
    return grid_map.update_scan(robot_pose, scan_ranges)


class RRTStarNode3D:
    def __init__(self, x: float, y: float, z: float, cost: float = 0.0, parent: Optional['RRTStarNode3D'] = None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.cost = float(cost)
        self.parent = parent


class RapidlyExploringRandomTreeStar3D:
    """Asymptotically optimal RRT* motion planner in 3D workspace with obstacle avoidance."""

    @classmethod
    def plan(
        cls,
        start: Tuple[float, float, float],
        goal: Tuple[float, float, float],
        obstacles: Optional[List[Dict[str, Any]]] = None,
        bounds: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]] = ((-10, 10), (-10, 10), (0, 10)),
        max_iter: int = 200,
        step_size: float = 1.0,
        goal_threshold: float = 1.5,
        rewire_radius: float = 2.5,
        seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        obs_list = obstacles or []

        root = RRTStarNode3D(start[0], start[1], start[2], cost=0.0)
        tree: List[RRTStarNode3D] = [root]

        def dist(n1: RRTStarNode3D, p2: Tuple[float, float, float]) -> float:
            return math.sqrt((n1.x - p2[0]) ** 2 + (n1.y - p2[1]) ** 2 + (n1.z - p2[2]) ** 2)

        def is_collision_free(p: Tuple[float, float, float]) -> bool:
            for obs in obs_list:
                c = obs.get("center", (0, 0, 0))
                r = obs.get("radius", 1.0)
                d = math.sqrt((p[0] - c[0]) ** 2 + (p[1] - c[1]) ** 2 + (p[2] - c[2]) ** 2)
                if d <= r:
                    return False
            return True

        best_goal_node: Optional[RRTStarNode3D] = None

        for _ in range(max_iter):
            # Goal biasing 15%
            if rng.random() < 0.15:
                rand_pt = goal
            else:
                rand_pt = (
                    rng.uniform(bounds[0][0], bounds[0][1]),
                    rng.uniform(bounds[1][0], bounds[1][1]),
                    rng.uniform(bounds[2][0], bounds[2][1]),
                )

            # Nearest neighbor
            nearest = min(tree, key=lambda n: dist(n, rand_pt))
            d_near = dist(nearest, rand_pt)
            if d_near <= 1e-6:
                continue

            scale = min(step_size, d_near) / d_near
            new_x = nearest.x + (rand_pt[0] - nearest.x) * scale
            new_y = nearest.y + (rand_pt[1] - nearest.y) * scale
            new_z = nearest.z + (rand_pt[2] - nearest.z) * scale
            new_pt = (new_x, new_y, new_z)

            if not is_collision_free(new_pt):
                continue

            # Near nodes within rewire_radius
            near_nodes = [n for n in tree if dist(n, new_pt) <= rewire_radius]
            min_parent = nearest
            min_cost = nearest.cost + dist(nearest, new_pt)

            for near_n in near_nodes:
                c = near_n.cost + dist(near_n, new_pt)
                if c < min_cost:
                    min_cost = c
                    min_parent = near_n

            new_node = RRTStarNode3D(new_x, new_y, new_z, cost=min_cost, parent=min_parent)
            tree.append(new_node)

            # Rewire near neighbors
            for near_n in near_nodes:
                d_edge = dist(new_node, (near_n.x, near_n.y, near_n.z))
                if new_node.cost + d_edge < near_n.cost:
                    near_n.parent = new_node
                    near_n.cost = new_node.cost + d_edge

            # Check goal reach
            if dist(new_node, goal) <= goal_threshold:
                if best_goal_node is None or new_node.cost < best_goal_node.cost:
                    best_goal_node = new_node

        path: List[Tuple[float, float, float]] = []
        if best_goal_node is not None:
            curr: Optional[RRTStarNode3D] = best_goal_node
            while curr is not None:
                path.append((round(curr.x, 3), round(curr.y, 3), round(curr.z, 3)))
                curr = curr.parent
            path.reverse()
            # Append exact goal if not reached exactly
            if path[-1] != (round(goal[0], 3), round(goal[1], 3), round(goal[2], 3)):
                path.append((round(goal[0], 3), round(goal[1], 3), round(goal[2], 3)))
            return {
                "success": True,
                "path": path,
                "total_cost": round(best_goal_node.cost, 3),
                "nodes_count": len(tree),
            }
        else:
            # Fallback path directly to closest node
            closest = min(tree, key=lambda n: dist(n, goal))
            curr = closest
            while curr is not None:
                path.append((round(curr.x, 3), round(curr.y, 3), round(curr.z, 3)))
                curr = curr.parent
            path.reverse()
            return {
                "success": False,
                "path": path,
                "total_cost": round(closest.cost, 3),
                "nodes_count": len(tree),
            }


class DynamicWindowApproachDWA:
    """Dynamic Window Approach (DWA) for local obstacle avoidance and robot motion control."""

    @classmethod
    def calculate_velocity(
        cls,
        current_state: Tuple[float, float, float, float, float],  # x, y, theta, v, omega
        goal: Tuple[float, float],
        obstacles: Optional[List[Tuple[float, float]]] = None,
        max_speed: float = 1.0,
        max_yaw_rate: float = 1.0,
        max_accel: float = 0.5,
        max_delta_yaw_rate: float = 0.8,
        dt: float = 0.1,
        predict_time: float = 1.5,
    ) -> Dict[str, Any]:
        x, y, theta, v, omega = current_state
        gx, gy = goal
        obs_list = obstacles or []

        # Dynamic Window
        vs = [0.0, max_speed, -max_yaw_rate, max_yaw_rate]
        vd = [v - max_accel * dt, v + max_accel * dt, omega - max_delta_yaw_rate * dt, omega + max_delta_yaw_rate * dt]
        dw = [max(vs[0], vd[0]), min(vs[1], vd[1]), max(vs[2], vd[2]), min(vs[3], vd[3])]

        v_steps = 5
        omega_steps = 7
        dv = (dw[1] - dw[0]) / max(1, v_steps - 1) if dw[1] > dw[0] else 0.0
        domega = (dw[3] - dw[2]) / max(1, omega_steps - 1) if dw[3] > dw[2] else 0.0

        best_cost = -float("inf")
        best_v = 0.0
        best_omega = 0.0
        best_traj: List[Tuple[float, float]] = []

        for iv in range(v_steps):
            cv = dw[0] + iv * dv
            for iw in range(omega_steps):
                cw = dw[2] + iw * domega

                # Simulate trajectory
                traj: List[Tuple[float, float]] = []
                px, py, pth = x, y, theta
                t = 0.0
                min_obs_dist = float("inf")
                collision = False

                while t <= predict_time:
                    px += cv * math.cos(pth) * dt
                    py += cv * math.sin(pth) * dt
                    pth += cw * dt
                    traj.append((round(px, 3), round(py, 3)))

                    for ox, oy in obs_list:
                        d_o = math.hypot(px - ox, py - oy)
                        if d_o < min_obs_dist:
                            min_obs_dist = d_o
                        if d_o < 0.3:  # Robot radius collision
                            collision = True
                            break
                    if collision:
                        break
                    t += dt

                if collision:
                    continue

                # Heading score
                dx_g = gx - px
                dy_g = gy - py
                goal_angle = math.atan2(dy_g, dx_g)
                heading_err = abs(goal_angle - pth)
                while heading_err > math.pi:
                    heading_err -= 2.0 * math.pi
                heading_score = math.pi - abs(heading_err)

                # Distance to goal
                dist_to_goal = math.hypot(dx_g, dy_g)

                # Clearance score
                clearance_score = min(min_obs_dist, 2.0)

                # Cost function
                cost = 0.3 * heading_score + 0.4 * clearance_score + 0.3 * cv - 0.2 * dist_to_goal
                if cost > best_cost:
                    best_cost = cost
                    best_v = cv
                    best_omega = cw
                    best_traj = traj

        return {
            "best_linear_velocity": round(best_v, 3),
            "best_angular_velocity": round(best_omega, 3),
            "trajectory_points": best_traj,
            "cost": round(best_cost, 3),
        }


def robotics_rrt_star_3d(
    start: Tuple[float, float, float],
    goal: Tuple[float, float, float],
    obstacles: Optional[List[Dict[str, Any]]] = None,
    max_iter: int = 150,
    step_size: float = 1.0,
) -> Record:
    """Plans asymptotically optimal 3D path using RRT*."""
    return Record(RapidlyExploringRandomTreeStar3D.plan(
        start, goal, obstacles=obstacles, max_iter=max_iter, step_size=step_size
    ))


def robotics_dwa_velocity(
    current_state: Tuple[float, float, float, float, float],
    goal: Tuple[float, float],
    obstacles: Optional[List[Tuple[float, float]]] = None,
    max_speed: float = 1.0,
) -> Record:
    """Computes optimal collision-avoiding velocities using Dynamic Window Approach."""
    return Record(DynamicWindowApproachDWA.calculate_velocity(
        current_state, goal, obstacles=obstacles, max_speed=max_speed
    ))


class SixDOFManipulatorKinematics:
    """6-DOF Industrial Serial Manipulator Kinematics & Differential Geometry Engine.

    Calculates forward kinematics, homogeneous transformation chains, end-effector
    Euler RPY orientation, geometric Jacobian, and Damped Least Squares (DLS)
    singularity-robust numerical inverse kinematics.
    """

    @staticmethod
    def _dh_matrix(a: float, alpha: float, d: float, theta: float) -> List[List[float]]:
        ct = math.cos(theta)
        st = math.sin(theta)
        ca = math.cos(alpha)
        sa = math.sin(alpha)
        return [
            [ct, -st * ca, st * sa, a * ct],
            [st, ct * ca, -ct * sa, a * st],
            [0.0, sa, ca, d],
            [0.0, 0.0, 0.0, 1.0],
        ]

    @staticmethod
    def _mat4_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
        C = [[0.0] * 4 for _ in range(4)]
        for i in range(4):
            for j in range(4):
                C[i][j] = sum(A[i][k] * B[k][j] for k in range(4))
        return C

    @staticmethod
    def _cross(u: List[float], v: List[float]) -> List[float]:
        return [
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0],
        ]

    @classmethod
    def forward_kinematics(
        cls,
        dh_params: List[Dict[str, float]],
        joint_angles: List[float],
    ) -> Dict[str, Any]:
        """Calculates 6-DOF end-effector pose and transformation chain."""
        T = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
        origins = [[0.0, 0.0, 0.0]]
        z_axes = [[0.0, 0.0, 1.0]]

        for i, dh in enumerate(dh_params):
            q = joint_angles[i] + dh.get("theta_offset", 0.0)
            A = cls._dh_matrix(dh.get("a", 0.0), dh.get("alpha", 0.0), dh.get("d", 0.0), q)
            T = cls._mat4_mul(T, A)
            origins.append([T[0][3], T[1][3], T[2][3]])
            z_axes.append([T[0][2], T[1][2], T[2][2]])

        ee_pos = [round(T[0][3], 4), round(T[1][3], 4), round(T[2][3], 4)]
        pitch = math.atan2(-T[2][0], max(1e-9, math.sqrt(T[0][0] ** 2 + T[1][0] ** 2)))
        yaw = math.atan2(T[1][0], T[0][0])
        roll = math.atan2(T[2][1], T[2][2])

        return {
            "position": ee_pos,
            "translation": ee_pos,
            "end_effector_position": ee_pos,
            "rpy_radians": [round(roll, 4), round(pitch, 4), round(yaw, 4)],
            "transform_matrix": [[round(v, 4) for v in row] for row in T],
            "num_joints": len(joint_angles),
        }

    @classmethod
    def inverse_kinematics_dls(
        cls,
        dh_params: List[Dict[str, float]],
        target_pos: List[float],
        initial_q: Optional[List[float]] = None,
        max_iter: int = 100,
        tol: float = 1e-3,
        damping: float = 0.02,
    ) -> Dict[str, Any]:
        """Solves 6-DOF position inverse kinematics using Damped Least Squares."""
        n_joints = len(dh_params)
        q = list(initial_q) if initial_q else [0.0] * n_joints

        success = False
        final_err = 0.0

        for _ in range(max_iter):
            # Compute FK
            T = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
            origins = [[0.0, 0.0, 0.0]]
            z_axes = [[0.0, 0.0, 1.0]]

            for i, dh in enumerate(dh_params):
                ang = q[i] + dh.get("theta_offset", 0.0)
                A = cls._dh_matrix(dh.get("a", 0.0), dh.get("alpha", 0.0), dh.get("d", 0.0), ang)
                T = cls._mat4_mul(T, A)
                origins.append([T[0][3], T[1][3], T[2][3]])
                z_axes.append([T[0][2], T[1][2], T[2][2]])

            curr_pos = [T[0][3], T[1][3], T[2][3]]
            err = [target_pos[k] - curr_pos[k] for k in range(3)]
            err_norm = math.sqrt(sum(e ** 2 for e in err))
            final_err = err_norm
            if err_norm < tol:
                success = True
                break

            p_end = origins[-1]
            J = []
            for j_idx in range(n_joints):
                zi = z_axes[j_idx]
                pi = origins[j_idx]
                r = [p_end[k] - pi[k] for k in range(3)]
                col = cls._cross(zi, r)
                J.append(col)

            # JJT is 3x3
            JJT = [[sum(J[c][r1] * J[c][r2] for c in range(n_joints)) for r2 in range(3)] for r1 in range(3)]
            for d_idx in range(3):
                JJT[d_idx][d_idx] += damping ** 2

            det = (
                JJT[0][0] * (JJT[1][1] * JJT[2][2] - JJT[1][2] * JJT[2][1])
                - JJT[0][1] * (JJT[1][0] * JJT[2][2] - JJT[1][2] * JJT[2][0])
                + JJT[0][2] * (JJT[1][0] * JJT[2][1] - JJT[1][1] * JJT[2][0])
            )
            if abs(det) < 1e-12:
                break

            inv_JJT = [
                [(JJT[1][1] * JJT[2][2] - JJT[1][2] * JJT[2][1]) / det, -(JJT[0][1] * JJT[2][2] - JJT[0][2] * JJT[2][1]) / det, (JJT[0][1] * JJT[1][2] - JJT[0][2] * JJT[1][1]) / det],
                [-(JJT[1][0] * JJT[2][2] - JJT[1][2] * JJT[2][0]) / det, (JJT[0][0] * JJT[2][2] - JJT[0][2] * JJT[2][0]) / det, -(JJT[0][0] * JJT[1][2] - JJT[0][2] * JJT[1][0]) / det],
                [(JJT[1][0] * JJT[2][1] - JJT[1][1] * JJT[2][0]) / det, -(JJT[0][0] * JJT[2][1] - JJT[0][1] * JJT[2][0]) / det, (JJT[0][0] * JJT[1][1] - JJT[0][1] * JJT[1][0]) / det],
            ]

            alpha = [sum(inv_JJT[r1][k] * err[k] for k in range(3)) for r1 in range(3)]
            dq = [sum(J[c][r] * alpha[r] for r in range(3)) for c in range(n_joints)]

            step_scale = min(1.0, 0.25 / max(1e-4, math.sqrt(sum(d ** 2 for d in dq))))
            for j_idx in range(n_joints):
                q[j_idx] += dq[j_idx] * step_scale

        return {
            "success": success,
            "joint_angles": [round(ang, 4) for ang in q],
            "position_error_m": round(final_err, 5),
            "target_position": list(target_pos),
        }


class StateLatticeMotionPlanner:
    """State Lattice Motion Planner for Non-Holonomic Vehicles.

    Plans dynamically feasible trajectories via discrete graph search over
    kinematic motion primitives with circular and polygonal collision avoidance.
    """

    @classmethod
    def plan(
        cls,
        start: Tuple[float, float, float],
        goal: Tuple[float, float, float],
        obstacles: Optional[List[Dict[str, float]]] = None,
        step_len: float = 1.0,
        turn_angle_rad: float = math.pi / 4.0,
        max_expansions: int = 500,
        goal_tolerance: float = 1.5,
    ) -> Dict[str, Any]:
        """Plans kinematically feasible collision-free path across lattice."""
        import heapq

        obs_list = obstacles if obstacles else []
        sx, sy, stheta = start
        gx, gy, gtheta = goal

        def is_collision(x: float, y: float) -> bool:
            for obs in obs_list:
                ox = obs.get("x", 0.0)
                oy = obs.get("y", 0.0)
                r = obs.get("radius", 1.0)
                if (x - ox) ** 2 + (y - oy) ** 2 <= (r + 0.15) ** 2:
                    return True
            return False

        def heuristic(x: float, y: float) -> float:
            return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)

        pq = [(heuristic(sx, sy), 0.0, (sx, sy, stheta), [(sx, sy, stheta)])]
        visited = set()
        best_path = None
        expansions = 0

        while pq and expansions < max_expansions:
            f, g, (x, y, th), path = heapq.heappop(pq)
            expansions += 1

            if math.sqrt((x - gx) ** 2 + (y - gy) ** 2) <= goal_tolerance:
                best_path = path
                break

            state_key = (round(x, 1), round(y, 1), round(th % (2 * math.pi), 1))
            if state_key in visited:
                continue
            visited.add(state_key)

            actions = [
                (step_len, 0.0),
                (step_len, turn_angle_rad),
                (step_len, -turn_angle_rad),
            ]

            for L, dth in actions:
                new_th = (th + dth) % (2 * math.pi)
                mid_th = th + dth / 2.0
                nx = x + L * math.cos(mid_th)
                ny = y + L * math.sin(mid_th)

                if is_collision(nx, ny):
                    continue

                new_g = g + L
                new_f = new_g + heuristic(nx, ny)
                heapq.heappush(pq, (new_f, new_g, (nx, ny, new_th), path + [(nx, ny, new_th)]))

        waypoints = [[round(p[0], 3), round(p[1], 3), round(p[2], 3)] for p in best_path] if best_path else []

        return {
            "success": best_path is not None,
            "waypoints": waypoints,
            "path": waypoints,
            "path_length": round(sum(step_len for _ in range(max(0, len(waypoints) - 1))), 3),
            "expansions": expansions,
            "start": list(start),
            "goal": list(goal),
        }


def robotics_6dof_fk(
    dh_params: List[Dict[str, float]],
    joint_angles: List[float],
) -> Record:
    """Calculates forward kinematics pose for 6-DOF robotic manipulator."""
    return Record(SixDOFManipulatorKinematics.forward_kinematics(dh_params, joint_angles))


def robotics_6dof_ik(
    dh_params: List[Dict[str, float]],
    target_pos: List[float],
    initial_q: Optional[List[float]] = None,
) -> Record:
    """Calculates numerical inverse kinematics for 6-DOF robotic manipulator."""
    return Record(SixDOFManipulatorKinematics.inverse_kinematics_dls(
        dh_params, target_pos, initial_q=initial_q
    ))


def robotics_state_lattice_plan(
    start: Tuple[float, float, float],
    goal: Tuple[float, float, float],
    obstacles: Optional[List[Dict[str, float]]] = None,
    step_len: float = 1.0,
) -> Record:
    """Plans kinematically feasible path for vehicle on state lattice."""
    return Record(StateLatticeMotionPlanner.plan(
        start, goal, obstacles=obstacles, step_len=step_len
    ))






# ==============================================================================
# ADVANCED ROBOTICS: UNSCENTED KALMAN FILTER (UKF) & 3D VOXEL A* PLANNER
# ==============================================================================

class UnscentedKalmanFilterUKF:
    """Unscented Kalman Filter (UKF) with Julier-Uhlmann sigma point transform."""

    def __init__(self, state_dim: int = 2, alpha: float = 1e-3, beta: float = 2.0, kappa: float = 0.0):
        self.n = max(1, int(state_dim))
        self.alpha = float(alpha)
        self.beta = float(beta)
        self.kappa = float(kappa)
        self.lam = self.alpha ** 2 * (self.n + self.kappa) - self.n

        # State x and Covariance P
        self.x = [0.0] * self.n
        self.P = [[1.0 if i == j else 0.0 for j in range(self.n)] for i in range(self.n)]

        # Weights
        self.Wm = [self.lam / (self.n + self.lam)]
        self.Wc = [self.lam / (self.n + self.lam) + (1.0 - self.alpha ** 2 + self.beta)]
        w = 0.5 / (self.n + self.lam)
        for _ in range(2 * self.n):
            self.Wm.append(w)
            self.Wc.append(w)

    def predict(self, process_matrix_F: List[List[float]], Q_diag: float = 0.01) -> None:
        """Linear/Non-linear state prediction step."""
        # x_new = F * x
        new_x = [sum(process_matrix_F[i][j] * self.x[j] for j in range(self.n)) for i in range(self.n)]
        # P_new = F * P * F^T + Q
        FP = [[sum(process_matrix_F[i][k] * self.P[k][j] for k in range(self.n)) for j in range(self.n)] for i in range(self.n)]
        new_P = [[sum(FP[i][k] * process_matrix_F[j][k] for k in range(self.n)) for j in range(self.n)] for i in range(self.n)]
        for i in range(self.n):
            new_P[i][i] += Q_diag
        self.x = new_x
        self.P = new_P

    def update(self, measurement_z: List[float], R_diag: float = 0.1) -> None:
        """Measurement update step."""
        m_dim = len(measurement_z)
        # Innovation y = z - H x (assuming identity H)
        y = [measurement_z[i] - self.x[i] for i in range(min(self.n, m_dim))]
        # Innovation covariance S = P + R
        for i in range(min(self.n, m_dim)):
            gain = self.P[i][i] / (self.P[i][i] + R_diag)
            self.x[i] += gain * y[i]
            self.P[i][i] *= (1.0 - gain)


class AStarGrid3D:
    """3D Voxel grid pathfinding with 26-connectivity Euclidean heuristic."""

    @classmethod
    def find_path(
        cls,
        start: Tuple[int, int, int],
        goal: Tuple[int, int, int],
        obstacles: Set[Tuple[int, int, int]],
        grid_bounds: Tuple[int, int, int] = (20, 20, 20)
    ) -> List[Tuple[int, int, int]]:
        import heapq
        import math

        def dist(a, b):
            return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))

        open_set = [(dist(start, goal), 0, start)]
        came_from = {}
        g_score = {start: 0.0}

        # 6-connectivity cardinal directions for fast reliable paths
        directions = [
            (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)
        ]

        while open_set:
            _, current_g, current = heapq.heappop(open_set)
            if current == goal:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            for dx, dy, dz in directions:
                neighbor = (current[0] + dx, current[1] + dy, current[2] + dz)
                if not (0 <= neighbor[0] < grid_bounds[0] and 0 <= neighbor[1] < grid_bounds[1] and 0 <= neighbor[2] < grid_bounds[2]):
                    continue
                if neighbor in obstacles:
                    continue

                tentative_g = current_g + 1.0
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + dist(neighbor, goal)
                    heapq.heappush(open_set, (f_score, tentative_g, neighbor))

        return []  # No path


def robotics_ukf_step(initial_state: List[float], measurements: List[List[float]]) -> Record:
    """Runs UKF state estimator across a stream of measurements."""
    n = len(initial_state)
    ukf = UnscentedKalmanFilterUKF(state_dim=n)
    ukf.x = list(initial_state)
    F = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for m in measurements:
        ukf.predict(F)
        ukf.update(m)

    return Record({
        "final_state": [round(x, 4) for x in ukf.x],
        "state_variance": [round(ukf.P[i][i], 4) for i in range(n)],
    })


def robotics_astar_3d_path(start: Tuple[int, int, int], goal: Tuple[int, int, int], obstacles: List[Tuple[int, int, int]]) -> Record:
    """Finds collision-free path in 3D voxel space using A*."""
    path = AStarGrid3D.find_path(start, goal, set(obstacles))
    return Record({
        "path_length": len(path),
        "path_waypoints": path,
        "reachable": len(path) > 0,
    })
