"""Math3D, Linear Algebra, Ray Tracing & SDF Domain Pack for DoomScript.

Enables native spoken-English 3D vector/matrix math, quaternions, camera transforms,
ray-primitive intersections, and signed distance field raymarching via 'use math3d'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.math3d.runtime import (
    Vec3,
    Vec4,
    Mat4,
    Quat,
    Ray,
    math3d_ray_sphere_intersect,
    math3d_ray_triangle_intersect,
    math3d_sdf_sphere,
    math3d_sdf_box,
    math3d_sdf_torus,
    math3d_sdf_smooth_union,
    math3d_sdf_normal,
    math3d_raymarch,
    Raymarcher3D,
    DualQuaternion,
    Quickhull3D,
    OrientedBoundingBoxOBB,
    FrustumCuller3D,
    BvhSpatialTree,
    math3d_raymarcher_render,
    math3d_dual_quaternion,
    math3d_quickhull,
    math3d_obb_create,
    math3d_obb_test_collision,
    math3d_frustum_create,
    math3d_frustum_cull_sphere,
    math3d_frustum_cull_scene,
    math3d_bvh_build,
    math3d_bvh_raycast,
)
from doomscript.domains.math3d.parser import Math3DDomainParser
from doomscript.domains.math3d.exporter import Math3DASTExporter


class Math3DRuntime(DomainRuntime):
    """Runtime coordinator for math3d routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


def math3d_create_vec3(x: float, y: float, z: float) -> Vec3:
    return Vec3(x, y, z)


def math3d_cross_product(v1: Vec3, v2: Vec3) -> Vec3:
    return v1.cross(v2)


def math3d_dot_product(v1: Vec3, v2: Vec3) -> float:
    return v1.dot(v2)


def math3d_normalize_vec(v: Vec3) -> Vec3:
    return v.normalize()


def math3d_look_at(eye: Vec3, target: Vec3, up: Vec3) -> Mat4:
    return Mat4.look_at(eye, target, up)


def math3d_perspective(fov: float, aspect: float, near: float, far: float) -> Mat4:
    return Mat4.perspective(fov, aspect, near, far)


def math3d_slerp(q1: Quat, q2: Quat, t: float) -> Quat:
    return Quat.slerp(q1, q2, t)


class Math3DDomain(DomainContract):
    """Domain contract for 3D Mathematics and Ray Tracing."""

    name = "math3d"
    aliases = ["3d", "vector3d", "linear_algebra"]
    description = "3D linear algebra, matrices, quaternions, ray tracing, and SDF raymarching"
    parser = Math3DDomainParser()
    runtime = Math3DRuntime()
    exporter = Math3DASTExporter()
    capabilities = ["vec3", "mat4", "quaternion", "raytracing", "sdf"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="create vector3 with x {x:expr} and y {y:expr} and z {z:expr} into {target:ident}",
            description="Creates a 3D vector",
        ),
        VerbSpec(
            pattern="calculate cross product of {v1:expr} and {v2:expr} into {target:ident}",
            description="Calculates 3D cross product",
        ),
        VerbSpec(
            pattern="calculate dot product of {v1:expr} and {v2:expr} into {target:ident}",
            description="Calculates 3D dot product",
        ),
        VerbSpec(
            pattern="normalize vector {v:expr} into {target:ident}",
            description="Normalizes vector to unit length",
        ),
        VerbSpec(
            pattern="create look at matrix from {eye:expr} to {target_pt:expr} with up {up:expr} into {target:ident}",
            description="Creates camera view matrix",
        ),
        VerbSpec(
            pattern="create perspective matrix with fov {fov:expr} and aspect {asp:expr} and near {znear:expr} and far {zfar:expr} into {target:ident}",
            description="Creates perspective projection matrix",
        ),
        VerbSpec(
            pattern="slerp quaternion {q1:expr} and {q2:expr} with t {t:expr} into {target:ident}",
            description="Spherical linear interpolation between quaternions",
        ),
        VerbSpec(
            pattern="intersect ray {ray:expr} with sphere at {center:expr} and radius {r:expr} into {target:ident}",
            description="Calculates ray-sphere intersection",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("create vector3 ")
            or s.startswith("calculate cross product of ")
            or s.startswith("calculate dot product of ")
            or s.startswith("normalize vector ")
            or s.startswith("create look at matrix ")
            or s.startswith("create perspective matrix ")
            or s.startswith("slerp quaternion ")
            or s.startswith("intersect ray ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


MATH3D_DOMAIN = Math3DDomain()
get_domain_registry().register(MATH3D_DOMAIN)

__all__ = [
    "Math3DDomain",
    "MATH3D_DOMAIN",
    "Math3DRuntime",
    "Vec3",
    "Vec4",
    "Mat4",
    "Quat",
    "Ray",
    "math3d_create_vec3",
    "math3d_cross_product",
    "math3d_dot_product",
    "math3d_normalize_vec",
    "math3d_look_at",
    "math3d_perspective",
    "math3d_slerp",
    "math3d_ray_sphere_intersect",
    "math3d_ray_triangle_intersect",
    "math3d_sdf_sphere",
    "math3d_sdf_box",
    "math3d_sdf_torus",
    "math3d_sdf_smooth_union",
    "math3d_sdf_normal",
    "math3d_raymarch",
    "Raymarcher3D",
    "DualQuaternion",
    "Quickhull3D",
    "OrientedBoundingBoxOBB",
    "FrustumCuller3D",
    "BvhSpatialTree",
    "math3d_raymarcher_render",
    "math3d_dual_quaternion",
    "math3d_quickhull",
    "math3d_obb_create",
    "math3d_obb_test_collision",
    "math3d_frustum_create",
    "math3d_frustum_cull_sphere",
    "math3d_frustum_cull_scene",
    "math3d_bvh_build",
    "math3d_bvh_raycast",
]
