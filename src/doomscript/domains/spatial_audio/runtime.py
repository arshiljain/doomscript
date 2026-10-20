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
from doomscript.runtime import Record


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


# ==============================================================================
# Advanced Spatial Audio: Higher Order Ambisonics, Acoustic Raytracer & HRTF
# ==============================================================================

class HigherOrderAmbisonics:
    """2nd-Order Ambisonics (9-channel HOA) spherical harmonics encoder and decoder."""

    @classmethod
    def encode_2nd_order(
        cls,
        signal: List[float],
        azimuth_deg: float,
        elevation_deg: float = 0.0,
    ) -> List[List[float]]:
        """
        Encodes mono signal into 9 ACN channels (N3D normalization):
        0: W (l=0, m=0)
        1: Y (l=1, m=-1), 2: Z (l=1, m=0), 3: X (l=1, m=1)
        4: V (l=2, m=-2), 5: T (l=2, m=-1), 6: R (l=2, m=0), 7: S (l=2, m=1), 8: U (l=2, m=2)
        """
        theta = math.radians(azimuth_deg)
        phi = math.radians(elevation_deg)
        cos_t, sin_t = math.cos(theta), math.sin(theta)
        cos_p, sin_p = math.cos(phi), math.sin(phi)

        y = [0.0] * 9
        # Order 0
        y[0] = 1.0
        # Order 1
        y[1] = sin_t * cos_p
        y[2] = sin_p
        y[3] = cos_t * cos_p
        # Order 2
        y[4] = math.sqrt(3.0) * sin_t * cos_t * (cos_p ** 2)
        y[5] = math.sqrt(3.0) * sin_t * sin_p * cos_p
        y[6] = 0.5 * (3.0 * (sin_p ** 2) - 1.0)
        y[7] = math.sqrt(3.0) * cos_t * sin_p * cos_p
        y[8] = 0.5 * math.sqrt(3.0) * ((cos_t ** 2) - (sin_t ** 2)) * (cos_p ** 2)

        channels = [[round(s * y[c], 6) for s in signal] for c in range(9)]
        return channels

    @classmethod
    def decode_to_loudspeakers(
        cls,
        hoa_channels: List[List[float]],
        speaker_angles_deg: List[float],
    ) -> List[List[float]]:
        """Decodes HOA channels to loudspeaker feeds at specified azimuth angles."""
        num_spk = len(speaker_angles_deg)
        n_samples = len(hoa_channels[0]) if hoa_channels else 0
        spk_feeds = [[0.0] * n_samples for _ in range(num_spk)]

        for spk_idx, ang in enumerate(speaker_angles_deg):
            theta = math.radians(ang)
            cos_t, sin_t = math.cos(theta), math.sin(theta)
            # Re-compute harmonics for speaker direction
            weights = [
                1.0 / num_spk,
                (sin_t) / num_spk,
                0.0,
                (cos_t) / num_spk,
                (math.sqrt(3.0) * sin_t * cos_t) / num_spk,
                0.0,
                (-0.5) / num_spk,
                0.0,
                (0.5 * math.sqrt(3.0) * ((cos_t ** 2) - (sin_t ** 2))) / num_spk,
            ]
            for i in range(n_samples):
                val = sum(hoa_channels[c][i] * weights[c] for c in range(min(9, len(hoa_channels))))
                spk_feeds[spk_idx][i] = round(val, 5)

        return spk_feeds


class AcousticRaytracer:
    """Image-source method for rectangular shoe-box acoustic room impulse response (RIR)."""

    SPEED_OF_SOUND = 343.0  # m/s

    @classmethod
    def generate_rir(
        cls,
        room_dims: Tuple[float, float, float],
        source_pos: Tuple[float, float, float],
        listener_pos: Tuple[float, float, float],
        absorption: Tuple[float, float, float] = (0.2, 0.2, 0.2),
        max_order: int = 2,
        sample_rate: int = 44100,
        duration_sec: float = 0.1,
    ) -> List[float]:
        """Synthesizes discrete room impulse response vector."""
        lx, ly, lz = room_dims
        xs, ys, zs = source_pos
        xl, yl, zl = listener_pos
        ax, ay, az = absorption

        rx = math.sqrt(max(0.0, 1.0 - ax))
        ry = math.sqrt(max(0.0, 1.0 - ay))
        rz = math.sqrt(max(0.0, 1.0 - az))

        num_samples = int(duration_sec * sample_rate)
        rir = [0.0] * num_samples

        for nx in range(-max_order, max_order + 1):
            for ny in range(-max_order, max_order + 1):
                for nz in range(-max_order, max_order + 1):
                    # Image source position
                    ix = nx * lx + (-xs if (nx % 2 != 0) else xs)
                    iy = ny * ly + (-ys if (ny % 2 != 0) else ys)
                    iz = nz * lz + (-zs if (nz % 2 != 0) else zs)

                    dx = ix - xl
                    dy = iy - yl
                    dz = iz - zl
                    dist = math.sqrt(dx * dx + dy * dy + dz * dz)
                    if dist < 0.05:
                        continue

                    delay_sec = dist / cls.SPEED_OF_SOUND
                    sample_idx = int(round(delay_sec * sample_rate))

                    if 0 <= sample_idx < num_samples:
                        # Attenuation: 1/dist * reflection loss
                        attenuation = (1.0 / dist) * (rx ** abs(nx)) * (ry ** abs(ny)) * (rz ** abs(nz))
                        rir[sample_idx] += round(attenuation, 6)

        # Normalize peak
        peak = max(abs(s) for s in rir) if rir else 1.0
        if peak > 0.0:
            rir = [round(s / peak, 5) for s in rir]

        return rir


