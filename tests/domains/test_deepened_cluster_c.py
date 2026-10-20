"""Comprehensive test suite for Cluster C: Mathematics, 3D & Scientific Computing.

Covers deepened features across:
- math3d: Raymarcher3D, DualQuaternion (SE3 ScLERP), Quickhull3D
- symbolic: SymbolicIntegrator, TaylorSeries, ExactRationalLinearSolver
- signals: WaveletTransform (Haar/DB4), STFTSpectrogram, SavitzkyGolayFilter
- research: SVDDecomposition, RungeKuttaFehlberg (RKF45), LevenbergMarquardt
- graphics: BlinnPhongShader, BilinearTextureMapper, SuperSampledFrameBuffer
"""

import math
from fractions import Fraction
import pytest
from doomscript.domains.math3d.runtime import (
    Vec3,
    Ray,
    Raymarcher3D,
    DualQuaternion,
    Quickhull3D,
    math3d_raymarcher_render,
    math3d_dual_quaternion,
    math3d_quickhull,
)
from doomscript.domains.symbolic.runtime import (
    SymbolicIntegrator,
    TaylorSeries,
    ExactRationalLinearSolver,
    symbolic_integrate,
    symbolic_taylor_series,
    symbolic_solve_rational_linear,
    symbolic_parse,
)
from doomscript.domains.signals.runtime import (
    WaveletTransform,
    STFTSpectrogram,
    SavitzkyGolayFilter,
    signals_stft,
    signals_savitzky_golay,
)
from doomscript.domains.research.runtime import (
    SVDDecomposition,
    RungeKuttaFehlberg,
    LevenbergMarquardt,
    research_svd,
    research_rkf45_solve,
    research_levenberg_marquardt,
)
from doomscript.domains.graphics.runtime import (
    BlinnPhongShader,
    BilinearTextureMapper,
    SuperSampledFrameBuffer,
    graphics_blinn_phong,
    graphics_sample_bilinear,
    graphics_supersampled_framebuffer,
)


# ============================================================================
# 1. Math3D Deepened Tests
# ============================================================================

def test_raymarcher_3d_scene():
    rm = Raymarcher3D(camera_pos=Vec3(0.0, 0.0, -4.0), look_at=Vec3(0.0, 0.0, 0.0))
    rm.add_sphere(Vec3(0.0, 0.0, 0.0), 1.0)
    rm.add_box(Vec3(2.0, 0.0, 0.0), Vec3(0.5, 0.5, 0.5))

    # Test point inside sphere
    dist, color = rm.scene_sdf(Vec3(0.0, 0.0, 0.0))
    assert dist == -1.0
    assert color == (1.0, 0.2, 0.2)

    # Estimate normal on sphere surface at (0, 0, -1)
    norm = rm.estimate_normal(Vec3(0.0, 0.0, -1.0))
    assert abs(norm.z - (-1.0)) < 0.01

    # Render buffer test
    grid = rm.render_buffer(width=20, height=10, max_steps=32)
    assert len(grid) == 10
    assert len(grid[0]) == 20
    # Center pixel should have a hit (non-space)
    assert any(ch != " " for row in grid for ch in row)


def test_dual_quaternion_se3_and_sclerp():
    # Identity rotation [1, 0, 0, 0] and translation [1, 2, 3]
    dq = DualQuaternion.from_rotation_translation([1.0, 0.0, 0.0, 0.0], [1.0, 2.0, 3.0])
    trans = dq.to_translation()
    assert trans == [1.0, 2.0, 3.0]

    # Transform a point [0, 0, 0] -> should be [1, 2, 3]
    pt_transformed = dq.transform_point([0.0, 0.0, 0.0])
    assert pt_transformed == [1.0, 2.0, 3.0]

    # ScLERP interpolation at t = 0.5
    dq_target = DualQuaternion.from_rotation_translation([1.0, 0.0, 0.0, 0.0], [3.0, 6.0, 9.0])
    dq_mid = DualQuaternion.sclerp(dq, dq_target, 0.5)
    trans_mid = dq_mid.to_translation()
    assert abs(trans_mid[0] - 2.0) < 1e-3
    assert abs(trans_mid[1] - 4.0) < 1e-3
    assert abs(trans_mid[2] - 6.0) < 1e-3


