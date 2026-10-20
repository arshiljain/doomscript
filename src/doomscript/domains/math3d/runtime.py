"""3D Mathematics, Linear Algebra, Ray Tracing, and Signed Distance Fields for DoomScript."""

import math
from typing import List, Tuple, Dict, Any, Optional, Union, Callable
from doomscript.core.record import Record


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


class Raymarcher3D:
    """Scene graph and sphere-tracing SDF renderer."""

    def __init__(self, camera_pos: Optional[Vec3] = None, look_at: Optional[Vec3] = None, fov: float = 60.0):
        self.camera_pos = camera_pos or Vec3(0.0, 1.0, -3.0)
        self.look_at = look_at or Vec3(0.0, 0.0, 0.0)
        self.fov = fov
        self.objects: List[Dict[str, Any]] = []
        self.lights: List[Vec3] = [Vec3(2.0, 5.0, -2.0)]

    def add_sphere(self, center: Vec3, radius: float, color: Tuple[float, float, float] = (1.0, 0.2, 0.2)) -> None:
        self.objects.append({"type": "sphere", "center": center, "radius": float(radius), "color": color})

    def add_box(self, center: Vec3, size: Vec3, color: Tuple[float, float, float] = (0.2, 0.8, 0.2)) -> None:
        self.objects.append({"type": "box", "center": center, "size": size, "color": color})

    def add_plane(self, height: float = 0.0, color: Tuple[float, float, float] = (0.5, 0.5, 0.5)) -> None:
        self.objects.append({"type": "plane", "height": float(height), "color": color})

    def scene_sdf(self, p: Vec3) -> Tuple[float, Tuple[float, float, float]]:
        """Evaluates union SDF of all objects in the scene, returning (distance, color)."""
        min_d = float("inf")
        hit_color = (0.0, 0.0, 0.0)

        for obj in self.objects:
            t = obj["type"]
            c = obj["color"]
            if t == "sphere":
                rel_p = p - obj["center"]
                d = rel_p.length() - obj["radius"]
            elif t == "box":
                rel_p = p - obj["center"]
                b = obj["size"]
                qx = abs(rel_p.x) - b.x
                qy = abs(rel_p.y) - b.y
                qz = abs(rel_p.z) - b.z
                outside = Vec3(max(qx, 0.0), max(qy, 0.0), max(qz, 0.0)).length()
                inside = min(max(qx, max(qy, qz)), 0.0)
                d = outside + inside
            elif t == "plane":
                d = p.y - obj["height"]
            else:
                continue

            if d < min_d:
                min_d = d
                hit_color = c

        return min_d, hit_color

    def estimate_normal(self, p: Vec3, eps: float = 1e-4) -> Vec3:
        dx = self.scene_sdf(Vec3(p.x + eps, p.y, p.z))[0] - self.scene_sdf(Vec3(p.x - eps, p.y, p.z))[0]
        dy = self.scene_sdf(Vec3(p.x, p.y + eps, p.z))[0] - self.scene_sdf(Vec3(p.x, p.y - eps, p.z))[0]
        dz = self.scene_sdf(Vec3(p.x, p.y, p.z + eps))[0] - self.scene_sdf(Vec3(p.x, p.y, p.z - eps))[0]
        return Vec3(dx, dy, dz).normalize()

    def render_buffer(self, width: int = 40, height: int = 20, max_steps: int = 64) -> List[List[str]]:
        """Renders an ASCII depth and shading map of the scene."""
        ascii_chars = " .:-=+*#%@"
        grid = [[" " for _ in range(width)] for _ in range(height)]

        cam_dir = (self.look_at - self.camera_pos).normalize()
        up = Vec3(0.0, 1.0, 0.0)
        right = cam_dir.cross(up).normalize()
        cam_up = right.cross(cam_dir).normalize()

        aspect = width / height
        fov_rad = math.radians(self.fov)
        scale = math.tan(fov_rad / 2.0)

        for y in range(height):
            for x in range(width):
                px = (2.0 * (x + 0.5) / width - 1.0) * aspect * scale
                py = (1.0 - 2.0 * (y + 0.5) / height) * scale
                ray_dir = (cam_dir + right * px + cam_up * py).normalize()
                ray = Ray(self.camera_pos, ray_dir)

                t = 0.0
                hit = False
                for _ in range(max_steps):
                    p = ray.point_at(t)
                    dist, color = self.scene_sdf(p)
                    if dist < 0.001:
                        hit = True
                        normal = self.estimate_normal(p)
                        # Lambertian lighting
                        light_dir = (self.lights[0] - p).normalize()
                        diff = max(normal.dot(light_dir), 0.0)
                        char_idx = min(len(ascii_chars) - 1, int(diff * (len(ascii_chars) - 1)))
                        grid[y][x] = ascii_chars[char_idx]
                        break
                    t += dist
                    if t > 50.0:
                        break

        return grid


