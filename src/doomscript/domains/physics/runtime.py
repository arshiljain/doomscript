"""Physics, Kinematics & Controls Domain Runtime for DoomScript.

Pure Python standard library implementation of 2D/3D ballistic trajectories,
aerodynamic drag simulation, AABB and SAT polygon collisions, damped harmonic oscillators,
orbital velocities, and PID feedback controllers.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR


class PhysicsRuntime(DomainRuntime):
    """Runtime coordinator for physics calculations."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def physics_trajectory(velocity: Any, angle_deg: Any, gravity: Any = 9.81, dt: Any = 0.05) -> List[Dict[str, float]]:
    """Simulate 2D projectile trajectory without drag."""
    v0 = float(velocity)
    theta = math.radians(float(angle_deg))
    g = float(gravity) if float(gravity) > 0 else 9.81
    dt = max(0.001, float(dt))

    vx = v0 * math.cos(theta)
    vy0 = v0 * math.sin(theta)

    points: List[Dict[str, float]] = []
    t = 0.0
    x, y = 0.0, 0.0

    while y >= 0.0 or len(points) < 2:
        points.append({"x": round(x, 4), "y": round(max(0.0, y), 4), "t": round(t, 4)})
        t += dt
        x = vx * t
        y = (vy0 * t) - (0.5 * g * t * t)
        if y < 0.0 and len(points) >= 2:
            break
        if len(points) > 10000:
            break

    return points


def physics_ballistic_range(velocity: Any, angle_deg: Any, gravity: Any = 9.81) -> float:
    """Calculate theoretical ideal ballistic range on flat ground: R = (v^2 * sin(2*theta)) / g."""
    v0 = float(velocity)
    theta = math.radians(float(angle_deg))
    g = float(gravity) if float(gravity) > 0 else 9.81
    r = (v0 * v0 * math.sin(2 * theta)) / g
    return round(max(0.0, r), 4)


def physics_projectile_drag(
    mass: Any,
    velocity: Any,
    angle_deg: Any,
    drag_coef: Any = 0.005,
    gravity: Any = 9.81,
    dt: Any = 0.02
) -> List[Dict[str, float]]:
    """Simulate 2D projectile trajectory with quadratic air resistance using Euler integration."""
    m = max(0.0001, float(mass))
    v0 = float(velocity)
    theta = math.radians(float(angle_deg))
    c_d = max(0.0, float(drag_coef))
    g = float(gravity)
    step = max(0.001, float(dt))

    x, y = 0.0, 0.0
    vx = v0 * math.cos(theta)
    vy = v0 * math.sin(theta)
    t = 0.0

    points: List[Dict[str, float]] = [{"x": 0.0, "y": 0.0, "t": 0.0}]

    while (y >= 0.0 or len(points) < 2) and len(points) < 10000:
        speed = math.sqrt(vx * vx + vy * vy)
        drag_force = c_d * speed * speed
        ax = -(drag_force * (vx / max(0.0001, speed))) / m
        ay = -g - (drag_force * (vy / max(0.0001, speed))) / m

        vx += ax * step
        vy += ay * step
        x += vx * step
        y += vy * step
        t += step

        points.append({"x": round(x, 4), "y": round(max(0.0, y), 4), "t": round(t, 4)})
        if y < 0.0 and len(points) > 2:
            break

    return points


def physics_aabb_collision(box1: Any, box2: Any) -> bool:
    """Check collision between two 2D Axis-Aligned Bounding Boxes."""
    def _parse(b):
        if isinstance(b, dict):
            return float(b.get("x", 0)), float(b.get("y", 0)), float(b.get("width", 0)), float(b.get("height", 0))
        if isinstance(b, (list, tuple)) and len(b) >= 4:
            return float(b[0]), float(b[1]), float(b[2]), float(b[3])
        return 0.0, 0.0, 0.0, 0.0

    x1, y1, w1, h1 = _parse(box1)
    x2, y2, w2, h2 = _parse(box2)

    return (
        x1 < x2 + w2
        and x1 + w1 > x2
        and y1 < y2 + h2
        and y1 + h1 > y2
    )


