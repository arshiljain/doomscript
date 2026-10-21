import pytest
import math
from doomscript.domains.image.runtime import HoughTransformCircles, IntegralImageHaarCascade, image_hough_circles, image_integral_image
from doomscript.domains.spatial_audio.runtime import MoorerReverberationNetwork, SoundOcclusionObstruction, spatial_audio_moorer_reverb, spatial_audio_occlusion
from doomscript.domains.signals.runtime import WaveletPacketDecomposition, CepstrumProcessor, signals_wavelet_packet_decompose, signals_real_cepstrum


def test_hough_transform_circles():
    width, height = 30, 30
    center_x, center_y, radius = 15, 15, 8
    edge_pixels = []
    
    for angle_deg in range(0, 360, 10):
        rad = math.radians(angle_deg)
        x = int(round(center_x + radius * math.cos(rad)))
        y = int(round(center_y + radius * math.sin(rad)))
        if 0 <= x < width and 0 <= y < height:
            edge_pixels.append((x, y))
            
    circles = HoughTransformCircles.detect_circles(
        edge_pixels, width, height, min_radius=6, max_radius=10, radius_step=1, threshold=5
    )
    assert len(circles) > 0
    best = circles[0]
    assert abs(best["center_x"] - center_x) <= 2
    assert abs(best["center_y"] - center_y) <= 2
    assert abs(best["radius"] - radius) <= 2
    
    # Also test domain helper
    rec = image_hough_circles(edge_pixels, width, height, min_r=6, max_r=10, threshold=5)
    assert rec["count"] > 0


def test_integral_image():
    # 10x10 matrix where each cell is 2.0
    grid = [[2.0] * 10 for _ in range(10)]
    sat = IntegralImageHaarCascade(grid)
    
    # 3x3 region sum should be 3 * 3 * 2.0 = 18.0
    val = sat.query_rect_sum(1, 1, 3, 3)
    assert abs(val - 18.0) < 1e-6

    # Test helper
    sat2 = image_integral_image(grid)
    assert abs(sat2.query_rect_sum(0, 0, 9, 9) - 200.0) < 1e-6


def test_moorer_reverberation():
    # Impulse train
    impulse = [1.0] + [0.0] * 3000
    wet = MoorerReverberationNetwork.process(impulse, sample_rate=44100)
    assert len(wet) == len(impulse)
    # Echoes should diffuse through the comb and all-pass filters
    assert any(abs(x) > 1e-4 for x in wet[50:1500])
    
    # Domain function test
    wet2 = spatial_audio_moorer_reverb(impulse, sample_rate=44100)
    assert len(wet2) == len(impulse)


def test_sound_occlusion_obstruction():
    sig = [1.0] * 50
    attenuated = SoundOcclusionObstruction.apply_occlusion(sig, wall_thickness_meters=0.2, material_density="concrete")
    assert len(attenuated) == len(sig)
    # Sound should be attenuated through concrete
    assert attenuated[-1] < 1.0
    
    # Domain helper test
    attenuated2 = spatial_audio_occlusion(sig, wall_thickness=0.3, material="wood")
    assert len(attenuated2) == len(sig)


def test_wavelet_packet_decomposition():
    sig = [math.sin(2 * math.pi * 0.1 * i) for i in range(16)]
    res = WaveletPacketDecomposition.decompose(sig, levels=2)
    assert res["levels"] == 2
    # Binary tree at level 2 has 2^2 = 4 terminal frequency nodes
    assert res["terminal_nodes"] == 4
    assert len(res["packets"]) == 4
    
    # Domain helper test
    rec = signals_wavelet_packet_decompose(sig, levels=2)
    assert rec["terminal_nodes"] == 4


def test_cepstrum_processor():
    # Pulse train at period = 32
    period = 32
    sig = [1.0 if i % period == 0 else 0.0 for i in range(256)]
    cep = CepstrumProcessor.real_cepstrum(sig)
    assert len(cep) == len(sig)
    
    # Domain helper test
    cep2 = signals_real_cepstrum(sig)
    assert len(cep2) == len(sig)