def test_quickhull_3d_cube():
    # 8 vertices of a unit cube
    cube_pts = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
        [1.0, 0.0, 1.0],
        [1.0, 1.0, 1.0],
        [0.0, 1.0, 1.0],
    ]
    # Add an interior point that should be discarded
    pts_with_interior = cube_pts + [[0.5, 0.5, 0.5]]

    qh = Quickhull3D()
    hull = qh.compute_hull(pts_with_interior)

    assert "faces" in hull
    assert hull["num_faces"] >= 6
    # All 8 corners must be in the hull
    assert len(hull["vertex_indices"]) == 8
    # Interior point index (8) should NOT be in vertex_indices
    assert 8 not in hull["vertex_indices"]


# ============================================================================
# 2. Symbolic Deepened Tests
# ============================================================================

def test_symbolic_integrator():
    # P(x) = 3 x^2 + 2 x + 1
    # Standard coeffs [3, 2, 1]
    # Integral = x^3 + x^2 + x -> coeffs [1.0, 1.0, 1.0, 0.0]
    integ = SymbolicIntegrator.integrate_polynomial([3.0, 2.0, 1.0])
    assert integ == [1.0, 1.0, 1.0, 0.0]

    # Definite integral from 0 to 2: (8 + 4 + 2) - 0 = 14.0
    def_val = SymbolicIntegrator.definite_integral_poly([3.0, 2.0, 1.0], 0.0, 2.0)
    assert def_val == 14.0

    # Term integration
    assert SymbolicIntegrator.integrate_term("x") == "(0.5 * x^2)"
    assert SymbolicIntegrator.integrate_term("sin(x)") == "-cos(x)"


def test_taylor_series():
    # Taylor expansion of e^x around x0 = 0: 1 + x + x^2/2 + x^3/6 + x^4/24
    ts = TaylorSeries("exp(x)", var="x", x0=0.0)
    res = ts.expand(order=4)

    assert res["order"] == 4
    coeffs = res["coefficients"]
    # [1.0, 1.0, 0.5, 1/6, 1/24]
    assert abs(coeffs[0] - 1.0) < 1e-4
    assert abs(coeffs[1] - 1.0) < 1e-4
    assert abs(coeffs[2] - 0.5) < 1e-4
    assert abs(coeffs[3] - 1.0 / 6.0) < 1e-4
    assert abs(coeffs[4] - 1.0 / 24.0) < 1e-4


def test_exact_rational_linear_solver():
    # 2x2 system:
    # 2x + y = 5
    # x - 3y = -1
    # Solution: x = 2, y = 1
    A = [[2, 1], [1, -3]]
    b = [5, -1]

    res = ExactRationalLinearSolver.solve(A, b)
    assert res["success"]
    assert res["solution"] == ["2", "1"]
    assert res["solution_floats"] == [2.0, 1.0]

    # Exact determinant: 2*(-3) - 1*1 = -7
    det = ExactRationalLinearSolver.determinant(A)
    assert det == Fraction(-7, 1)


# ============================================================================
# 3. Signals Deepened Tests
# ============================================================================

def test_wavelet_haar_reconstruction():
    sig = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    dwt = WaveletTransform.haar_dwt(sig)
    assert len(dwt["approx"]) == 4
    assert len(dwt["detail"]) == 4

    rec = WaveletTransform.haar_idwt(dwt["approx"], dwt["detail"])
    assert len(rec) == len(sig)
    for orig, r in zip(sig, rec):
        assert abs(orig - r) < 1e-5


def test_stft_spectrogram():
    # 128 samples of pure tone
    sample_rate = 128
    sig = [math.sin(2.0 * math.pi * 10.0 * i / sample_rate) for i in range(128)]

    spec = STFTSpectrogram.compute(sig, frame_size=32, hop_size=16, window="hann")
    assert spec["num_frames"] > 0
    assert spec["num_bins"] == 17  # 32 / 2 + 1
    assert len(spec["spectrogram"]) == spec["num_frames"]


