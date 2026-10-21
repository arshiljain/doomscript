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
from doomscript.core.record import Record


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


# ==============================================================================
# HIGHER-ORDER SPHERICAL HARMONICS 3D (HOA) ENCODER
# ==============================================================================

class HigherOrderSphericalHarmonics3D:
    """Higher-Order Ambisonics 3D spherical harmonics encoder with ACN sorting and N3D/SN3D."""

    @staticmethod
    def _legendre_polynomials(l_max: int, x: float) -> Dict[Tuple[int, int], float]:
        """Calculates associated Legendre polynomials P_l^m(x) via stable recurrence."""
        p: Dict[Tuple[int, int], float] = {}
        # Base case P_0^0 = 1
        p[(0, 0)] = 1.0
        if l_max == 0:
            return p

        # P_m^m(x) = (-1)^m * (2m - 1)!! * (1 - x^2)^(m/2)
        somx2 = math.sqrt(max(0.0, 1.0 - x * x))
        fact = 1.0
        for m in range(1, l_max + 1):
            fact *= (2.0 * m - 1.0)
            val = fact * (somx2 ** m)
            if m % 2 != 0:
                val = -val
            p[(m, m)] = val

        # P_{m+1}^m(x) = x * (2m + 1) * P_m^m(x)
        for m in range(l_max):
            p[(m + 1, m)] = x * (2.0 * m + 1.0) * p[(m, m)]

        # Recurrence for l > m + 1:
        # (l - m) P_l^m(x) = x (2l - 1) P_{l-1}^m(x) - (l + m - 1) P_{l-2}^m(x)
        for m in range(l_max + 1):
            for l in range(m + 2, l_max + 1):
                num = x * (2.0 * l - 1.0) * p[(l - 1, m)] - (l + m - 1.0) * p[(l - 2, m)]
                p[(l, m)] = num / (l - m)

        return p

    @classmethod
    def encode_direction(
        cls,
        azimuth_deg: float,
        elevation_deg: float,
        order: int = 2,
        normalization: str = "N3D",
    ) -> Dict[str, Any]:
        """Encodes 3D direction (azimuth phi, elevation theta) into HOA spherical harmonics weights."""
        l_max = max(0, min(3, int(order)))
        phi = math.radians(azimuth_deg % 360.0)
        theta = math.radians(max(-90.0, min(90.0, elevation_deg)))

        # x = sin(elevation)
        x = math.sin(theta)
        leg = cls._legendre_polynomials(l_max, x)

        acn_channels = []
        n_channels = (l_max + 1) ** 2

        for l in range(l_max + 1):
            for m in range(-l, l + 1):
                acn = l * l + l + m
                abs_m = abs(m)

                # Normalization constant N_l^m
                # N3D: sqrt( (2l + 1) * (l - |m|)! / (l + |m|)! )
                fact_ratio = math.factorial(l - abs_m) / math.factorial(l + abs_m)
                if normalization.upper() == "N3D":
                    norm_k = math.sqrt((2.0 * l + 1.0) * fact_ratio)
                else:  # SN3D
                    norm_k = math.sqrt(fact_ratio)

                p_val = leg[(l, abs_m)]

                if m > 0:
                    y_lm = math.sqrt(2.0) * norm_k * p_val * math.cos(m * phi)
                elif m < 0:
                    y_lm = math.sqrt(2.0) * norm_k * p_val * math.sin(abs_m * phi)
                else:
                    y_lm = norm_k * p_val

                acn_channels.append({
                    "acn": acn,
                    "order_l": l,
                    "degree_m": m,
                    "weight": round(y_lm, 6),
                })

        return {
            "order": l_max,
            "normalization": normalization.upper(),
            "channels_count": n_channels,
            "azimuth_deg": azimuth_deg,
            "elevation_deg": elevation_deg,
            "channels": [Record(ch) for ch in acn_channels],
        }


# ==============================================================================
# ACOUSTIC RAY TRACING & REVERBERATION TIME (RT60) SOLVER
# ==============================================================================

