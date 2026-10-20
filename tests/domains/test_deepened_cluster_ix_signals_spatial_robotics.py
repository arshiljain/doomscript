"""Tests for Deepened Cluster IX: Digital Signal Processing, Spatial Audio & Robotics Domains."""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# SIGNALS DEEPENED TESTS
# ==============================================================================

def test_signals_kalman_filter():
    """Validates multi-dimensional linear Kalman filter state estimation."""
    code = """
use signals
set F to [[1.0, 1.0], [0.0, 1.0]]
set H to [[1.0, 0.0]]
set Q to [[0.01, 0.0], [0.0, 0.01]]
set R to [[0.1]]
set z_meas to [[1.0], [2.1], [2.9], [4.05], [5.02]]
filter measurements z_meas using kalman with transition F and observation H and process noise Q and measurement noise R into kf_res
assert kf_res's num_steps equals 5
assert kf_res's final_state[0] is greater than 4.5
"""
    env = execute(code)
    assert env["kf_res"]["num_steps"] == 5
    assert env["kf_res"]["final_state"][0] > 4.5


def test_signals_butterworth_lowpass():
    """Validates cascaded biquad Butterworth IIR digital lowpass filter."""
    code = """
use signals
set test_sig to [1.0, 2.0, 1.0, 0.0, -1.0, 1.0, 2.0, 1.0, 0.0, -1.0]
apply butterworth lowpass filter to test_sig with cutoff 50.0 order 4 rate 1000.0 into filtered
assert len(filtered) equals 10
"""
    env = execute(code)
    assert len(env["filtered"]) == 10


def test_signals_emd_decompose():
    """Validates Empirical Mode Decomposition (EMD) Intrinsic Mode Function extraction."""
    code = """
use signals
set wave to [
    0.0, 0.8, 0.95, 0.3, -0.5, -0.9, -0.3, 0.6, 1.0, 0.5,
    -0.2, -0.8, -0.9, -0.2, 0.7, 0.9, 0.2, -0.6, -0.8, 0.0
]
decompose signal wave into imfs max 3 into emd_res
assert emd_res's original_length equals 20
assert emd_res's num_imfs is greater than 0
"""
    env = execute(code)
    assert env["emd_res"]["original_length"] == 20
    assert env["emd_res"]["num_imfs"] > 0


# ==============================================================================
# SPATIAL AUDIO DEEPENED TESTS
# ==============================================================================

def test_spatial_audio_early_reflections():
    """Validates shoebox room acoustic image-source reflection calculations."""
    code = """
use spatial_audio
set room to [8.0, 6.0, 3.0]
set src to [2.0, 2.0, 1.5]
set rec to [5.0, 4.0, 1.5]
calculate early reflections in room room from source src to receiver rec into refl_res
assert refl_res's reflections_count is greater than 10
assert refl_res's direct_sound_delay_ms is greater than 0.0
assert refl_res's room_volume_m3 equals 144.0
assert refl_res's rt60_sabine_sec is greater than 0.0
"""
    env = execute(code)
    assert env["refl_res"]["reflections_count"] > 10
    assert env["refl_res"]["room_volume_m3"] == 144.0


def test_spatial_audio_convolve_ir():
    """Validates discrete audio convolution with acoustic impulse response."""
    code = """
use spatial_audio
set dry_sig to [1.0, 0.5, 0.2, 0.0]
set ir to [0.8, 0.4, 0.2]
convolve audio dry_sig with impulse response ir into conv_res
assert conv_res's num_samples equals 6
assert conv_res's peak_amplitude is greater than 0.0
assert conv_res's convolved[0] equals 0.8
"""
    env = execute(code)
    assert env["conv_res"]["num_samples"] == 6
    assert abs(env["conv_res"]["convolved"][0] - 0.8) < 1e-4


# ==============================================================================
# ROBOTICS DEEPENED TESTS
# ==============================================================================

def test_robotics_dubins_path():
    """Validates non-holonomic Dubins car shortest path planning."""
    code = """
use robotics
set p_start to [0.0, 0.0, 0.0]
set p_goal to [5.0, 5.0, 1.5708]
calculate dubins path from p_start to p_goal with radius 1.5 into dub_res
assert dub_res's total_length is greater than 0.0
assert dub_res's waypoints_count is greater than 10
"""
    env = execute(code)
    assert env["dub_res"]["total_length"] > 0.0
    assert env["dub_res"]["waypoints_count"] > 10
    assert env["dub_res"]["path_type"] in ["LSL", "RSR", "LSR", "RSL", "RLR", "LRL"]


def test_robotics_occupancy_grid_update():
    """Validates 2D log-odds occupancy grid mapping via Bresenham ray-casting."""
    code = """
use robotics
set pose to [0.0, 0.0, 0.0]
set scans to [2.0, 2.5, 3.0, 2.5, 2.0]
update occupancy grid with pose pose and scan ranges scans into occ_res
assert occ_res's total_cells equals 1600
assert occ_res's free_count is greater than 0
"""
    env = execute(code)
    assert env["occ_res"]["total_cells"] == 1600
    assert env["occ_res"]["free_count"] > 0
