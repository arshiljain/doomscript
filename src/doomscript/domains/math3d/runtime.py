"""3D Mathematics, Linear Algebra, Ray Tracing, and Signed Distance Fields for DoomScript."""

import math
from typing import List, Tuple, Dict, Any, Optional, Union, Callable


class Vec3:
    """3D Vector representation with complete vector algebra."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return f"Vec3({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        raise IndexError("Vec3 index out of range (0-2)")

    def __len__(self) -> int:
        return 3

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Vec3):
            return abs(self.x - other.x) < 1e-6 and abs(self.y - other.y) < 1e-6 and abs(self.z - other.z) < 1e-6
        return False

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def __mul__(self, scalar: Union[float, int]) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: Union[float, int]) -> "Vec3":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: Union[float, int]) -> "Vec3":
        if scalar == 0:
            raise ZeroDivisionError("Cannot divide vector by zero scalar")
        inv = 1.0 / scalar
        return Vec3(self.x * inv, self.y * inv, self.z * inv)

    def dot(self, other: "Vec3") -> float:
        """Compute the dot (scalar) product."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        """Compute the vector cross product."""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length_squared(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    def length(self) -> float:
        return math.sqrt(self.length_squared())

    def normalize(self) -> "Vec3":
        l = self.length()
        if l < 1e-9:
            return Vec3(0.0, 0.0, 0.0)
        return self / l

    def distance_to(self, other: "Vec3") -> float:
        return (self - other).length()

    def reflect(self, normal: "Vec3") -> "Vec3":
        """Reflect this vector around an incident surface normal."""
        return self - normal * (2.0 * self.dot(normal))

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.z]


class Vec4:
    """4D Vector or Homogeneous 3D Coordinate."""

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.w = float(w)

    def __repr__(self) -> str:
        return f"Vec4({self.x:.4f}, {self.y:.4f}, {self.z:.4f}, {self.w:.4f})"

    def __getitem__(self, index: int) -> float:
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2:
            return self.z
        elif index == 3:
            return self.w
        raise IndexError("Vec4 index out of range (0-3)")

    def to_vec3(self) -> Vec3:
        if abs(self.w) > 1e-9:
            return Vec3(self.x / self.w, self.y / self.w, self.z / self.w)
        return Vec3(self.x, self.y, self.z)


class Mat4:
    """4x4 Matrix for 3D Computer Graphics Transformations."""

    def __init__(self, values: Optional[List[List[float]]] = None):
        if values is None:
            self.m = [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        else:
            self.m = [[float(v) for v in row] for row in values]

    @classmethod
    def identity(cls) -> "Mat4":
        return cls()

    @classmethod
    def translation(cls, tx: float, ty: float, tz: float) -> "Mat4":
        res = cls()
        res.m[0][3] = tx
        res.m[1][3] = ty
        res.m[2][3] = tz
        return res

    @classmethod
    def scaling(cls, sx: float, sy: float, sz: float) -> "Mat4":
        res = cls()
        res.m[0][0] = sx
        res.m[1][1] = sy
        res.m[2][2] = sz
        return res

    @classmethod
    def rotation_x(cls, radians: float) -> "Mat4":
        c, s = math.cos(radians), math.sin(radians)
        res = cls()
        res.m[1][1] = c
        res.m[1][2] = -s
        res.m[2][1] = s
        res.m[2][2] = c
        return res

    @classmethod
    def rotation_y(cls, radians: float) -> "Mat4":
        c, s = math.cos(radians), math.sin(radians)
        res = cls()
        res.m[0][0] = c
        res.m[0][2] = s
        res.m[2][0] = -s
        res.m[2][2] = c
        return res

    @classmethod
    def rotation_z(cls, radians: float) -> "Mat4":
        c, s = math.cos(radians), math.sin(radians)
        res = cls()
        res.m[0][0] = c
        res.m[0][1] = -s
        res.m[1][0] = s
        res.m[1][1] = c
        return res

    @classmethod
    def look_at(cls, eye: Vec3, target: Vec3, up: Vec3) -> "Mat4":
        """Camera View Matrix pointing from eye to target."""
        f = (target - eye).normalize()
        s = f.cross(up.normalize()).normalize()
        u = s.cross(f)

        res = cls()
        res.m[0][0] = s.x
        res.m[0][1] = s.y
        res.m[0][2] = s.z
        res.m[0][3] = -s.dot(eye)

        res.m[1][0] = u.x
        res.m[1][1] = u.y
        res.m[1][2] = u.z
        res.m[1][3] = -u.dot(eye)

        res.m[2][0] = -f.x
        res.m[2][1] = -f.y
        res.m[2][2] = -f.z
        res.m[2][3] = f.dot(eye)
        return res

    @classmethod
    def perspective(cls, fov_radians: float, aspect: float, near: float, far: float) -> "Mat4":
        """Symmetric Perspective Projection Matrix."""
        tan_half = math.tan(fov_radians / 2.0)
        res = cls([[0.0] * 4 for _ in range(4)])
        res.m[0][0] = 1.0 / (aspect * tan_half)
        res.m[1][1] = 1.0 / tan_half
        res.m[2][2] = -(far + near) / (far - near)
        res.m[2][3] = -(2.0 * far * near) / (far - near)
        res.m[3][2] = -1.0
        return res

    @classmethod
    def orthographic(cls, left: float, right: float, bottom: float, top: float, near: float, far: float) -> "Mat4":
        """Orthographic Projection Matrix."""
        res = cls()
        res.m[0][0] = 2.0 / (right - left)
        res.m[1][1] = 2.0 / (top - bottom)
        res.m[2][2] = -2.0 / (far - near)
        res.m[0][3] = -(right + left) / (right - left)
        res.m[1][3] = -(top + bottom) / (top - bottom)
        res.m[2][3] = -(far + near) / (far - near)
        return res

    def __mul__(self, other: Union["Mat4", Vec4, Vec3]) -> Any:
        if isinstance(other, Mat4):
            res = Mat4([[0.0] * 4 for _ in range(4)])
            for i in range(4):
                for j in range(4):
                    res.m[i][j] = sum(self.m[i][k] * other.m[k][j] for k in range(4))
            return res
        elif isinstance(other, Vec4):
            v = [other.x, other.y, other.z, other.w]
            out = [sum(self.m[i][k] * v[k] for k in range(4)) for i in range(4)]
            return Vec4(out[0], out[1], out[2], out[3])
        elif isinstance(other, Vec3):
            v4 = Vec4(other.x, other.y, other.z, 1.0)
            return (self * v4).to_vec3()
        raise TypeError(f"Unsupported operand type for Mat4 multiplication: {type(other)}")

    def transpose(self) -> "Mat4":
        return Mat4([[self.m[j][i] for j in range(4)] for i in range(4)])


class Quat:
    """Quaternion for 3D Rotations."""

    def __init__(self, w: float = 1.0, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return f"Quat({self.w:.4f}, {self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    @classmethod
    def from_axis_angle(cls, axis: Vec3, angle_radians: float) -> "Quat":
        n = axis.normalize()
        half_ang = angle_radians * 0.5
        s = math.sin(half_ang)
        return cls(math.cos(half_ang), n.x * s, n.y * s, n.z * s)

    def norm(self) -> float:
        return math.sqrt(self.w * self.w + self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self) -> "Quat":
        n = self.norm()
        if n < 1e-9:
            return Quat(1.0, 0.0, 0.0, 0.0)
        inv = 1.0 / n
        return Quat(self.w * inv, self.x * inv, self.y * inv, self.z * inv)

    def conjugate(self) -> "Quat":
        return Quat(self.w, -self.x, -self.y, -self.z)

    def __mul__(self, other: "Quat") -> "Quat":
        return Quat(
            self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z,
            self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y,
            self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x,
            self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w,
        )

    def rotate_vec(self, v: Vec3) -> Vec3:
        qv = Quat(0.0, v.x, v.y, v.z)
        res = self * qv * self.conjugate()
        return Vec3(res.x, res.y, res.z)

    def to_mat4(self) -> Mat4:
        q = self.normalize()
        w, x, y, z = q.w, q.x, q.y, q.z
        return Mat4([
            [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w), 0.0],
            [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w), 0.0],
            [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y), 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ])

    @classmethod
    def slerp(cls, q1: "Quat", q2: "Quat", t: float) -> "Quat":
        """Spherical Linear Interpolation between two quaternions."""
        cos_half_theta = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z
        if cos_half_theta < 0.0:
            q2 = Quat(-q2.w, -q2.x, -q2.y, -q2.z)
            cos_half_theta = -cos_half_theta

        if abs(cos_half_theta) >= 1.0:
            return q1

        half_theta = math.acos(cos_half_theta)
        sin_half_theta = math.sqrt(1.0 - cos_half_theta * cos_half_theta)

        if abs(sin_half_theta) < 1e-3:
            return Quat(
                q1.w * 0.5 + q2.w * 0.5,
                q1.x * 0.5 + q2.x * 0.5,
                q1.y * 0.5 + q2.y * 0.5,
                q1.z * 0.5 + q2.z * 0.5,
            ).normalize()

        ratio_a = math.sin((1.0 - t) * half_theta) / sin_half_theta
        ratio_b = math.sin(t * half_theta) / sin_half_theta
        return Quat(
            q1.w * ratio_a + q2.w * ratio_b,
            q1.x * ratio_a + q2.x * ratio_b,
            q1.y * ratio_a + q2.y * ratio_b,
            q1.z * ratio_a + q2.z * ratio_b,
        )


class Ray:
    """3D Ray with origin and normalized direction vector."""

    def __init__(self, origin: Vec3, direction: Vec3):
        self.origin = origin
        self.direction = direction.normalize()

    def point_at(self, t: float) -> Vec3:
        return self.origin + self.direction * t


def math3d_ray_sphere_intersect(ray: Ray, center: Vec3, radius: float) -> Dict[str, Any]:
    """Ray-Sphere intersection test."""
    oc = ray.origin - center
    a = ray.direction.dot(ray.direction)
    b = 2.0 * oc.dot(ray.direction)
    c = oc.dot(oc) - radius * radius
    discriminant = b * b - 4 * a * c

    if discriminant < 0:
        return {"hit": False, "t": None, "point": None, "normal": None}

    sqrt_disc = math.sqrt(discriminant)
    t = (-b - sqrt_disc) / (2.0 * a)
    if t < 0:
        t = (-b + sqrt_disc) / (2.0 * a)
        if t < 0:
            return {"hit": False, "t": None, "point": None, "normal": None}

    hit_pt = ray.point_at(t)
    normal = (hit_pt - center).normalize()
    return {"hit": True, "t": t, "point": hit_pt, "normal": normal}


def math3d_ray_triangle_intersect(ray: Ray, v0: Vec3, v1: Vec3, v2: Vec3) -> Dict[str, Any]:
    """Möller-Trumbore Ray-Triangle intersection."""
    edge1 = v1 - v0
    edge2 = v2 - v0
    h = ray.direction.cross(edge2)
    a = edge1.dot(h)

    if abs(a) < 1e-7:
        return {"hit": False, "t": None, "point": None, "normal": None}

    f = 1.0 / a
    s = ray.origin - v0
    u = f * s.dot(h)
    if u < 0.0 or u > 1.0:
        return {"hit": False, "t": None, "point": None, "normal": None}

    q = s.cross(edge1)
    v = f * ray.direction.dot(q)
    if v < 0.0 or u + v > 1.0:
        return {"hit": False, "t": None, "point": None, "normal": None}

    t = f * edge2.dot(q)
    if t > 1e-7:
        hit_pt = ray.point_at(t)
        normal = edge1.cross(edge2).normalize()
        return {"hit": True, "t": t, "point": hit_pt, "normal": normal}
    return {"hit": False, "t": None, "point": None, "normal": None}


def math3d_sdf_sphere(p: Vec3, radius: float) -> float:
    """Signed Distance Field: Sphere centered at origin."""
    return p.length() - radius


def math3d_sdf_box(p: Vec3, b: Vec3) -> float:
    """Signed Distance Field: Axis-aligned box centered at origin."""
    q = Vec3(abs(p.x) - b.x, abs(p.y) - b.y, abs(p.z) - b.z)
    outside = Vec3(max(q.x, 0.0), max(q.y, 0.0), max(q.z, 0.0)).length()
    inside = min(max(q.x, max(q.y, q.z)), 0.0)
    return outside + inside


def math3d_sdf_torus(p: Vec3, r_major: float, r_minor: float) -> float:
    """Signed Distance Field: Torus lying in XZ plane."""
    q_x = math.sqrt(p.x * p.x + p.z * p.z) - r_major
    q_y = p.y
    return math.sqrt(q_x * q_x + q_y * q_y) - r_minor


def math3d_sdf_smooth_union(d1: float, d2: float, k: float = 0.1) -> float:
    """Smooth minimum (blending) between two distance fields."""
    h = max(k - abs(d1 - d2), 0.0) / k
    return min(d1, d2) - h * h * k * (1.0 / 4.0)


def math3d_sdf_normal(sdf_fn: Callable[[Vec3], float], p: Vec3, eps: float = 1e-4) -> Vec3:
    """Numerical gradient estimation of normal on SDF surface."""
    dx = sdf_fn(Vec3(p.x + eps, p.y, p.z)) - sdf_fn(Vec3(p.x - eps, p.y, p.z))
    dy = sdf_fn(Vec3(p.x, p.y + eps, p.z)) - sdf_fn(Vec3(p.x, p.y - eps, p.z))
    dz = sdf_fn(Vec3(p.x, p.y, p.z + eps)) - sdf_fn(Vec3(p.x, p.y, p.z - eps))
    return Vec3(dx, dy, dz).normalize()


def math3d_raymarch(sdf_fn: Callable[[Vec3], float], ray: Ray, max_steps: int = 100, max_dist: float = 100.0, eps: float = 1e-3) -> Dict[str, Any]:
    """Sphere tracing / raymarching engine through an arbitrary SDF."""
    t = 0.0
    for step in range(max_steps):
        p = ray.point_at(t)
        dist = sdf_fn(p)
        if dist < eps:
            norm = math3d_sdf_normal(sdf_fn, p)
            return {"hit": True, "steps": step + 1, "t": t, "point": p, "normal": norm}
        t += dist
        if t >= max_dist:
            break
    return {"hit": False, "steps": max_steps, "t": None, "point": None, "normal": None}