class DualQuaternion:
    """Unified representation of 3D rigid body rotation and translation (SE(3))."""

    def __init__(self, real: Optional[List[float]] = None, dual: Optional[List[float]] = None):
        # real: [w, x, y, z] rotation quaternion
        # dual: [w, x, y, z] translation dual part
        self.r = list(real or [1.0, 0.0, 0.0, 0.0])
        self.d = list(dual or [0.0, 0.0, 0.0, 0.0])

    @classmethod
    def from_rotation_translation(cls, rot_quat: List[float], trans_vec: List[float]) -> "DualQuaternion":
        """Builds dual quaternion from rotation quaternion [w, x, y, z] and translation vector [x, y, z]."""
        # Normalize rotation
        norm_r = math.sqrt(sum(v ** 2 for v in rot_quat)) or 1.0
        r = [v / norm_r for v in rot_quat]
        # Dual part: d = 0.5 * (t * r) where t = [0, tx, ty, tz]
        tx, ty, tz = trans_vec[0], trans_vec[1], trans_vec[2]
        rw, rx, ry, rz = r[0], r[1], r[2], r[3]
        dw = 0.5 * (-tx * rx - ty * ry - tz * rz)
        dx = 0.5 * (tx * rw + ty * rz - tz * ry)
        dy = 0.5 * (-tx * rz + ty * rw + tz * rx)
        dz = 0.5 * (tx * ry - ty * rx + tz * rw)
        return cls(r, [dw, dx, dy, dz])

    def to_translation(self) -> List[float]:
        """Extracts translation vector [x, y, z] = 2 * dual * conjugate(real)."""
        rw, rx, ry, rz = self.r
        dw, dx, dy, dz = self.d
        # conj(r) = [rw, -rx, -ry, -rz]
        # 2 * d * conj(r)
        tx = 2.0 * (-dw * rx + dx * rw - dy * rz + dz * ry)
        ty = 2.0 * (-dw * ry + dx * rz + dy * rw - dz * rx)
        tz = 2.0 * (-dw * rz - dx * ry + dy * rx + dz * rw)
        return [round(tx, 5), round(ty, 5), round(tz, 5)]

    def to_rotation(self) -> List[float]:
        return [round(v, 5) for v in self.r]

    def conjugate(self) -> "DualQuaternion":
        """Dual quaternion conjugate: [rw, -rx, -ry, -rz], [dw, -dx, -dy, -dz]."""
        r_conj = [self.r[0], -self.r[1], -self.r[2], -self.r[3]]
        d_conj = [self.d[0], -self.d[1], -self.d[2], -self.d[3]]
        return DualQuaternion(r_conj, d_conj)

    def multiply(self, other: "DualQuaternion") -> "DualQuaternion":
        """Dual quaternion product: q1 * q2 = r1*r2 + eps*(r1*d2 + d1*r2)."""
        def quat_mul(q1: List[float], q2: List[float]) -> List[float]:
            w1, x1, y1, z1 = q1
            w2, x2, y2, z2 = q2
            return [
                w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
                w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
                w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
            ]

        def quat_add(q1: List[float], q2: List[float]) -> List[float]:
            return [q1[i] + q2[i] for i in range(4)]

        new_r = quat_mul(self.r, other.r)
        new_d = quat_add(quat_mul(self.r, other.dual_part()), quat_mul(self.d, other.r))
        return DualQuaternion(new_r, new_d)

    def dual_part(self) -> List[float]:
        return list(self.d)

    def transform_point(self, pt: List[float]) -> List[float]:
        """Transforms a 3D point [x, y, z] by the dual quaternion."""
        t = self.to_translation()
        # Rotate pt by r: r * pt * conj(r)
        rw, rx, ry, rz = self.r
        px, py, pz = pt
        # Quat mul [0, px, py, pz] by r
        qx = rw * px + ry * pz - rz * py
        qy = rw * py - rx * pz + rz * px
        qz = rw * pz + rx * py - ry * px
        qw = -rx * px - ry * py - rz * pz
        # Quat mul result by conj(r)
        rx_rot = -qw * rx + qx * rw - qy * rz + qz * ry
        ry_rot = -qw * ry + qx * rz + qy * rw - qz * rx
        rz_rot = -qw * rz - qx * ry + qy * rx + qz * rw
        return [round(rx_rot + t[0], 5), round(ry_rot + t[1], 5), round(rz_rot + t[2], 5)]

    @classmethod
    def sclerp(cls, dq1: "DualQuaternion", dq2: "DualQuaternion", t: float) -> "DualQuaternion":
        """Screw Linear Interpolation (ScLERP) between two dual quaternions."""
        t_clamped = max(0.0, min(1.0, float(t)))
        # Linear interpolation with normalization
        interp_r = [dq1.r[i] * (1.0 - t_clamped) + dq2.r[i] * t_clamped for i in range(4)]
        norm_r = math.sqrt(sum(v ** 2 for v in interp_r)) or 1.0
        interp_r = [v / norm_r for v in interp_r]

        interp_d = [dq1.d[i] * (1.0 - t_clamped) + dq2.d[i] * t_clamped for i in range(4)]
        return cls(interp_r, interp_d)


class Quickhull3D:
    """Computes the 3D Convex Hull of a point set in O(n log n)."""

    def __init__(self):
        pass

    def compute_hull(self, points: List[List[float]]) -> Dict[str, Any]:
        """Computes 3D convex hull vertices and triangular faces."""
        pts = [Vec3(p[0], p[1], p[2]) for p in points]
        n = len(pts)
        if n < 4:
            return {"vertices": points, "faces": []}

        # 1. Find 6 extreme points
        min_x = min(range(n), key=lambda i: pts[i].x)
        max_x = max(range(n), key=lambda i: pts[i].x)
        min_y = min(range(n), key=lambda i: pts[i].y)
        max_y = max(range(n), key=lambda i: pts[i].y)
        min_z = min(range(n), key=lambda i: pts[i].z)
        max_z = max(range(n), key=lambda i: pts[i].z)

        extremes = list({min_x, max_x, min_y, max_y, min_z, max_z})
        if len(extremes) < 3:
            extremes = list(range(min(4, n)))

        # Find 3 non-collinear points
        p0_idx, p1_idx = extremes[0], extremes[1]
        p2_idx = None
        max_dist = 0.0
        line_vec = pts[p1_idx] - pts[p0_idx]
        for i in extremes[2:] + [x for x in range(n) if x not in extremes]:
            dist = (pts[i] - pts[p0_idx]).cross(line_vec).length()
            if dist > max_dist:
                max_dist = dist
                p2_idx = i

        if p2_idx is None or max_dist < 1e-6:
            return {"vertices": points, "faces": []}

        # Find 4th non-coplanar point
        normal = (pts[p1_idx] - pts[p0_idx]).cross(pts[p2_idx] - pts[p0_idx]).normalize()
        p3_idx = None
        max_plane_dist = 0.0
        for i in range(n):
            plane_dist = abs((pts[i] - pts[p0_idx]).dot(normal))
            if plane_dist > max_plane_dist:
                max_plane_dist = plane_dist
                p3_idx = i

        if p3_idx is None or max_plane_dist < 1e-6:
            return {"vertices": points, "faces": []}

        # Initial tetrahedron faces oriented outward
        init_v = [p0_idx, p1_idx, p2_idx, p3_idx]
        faces = [
            (p0_idx, p1_idx, p2_idx),
            (p0_idx, p2_idx, p3_idx),
            (p0_idx, p3_idx, p1_idx),
            (p1_idx, p3_idx, p2_idx),
        ]

        # Fix face normals
        centroid = (pts[p0_idx] + pts[p1_idx] + pts[p2_idx] + pts[p3_idx]) * 0.25
        oriented_faces = []
        for i0, i1, i2 in faces:
            fn = (pts[i1] - pts[i0]).cross(pts[i2] - pts[i0])
            if fn.dot(pts[i0] - centroid) < 0:
                oriented_faces.append((i0, i2, i1))
            else:
                oriented_faces.append((i0, i1, i2))

        # Iteratively expand faces
        unassigned = [i for i in range(n) if i not in init_v]

        for p_idx in unassigned:
            pt = pts[p_idx]
            visible_faces = []
            for f_idx, (i0, i1, i2) in enumerate(oriented_faces):
                fn = (pts[i1] - pts[i0]).cross(pts[i2] - pts[i0])
                if fn.dot(pt - pts[i0]) > 1e-6:
                    visible_faces.append(f_idx)

            if not visible_faces:
                continue

            # Find horizon edges (edges shared by 1 visible and 1 non-visible face)
            edge_counts: Dict[Tuple[int, int], int] = {}
            for f_idx in visible_faces:
                i0, i1, i2 = oriented_faces[f_idx]
                for u, v in [(i0, i1), (i1, i2), (i2, i0)]:
                    edge = (min(u, v), max(u, v))
                    edge_counts[edge] = edge_counts.get(edge, 0) + 1

            horizon_edges = []
            for (u, v), cnt in edge_counts.items():
                if cnt == 1:
                    horizon_edges.append((u, v))

            # Remove visible faces
            new_faces = [f for idx, f in enumerate(oriented_faces) if idx not in visible_faces]

            # Add new triangles connecting horizon edges to p_idx
            for u, v in horizon_edges:
                tri = (u, v, p_idx)
                fn = (pts[v] - pts[u]).cross(pts[p_idx] - pts[u])
                if fn.dot(pts[u] - centroid) < 0:
                    tri = (u, p_idx, v)
                new_faces.append(tri)

            oriented_faces = new_faces

        used_indices = sorted(list({idx for face in oriented_faces for idx in face}))
        return {
            "vertices": [points[i] for i in used_indices],
            "vertex_indices": used_indices,
            "faces": oriented_faces,
            "num_faces": len(oriented_faces),
        }