class AcousticRayTracingShoebox:
    """Stochastic Monte Carlo ray-tracing room acoustics and Sabine/Eyring RT60 estimation."""

    SPEED_OF_SOUND = 343.0  # m/s

    @classmethod
    def simulate(
        cls,
        room_dimensions_m: List[float],
        source_pos_m: List[float],
        receiver_pos_m: List[float],
        absorption_coeff: float = 0.15,
        num_rays: int = 60,
        max_bounces: int = 8,
    ) -> Dict[str, Any]:
        lx, ly, lz = [float(v) for v in room_dimensions_m]
        sx, sy, sz = [float(v) for v in source_pos_m]
        rx, ry, rz = [float(v) for v in receiver_pos_m]
        alpha = max(0.01, min(0.99, float(absorption_coeff)))

        # Sabine and Eyring RT60 formulas
        volume = lx * ly * lz
        surface_area = 2.0 * (lx * ly + ly * lz + lz * lx)
        rt60_sabine = 0.161 * volume / (surface_area * alpha)
        rt60_eyring = 0.161 * volume / (-surface_area * math.log(1.0 - alpha))

        # Direct sound distance and time of flight
        direct_dist = math.sqrt((rx - sx) ** 2 + (ry - sy) ** 2 + (rz - sz) ** 2)
        direct_tof_ms = (direct_dist / cls.SPEED_OF_SOUND) * 1000.0

        # Receiver detection radius
        receiver_radius = 0.8  # m

        detections = []
        n_rays = max(10, int(num_rays))

        for ray_idx in range(n_rays):
            # Uniform spherical distribution on sphere (Fibonacci lattice)
            theta = math.acos(1.0 - 2.0 * (ray_idx + 0.5) / n_rays)
            phi = math.pi * (1.0 + 5.0 ** 0.5) * ray_idx

            dx = math.sin(theta) * math.cos(phi)
            dy = math.sin(theta) * math.sin(phi)
            dz = math.cos(theta)

            px, py, pz = sx, sy, sz
            energy = 1.0
            total_dist = 0.0

            for bounce in range(max_bounces):
                # Find collision with closest room boundary plane
                # x in {0, lx}, y in {0, ly}, z in {0, lz}
                t_candidates = []
                if dx > 1e-6:
                    t_candidates.append(((lx - px) / dx, "x_max"))
                elif dx < -1e-6:
                    t_candidates.append((-px / dx, "x_min"))

                if dy > 1e-6:
                    t_candidates.append(((ly - py) / dy, "y_max"))
                elif dy < -1e-6:
                    t_candidates.append((-py / dy, "y_min"))

                if dz > 1e-6:
                    t_candidates.append(((lz - pz) / dz, "z_max"))
                elif dz < -1e-6:
                    t_candidates.append((-pz / dz, "z_min"))

                if not t_candidates:
                    break

                t_hit, plane = min(t_candidates, key=lambda item: item[0])

                # Check if ray segment intersects receiver sphere
                # Vector from p to receiver
                vx, vy, vz = rx - px, ry - py, rz - pz
                t_proj = vx * dx + vy * dy + vz * dz
                if 0 < t_proj < t_hit:
                    # Closest distance to receiver
                    perp_sq = (vx * vx + vy * vy + vz * vz) - (t_proj * t_proj)
                    if perp_sq < (receiver_radius * receiver_radius):
                        hit_dist = total_dist + t_proj
                        detections.append({
                            "arrival_time_ms": round((hit_dist / cls.SPEED_OF_SOUND) * 1000.0, 2),
                            "energy": round(energy, 6),
                            "bounce_order": bounce,
                        })

                # Advance ray to wall
                px += t_hit * dx
                py += t_hit * dy
                pz += t_hit * dz
                total_dist += t_hit

                # Specular reflection
                if "x" in plane:
                    dx = -dx
                elif "y" in plane:
                    dy = -dy
                elif "z" in plane:
                    dz = -dz

                # Absorb energy
                energy *= (1.0 - alpha)

        detections.sort(key=lambda d: d["arrival_time_ms"])

        return {
            "room_volume_m3": round(volume, 2),
            "surface_area_m2": round(surface_area, 2),
            "rt60_sabine_sec": round(rt60_sabine, 3),
            "rt60_eyring_sec": round(rt60_eyring, 3),
            "direct_tof_ms": round(direct_tof_ms, 2),
            "detected_reflections_count": len(detections),
            "early_reflections": [Record(d) for d in detections[:10]],
        }


def spatial_audio_spherical_harmonics_encode(
    azimuth_deg: float,
    elevation_deg: float,
    order: int = 2,
    normalization: str = "N3D",
) -> Record:
    """Encodes 3D audio source into Higher-Order Ambisonics spherical harmonics."""
    return Record(HigherOrderSphericalHarmonics3D.encode_direction(
        azimuth_deg, elevation_deg, order=order, normalization=normalization
    ))