def test_savitzky_golay_filter():
    # Smooth quadratic signal with noise
    clean = [float(i ** 2) for i in range(15)]
    noisy = [c + (0.1 if i % 2 == 0 else -0.1) for i, c in enumerate(clean)]

    smoothed = SavitzkyGolayFilter.filter(noisy, window_length=5, poly_order=2, deriv=0)
    assert len(smoothed) == len(clean)
    # Check that error with respect to clean signal is reduced
    noisy_err = sum(abs(n - c) for n, c in zip(noisy, clean))
    smooth_err = sum(abs(s - c) for s, c in zip(smoothed, clean))
    assert smooth_err <= noisy_err


# ============================================================================
# 4. Research Deepened Tests
# ============================================================================

def test_svd_decomposition():
    # 3x2 matrix
    A = [
        [3.0, 2.0],
        [2.0, 3.0],
        [2.0, -2.0],
    ]
    svd = SVDDecomposition()
    res = svd.decompose(A)

    sigmas = res["singular_values"]
    assert len(sigmas) == 2
    assert sigmas[0] >= sigmas[1]
    assert sigmas[0] > 0
    assert res["rank"] == 2


def test_rkf45_ode_solver():
    # dy/dt = -y, y(0) = 1.0. Exact solution: y(t) = exp(-t)
    def ode(t: float, y: list) -> list:
        return [-y[0]]

    rkf = RungeKuttaFehlberg(tol=1e-5)
    res = rkf.solve(ode, y0=[1.0], t_span=(0.0, 1.0))

    final_y = res["final_y"][0]
    expected = math.exp(-1.0)  # ~0.367879
    assert abs(final_y - expected) < 1e-4
    assert res["num_steps"] > 1


def test_levenberg_marquardt_curve_fit():
    # Model: y = a * x + b
    def model(x: float, p: list) -> float:
        return p[0] * x + p[1]

    x_pts = [1.0, 2.0, 3.0, 4.0, 5.0]
    # a = 2.0, b = 3.0
    y_pts = [5.0, 7.0, 9.0, 11.0, 13.0]

    lm = LevenbergMarquardt(max_iter=50)
    res = lm.fit(model, x_pts, y_pts, p0=[1.0, 1.0])

    a_fit, b_fit = res["optimal_params"]
    assert abs(a_fit - 2.0) < 1e-3
    assert abs(b_fit - 3.0) < 1e-3
    assert res["final_cost"] < 1e-5


# ============================================================================
# 5. Graphics Deepened Tests
# ============================================================================

def test_blinn_phong_shader():
    shader = BlinnPhongShader(
        light_pos=(0.0, 10.0, -5.0),
        camera_pos=(0.0, 0.0, -5.0),
    )
    # Fragment facing upward toward light
    color = shader.shade_fragment(
        frag_pos=(0.0, 0.0, 0.0),
        frag_normal=(0.0, 1.0, 0.0),
        diffuse_color=(0.8, 0.2, 0.2),
    )
    assert len(color) == 3
    assert all(0 <= c <= 255 for c in color)
    # Red component should be prominent
    assert color[0] > color[1] and color[0] > color[2]


def test_bilinear_texture_mapper():
    # 2x2 texture:
    # (0,0)=Black, (1,0)=White, (0,1)=White, (1,1)=Black
    pixels = [
        (0, 0, 0), (255, 255, 255),
        (255, 255, 255), (0, 0, 0),
    ]
    tex = BilinearTextureMapper(width=2, height=2, pixels=pixels)

    # Sample exactly at center (0.5, 0.5) -> should be average ~128
    mid_color = tex.sample(0.5, 0.5)
    assert abs(mid_color[0] - 128) <= 2
    assert abs(mid_color[1] - 128) <= 2
    assert abs(mid_color[2] - 128) <= 2

    # Corner samples
    c00 = tex.sample(0.0, 0.0)
    assert c00 == (0, 0, 0)
    c10 = tex.sample(1.0, 0.0)
    assert c10 == (255, 255, 255)


def test_supersampled_framebuffer():
    # Target 4x4, SSAA scale = 2 -> render 8x8
    ssaa = SuperSampledFrameBuffer(target_width=4, target_height=4, scale=2)
    # Set subpixels
    for y in range(8):
        for x in range(8):
            ssaa.set_subpixel(x, y, (100, 150, 200))

    downscaled = ssaa.downsample()
    assert downscaled.width == 4
    assert downscaled.height == 4

    p = downscaled.get_pixel(0, 0)
    assert p[0] == 100
    assert p[1] == 150
    assert p[2] == 200
