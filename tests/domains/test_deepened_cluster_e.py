"""Unit and integration tests for Deepened Cluster E (Media, Spatial & Game Systems).

Tests the enhanced capabilities of:
- image: GeometricWarp, MorphologicalOps, ColorQuantizer
- audio: PolyphonicSynth, YINPitchDetector, ParametricEQ
- spatial_audio: HigherOrderAmbisonics, AcousticRaytracer, HRTFConvolution
- game: BehaviorTree, SteeringBehaviors, TilemapPhysics
- metrics: OTLPTraceExporter, ExponentialDecayReservoir, EWMAAnomalyDetector
"""

import math
import pytest

from doomscript.domains.image.runtime import (
    GeometricWarp,
    MorphologicalOps,
    ColorQuantizer,
    image_warp_affine,
    image_morphology,
    image_quantize_palette,
)
from doomscript.domains.audio.runtime import (
    PolyphonicSynth,
    YINPitchDetector,
    ParametricEQ,
    audio_poly_synth_render,
    audio_yin_pitch,
    audio_parametric_eq,
)
from doomscript.domains.spatial_audio.runtime import (
    HigherOrderAmbisonics,
    AcousticRaytracer,
    HRTFConvolution,
    spatial_audio_hoa_encode,
    spatial_audio_room_impulse_response,
    spatial_audio_hrtf_binaural,
)
from doomscript.domains.game.runtime import (
    BehaviorTree,
    SequenceNode,
    SelectorNode,
    InverterNode,
    ActionNode,
    ConditionNode,
    NodeStatus,
    SteeringBehaviors,
    TilemapPhysics,
    game_create_tilemap,
    game_tilemap_set,
    game_create_behavior_tree,
    game_steering_seek,
    game_tilemap_resolve,
)
from doomscript.domains.metrics.runtime import (
    TraceSpan,
    OTLPTraceExporter,
    ExponentialDecayReservoir,
    EWMAAnomalyDetector,
    metrics_export_otlp_traces,
    metrics_create_ewma_detector,
)


# ==============================================================================
# Image Tests
# ==============================================================================

def test_image_warp_affine():
    # 10x10 image with white dot at (4, 4)
    img = [[0.0] * 10 for _ in range(10)]
    img[4][4] = 255.0

    # Translate by (+2, +2)
    mat = GeometricWarp.affine_matrix(translation=(2.0, 2.0))
    warped = GeometricWarp.warp(img, mat)

    assert len(warped) == 10
    assert len(warped[0]) == 10
    # Peak should now be at (6, 6)
    assert warped[6][6] > 200.0
    assert warped[4][4] < 50.0


def test_image_morphological_ops():
    # 7x7 grid with single central white pixel at (3, 3)
    img = [[0.0] * 7 for _ in range(7)]
    img[3][3] = 255.0

    # Dilation with 3x3 square expands pixel to 3x3 block
    dil = MorphologicalOps.dilate(img, size=3, shape="rect")
    for y in range(2, 5):
        for x in range(2, 5):
            assert dil[y][x] == 255.0
    assert dil[0][0] == 0.0

    # Erosion on dilated image shrinks it back to center
    ero = MorphologicalOps.erode(dil, size=3, shape="rect")
    assert ero[3][3] == 255.0
    assert ero[2][2] == 0.0

    # Morphological gradient
    grad = MorphologicalOps.gradient(dil, size=3, shape="rect")
    assert len(grad) == 7


def test_color_quantizer_and_dithering():
    # Generate 32 distinct RGB colors
    colors = [(i * 8, 255 - i * 8, (i * 16) % 256) for i in range(32)]
    palette = ColorQuantizer.median_cut(colors, num_colors=4)

    assert len(palette) == 4
    for r, g, b in palette:
        assert 0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255

    # Test Floyd-Steinberg dithering on 4x4 patch
    patch = [[(128, 128, 128)] * 4 for _ in range(4)]
    dithered = ColorQuantizer.dither_floyd_steinberg(patch, palette)
    assert len(dithered) == 4
    for row in dithered:
        for pix in row:
            assert pix in palette


# ==============================================================================
# Audio Tests
# ==============================================================================