def spatial_audio_ray_trace_room(
    room_dims: List[float],
    source_pos: List[float],
    receiver_pos: List[float],
    absorption: float = 0.15,
    num_rays: int = 60,
) -> Record:
    """Performs stochastic Monte Carlo acoustic ray-tracing and estimates RT60."""
    return Record(AcousticRayTracingShoebox.simulate(
        room_dims, source_pos, receiver_pos, absorption_coeff=absorption, num_rays=num_rays
    ))


# ==============================================================================
# BINAURAL ROOM IMPULSE RESPONSE (BRIR) GENERATOR & AMBISONICS B-FORMAT DECODER
# ==============================================================================


class BinauralRoomImpulseResponseBRIRGenerator:
    """Synthesizes Left & Right Binaural Room Impulse Responses (BRIR).

    Combines Allen & Berkley 3D Image Source Method (ISM) for room boundary reflections
    with Woodworth-Schlosser spherical head diffraction for Interaural Time Difference (ITD)
    and frequency-dependent head shadow Interaural Level Difference (ILD).
    """

    SPEED_OF_SOUND = 343.0  # m/s

    @classmethod
    def generate(
        cls,
        room_dims: List[float],
        source_pos: List[float],
        listener_pos: List[float],
        max_order: int = 2,
        absorption: float = 0.2,
        sample_rate: int = 16000,
        head_radius: float = 0.0875,
    ) -> Dict[str, Any]:
        """Generates left and right impulse response buffers from room acoustics."""
        lx, ly, lz = room_dims
        sx, sy, sz = source_pos
        rx, ry, rz = listener_pos

        c = cls.SPEED_OF_SOUND
        refl_coeff = math.sqrt(max(0.0, 1.0 - absorption))

        # Direct distance and ITD
        dx_dir = sx - rx
        dy_dir = sy - ry
        dz_dir = sz - rz
        d_direct = math.sqrt(dx_dir * dx_dir + dy_dir * dy_dir + dz_dir * dz_dir)
        direct_tof = d_direct / c

        # Determine buffer length based on max reflection distance
        max_dist = math.sqrt(
            ((2 * max_order + 1) * lx) ** 2
            + ((2 * max_order + 1) * ly) ** 2
            + ((2 * max_order + 1) * lz) ** 2
        )
        max_time = (max_dist / c) + 0.02
        buffer_len = int(math.ceil(max_time * sample_rate))
        buffer_len = min(max(buffer_len, int(direct_tof * sample_rate) + 64), 8192)

        brir_l = [0.0] * buffer_len
        brir_r = [0.0] * buffer_len

        reflections_count = 0

        # Traverse image sources in 3D grid
        for mx in range(-max_order, max_order + 1):
            for my in range(-max_order, max_order + 1):
                for mz in range(-max_order, max_order + 1):
                    for px in (0, 1):
                        for py in (0, 1):
                            for pz in (0, 1):
                                order = abs(2 * mx - px) + abs(2 * my - py) + abs(2 * mz - pz)
                                if order > max_order:
                                    continue

                                # Image source position
                                ix = 2.0 * mx * lx + (sx if px == 0 else -sx)
                                iy = 2.0 * my * ly + (sy if py == 0 else -sy)
                                iz = 2.0 * mz * lz + (sz if pz == 0 else -sz)

                                vx = ix - rx
                                vy = iy - ry
                                vz = iz - rz
                                dist = math.sqrt(vx * vx + vy * vy + vz * vz)
                                if dist < 1e-4:
                                    continue

                                tof = dist / c
                                amp = (refl_coeff ** order) / max(0.5, dist)

                                # Azimuth angle relative to listener (listener faces +X axis)
                                theta = math.atan2(vy, vx)  # in [-pi, pi]

                                # Woodworth formula for ITD: delta_t = (a/c) * (theta + sin(theta))
                                # Positive theta is on listener's left
                                sin_th = math.sin(theta)
                                if abs(theta) <= math.pi / 2.0:
                                    delta_itd = (head_radius / c) * (theta + sin_th)
                                else:
                                    # Behind listener
                                    th_abs = abs(theta)
                                    delta_itd = (head_radius / c) * (math.pi - th_abs + math.sin(th_abs))
                                    if theta < 0:
                                        delta_itd = -delta_itd

                                # Left ear arrives earlier if theta > 0
                                t_l = tof - 0.5 * delta_itd
                                t_r = tof + 0.5 * delta_itd

                                # Head shadow ILD approximation
                                g_l = amp * (1.0 + 0.5 * math.sin(theta))
                                g_r = amp * (1.0 - 0.5 * math.sin(theta))

                                # Sinc/fractional-delay impulse accumulation
                                idx_l = int(round(t_l * sample_rate))
                                idx_r = int(round(t_r * sample_rate))

                                if 0 <= idx_l < buffer_len:
                                    brir_l[idx_l] += g_l
                                if 0 <= idx_r < buffer_len:
                                    brir_r[idx_r] += g_r

                                reflections_count += 1

        # Direct azimuth and ITD
        dir_theta = math.atan2(dy_dir, dx_dir)
        direct_itd_us = abs((head_radius / c) * (dir_theta + math.sin(dir_theta))) * 1e6

        return {
            "brir_left": [round(x, 5) for x in brir_l],
            "brir_right": [round(x, 5) for x in brir_r],
            "direct_delay_ms": round(direct_tof * 1000.0, 2),
            "direct_itd_microseconds": round(direct_itd_us, 1),
            "reflections_count": reflections_count,
            "buffer_length": buffer_len,
            "sample_rate": sample_rate,
        }