class HRTFConvolution:
    """Synthetic Head-Related Transfer Function spatial binaural filtering."""

    @classmethod
    def spatialize(
        cls,
        signal: List[float],
        azimuth_deg: float,
        elevation_deg: float = 0.0,
        sample_rate: int = 44100,
    ) -> Tuple[List[float], List[float]]:
        """Convolves mono sound with synthetic spherical head HRTF."""
        c = 343.0
        head_radius = 0.0875  # 8.75 cm
        theta = math.radians(azimuth_deg % 360)
        if theta > math.pi:
            theta -= 2.0 * math.pi

        abs_theta = abs(theta)
        # Woodworth formula for ITD
        if abs_theta <= math.pi / 2.0:
            itd = (head_radius / c) * (abs_theta + math.sin(abs_theta))
        else:
            itd = (head_radius / c) * (math.pi - abs_theta + math.sin(abs_theta))

        delay_samples = itd * sample_rate
        int_delay = int(round(delay_samples))

        # ILD attenuation factor
        far_gain = max(0.2, 0.5 + 0.5 * math.cos(abs_theta))

        n = len(signal)
        left = [0.0] * n
        right = [0.0] * n

        if theta >= 0.0:
            # Sound from right: right ear direct, left ear delayed and shadowed
            right = list(signal)
            for i in range(n):
                src = i - int_delay
                if src >= 0:
                    left[i] = round(signal[src] * far_gain, 5)
        else:
            # Sound from left: left ear direct, right ear delayed and shadowed
            left = list(signal)
            for i in range(n):
                src = i - int_delay
                if src >= 0:
                    right[i] = round(signal[src] * far_gain, 5)

        return left, right


def spatial_audio_hoa_encode(signal: List[float], azimuth_deg: float, elevation_deg: float = 0.0) -> List[List[float]]:
    """Encodes mono signal to 2nd-order Ambisonics (9 channels)."""
    return HigherOrderAmbisonics.encode_2nd_order(signal, azimuth_deg, elevation_deg)


def spatial_audio_room_impulse_response(
    room_dims: Tuple[float, float, float],
    source_pos: Tuple[float, float, float],
    listener_pos: Tuple[float, float, float],
    duration_sec: float = 0.1,
) -> List[float]:
    """Calculates acoustic room impulse response using image source raytracing."""
    return AcousticRaytracer.generate_rir(room_dims, source_pos, listener_pos, duration_sec=duration_sec)


def spatial_audio_hrtf_binaural(signal: List[float], azimuth_deg: float, elevation_deg: float = 0.0) -> Tuple[List[float], List[float]]:
    """Spatially renders mono signal to binaural stereo via synthetic HRTF."""
    return HRTFConvolution.spatialize(signal, azimuth_deg, elevation_deg)


# ==============================================================================
# VECTOR BASE AMPLITUDE PANNING (VBAP) & ATMOSPHERIC ATTENUATION
# ==============================================================================

