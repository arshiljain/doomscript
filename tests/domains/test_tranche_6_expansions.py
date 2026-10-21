"""Unit tests for Tranche 6 Domain Expansions (physics, math3d, robotics)."""

import math
import pytest
from doomscript.domains.physics.runtime import (
    WaveEquation1D,
    ContinuousCollisionDetectionCCD,
    CoupledOscillatorsNormalModes,
    physics_wave_equation_1d,
    physics_ccd_time_of_impact,
    physics_normal_modes,
)
from doomscript.domains.math3d.runtime import (
    BarycentricCoordinates3D,
    SphericalHarmonics3D,
    math3d_barycentric_triangle,
    math3d_spherical_harmonic_eval,
)
from doomscript.domains.robotics.runtime import (
    UnscentedKalmanFilterUKF,
    AStarGrid3D,
    robotics_ukf_step,
    robotics_astar_3d_path,
)


def test_physics_wave_equation_and_ccd():
    """Verify FDTD 1D wave equation and continuous collision time-of-impact."""
    wave_res = physics_wave_equation_1d(length=10.0, c=1.0, dt=0.05, timesteps=30)
    assert wave_res.cfl < 1.0
    assert wave_res.peak_amplitude > 0.0

    # Moving sphere 1 at (0, 0, 0) velocity (+10, 0, 0), radius 1
    # Static sphere 2 at (5, 0, 0) velocity (0, 0, 0), radius 1
    # Touching distance is r1 + r2 = 2.0 -> centers are 2.0 apart when p1_x = 3.0 -> t = 3.0 / 10.0 = 0.3s
    ccd_res = physics_ccd_time_of_impact(
        p1=[0.0, 0.0, 0.0], v1=[10.0, 0.0, 0.0], r1=1.0,
        p2=[5.0, 0.0, 0.0], v2=[0.0, 0.0, 0.0], r2=1.0,
    )
    assert ccd_res.collided is True
    assert ccd_res.toi == pytest.approx(0.3, abs=0.01)


def test_physics_normal_modes():
    """Verify coupled oscillator normal mode frequencies."""
    masses = [1.0, 1.0, 1.0]
    k_springs = [10.0, 10.0, 10.0, 10.0]
    modes_res = physics_normal_modes(masses, k_springs)
    assert modes_res.num_oscillators == 3
    assert len(modes_res.normal_mode_frequencies) == 3
    assert modes_res.normal_mode_frequencies[0] > 0.0


def test_math3d_barycentric_and_spherical_harmonics():
    """Verify barycentric coordinate centroid and spherical harmonics basis values."""
    # Equilateral triangle in XY plane
    a = [0.0, 0.0, 0.0]
    b = [1.0, 0.0, 0.0]
    c = [0.0, 1.0, 0.0]
    # Triangle centroid: (1/3, 1/3, 0)
    centroid = [1.0 / 3.0, 1.0 / 3.0, 0.0]
    bary = math3d_barycentric_triangle(centroid, a, b, c)

    assert bary.inside_triangle is True
    assert bary.u == pytest.approx(1.0 / 3.0, abs=1e-3)
    assert bary.v == pytest.approx(1.0 / 3.0, abs=1e-3)
    assert bary.w == pytest.approx(1.0 / 3.0, abs=1e-3)

    # Spherical harmonics on z-axis (0, 0, 1)
    sh_basis = math3d_spherical_harmonic_eval([0.0, 0.0, 1.0])
    assert len(sh_basis) == 9
    assert sh_basis[0] == pytest.approx(0.5 * math.sqrt(1.0 / math.pi))


def test_robotics_ukf_and_3d_astar():
    """Verify UKF filter convergence and 3D voxel A* path search."""
    init_state = [0.0, 0.0]
    # Constant measurement of 5.0
    meas = [[5.0, 5.0]] * 10
    ukf_res = robotics_ukf_step(init_state, meas)
    assert ukf_res.final_state[0] > 3.0
    assert ukf_res.final_state[1] > 3.0

    # 3D A* around an obstacle wall at x=5
    start = (0, 5, 5)
    goal = (10, 5, 5)
    # Wall from y=2 to 8 at x=5, with a hole at z=9
    obstacles = [(5, y, 5) for y in range(2, 9)]
    path_res = robotics_astar_3d_path(start, goal, obstacles)

    assert path_res.reachable is True
    assert path_res.path_length > 10
    # Must avoid the obstacles
    for wp in path_res.path_waypoints:
        assert wp not in obstacles