class AmbisonicsBFormatBinauralDecoder:
    """Binaural Decoder for First-Order Ambisonics (B-Format: W, X, Y, Z).

    Decodes spherical harmonics into 8 virtual loudspeakers located on a cube sphere,
    then applies head diffraction and interaural delays to produce headphone binaural stereo.
    """

    # 8 Virtual Loudspeaker coordinates: (azimuth_deg, elevation_deg) on cube vertices
    # Azimuth: +/- 45 deg, +/- 135 deg; Elevation: +/- 35.26 deg
    VIRTUAL_SPEAKERS_8 = [
        (45.0, 35.26),
        (135.0, 35.26),
        (-135.0, 35.26),
        (-45.0, 35.26),
        (45.0, -35.26),
        (135.0, -35.26),
        (-135.0, -35.26),
        (-45.0, -35.26),
    ]

    @classmethod
    def decode(
        cls,
        w_channel: List[float],
        x_channel: List[float],
        y_channel: List[float],
        z_channel: List[float],
        num_virtual_speakers: int = 8,
    ) -> Dict[str, Any]:
        """Decodes B-format streams into left and right binaural signals."""
        n = min(len(w_channel), len(x_channel), len(y_channel), len(z_channel))
        if n == 0:
            return {"left_channel": [], "right_channel": [], "num_samples": 0}

        speakers = cls.VIRTUAL_SPEAKERS_8[:num_virtual_speakers]
        m = len(speakers)

        # Decoding weights for each virtual speaker k:
        # S_k = (1 / sqrt(2)) * W + cos(el)*cos(az)*X + cos(el)*sin(az)*Y + sin(el)*Z
        speaker_feeds = [[0.0] * n for _ in range(m)]

        for k, (az_deg, el_deg) in enumerate(speakers):
            az = math.radians(az_deg)
            el = math.radians(el_deg)

            w_w = 1.0 / math.sqrt(2.0)
            w_x = math.cos(el) * math.cos(az)
            w_y = math.cos(el) * math.sin(az)
            w_z = math.sin(el)

            norm = 1.0 / math.sqrt(w_w * w_w + w_x * w_x + w_y * w_y + w_z * w_z)
            w_w *= norm
            w_x *= norm
            w_y *= norm
            w_z *= norm

            for t in range(n):
                speaker_feeds[k][t] = (
                    w_w * w_channel[t]
                    + w_x * x_channel[t]
                    + w_y * y_channel[t]
                    + w_z * z_channel[t]
                )

        # Virtual speaker to binaural summing with simple pinna/head weighting
        out_left = [0.0] * n
        out_right = [0.0] * n

        for k, (az_deg, _) in enumerate(speakers):
            az = math.radians(az_deg)
            # Left ear gain higher for positive azimuth (left hemisphere)
            g_left = (1.0 + math.sin(az)) * 0.5
            g_right = (1.0 - math.sin(az)) * 0.5

            for t in range(n):
                feed = speaker_feeds[k][t]
                out_left[t] += feed * g_left
                out_right[t] += feed * g_right

        # Normalization
        norm_factor = 1.0 / max(1.0, math.sqrt(float(m)))
        out_left = [round(x * norm_factor, 5) for x in out_left]
        out_right = [round(x * norm_factor, 5) for x in out_right]

        return {
            "left_channel": out_left,
            "right_channel": out_right,
            "num_samples": n,
            "num_virtual_speakers": m,
        }