def test_polyphonic_synth():
    synth = PolyphonicSynth(sample_rate=22050, max_voices=4)
    # C major triad: C4(60), E4(64), G4(67)
    synth.note_on(60, velocity=0.8, waveform="sawtooth")
    synth.note_on(64, velocity=0.8, waveform="sawtooth")
    synth.note_on(67, velocity=0.8, waveform="sawtooth")

    rendered = synth.render(duration_sec=0.1)
    assert len(rendered) == int(0.1 * 22050)

    # Check signal presence and clipping bounds
    max_amp = max(abs(s) for s in rendered)
    assert max_amp > 0.01
    assert max_amp <= 1.0


def test_yin_pitch_detector():
    # 440 Hz (A4) test signal
    sr = 44100
    dur = 0.05
    n = int(dur * sr)
    samples = [math.sin(2.0 * math.pi * 440.0 * i / sr) for i in range(n)]

    pitch_info = YINPitchDetector.detect_pitch(samples, sample_rate=sr, threshold=0.15)
    f0 = pitch_info["pitch_hz"]
    assert abs(f0 - 440.0) < 4.0
    assert pitch_info["clarity"] > 0.85


def test_parametric_eq():
    sr = 44100
    n = 1000
    # Mix 100 Hz and 5000 Hz tones
    clean = [
        math.sin(2.0 * math.pi * 100.0 * i / sr) + math.sin(2.0 * math.pi * 5000.0 * i / sr)
        for i in range(n)
    ]

    bands = [
        {"type": "peaking", "freq": 100.0, "gain_db": 6.0, "q": 1.0},
        {"type": "peaking", "freq": 5000.0, "gain_db": -12.0, "q": 1.0},
    ]

    filtered = ParametricEQ.process(clean, bands, sample_rate=sr)
    assert len(filtered) == len(clean)
    assert all(-1.0 <= s <= 1.0 for s in filtered)


# ==============================================================================
# Spatial Audio Tests
# ==============================================================================

def test_higher_order_ambisonics():
    impulse = [1.0] + [0.0] * 15
    # Sound directly in front: azimuth = 0, elevation = 0
    hoa = HigherOrderAmbisonics.encode_2nd_order(impulse, azimuth_deg=0.0, elevation_deg=0.0)
    assert len(hoa) == 9  # 9 channels for 2nd order

    # W (channel 0) and X (channel 3) should have full positive energy
    assert hoa[0][0] == 1.0
    assert abs(hoa[3][0] - 1.0) < 1e-4
    # Y (channel 1, left-right) should be 0 for front sound
    assert abs(hoa[1][0]) < 1e-4

    # Decode to 4 quad loudspeakers (0, 90, 180, 270 deg)
    speakers = [0.0, 90.0, 180.0, 270.0]
    spk_feeds = HigherOrderAmbisonics.decode_to_loudspeakers(hoa, speakers)
    assert len(spk_feeds) == 4
    # Front speaker (0 deg) should have highest amplitude
    assert spk_feeds[0][0] > spk_feeds[2][0]


def test_acoustic_raytracer():
    room = (5.0, 4.0, 3.0)
    source = (2.0, 2.0, 1.5)
    listener = (3.0, 2.0, 1.5)  # 1 meter away

    rir = AcousticRaytracer.generate_rir(room, source, listener, max_order=2, sample_rate=44100, duration_sec=0.05)
    assert len(rir) == int(0.05 * 44100)

    # Direct sound arrival time: dist = 1.0 m, speed = 343 m/s => ~128 samples
    expected_delay = int(round((1.0 / 343.0) * 44100))
    # Search for peak within small window around expected delay
    peak_idx = rir.index(max(rir))
    assert abs(peak_idx - expected_delay) <= 2


def test_hrtf_convolution():
    mono = [1.0, 0.5, 0.2, 0.0] + [0.0] * 50
    # Sound from hard right (90 deg)
    left, right = HRTFConvolution.spatialize(mono, azimuth_deg=90.0, sample_rate=44100)

    # Right ear receives sound at t=0
    assert right[0] == 1.0
    # Left ear receives delayed sound with lower amplitude
    assert left[0] == 0.0
    assert max(left) < 1.0


# ==============================================================================
# Game Tests
# ==============================================================================

