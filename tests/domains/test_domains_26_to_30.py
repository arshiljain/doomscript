"""Comprehensive test suite for Phase 1 new domains:
- math3d (Domain 26)
- compiler (Domain 27)
- robotics (Domain 28)
- signals (Domain 29)
- astronomy (Domain 30)
-"""

import pytest
import math
from doomscript.compiler.engine import execute


def test_math3d_domain():
    code = """
use math3d
v1 = Vec3(1.0, 2.0, 3.0)
v2 = Vec3(4.0, 5.0, 6.0)
dot_val = v1.dot(v2)
cross_vec = v1.cross(v2)
v_norm = v1.normalize()

ray = Ray(Vec3(0.0, 0.0, -5.0), Vec3(0.0, 0.0, 1.0))
hit_sph = math3d_ray_sphere_intersect(ray, Vec3(0.0, 0.0, 0.0), 1.0)

v0 = Vec3(-1.0, -1.0, 0.0)
v1_tri = Vec3(1.0, -1.0, 0.0)
v2_tri = Vec3(0.0, 1.0, 0.0)
hit_tri = math3d_ray_triangle_intersect(ray, v0, v1_tri, v2_tri)

q1 = Quat.from_axis_angle(Vec3(0.0, 1.0, 0.0), 0.0)
q2 = Quat.from_axis_angle(Vec3(0.0, 1.0, 0.0), 3.14159)
q_mid = Quat.slerp(q1, q2, 0.5)

sdf_dist = math3d_sdf_sphere(Vec3(2.0, 0.0, 0.0), 1.0)
m_look = Mat4.look_at(Vec3(0.0, 0.0, 5.0), Vec3(0.0, 0.0, 0.0), Vec3(0.0, 1.0, 0.0))
"""
    env = execute(code)
    assert env["dot_val"] == 32.0
    assert abs(env["cross_vec"].x - (-3.0)) < 1e-5
    assert abs(env["cross_vec"].y - 6.0) < 1e-5
    assert abs(env["cross_vec"].z - (-3.0)) < 1e-5
    assert abs(env["v_norm"].length() - 1.0) < 1e-5
    assert env["hit_sph"]["hit"] is True
    assert abs(env["hit_sph"]["t"] - 4.0) < 1e-5
    assert env["hit_tri"]["hit"] is True
    assert abs(env["hit_tri"]["t"] - 5.0) < 1e-5
    assert abs(env["sdf_dist"] - 1.0) < 1e-5
    assert env["q_mid"].norm() > 0.99


def test_compiler_domain():
    code = """
use compiler
asm_src = \"\"\"
LOAD_CONST 10
STORE_FAST x
LOAD_CONST 20
STORE_FAST y
LOAD_FAST x
LOAD_FAST y
ADD
STORE_FAST z
HALT
\"\"\"
prog = compiler_assemble_string(asm_src)
vm_res = compiler_run_bytecode(prog["instructions"], prog["constants"])
ast_tree = compiler_parse_pratt("1 + 2 * 3 ^ 4")
"""
    env = execute(code)
    assert env["vm_res"]["halted"] is True
    assert env["vm_res"]["locals"]["z"] == 30
    assert env["ast_tree"] == ["+", 1, ["*", 2, ["^", 3, 4]]]


def test_robotics_domain():
    code = """
use robotics
dh = [
    [0.0, 0.5, 0.0, 1.5708],
    [0.0, 0.0, 0.5, 0.0]
]
fk = robotics_forward_kinematics(dh)
ik = robotics_inverse_kinematics_2link(1.0, 1.0, 1.0, 1.0)
q_traj = robotics_cubic_trajectory(0.0, 90.0, 0.0, 0.0, 0.0, 2.0, 1.0)

ekf = robotics_create_ekf(0.0, 0.0, 0.05, 0.5)
ekf.predict(0.1)
ekf.update(1.0, 0.5)
state = ekf.get_estimate()
"""
    env = execute(code)
    assert len(env["fk"]["end_effector"]) == 3
    assert env["ik"] is not None
    assert abs(env["ik"]["theta1_deg"] - 0.0) < 1e-4 or abs(env["ik"]["theta2_deg"] - 90.0) < 1e-4
    assert abs(env["q_traj"] - 45.0) < 1e-4
    assert env["state"]["x"] > 0


def test_signals_domain():
    code = """
use signals
sig = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
dwt = signals_haar_dwt(sig)
recon = signals_haar_idwt(dwt["approx"], dwt["detail"])
filtered = signals_fir_lowpass(sig, 5, 100.0, 1000.0)
hilb = signals_hilbert(sig)
peaks = signals_find_peaks([1.0, 3.0, 2.0, 5.0, 1.0])
"""
    env = execute(code)
    for orig, rec in zip(env["sig"], env["recon"]):
        assert abs(orig - rec) < 1e-5
    assert len(env["filtered"]) == len(env["sig"])
    assert len(env["hilb"]["envelope"]) == len(env["sig"])
    assert len(env["peaks"]) == 2
    assert env["peaks"][0]["index"] == 1
    assert env["peaks"][1]["index"] == 3


def test_astronomy_domain():
    code = """
use astronomy
jd = astronomy_julian_date(2026, 10, 20, 12, 0, 0.0)
orbit = astronomy_kepler_orbit(7000000.0, 0.01, 28.5, 45.0, 0.0, 0.0)
horiz = astronomy_eq_to_horiz(12.0, 45.0, 37.0, 12.0)
hoh = astronomy_hohmann_transfer(7000000.0, 42164000.0)
"""
    env = execute(code)
    assert env["jd"] > 2460000.0
    assert len(env["orbit"]["position"]) == 3
    assert len(env["orbit"]["velocity"]) == 3
    assert "altitude_deg" in env["horiz"]
    assert "azimuth_deg" in env["horiz"]
    assert env["hoh"]["total_delta_v"] > 3000.0
    assert env["hoh"]["transfer_time_hours"] > 5.0
