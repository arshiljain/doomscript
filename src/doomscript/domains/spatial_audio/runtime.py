"""3D Spatial Audio, Ambisonics & Psychoacoustics Domain for DoomScript.

Provides 100% pure Python DSP audio spatialization:
- Binaural panning with Interaural Time Difference (ITD, Woodworth's formula) and Level Difference (ILD)
- First-Order Ambisonics (FOA) B-format spherical harmonic encoding (W, X, Y, Z) and stereo decoding
- Acoustic Doppler frequency and pitch shifting
- Schroeder algorithmic reverberation (4 parallel comb filters + 2 series allpass filters)
Zero external dependencies.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple, Union


class BinauralPanner:
    """Binaural spatialization using Woodworth's ITD spherical head model and ILD shadowing."""

    SPEED_OF_SOUND = 343.0  # m/s
    HEAD_RADIUS = 0.0875    # 8.75 cm average human head radius

    @staticmethod
    def pan(
        signal: List[float],
        azimuth_deg: float,
        sample_rate: int = 44100,
    ) -> Tuple[List[float], List[float]]:
        """Pans a mono signal into binaural (left, right) channels based on azimuth angle."""
        n = len(signal)
        if n == 0:
            return [], []

        # Convert azimuth to radians in [-pi, pi]
        theta = math.radians(azimuth_deg % 360)
        if theta > math.pi:
            theta -= 2 * math.pi

        # Woodworth formula for ITD: tau = (r / c) * (theta + sin(theta)) for |theta| <= pi/2
        abs_theta = abs(theta)
        if abs_theta <= math.pi / 2:
            itd_sec = (BinauralPanner.HEAD_RADIUS / BinauralPanner.SPEED_OF_SOUND) * (abs_theta + math.sin(abs_theta))
        else:
            itd_sec = (BinauralPanner.HEAD_RADIUS / BinauralPanner.SPEED_OF_SOUND) * (math.pi - abs_theta + math.sin(abs_theta))

        delay_samples = itd_sec * sample_rate

        # ILD: High-frequency head shadowing gain approximation
        # Source to the right (theta > 0): left ear delayed and attenuated
        # Source to the left (theta < 0): right ear delayed and attenuated
        gain_near = 1.0
        gain_far = 0.5 + 0.5 * math.cos(abs_theta)

        left_signal = [0.0] * n
        right_signal = [0.0] * n

        def delay_channel(in_sig: List[float], delay: float, gain: float) -> List[float]:
            out = [0.0] * n
            int_d = int(math.floor(delay))
            frac_d = delay - int_d
            for i in range(n):
                src_idx = i - int_d
                if src_idx >= 0:
                    val0 = in_sig[src_idx]
                    val1 = in_sig[src_idx - 1] if src_idx - 1 >= 0 else 0.0
                    val = (1.0 - frac_d) * val0 + frac_d * val1
                    out[i] = val * gain
            return out

        if theta >= 0:
            # Sound from right
            right_signal = [s * gain_near for s in signal]
            left_signal = delay_channel(signal, delay_samples, gain_far)
        else:
            # Sound from left
            left_signal = [s * gain_near for s in signal]
            right_signal = delay_channel(signal, delay_samples, gain_far)

        return left_signal, right_signal


class AmbisonicsBFormat:
    """First-Order Ambisonics (FOA) spherical harmonic encoder and decoder."""

    @staticmethod
    def encode(
        signal: List[float], azimuth_deg: float, elevation_deg: float = 0.0
    ) -> Dict[str, List[float]]:
        """Encodes mono signal to B-format (W, X, Y, Z)."""
        theta = math.radians(azimuth_deg)
        phi = math.radians(elevation_deg)

        # Spherical harmonic weights
        w_weight = 1.0 / math.sqrt(2.0)
        x_weight = math.cos(theta) * math.cos(phi)
        y_weight = math.sin(theta) * math.cos(phi)
        z_weight = math.sin(phi)

        return {
            "W": [s * w_weight for s in signal],
            "X": [s * x_weight for s in signal],
            "Y": [s * y_weight for s in signal],
            "Z": [s * z_weight for s in signal],
        }

    @staticmethod
    def decode_stereo(b_format: Dict[str, List[float]]) -> Tuple[List[float], List[float]]:
        """Decodes B-format to stereo virtual loudspeakers at +/- 45 degrees."""
        w = b_format["W"]
        x = b_format["X"]
        y = b_format["Y"]
        n = len(w)

        sqrt2_inv = 1.0 / math.sqrt(2.0)
        left: List[float] = [0.0] * n
        right: List[float] = [0.0] * n

        for i in range(n):
            left[i] = round(sqrt2_inv * w[i] + 0.5 * x[i] + 0.5 * y[i], 5)
            right[i] = round(sqrt2_inv * w[i] + 0.5 * x[i] - 0.5 * y[i], 5)

        return left, right