class VectorBaseAmplitudePanning:
    """Calculates normalized loudspeaker gains for arbitrary 2D/3D speaker layouts."""

    @staticmethod
    def pan_2d(
        source_azimuth_deg: float,
        speaker_angles_deg: List[float],
    ) -> List[float]:
        """Calculates normalized VBAP gains for circular speaker array."""
        num_spk = len(speaker_angles_deg)
        if num_spk == 0:
            return []
        if num_spk == 1:
            return [1.0]

        theta = math.radians(source_azimuth_deg % 360)
        spk_rads = [math.radians(a % 360) for a in speaker_angles_deg]

        # Find adjacent speaker pair enclosing source angle
        spk_indices = list(range(num_spk))
        # Sort speakers by angle
        sorted_pairs = sorted(zip(spk_rads, spk_indices))
        s_rads = [p[0] for p in sorted_pairs]
        s_idxs = [p[1] for p in sorted_pairs]

        p1_idx = s_idxs[-1]
        p2_idx = s_idxs[0]

        for i in range(num_spk):
            ang1 = s_rads[i]
            ang2 = s_rads[(i + 1) % num_spk]
            if ang2 < ang1:
                # Wrap-around across 0
                if theta >= ang1 or theta <= ang2:
                    p1_idx = s_idxs[i]
                    p2_idx = s_idxs[(i + 1) % num_spk]
                    break
            else:
                if ang1 <= theta <= ang2:
                    p1_idx = s_idxs[i]
                    p2_idx = s_idxs[(i + 1) % num_spk]
                    break

        v_source = [math.cos(theta), math.sin(theta)]
        ang_p1 = math.radians(speaker_angles_deg[p1_idx])
        ang_p2 = math.radians(speaker_angles_deg[p2_idx])
        l1 = [math.cos(ang_p1), math.sin(ang_p1)]
        l2 = [math.cos(ang_p2), math.sin(ang_p2)]

        # Invert 2x2 matrix [l1 l2]
        det = l1[0] * l2[1] - l1[1] * l2[0]
        if abs(det) < 1e-9:
            g1, g2 = 0.5, 0.5
        else:
            g1 = (l2[1] * v_source[0] - l2[0] * v_source[1]) / det
            g2 = (-l1[1] * v_source[0] + l1[0] * v_source[1]) / det

        g1 = max(0.0, g1)
        g2 = max(0.0, g2)
        norm = math.sqrt(g1 * g1 + g2 * g2)
        if norm > 1e-9:
            g1 /= norm
            g2 /= norm

        gains = [0.0] * num_spk
        gains[p1_idx] = round(g1, 4)
        gains[p2_idx] = round(g2, 4)
        return gains


class AtmosphericAttenuation:
    """Distance-dependent inverse square law attenuation and frequency-dependent air damping."""

    SPEED_OF_SOUND = 343.0

    @classmethod
    def apply(
        cls,
        signal: List[float],
        distance_meters: float,
        ref_distance: float = 1.0,
        rolloff_factor: float = 1.0,
        air_absorption_db_per_km: float = 10.0,
        sample_rate: int = 44100,
    ) -> List[float]:
        """Attenuates signal by distance and high-frequency atmospheric absorption."""
        d = max(0.1, float(distance_meters))
        d_ref = max(0.1, float(ref_distance))

        # Geometric distance attenuation (Inverse Distance Law)
        geom_gain = d_ref / (d_ref + rolloff_factor * (d - d_ref))
        geom_gain = max(0.0, min(1.0, geom_gain))

        # Atmospheric air absorption (dB loss -> linear)
        dist_km = d / 1000.0
        loss_db = air_absorption_db_per_km * dist_km
        abs_gain = 10.0 ** (-loss_db / 20.0)

        # High-frequency damping filter (single-pole IIR)
        # Higher distance -> lower cutoff
        cutoff = max(500.0, 20000.0 / (1.0 + 0.1 * d))
        alpha = (2.0 * math.pi * cutoff / sample_rate) / (2.0 * math.pi * cutoff / sample_rate + 1.0)

        out = []
        prev = 0.0
        total_gain = geom_gain * abs_gain
        for s in signal:
            filtered = prev + alpha * (s - prev)
            prev = filtered
            out.append(round(filtered * total_gain, 6))

        return out


def spatial_audio_vbap_2d(source_azimuth_deg: float, speaker_angles_deg: List[float]) -> List[float]:
    """Calculates 2D VBAP loudspeaker gains."""
    return VectorBaseAmplitudePanning.pan_2d(source_azimuth_deg, speaker_angles_deg)


def spatial_audio_distance_attenuate(
    signal: List[float],
    distance: float,
    ref_distance: float = 1.0,
    rolloff: float = 1.0,
) -> List[float]:
    """Applies distance attenuation and atmospheric air damping."""
    return AtmosphericAttenuation.apply(signal, distance, ref_distance=ref_distance, rolloff_factor=rolloff)


# ==============================================================================
# SHOEBOX ROOM ACOUSTICS & IMPULSE CONVOLUTION
# ==============================================================================