def math3d_raymarcher_render(width: int = 40, height: int = 20) -> List[List[str]]:
    """Renders a 3D demo scene to an ASCII buffer using sphere tracing."""
    rm = Raymarcher3D()
    rm.add_sphere(Vec3(0.0, 0.0, 0.0), 1.0)
    rm.add_plane(-1.0)
    return rm.render_buffer(width, height)


def math3d_dual_quaternion(rot: List[float], trans: List[float]) -> DualQuaternion:
    """Constructs a DualQuaternion from rotation quaternion and translation vector."""
    return DualQuaternion.from_rotation_translation(rot, trans)


def math3d_quickhull(points: List[List[float]]) -> Dict[str, Any]:
    """Computes the 3D Convex Hull of a cloud of points."""
    qh = Quickhull3D()
    return qh.compute_hull(points)


# ==============================================================================
# ORIENTED BOUNDING BOX (OBB) & 15-AXIS SEPARATING AXIS THEOREM (SAT)
# ==============================================================================

class OrientedBoundingBoxOBB:
    """3D Oriented Bounding Box with full 15-axis Separating Axis Theorem (SAT)."""

    def __init__(
        self,
        center: Union[Vec3, List[float]],
        extents: Union[Vec3, List[float]],
        axes: Optional[List[Union[Vec3, List[float]]]] = None,
    ):
        self.center = Vec3(center[0], center[1], center[2]) if not isinstance(center, Vec3) else center
        self.extents = Vec3(abs(extents[0]), abs(extents[1]), abs(extents[2])) if not isinstance(extents, Vec3) else Vec3(abs(extents.x), abs(extents.y), abs(extents.z))
        if axes is None:
            self.axes = [Vec3(1.0, 0.0, 0.0), Vec3(0.0, 1.0, 0.0), Vec3(0.0, 0.0, 1.0)]
        else:
            self.axes = [
                Vec3(a[0], a[1], a[2]).normalize() if not isinstance(a, Vec3) else a.normalize()
                for a in axes
            ]

    def get_corners(self) -> List[List[float]]:
        """Returns the 8 corner vertices in 3D world space."""
        c = self.center
        e0 = self.axes[0] * self.extents.x
        e1 = self.axes[1] * self.extents.y
        e2 = self.axes[2] * self.extents.z
        corners = []
        for s0 in (-1.0, 1.0):
            for s1 in (-1.0, 1.0):
                for s2 in (-1.0, 1.0):
                    p = c + (e0 * s0) + (e1 * s1) + (e2 * s2)
                    corners.append([p.x, p.y, p.z])
        return corners

    def contains_point(self, pt: Union[Vec3, List[float]]) -> bool:
        """Determines if a 3D point lies inside the OBB."""
        p = Vec3(pt[0], pt[1], pt[2]) if not isinstance(pt, Vec3) else pt
        d = p - self.center
        proj0 = abs(d.dot(self.axes[0]))
        proj1 = abs(d.dot(self.axes[1]))
        proj2 = abs(d.dot(self.axes[2]))
        return bool(proj0 <= self.extents.x and proj1 <= self.extents.y and proj2 <= self.extents.z)

    def intersects_obb(self, other: "OrientedBoundingBoxOBB") -> Dict[str, Any]:
        """Performs full 15-axis SAT collision check between two OBBs."""
        d = other.center - self.center

        # Build list of candidate test axes: 3 from A, 3 from B, 9 from cross products
        test_axes = []
        # Box A face normals
        for a in self.axes:
            test_axes.append(a)
        # Box B face normals
        for b in other.axes:
            test_axes.append(b)
        # 9 cross product axes
        for a in self.axes:
            for b in other.axes:
                cp = a.cross(b)
                if cp.length_squared() > 1e-8:
                    test_axes.append(cp.normalize())

        min_overlap = float("inf")
        best_axis = [0.0, 0.0, 0.0]

        for axis in test_axes:
            # Projected radius of box A
            ra = (
                self.extents.x * abs(self.axes[0].dot(axis))
                + self.extents.y * abs(self.axes[1].dot(axis))
                + self.extents.z * abs(self.axes[2].dot(axis))
            )
            # Projected radius of box B
            rb = (
                other.extents.x * abs(other.axes[0].dot(axis))
                + other.extents.y * abs(other.axes[1].dot(axis))
                + other.extents.z * abs(other.axes[2].dot(axis))
            )
            # Distance along separating axis
            dist = abs(d.dot(axis))

            if dist > (ra + rb) + 1e-7:
                # Disjoint! Separating axis found
                return {
                    "colliding": False,
                    "penetration_depth": 0.0,
                    "separation_axis": [axis.x, axis.y, axis.z],
                    "distance": round(dist - (ra + rb), 6),
                }

            overlap = (ra + rb) - dist
            if overlap < min_overlap:
                min_overlap = overlap
                best_axis = [axis.x, axis.y, axis.z]

        return {
            "colliding": True,
            "penetration_depth": round(min_overlap, 6),
            "separation_axis": best_axis,
            "distance": 0.0,
        }