class DopplerEffect:
    """Acoustic Doppler frequency and pitch shift simulation."""

    SPEED_OF_SOUND = 343.0  # m/s

    @staticmethod
    def shift(
        signal: List[float], source_speed: float, listener_speed: float = 0.0, sample_rate: int = 44100
    ) -> List[float]:
        """Resamples signal according to Doppler frequency ratio:
        f' = f * (c - v_listener) / (c - v_source).
        """
        c = DopplerEffect.SPEED_OF_SOUND
        ratio = (c - listener_speed) / max(0.1, (c - source_speed))

        n = len(signal)
        if n == 0 or ratio <= 0:
            return list(signal)

        # Resample signal by factor 'ratio'
        out_len = int(n / ratio)
        output = [0.0] * out_len

        for i in range(out_len):
            src_pos = i * ratio
            idx = int(math.floor(src_pos))
            frac = src_pos - idx
            if idx + 1 < n:
                output[i] = (1.0 - frac) * signal[idx] + frac * signal[idx + 1]
            elif idx < n:
                output[i] = signal[idx]
            else:
                break

        return output


class SchroederReverberator:
    """Algorithmic reverberator with 4 feedback comb filters in parallel and 2 allpass filters."""

    @staticmethod
    def process(signal: List[float], rt60: float = 1.5, sample_rate: int = 44100) -> List[float]:
        n = len(signal)
        if n == 0:
            return []

        # Comb filter delay lengths in milliseconds (mutually prime)
        comb_delays_ms = [29.7, 37.1, 41.1, 43.7]
        comb_delays = [int(ms * 0.001 * sample_rate) for ms in comb_delays_ms]

        # Calculate feedback gains g = 10^(-3 * delay_sec / RT60)
        comb_gains = [10.0 ** (-3.0 * (d / sample_rate) / max(0.1, rt60)) for d in comb_delays]

        # Process 4 parallel comb filters
        comb_outputs: List[List[float]] = []
        for d, g in zip(comb_delays, comb_gains):
            buffer = [0.0] * d
            buf_idx = 0
            out = [0.0] * n
            for i in range(n):
                delayed = buffer[buf_idx]
                out[i] = delayed
                buffer[buf_idx] = signal[i] + delayed * g
                buf_idx = (buf_idx + 1) % d
            comb_outputs.append(out)

        # Sum comb outputs
        mixed = [0.0] * n
        for i in range(n):
            mixed[i] = 0.25 * sum(comb_outputs[c][i] for c in range(4))

        # 2 Cascaded Allpass filters
        allpass_delays_ms = [5.0, 1.7]
        allpass_gains = [0.7, 0.7]

        cur_signal = mixed
        for ms, g in zip(allpass_delays_ms, allpass_gains):
            d = max(1, int(ms * 0.001 * sample_rate))
            buffer = [0.0] * d
            buf_idx = 0
            ap_out = [0.0] * n
            for i in range(n):
                delayed = buffer[buf_idx]
                ap_out[i] = -g * cur_signal[i] + delayed
                buffer[buf_idx] = cur_signal[i] + g * delayed
                buf_idx = (buf_idx + 1) % d
            cur_signal = ap_out

        # Blend dry + wet
        wet_dry = 0.4
        result = [round(signal[i] * (1.0 - wet_dry) + cur_signal[i] * wet_dry, 5) for i in range(n)]
        return result


# --- Public High-Level Runtime Functions ---

def spatial_audio_binaural(
    signal: List[float], azimuth_deg: float, sample_rate: int = 44100
) -> Tuple[List[float], List[float]]:
    """Spatializes a mono signal to binaural stereo."""
    return BinauralPanner.pan(signal, azimuth_deg, sample_rate)


def spatial_audio_ambisonics_encode(
    signal: List[float], azimuth_deg: float, elevation_deg: float = 0.0
) -> Dict[str, List[float]]:
    """Encodes mono signal to First-Order Ambisonics B-format (W, X, Y, Z)."""
    return AmbisonicsBFormat.encode(signal, azimuth_deg, elevation_deg)


def spatial_audio_ambisonics_decode_stereo(b_format: Dict[str, List[float]]) -> Tuple[List[float], List[float]]:
    """Decodes B-format channels to virtual stereo loudspeakers."""
    return AmbisonicsBFormat.decode_stereo(b_format)


def spatial_audio_doppler(
    signal: List[float], source_speed: float, listener_speed: float = 0.0, sample_rate: int = 44100
) -> List[float]:
    """Applies acoustic Doppler shift."""
    return DopplerEffect.shift(signal, source_speed, listener_speed, sample_rate)


def spatial_audio_schroeder_reverb(
    signal: List[float], rt60: float = 1.5, sample_rate: int = 44100
) -> List[float]:
    """Applies Schroeder algorithmic reverberation."""
    return SchroederReverberator.process(signal, rt60, sample_rate)