def physics_sat_polygon_collision(poly1: Any, poly2: Any) -> bool:
    """Separating Axis Theorem (SAT) collision check between two 2D convex polygons."""
    p1 = [list(pt) for pt in poly1]
    p2 = [list(pt) for pt in poly2]

    if len(p1) < 3 or len(p2) < 3:
        return False

    def _get_axes(pts):
        axes = []
        for i in range(len(pts)):
            p_a = pts[i]
            p_b = pts[(i + 1) % len(pts)]
            edge = [p_b[0] - p_a[0], p_b[1] - p_a[1]]
            normal = [-edge[1], edge[0]]
            length = math.sqrt(normal[0] ** 2 + normal[1] ** 2)
            if length > 0.00001:
                axes.append([normal[0] / length, normal[1] / length])
        return axes

    def _project(pts, axis):
        dots = [pt[0] * axis[0] + pt[1] * axis[1] for pt in pts]
        return min(dots), max(dots)

    for axis in _get_axes(p1) + _get_axes(p2):
        min_a, max_a = _project(p1, axis)
        min_b, max_b = _project(p2, axis)
        if max_a < min_b or max_b < min_a:
            return False
    return True


def physics_spring_damper(
    mass: Any,
    k: Any,
    c: Any,
    x0: Any,
    v0: Any = 0.0,
    dt: Any = 0.02,
    steps: Any = 50
) -> List[Dict[str, float]]:
    """Simulate damped harmonic oscillator (m*x'' + c*x' + k*x = 0)."""
    m = max(0.001, float(mass))
    spring_k = float(k)
    damping_c = float(c)
    x = float(x0)
    v = float(v0)
    dt_val = max(0.001, float(dt))
    num_steps = max(1, int(steps))

    states: List[Dict[str, float]] = []
    t = 0.0

    for _ in range(num_steps):
        states.append({"t": round(t, 4), "x": round(x, 4), "v": round(v, 4)})
        # acceleration a = -(k*x + c*v) / m
        a = -(spring_k * x + damping_c * v) / m
        v += a * dt_val
        x += v * dt_val
        t += dt_val

    return states


def physics_orbital_velocity(mass: Any, radius: Any, g_const: float = 6.67430e-11) -> float:
    """Calculate circular orbital velocity v = sqrt(GM/r)."""
    m = float(mass)
    r = max(0.0001, float(radius))
    return round(math.sqrt((g_const * m) / r), 4)


def physics_escape_velocity(mass: Any, radius: Any, g_const: float = 6.67430e-11) -> float:
    """Calculate escape velocity v_esc = sqrt(2GM/r)."""
    m = float(mass)
    r = max(0.0001, float(radius))
    return round(math.sqrt((2.0 * g_const * m) / r), 4)


class PhysicsPID:
    """Proportional-Integral-Derivative (PID) Controller."""

    def __init__(self, kp: float, ki: float, kd: float):
        self.kp = float(kp)
        self.ki = float(ki)
        self.kd = float(kd)
        self.integral = 0.0
        self.last_error = 0.0

    def update(self, setpoint: float, measurement: float, dt: float) -> float:
        dt = max(0.0001, float(dt))
        error = float(setpoint) - float(measurement)
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        self.last_error = error
        return round(self.kp * error + self.ki * self.integral + self.kd * derivative, 4)


def physics_pid_create(kp: Any, ki: Any, kd: Any) -> PhysicsPID:
    """Create a new PID Controller."""
    return PhysicsPID(float(kp), float(ki), float(kd))


def physics_pid_update(pid: Any, setpoint: Any, measurement: Any, dt: Any = 0.1) -> float:
    """Update a PID Controller with setpoint and feedback measurement."""
    if isinstance(pid, PhysicsPID):
        return pid.update(float(setpoint), float(measurement), float(dt))
    return 0.0


physics_create_pid = physics_pid_create
physics_update_pid = physics_pid_update
physics_projectile_trajectory = physics_trajectory
physics_projectile_range = physics_ballistic_range
physics_harmonic_oscillator = physics_spring_damper
physics_check_sat_collision = physics_sat_polygon_collision


def physics_drag_trajectory(velocity: Any, angle_deg: Any, drag_coef: Any = 0.05, mass: Any = 1.0, gravity: Any = 9.81, dt: Any = 0.05, steps: Any = 100) -> List[Dict[str, float]]:
    return physics_projectile_drag(mass=mass, velocity=velocity, angle_deg=angle_deg, drag_coef=drag_coef, gravity=gravity, dt=dt)


def physics_check_aabb_collision(*args) -> bool:
    if len(args) == 2:
        return physics_aabb_collision(args[0], args[1])
    elif len(args) >= 8:
        box1 = (args[0], args[1], args[2], args[3])
        box2 = (args[4], args[5], args[6], args[7])
        return physics_aabb_collision(box1, box2)
    return False


def execute_physics_ir(spec_id: str) -> Any:
    """Executes a stored Physics IR specification."""
    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    spec = reg.get_spec(spec_id)
    if spec is None:
        raise ValueError(f"Unknown physics spec: {spec_id}")
    return PhysicsRuntime().execute_ir(spec, {})