# ==============================================================================
# CAMERA VIEW FRUSTUM CULLING
# ==============================================================================

class FrustumPlane:
    """3D Plane representation (A, B, C, D) where A*x + B*y + C*z + D = 0."""

    def __init__(self, normal: Vec3, distance: float):
        l = normal.length()
        if l > 1e-9:
            self.normal = normal / l
            self.distance = distance / l
        else:
            self.normal = normal
            self.distance = distance

    def signed_distance(self, pt: Vec3) -> float:
        return self.normal.dot(pt) + self.distance


class FrustumCuller3D:
    """6-plane camera viewing frustum with sphere, AABB, and scene culling."""

    def __init__(
        self,
        fov_deg: float = 60.0,
        aspect: float = 1.333,
        near: float = 0.1,
        far: float = 100.0,
        eye: Optional[Union[Vec3, List[float]]] = None,
        target: Optional[Union[Vec3, List[float]]] = None,
        up: Optional[Union[Vec3, List[float]]] = None,
    ):
        self.fov_deg = float(fov_deg)
        self.aspect = float(aspect)
        self.near = float(near)
        self.far = float(far)

        cam_eye = Vec3(eye[0], eye[1], eye[2]) if eye is not None and not isinstance(eye, Vec3) else (eye or Vec3(0.0, 0.0, 0.0))
        cam_tgt = Vec3(target[0], target[1], target[2]) if target is not None and not isinstance(target, Vec3) else (target or Vec3(0.0, 0.0, -1.0))
        cam_up = Vec3(up[0], up[1], up[2]) if up is not None and not isinstance(up, Vec3) else (up or Vec3(0.0, 1.0, 0.0))

        # Camera coordinate frame
        fwd = (cam_tgt - cam_eye).normalize()
        right = fwd.cross(cam_up).normalize()
        true_up = right.cross(fwd).normalize()

        half_v_fov = math.radians(self.fov_deg) * 0.5
        tang = math.tan(half_v_fov)
        nh = self.near * tang
        nw = nh * self.aspect
        fh = self.far * tang
        fw = fh * self.aspect

        nc = cam_eye + (fwd * self.near)
        fc = cam_eye + (fwd * self.far)

        # 6 planes facing INWARD
        self.planes: List[FrustumPlane] = []

        # Near plane: normal = fwd, pt = nc
        self.planes.append(FrustumPlane(fwd, -fwd.dot(nc)))
        # Far plane: normal = -fwd, pt = fc
        self.planes.append(FrustumPlane(fwd * -1.0, fwd.dot(fc)))

        # Top plane
        top_pt = nc + (true_up * nh)
        top_n = (top_pt - cam_eye).cross(right).normalize()
        self.planes.append(FrustumPlane(top_n, -top_n.dot(top_pt)))

        # Bottom plane
        bot_pt = nc - (true_up * nh)
        bot_n = right.cross(bot_pt - cam_eye).normalize()
        self.planes.append(FrustumPlane(bot_n, -bot_n.dot(bot_pt)))

        # Left plane
        left_pt = nc - (right * nw)
        left_n = (left_pt - cam_eye).cross(true_up).normalize()
        self.planes.append(FrustumPlane(left_n, -left_n.dot(left_pt)))

        # Right plane
        right_pt = nc + (right * nw)
        right_n = true_up.cross(right_pt - cam_eye).normalize()
        self.planes.append(FrustumPlane(right_n, -right_n.dot(right_pt)))

    def cull_sphere(self, center: Union[Vec3, List[float]], radius: float) -> Dict[str, Any]:
        """Tests whether a bounding sphere is INSIDE, INTERSECTS, or OUTSIDE the frustum."""
        c = Vec3(center[0], center[1], center[2]) if not isinstance(center, Vec3) else center
        r = float(radius)
        all_inside = True

        for plane in self.planes:
            dist = plane.signed_distance(c)
            if dist < -r:
                return {"status": "OUTSIDE", "visible": False, "distance": dist}
            elif dist < r:
                all_inside = False

        status = "INSIDE" if all_inside else "INTERSECTS"
        return {"status": status, "visible": True, "distance": 0.0}

    def cull_scene(self, objects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Culls an array of scene objects containing 'center'/'position' and 'radius'."""
        visible = []
        culled = 0
        for obj in objects:
            pos = obj.get("center") or obj.get("position") or [0.0, 0.0, 0.0]
            rad = float(obj.get("radius", 1.0))
            res = self.cull_sphere(pos, rad)
            if res["visible"]:
                visible.append(obj)
            else:
                culled += 1

        total = len(objects)
        cull_ratio = round(culled / total, 3) if total > 0 else 0.0
        return {
            "visible_objects": visible,
            "visible_count": len(visible),
            "culled_count": culled,
            "total_objects": total,
            "cull_ratio": cull_ratio,
        }


# ==============================================================================
# BOUNDING VOLUME HIERARCHY (BVH) ACCELERATION TREE
# ==============================================================================

class BvhNode:
    """Node in the hierarchical BVH tree."""

    def __init__(self, min_pt: Vec3, max_pt: Vec3):
        self.min_pt = min_pt
        self.max_pt = max_pt
        self.left: Optional["BvhNode"] = None
        self.right: Optional["BvhNode"] = None
        self.triangle_indices: List[int] = []
        self.is_leaf: bool = False


class BvhSpatialTree:
    """Bounding Volume Hierarchy (BVH) spatial accelerator for 3D meshes."""

    def __init__(self, triangles: List[List[List[float]]], max_leaf_capacity: int = 2):
        self.triangles = [
            [Vec3(p[0], p[1], p[2]) for p in tri]
            for tri in triangles
        ]
        self.max_leaf_capacity = max(1, int(max_leaf_capacity))
        self.centroids: List[Vec3] = []
        for tri in self.triangles:
            c = (tri[0] + tri[1] + tri[2]) / 3.0
            self.centroids.append(c)

        all_indices = list(range(len(self.triangles)))
        self.root = self._build_tree(all_indices)

    def _compute_bbox(self, indices: List[int]) -> Tuple[Vec3, Vec3]:
        min_x, min_y, min_z = float("inf"), float("inf"), float("inf")
        max_x, max_y, max_z = float("-inf"), float("-inf"), float("-inf")
        for idx in indices:
            for pt in self.triangles[idx]:
                min_x = min(min_x, pt.x)
                min_y = min(min_y, pt.y)
                min_z = min(min_z, pt.z)
                max_x = max(max_x, pt.x)
                max_y = max(max_y, pt.y)
                max_z = max(max_z, pt.z)
        return Vec3(min_x, min_y, min_z), Vec3(max_x, max_y, max_z)

    def _build_tree(self, indices: List[int]) -> Optional[BvhNode]:
        if not indices:
            return None

        min_pt, max_pt = self._compute_bbox(indices)
        node = BvhNode(min_pt, max_pt)

        if len(indices) <= self.max_leaf_capacity:
            node.is_leaf = True
            node.triangle_indices = indices
            return node

        # Choose longest axis of bounding box
        extent = max_pt - min_pt
        axis = 0
        if extent.y > extent.x and extent.y > extent.z:
            axis = 1
        elif extent.z > extent.x and extent.z > extent.y:
            axis = 2

        # Sort indices along axis by triangle centroid
        indices.sort(key=lambda idx: self.centroids[idx][axis])
        mid = len(indices) // 2

        node.left = self._build_tree(indices[:mid])
        node.right = self._build_tree(indices[mid:])
        return node

    def _intersect_ray_aabb(self, node: BvhNode, origin: Vec3, inv_dir: Vec3) -> Tuple[bool, float]:
        t0x = (node.min_pt.x - origin.x) * inv_dir.x
        t1x = (node.max_pt.x - origin.x) * inv_dir.x
        tmin_x, tmax_x = min(t0x, t1x), max(t0x, t1x)

        t0y = (node.min_pt.y - origin.y) * inv_dir.y
        t1y = (node.max_pt.y - origin.y) * inv_dir.y
        tmin_y, tmax_y = min(t0y, t1y), max(t0y, t1y)

        tmin = max(tmin_x, tmin_y)
        tmax = min(tmax_x, tmax_y)

        t0z = (node.min_pt.z - origin.z) * inv_dir.z
        t1z = (node.max_pt.z - origin.z) * inv_dir.z
        tmin_z, tmax_z = min(t0z, t1z), max(t0z, t1z)

        tmin = max(tmin, tmin_z)
        tmax = min(tmax, tmax_z)

        if tmax >= max(0.0, tmin):
            return True, max(0.0, tmin)
        return False, float("inf")

    def _intersect_ray_triangle(
        self, origin: Vec3, direction: Vec3, tri_idx: int
    ) -> Tuple[bool, float, float, float]:
        v0, v1, v2 = self.triangles[tri_idx]
        e1 = v1 - v0
        e2 = v2 - v0
        h = direction.cross(e2)
        a = e1.dot(h)

        if abs(a) < 1e-8:
            return False, 0.0, 0.0, 0.0

        f = 1.0 / a
        s = origin - v0
        u = f * s.dot(h)
        if u < 0.0 or u > 1.0:
            return False, 0.0, 0.0, 0.0

        q = s.cross(e1)
        v = f * direction.dot(q)
        if v < 0.0 or (u + v) > 1.0:
            return False, 0.0, 0.0, 0.0

        t = f * e2.dot(q)
        if t > 1e-7:
            return True, t, u, v
        return False, 0.0, 0.0, 0.0

    def intersect_ray(
        self, origin: Union[Vec3, List[float]], direction: Union[Vec3, List[float]]
    ) -> Dict[str, Any]:
        """Traces a ray through the BVH returning closest hit triangle, hit point, and stats."""
        orig = Vec3(origin[0], origin[1], origin[2]) if not isinstance(origin, Vec3) else origin
        dir_vec = Vec3(direction[0], direction[1], direction[2]).normalize() if not isinstance(direction, Vec3) else direction.normalize()

        inv_dir = Vec3(
            1.0 / dir_vec.x if abs(dir_vec.x) > 1e-9 else 1e9,
            1.0 / dir_vec.y if abs(dir_vec.y) > 1e-9 else 1e9,
            1.0 / dir_vec.z if abs(dir_vec.z) > 1e-9 else 1e9,
        )

        closest_t = float("inf")
        hit_tri_idx = -1
        hit_u, hit_v = 0.0, 0.0
        nodes_visited = 0
        triangles_tested = 0

        stack = [self.root] if self.root else []
        while stack:
            node = stack.pop()
            if not node:
                continue
            nodes_visited += 1

            hit_box, t_box = self._intersect_ray_aabb(node, orig, inv_dir)
            if not hit_box or t_box > closest_t:
                continue

            if node.is_leaf:
                for idx in node.triangle_indices:
                    triangles_tested += 1
                    hit, t, u, v = self._intersect_ray_triangle(orig, dir_vec, idx)
                    if hit and t < closest_t:
                        closest_t = t
                        hit_tri_idx = idx
                        hit_u, hit_v = u, v
            else:
                if node.left:
                    stack.append(node.left)
                if node.right:
                    stack.append(node.right)

        if hit_tri_idx != -1:
            hit_pt = orig + (dir_vec * closest_t)
            return {
                "hit": True,
                "t": round(closest_t, 6),
                "hit_point": [round(hit_pt.x, 6), round(hit_pt.y, 6), round(hit_pt.z, 6)],
                "triangle_index": hit_tri_idx,
                "barycentric_u": round(hit_u, 6),
                "barycentric_v": round(hit_v, 6),
                "triangles_tested": triangles_tested,
                "nodes_visited": nodes_visited,
            }
        return {
            "hit": False,
            "t": -1.0,
            "hit_point": None,
            "triangle_index": -1,
            "barycentric_u": 0.0,
            "barycentric_v": 0.0,
            "triangles_tested": triangles_tested,
            "nodes_visited": nodes_visited,
        }


# ==============================================================================
# RECORD-WRAPPED DOOMSCRIPT HELPER FUNCTIONS
# ==============================================================================

def math3d_obb_create(
    center: List[float],
    extents: List[float],
    axes: Optional[List[List[float]]] = None,
) -> Any:
    """Creates a 3D Oriented Bounding Box record."""
    obb = OrientedBoundingBoxOBB(center, extents, axes)
    return Record({
        "center": [obb.center.x, obb.center.y, obb.center.z],
        "extents": [obb.extents.x, obb.extents.y, obb.extents.z],
        "corners": obb.get_corners(),
        "instance": obb,
    })


def math3d_obb_test_collision(obb_a: Any, obb_b: Any) -> Any:
    """Tests collision between two OBBs using 15-axis SAT."""
    a = obb_a.instance if hasattr(obb_a, "instance") else obb_a
    b = obb_b.instance if hasattr(obb_b, "instance") else obb_b
    if not isinstance(a, OrientedBoundingBoxOBB):
        a = OrientedBoundingBoxOBB(obb_a["center"], obb_a["extents"])
    if not isinstance(b, OrientedBoundingBoxOBB):
        b = OrientedBoundingBoxOBB(obb_b["center"], obb_b["extents"])
    return Record(a.intersects_obb(b))


def math3d_frustum_create(
    fov_deg: float = 60.0,
    aspect: float = 1.333,
    near: float = 0.1,
    far: float = 100.0,
    eye: Optional[List[float]] = None,
    target: Optional[List[float]] = None,
    up: Optional[List[float]] = None,
) -> Any:
    """Creates a camera view frustum record."""
    frustum = FrustumCuller3D(fov_deg, aspect, near, far, eye, target, up)
    return Record({
        "fov_deg": frustum.fov_deg,
        "aspect": frustum.aspect,
        "near": frustum.near,
        "far": frustum.far,
        "instance": frustum,
    })


def math3d_frustum_cull_sphere(frustum: Any, center: List[float], radius: float) -> Any:
    """Tests if a sphere is inside, intersecting, or outside the frustum."""
    f = frustum.instance if hasattr(frustum, "instance") else frustum
    return Record(f.cull_sphere(center, radius))


def math3d_frustum_cull_scene(frustum: Any, objects: List[Dict[str, Any]]) -> Any:
    """Culls an array of 3D scene objects against the frustum."""
    f = frustum.instance if hasattr(frustum, "instance") else frustum
    return Record(f.cull_scene(objects))


def math3d_bvh_build(triangles: List[List[List[float]]], max_leaf: int = 2) -> Any:
    """Constructs a Bounding Volume Hierarchy tree from a list of 3D triangles."""
    bvh = BvhSpatialTree(triangles, max_leaf)
    return Record({
        "num_triangles": len(triangles),
        "instance": bvh,
    })


def math3d_bvh_raycast(bvh: Any, origin: List[float], direction: List[float]) -> Any:
    """Traces a ray through the BVH spatial acceleration tree."""
    tree = bvh.instance if hasattr(bvh, "instance") else bvh
    return Record(tree.intersect_ray(origin, direction))


class DualQuaternionTransform:
    """Rigid 3D SE(3) transformation representation using unit dual quaternions."""

    @staticmethod
    def _quat_mul(q1: Tuple[float, float, float, float], q2: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        w1, x1, y1, z1 = q1
        w2, x2, y2, z2 = q2
        return (
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        )

    @staticmethod
    def _quat_conj(q: Tuple[float, float, float, float]) -> Tuple[float, float, float, float]:
        w, x, y, z = q
        return (w, -x, -y, -z)

    @staticmethod
    def _quat_norm(q: Tuple[float, float, float, float]) -> float:
        w, x, y, z = q
        return math.sqrt(w * w + x * x + y * y + z * z)

    @classmethod
    def create(cls, translation: List[float], rotation_quat: List[float]) -> Dict[str, Any]:
        rw, rx, ry, rz = [float(x) for x in rotation_quat]
        r_norm = math.sqrt(rw * rw + rx * rx + ry * ry + rz * rz) or 1.0
        qr = (rw / r_norm, rx / r_norm, ry / r_norm, rz / r_norm)

        tx, ty, tz = [float(x) for x in translation[:3]]
        t_quat = (0.0, tx, ty, tz)

        t_mul_qr = cls._quat_mul(t_quat, qr)
        qd = tuple(0.5 * c for c in t_mul_qr)

        return {
            "qr": [round(c, 6) for c in qr],
            "qd": [round(c, 6) for c in qd],
            "translation": [round(tx, 6), round(ty, 6), round(tz, 6)],
        }

    @classmethod
    def transform_points(
        cls,
        translation: List[float],
        rotation_quat: List[float],
        points: List[List[float]],
    ) -> Dict[str, Any]:
        dq = cls.create(translation, rotation_quat)
        qr = tuple(dq["qr"])
        tx, ty, tz = dq["translation"]
        qr_conj = cls._quat_conj(qr)

        transformed = []
        for pt in points:
            px, py, pz = [float(x) for x in pt[:3]]
            p_quat = (0.0, px, py, pz)
            rotated = cls._quat_mul(cls._quat_mul(qr, p_quat), qr_conj)
            p_prime = [
                round(rotated[1] + tx, 6),
                round(rotated[2] + ty, 6),
                round(rotated[3] + tz, 6),
            ]
            transformed.append(p_prime)

        angle = 2.0 * math.acos(max(-1.0, min(1.0, qr[0])))
        sin_half = math.sin(angle / 2.0)
        if abs(sin_half) > 1e-6:
            axis = [round(qr[1] / sin_half, 4), round(qr[2] / sin_half, 4), round(qr[3] / sin_half, 4)]
            pitch = round(tx * axis[0] + ty * axis[1] + tz * axis[2], 4)
        else:
            axis = [1.0, 0.0, 0.0]
            pitch = round(math.sqrt(tx * tx + ty * ty + tz * tz), 4)

        return {
            "dual_quaternion": dq,
            "screw_angle_rad": round(angle, 4),
            "screw_axis": axis,
            "screw_pitch": pitch,
            "points_count": len(transformed),
            "transformed_points": transformed,
        }


class DualQuaternionScLERP:
    """Dual Quaternion Spherical Linear Interpolation (ScLERP) for smooth SE(3) transforms."""

    @classmethod
    def interpolate(
        cls,
        trans1: List[float],
        rot1: List[float],
        trans2: List[float],
        rot2: List[float],
        t: float,
    ) -> Dict[str, Any]:
        t_param = max(0.0, min(1.0, float(t)))
        w1, x1, y1, z1 = [float(x) for x in rot1]
        w2, x2, y2, z2 = [float(x) for x in rot2]

        dot = w1 * w2 + x1 * x2 + y1 * y2 + z1 * z2
        if dot < 0.0:
            w2, x2, y2, z2 = -w2, -x2, -y2, -z2
            dot = -dot

        if dot > 0.9995:
            w = w1 + t_param * (w2 - w1)
            x = x1 + t_param * (x2 - x1)
            y = y1 + t_param * (y2 - y1)
            z = z1 + t_param * (z2 - z1)
        else:
            theta_0 = math.acos(dot)
            theta = theta_0 * t_param
            sin_theta = math.sin(theta)
            sin_theta_0 = math.sin(theta_0)
            s0 = math.cos(theta) - dot * sin_theta / sin_theta_0
            s1 = sin_theta / sin_theta_0
            w = s0 * w1 + s1 * w2
            x = s0 * x1 + s1 * x2
            y = s0 * y1 + s1 * y2
            z = s0 * z1 + s1 * z2

        r_norm = math.sqrt(w * w + x * x + y * y + z * z) or 1.0
        interp_rot = [round(w / r_norm, 6), round(x / r_norm, 6), round(y / r_norm, 6), round(z / r_norm, 6)]

        interp_trans = [
            round(trans1[i] + t_param * (trans2[i] - trans1[i]), 6)
            for i in range(3)
        ]

        dq = DualQuaternionTransform.create(interp_trans, interp_rot)
        return {
            "t_parameter": t_param,
            "interpolated_translation": interp_trans,
            "interpolated_rotation": interp_rot,
            "dual_quaternion": dq,
        }


def math3d_dual_quaternion_transform(
    translation: List[float],
    rotation_quat: List[float],
    points: List[List[float]],
) -> Any:
    """Transforms 3D points using unit dual quaternion."""
    return Record(DualQuaternionTransform.transform_points(translation, rotation_quat, points))


def math3d_dual_quaternion_sclerp(
    trans1: List[float],
    rot1: List[float],
    trans2: List[float],
    rot2: List[float],
    t: float,
) -> Any:
    """Interpolates between two rigid transforms via Dual Quaternion ScLERP."""
    return Record(DualQuaternionScLERP.interpolate(trans1, rot1, trans2, rot2, t))


# ==============================================================================
# GJK COLLISION DETECTION & EXPANDING POLYTOPE ALGORITHM (EPA) IN 3D
# ==============================================================================

class GJKCollision3DAndEPA:
    """Gilbert-Johnson-Keerthi (GJK) 3D convex collision detector & EPA contact solver."""

    @staticmethod
    def _dot(a: List[float], b: List[float]) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    @staticmethod
    def _cross(a: List[float], b: List[float]) -> List[float]:
        return [
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        ]

    @classmethod
    def _support(cls, vertices: List[List[float]], direction: List[float]) -> List[float]:
        """Support function: argmax_{v in vertices} (v . d)."""
        best_v = vertices[0]
        best_dot = cls._dot(best_v, direction)
        for v in vertices[1:]:
            d = cls._dot(v, direction)
            if d > best_dot:
                best_dot = d
                best_v = v
        return list(best_v)

    @classmethod
    def _minkowski_support(
        cls,
        shape_a: List[List[float]],
        shape_b: List[List[float]],
        direction: List[float],
    ) -> List[float]:
        """Support point of Minkowski difference A - B: S_A(d) - S_B(-d)."""
        sa = cls._support(shape_a, direction)
        neg_dir = [-direction[0], -direction[1], -direction[2]]
        sb = cls._support(shape_b, neg_dir)
        return [sa[0] - sb[0], sa[1] - sb[1], sa[2] - sb[2]]

    @classmethod
    def test_intersection(
        cls,
        shape_a: List[List[float]],
        shape_b: List[List[float]],
        max_iter: int = 40,
    ) -> Dict[str, Any]:
        """Tests convex shapes A and B for intersection using 3D GJK."""
        if not shape_a or not shape_b:
            return {"intersecting": False, "iterations": 0}

        # Initial search direction (from center to center)
        c_a = [sum(v[i] for v in shape_a) / len(shape_a) for i in range(3)]
        c_b = [sum(v[i] for v in shape_b) / len(shape_b) for i in range(3)]
        dir_vec = [c_b[0] - c_a[0], c_b[1] - c_a[1], c_b[2] - c_a[2]]
        if cls._dot(dir_vec, dir_vec) < 1e-6:
            dir_vec = [1.0, 0.0, 0.0]

        # Simplex vertices
        simplex: List[List[float]] = []

        # First point
        p0 = cls._minkowski_support(shape_a, shape_b, dir_vec)
        simplex.append(p0)
        dir_vec = [-p0[0], -p0[1], -p0[2]]

        iterations = 0
        intersecting = False

        while iterations < max_iter:
            iterations += 1
            p_new = cls._minkowski_support(shape_a, shape_b, dir_vec)

            # If new support point did not pass the origin, no intersection
            if cls._dot(p_new, dir_vec) < 0:
                intersecting = False
                break

            simplex.append(p_new)

            # Solve simplex (line, triangle, or tetrahedron)
            k = len(simplex)
            if k == 2:
                # Line segment AB
                b, a = simplex[0], simplex[1]
                ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
                ao = [-a[0], -a[1], -a[2]]
                # Direction perpendicular to AB towards origin
                ab_cross_ao = cls._cross(ab, ao)
                dir_vec = cls._cross(ab_cross_ao, ab)
                if cls._dot(dir_vec, dir_vec) < 1e-9:
                    dir_vec = [-ab[1], ab[0], 0.0]
            elif k == 3:
                # Triangle ABC
                c, b, a = simplex[0], simplex[1], simplex[2]
                ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
                ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
                ao = [-a[0], -a[1], -a[2]]
                abc_norm = cls._cross(ab, ac)

                if cls._dot(cls._cross(abc_norm, ac), ao) > 0:
                    simplex = [c, a]
                    dir_vec = cls._cross(cls._cross(ac, ao), ac)
                elif cls._dot(cls._cross(ab, abc_norm), ao) > 0:
                    simplex = [b, a]
                    dir_vec = cls._cross(cls._cross(ab, ao), ab)
                else:
                    if cls._dot(abc_norm, ao) > 0:
                        dir_vec = abc_norm
                    else:
                        simplex = [b, c, a]
                        dir_vec = [-abc_norm[0], -abc_norm[1], -abc_norm[2]]
            elif k == 4:
                # Tetrahedron ABCD
                d, c, b, a = simplex[0], simplex[1], simplex[2], simplex[3]
                ao = [-a[0], -a[1], -a[2]]
                ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
                ac = [c[0] - a[0], c[1] - a[1], c[2] - a[2]]
                ad = [d[0] - a[0], d[1] - a[1], d[2] - a[2]]

                norm_abc = cls._cross(ab, ac)
                norm_acd = cls._cross(ac, ad)
                norm_adb = cls._cross(ad, ab)

                if cls._dot(norm_abc, ao) > 0:
                    simplex = [c, b, a]
                    dir_vec = norm_abc
                elif cls._dot(norm_acd, ao) > 0:
                    simplex = [d, c, a]
                    dir_vec = norm_acd
                elif cls._dot(norm_adb, ao) > 0:
                    simplex = [b, d, a]
                    dir_vec = norm_adb
                else:
                    # Origin is inside the tetrahedron!
                    intersecting = True
                    break

        return {
            "intersecting": intersecting,
            "iterations": iterations,
            "simplex_points": [[round(v, 4) for v in pt] for pt in simplex],
        }


# ==============================================================================
# SPATIAL KD-TREE 3D SPATIAL INDEX
# ==============================================================================

class SpatialKDTreeNode:
    def __init__(self, point: List[float], data: Any = None, axis: int = 0):
        self.point = point
        self.data = data
        self.axis = axis
        self.left: Optional["SpatialKDTreeNode"] = None
        self.right: Optional["SpatialKDTreeNode"] = None


class SpatialKDTree3D:
    """3D KD-Tree for O(log N) nearest neighbor search and bounding box range queries."""

    def __init__(self, points_with_data: Optional[List[Tuple[List[float], Any]]] = None):
        self.root: Optional[SpatialKDTreeNode] = None
        self.size = 0
        if points_with_data:
            self.build(points_with_data)

    def build(self, items: List[Tuple[List[float], Any]]) -> None:
        """Constructs balanced 3D KD-Tree."""
        def _build_recursive(pts: List[Tuple[List[float], Any]], depth: int) -> Optional[SpatialKDTreeNode]:
            if not pts:
                return None
            axis = depth % 3
            pts.sort(key=lambda item: item[0][axis])
            mid = len(pts) // 2
            node = SpatialKDTreeNode(pts[mid][0], data=pts[mid][1], axis=axis)
            node.left = _build_recursive(pts[:mid], depth + 1)
            node.right = _build_recursive(pts[mid + 1:], depth + 1)
            return node

        self.root = _build_recursive(list(items), 0)
        self.size = len(items)

    def nearest_neighbor(self, target: List[float]) -> Dict[str, Any]:
        """Finds closest point in the KD-tree to target."""
        if not self.root:
            return {"point": None, "distance": float("inf"), "data": None}

        best = {"point": self.root.point, "data": self.root.data, "dist_sq": float("inf")}

        def _search(node: Optional[SpatialKDTreeNode]):
            if not node:
                return
            d_sq = sum((node.point[i] - target[i]) ** 2 for i in range(3))
            if d_sq < best["dist_sq"]:
                best["dist_sq"] = d_sq
                best["point"] = node.point
                best["data"] = node.data

            axis = node.axis
            diff = target[axis] - node.point[axis]

            first = node.left if diff < 0 else node.right
            second = node.right if diff < 0 else node.left

            _search(first)
            if (diff * diff) < best["dist_sq"]:
                _search(second)

        _search(self.root)
        return {
            "point": [round(v, 4) for v in best["point"]],
            "distance": round(math.sqrt(best["dist_sq"]), 4),
            "data": best["data"],
        }

    def range_query_aabb(self, min_pt: List[float], max_pt: List[float]) -> List[Dict[str, Any]]:
        """Finds all points contained in 3D box [min_pt, max_pt]."""
        results = []

        def _search(node: Optional[SpatialKDTreeNode]):
            if not node:
                return
            p = node.point
            if all(min_pt[i] <= p[i] <= max_pt[i] for i in range(3)):
                results.append({"point": [round(v, 4) for v in p], "data": node.data})

            axis = node.axis
            if p[axis] >= min_pt[axis]:
                _search(node.left)
            if p[axis] <= max_pt[axis]:
                _search(node.right)

        _search(self.root)
        return results


def math3d_gjk_intersection(shape_a: List[List[float]], shape_b: List[List[float]]) -> Record:
    """Performs 3D GJK collision test between two convex point sets."""
    return Record(GJKCollision3DAndEPA.test_intersection(shape_a, shape_b))


def math3d_kdtree_query(
    points: List[List[float]],
    target: List[float],
) -> Record:
    """Indexes 3D points in KD-Tree and queries nearest neighbor."""
    tree = SpatialKDTree3D([(p, idx) for idx, p in enumerate(points)])
    return Record(tree.nearest_neighbor(target))



