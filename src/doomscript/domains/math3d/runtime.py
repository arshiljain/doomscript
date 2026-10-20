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

