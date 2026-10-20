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