class RoomImageSourceEarlyReflections:
    """Image Source Method (Allen & Berkley) for early room reflection acoustics."""

    SPEED_OF_SOUND = 343.0  # m/s

    @classmethod
    def compute(
        cls,
        room_dims: List[float],
        source_pos: List[float],
        receiver_pos: List[float],
        absorption: float = 0.2,
        max_order: int = 2,
    ) -> Record:
        """Calculates discrete acoustic reflection paths up to max reflection order."""
        Lx, Ly, Lz = float(room_dims[0]), float(room_dims[1]), float(room_dims[2])
        xs, ys, zs = float(source_pos[0]), float(source_pos[1]), float(source_pos[2])
        xr, yr, zr = float(receiver_pos[0]), float(receiver_pos[1]), float(receiver_pos[2])
        alpha = max(0.01, min(0.99, float(absorption)))
        refl_coeff = math.sqrt(1.0 - alpha)
        order = max(1, int(max_order))

        # Direct path
        d_direct = math.sqrt((xs - xr) ** 2 + (ys - yr) ** 2 + (zs - zr) ** 2)
        tau_direct = d_direct / cls.SPEED_OF_SOUND

        arrivals = []

        # Iterate 3D image source grid: n_x, n_y, n_z in [-order, order]
        for nx in range(-order, order + 1):
            for ny in range(-order, order + 1):
                for nz in range(-order, order + 1):
                    # Image source coordinates
                    im_x = (2 * nx * Lx + xs) if (nx % 2 == 0) else (2 * nx * Lx + (2 * Lx - xs))
                    im_y = (2 * ny * Ly + ys) if (ny % 2 == 0) else (2 * ny * Ly + (2 * Ly - ys))
                    im_z = (2 * nz * Lz + zs) if (nz % 2 == 0) else (2 * nz * Lz + (2 * Lz - zs))

                    dist = math.sqrt((im_x - xr) ** 2 + (im_y - yr) ** 2 + (im_z - zr) ** 2)
                    delay_sec = dist / cls.SPEED_OF_SOUND
                    reflections = abs(nx) + abs(ny) + abs(nz)

                    if reflections > order:
                        continue

                    amplitude = (refl_coeff ** reflections) / max(0.1, dist)

                    arrivals.append({
                        "order": reflections,
                        "delay_ms": round(delay_sec * 1000.0, 3),
                        "distance_m": round(dist, 4),
                        "amplitude": round(amplitude, 6),
                    })

        # Sort arrivals by arrival time
        arrivals.sort(key=lambda a: a["delay_ms"])

        # Sabine reverberation time approximation: RT60 = 0.161 * V / A
        volume = Lx * Ly * Lz
        total_surface = 2.0 * (Lx * Ly + Ly * Lz + Lx * Lz)
        total_absorption = total_surface * alpha
        rt60_sabine = 0.161 * volume / max(1e-3, total_absorption)

        return Record({
            "reflections_count": len(arrivals),
            "direct_sound_delay_ms": round(tau_direct * 1000.0, 3),
            "early_arrivals": arrivals[:20],
            "rt60_sabine_sec": round(rt60_sabine, 4),
            "room_volume_m3": round(volume, 2),
        })


class ConvolveImpulseResponse:
    """Time-domain overlap-add FIR impulse response convolver."""

    @classmethod
    def convolve(
        cls,
        signal: List[float],
        ir: List[float],
    ) -> Record:
        """Convolves discrete audio signal with acoustic impulse response."""
        n = len(signal)
        m = len(ir)
        if n == 0 or m == 0:
            return Record({"convolved": [], "length": 0, "peak_amplitude": 0.0})

        out_len = n + m - 1
        out = [0.0] * out_len

        for i in range(n):
            si = signal[i]
            if abs(si) < 1e-12:
                continue
            for j in range(m):
                out[i + j] += si * ir[j]

        peak = max(abs(v) for v in out) if out else 0.0

        return Record({
            "convolved": [round(v, 6) for v in out],
            "num_samples": out_len,
            "peak_amplitude": round(peak, 6),
        })


def spatial_audio_early_reflections(
    room_dims: List[float],
    source_pos: List[float],
    receiver_pos: List[float],
    absorption: float = 0.2,
    max_order: int = 2,
) -> Record:
    """Calculates image-source room acoustic reflections."""
    return RoomImageSourceEarlyReflections.compute(
        room_dims, source_pos, receiver_pos, absorption=absorption, max_order=max_order
    )


def spatial_audio_convolve_ir(
    signal: List[float],
    ir: List[float],
) -> Record:
    """Convolves audio signal with impulse response."""
    return ConvolveImpulseResponse.convolve(signal, ir)


