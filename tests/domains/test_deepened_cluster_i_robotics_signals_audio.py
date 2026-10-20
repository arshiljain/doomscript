"""Comprehensive unit test suite for Deepened Cluster I:
- Robotics: RRT & RRT* Path Planning, APF Artificial Potential Fields, Differential Drive Odometry, Pure Pursuit, Stewart Platform IK, Trapezoidal Profiles
- Signals: Cooley-Tukey Radix-2 FFT/IFFT, Hilbert Transform & Analytic Signal Envelopes, Cross-Correlation, Pitch Detection, Peak Finding with Prominence, Lomb-Scargle Periodogram
- Spatial Audio: 2nd-Order Higher Order Ambisonics (HOA), Image Source Acoustic Raytracing, Synthetic HRTF Binaural Rendering, 2D VBAP, Distance & Air Attenuation
"""

import math
import pytest
from doomscript.compiler.engine import execute


def test_deepened_robotics_rrt_and_rrt_star():
    code = """use robotics
start_pt = [1.0, 1.0]
goal_pt = [9.0, 9.0]
bounds = [0.0, 10.0, 0.0, 10.0]
obstacles = [{"x": 5.0, "y": 5.0, "r": 1.5}]

plan rrt path from start_pt to goal_pt in bounds bounds with obstacles obstacles step 1.0 into rrt_path
plan rrt star path from start_pt to goal_pt in bounds bounds with obstacles obstacles radius 3.0 into rrt_star_path
"""
    env = execute(code)
    assert env["rrt_path"] is not None
    assert len(env["rrt_path"]) >= 2
    assert env["rrt_path"][0] == [1.0, 1.0]
    assert env["rrt_path"][-1] == [9.0, 9.0]

    assert env["rrt_star_path"] is not None
    assert len(env["rrt_star_path"]) >= 2
    assert env["rrt_star_path"][0] == [1.0, 1.0]
    assert env["rrt_star_path"][-1] == [9.0, 9.0]


def test_deepened_robotics_apf_and_diff_drive():
    code = """use robotics
pos = [2.0, 2.0]
goal = [8.0, 8.0]
obstacles = [{"x": 4.0, "y": 4.0, "r": 1.0}]

calculate apf force at pos for goal goal with obstacles obstacles into apf
calculate differential drive forward with left 5.0 and right 7.0 radius 0.05 base 0.2 into dd_vel
integrate odometry for pose [0.0, 0.0, 0.0] with v 1.0 and w 0.5 over dt 0.2 into new_pose
"""
    env = execute(code)
    assert env["apf"]["magnitude"] > 0.0
    assert 40.0 <= env["apf"]["heading_deg"] <= 50.0

    v, w = env["dd_vel"]
    assert round(v, 3) == 0.3
    assert round(w, 3) == 0.5

    x, y, theta = env["new_pose"]
    assert x > 0.0
    assert theta > 0.0


def test_deepened_robotics_pure_pursuit_and_stewart_and_trapezoidal():
    code = """use robotics
robot_pose = [0.0, 0.0, 0.0]
path = [[1.0, 0.5], [2.0, 1.0], [3.0, 1.5]]
pure pursuit steer for pose robot_pose along path path lookahead 1.0 into steer

trans = [0.0, 0.0, 1.2]
rot = [0.0, 0.0, 0.0]
solve stewart platform ik for translation trans and rotation rot into legs

plan trapezoidal profile for distance 20.0 with max velocity 4.0 and max acceleration 2.0 into trap
"""
    env = execute(code)
    assert "curvature" in env["steer"]
    assert len(env["legs"]) == 6
    assert all(l > 1.0 for l in env["legs"])
    assert env["trap"]["total_time"] == 7.0
    assert env["trap"]["v_peak"] == 4.0


def test_deepened_signals_fft_and_ifft():
    code = """use signals
sig = [1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0]
compute fft of signal sig into spec
compute ifft of spectrum spec into recon
"""
    env = execute(code)
    assert len(env["spec"]) == 8
    assert len(env["recon"]) == 8
    for orig, rec in zip([1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0, 0.0], env["recon"]):
        assert abs(orig - rec.real) < 1e-5


def test_deepened_signals_hilbert_and_xcorr_and_pitch():
    code = """use signals
sig = [0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, -1.0]
calculate analytic signal of sig using hilbert into h_res

sig_a = [1.0, 0.0, 0.0, 0.0, 0.0]
sig_b = [0.0, 1.0, 0.0, 0.0, 0.0]
cross correlate signal sig_a with sig_b into xcorr

sample_rate = 16000
freq = 200.0
tone = [math.sin(2.0 * math.pi * freq * i / sample_rate) for i in range(800)]
detect pitch in signal tone with rate sample_rate into pitch_res
"""
    env = execute(code)
    assert len(env["h_res"]["envelope"]) == 8
    assert all(abs(e - 1.0) < 0.2 for e in env["h_res"]["envelope"])
    assert env["xcorr"]["lag"] == -1
    assert env["pitch_res"]["voiced"] is True
    assert abs(env["pitch_res"]["frequency_hz"] - 200.0) < 2.0


def test_deepened_signals_peaks_and_lomb_scargle():
    code = """use signals
samples = [0.0, 1.0, 5.0, 1.0, 0.0, 2.0, 8.0, 2.0, 0.0]
find peaks in signal samples with prominence 3.0 distance 2 into peaks

times = [0.0, 0.25, 0.5, 0.75, 1.0]
vals = [1.0, 0.0, -1.0, 0.0, 1.0]
freqs = [1.0, 2.0]
compute lomb scargle periodogram for times times and values vals at frequencies freqs into lsp
"""
    env = execute(code)
    assert len(env["peaks"]) == 2
    assert env["peaks"][0]["height"] == 5.0
    assert env["peaks"][1]["height"] == 8.0
    assert len(env["lsp"]["powers"]) == 2


def test_deepened_spatial_audio_hoa_and_rir():
    code = """use spatial_audio
sig = [0.1, 0.2, 0.3, 0.4]
encode hoa 2nd order audio sig at azimuth 90.0 elevation 0.0 into hoa
decode hoa audio hoa to speakers [0.0, 90.0, 180.0, 270.0] into spk_feeds

dims = (6.0, 5.0, 3.0)
src = (1.0, 1.0, 1.5)
lis = (3.0, 2.5, 1.5)
simulate room impulse response in room dims with source src and listener lis duration 0.02 into rir
"""
    env = execute(code)
    assert len(env["hoa"]) == 9
    assert len(env["spk_feeds"]) == 4
    assert len(env["rir"]) > 100


def test_deepened_spatial_audio_vbap_and_attenuation():
    code = """use spatial_audio
calculate vbap gains for azimuth 45.0 on speakers [0.0, 90.0, 180.0, 270.0] into gains

sig = [0.5, -0.5, 0.5, -0.5]
attenuate audio sig at distance 20.0 reference 1.0 rolloff 1.0 into attenuated
"""
    env = execute(code)
    assert len(env["gains"]) == 4
    assert env["gains"][0] > 0.6
    assert env["gains"][1] > 0.6
    assert env["gains"][2] == 0.0
    assert env["gains"][3] == 0.0

    assert len(env["attenuated"]) == 4
    assert abs(env["attenuated"][0]) < abs(env["sig"][0])
