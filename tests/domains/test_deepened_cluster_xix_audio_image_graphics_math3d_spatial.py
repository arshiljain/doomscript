"""Comprehensive unit tests for Deepened Cluster XIX:
Audio, Image, Graphics, Math3D, and Spatial Audio domains in DoomScript.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Domain runtime classes & algorithms
from doomscript.domains.audio.runtime import (
    LPCVocoderLinearPredictiveCoding,
    BiquadIIRFilterCascaded,
)
from doomscript.domains.image.runtime import (
    CannyEdgeDetectorPure,
    OtsuAdaptiveThresholding,
)
from doomscript.domains.graphics.runtime import (
    BresenhamWuAntiAliasedLine,
    PolygonScanlineActiveEdgeTableRasterizer,
    RayMarchingSignedDistanceFieldSDF,
)
from doomscript.domains.math3d.runtime import (
    GJKCollision3DAndEPA,
    SpatialKDTree3D,
)
from doomscript.domains.spatial_audio.runtime import (
    HigherOrderSphericalHarmonics3D,
    AcousticRayTracingShoebox,
)


# ==============================================================================
# AUDIO DOMAIN TESTS
# ==============================================================================

def test_audio_lpc_vocoder():
    # Synthetic speech-like harmonic signal
    fs = 8000
    signal = [math.sin(2.0 * math.pi * 300.0 * n / fs) + 0.5 * math.sin(2.0 * math.pi * 700.0 * n / fs) for n in range(128)]
    res = LPCVocoderLinearPredictiveCoding.analyze_and_synthesize(signal, order=8)
    assert res["lpc_order"] == 8
    assert len(res["coefficients"]) == 8
    assert len(res["reflection_coefficients"]) == 8
    assert res["prediction_gain_db"] > 5.0
    assert len(res["reconstructed_samples"]) == 128
    # Reconstructed signal should correlate closely with original
    err = sum(abs(a - b) for a, b in zip(signal, res["reconstructed_samples"])) / 128
    assert err < 0.2


def test_audio_biquad_eq_filter():
    signal = [1.0 if n == 0 else 0.0 for n in range(64)]  # Unit impulse
    res = BiquadIIRFilterCascaded.filter_signal(signal, filter_type="lowpass", cutoff_hz=1000.0, sample_rate=44100)
    assert res["filter_type"] == "lowpass"
    assert len(res["output_samples"]) == 64
    assert res["magnitude_at_cutoff_db"] < 0.0  # Lowpass attenuates at cutoff (~ -3dB)


def test_audio_spoken_english():
    code = """use audio
analyze lpc speech samples [0.1, 0.4, 0.8, 0.5, -0.2, -0.7, -0.4, 0.2, 0.6, 0.9, 0.3, -0.3] order 4 into lpc_res
apply biquad filter lowpass to [0.1, 0.5, 0.9, 0.3, -0.4, -0.8] cutoff 1500 into bq_res
"""
    env = execute(code)
    assert env["lpc_res"].lpc_order == 4
    assert len(env["bq_res"].output_samples) == 6


# ==============================================================================
# IMAGE DOMAIN TESTS
# ==============================================================================

def test_image_canny_edge_detector():
    # 10x10 synthetic image with vertical edge down middle
    img = [[200.0 if c >= 5 else 20.0 for c in range(10)] for r in range(10)]
    res = CannyEdgeDetectorPure.detect(img, low_threshold=30.0, high_threshold=80.0)
    assert res["rows"] == 10
    assert res["cols"] == 10
    assert res["edges_count"] > 0
    # Center vertical column should contain detected edge pixels
    edge_cols = [c for r in range(10) for c in range(10) if res["edge_matrix"][r][c] == 1]
    assert any(c in (4, 5) for c in edge_cols)


def test_image_otsu_thresholding():
    # Bimodal image: background around 30, foreground around 200
    img = [
        [25, 30, 35, 190, 200, 210],
        [28, 32, 26, 195, 205, 215],
        [31, 29, 34, 185, 202, 208],
    ]
    res = OtsuAdaptiveThresholding.binarize(img)
    assert 50 < res["optimal_threshold"] < 180
    assert res["foreground_count"] == 9
    assert res["background_count"] == 9


def test_image_spoken_english():
    code = """use image
detect canny edges in image [[0,0,0,100,100,0,0,0], [0,0,0,100,100,0,0,0], [0,0,0,100,100,0,0,0], [0,0,0,100,100,0,0,0], [0,0,0,100,100,0,0,0]] low 20.0 high 60.0 into canny_res
binarize image with otsu [[10, 15, 20, 200, 210, 220], [12, 18, 22, 205, 215, 225]] into otsu_res
"""
    env = execute(code)
    assert env["canny_res"].rows == 5
    assert env["otsu_res"].foreground_count == 6


# ==============================================================================
# GRAPHICS DOMAIN TESTS
# ==============================================================================

def test_graphics_wu_antialiased_line():
    pixels = BresenhamWuAntiAliasedLine.rasterize(1.0, 1.0, 10.0, 5.0, color=(255, 128, 0))
    assert len(pixels) > 5
    # Pixel coordinates should be within bounding box
    for px, py, rgba in pixels:
        assert 1 <= px <= 10
        assert 0 <= py <= 6
        assert 0 <= rgba[3] <= 255


def test_graphics_polygon_scanline_fill():
    # Triangle (10, 10), (30, 10), (20, 30)
    verts = [(10.0, 10.0), (30.0, 10.0), (20.0, 30.0)]
    res = PolygonScanlineActiveEdgeTableRasterizer.rasterize_polygon(verts, color=(0, 255, 0))
    assert res["total_pixels"] > 50
    assert res["y_bounds"][0] == 10
    assert res["y_bounds"][1] == 30


def test_graphics_ray_marching_sdf():
    # Ray towards sphere at (0, 0, 3)
    res = RayMarchingSignedDistanceFieldSDF.ray_march(
        ray_origin=(0.0, 0.0, 0.0),
        ray_direction=(0.0, 0.0, 1.0),
        max_steps=32,
    )
    assert res["hit"] is True
    assert abs(res["distance"] - 2.0) < 0.2  # Center at z=3, radius 1 -> hit at z=2


def test_graphics_spoken_english():
    code = """use graphics
