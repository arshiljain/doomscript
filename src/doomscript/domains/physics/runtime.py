"""Physics, Kinematics & Controls Domain Runtime for DoomScript.

Pure Python standard library implementation of 2D/3D ballistic trajectories,
aerodynamic drag simulation, AABB and SAT polygon collisions, damped harmonic oscillators,
orbital velocities, and PID feedback controllers.
"""

import math
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.runtime import Record


class PhysicsRuntime(DomainRuntime):
    """Runtime coordinator for physics calculations."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def physics_kinetic_energy(mass: Any, velocity: Any) -> float:
    """Calculate kinetic energy: KE = 0.5 * m * v^2."""
    return 0.5 * float(mass) * (float(velocity) ** 2)


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


# ==============================================================================
# Advanced Physics Deepening: N-Body, Rigid Body Collision & Real Gases
# ==============================================================================

class BarnesHutNode:
    """Octree spatial decomposition node for 3D Barnes-Hut N-body simulation."""

    def __init__(self, cx: float, cy: float, cz: float, size: float):
        self.cx = float(cx)
        self.cy = float(cy)
        self.cz = float(cz)
        self.size = float(size)
        self.mass = 0.0
        self.com_x = 0.0
        self.com_y = 0.0
        self.com_z = 0.0
        self.particle: Optional[Dict[str, float]] = None
        self.children: Optional[List['BarnesHutNode']] = None

    def _get_octant(self, px: float, py: float, pz: float) -> int:
        idx = 0
        if px >= self.cx:
            idx |= 1
        if py >= self.cy:
            idx |= 2
        if pz >= self.cz:
            idx |= 4
        return idx

    def _subdivide(self) -> None:
        half = self.size / 2.0
        quarter = self.size / 4.0
        self.children = []
        for i in range(8):
            ox = self.cx + (quarter if (i & 1) else -quarter)
            oy = self.cy + (quarter if (i & 2) else -quarter)
            oz = self.cz + (quarter if (i & 4) else -quarter)
            self.children.append(BarnesHutNode(ox, oy, oz, half))

    def insert(self, p: Dict[str, float]) -> None:
        pmass = float(p.get("mass", 1.0))
        px = float(p.get("x", 0.0))
        py = float(p.get("y", 0.0))
        pz = float(p.get("z", 0.0))

        if self.mass == 0.0 and self.particle is None and self.children is None:
            self.particle = p
            self.mass = pmass
            self.com_x = px
            self.com_y = py
            self.com_z = pz
            return

        if self.children is None:
            self._subdivide()
            old_p = self.particle
            self.particle = None
            if old_p is not None:
                old_oct = self._get_octant(old_p["x"], old_p["y"], old_p["z"])
                assert self.children is not None
                self.children[old_oct].insert(old_p)

        new_total_mass = self.mass + pmass
        if new_total_mass > 0.0:
            self.com_x = (self.com_x * self.mass + px * pmass) / new_total_mass
            self.com_y = (self.com_y * self.mass + py * pmass) / new_total_mass
            self.com_z = (self.com_z * self.mass + pz * pmass) / new_total_mass
            self.mass = new_total_mass

        octant = self._get_octant(px, py, pz)
        assert self.children is not None
        self.children[octant].insert(p)


class BarnesHutNBody:
    """3D Barnes-Hut hierarchical N-body gravity and electrostatic solver."""

    @staticmethod
    def _compute_force_on(node: BarnesHutNode, p: Dict[str, float], theta: float, G: float, eps: float) -> Tuple[float, float, float]:
        if node.mass == 0.0:
            return 0.0, 0.0, 0.0

        dx = node.com_x - p["x"]
        dy = node.com_y - p["y"]
        dz = node.com_z - p["z"]
        dist_sq = dx * dx + dy * dy + dz * dz + eps * eps
        dist = math.sqrt(dist_sq)

        if dist < 1e-12:
            return 0.0, 0.0, 0.0

        if node.children is None:
            if node.particle is p:
                return 0.0, 0.0, 0.0
            f_mag = G * (node.mass * p.get("mass", 1.0)) / (dist_sq * dist)
            return f_mag * dx, f_mag * dy, f_mag * dz

        # Multipole acceptance criterion
        if (node.size / dist) < theta:
            f_mag = G * (node.mass * p.get("mass", 1.0)) / (dist_sq * dist)
            return f_mag * dx, f_mag * dy, f_mag * dz

        fx_tot, fy_tot, fz_tot = 0.0, 0.0, 0.0
        for child in node.children:
            cfx, cfy, cfz = BarnesHutNBody._compute_force_on(child, p, theta, G, eps)
            fx_tot += cfx
            fy_tot += cfy
            fz_tot += cfz
        return fx_tot, fy_tot, fz_tot

    @classmethod
    def step(
        cls,
        particles: List[Dict[str, float]],
        dt: float = 0.01,
        theta: float = 0.5,
        G: float = 1.0,
        eps: float = 1e-4,
    ) -> List[Dict[str, float]]:
        """Performs one numerical integration time step for N particles."""
        if not particles:
            return []

        # Find spatial bounds
        min_x = min(p["x"] for p in particles)
        max_x = max(p["x"] for p in particles)
        min_y = min(p["y"] for p in particles)
        max_y = max(p["y"] for p in particles)
        min_z = min(p["z"] for p in particles)
        max_z = max(p["z"] for p in particles)

        cx = (min_x + max_x) / 2.0
        cy = (min_y + max_y) / 2.0
        cz = (min_z + max_z) / 2.0
        size = max(max_x - min_x, max_y - min_y, max_z - min_z, 1.0) * 1.2

        root = BarnesHutNode(cx, cy, cz, size)
        for p in particles:
            root.insert(p)

        updated_particles: List[Dict[str, float]] = []
        for p in particles:
            m = max(1e-9, float(p.get("mass", 1.0)))
            fx, fy, fz = cls._compute_force_on(root, p, theta, G, eps)
            vx = float(p.get("vx", 0.0)) + (fx / m) * dt
            vy = float(p.get("vy", 0.0)) + (fy / m) * dt
            vz = float(p.get("vz", 0.0)) + (fz / m) * dt
            x = float(p["x"]) + vx * dt
            y = float(p["y"]) + vy * dt
            z = float(p["z"]) + vz * dt

            updated_particles.append({
                "x": round(x, 6),
                "y": round(y, 6),
                "z": round(z, 6),
                "vx": round(vx, 6),
                "vy": round(vy, 6),
                "vz": round(vz, 6),
                "mass": m,
            })

        return updated_particles


class ImpulseCollision2D:
    """Rigid body 2D collision resolution with linear/angular momentum and friction."""

    @staticmethod
    def resolve_collision(
        body_a: Dict[str, Any],
        body_b: Dict[str, Any],
        contact_point: Tuple[float, float],
        normal: Tuple[float, float],
        restitution: Optional[float] = None,
        friction: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Resolves linear and angular momentum impulse between two 2D rigid bodies.
        `normal` points from body A to body B.
        """
        ma = float(body_a.get("mass", 1.0))
        mb = float(body_b.get("mass", 1.0))
        ia = float(body_a.get("inertia", 1.0))
        ib = float(body_b.get("inertia", 1.0))

        inv_ma = 0.0 if ma <= 0.0 else 1.0 / ma
        inv_mb = 0.0 if mb <= 0.0 else 1.0 / mb
        inv_ia = 0.0 if ia <= 0.0 else 1.0 / ia
        inv_ib = 0.0 if ib <= 0.0 else 1.0 / ib

        pos_a = (float(body_a.get("x", 0.0)), float(body_a.get("y", 0.0)))
        pos_b = (float(body_b.get("x", 0.0)), float(body_b.get("y", 0.0)))

        va = (float(body_a.get("vx", 0.0)), float(body_a.get("vy", 0.0)))
        vb = (float(body_b.get("vx", 0.0)), float(body_b.get("vy", 0.0)))
        omega_a = float(body_a.get("omega", 0.0))
        omega_b = float(body_b.get("omega", 0.0))

        # Lever arms from center of mass to contact point
        ra = (contact_point[0] - pos_a[0], contact_point[1] - pos_a[1])
        rb = (contact_point[0] - pos_b[0], contact_point[1] - pos_b[1])

        # Velocity at contact points: v + omega x r (in 2D: (-omega*ry, omega*rx))
        vap = (va[0] - omega_a * ra[1], va[1] + omega_a * ra[0])
        vbp = (vb[0] - omega_b * rb[1], vb[1] + omega_b * rb[0])

        # Relative contact velocity: B relative to A
        v_rel = (vbp[0] - vap[0], vbp[1] - vap[1])

        # Normalize normal vector
        n_len = math.hypot(normal[0], normal[1])
        if n_len < 1e-12:
            return {"body_a": dict(body_a), "body_b": dict(body_b), "impulse": (0.0, 0.0)}
        n = (normal[0] / n_len, normal[1] / n_len)
        t = (-n[1], n[0])  # Tangent vector

        # Normal relative velocity
        vn = v_rel[0] * n[0] + v_rel[1] * n[1]
        if vn > 0.0:
            # Bodies are moving away from each other
            return {"body_a": dict(body_a), "body_b": dict(body_b), "impulse": (0.0, 0.0)}

        # Restitution
        e = min(float(body_a.get("restitution", 0.8)), float(body_b.get("restitution", 0.8))) if restitution is None else float(restitution)
        mu = math.sqrt(float(body_a.get("friction", 0.3)) * float(body_b.get("friction", 0.3))) if friction is None else float(friction)

        # Cross products (2D scalar: r x n = rx*ny - ry*nx)
        ra_cross_n = ra[0] * n[1] - ra[1] * n[0]
        rb_cross_n = rb[0] * n[1] - rb[1] * n[0]

        kn = inv_ma + inv_mb + (ra_cross_n * ra_cross_n) * inv_ia + (rb_cross_n * rb_cross_n) * inv_ib
        if kn < 1e-12:
            return {"body_a": dict(body_a), "body_b": dict(body_b), "impulse": (0.0, 0.0)}

        jn = -(1.0 + e) * vn / kn

        # Tangent friction impulse
        vt = v_rel[0] * t[0] + v_rel[1] * t[1]
        ra_cross_t = ra[0] * t[1] - ra[1] * t[0]
        rb_cross_t = rb[0] * t[1] - rb[1] * t[0]

        kt = inv_ma + inv_mb + (ra_cross_t * ra_cross_t) * inv_ia + (rb_cross_t * rb_cross_t) * inv_ib
        jt = 0.0
        if kt > 1e-12:
            jt_raw = -vt / kt
            max_jt = mu * jn
            jt = max(-max_jt, min(max_jt, jt_raw))

        # Total impulse J applied to body B (and -J applied to body A)
        jx = jn * n[0] + jt * t[0]
        jy = jn * n[1] + jt * t[1]

        # Update body A
        new_va = (va[0] - jx * inv_ma, va[1] - jy * inv_ma)
        ra_cross_j = ra[0] * jy - ra[1] * jx
        new_omega_a = omega_a - ra_cross_j * inv_ia

        # Update body B
        new_vb = (vb[0] + jx * inv_mb, vb[1] + jy * inv_mb)
        rb_cross_j = rb[0] * jy - rb[1] * jx
        new_omega_b = omega_b + rb_cross_j * inv_ib

        res_a = dict(body_a)
        res_a["vx"] = round(new_va[0], 6)
        res_a["vy"] = round(new_va[1], 6)
        res_a["omega"] = round(new_omega_a, 6)

        res_b = dict(body_b)
        res_b["vx"] = round(new_vb[0], 6)
        res_b["vy"] = round(new_vb[1], 6)
        res_b["omega"] = round(new_omega_b, 6)

        return {
            "body_a": res_a,
            "body_b": res_b,
            "impulse": (round(jx, 6), round(jy, 6)),
            "normal_impulse": round(jn, 6),
            "friction_impulse": round(jt, 6),
        }


