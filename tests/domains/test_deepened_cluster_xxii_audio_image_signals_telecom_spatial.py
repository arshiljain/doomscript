"""Unit tests for Cluster XXII Deepened Domains:
Audio, Image, Signals, Telecom, Spatial Audio.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import math
import textwrap
import unittest
from doomscript.compiler.engine import execute

from doomscript.domains.audio.runtime import (
    PitchShiftPhaseVocoder,
    DynamicRangeCompressorLimiter,
    audio_pitch_shift,
    audio_compress_limit,
)
from doomscript.domains.image.runtime import (
    HarrisCornerDetectorPure,
    BicubicImageResampler,
    image_harris_corners,
    image_resample_bicubic,
)
from doomscript.domains.signals.runtime import (
    HilbertTransformAnalyticSignal,
    PseudoWignerVilleDistribution,
    signals_hilbert_envelope,
    signals_pseudo_wigner_ville,
)
from doomscript.domains.telecom.runtime import (
    TurboCodeIterativeDecoder,
    CostasLoopCarrierRecovery,
    telecom_turbo_encode,
    telecom_turbo_decode,
    telecom_costas_loop_recovery,
)
from doomscript.domains.spatial_audio.runtime import (
    BinauralRoomImpulseResponseBRIRGenerator,
    AmbisonicsBFormatBinauralDecoder,
    spatial_generate_brir,
    spatial_ambisonics_binaural_decode,
)


class TestDeepenedClusterXXII(unittest.TestCase):

    # =========================================================================
    # AUDIO
    # =========================================================================

    def test_audio_phase_vocoder_direct(self):
        samples = [math.sin(2.0 * math.pi * 440.0 * i / 44100.0) for i in range(256)]
        res = PitchShiftPhaseVocoder.pitch_shift(samples, semitones=4.0, sample_rate=44100)
        self.assertEqual(len(res["output_samples"]), 256)
        self.assertAlmostEqual(res["pitch_ratio"], 2.0 ** (4.0 / 12.0), places=2)

    def test_audio_dynamic_compressor_direct(self):
        samples = [0.1, 0.9, 1.5, -1.8, 0.8, -0.95, 0.2] * 10
        res = DynamicRangeCompressorLimiter.process(
            samples, threshold_db=-6.0, ratio=8.0, attack_ms=2.0, release_ms=20.0, makeup_gain_db=1.0
        )
        self.assertGreater(res["max_gain_reduction_db"], 0.0)
        self.assertEqual(len(res["output_samples"]), len(samples))

    def test_audio_spoken_english(self):
        code = textwrap.dedent("""
            use audio
            set test_samples to [0.0, 0.707, 1.0, 0.707, 0.0, -0.707, -1.0, -0.707] * 16
            pitch shift audio test_samples by 4 semitones sample rate 44100 into shifted_res
            set out_len to shifted_res's output_length
            set p_ratio to shifted_res's pitch_ratio
            apply dynamic range limiter to test_samples threshold -6.0 ratio 4.0 attack 2.0 release 20.0 makeup 1.0 into comp_res
            set gr to comp_res's max_gain_reduction_db
        """).strip()
        env = execute(code)
        self.assertEqual(env["out_len"], 128)
        self.assertAlmostEqual(env["p_ratio"], 2.0 ** (4.0 / 12.0), places=2)
        self.assertGreaterEqual(env["gr"], 0.0)

    # =========================================================================
    # IMAGE
    # =========================================================================

    def test_image_harris_corner_detector_direct(self):
        img = [[0.0] * 12 for _ in range(12)]
        for r in range(3, 8):
            for c in range(3, 8):
                img[r][c] = 255.0
        res = HarrisCornerDetectorPure.detect(img, k=0.04, threshold=2000.0, nms_radius=1)
        self.assertGreater(res["corner_count"], 0)
        self.assertEqual(res["rows"], 12)
        self.assertEqual(res["cols"], 12)

    def test_image_bicubic_resampler_direct(self):
        small_img = [
            [10.0, 20.0, 30.0, 40.0],
            [50.0, 60.0, 70.0, 80.0],
            [90.0, 100.0, 110.0, 120.0],
            [130.0, 140.0, 150.0, 160.0],
        ]
        res_bicubic = BicubicImageResampler.resample(small_img, new_rows=8, new_cols=8, method="bicubic")
        res_bilinear = BicubicImageResampler.resample(small_img, new_rows=6, new_cols=6, method="bilinear")
        self.assertEqual(res_bicubic["new_rows"], 8)
        self.assertEqual(res_bicubic["new_cols"], 8)
        self.assertEqual(res_bilinear["new_rows"], 6)
        self.assertEqual(res_bilinear["new_cols"], 6)

    def test_image_spoken_english(self):
        code = textwrap.dedent("""
            use image
            set img to [
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 200.0, 200.0, 200.0, 200.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 200.0, 200.0, 200.0, 200.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 200.0, 200.0, 200.0, 200.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ]
            detect harris corners in image img sensitivity 0.04 threshold 2000.0 nms 1 into harris_res
            set num_corners to harris_res's corner_count
            resample image img to rows 5 cols 5 using bicubic into downsampled_res
            set new_h to downsampled_res's new_rows
        """).strip()
        env = execute(code)
        self.assertGreater(env["num_corners"], 0)
        self.assertEqual(env["new_h"], 5)

    # =========================================================================
    # SIGNALS
    # =========================================================================

    def test_signals_hilbert_direct(self):
        fs = 500.0
        n_pts = 64
        t_arr = [i / fs for i in range(n_pts)]
        sig = [
            (1.0 + 0.5 * math.cos(2.0 * math.pi * 5.0 * t)) * math.sin(2.0 * math.pi * 50.0 * t)
            for t in t_arr
        ]
        res = HilbertTransformAnalyticSignal.analyze(sig, sample_rate=fs)
        self.assertEqual(res["sample_count"], 64)
        self.assertGreater(res["mean_envelope"], 0.4)

    def test_signals_pwvd_direct(self):
        sig = [math.sin(0.1 * i * i * 0.05) for i in range(32)]
        res = PseudoWignerVilleDistribution.compute(sig, window_len=11, num_freq_bins=16, sample_rate=500.0)
        self.assertGreater(res["total_energy"], 0.0)
        self.assertEqual(res["num_times"], 32)
        self.assertEqual(res["num_freq_bins"], 16)

    def test_signals_spoken_english(self):
        code = textwrap.dedent("""
            use signals
            set sig to [1.0, 0.5, -0.5, -1.0, -0.5, 0.5] * 8
            compute hilbert analytic envelope of sig sample rate 500.0 into hilb_res
            set env_mean to hilb_res's mean_envelope
            compute pseudo wigner ville distribution of sig window 11 freq bins 16 sample rate 500.0 into pwvd_res
            set tot_energy to pwvd_res's total_energy
        """).strip()
        env = execute(code)
        self.assertGreater(env["env_mean"], 0.1)
        self.assertGreater(env["tot_energy"], 0.0)

    # =========================================================================
    # TELECOM
    # =========================================================================

    def test_telecom_turbo_direct(self):
        bits = [1, 0, 1, 1, 0, 1, 0, 0]
        enc = TurboCodeIterativeDecoder.encode(bits)
        self.assertEqual(len(enc["systematic_bits"]), 8)
        self.assertEqual(len(enc["parity1_bits"]), 8)
        self.assertEqual(len(enc["parity2_bits"]), 8)

        # Generate LLRs: +6 for 0, -6 for 1
        l_sys = [-6.0 if b == 1 else 6.0 for b in enc["systematic_bits"]]
        l_p1 = [-6.0 if b == 1 else 6.0 for b in enc["parity1_bits"]]
        l_p2 = [-6.0 if b == 1 else 6.0 for b in enc["parity2_bits"]]

        dec = TurboCodeIterativeDecoder.decode(l_sys, l_p1, l_p2, interleaver=enc["interleaver"], iterations=4)
        self.assertEqual(dec["decoded_bits"], bits)

    def test_telecom_costas_loop_direct(self):
        samples = [1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0] * 10
        res = CostasLoopCarrierRecovery.process(samples, modulation="bpsk", loop_bw=0.04)
        self.assertEqual(res["sample_count"], 80)
        self.assertTrue(res["lock_detected"])

    def test_telecom_spoken_english(self):
        code = textwrap.dedent("""
            use telecom
            set sys_llr to [-6.0, 6.0, -6.0, -6.0, 6.0, -6.0, 6.0, 6.0]
            set p1_llr to [-5.0, 5.0, -5.0, 5.0, -5.0, 5.0, -5.0, 5.0]
            set p2_llr to [-5.0, -5.0, 5.0, 5.0, -5.0, 5.0, 5.0, -5.0]
            decode turbo code llr sys sys_llr par1 p1_llr par2 p2_llr iterations 4 into turbo_res
            set dec_bits to turbo_res's decoded_bits
            set rf_samples to [1.0, -1.0, 1.0, 1.0, -1.0, 1.0, -1.0, -1.0] * 10
            recover carrier with costas loop from rf_samples modulation bpsk loop bandwidth 0.05 into costas_res
            set is_locked to costas_res's lock_detected
        """).strip()
        env = execute(code)
        self.assertEqual(env["dec_bits"], [1, 0, 1, 1, 0, 1, 0, 0])
        self.assertTrue(env["is_locked"])

    # =========================================================================
    # SPATIAL AUDIO
    # =========================================================================

    def test_spatial_audio_brir_direct(self):
        room = [5.0, 4.0, 2.8]
        src = [2.0, 1.5, 1.2]
        lis = [3.0, 2.0, 1.2]
        res = BinauralRoomImpulseResponseBRIRGenerator.generate(room, src, lis, max_order=2, sample_rate=16000)
        self.assertGreater(res["reflections_count"], 0)
        self.assertGreater(res["direct_delay_ms"], 0.0)
        self.assertEqual(len(res["brir_left"]), len(res["brir_right"]))

    def test_spatial_audio_ambisonics_direct(self):
        w = [1.0] * 8
        x = [0.5] * 8
        y = [0.2] * 8
        z = [0.1] * 8
        res = AmbisonicsBFormatBinauralDecoder.decode(w, x, y, z, num_virtual_speakers=8)
        self.assertEqual(res["num_samples"], 8)
        self.assertEqual(len(res["left_channel"]), 8)
        self.assertEqual(len(res["right_channel"]), 8)

    def test_spatial_audio_spoken_english(self):
        code = textwrap.dedent("""
            use spatial_audio
            set room_size to [5.0, 4.0, 2.8]
            set src to [2.0, 1.5, 1.2]
            set lis to [3.0, 2.0, 1.2]
            generate binaural room impulse response room room_size source src listener lis order 2 absorption 0.25 sample rate 16000 into brir_res
            set refl_count to brir_res's reflections_count
            set w_sig to [1.0, 0.8, 0.6, 0.4, 0.2, 0.0, -0.2, -0.4]
            set x_sig to [0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2]
            set y_sig to [0.2, 0.2, 0.1, 0.1, 0.0, 0.0, -0.1, -0.1]
            set z_sig to [0.0, 0.1, 0.0, -0.1, 0.0, 0.1, 0.0, -0.1]
            decode b format ambisonics to binaural w w_sig x x_sig y y_sig z z_sig virtual speakers 8 into amb_dec_res
            set n_samples to amb_dec_res's num_samples
        """).strip()
        env = execute(code)
        self.assertGreater(env["refl_count"], 0)
        self.assertEqual(env["n_samples"], 8)


if __name__ == "__main__":
    unittest.main()