rasterize antialiased line from 1.0, 1.0 to 10.0, 5.0 with color (255, 0, 0) into wu_res
scanline fill polygon [[5, 5], [20, 5], [15, 18]] with color (0, 255, 0) into poly_res
ray march sdf origin (0.0, 0.0, 0.0) direction (0.0, 0.0, 1.0) steps 32 into rm_res
"""
    env = execute(code)
    assert env["wu_res"].pixel_count > 5
    assert env["poly_res"].total_pixels > 20
    assert env["rm_res"].hit is True


# ==============================================================================
# MATH3D DOMAIN TESTS
# ==============================================================================

def test_math3d_gjk_collision():
    # Box A: [-1, 1]^3
    box_a = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
    ]
    # Box B overlapping with Box A: [0.5, 2.5]^3
    box_b = [
        [0.5, 0.5, 0.5], [2.5, 0.5, 0.5], [2.5, 2.5, 0.5], [0.5, 2.5, 0.5],
        [0.5, 0.5, 2.5], [2.5, 0.5, 2.5], [2.5, 2.5, 2.5], [0.5, 2.5, 2.5],
    ]
    # Box C separated: [5, 7]^3
    box_c = [
        [5, 5, 5], [7, 5, 5], [7, 7, 5], [5, 7, 5],
        [5, 5, 7], [7, 5, 7], [7, 7, 7], [5, 7, 7],
    ]

    res_overlap = GJKCollision3DAndEPA.test_intersection(box_a, box_b)
    assert res_overlap["intersecting"] is True

    res_disjoint = GJKCollision3DAndEPA.test_intersection(box_a, box_c)
    assert res_disjoint["intersecting"] is False


def test_math3d_kdtree_search():
    points = [
        ([0.0, 0.0, 0.0], "origin"),
        ([1.0, 2.0, 3.0], "target_pt"),
        ([5.0, 5.0, 5.0], "far_pt"),
        ([-2.0, -1.0, 4.0], "other_pt"),
    ]
    tree = SpatialKDTree3D(points)
    res = tree.nearest_neighbor([1.1, 2.05, 2.95])
    assert res["data"] == "target_pt"
    assert res["distance"] < 0.2


def test_math3d_spoken_english():
    code = """use math3d
test gjk collision between [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]] and [[0.5, 0.5, 0.5], [2.5, 0.5, 0.5], [2.5, 2.5, 0.5], [0.5, 2.5, 0.5], [0.5, 0.5, 2.5], [2.5, 0.5, 2.5], [2.5, 2.5, 2.5], [0.5, 2.5, 2.5]] into gjk_res
query kdtree points [[0.0, 0.0, 0.0], [5.0, 5.0, 5.0], [1.0, 2.0, 3.0]] for target [1.1, 2.1, 2.9] into kd_res
"""
    env = execute(code)
    assert env["gjk_res"].intersecting is True
    assert env["kd_res"].distance < 0.3


# ==============================================================================
# SPATIAL AUDIO DOMAIN TESTS
# ==============================================================================

def test_spatial_audio_higher_order_spherical_harmonics():
    res = HigherOrderSphericalHarmonics3D.encode_direction(azimuth_deg=45.0, elevation_deg=30.0, order=2)
    assert res["order"] == 2
    assert res["channels_count"] == 9  # (2 + 1)^2 = 9 channels
    assert len(res["channels"]) == 9
    # Channel 0 (omni W) should be positive
    assert res["channels"][0].weight > 0.0


def test_spatial_audio_ray_tracing_shoebox():
    room = [6.0, 4.0, 3.0]
    source = [1.0, 1.0, 1.0]
    receiver = [4.0, 2.5, 1.5]
    res = AcousticRayTracingShoebox.simulate(room, source, receiver, absorption_coeff=0.2, num_rays=40)
    assert res["room_volume_m3"] == 72.0
    assert 0.1 < res["rt60_sabine_sec"] < 2.0
    assert res["direct_tof_ms"] > 0.0


def test_spatial_audio_spoken_english():
    code = """use spatial_audio
calculate spherical harmonics azimuth 60.0 elevation 30.0 order 2 into sh_res
simulate acoustic ray tracing room [6.0, 5.0, 3.0] source [1.0, 1.0, 1.0] receiver [4.0, 3.0, 1.5] absorption 0.2 rays 40 into ray_res
"""
    env = execute(code)
    assert env["sh_res"].channels_count == 9
    assert env["ray_res"].room_volume_m3 == 90.0
