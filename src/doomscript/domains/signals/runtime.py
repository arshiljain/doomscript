"""Digital Signal Processing, Wavelet Transforms, and Filter Design for DoomScript."""

import math
import cmath
from typing import List, Dict, Any, Tuple, Optional


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