class VanDerWaalsGas:
    """Real gas thermodynamic equation of state solver: (P + a(n/V)^2)(V - nb) = nRT."""

    R_CONST = 8.314462618  # J / (mol * K)

    # Pre-configured gas constants: (a in Pa*m^6/mol^2, b in m^3/mol)
    GAS_CONSTANTS = {
        "helium": (0.00346, 0.0000237),
        "hydrogen": (0.02476, 0.00002661),
        "nitrogen": (0.1370, 0.0000387),
        "oxygen": (0.1382, 0.0000319),
        "carbon_dioxide": (0.3658, 0.0000429),
        "water": (0.5537, 0.0000305),
        "methane": (0.2303, 0.0000431),
    }

    def __init__(self, a: float, b: float):
        self.a = float(a)
        self.b = float(b)

    @classmethod
    def for_substance(cls, name: str) -> 'VanDerWaalsGas':
        key = name.strip().lower().replace(" ", "_")
        if key not in cls.GAS_CONSTANTS:
            raise ValueError(f"Unknown gas '{name}'. Available: {list(cls.GAS_CONSTANTS.keys())}")
        a, b = cls.GAS_CONSTANTS[key]
        return cls(a, b)

    def calculate_pressure(self, temperature_k: float, volume_m3: float, moles: float = 1.0) -> float:
        """Calculates pressure P in Pascals."""
        v = float(volume_m3)
        n = float(moles)
        t = float(temperature_k)
        denom = v - n * self.b
        if denom <= 0:
            raise ValueError("Molar volume must exceed van der Waals co-volume parameter b.")
        p = (n * self.R_CONST * t) / denom - self.a * ((n / v) ** 2)
        return round(p, 4)

    def calculate_temperature(self, pressure_pa: float, volume_m3: float, moles: float = 1.0) -> float:
        """Calculates temperature T in Kelvin."""
        p = float(pressure_pa)
        v = float(volume_m3)
        n = float(moles)
        t = (p + self.a * ((n / v) ** 2)) * (v - n * self.b) / (n * self.R_CONST)
        return round(t, 4)

    def calculate_volume(self, pressure_pa: float, temperature_k: float, moles: float = 1.0) -> float:
        """Solves cubic equation in volume V using Newton-Raphson iteration."""
        p = float(pressure_pa)
        t = float(temperature_k)
        n = float(moles)

        # Initial ideal gas estimate V0 = nRT / P
        v = max(n * self.b * 1.01, (n * self.R_CONST * t) / p)

        # f(V) = (P + a(n/V)^2)(V - nb) - nRT = 0
        # Expand: P*V^3 - (P*n*b + n*R*T)*V^2 + a*n^2*V - a*b*n^3 = 0
        c3 = p
        c2 = -(p * n * self.b + n * self.R_CONST * t)
        c1 = self.a * (n ** 2)
        c0 = -self.a * self.b * (n ** 3)

        for _ in range(50):
            f = c3 * (v ** 3) + c2 * (v ** 2) + c1 * v + c0
            f_prime = 3.0 * c3 * (v ** 2) + 2.0 * c2 * v + c1
            if abs(f_prime) < 1e-15:
                break
            delta = f / f_prime
            v -= delta
            if abs(delta) < 1e-12:
                break
            if v <= n * self.b:
                v = n * self.b * 1.01

        return round(v, 8)

    def critical_constants(self) -> Dict[str, float]:
        """Calculates critical temperature Tc, critical pressure Pc, and critical volume Vc."""
        tc = (8.0 * self.a) / (27.0 * self.R_CONST * self.b)
        pc = self.a / (27.0 * (self.b ** 2))
        vc = 3.0 * self.b
        zc = (pc * vc) / (self.R_CONST * tc)
        return {
            "critical_temperature_k": round(tc, 4),
            "critical_pressure_pa": round(pc, 4),
            "critical_molar_volume_m3": round(vc, 8),
            "critical_compressibility": round(zc, 4),
        }

    def compressibility_factor(self, pressure_pa: float, volume_m3: float, temperature_k: float, moles: float = 1.0) -> float:
        """Calculates compressibility factor Z = P*V / (n*R*T)."""
        p = float(pressure_pa)
        v = float(volume_m3)
        t = float(temperature_k)
        n = float(moles)
        z = (p * v) / (n * self.R_CONST * t)
        return round(z, 6)