def test_behavior_tree():
    bb = {"stamina": 50, "attack_done": False, "rest_done": False}

    def can_attack(b):
        return b["stamina"] >= 80

    def do_attack(b):
        b["attack_done"] = True
        return NodeStatus.SUCCESS

    def do_rest(b):
        b["rest_done"] = True
        return NodeStatus.SUCCESS

    # Tree: Selector [ Sequence [ can_attack, do_attack ], do_rest ]
    root = SelectorNode([
        SequenceNode([
            ConditionNode(can_attack),
            ActionNode(do_attack),
        ]),
        ActionNode(do_rest),
    ])

    tree = BehaviorTree(root, bb)
    # First tick: stamina < 80, should rest
    st = tree.tick()
    assert st == NodeStatus.SUCCESS
    assert not bb["attack_done"]
    assert bb["rest_done"]

    # Second tick: restore stamina, should attack
    bb["stamina"] = 100
    bb["attack_done"] = False
    bb["rest_done"] = False
    tree.tick()
    assert bb["attack_done"]
    assert not bb["rest_done"]


def test_steering_behaviors():
    pos = (0.0, 0.0)
    vel = (0.0, 0.0)
    target = (10.0, 0.0)

    force = SteeringBehaviors.seek(pos, vel, target, max_speed=4.0, max_force=0.5)
    # Force should point along +x direction
    assert force[0] > 0.0
    assert abs(force[1]) < 1e-4

    # Arrive within slowing radius should scale down force
    force_arrive = SteeringBehaviors.arrive(pos, vel, (0.5, 0.0), slowing_radius=5.0, max_speed=4.0, max_force=0.5)
    assert force_arrive[0] > 0.0


def test_tilemap_physics():
    # 5x5 tilemap with solid floor at row 4
    tm = game_create_tilemap(5, 5)
    for x in range(5):
        game_tilemap_set(tm, x, 4, "solid")

    box_pos = (2.0, 2.5)
    box_size = (0.8, 0.8)
    # Moving downwards into floor (+y is downwards)
    box_vel = (0.0, 1.5)

    res = TilemapPhysics.resolve_box(box_pos, box_size, box_vel, tm, tile_size=1.0)
    new_pos = res["pos"]
    new_vel = res["vel"]

    # Floor is at y=4. Box top should be stopped at y = 4 - 0.8 = 3.2
    assert abs(new_pos[1] - 3.2) < 1e-3
    assert new_vel[1] == 0.0
    assert res["on_ground"] is True


# ==============================================================================
# Metrics Tests
# ==============================================================================

def test_otlp_trace_exporter():
    span = TraceSpan(name="test_operation", trace_id="trace-abc-123")
    span.tag("http.status_code", 200)
    span.tag("env", "production")
    span.log_event("query_completed")
    span.finish()

    payload = OTLPTraceExporter.export_spans([span], service_name="doom-engine")
    assert "resourceSpans" in payload
    r_spans = payload["resourceSpans"][0]
    s_spans = r_spans["scopeSpans"][0]["spans"]
    assert len(s_spans) == 1

    exported_span = s_spans[0]
    assert exported_span["name"] == "test_operation"
    assert len(exported_span["traceId"]) == 32
    assert len(exported_span["spanId"]) == 16
    assert any(a["key"] == "http.status_code" for a in exported_span["attributes"])


def test_exponential_decay_reservoir():
    res = ExponentialDecayReservoir(size=200, alpha=0.01)
    # Feed 100 observations
    for i in range(100):
        res.update(float(i))

    p50 = res.get_percentile(50.0)
    p90 = res.get_percentile(90.0)

    assert 40.0 <= p50 <= 60.0
    assert 80.0 <= p90 <= 99.0


def test_ewma_anomaly_detector():
    detector = EWMAAnomalyDetector(alpha=0.2, threshold_z=3.0)

    # Establish baseline around 10.0
    for _ in range(30):
        res = detector.update(10.0)
        assert res["is_anomaly"] is False

    # Inject extreme anomaly (100.0)
    res_spike = detector.update(100.0)
    assert res_spike["is_anomaly"] is True
    assert res_spike["z_score"] > 3.0
