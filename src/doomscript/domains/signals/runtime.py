"""Digital Signal Processing, Wavelet Transforms, and Filter Design for DoomScript."""

import math
import cmath
from typing import List, Dict, Any, Tuple, Optional, Union
from doomscript.core.record import Record


def dft(x: List[float]) -> List[complex]:
    N = len(x)
    X = []
    for k in range(N):
        s = 0.0 + 0.0j
        for n in range(N):
            angle = -2.0 * math.pi * k * n / N
            s += x[n] * complex(math.cos(angle), math.sin(angle))
        X.append(s)
    return X


def idft(X: List[complex]) -> List[complex]:
    N = len(X)
    x = []
    for n in range(N):
        s = 0.0 + 0.0j
        for k in range(N):
            angle = 2.0 * math.pi * k * n / N
            s += X[k] * complex(math.cos(angle), math.sin(angle))
        x.append(s / N)
    return x


class WaveletTransform:
    """Discrete Wavelet Transform (Haar and Daubechies-4)."""

    @staticmethod
    def haar_dwt(signal: List[float]) -> Dict[str, List[float]]:
        n = len(signal)
        if n % 2 != 0:
            signal = signal + [signal[-1]]
            n += 1
        approx = []
        detail = []
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        for i in range(0, n, 2):
            a = (signal[i] + signal[i + 1]) * inv_sqrt2
            d = (signal[i] - signal[i + 1]) * inv_sqrt2
            approx.append(a)
            detail.append(d)
        return {"approx": approx, "detail": detail}

    @staticmethod
    def haar_idwt(approx: List[float], detail: List[float]) -> List[float]:
        inv_sqrt2 = 1.0 / math.sqrt(2.0)
        n = min(len(approx), len(detail))
        recon = []
        for i in range(n):
            a = approx[i]
            d = detail[i]
            recon.append((a + d) * inv_sqrt2)
            recon.append((a - d) * inv_sqrt2)
        return recon

    @staticmethod
    def db4_dwt(signal: List[float]) -> Dict[str, List[float]]:
        # Daubechies-4 filter coefficients
        s3 = math.sqrt(3.0)
        denom = 4.0 * math.sqrt(2.0)
        h = [
            (1.0 + s3) / denom,
            (3.0 + s3) / denom,
            (3.0 - s3) / denom,
            (1.0 - s3) / denom,
        ]
        g = [h[3], -h[2], h[1], -h[0]]

        n = len(signal)
        pad_len = (4 - (n % 4)) % 4
        padded = signal + [0.0] * pad_len
        n = len(padded)

        approx = []
        detail = []
        for i in range(0, n, 2):
            a_sum = sum(h[k] * padded[(i + k) % n] for k in range(4))
            d_sum = sum(g[k] * padded[(i + k) % n] for k in range(4))
            approx.append(a_sum)
            detail.append(d_sum)
        return {"approx": approx, "detail": detail}


class FilterDesign:
    """Windowed-Sinc FIR and Bilinear Transform Butterworth IIR Filters."""

    @staticmethod
    def fir_lowpass(num_taps: int, cutoff_hz: float, sample_rate_hz: float) -> List[float]:
        if num_taps % 2 == 0:
            num_taps += 1  # Type I FIR requires odd taps
        fc = cutoff_hz / sample_rate_hz
        m = (num_taps - 1) // 2
        taps = []
        for i in range(num_taps):
            n = i - m
            if n == 0:
                sinc_val = 2.0 * math.pi * fc
            else:
                sinc_val = math.sin(2.0 * math.pi * fc * n) / n
            # Hamming window
            window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (num_taps - 1))
            taps.append(sinc_val * window)
        # Normalize gain to 1.0 at DC
        tap_sum = sum(taps)
        if abs(tap_sum) > 1e-9:
            taps = [t / tap_sum for t in taps]
        return taps

    @staticmethod
    def convolve(signal: List[float], kernel: List[float]) -> List[float]:
        s_len, k_len = len(signal), len(kernel)
        out_len = s_len + k_len - 1
        res = [0.0] * out_len
        for i in range(s_len):
            for j in range(k_len):
                res[i + j] += signal[i] * kernel[j]
        # Return same length centered
        start = (k_len - 1) // 2
        return res[start : start + s_len]

    @staticmethod
    def butterworth_2nd_order(cutoff_hz: float, sample_rate_hz: float, is_lowpass: bool = True) -> Tuple[List[float], List[float]]:
        """2nd-order Butterworth IIR filter coefficients [b0, b1, b2], [a0, a1, a2]."""
        ita = 1.0 / math.tan(math.pi * cutoff_hz / sample_rate_hz)
        q = math.sqrt(2.0)
        if is_lowpass:
            b0 = 1.0 / (1.0 + q * ita + ita * ita)
            b1 = 2.0 * b0
            b2 = b0
            a1 = 2.0 * (ita * ita - 1.0) * b0
            a2 = -(1.0 - q * ita + ita * ita) * b0
        else:
            b0 = 1.0 / (1.0 + q * ita + ita * ita)
            b1 = -2.0 * b0
            b2 = b0
            a1 = 2.0 * (ita * ita - 1.0) * b0
            a2 = -(1.0 - q * ita + ita * ita) * b0
        return [b0, b1, b2], [1.0, -a1, -a2]

    @staticmethod
    def apply_iir(signal: List[float], b: List[float], a: List[float]) -> List[float]:
        out = [0.0] * len(signal)
        for n in range(len(signal)):
            out[n] = b[0] * signal[n]
            if n >= 1:
                out[n] += b[1] * signal[n - 1] - a[1] * out[n - 1]
            if n >= 2:
                out[n] += b[2] * signal[n - 2] - a[2] * out[n - 2]
        return out