def spatial_generate_brir(
    room_dims: List[float],
    source_pos: List[float],
    listener_pos: List[float],
    max_order: int = 2,
    absorption: float = 0.2,
    sample_rate: int = 16000,
) -> Record:
    """Generates Binaural Room Impulse Responses (BRIR) using Image Source Method."""
    return Record(
        BinauralRoomImpulseResponseBRIRGenerator.generate(
            room_dims,
            source_pos,
            listener_pos,
            max_order=max_order,
            absorption=absorption,
            sample_rate=sample_rate,
        )
    )


def spatial_ambisonics_binaural_decode(
    w_channel: List[float],
    x_channel: List[float],
    y_channel: List[float],
    z_channel: List[float],
    num_virtual_speakers: int = 8,
) -> Record:
    """Decodes Ambisonics B-format signals to headphone binaural stereo."""
    return Record(
        AmbisonicsBFormatBinauralDecoder.decode(
            w_channel,
            x_channel,
            y_channel,
            z_channel,
            num_virtual_speakers=num_virtual_speakers,
        )
    )






# ==============================================================================
# ACOUSTIC SPATIALIZATION: MOORER REVERB NETWORK & OCCLUSION ATTENUATION
# ==============================================================================

class MoorerReverberationNetwork:
    """Moorer artificial reverberation model with parallel lowpass-feedback comb filters and allpass diffusor."""

    @classmethod
    def process(
        cls,
        samples: List[float],
        sample_rate: int = 44100,
        comb_delays_ms: Optional[List[float]] = None,
        feedback: float = 0.75,
        damping: float = 0.25,
    ) -> List[float]:
        delays_ms = comb_delays_ms or [29.7, 37.1, 41.1, 43.7]
        delays = [max(1, int(d_ms * sample_rate / 1000.0)) for d_ms in delays_ms]
        n = len(samples)

        # Parallel lowpass feedback comb filters
        comb_outputs = [0.0] * n
        for d in delays:
            buf = [0.0] * d
            lp_state = 0.0
            for i in range(n):
                delayed = buf[i % d]
                # Lowpass filter in feedback loop
                lp_state = delayed * (1.0 - damping) + lp_state * damping
                feed = samples[i] + lp_state * feedback
                buf[i % d] = feed
                comb_outputs[i] += delayed

        # Scale down sum
        scale = 1.0 / len(delays)
        out = [comb_outputs[i] * scale for i in range(n)]

        # All-pass filter stage for diffusion
        ap_delay = max(1, int(5.0 * sample_rate / 1000.0))
        ap_buf = [0.0] * ap_delay
        ap_g = 0.7
        wet = [0.0] * n
        for i in range(n):
            delayed = ap_buf[i % ap_delay]
            inp = out[i]
            val = -ap_g * inp + delayed
            ap_buf[i % ap_delay] = inp + ap_g * val
            wet[i] = val

        return wet


class SoundOcclusionObstruction:
    """Frequency-dependent acoustic transmission loss for occluded and obstructed sound sources."""

    @classmethod
    def apply_occlusion(cls, samples: List[float], wall_thickness_meters: float = 0.2, material_density: str = "concrete") -> List[float]:
        # Transmission loss cutoff frequency
        cutoffs = {"concrete": 0.05, "wood": 0.2, "glass": 0.15, "drywall": 0.3}
        alpha = cutoffs.get(material_density.lower(), 0.1)
        # Apply IIR 1st order lowpass filter: y[i] = y[i-1] * (1-alpha) + x[i] * alpha
        out = [0.0] * len(samples)
        state = 0.0
        attenuation = max(0.05, 1.0 - wall_thickness_meters * 1.5)
        for i in range(len(samples)):
            state = state * (1.0 - alpha) + samples[i] * alpha
            out[i] = state * attenuation
        return out


def spatial_audio_moorer_reverb(samples: List[float], sample_rate: int = 44100, feedback: float = 0.7) -> List[float]:
    """Applies Moorer reverberation algorithm with lowpass feedback comb filters."""
    return MoorerReverberationNetwork.process(samples, sample_rate=sample_rate, feedback=feedback)


def spatial_audio_occlusion(samples: List[float], wall_thickness: float = 0.2, material: str = "concrete") -> List[float]:
    """Applies acoustic wall occlusion low-pass transmission filter."""
    return SoundOcclusionObstruction.apply_occlusion(samples, wall_thickness_meters=wall_thickness, material_density=material)