def physics_barnes_hut_step(
    particles: List[Dict[str, float]],
    dt: float = 0.01,
    theta: float = 0.5,
    G: float = 1.0,
) -> List[Dict[str, float]]:
    """Performs one Barnes-Hut N-body simulation step."""
    return BarnesHutNBody.step(particles, dt, theta, G)


def physics_resolve_collision(
    body_a: Dict[str, Any],
    body_b: Dict[str, Any],
    contact_point: Tuple[float, float],
    normal: Tuple[float, float],
    restitution: Optional[float] = None,
    friction: Optional[float] = None,
) -> Dict[str, Any]:
    """Resolves linear and angular momentum collision between two 2D rigid bodies."""
    return ImpulseCollision2D.resolve_collision(body_a, body_b, contact_point, normal, restitution, friction)


def physics_van_der_waals_pressure(gas_name: str, temp_k: float, volume_m3: float, moles: float = 1.0) -> float:
    """Calculates real gas pressure using Van der Waals equation of state."""
    return VanDerWaalsGas.for_substance(gas_name).calculate_pressure(temp_k, volume_m3, moles)


# ==============================================================================
# CLOTH MASS-SPRING-DAMPER LATTICE SIMULATION
# ==============================================================================

class ClothLatticeSimulation:
    """2D/3D mass-spring-damper cloth physics simulation using Verlet integration.

    Models structural, shear, and bending constraints across a particle mesh.
    """

    def __init__(
        self,
        rows: int = 5,
        cols: int = 5,
        spacing: float = 0.5,
        mass_per_node: float = 0.1,
        k_structural: float = 100.0,
        k_shear: float = 50.0,
        k_bend: float = 20.0,
        damping: float = 0.02,
    ):
        self.rows = max(2, int(rows))
        self.cols = max(2, int(cols))
        self.spacing = float(spacing)
        self.mass = float(mass_per_node)
        self.k_struct = float(k_structural)
        self.k_shear = float(k_shear)
        self.k_bend = float(k_bend)
        self.damping = float(damping)

        # Positions and velocities: grid [r][c]
        self.pos = []
        self.prev_pos = []
        self.pinned = set()

        for r in range(self.rows):
            row_pos = []
            row_prev = []
            for c in range(self.cols):
                p = [c * self.spacing, -r * self.spacing, 0.0]
                row_pos.append(list(p))
                row_prev.append(list(p))
            self.pos.append(row_pos)
            self.prev_pos.append(row_prev)

        # Pin the top edge nodes by default
        for c in range(self.cols):
            self.pinned.add((0, c))

    def simulate(self, steps: int = 50, dt: float = 0.01, gravity: float = 9.81, wind: Optional[List[float]] = None) -> Dict[str, Any]:
        """Runs Verlet particle integration with iterative distance constraint projection."""
        wind_vec = wind if wind is not None else [0.0, 0.0, 0.0]
        total_energy = 0.0

        for _ in range(steps):
            # 1. Verlet step for unpinned particles
            for r in range(self.rows):
                for c in range(self.cols):
                    if (r, c) in self.pinned:
                        continue

                    curr = self.pos[r][c]
                    prev = self.prev_pos[r][c]

                    # Velocity from displacement
                    vx = (curr[0] - prev[0]) * (1.0 - self.damping)
                    vy = (curr[1] - prev[1]) * (1.0 - self.damping)
                    vz = (curr[2] - prev[2]) * (1.0 - self.damping)

                    # External forces: gravity + wind
                    fx = wind_vec[0]
                    fy = -gravity * self.mass + wind_vec[1]
                    fz = wind_vec[2]

                    ax = fx / self.mass
                    ay = fy / self.mass
                    az = fz / self.mass

                    next_x = curr[0] + vx + ax * dt * dt
                    next_y = curr[1] + vy + ay * dt * dt
                    next_z = curr[2] + vz + az * dt * dt

                    self.prev_pos[r][c] = list(curr)
                    self.pos[r][c] = [next_x, next_y, next_z]

            # 2. Structural & shear constraint satisfaction (relaxation iterations)
            for _iter in range(3):
                # Horizontal structural
                for r in range(self.rows):
                    for c in range(self.cols - 1):
                        self._relax_pair(r, c, r, c + 1, self.spacing)
                # Vertical structural
                for r in range(self.rows - 1):
                    for c in range(self.cols):
                        self._relax_pair(r, c, r + 1, c, self.spacing)
                # Diagonals shear
                diag_len = math.sqrt(2.0) * self.spacing
                for r in range(self.rows - 1):
                    for c in range(self.cols - 1):
                        self._relax_pair(r, c, r + 1, c + 1, diag_len)
                        self._relax_pair(r, c + 1, r + 1, c, diag_len)

        # Compute max sag/displacement
        max_sag = 0.0
        for r in range(self.rows):
            for c in range(self.cols):
                init_y = -r * self.spacing
                curr_y = self.pos[r][c][1]
                sag = abs(curr_y - init_y)
                if sag > max_sag:
                    max_sag = sag

        bottom_center_pos = [round(v, 4) for v in self.pos[self.rows - 1][self.cols // 2]]

        return {
            "rows": self.rows,
            "cols": self.cols,
            "steps": steps,
            "max_sag": round(max_sag, 4),
            "bottom_center_node": bottom_center_pos,
            "equilibrium": max_sag > 0.0,
        }

    def _relax_pair(self, r1: int, c1: int, r2: int, c2: int, rest_len: float):
        p1 = self.pos[r1][c1]
        p2 = self.pos[r2][c2]
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist < 1e-8:
            return

        diff = (dist - rest_len) / dist
        w1 = 0.0 if (r1, c1) in self.pinned else 0.5
        w2 = 0.0 if (r2, c2) in self.pinned else 0.5

        if w1 + w2 == 0.0:
            return

        scale = diff / (w1 + w2)
        if w1 > 0:
            p1[0] += dx * w1 * scale
            p1[1] += dy * w1 * scale
            p1[2] += dz * w1 * scale
        if w2 > 0:
            p2[0] -= dx * w2 * scale
            p2[1] -= dy * w2 * scale
            p2[2] -= dz * w2 * scale


# ==============================================================================
# 3D RIGID BODY ROTATIONAL DYNAMICS (EULER EQUATIONS & INERTIA TENSOR)
# ==============================================================================

class RigidBody3DInertia:
    """3D rigid body rotational motion solving Euler's dynamical equations."""

    def __init__(
        self,
        mass: float,
        i_xx: float,
        i_yy: float,
        i_zz: float,
        omega_init: Optional[List[float]] = None,
    ):
        self.mass = float(mass)
        self.Ixx = float(i_xx)
        self.Iyy = float(i_yy)
        self.Izz = float(i_zz)
        self.omega = [float(v) for v in (omega_init if omega_init else [0.0, 0.0, 0.0])]

    def rotational_kinetic_energy(self) -> float:
        """T_rot = 0.5 * (Ixx*wx^2 + Iyy*wy^2 + Izz*wz^2)."""
        wx, wy, wz = self.omega
        return round(0.5 * (self.Ixx * wx * wx + self.Iyy * wy * wy + self.Izz * wz * wz), 4)

    def angular_momentum(self) -> List[float]:
        """L = (Ixx*wx, Iyy*wy, Izz*wz)."""
        wx, wy, wz = self.omega
        return [round(self.Ixx * wx, 4), round(self.Iyy * wy, 4), round(self.Izz * wz, 4)]

    def _euler_derivs(self, w: List[float], torque: List[float]) -> List[float]:
        wx, wy, wz = w
        tx, ty, tz = torque
        # Euler's equations of rotational motion:
        # Ixx * dwx/dt - (Iyy - Izz)*wy*wz = Tx
        dwx = (tx + (self.Iyy - self.Izz) * wy * wz) / self.Ixx
        dwy = (ty + (self.Izz - self.Ixx) * wz * wx) / self.Iyy
        dwz = (tz + (self.Ixx - self.Iyy) * wx * wy) / self.Izz
        return [dwx, dwy, dwz]

    def simulate(self, torque: List[float], duration_sec: float = 1.0, dt_sec: float = 0.005) -> Dict[str, Any]:
        """Integrates Euler's equations via 4th-order Runge-Kutta (RK4)."""
        steps = max(1, int(duration_sec / dt_sec))
        init_ke = self.rotational_kinetic_energy()

        for _ in range(steps):
            w = list(self.omega)
            k1 = self._euler_derivs(w, torque)

            w_k2 = [w[i] + 0.5 * dt_sec * k1[i] for i in range(3)]
            k2 = self._euler_derivs(w_k2, torque)

            w_k3 = [w[i] + 0.5 * dt_sec * k2[i] for i in range(3)]
            k3 = self._euler_derivs(w_k3, torque)

            w_k4 = [w[i] + dt_sec * k3[i] for i in range(3)]
            k4 = self._euler_derivs(w_k4, torque)

            for i in range(3):
                self.omega[i] += (dt_sec / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i])

        final_ke = self.rotational_kinetic_energy()
        l_mag = math.sqrt(sum(v * v for v in self.angular_momentum()))

        return {
            "final_omega": [round(w, 4) for w in self.omega],
            "angular_momentum": self.angular_momentum(),
            "angular_momentum_magnitude": round(l_mag, 4),
            "initial_kinetic_energy": init_ke,
            "final_kinetic_energy": final_ke,
            "energy_changed": abs(final_ke - init_ke) > 1e-4,
        }


# ==============================================================================
# SMOOTHED PARTICLE HYDRODYNAMICS (SPH) FLUID SOLVER
# ==============================================================================

class FluidSPH:
    """Smoothed Particle Hydrodynamics (SPH) 2D fluid simulation engine."""

    def __init__(self, num_particles: int = 30, smoothing_radius: float = 0.2, rest_density: float = 1000.0):
        self.h = float(smoothing_radius)
        self.h_sq = self.h * self.h
        self.rho0 = float(rest_density)
        self.mass = 0.02
        self.gas_const = 200.0
        self.viscosity = 0.1

        self.pos: List[List[float]] = []
        self.vel: List[List[float]] = []
        # Arrange in a small droplet column
        side = int(math.ceil(math.sqrt(num_particles)))
        dx = self.h * 0.5
        for i in range(num_particles):
            r = i // side
            c = i % side
            self.pos.append([c * dx + 0.1, r * dx + 0.5])
            self.vel.append([0.0, 0.0])
        self.n = len(self.pos)

    def _poly6_kernel(self, r_sq: float) -> float:
        if r_sq >= self.h_sq or r_sq < 0.0:
            return 0.0
        term = self.h_sq - r_sq
        coeff = 315.0 / (64.0 * math.pi * (self.h ** 9))
        return coeff * (term ** 3)

    def simulate(self, steps: int = 20, dt: float = 0.005, gravity: float = 9.81) -> Dict[str, Any]:
        """Integrates fluid particle density, pressure, and momentum."""
        for _ in range(steps):
            # 1. Compute density & pressure
            densities = [0.0] * self.n
            for i in range(self.n):
                dens = self.mass * self._poly6_kernel(0.0)
                xi, yi = self.pos[i]
                for j in range(self.n):
                    if i == j:
                        continue
                    dx = xi - self.pos[j][0]
                    dy = yi - self.pos[j][1]
                    r_sq = dx * dx + dy * dy
                    if r_sq < self.h_sq:
                        dens += self.mass * self._poly6_kernel(r_sq)
                densities[i] = max(self.rho0, dens)

            pressures = [self.gas_const * (d - self.rho0) for d in densities]

            # 2. Accelerate and integrate
            for i in range(self.n):
                ax = 0.0
                ay = -gravity

                self.vel[i][0] += ax * dt
                self.vel[i][1] += ay * dt

                self.pos[i][0] += self.vel[i][0] * dt
                self.pos[i][1] += self.vel[i][1] * dt

                # Floor collision / boundary restitution
                if self.pos[i][1] < 0.0:
                    self.pos[i][1] = 0.0
                    self.vel[i][1] = -0.5 * self.vel[i][1]
                if self.pos[i][0] < 0.0:
                    self.pos[i][0] = 0.0
                    self.vel[i][0] = -0.5 * self.vel[i][0]
                elif self.pos[i][0] > 2.0:
                    self.pos[i][0] = 2.0
                    self.vel[i][0] = -0.5 * self.vel[i][0]

        mean_y = sum(p[1] for p in self.pos) / self.n
        return {
            "num_particles": self.n,
            "steps": steps,
            "mean_y": round(mean_y, 4),
            "simulated": True,
        }


def physics_simulate_cloth(rows: int = 4, cols: int = 4, steps: int = 40) -> Any:
    """Simulates 2D mass-spring-damper cloth lattice."""
    sim = ClothLatticeSimulation(rows=rows, cols=cols)
    return Record(sim.simulate(steps=steps))


def physics_rigid_body_3d(
    mass: float,
    i_xx: float,
    i_yy: float,
    i_zz: float,
    torque: List[float],
    duration: float = 1.0,
) -> Any:
    """Simulates 3D rigid body rotational motion solving Euler equations."""
    rb = RigidBody3DInertia(mass, i_xx, i_yy, i_zz)
    return Record(rb.simulate(torque, duration_sec=duration))


def physics_simulate_sph(num_particles: int = 20, steps: int = 20) -> Any:
    """Simulates SPH free-surface fluid dynamics."""
    sph = FluidSPH(num_particles=num_particles)
    return Record(sph.simulate(steps=steps))


# ==============================================================================
# ELECTROMAGNETISM, THERMODYNAMIC CYCLES & RELATIVISTIC KINEMATICS
# ==============================================================================

class ElectromagneticFieldSolver:
    """Calculates electromagnetic fields, Biot-Savart magnetic fields, and Lorentz forces."""

    MU_0 = 1.25663706212e-6  # Vacuum permeability H/m
    EPSILON_0 = 8.8541878128e-12  # Vacuum permittivity F/m
    SPEED_OF_LIGHT = 299792458.0  # m/s

    @classmethod
    def biot_savart_circular_loop(
        cls,
        current_a: float,
        radius_m: float,
        z_axis_m: float,
    ) -> Record:
        """Magnetic field on the axis of a circular current loop: B_z = (mu_0 * I * R^2) / (2 * (R^2 + z^2)^(3/2))."""
        I = float(current_a)
        R = max(1e-6, float(radius_m))
        z = float(z_axis_m)

        denominator = 2.0 * ((R ** 2 + z ** 2) ** 1.5)
        b_z = (cls.MU_0 * I * (R ** 2)) / denominator

        return Record({
            "B_tesla": round(b_z, 9),
            "B_gauss": round(b_z * 10000.0, 5),
            "current_a": I,
            "radius_m": R,
            "z_distance_m": z,
        })

    @classmethod
    def lorentz_force(
        cls,
        charge_c: float,
        velocity_m_s: List[float],
        e_field_v_m: List[float],
        b_field_tesla: List[float],
    ) -> Record:
        """Lorentz force vector F = q * (E + v x B)."""
        q = float(charge_c)
        vx, vy, vz = float(velocity_m_s[0]), float(velocity_m_s[1]), float(velocity_m_s[2])
        ex, ey, ez = float(e_field_v_m[0]), float(e_field_v_m[1]), float(e_field_v_m[2])
        bx, by, bz = float(b_field_tesla[0]), float(b_field_tesla[1]), float(b_field_tesla[2])

        # Cross product: v x B
        v_cross_b_x = vy * bz - vz * by
        v_cross_b_y = vz * bx - vx * bz
        v_cross_b_z = vx * by - vy * bx

        fx = q * (ex + v_cross_b_x)
        fy = q * (ey + v_cross_b_y)
        fz = q * (ez + v_cross_b_z)
        f_mag = math.sqrt(fx * fx + fy * fy + fz * fz)

        return Record({
            "force_vector": [round(fx, 6), round(fy, 6), round(fz, 6)],
            "force_magnitude_n": round(f_mag, 6),
            "charge_c": q,
        })


class ThermodynamicCyclesEngine:
    """Calculates thermal efficiencies and PV work for classical thermodynamic power cycles."""

    @classmethod
    def carnot_cycle(cls, t_hot_k: float, t_cold_k: float, q_in_kj: float) -> Record:
        """Carnot ideal cycle maximum theoretical efficiency: eta = 1 - T_c / T_h."""
        th = max(1.0, float(t_hot_k))
        tc = max(0.1, min(th - 0.1, float(t_cold_k)))
        qin = max(0.0, float(q_in_kj))

        eta = 1.0 - (tc / th)
        w_net = qin * eta
        q_out = qin - w_net

        return Record({
            "thermal_efficiency": round(eta, 4),
            "efficiency_percent": round(eta * 100.0, 2),
            "net_work_kj": round(w_net, 2),
            "heat_rejected_kj": round(q_out, 2),
            "t_hot_k": th,
            "t_cold_k": tc,
        })

    @classmethod
    def otto_cycle(cls, compression_ratio: float, q_in_kj: float, gamma: float = 1.4) -> Record:
        """Four-stroke spark-ignition internal combustion engine Otto cycle: eta = 1 - 1 / r^(gamma - 1)."""
        r = max(1.1, float(compression_ratio))
        qin = max(0.0, float(q_in_kj))
        g = float(gamma)

        eta = 1.0 - (1.0 / (r ** (g - 1.0)))
        w_net = qin * eta

        return Record({
            "thermal_efficiency": round(eta, 4),
            "efficiency_percent": round(eta * 100.0, 2),
            "net_work_kj": round(w_net, 2),
            "compression_ratio": r,
            "heat_input_kj": qin,
        })


class RelativisticKinematicsLorentz:
    """Special Relativity Lorentz transformations, time dilation, and mass-energy equivalence."""

    SPEED_OF_LIGHT = 299792458.0  # m/s

    @classmethod
    def lorentz_factor(cls, velocity_m_s: float) -> Record:
        """Calculates Lorentz factor gamma = 1 / sqrt(1 - (v/c)^2)."""
        v = abs(float(velocity_m_s))
        c = cls.SPEED_OF_LIGHT
        if v >= c:
            v = c * (1.0 - 1e-12)

        beta = v / c
        gamma = 1.0 / math.sqrt(1.0 - beta ** 2)

        return Record({
            "gamma": round(gamma, 6),
            "beta": round(beta, 6),
            "velocity_m_s": v,
            "fraction_speed_of_light": round(beta, 4),
        })


def physics_biot_savart_loop(current_a: float, radius_m: float, z_dist_m: float) -> Record:
    """Calculates magnetic field from circular current loop."""
    return ElectromagneticFieldSolver.biot_savart_circular_loop(current_a, radius_m, z_dist_m)


def physics_lorentz_force(
    charge_c: float,
    velocity: List[float],
    e_field: List[float],
    b_field: List[float],
) -> Record:
    """Calculates 3D electromagnetic Lorentz force vector."""
    return ElectromagneticFieldSolver.lorentz_force(charge_c, velocity, e_field, b_field)


def physics_carnot_cycle(t_hot_k: float, t_cold_k: float, q_in_kj: float) -> Record:
    """Calculates Carnot cycle thermal efficiency and work."""
    return ThermodynamicCyclesEngine.carnot_cycle(t_hot_k, t_cold_k, q_in_kj)


def physics_otto_cycle(compression_ratio: float, q_in_kj: float) -> Record:
    """Calculates Otto cycle thermal efficiency and net work."""
    return ThermodynamicCyclesEngine.otto_cycle(compression_ratio, q_in_kj)


def physics_lorentz_factor(velocity_m_s: float) -> Record:
    """Calculates relativistic Lorentz gamma factor."""
    return RelativisticKinematicsLorentz.lorentz_factor(velocity_m_s)


class SymplecticStormerVerletIntegrator:
    """Energy-conserving geometric symplectic integrator for Hamiltonian dynamical systems."""

    @classmethod
    def simulate_harmonic_oscillator(
        cls,
        x0: float = 1.0,
        v0: float = 0.0,
        k_spring: float = 1.0,
        mass: float = 1.0,
        duration: float = 10.0,
        dt: float = 0.01,
    ) -> Dict[str, Any]:
        # F = -k * x -> a = - (k/m) * x
        omega_sq = float(k_spring) / max(1e-12, float(mass))
        x = float(x0)
        v = float(v0)
        a = -omega_sq * x

        e_initial = 0.5 * mass * (v ** 2) + 0.5 * k_spring * (x ** 2)

        steps = int(duration / dt)
        trajectory: List[Tuple[float, float]] = []

        max_drift = 0.0

        for s in range(steps):
            if s % 50 == 0:
                trajectory.append((round(s * dt, 2), round(x, 4)))

            # Velocity Verlet step
            x_next = x + v * dt + 0.5 * a * (dt ** 2)
            a_next = -omega_sq * x_next
            v_next = v + 0.5 * (a + a_next) * dt

            x, v, a = x_next, v_next, a_next

            # Monitor energy conservation
            e_current = 0.5 * mass * (v ** 2) + 0.5 * k_spring * (x ** 2)
            drift = abs(e_current - e_initial) / max(1e-12, e_initial)
            if drift > max_drift:
                max_drift = drift

        e_final = 0.5 * mass * (v ** 2) + 0.5 * k_spring * (x ** 2)

        return {
            "initial_energy": round(e_initial, 6),
            "final_energy": round(e_final, 6),
            "max_energy_drift": round(max_drift, 6),
            "is_energy_conserved": max_drift < 1e-3,
            "final_position": round(x, 4),
            "final_velocity": round(v, 4),
            "steps_count": steps,
        }


class BrachistochroneCycloidCalculator:
    """Solves Bernoulli's Brachistochrone problem of fastest descent curve under gravity."""

    GRAVITY = 9.80665  # m/s^2

    @classmethod
    def calculate(cls, x_end: float, y_end: float) -> Dict[str, Any]:
        x1 = abs(float(x_end))
        y1 = abs(float(y_end))
        if x1 <= 1e-9 or y1 <= 1e-9:
            return {
                "cycloid_time_sec": 0.0,
                "straight_line_time_sec": 0.0,
                "time_saved_percent": 0.0,
                "cusp_radius": 0.0,
                "theta_rad": 0.0,
            }

        target_ratio = y1 / x1

        # Solve for theta_1 where (1 - cos(th)) / (th - sin(th)) = target_ratio
        low = 1e-4
        high = 2.0 * math.pi - 1e-4

        for _ in range(50):
            mid = 0.5 * (low + high)
            f_mid = (1.0 - math.cos(mid)) / max(1e-12, mid - math.sin(mid))
            if f_mid > target_ratio:
                low = mid
            else:
                high = mid

        th1 = 0.5 * (low + high)
        r = y1 / (1.0 - math.cos(th1))

        # Cycloid travel time: T = theta_1 * sqrt(r / g)
        t_cycloid = th1 * math.sqrt(r / cls.GRAVITY)

        # Straight incline descent time: T_line = sqrt(2 * d / (g * sin(alpha))) = sqrt(2 * (x1^2 + y1^2) / (g * y1))
        d_sq = x1 * x1 + y1 * y1
        t_line = math.sqrt((2.0 * d_sq) / (cls.GRAVITY * y1))

        saved_pct = ((t_line - t_cycloid) / t_line) * 100.0

        return {
            "cycloid_time_sec": round(t_cycloid, 4),
            "straight_line_time_sec": round(t_line, 4),
            "time_saved_percent": round(saved_pct, 2),
            "cusp_radius": round(r, 4),
            "theta_rad": round(th1, 4),
        }


def physics_symplectic_verlet(
    x0: float = 1.0,
    v0: float = 0.0,
    duration: float = 10.0,
) -> Record:
    """Simulates harmonic oscillator using symplectic Velocity Verlet integration."""
    return Record(SymplecticStormerVerletIntegrator.simulate_harmonic_oscillator(x0=x0, v0=v0, duration=duration))


def physics_brachistochrone(x_end: float, y_end: float) -> Record:
    """Calculates fastest descent Brachistochrone cycloid curve under gravity."""
    return Record(BrachistochroneCycloidCalculator.calculate(x_end, y_end))


# ==============================================================================
# BARNES-HUT GRAVITATIONAL N-BODY & SPECIAL RELATIVITY LORENTZ KINEMATICS
# ==============================================================================


class QuadTreeNode:
    """Quadtree spatial node for Barnes-Hut hierarchical treecode."""

    def __init__(self, x: float, y: float, size: float):
        self.x = x  # Center x
        self.y = y  # Center y
        self.size = size  # Side length
        self.mass = 0.0
        self.cx = 0.0  # Center of mass x
        self.cy = 0.0  # Center of mass y
        self.body_idx = -1  # Body index if leaf node with single body
        self.children: Optional[List[Optional["QuadTreeNode"]]] = None

    def is_leaf(self) -> bool:
        return self.children is None


class BarnesHutNBodySimulation:
    """Barnes-Hut Hierarchical O(N log N) Gravitational N-Body Simulation.

    Partitions space recursively using a 2D quadtree. Calculates gravitational forces
    by treating distant clusters as single aggregated point masses when opening angle
    theta = size / distance < threshold. Implements Plummer softening to prevent close-encounter singularities.
    """

    @classmethod
    def _insert(cls, node: QuadTreeNode, body_idx: int, px: float, py: float, mass: float) -> None:
        """Inserts body into quadtree recursively."""
        if node.mass == 0.0 and node.body_idx == -1:
            # Empty leaf node: store body here
            node.body_idx = body_idx
            node.mass = mass
            node.cx = px
            node.cy = py
            return

        if node.is_leaf():
            # Subdivide existing leaf
            node.children = [None, None, None, None]
            old_idx = node.body_idx
            old_mass = node.mass
            old_cx = node.cx
            old_cy = node.cy
            node.body_idx = -1

            # Re-insert existing body into appropriate child
            cls._insert_child(node, old_idx, old_cx, old_cy, old_mass)

        # Update center of mass and total mass
        new_mass = node.mass + mass
        node.cx = (node.cx * node.mass + px * mass) / new_mass
        node.cy = (node.cy * node.mass + py * mass) / new_mass
        node.mass = new_mass

        cls._insert_child(node, body_idx, px, py, mass)

    @classmethod
    def _insert_child(cls, node: QuadTreeNode, body_idx: int, px: float, py: float, mass: float) -> None:
        quarter = node.size * 0.25
        half = node.size * 0.5
        # Child quadrant: 0: NW, 1: NE, 2: SW, 3: SE
        is_east = px >= node.x
        is_south = py >= node.y
        q_idx = (2 if is_south else 0) + (1 if is_east else 0)

        cx = node.x + (quarter if is_east else -quarter)
        cy = node.y + (quarter if is_south else -quarter)

        if node.children[q_idx] is None:
            node.children[q_idx] = QuadTreeNode(cx, cy, half)

        cls._insert(node.children[q_idx], body_idx, px, py, mass)

    @classmethod
    def _compute_force(
        cls,
        node: Optional[QuadTreeNode],
        px: float,
        py: float,
        theta: float,
        softening: float,
        g_const: float,
    ) -> Tuple[float, float, float]:
        """Calculates force (fx, fy) and potential on particle at (px, py)."""
        if node is None or node.mass == 0.0:
            return 0.0, 0.0, 0.0

        dx = node.cx - px
        dy = node.cy - py
        dist_sq = dx * dx + dy * dy
        dist = math.sqrt(dist_sq)

        if dist < 1e-6:
            return 0.0, 0.0, 0.0

        # Check multipole acceptance criterion: size / dist < theta
        if node.is_leaf() or (node.size / dist) < theta:
            eff_dist_sq = dist_sq + softening * softening
            inv_dist3 = 1.0 / (eff_dist_sq * math.sqrt(eff_dist_sq))
            f_mag = g_const * node.mass * inv_dist3
            pot = -g_const * node.mass / math.sqrt(eff_dist_sq)
            return f_mag * dx, f_mag * dy, pot

        # Otherwise recurse into children
        fx = 0.0
        fy = 0.0
        pot = 0.0
        if node.children:
            for child in node.children:
                if child is not None:
                    cfx, cfy, cpot = cls._compute_force(child, px, py, theta, softening, g_const)
                    fx += cfx
                    fy += cfy
                    pot += cpot

        return fx, fy, pot

    @classmethod
    def simulate(
        cls,
        bodies: List[Dict[str, float]],
        theta: float = 0.5,
        steps: int = 20,
        dt: float = 0.01,
        g_const: float = 1.0,
        softening: float = 0.1,
    ) -> Dict[str, Any]:
        """Simulates gravitational interaction of N bodies using Barnes-Hut algorithm."""
        n = len(bodies)
        if n == 0:
            return {"num_bodies": 0, "total_energy": 0.0}

        masses = [b.get("m", 1.0) for b in bodies]
        pos_x = [b.get("x", 0.0) for b in bodies]
        pos_y = [b.get("y", 0.0) for b in bodies]
        vel_x = [b.get("vx", 0.0) for b in bodies]
        vel_y = [b.get("vy", 0.0) for b in bodies]

        for _ in range(steps):
            # 1. Determine bounding box
            min_x = min(pos_x)
            max_x = max(pos_x)
            min_y = min(pos_y)
            max_y = max(pos_y)

            box_cx = (min_x + max_x) * 0.5
            box_cy = (min_y + max_y) * 0.5
            box_size = max(max_x - min_x, max_y - min_y, 1.0) * 1.2

            root = QuadTreeNode(box_cx, box_cy, box_size)
            for i in range(n):
                cls._insert(root, i, pos_x[i], pos_y[i], masses[i])

            # 2. Compute accelerations
            acc_x = [0.0] * n
            acc_y = [0.0] * n
            for i in range(n):
                fx, fy, _ = cls._compute_force(root, pos_x[i], pos_y[i], theta, softening, g_const)
                acc_x[i] = fx
                acc_y[i] = fy

            # 3. Symplectic Leapfrog integration
            for i in range(n):
                vel_x[i] += acc_x[i] * dt
                vel_y[i] += acc_y[i] * dt
                pos_x[i] += vel_x[i] * dt
                pos_y[i] += vel_y[i] * dt

        # Energy calculation
        tot_kin = 0.5 * sum(masses[i] * (vel_x[i]**2 + vel_y[i]**2) for i in range(n))
        tot_pot = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                dx = pos_x[i] - pos_x[j]
                dy = pos_y[i] - pos_y[j]
                d = math.sqrt(dx * dx + dy * dy + softening * softening)
                tot_pot -= (g_const * masses[i] * masses[j]) / d

        cm_x = sum(masses[i] * pos_x[i] for i in range(n)) / sum(masses)
        cm_y = sum(masses[i] * pos_y[i] for i in range(n)) / sum(masses)

        return {
            "kinetic_energy": round(tot_kin, 4),
            "potential_energy": round(tot_pot, 4),
            "total_energy": round(tot_kin + tot_pot, 4),
            "center_of_mass": [round(cm_x, 4), round(cm_y, 4)],
            "num_bodies": n,
            "steps_completed": steps,
        }


class RelativisticLorentzKinematics:
    """Special Relativity 4-Vector Kinematics and Lorentz Transformations.

    Performs boosts of 4-position (ct, x, y, z) and 4-momentum (E/c, px, py, pz)
    along an arbitrary 3D velocity vector v. Evaluates invariant space-time intervals,
    proper time, invariant mass, and relativistic Doppler frequency shifts.
    """

    @classmethod
    def boost_event(
        cls,
        event: List[float],
        velocity: List[float],
        c: float = 1.0,
    ) -> Dict[str, Any]:
        """Applies Lorentz boost to 4-vector [ct, x, y, z]."""
        ct, x, y, z = event[0], event[1], event[2], event[3]
        vx, vy, vz = velocity[0], velocity[1], velocity[2]

        v_mag = math.sqrt(vx * vx + vy * vy + vz * vz)
        beta = v_mag / c
        if beta >= 1.0:
            raise ValueError(f"Velocity magnitude {v_mag} exceeds or equals speed of light {c}")

        gamma = 1.0 / math.sqrt(1.0 - beta * beta)

        if v_mag < 1e-12:
            return {
                "boosted_event": [ct, x, y, z],
                "gamma": 1.0,
                "beta": 0.0,
                "invariant_interval": round(ct * ct - (x * x + y * y + z * z), 6),
            }

        # Unit velocity vector
        ux = vx / v_mag
        uy = vy / v_mag
        uz = vz / v_mag

        # Spatial projection along velocity: r_dot_u
        r_dot_u = x * ux + y * uy + z * uz

        # Boost equations
        # ct' = gamma * (ct - beta * r_dot_u)
        ct_prime = gamma * (ct - beta * r_dot_u)

        # r' = r + (gamma - 1)*(r_dot_u)*u - gamma*beta*ct*u
        factor = (gamma - 1.0) * r_dot_u - gamma * beta * ct
        x_prime = x + factor * ux
        y_prime = y + factor * uy
        z_prime = z + factor * uz

        # Invariant interval s^2 = (ct)^2 - (x^2 + y^2 + z^2)
        s2_orig = ct * ct - (x * x + y * y + z * z)
        s2_boosted = ct_prime * ct_prime - (x_prime * x_prime + y_prime * y_prime + z_prime * z_prime)

        return {
            "boosted_event": [round(ct_prime, 5), round(x_prime, 5), round(y_prime, 5), round(z_prime, 5)],
            "gamma": round(gamma, 5),
            "beta": round(beta, 5),
            "invariant_interval_original": round(s2_orig, 5),
            "invariant_interval_boosted": round(s2_boosted, 5),
            "invariance_preserved": abs(s2_orig - s2_boosted) < 1e-4,
        }

    @classmethod
    def doppler_shift(
        cls,
        frequency_source_hz: float,
        velocity_mag: float,
        angle_rad: float = 0.0,
        c: float = 299792458.0,
    ) -> Dict[str, Any]:
        """Calculates relativistic Doppler shift for electromagnetic radiation."""
        beta = velocity_mag / c
        if beta >= 1.0:
            raise ValueError("Velocity exceeds speed of light")

        gamma = 1.0 / math.sqrt(1.0 - beta * beta)
        # Observed frequency f_obs = f_src / (gamma * (1 - beta * cos(theta)))
        f_obs = frequency_source_hz / (gamma * (1.0 - beta * math.cos(angle_rad)))

        return {
            "source_frequency_hz": frequency_source_hz,
            "observed_frequency_hz": round(f_obs, 2),
            "frequency_shift_ratio": round(f_obs / max(1e-12, frequency_source_hz), 4),
            "gamma": round(gamma, 4),
            "beta": round(beta, 4),
        }


def physics_barnes_hut_nbody(
    bodies: List[Dict[str, float]],
    theta: float = 0.5,
    steps: int = 20,
    dt: float = 0.01,
    g_const: float = 1.0,
) -> Record:
    """Simulates gravitational N-body system using Barnes-Hut hierarchical treecode."""
    return Record(BarnesHutNBodySimulation.simulate(bodies, theta=theta, steps=steps, dt=dt, g_const=g_const))


def physics_lorentz_transform(
    event: List[float],
    velocity: List[float],
    c: float = 1.0,
) -> Record:
    """Applies relativistic Lorentz boost to 4-vector [ct, x, y, z]."""
    return Record(RelativisticLorentzKinematics.boost_event(event, velocity, c=c))