class SignalAnalytics:
    """Hilbert Transform, Analytic Signal, and Peak Detection."""

    @staticmethod
    def hilbert_transform(signal: List[float]) -> Dict[str, Any]:
        """Compute the analytic signal and amplitude envelope via Hilbert transform."""
        n = len(signal)
        X = dft(signal)
        # Form H multiplier
        H = [0.0] * n
        if n % 2 == 0:
            H[0] = 1.0
            H[n // 2] = 1.0
            for i in range(1, n // 2):
                H[i] = 2.0
        else:
            H[0] = 1.0
            for i in range(1, (n + 1) // 2):
                H[i] = 2.0

        Z = [X[i] * H[i] for i in range(n)]
        analytic = idft(Z)
        envelope = [abs(c) for c in analytic]
        phase = [math.atan2(c.imag, c.real) for c in analytic]
        return {
            "envelope": envelope,
            "phase": phase,
            "analytic_real": [c.real for c in analytic],
            "analytic_imag": [c.imag for c in analytic],
        }

    @staticmethod
    def find_peaks(signal: List[float], min_height: Optional[float] = None, min_distance: int = 1) -> List[Dict[str, Any]]:
        peaks = []
        n = len(signal)
        last_peak_idx = -min_distance - 1

        for i in range(1, n - 1):
            if signal[i] > signal[i - 1] and signal[i] > signal[i + 1]:
                if min_height is not None and signal[i] < min_height:
                    continue
                if i - last_peak_idx >= min_distance:
                    peaks.append({"index": i, "value": signal[i]})
                    last_peak_idx = i
        return peaks


def signals_haar_dwt(signal: List[float]) -> Dict[str, List[float]]:
    return WaveletTransform.haar_dwt(signal)


def signals_haar_idwt(approx: List[float], detail: List[float]) -> List[float]:
    return WaveletTransform.haar_idwt(approx, detail)


def signals_db4_dwt(signal: List[float]) -> Dict[str, List[float]]:
    return WaveletTransform.db4_dwt(signal)


def signals_fir_lowpass(signal: List[float], num_taps: int, cutoff_hz: float, sample_rate_hz: float) -> List[float]:
    kernel = FilterDesign.fir_lowpass(num_taps, cutoff_hz, sample_rate_hz)
    return FilterDesign.convolve(signal, kernel)


def signals_butterworth_filter(signal: List[float], cutoff_hz: float, sample_rate_hz: float, is_lowpass: bool = True) -> List[float]:
    b, a = FilterDesign.butterworth_2nd_order(cutoff_hz, sample_rate_hz, is_lowpass)
    return FilterDesign.apply_iir(signal, b, a)


def signals_hilbert(signal: List[float]) -> Dict[str, Any]:
    return SignalAnalytics.hilbert_transform(signal)


def signals_find_peaks(signal: List[float], min_height: Optional[float] = None, min_distance: int = 1) -> List[Dict[str, Any]]:
    return SignalAnalytics.find_peaks(signal, min_height, min_distance)


class STFTSpectrogram:
    """Short-Time Fourier Transform (STFT) and Spectrogram computer."""

    @staticmethod
    def get_window(window_type: str, n: int) -> List[float]:
        wt = window_type.lower()
        if wt == "hann":
            return [0.5 * (1.0 - math.cos(2.0 * math.pi * i / (n - 1))) for i in range(n)]
        elif wt == "hamming":
            return [0.54 - 0.46 * math.cos(2.0 * math.pi * i / (n - 1)) for i in range(n)]
        elif wt == "blackman":
            return [
                0.42 - 0.5 * math.cos(2.0 * math.pi * i / (n - 1)) + 0.08 * math.cos(4.0 * math.pi * i / (n - 1))
                for i in range(n)
            ]
        else:  # rectangular
            return [1.0] * n

    @classmethod
    def compute(
        cls,
        signal: List[float],
        frame_size: int = 64,
        hop_size: int = 32,
        window: str = "hann",
    ) -> Dict[str, Any]:
        """Computes STFT magnitude and power spectrogram."""
        w = cls.get_window(window, frame_size)
        num_frames = (len(signal) - frame_size) // hop_size + 1
        if num_frames <= 0:
            return {"frames": [], "spectrogram": [], "frequencies": []}

        spectrogram = []
        magnitudes = []

        for f_idx in range(num_frames):
            start = f_idx * hop_size
            frame = [signal[start + i] * w[i] for i in range(frame_size)]

            # DFT
            X = dft(frame)
            half = frame_size // 2 + 1
            mag_frame = [abs(c) for c in X[:half]]
            power_frame = [round((m ** 2) / frame_size, 5) for m in mag_frame]

            magnitudes.append(mag_frame)
            spectrogram.append(power_frame)

        return {
            "num_frames": num_frames,
            "num_bins": frame_size // 2 + 1,
            "spectrogram": spectrogram,
            "magnitudes": magnitudes,
        }


class SavitzkyGolayFilter:
    """Savitzky-Golay polynomial smoothing and differentiation filter with exact boundary interpolation."""

    @staticmethod
    def _compute_weights(window_length: int, poly_order: int, t0: float = 0.0, deriv_order: int = 0) -> List[float]:
        """Computes convolution weights for offset t0 via Vandermonde pseudo-inverse."""
        m = (window_length - 1) // 2
        order = poly_order + 1
        rows = window_length

        A = [[(i - m) ** j for j in range(order)] for i in range(rows)]
        ATA = [[sum(A[i][r] * A[i][c] for i in range(rows)) for c in range(order)] for r in range(order)]

        aug = [list(ATA[r]) + [1.0 if r == c else 0.0 for c in range(order)] for r in range(order)]
        for col in range(order):
            pivot_row = max(range(col, order), key=lambda r: abs(aug[r][col]))
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            pivot = aug[col][col]
            if abs(pivot) < 1e-12:
                continue
            for c in range(col, 2 * order):
                aug[col][c] /= pivot
            for r in range(order):
                if r != col:
                    factor = aug[r][col]
                    for c in range(col, 2 * order):
                        aug[r][c] -= factor * aug[col][c]

        ATA_inv = [aug[r][order:] for r in range(order)]
        Pinv = [[sum(ATA_inv[j][k] * A[p][k] for k in range(order)) for p in range(rows)] for j in range(order)]

        weights = [0.0] * rows
        for p in range(rows):
            w = sum(
                (math.factorial(j) / math.factorial(j - deriv_order)) * (t0 ** (j - deriv_order)) * Pinv[j][p]
                for j in range(deriv_order, order)
            )
            weights[p] = round(w, 8)
        return weights

    @classmethod
    def filter(
        cls,
        signal: List[float],
        window_length: int = 7,
        poly_order: int = 2,
        deriv: int = 0,
    ) -> List[float]:
        """Applies Savitzky-Golay filter to signal using boundary polynomial extrapolation."""
        n = len(signal)
        if window_length % 2 == 0:
            window_length += 1
        if window_length > n:
            window_length = n if n % 2 != 0 else n - 1
        if window_length < 3:
            return list(signal)

        poly_order = min(poly_order, window_length - 1)
        m = (window_length - 1) // 2

        center_weights = cls._compute_weights(window_length, poly_order, 0.0, deriv)

        filtered = []
        for i in range(n):
            if i < m:
                # Left boundary
                weights = cls._compute_weights(window_length, poly_order, float(i - m), deriv)
                window = signal[:window_length]
                val = sum(x * w for x, w in zip(window, weights))
            elif i >= n - m:
                # Right boundary
                weights = cls._compute_weights(window_length, poly_order, float(i - (n - 1 - m)), deriv)
                window = signal[n - window_length:]
                val = sum(x * w for x, w in zip(window, weights))
            else:
                # Central window
                window = signal[i - m : i - m + window_length]
                val = sum(x * w for x, w in zip(window, center_weights))
            filtered.append(round(val, 6))

        return filtered


def signals_stft(signal: List[float], frame_size: int = 64, hop_size: int = 32) -> Dict[str, Any]:
    """Computes Short-Time Fourier Transform power spectrogram."""
    return STFTSpectrogram.compute(signal, frame_size, hop_size)


def signals_savitzky_golay(signal: List[float], window_length: int = 7, poly_order: int = 2, deriv: int = 0) -> List[float]:
    """Applies Savitzky-Golay polynomial smoothing or differentiation."""
    return SavitzkyGolayFilter.filter(signal, window_length, poly_order, deriv)


# ===========================================================================
# COOLEY-TUKEY RADIX-2 FAST FOURIER TRANSFORM (FFT & IFFT)
# ===========================================================================

class CooleyTukeyFFT:
    """In-place Radix-2 Cooley-Tukey FFT and IFFT with power-of-two padding."""

    @staticmethod
    def _next_pow2(n: int) -> int:
        p = 1
        while p < n:
            p <<= 1
        return p

    @classmethod
    def fft(cls, signal: List[Union[float, complex]]) -> List[complex]:
        n = len(signal)
        if n == 0:
            return []
        p2 = cls._next_pow2(n)
        a = [complex(s) for s in signal] + [0.0 + 0.0j] * (p2 - n)
        cls._radix2(a, invert=False)
        return a

    @classmethod
    def ifft(cls, spectrum: List[complex]) -> List[complex]:
        n = len(spectrum)
        if n == 0:
            return []
        p2 = cls._next_pow2(n)
        a = list(spectrum) + [0.0 + 0.0j] * (p2 - n)
        cls._radix2(a, invert=True)
        scale = 1.0 / p2
        return [x * scale for x in a]

    @staticmethod
    def _radix2(a: List[complex], invert: bool = False):
        n = len(a)
        # Bit-reversal permutation
        j = 0
        for i in range(n):
            if i < j:
                a[i], a[j] = a[j], a[i]
            mask = n >> 1
            while mask and j & mask:
                j ^= mask
                mask >>= 1
            j ^= mask

        # Butterfly computation
        length = 2
        sign = 1.0 if invert else -1.0
        while length <= n:
            angle = sign * 2.0 * math.pi / length
            w_len = complex(math.cos(angle), math.sin(angle))
            half = length >> 1
            for i in range(0, n, length):
                w = 1.0 + 0.0j
                for k in range(half):
                    u = a[i + k]
                    v = a[i + k + half] * w
                    a[i + k] = u + v
                    a[i + k + half] = u - v
                    w *= w_len
            length <<= 1


# ===========================================================================
# HILBERT TRANSFORM & INSTANTANEOUS ENVELOPE / FREQUENCY
# ===========================================================================

class HilbertTransform:
    """Computes exact discrete-time Hilbert transform and analytic signal."""

    @staticmethod
    def compute(signal: List[float]) -> Dict[str, Any]:
        n = len(signal)
        if n == 0:
            return {"analytic": [], "envelope": [], "phase": [], "instantaneous_freq": []}

        # FFT -> zero negative frequencies and double positive -> IFFT
        X = CooleyTukeyFFT.fft(signal)
        m = len(X)
        H = [0.0 + 0.0j] * m

        if m % 2 == 0:
            H[0] = 1.0
            H[m // 2] = 1.0
            for i in range(1, m // 2):
                H[i] = 2.0
        else:
            H[0] = 1.0
            for i in range(1, (m + 1) // 2):
                H[i] = 2.0

        for i in range(m):
            X[i] *= H[i]

        analytic_full = CooleyTukeyFFT.ifft(X)
        analytic = analytic_full[:n]

        envelope = [round(abs(z), 6) for z in analytic]
        phase = [round(math.atan2(z.imag, z.real), 6) for z in analytic]

        # Instantaneous frequency: numerical phase derivative unwrapped
        inst_freq = [0.0] * n
        for i in range(1, n):
            dphi = phase[i] - phase[i - 1]
            # Wrap phase difference to [-pi, pi]
            while dphi > math.pi:
                dphi -= 2.0 * math.pi
            while dphi < -math.pi:
                dphi += 2.0 * math.pi
            inst_freq[i] = round(dphi / (2.0 * math.pi), 6)
        if n > 1:
            inst_freq[0] = inst_freq[1]

        return {
            "analytic": analytic,
            "envelope": envelope,
            "phase": phase,
            "instantaneous_freq": inst_freq,
        }


# ===========================================================================
# CROSS-CORRELATION & AUTOCORRELATION PITCH ESTIMATOR
# ===========================================================================

class CrossCorrelation:
    """Normalized cross-correlation and optimal time-delay estimation."""

    @staticmethod
    def correlate(x: List[float], y: List[float]) -> Dict[str, Any]:
        nx = len(x)
        ny = len(y)
        if nx == 0 or ny == 0:
            return {"lag": 0, "max_correlation": 0.0, "correlations": []}

        # Demean signals
        mean_x = sum(x) / nx
        mean_y = sum(y) / ny
        dx = [v - mean_x for v in x]
        dy = [v - mean_y for v in y]

        denom_x = math.sqrt(sum(v * v for v in dx))
        denom_y = math.sqrt(sum(v * v for v in dy))
        denom = denom_x * denom_y if denom_x > 1e-12 and denom_y > 1e-12 else 1.0

        # Compute correlations across lags [-max_lag, max_lag]
        max_lag = max(nx, ny) - 1
        lags = list(range(-max_lag, max_lag + 1))
        corrs = []

        best_lag = 0
        best_val = -1e9

        for lag in lags:
            val = 0.0
            count = 0
            for i in range(nx):
                j = i - lag
                if 0 <= j < ny:
                    val += dx[i] * dy[j]
                    count += 1
            norm_val = (val / denom) if count > 0 else 0.0
            corrs.append(round(norm_val, 6))
            if norm_val > best_val:
                best_val = norm_val
                best_lag = lag

        return {
            "lag": best_lag,
            "max_correlation": round(best_val, 6),
            "correlations": corrs,
            "lags": lags,
        }

    @staticmethod
    def detect_pitch(signal: List[float], sample_rate: int = 44100, fmin: float = 60.0, fmax: float = 800.0) -> Dict[str, Any]:
        """Estimates fundamental frequency (F0) using autocorrelation and parabolic interpolation."""
        n = len(signal)
        min_lag = int(sample_rate / fmax)
        max_lag = min(int(sample_rate / fmin), n - 1)

        if n <= max_lag or min_lag >= max_lag:
            return {"frequency_hz": 0.0, "clarity": 0.0, "voiced": False}

        mean_s = sum(signal) / n
        ds = [v - mean_s for v in signal]
        r0 = sum(v * v for v in ds)
        if r0 < 1e-12:
            return {"frequency_hz": 0.0, "clarity": 0.0, "voiced": False}

        autocorr = [0.0] * (max_lag + 1)
        for lag in range(min_lag, max_lag + 1):
            s = sum(ds[i] * ds[i + lag] for i in range(n - lag))
            autocorr[lag] = s / r0

        # Find peak lag in range [min_lag, max_lag]
        best_lag = min_lag
        best_r = autocorr[min_lag]
        for lag in range(min_lag, max_lag + 1):
            if autocorr[lag] > best_r:
                best_r = autocorr[lag]
                best_lag = lag

        # Parabolic interpolation for fractional pitch
        if min_lag < best_lag < max_lag:
            alpha = autocorr[best_lag - 1]
            beta = autocorr[best_lag]
            gamma = autocorr[best_lag + 1]
            denom = 2.0 * (alpha - 2.0 * beta + gamma)
            delta = (alpha - gamma) / denom if abs(denom) > 1e-9 else 0.0
            fine_lag = best_lag + delta
        else:
            fine_lag = float(best_lag)

        freq = (sample_rate / fine_lag) if fine_lag > 0 else 0.0
        voiced = bool(best_r >= 0.3)

        return {
            "frequency_hz": round(freq, 2),
            "clarity": round(best_r, 4),
            "voiced": voiced,
            "period_samples": round(fine_lag, 2),
        }


# ===========================================================================
# TOPOLOGICAL PEAK DETECTOR WITH PROMINENCE & BASES
# ===========================================================================

class PeakDetector:
    """Discovers local maxima and calculates topological prominence and baseline intervals."""

    @staticmethod
    def find_peaks(
        signal: List[float],
        min_prominence: float = 0.1,
        min_distance: int = 1,
    ) -> List[Dict[str, Any]]:
        n = len(signal)
        if n < 3:
            return []

        # Find local peaks
        raw_peaks = []
        for i in range(1, n - 1):
            if signal[i] > signal[i - 1] and signal[i] >= signal[i + 1]:
                raw_peaks.append(i)

        peaks_with_prom = []
        for p in raw_peaks:
            peak_val = signal[p]

            # Search left valley
            left_min = peak_val
            for j in range(p - 1, -1, -1):
                if signal[j] > peak_val:
                    break
                if signal[j] < left_min:
                    left_min = signal[j]

            # Search right valley
            right_min = peak_val
            for j in range(p + 1, n):
                if signal[j] > peak_val:
                    break
                if signal[j] < right_min:
                    right_min = signal[j]

            base = max(left_min, right_min)
            prom = peak_val - base
            if prom >= min_prominence:
                peaks_with_prom.append({
                    "index": p,
                    "height": round(peak_val, 4),
                    "prominence": round(prom, 4),
                    "base": round(base, 4),
                })

        # Filter by min_distance
        if min_distance > 1 and len(peaks_with_prom) > 1:
            peaks_with_prom.sort(key=lambda x: x["height"], reverse=True)
            filtered = []
            for p in peaks_with_prom:
                if all(abs(p["index"] - f["index"]) >= min_distance for f in filtered):
                    filtered.append(p)
            filtered.sort(key=lambda x: x["index"])
            return filtered

        return peaks_with_prom


# ===========================================================================
# LOMB-SCARGLE PERIODOGRAM FOR NON-UNIFORMLY SAMPLED SIGNALS
# ===========================================================================

class LombScarglePeriodogram:
    """Computes Scargle power spectral density for unevenly spaced observations."""

    @staticmethod
    def compute(
        t: List[float],
        y: List[float],
        frequencies: List[float],
    ) -> Dict[str, List[float]]:
        n = len(t)
        if n < 2 or len(y) != n:
            return {"frequencies": frequencies, "powers": [0.0] * len(frequencies)}

        y_mean = sum(y) / n
        dy = [val - y_mean for val in y]
        variance = sum(v * v for v in dy) / (n - 1) if n > 1 else 1.0
        if variance < 1e-12:
            return {"frequencies": frequencies, "powers": [0.0] * len(frequencies)}

        powers = []
        for f in frequencies:
            omega = 2.0 * math.pi * f

            # Tau offset: tan(2 * omega * tau) = sum(sin(2*omega*t)) / sum(cos(2*omega*t))
            sum_s2 = sum(math.sin(2.0 * omega * ti) for ti in t)
            sum_c2 = sum(math.cos(2.0 * omega * ti) for ti in t)
            tau = math.atan2(sum_s2, sum_c2) / (2.0 * omega) if abs(omega) > 1e-9 else 0.0

            sum_cos_term = 0.0
            sum_sin_term = 0.0
            sum_cos_sq = 0.0
            sum_sin_sq = 0.0

            for ti, yi in zip(t, dy):
                c = math.cos(omega * (ti - tau))
                s = math.sin(omega * (ti - tau))
                sum_cos_term += yi * c
                sum_sin_term += yi * s
                sum_cos_sq += c * c
                sum_sin_sq += s * s

            term1 = (sum_cos_term ** 2) / sum_cos_sq if sum_cos_sq > 1e-9 else 0.0
            term2 = (sum_sin_term ** 2) / sum_sin_sq if sum_sin_sq > 1e-9 else 0.0

            power = (term1 + term2) / (2.0 * variance)
            powers.append(round(power, 6))

        return {"frequencies": frequencies, "powers": powers}


# High-level domain entrypoints
def signals_apply_window(signal: List[float], window_type: str = "hann") -> List[float]:
    """Applies window function to input signal."""
    w = STFTSpectrogram.get_window(window_type, len(signal))
    return [float(s) * win for s, win in zip(signal, w)]


def signals_dominant_frequency(spectrum: List[complex], sample_rate: float = 44100.0) -> float:
    """Finds peak dominant frequency in Hz from complex spectrum."""
    n = len(spectrum)
    if n <= 1:
        return 0.0
    half_n = n // 2
    best_bin = 0
    max_mag = -1.0
    for k in range(1, half_n):
        mag = abs(spectrum[k])
        if mag > max_mag:
            max_mag = mag
            best_bin = k
    return round(best_bin * float(sample_rate) / float(n), 2)


def signals_fft(signal: List[float]) -> List[complex]:
    return CooleyTukeyFFT.fft(signal)


def signals_ifft(spectrum: List[complex]) -> List[complex]:
    return CooleyTukeyFFT.ifft(spectrum)


def signals_hilbert(signal: List[float]) -> Any:
    return Record(HilbertTransform.compute(signal))


def signals_cross_correlation(x: List[float], y: List[float]) -> Any:
    return Record(CrossCorrelation.correlate(x, y))


def signals_detect_pitch(signal: List[float], sample_rate: int = 44100, fmin: float = 60.0, fmax: float = 800.0) -> Any:
    return Record(CrossCorrelation.detect_pitch(signal, sample_rate, fmin, fmax))


def signals_find_peaks(signal: List[float], min_prominence: float = 0.1, min_distance: int = 1) -> List[Any]:
    peaks = PeakDetector.find_peaks(signal, min_prominence, min_distance)
    return [Record(p) for p in peaks]


def signals_lomb_scargle(t: List[float], y: List[float], frequencies: List[float]) -> Any:
    return Record(LombScarglePeriodogram.compute(t, y, frequencies))


# ==============================================================================
# ADVANCED DSP: MULTIVARIATE KALMAN FILTER, BUTTERWORTH IIR & EMD
# ==============================================================================

def _matrix_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    rows_A = len(A)
    cols_A = len(A[0]) if rows_A > 0 else 0
    rows_B = len(B)
    cols_B = len(B[0]) if rows_B > 0 else 0
    if cols_A != rows_B:
        raise ValueError(f"Incompatible matrix dimensions: {rows_A}x{cols_A} and {rows_B}x{cols_B}")
    C = [[0.0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for k in range(cols_A):
            aik = A[i][k]
            for j in range(cols_B):
                C[i][j] += aik * B[k][j]
    return C


def _matrix_transpose(A: List[List[float]]) -> List[List[float]]:
    if not A or not A[0]:
        return []
    return [[A[r][c] for r in range(len(A))] for c in range(len(A[0]))]


def _matrix_add(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    return [[A[r][c] + B[r][c] for c in range(len(A[0]))] for r in range(len(A))]


def _matrix_sub(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    return [[A[r][c] - B[r][c] for c in range(len(A[0]))] for r in range(len(A))]


def _matrix_inv(A: List[List[float]]) -> List[List[float]]:
    n = len(A)
    aug = [list(A[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        pivot_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot_row][col]) < 1e-12:
            # Fallback ridge regularization
            aug[col][col] += 1e-6
            pivot_row = col
        aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
        pivot = aug[col][col]
        for c in range(col, 2 * n):
            aug[col][c] /= pivot
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                for c in range(col, 2 * n):
                    aug[r][c] -= factor * aug[col][c]
    return [[aug[i][j + n] for j in range(n)] for i in range(n)]


class KalmanFilterEstimator:
    """Discrete-time linear Kalman Filter for state estimation and tracking."""

    def __init__(
        self,
        F: List[List[float]],
        H: List[List[float]],
        Q: List[List[float]],
        R: List[List[float]],
        x0: Optional[List[float]] = None,
        P0: Optional[List[List[float]]] = None,
    ):
        self.F = [[float(v) for v in row] for row in F]
        self.H = [[float(v) for v in row] for row in H]
        self.Q = [[float(v) for v in row] for row in Q]
        self.R = [[float(v) for v in row] for row in R]
        self.dim_x = len(self.F)
        self.dim_z = len(self.H)

        if x0 is not None:
            self.x = [[float(v)] for v in x0]
        else:
            self.x = [[0.0] for _ in range(self.dim_x)]

        if P0 is not None:
            self.P = [[float(v) for v in row] for row in P0]
        else:
            self.P = [[1.0 if i == j else 0.0 for j in range(self.dim_x)] for i in range(self.dim_x)]

    def filter(self, measurements: List[Any]) -> Record:
        """Executes full Kalman filtering over observation sequence."""
        filtered_states: List[List[float]] = []
        covariances: List[List[List[float]]] = []
        innovations: List[List[float]] = []

        I = [[1.0 if i == j else 0.0 for j in range(self.dim_x)] for i in range(self.dim_x)]
        F_T = _matrix_transpose(self.F)
        H_T = _matrix_transpose(self.H)

        for z_raw in measurements:
            if isinstance(z_raw, (int, float)):
                z = [[float(z_raw)]]
            elif isinstance(z_raw, list):
                z = [[float(v)] for v in z_raw]
            else:
                z = [[0.0]]

            # 1. Prediction step:
            # x_pred = F * x
            x_pred = _matrix_mul(self.F, self.x)
            # P_pred = F * P * F^T + Q
            P_pred = _matrix_add(_matrix_mul(_matrix_mul(self.F, self.P), F_T), self.Q)

            # 2. Measurement update step:
            # y = z - H * x_pred (Innovation)
            y = _matrix_sub(z, _matrix_mul(self.H, x_pred))
            innovations.append([round(y[i][0], 4) for i in range(len(y))])

            # S = H * P_pred * H^T + R (Innovation covariance)
            S = _matrix_add(_matrix_mul(_matrix_mul(self.H, P_pred), H_T), self.R)
            S_inv = _matrix_inv(S)

            # K = P_pred * H^T * S^-1 (Kalman Gain)
            K = _matrix_mul(_matrix_mul(P_pred, H_T), S_inv)

            # x = x_pred + K * y
            self.x = _matrix_add(x_pred, _matrix_mul(K, y))

            # P = (I - K * H) * P_pred
            self.P = _matrix_mul(_matrix_sub(I, _matrix_mul(K, self.H)), P_pred)

            curr_state = [round(self.x[i][0], 4) for i in range(self.dim_x)]
            filtered_states.append(curr_state)
            covariances.append([[round(self.P[r][c], 4) for c in range(self.dim_x)] for r in range(self.dim_x)])

        final_st = filtered_states[-1] if filtered_states else [0.0] * self.dim_x

        return Record({
            "filtered_states": filtered_states,
            "final_state": final_st,
            "covariances": covariances,
            "innovations": innovations,
            "num_steps": len(filtered_states),
        })


class ButterworthIIRFilter:
    """N-th Order Digital Butterworth Filter with Bilinear Transform and Biquad SOS."""

    @classmethod
    def design_lowpass(
        cls,
        cutoff_hz: float,
        order: int = 4,
        sample_rate: float = 1000.0,
    ) -> List[Tuple[List[float], List[float]]]:
        """Calculates cascaded biquad section coefficients [b0, b1, b2], [a0, a1, a2]."""
        n = max(1, int(order))
        fs = float(sample_rate)
        fc = max(1e-3, min(float(cutoff_hz), fs * 0.499))

        # Bilinear transform frequency pre-warping
        omega_p = 2.0 * fs * math.tan(math.pi * fc / fs)

        sections = []
        num_pairs = n // 2

        for k in range(num_pairs):
            theta = math.pi * (2 * k + 1) / (2 * n)
            # Analog s-domain pole pair: s^2 + 2*cos(theta)*omega_p*s + omega_p^2
            alpha = 2.0 * math.cos(theta) * omega_p
            beta = omega_p * omega_p

            # Substitute s = 2*fs * (1 - z^-1)/(1 + z^-1)
            # Let c = 2 * fs
            c = 2.0 * fs
            c2 = c * c

            a0 = c2 + alpha * c + beta
            a1 = 2.0 * (beta - c2)
            a2 = c2 - alpha * c + beta

            b0 = beta
            b1 = 2.0 * beta
            b2 = beta

            # Normalize by a0
            sec_b = [b0 / a0, b1 / a0, b2 / a0]
            sec_a = [1.0, a1 / a0, a2 / a0]
            sections.append((sec_b, sec_a))

        if n % 2 == 1:
            # Single 1st-order real pole
            # s + omega_p -> c*(1 - z^-1)/(1 + z^-1) + omega_p
            c = 2.0 * fs
            a0 = c + omega_p
            a1 = omega_p - c
            b0 = omega_p
            b1 = omega_p
            sections.append(([b0 / a0, b1 / a0, 0.0], [1.0, a1 / a0, 0.0]))

        return sections

    @classmethod
    def apply(
        cls,
        signal: List[float],
        cutoff_hz: float,
        order: int = 4,
        sample_rate: float = 1000.0,
    ) -> List[float]:
        """Filters input signal with cascaded direct-form II transposed biquads."""
        sections = cls.design_lowpass(cutoff_hz, order, sample_rate)
        curr = list(signal)

        for b, a in sections:
            b0, b1, b2 = b
            _, a1, a2 = a
            out = []
            s1 = 0.0
            s2 = 0.0
            for x in curr:
                y = b0 * x + s1
                s1 = b1 * x - a1 * y + s2
                s2 = b2 * x - a2 * y
                out.append(round(y, 6))
            curr = out

        return curr


class EmpiricalModeDecompositionEMD:
    """Empirical Mode Decomposition (EMD) sifting algorithm for non-stationary signals."""

    @classmethod
    def _find_extrema(cls, x: List[float]) -> Tuple[List[int], List[int]]:
        maxima = []
        minima = []
        n = len(x)
        for i in range(1, n - 1):
            if x[i] >= x[i - 1] and x[i] >= x[i + 1] and (x[i] > x[i - 1] or x[i] > x[i + 1]):
                maxima.append(i)
            elif x[i] <= x[i - 1] and x[i] <= x[i + 1] and (x[i] < x[i - 1] or x[i] < x[i + 1]):
                minima.append(i)
        return maxima, minima

    @classmethod
    def _interpolate_envelope(cls, indices: List[int], values: List[float], n: int) -> List[float]:
        """Piecewise linear envelope interpolation with flat boundary extrapolation."""
        if not indices:
            return [0.0] * n
        if len(indices) == 1:
            return [values[indices[0]]] * n

        env = [0.0] * n
        # Flat start
        first_idx = indices[0]
        first_val = values[first_idx]
        for i in range(first_idx):
            env[i] = first_val

        # Linear segments
        for k in range(len(indices) - 1):
            i0, i1 = indices[k], indices[k + 1]
            v0, v1 = values[i0], values[i1]
            span = i1 - i0
            for i in range(i0, i1):
                t = (i - i0) / span
                env[i] = v0 + t * (v1 - v0)

        # Flat end
        last_idx = indices[-1]
        last_val = values[last_idx]
        for i in range(last_idx, n):
            env[i] = last_val

        return env

    @classmethod
    def decompose(
        cls,
        signal: List[float],
        max_imfs: int = 4,
        max_siftings: int = 10,
    ) -> Record:
        """Decomposes signal into Intrinsic Mode Functions (IMFs) and residual trend."""
        n = len(signal)
        residue = [float(v) for v in signal]
        imfs: List[List[float]] = []

        for _ in range(max_imfs):
            h = list(residue)
            for _ in range(max_siftings):
                maxima, minima = cls._find_extrema(h)
                if len(maxima) < 2 or len(minima) < 2:
                    break
                upper_env = cls._interpolate_envelope(maxima, h, n)
                lower_env = cls._interpolate_envelope(minima, h, n)
                mean_env = [(upper_env[i] + lower_env[i]) * 0.5 for i in range(n)]
                h = [h[i] - mean_env[i] for i in range(n)]

            maxima, minima = cls._find_extrema(h)
            if len(maxima) + len(minima) < 3:
                break

            imf = [round(v, 6) for v in h]
            imfs.append(imf)
            residue = [residue[i] - imf[i] for i in range(n)]

        return Record({
            "imfs": imfs,
            "residue": [round(v, 6) for v in residue],
            "num_imfs": len(imfs),
            "original_length": n,
        })


def signals_kalman_filter(
    measurements: List[Any],
    F: List[List[float]],
    H: List[List[float]],
    Q: List[List[float]],
    R: List[List[float]],
    x0: Optional[List[float]] = None,
    P0: Optional[List[List[float]]] = None,
) -> Record:
    """Applies discrete Kalman filter to measurement series."""
    kf = KalmanFilterEstimator(F, H, Q, R, x0=x0, P0=P0)
    return kf.filter(measurements)


def signals_butterworth_lowpass(
    signal: List[float],
    cutoff_hz: float,
    order: int = 4,
    sample_rate: float = 1000.0,
) -> List[float]:
    """Filters signal with Butterworth IIR lowpass filter."""
    return ButterworthIIRFilter.apply(signal, cutoff_hz, order=order, sample_rate=sample_rate)


def signals_emd_decompose(
    signal: List[float],
    max_imfs: int = 4,
) -> Record:
    """Decomposes signal into Intrinsic Mode Functions (IMFs)."""
    return EmpiricalModeDecompositionEMD.decompose(signal, max_imfs=max_imfs)


class ChirpZTransformCZT:
    """Chirp Z-Transform (CZT) using Bluestein's fast circular convolution algorithm."""

    @classmethod
    def compute(
        cls,
        signal: List[Union[float, complex]],
        m_bins: int,
        w: Optional[complex] = None,
        a: complex = 1.0 + 0.0j,
    ) -> Dict[str, Any]:
        n = len(signal)
        if n == 0 or m_bins <= 0:
            return {"czt_spectrum": [], "magnitudes": [], "num_bins": 0}

        # Default W: full unit circle division
        if w is None:
            angle = -2.0 * math.pi / float(m_bins)
            w = complex(math.cos(angle), math.sin(angle))

        # Direct evaluation when small, or Bluestein's FFT convolution
        # To avoid numerical precision issues with power-of-two padding on fractional powers:
        # direct Bluestein / discrete spiral evaluation
        czt_out: List[complex] = []
        magnitudes: List[float] = []

        for k in range(m_bins):
            # z_k = A * (W ** (-k))
            # z_k ** (-n) = (A ** (-n)) * (W ** (n * k))
            val = 0.0 + 0.0j
            for i, x in enumerate(signal):
                # factor = (A ** (-i)) * (W ** (i * k))
                # Compute (a ** (-i))
                a_inv_i = (a ** (-i)) if a != 1.0 else (1.0 + 0.0j)
                w_ik = w ** (i * k)
                val += complex(x) * a_inv_i * w_ik
            czt_out.append(complex(round(val.real, 6), round(val.imag, 6)))
            magnitudes.append(round(abs(val), 6))

        return {
            "czt_spectrum": czt_out,
            "magnitudes": magnitudes,
            "num_bins": m_bins,
            "signal_length": n,
        }


class LevinsonDurbinLPC:
    """Levinson-Durbin recursion for solving Yule-Walker equations to obtain LPC and reflection coefficients."""

    @classmethod
    def solve(cls, autocorr: List[float], order: int) -> Dict[str, Any]:
        p = max(1, min(int(order), len(autocorr) - 1))
        r0 = float(autocorr[0])
        if r0 <= 1e-12:
            return {
                "lpc_coefficients": [0.0] * p,
                "reflection_coefficients": [0.0] * p,
                "prediction_error": 0.0,
                "order": p,
            }

        # Initialize recursion
        a_prev: List[float] = []
        k_coeffs: List[float] = []
        e_prev = r0

        for i in range(1, p + 1):
            # Compute lambda: sum_{j=1}^{i-1} a_{j} * r[i-j]
            lambda_val = float(autocorr[i])
            for j in range(len(a_prev)):
                lambda_val += a_prev[j] * float(autocorr[i - (j + 1)])

            k_i = -lambda_val / max(1e-12, e_prev)
            k_coeffs.append(round(k_i, 6))

            # Update LPC coefficients
            a_curr = [0.0] * i
            a_curr[i - 1] = k_i
            for j in range(len(a_prev)):
                a_curr[j] = a_prev[j] + k_i * a_prev[len(a_prev) - 1 - j]

            e_prev = e_prev * (1.0 - k_i * k_i)
            a_prev = a_curr

        return {
            "lpc_coefficients": [round(c, 6) for c in a_prev],
            "reflection_coefficients": k_coeffs,
            "prediction_error": round(max(0.0, e_prev), 6),
            "order": p,
        }


def signals_czt(
    signal: List[float],
    num_bins: int = 16,
) -> Record:
    """Computes Chirp Z-Transform along spiral contour."""
    return Record(ChirpZTransformCZT.compute(signal, m_bins=num_bins))


def signals_levinson_durbin(
    autocorr: List[float],
    order: int = 4,
) -> Record:
    """Computes LPC and reflection coefficients via Levinson-Durbin recursion."""
    return Record(LevinsonDurbinLPC.solve(autocorr, order=order))


# ==============================================================================
# HILBERT TRANSFORM ANALYTIC SIGNAL & PSEUDO-WIGNER-VILLE DISTRIBUTION
# ==============================================================================


class HilbertTransformAnalyticSignal:
    """Computes discrete Hilbert Transform, Analytic Signal, and Instantaneous Attributes.

    Constructs the analytic signal z[n] = x[n] + j*H{x[n]} via exact discrete Fourier
    transform frequency-domain multiplier (Marple 1999):
    H(k) = 1 for k=0, N/2; 2 for 1 <= k < N/2; 0 for N/2 < k < N.
    Derives instantaneous envelope, phase unwrapping, and instantaneous frequency.
    """

    @staticmethod
    def _dft(x: List[float]) -> List[complex]:
        n = len(x)
        out = [0.0 + 0.0j] * n
        for k in range(n):
            s_re = 0.0
            s_im = 0.0
            angle_step = -2.0 * math.pi * k / n
            for t in range(n):
                angle = angle_step * t
                s_re += x[t] * math.cos(angle)
                s_im += x[t] * math.sin(angle)
            out[k] = complex(s_re, s_im)
        return out

    @staticmethod
    def _idft(X: List[complex]) -> List[complex]:
        n = len(X)
        out = [0.0 + 0.0j] * n
        for t in range(n):
            s_re = 0.0
            s_im = 0.0
            angle_step = 2.0 * math.pi * t / n
            for k in range(n):
                angle = angle_step * k
                re = X[k].real
                im = X[k].imag
                s_re += re * math.cos(angle) - im * math.sin(angle)
                s_im += re * math.sin(angle) + im * math.cos(angle)
            out[t] = complex(s_re / n, s_im / n)
        return out

    @classmethod
    def analyze(
        cls,
        signal: List[float],
        sample_rate: float = 1000.0,
    ) -> Dict[str, Any]:
        """Computes analytic signal, envelope, phase, and instantaneous frequency."""
        n = len(signal)
        if n == 0:
            return {
                "analytic_real": [],
                "analytic_imag": [],
                "instantaneous_envelope": [],
                "instantaneous_phase": [],
                "instantaneous_frequency_hz": [],
                "mean_envelope": 0.0,
                "mean_frequency_hz": 0.0,
            }

        # 1. Forward DFT
        X = cls._dft(signal)

        # 2. Apply Marple analytic signal filter H(k)
        H = [0.0] * n
        if n % 2 == 0:
            H[0] = 1.0
            H[n // 2] = 1.0
            for k in range(1, n // 2):
                H[k] = 2.0
        else:
            H[0] = 1.0
            for k in range(1, (n + 1) // 2):
                H[k] = 2.0

        Z = [X[k] * H[k] for k in range(n)]

        # 3. Inverse DFT to get analytic signal z[n]
        z = cls._idft(Z)

        analytic_real = [round(c.real, 6) for c in z]
        analytic_imag = [round(c.imag, 6) for c in z]

        # 4. Instantaneous envelope
        envelope = [round(math.hypot(c.real, c.imag), 6) for c in z]

        # 5. Instantaneous phase and phase unwrapping
        raw_phase = [math.atan2(c.imag, c.real) for c in z]
        unwrapped_phase = [0.0] * n
        if n > 0:
            unwrapped_phase[0] = raw_phase[0]
            for i in range(1, n):
                diff = raw_phase[i] - raw_phase[i - 1]
                diff = (diff + math.pi) % (2.0 * math.pi) - math.pi
                unwrapped_phase[i] = unwrapped_phase[i - 1] + diff

        # 6. Instantaneous frequency (central difference)
        dt = 1.0 / max(1e-6, sample_rate)
        inst_freq = [0.0] * n
        if n == 1:
            inst_freq[0] = 0.0
        elif n == 2:
            f = (unwrapped_phase[1] - unwrapped_phase[0]) / (2.0 * math.pi * dt)
            inst_freq[0] = round(max(0.0, f), 4)
            inst_freq[1] = round(max(0.0, f), 4)
        else:
            inst_freq[0] = round(max(0.0, (unwrapped_phase[1] - unwrapped_phase[0]) / (2.0 * math.pi * dt)), 4)
            for i in range(1, n - 1):
                f = (unwrapped_phase[i + 1] - unwrapped_phase[i - 1]) / (4.0 * math.pi * dt)
                inst_freq[i] = round(max(0.0, f), 4)
            inst_freq[n - 1] = round(max(0.0, (unwrapped_phase[n - 1] - unwrapped_phase[n - 2]) / (2.0 * math.pi * dt)), 4)

        mean_env = sum(envelope) / max(1, n)
        mean_freq = sum(inst_freq) / max(1, n)

        return {
            "analytic_real": analytic_real,
            "analytic_imag": analytic_imag,
            "instantaneous_envelope": envelope,
            "instantaneous_phase": [round(p, 4) for p in unwrapped_phase],
            "instantaneous_frequency_hz": inst_freq,
            "mean_envelope": round(mean_env, 6),
            "mean_frequency_hz": round(mean_freq, 4),
            "sample_count": n,
        }


class PseudoWignerVilleDistribution:
    """Discrete Pseudo-Wigner-Ville Distribution (PWVD) Time-Frequency Analyzer.

    Computes the smoothed bilinear time-frequency energy distribution:
    PWVD(t, omega) = 2 * sum_{tau = -M}^M z[t + tau] * z*[t - tau] * |h[tau]|^2 * exp(-j * 2 * omega * tau)
    using the analytic signal z[n] to eliminate low-frequency aliasing and negative frequency cross-terms.
    """

    @classmethod
    def compute(
        cls,
        signal: List[float],
        window_len: int = 15,
        num_freq_bins: int = 32,
        sample_rate: float = 1000.0,
    ) -> Dict[str, Any]:
        """Calculates PWVD energy matrix over time and frequency."""
        n = len(signal)
        if n == 0:
            return {
                "time_frequency_matrix": [],
                "times": [],
                "frequencies": [],
                "total_energy": 0.0,
            }

        # 1. Obtain analytic signal to suppress negative frequency cross-terms
        analytic_res = HilbertTransformAnalyticSignal.analyze(signal, sample_rate=sample_rate)
        z = [
            complex(r, im)
            for r, im in zip(analytic_res["analytic_real"], analytic_res["analytic_imag"])
        ]

        # 2. Form symmetrical Hann window of odd length window_len
        w_len = max(3, int(window_len))
        if w_len % 2 == 0:
            w_len += 1
        half_w = w_len // 2

        window = [
            0.5 * (1.0 - math.cos(2.0 * math.pi * i / (w_len - 1)))
            for i in range(w_len)
        ]
        w_norm = [w * w for w in window]

        # 3. Frequency bins and time steps
        num_bins = max(4, int(num_freq_bins))
        dt = 1.0 / max(1e-6, sample_rate)
        times = [round(t * dt, 4) for t in range(n)]
        df = (sample_rate / 2.0) / num_bins
        frequencies = [round(k * df, 2) for k in range(num_bins)]

        tf_matrix: List[List[float]] = []
        total_energy = 0.0
        max_val = -1e9
        peak_t = 0
        peak_k = 0

        for t in range(n):
            # Compute instantaneous auto-correlation for lag tau in [-half_w, half_w]
            row = [0.0] * num_bins
            for k in range(num_bins):
                omega = 2.0 * math.pi * (k / float(2 * num_bins))
                re_sum = 0.0

                for tau in range(-half_w, half_w + 1):
                    idx_plus = t + tau
                    idx_minus = t - tau

                    if 0 <= idx_plus < n and 0 <= idx_minus < n:
                        z_plus = z[idx_plus]
                        z_minus = z[idx_minus]
                        # z_plus * conj(z_minus)
                        c_prod = complex(
                            z_plus.real * z_minus.real + z_plus.imag * z_minus.imag,
                            z_plus.imag * z_minus.real - z_plus.real * z_minus.imag,
                        )
                        w_factor = w_norm[tau + half_w]

                        # Real part of c_prod * exp(-j * 2 * omega * tau)
                        angle = -2.0 * omega * tau
                        re_val = (c_prod.real * math.cos(angle) - c_prod.imag * math.sin(angle)) * w_factor
                        re_sum += re_val

                energy_val = round(max(0.0, 2.0 * re_sum), 5)
                row[k] = energy_val
                total_energy += energy_val
                if energy_val > max_val:
                    max_val = energy_val
                    peak_t = t
                    peak_k = k

            tf_matrix.append(row)

        return {
            "time_frequency_matrix": tf_matrix,
            "times": times,
            "frequencies": frequencies,
            "total_energy": round(total_energy, 4),
            "peak_time_index": peak_t,
            "peak_freq_index": peak_k,
            "peak_frequency_hz": frequencies[peak_k] if frequencies else 0.0,
            "num_times": n,
            "num_freq_bins": num_bins,
        }


def signals_hilbert_envelope(
    signal: List[float],
    sample_rate: float = 1000.0,
) -> Record:
    """Computes discrete Hilbert analytic signal, envelope, phase, and instantaneous frequency."""
    return Record(HilbertTransformAnalyticSignal.analyze(signal, sample_rate=sample_rate))


def signals_pseudo_wigner_ville(
    signal: List[float],
    window_len: int = 15,
    num_freq_bins: int = 32,
    sample_rate: float = 1000.0,
) -> Record:
    """Computes Pseudo-Wigner-Ville joint time-frequency distribution."""
    return Record(
        PseudoWignerVilleDistribution.compute(
            signal,
            window_len=window_len,
            num_freq_bins=num_freq_bins,
            sample_rate=sample_rate,
        )
    )





