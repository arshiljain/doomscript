"""Digital Signal Processing, Wavelet Transforms, and Filter Design for DoomScript."""

import math
import cmath
from typing import List, Dict, Any, Tuple, Optional
from doomscript.runtime import Record


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


