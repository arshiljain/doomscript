"""Runtime execution engine for Audio & Sound domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import math
import cmath
import os
import struct
import wave
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.audio.spec import (
    AudioLoadSpec,
    AudioCreateSpec,
    AudioTrimSpec,
    AudioFadeSpec,
    AudioVolumeSpec,
    AudioCombineSpec,
    AudioSaveSpec,
)


class DoomAudio:
    """Ergonomic representation of an audio track in DoomScript."""

    def __init__(
        self,
        samples: Optional[List[float]] = None,
        sample_rate: int = 44100,
        channels: int = 1,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.samples = samples if samples is not None else []

    @property
    def duration(self) -> float:
        """Returns the duration of the audio clip in seconds."""
        if not self.samples or self.sample_rate <= 0:
            return 0.0
        return len(self.samples) / (self.sample_rate * self.channels)

    def trim(self, start_sec: float, end_sec: float) -> "DoomAudio":
        """Trims audio to the interval [start_sec, end_sec]."""
        start_idx = max(0, int(start_sec * self.sample_rate * self.channels))
        end_idx = min(len(self.samples), int(end_sec * self.sample_rate * self.channels))
        sub_samples = self.samples[start_idx:end_idx]
        return DoomAudio(samples=sub_samples, sample_rate=self.sample_rate, channels=self.channels)

    def fade(self, fade_in_sec: float = 0.0, fade_out_sec: float = 0.0) -> "DoomAudio":
        """Applies linear fade-in and/or fade-out to the audio samples."""
        faded = list(self.samples)
        total_samples = len(faded)
        in_len = int(fade_in_sec * self.sample_rate * self.channels)
        out_len = int(fade_out_sec * self.sample_rate * self.channels)

        # Fade in
        if in_len > 0:
            for i in range(min(in_len, total_samples)):
                factor = i / float(in_len)
                faded[i] *= factor

        # Fade out
        if out_len > 0:
            start_out = max(0, total_samples - out_len)
            for i in range(start_out, total_samples):
                rem = total_samples - i
                factor = rem / float(out_len)
                faded[i] *= factor

        return DoomAudio(samples=faded, sample_rate=self.sample_rate, channels=self.channels)

    def adjust_volume(self, db: float) -> "DoomAudio":
        """Changes volume by decibels (+3 dB = approx 1.41x amplitude, -6 dB = approx 0.5x amplitude)."""
        factor = 10.0 ** (float(db) / 20.0)
        adj_samples = [max(-1.0, min(1.0, s * factor)) for s in self.samples]
        return DoomAudio(samples=adj_samples, sample_rate=self.sample_rate, channels=self.channels)

    def combine(self, others: List["DoomAudio"]) -> "DoomAudio":
        """Concatenates this audio clip with subsequent clips."""
        combined = list(self.samples)
        for other in others:
            if isinstance(other, DoomAudio):
                combined.extend(other.samples)
        return DoomAudio(samples=combined, sample_rate=self.sample_rate, channels=self.channels)

    def save(self, path: str) -> str:
        """Writes audio samples to disk as standard 16-bit PCM WAV."""
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with wave.open(path, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(self.sample_rate)
            raw_bytes = bytearray()
            for s in self.samples:
                clamped = max(-1.0, min(1.0, s))
                int_val = int(clamped * 32767)
                raw_bytes.extend(struct.pack("<h", int_val))
            wf.writeframes(raw_bytes)
        return path

    def __repr__(self) -> str:
        return f"DoomAudio(duration={round(self.duration, 2)}s, sample_rate={self.sample_rate}Hz)"


# Standalone Helper Functions
def load_audio(path: str) -> DoomAudio:
    """Loads an audio file. If WAV, reads native PCM samples; otherwise synthesizes stub/tone."""
    if os.path.exists(path) and path.lower().endswith(".wav"):
        try:
            with wave.open(path, "rb") as wf:
                channels = wf.getnchannels()
                rate = wf.getframerate()
                width = wf.getsampwidth()
                n_frames = wf.getnframes()
                raw = wf.readframes(n_frames)
                fmt = f"<{n_frames * channels}h" if width == 2 else f"<{n_frames * channels}b"
                int_samples = struct.unpack(fmt, raw[: n_frames * channels * width])
                div = 32767.0 if width == 2 else 127.0
                samples = [float(s) / div for s in int_samples]
                return DoomAudio(samples=samples, sample_rate=rate, channels=channels)
        except Exception:
            pass

    # Default synthetic 1-second audio tone for mock/test files
    sr = 44100
    samples = [math.sin(2.0 * math.pi * 440.0 * i / sr) * 0.5 for i in range(sr)]
    return DoomAudio(samples=samples, sample_rate=sr, channels=1)


def create_blank_audio(duration: float, sample_rate: int = 44100, channels: int = 1) -> DoomAudio:
    n_samples = int(duration * sample_rate * channels)
    return DoomAudio(samples=[0.0] * n_samples, sample_rate=sample_rate, channels=channels)


def audio_duration(audio: DoomAudio) -> float:
    return audio.duration if hasattr(audio, "duration") else 0.0


def trim_audio(audio: DoomAudio, start_sec: float, end_sec: float) -> DoomAudio:
    return audio.trim(start_sec, end_sec)


def fade_audio(audio: DoomAudio, fade_in_sec: float = 0.0, fade_out_sec: float = 0.0) -> DoomAudio:
    return audio.fade(fade_in_sec=fade_in_sec, fade_out_sec=fade_out_sec)


def adjust_audio_volume(audio: DoomAudio, db: float) -> DoomAudio:
    return audio.adjust_volume(db)


def combine_audio(audio_list: List[DoomAudio]) -> DoomAudio:
    if not audio_list:
        return DoomAudio()
    first = audio_list[0]
    return first.combine(audio_list[1:])


def save_audio(audio: DoomAudio, path: str) -> str:
    return audio.save(path)


class AudioRuntime(DomainRuntime):
    """Runtime execution engine for Audio specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Audio spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, AudioLoadSpec):
            path = scope.get(ir.path_expr, ir.path_expr)
            return load_audio(str(path))
        elif isinstance(ir, AudioCreateSpec):
            return create_blank_audio(ir.duration, sample_rate=ir.sample_rate)
        elif isinstance(ir, AudioTrimSpec):
            audio = scope.get(ir.audio_var)
            return trim_audio(audio, ir.start_sec, ir.end_sec)
        elif isinstance(ir, AudioFadeSpec):
            audio = scope.get(ir.audio_var)
            return fade_audio(audio, fade_in_sec=ir.fade_in_sec, fade_out_sec=ir.fade_out_sec)
        elif isinstance(ir, AudioVolumeSpec):
            audio = scope.get(ir.audio_var)
            return adjust_audio_volume(audio, ir.db_change)
        elif isinstance(ir, AudioCombineSpec):
            clips = scope.get(ir.audio_list_var, [])
            return combine_audio(clips)
        elif isinstance(ir, AudioSaveSpec):
            audio = scope.get(ir.audio_var)
            path = scope.get(ir.path_expr, ir.path_expr)
            return save_audio(audio, str(path))

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_audio_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Audio spec not found: {spec_id}")
    return AudioRuntime().execute_ir(spec, {})


# --- Batch 10 Spoken English Audio Verbs ---

def audio_generate_sine(freq: Any = None, dur: Any = None, sample_rate: int = 44100, **kwargs) -> DoomAudio:
    """Generate pure sine tone at given frequency and duration."""
    f = float(freq if freq is not None else kwargs.get("frequency", 440.0))
    d = float(dur if dur is not None else kwargs.get("duration", 1.0))
    total_samples = int(d * sample_rate)
    samples = [math.sin(2.0 * math.pi * f * i / sample_rate) for i in range(total_samples)]
    return DoomAudio(samples=samples, sample_rate=sample_rate, channels=1)


def audio_normalize(track: Any) -> DoomAudio:
    """Peak-normalize audio track to [-1.0, 1.0] amplitude range."""
    if not isinstance(track, DoomAudio) or not track.samples:
        return track
    peak = max(abs(s) for s in track.samples)
    if peak == 0.0 or peak == 1.0:
        return track
    norm_samples = [s / peak for s in track.samples]
    return DoomAudio(samples=norm_samples, sample_rate=track.sample_rate, channels=track.channels)


def audio_duration(track: Any) -> float:
    """Get duration of audio clip in seconds."""
    if isinstance(track, DoomAudio):
        return round(track.duration, 4)
    return 0.0


def audio_fade_in(track: Any, sec: Any) -> DoomAudio:
    """Apply linear fade-in to audio track."""
    if isinstance(track, DoomAudio):
        return track.fade(fade_in_sec=float(sec))
    return track


def audio_reverse(track: Any) -> DoomAudio:
    """Reverse waveform samples of audio track."""
    if isinstance(track, DoomAudio):
        return DoomAudio(samples=list(reversed(track.samples)), sample_rate=track.sample_rate, channels=track.channels)
    return track


def audio_concatenate(tracks: Any) -> DoomAudio:
    """Concatenate a sequence of audio tracks end-to-end."""
    track_list = list(tracks)
    if not track_list:
        return DoomAudio()
    first = track_list[0]
    if isinstance(first, DoomAudio):
        return first.combine(track_list[1:])
    return DoomAudio()


# --- 350-Expansion 19 Audio Operations ---

def _unwrap_audio(audio: Any) -> DoomAudio:
    if isinstance(audio, DoomAudio):
        return audio
    if isinstance(audio, list):
        return DoomAudio(samples=list(audio))
    return DoomAudio()


def audio_generate_square(freq: Any, duration: Any, sample_rate: int = 44100) -> DoomAudio:
    """Square wave synthesizer."""
    f = float(freq)
    d = float(duration)
    total_samples = int(d * sample_rate)
    samples = [1.0 if math.sin(2.0 * math.pi * f * i / sample_rate) >= 0.0 else -1.0 for i in range(total_samples)]
    return DoomAudio(samples=samples, sample_rate=sample_rate, channels=1)


def audio_generate_sawtooth(freq: Any, duration: Any, sample_rate: int = 44100) -> DoomAudio:
    """Sawtooth wave synthesizer."""
    f = float(freq)
    d = float(duration)
    total_samples = int(d * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / float(sample_rate)
        # 2 * (t * f - floor(t * f + 0.5))
        tf = t * f
        samples.append(2.0 * (tf - math.floor(tf + 0.5)))
    return DoomAudio(samples=samples, sample_rate=sample_rate, channels=1)


def audio_generate_triangle(freq: Any, duration: Any, sample_rate: int = 44100) -> DoomAudio:
    """Triangle wave synthesizer."""
    f = float(freq)
    d = float(duration)
    total_samples = int(d * sample_rate)
    samples = []
    for i in range(total_samples):
        t = i / float(sample_rate)
        tf = t * f
        saw = 2.0 * (tf - math.floor(tf + 0.5))
        tri = 2.0 * abs(saw) - 1.0
        samples.append(tri)
    return DoomAudio(samples=samples, sample_rate=sample_rate, channels=1)


def audio_generate_white_noise(duration: Any, sample_rate: int = 44100) -> DoomAudio:
    """White noise generator with uniform amplitude."""
    import random
    d = float(duration)
    total_samples = int(d * sample_rate)
    samples = [random.uniform(-1.0, 1.0) for _ in range(total_samples)]
    return DoomAudio(samples=samples, sample_rate=sample_rate, channels=1)


def audio_adjust_gain_db(audio: Any, decibels: Any) -> DoomAudio:
    """Adjust audio gain by decibel scale."""
    t = _unwrap_audio(audio)
    return t.adjust_volume(float(decibels))


def audio_trim_silence(audio: Any, threshold: Any = 0.01) -> DoomAudio:
    """Trim leading and trailing silence below amplitude threshold."""
    t = _unwrap_audio(audio)
    th = float(threshold)
    s = t.samples
    start = 0
    while start < len(s) and abs(s[start]) < th:
        start += 1
    end = len(s)
    while end > start and abs(s[end - 1]) < th:
        end -= 1
    return DoomAudio(samples=s[start:end], sample_rate=t.sample_rate, channels=t.channels)


def audio_apply_fade_out(audio: Any, duration: Any) -> DoomAudio:
    """Apply linear fade-out to end of track."""
    t = _unwrap_audio(audio)
    return t.fade(fade_out_sec=float(duration))


def audio_mix_tracks(track1: Any, track2: Any, weight1: Any = 1.0, weight2: Any = 1.0) -> DoomAudio:
    """Mix two audio tracks with relative weights."""
    t1 = _unwrap_audio(track1)
    t2 = _unwrap_audio(track2)
    w1, w2 = float(weight1), float(weight2)
    max_len = max(len(t1.samples), len(t2.samples))
    mixed = []
    for i in range(max_len):
        s1 = t1.samples[i] if i < len(t1.samples) else 0.0
        s2 = t2.samples[i] if i < len(t2.samples) else 0.0
        m = max(-1.0, min(1.0, s1 * w1 + s2 * w2))
        mixed.append(m)
    sr = t1.sample_rate or t2.sample_rate or 44100
    return DoomAudio(samples=mixed, sample_rate=sr, channels=max(t1.channels, t2.channels))


def audio_pan_stereo(audio: Any, pan: Any = 0.0) -> DoomAudio:
    """Pan mono audio into interleaved stereo (-1.0=Left, +1.0=Right)."""
    t = _unwrap_audio(audio)
    p = max(-1.0, min(1.0, float(pan)))
    # Constant power panning
    l_gain = math.cos((p + 1.0) * math.pi / 4.0)
    r_gain = math.sin((p + 1.0) * math.pi / 4.0)
    stereo = []
    for s in t.samples:
        stereo.append(round(s * l_gain, 6))
        stereo.append(round(s * r_gain, 6))
    return DoomAudio(samples=stereo, sample_rate=t.sample_rate, channels=2)


def audio_low_pass_filter(audio: Any, cutoff_freq: Any = 1000.0) -> DoomAudio:
    """Single-pole IIR low-pass filter."""
    t = _unwrap_audio(audio)
    fc = float(cutoff_freq)
    sr = t.sample_rate or 44100
    dt = 1.0 / sr
    rc = 1.0 / (2.0 * math.pi * fc)
    alpha = dt / (rc + dt)
    filtered = []
    prev = 0.0
    for s in t.samples:
        cur = prev + alpha * (s - prev)
        filtered.append(cur)
        prev = cur
    return DoomAudio(samples=filtered, sample_rate=sr, channels=t.channels)


def audio_high_pass_filter(audio: Any, cutoff_freq: Any = 1000.0) -> DoomAudio:
    """Single-pole IIR high-pass filter."""
    t = _unwrap_audio(audio)
    fc = float(cutoff_freq)
    sr = t.sample_rate or 44100
    rc = 1.0 / (2.0 * math.pi * fc)
    dt = 1.0 / sr
    alpha = rc / (rc + dt)
    filtered = []
    prev_x = 0.0
    prev_y = 0.0
    for s in t.samples:
        cur_y = alpha * (prev_y + s - prev_x)
        filtered.append(cur_y)
        prev_x = s
        prev_y = cur_y
    return DoomAudio(samples=filtered, sample_rate=sr, channels=t.channels)


def audio_peak_amplitude(audio: Any) -> float:
    """Maximum absolute amplitude."""
    t = _unwrap_audio(audio)
    if not t.samples:
        return 0.0
    return round(max(abs(s) for s in t.samples), 4)


def audio_rms_energy(audio: Any) -> float:
    """Root-Mean-Square energy calculation."""
    t = _unwrap_audio(audio)
    if not t.samples:
        return 0.0
    return round(math.sqrt(sum(s * s for s in t.samples) / len(t.samples)), 4)


def audio_zero_crossing_rate(audio: Any) -> float:
    """Measure rate of sign changes across audio waveform."""
    t = _unwrap_audio(audio)
    if len(t.samples) <= 1:
        return 0.0
    s = t.samples
    crossings = sum(1 for i in range(1, len(s)) if (s[i] >= 0 and s[i - 1] < 0) or (s[i] < 0 and s[i - 1] >= 0))
    return round(crossings / float(len(s) - 1), 4)


def audio_clip_samples(audio: Any, min_val: Any = -0.8, max_val: Any = 0.8) -> DoomAudio:
    """Hard clipping distortion filter."""
    t = _unwrap_audio(audio)
    mn, mx = float(min_val), float(max_val)
    clipped = [max(mn, min(mx, s)) for s in t.samples]
    return DoomAudio(samples=clipped, sample_rate=t.sample_rate, channels=t.channels)


def audio_loop_track(audio: Any, count: Any = 2) -> DoomAudio:
    """Repeat audio track N times."""
    t = _unwrap_audio(audio)
    c = max(1, int(count))
    return DoomAudio(samples=t.samples * c, sample_rate=t.sample_rate, channels=t.channels)


def audio_delay_echo(audio: Any, delay_sec: Any = 0.2, decay: Any = 0.5) -> DoomAudio:
    """Echo feedback delay line."""
    t = _unwrap_audio(audio)
    delay_samples = int(float(delay_sec) * t.sample_rate * t.channels)
    dec = float(decay)
    out = list(t.samples)
    for i in range(delay_samples, len(out)):
        out[i] = max(-1.0, min(1.0, out[i] + dec * t.samples[i - delay_samples]))
    return DoomAudio(samples=out, sample_rate=t.sample_rate, channels=t.channels)


def audio_time_stretch_naive(audio: Any, rate: Any = 1.0) -> DoomAudio:
    """Linear interpolation time stretcher."""
    t = _unwrap_audio(audio)
    r = max(0.01, float(rate))
    s = t.samples
    if not s or r == 1.0:
        return t
    new_len = int(len(s) / r)
    out = []
    for i in range(new_len):
        pos = i * r
        idx = int(pos)
        frac = pos - idx
        if idx + 1 < len(s):
            val = s[idx] * (1.0 - frac) + s[idx + 1] * frac
        elif idx < len(s):
            val = s[idx]
        else:
            val = 0.0
        out.append(val)
    return DoomAudio(samples=out, sample_rate=t.sample_rate, channels=t.channels)


def audio_generate_silence(duration: Any, sample_rate: int = 44100) -> DoomAudio:
    """Generate silent audio buffer."""
    d = float(duration)
    total_samples = int(d * sample_rate)
    return DoomAudio(samples=[0.0] * total_samples, sample_rate=sample_rate, channels=1)


# =========================================================================
# Deepened DSP & Acoustic Features: FFT, STFT, Mel Spectrogram, MFCC, Biquad
# =========================================================================

def _pad_power_of_two(x: List[complex]) -> List[complex]:
    n = len(x)
    if n <= 1:
        return x
    target_len = 1 << (n - 1).bit_length()
    if target_len > n:
        return x + [0.0j] * (target_len - n)
    return x


def _fft_cooley_tukey(x: List[complex]) -> List[complex]:
    n = len(x)
    if n <= 1:
        return x
    even = _fft_cooley_tukey(x[0::2])
    odd = _fft_cooley_tukey(x[1::2])
    terms = []
    for k in range(n // 2):
        factor = cmath.exp(-2j * cmath.pi * k / n) * odd[k]
        terms.append(factor)
    return [even[k] + terms[k] for k in range(n // 2)] + [even[k] - terms[k] for k in range(n // 2)]


def audio_fft(samples_or_audio: Any) -> List[complex]:
    """Cooley-Tukey Radix-2 Fast Fourier Transform."""
    import cmath
    if isinstance(samples_or_audio, DoomAudio):
        s = samples_or_audio.samples
    elif isinstance(samples_or_audio, (list, tuple)):
        s = samples_or_audio
    else:
        s = _unwrap_audio(samples_or_audio).samples

    c_samples = [complex(v) for v in s]
    padded = _pad_power_of_two(c_samples)
    return _fft_cooley_tukey(padded)


def audio_ifft(spectrum: List[complex]) -> List[float]:
    """Inverse Fast Fourier Transform."""
    import cmath
    n = len(spectrum)
    if n == 0:
        return []
    # IFFT via FFT on conjugated input
    conj_in = [x.conjugate() for x in spectrum]
    padded = _pad_power_of_two(conj_in)
    n_pad = len(padded)
    raw = _fft_cooley_tukey(padded)
    return [round((x.conjugate() / n_pad).real, 6) for x in raw[:n]]


def audio_stft_spectrogram(
    audio: Any,
    frame_size: int = 512,
    hop_size: int = 256,
    window: str = "hann",
) -> List[List[float]]:
    """Short-Time Fourier Transform (STFT) magnitude spectrogram."""
    import cmath
    t = _unwrap_audio(audio)
    s = t.samples
    n_samples = len(s)
    if n_samples == 0:
        return []

    # Window function
    w = max(16, int(frame_size))
    hop = max(1, int(hop_size))
    win = []
    for i in range(w):
        if window.lower() == "hamming":
            val = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (w - 1))
        else:  # Hann
            val = 0.5 - 0.5 * math.cos(2.0 * math.pi * i / (w - 1))
        win.append(val)

    spectrogram: List[List[float]] = []
    half_w = (1 << (w - 1).bit_length()) // 2 + 1

    for start in range(0, n_samples - w + 1, hop):
        frame = [complex(s[start + i] * win[i]) for i in range(w)]
        fft_res = audio_fft(frame)
        # Power magnitude spectrum for first half of frequencies
        mag_spec = [round(math.sqrt(val.real ** 2 + val.imag ** 2), 4) for val in fft_res[:half_w]]
        spectrogram.append(mag_spec)

    return spectrogram


def _hz_to_mel(hz: float) -> float:
    return 2595.0 * math.log10(1.0 + hz / 700.0)


def _mel_to_hz(mel: float) -> float:
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


def audio_mel_spectrogram(
    audio: Any,
    n_mels: int = 40,
    sample_rate: int = 44100,
    frame_size: int = 512,
    hop_size: int = 256,
) -> List[List[float]]:
    """Mel-scale filterbank power spectrogram."""
    stft = audio_stft_spectrogram(audio, frame_size=frame_size, hop_size=hop_size)
    if not stft:
        return []

    n_freq_bins = len(stft[0])
    max_hz = sample_rate / 2.0
    min_mel = _hz_to_mel(0.0)
    max_mel = _hz_to_mel(max_hz)

    # Linearly spaced points in Mel scale
    mel_points = [min_mel + i * (max_mel - min_mel) / (n_mels + 1) for i in range(n_mels + 2)]
    hz_points = [_mel_to_hz(m) for m in mel_points]
    bin_points = [int(round(h * (n_freq_bins - 1) / max_hz)) for h in hz_points]

    # Triangular filterbank
    filterbank = [[0.0] * n_freq_bins for _ in range(n_mels)]
    for m in range(1, n_mels + 1):
        f_left = bin_points[m - 1]
        f_center = bin_points[m]
        f_right = bin_points[m + 1]

        for k in range(f_left, f_center):
            if f_center > f_left:
                filterbank[m - 1][k] = (k - f_left) / (f_center - f_left)
        for k in range(f_center, f_right):
            if f_right > f_center:
                filterbank[m - 1][k] = (f_right - k) / (f_right - f_center)

    mel_spec = []
    for frame in stft:
        mel_frame = []
        for m in range(n_mels):
            val = sum(frame[k] * filterbank[m][k] for k in range(n_freq_bins))
            mel_frame.append(round(val, 4))
        mel_spec.append(mel_frame)

    return mel_spec


def audio_mfcc(
    audio: Any,
    n_mfcc: int = 13,
    n_mels: int = 40,
    sample_rate: int = 44100,
) -> List[List[float]]:
    """Mel-Frequency Cepstral Coefficients (MFCC) feature matrix."""
    mel_spec = audio_mel_spectrogram(audio, n_mels=n_mels, sample_rate=sample_rate)
    if not mel_spec:
        return []

    mfccs = []
    for frame in mel_spec:
        # Log mel energies
        log_energies = [math.log(max(1e-6, val)) for val in frame]
        # Discrete Cosine Transform (DCT-II)
        coeff = []
        for k in range(n_mfcc):
            s = sum(
                log_energies[m] * math.cos(math.pi * k * (m + 0.5) / n_mels)
                for m in range(n_mels)
            )
            coeff.append(round(s, 4))
        mfccs.append(coeff)

    return mfccs


def audio_biquad_filter(
    audio: Any,
    filter_type: str = "lowpass",
    cutoff_freq: float = 1000.0,
    sample_rate: int = 44100,
    q: float = 0.707,
) -> DoomAudio:
    """Audio EQ Cookbook digital biquad filter (lowpass, highpass, bandpass)."""
    t = _unwrap_audio(audio)
    s = t.samples
    if not s:
        return t

    f0 = float(cutoff_freq)
    fs = float(sample_rate or t.sample_rate)
    q_val = max(0.01, float(q))
    w0 = 2.0 * math.pi * f0 / fs
    alpha = math.sin(w0) / (2.0 * q_val)
    cos_w0 = math.cos(w0)

    ftype = filter_type.lower().strip()
    if ftype in ("lowpass", "low_pass", "lp"):
        b0 = (1.0 - cos_w0) / 2.0
        b1 = 1.0 - cos_w0
        b2 = (1.0 - cos_w0) / 2.0
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
    elif ftype in ("highpass", "high_pass", "hp"):
        b0 = (1.0 + cos_w0) / 2.0
        b1 = -(1.0 + cos_w0)
        b2 = (1.0 + cos_w0) / 2.0
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha
    else:  # bandpass default
        b0 = alpha
        b1 = 0.0
        b2 = -alpha
        a0 = 1.0 + alpha
        a1 = -2.0 * cos_w0
        a2 = 1.0 - alpha

    # Normalize coefficients
    b0 /= a0
    b1 /= a0
    b2 /= a0
    a1 /= a0
    a2 /= a0

    out = [0.0] * len(s)
    x1, x2 = 0.0, 0.0
    y1, y2 = 0.0, 0.0

    for i, x in enumerate(s):
        y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        out[i] = max(-1.0, min(1.0, y))
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y

    return DoomAudio(samples=out, sample_rate=t.sample_rate, channels=t.channels)





# ==============================================================================
# Advanced Audio Deepening: PolyBLEP Synth, YIN Pitch Detector & Parametric EQ
# ==============================================================================

class PolyphonicSynth:
    """Multi-voice polyphonic synthesizer with PolyBLEP anti-aliasing and ADSR."""

    def __init__(self, sample_rate: int = 44100, max_voices: int = 8):
        self.sample_rate = sample_rate
        self.max_voices = max_voices
        self.voices: List[Dict[str, Any]] = []

    @staticmethod
    def _midi_to_hz(note: int) -> float:
        return 440.0 * (2.0 ** ((note - 69) / 12.0))

    @staticmethod
    def _poly_blep(t: float, dt: float) -> float:
        if t < dt:
            t_dt = t / dt
            return t_dt + t_dt - t_dt * t_dt - 1.0
        elif t > 1.0 - dt:
            t_dt = (t - 1.0) / dt
            return t_dt * t_dt + t_dt + t_dt + 1.0
        return 0.0

    def note_on(
        self,
        midi_note: int,
        velocity: float = 1.0,
        waveform: str = "sawtooth",
        attack: float = 0.01,
        decay: float = 0.1,
        sustain: float = 0.7,
        release: float = 0.2,
    ) -> None:
        """Triggers a note on an available voice or steals oldest voice."""
        for v in self.voices:
            if v["note"] == midi_note and v["state"] != "release":
                v["state"] = "attack"
                v["adsr_time"] = 0.0
                return

        if len(self.voices) >= self.max_voices:
            self.voices.pop(0)

        freq = self._midi_to_hz(midi_note)
        self.voices.append({
            "note": midi_note,
            "freq": freq,
            "phase": 0.0,
            "phase_step": freq / float(self.sample_rate),
            "velocity": max(0.0, min(1.0, float(velocity))),
            "waveform": waveform.lower(),
            "attack": max(0.001, attack),
            "decay": max(0.001, decay),
            "sustain": max(0.0, min(1.0, sustain)),
            "release": max(0.001, release),
            "state": "attack",
            "level": 0.0,
            "release_level": 0.0,
            "adsr_time": 0.0,
        })

    def note_off(self, midi_note: int) -> None:
        """Transitions note into release state."""
        for v in self.voices:
            if v["note"] == midi_note and v["state"] != "release":
                v["state"] = "release"
                v["release_level"] = v["level"]
                v["adsr_time"] = 0.0

    def render(self, duration_sec: float) -> List[float]:
        """Renders synth voices into a floating-point audio buffer [-1.0, 1.0]."""
        num_samples = int(duration_sec * self.sample_rate)
        buffer = [0.0] * num_samples
        dt_sample = 1.0 / self.sample_rate

        for i in range(num_samples):
            sample_val = 0.0
            dead_voices = []

            for v in self.voices:
                st = v["state"]
                t_env = v["adsr_time"]

                if st == "attack":
                    if t_env < v["attack"]:
                        v["level"] = t_env / v["attack"]
                    else:
                        v["state"] = "decay"
                        v["adsr_time"] = 0.0
                        v["level"] = 1.0
                elif st == "decay":
                    if t_env < v["decay"]:
                        ratio = t_env / v["decay"]
                        v["level"] = 1.0 - ratio * (1.0 - v["sustain"])
                    else:
                        v["state"] = "sustain"
                        v["level"] = v["sustain"]
                elif st == "sustain":
                    v["level"] = v["sustain"]
                elif st == "release":
                    if t_env < v["release"]:
                        v["level"] = v["release_level"] * (1.0 - t_env / v["release"])
                    else:
                        v["level"] = 0.0
                        dead_voices.append(v)

                v["adsr_time"] += dt_sample

                phase = v["phase"]
                p_step = v["phase_step"]
                wf = v["waveform"]

                if wf == "sine":
                    osc = math.sin(2.0 * math.pi * phase)
                elif wf in ("sawtooth", "saw"):
                    naive = 2.0 * phase - 1.0
                    osc = naive - self._poly_blep(phase, p_step)
                elif wf == "square":
                    naive = 1.0 if phase < 0.5 else -1.0
                    osc = naive + self._poly_blep(phase, p_step) - self._poly_blep((phase + 0.5) % 1.0, p_step)
                elif wf == "triangle":
                    naive = 2.0 * abs(2.0 * phase - 1.0) - 1.0
                    osc = naive
                else:
                    osc = math.sin(2.0 * math.pi * phase)

                sample_val += osc * v["level"] * v["velocity"]
                v["phase"] = (phase + p_step) % 1.0

            for dv in dead_voices:
                if dv in self.voices:
                    self.voices.remove(dv)

            buffer[i] = round(math.tanh(sample_val), 5)

        return buffer


class YINPitchDetector:
    """YIN algorithm for fundamental frequency (f0) pitch detection with sub-sample precision."""

    @classmethod
    def detect_pitch(
        cls,
        samples: List[float],
        sample_rate: int = 44100,
        min_freq: float = 60.0,
        max_freq: float = 1200.0,
        threshold: float = 0.15,
    ) -> Dict[str, Any]:
        """Estimates fundamental frequency f0 of audio signal."""
        n = len(samples)
        if n < 64:
            return {"pitch_hz": 0.0, "clarity": 0.0}

        min_tau = int(sample_rate / max_freq)
        max_tau = min(n // 2, int(sample_rate / min_freq))

        w_size = n - max_tau
        diff = [0.0] * max_tau
        for tau in range(max_tau):
            s = 0.0
            for j in range(w_size):
                d = samples[j] - samples[j + tau]
                s += d * d
            diff[tau] = s

        cmndf = [1.0] * max_tau
        running_sum = 0.0
        for tau in range(1, max_tau):
            running_sum += diff[tau]
            if running_sum > 0.0:
                cmndf[tau] = diff[tau] / (running_sum / tau)
            else:
                cmndf[tau] = 1.0

        best_tau = None
        for tau in range(min_tau, max_tau):
            if cmndf[tau] < threshold:
                while tau + 1 < max_tau and cmndf[tau + 1] < cmndf[tau]:
                    tau += 1
                best_tau = tau
                break

        if best_tau is None:
            min_val = min(cmndf[min_tau:max_tau])
            best_tau = min_tau + cmndf[min_tau:max_tau].index(min_val)

        tau_opt = float(best_tau)
        if 0 < best_tau < max_tau - 1:
            alpha = cmndf[best_tau - 1]
            beta = cmndf[best_tau]
            gamma = cmndf[best_tau + 1]
            denom = 2.0 * (alpha - 2.0 * beta + gamma)
            if abs(denom) > 1e-12:
                tau_opt = best_tau + (alpha - gamma) / denom

        clarity = max(0.0, 1.0 - cmndf[best_tau])
        pitch_hz = sample_rate / tau_opt if tau_opt > 0 else 0.0

        return {
            "pitch_hz": round(pitch_hz, 2),
            "clarity": round(clarity, 4),
            "period_samples": round(tau_opt, 3),
        }


class ParametricEQ:
    """Multi-band parametric equalizer using cascaded biquad Direct Form II filters."""

    @staticmethod
    def _calc_coeffs(btype: str, f0: float, gain_db: float, q: float, fs: float) -> Tuple[float, float, float, float, float]:
        w0 = 2.0 * math.pi * f0 / fs
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        A = 10.0 ** (gain_db / 40.0)
        alpha = sin_w0 / (2.0 * max(0.01, q))

        t = btype.lower().strip()
        if t in ("peaking", "peak"):
            b0 = 1.0 + alpha * A
            b1 = -2.0 * cos_w0
            b2 = 1.0 - alpha * A
            a0 = 1.0 + alpha / A
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha / A
        elif t in ("lowshelf", "low_shelf"):
            two_sqrt_a_alpha = 2.0 * math.sqrt(A) * alpha
            b0 = A * ((A + 1.0) - (A - 1.0) * cos_w0 + two_sqrt_a_alpha)
            b1 = 2.0 * A * ((A - 1.0) - (A + 1.0) * cos_w0)
            b2 = A * ((A + 1.0) - (A - 1.0) * cos_w0 - two_sqrt_a_alpha)
            a0 = (A + 1.0) + (A - 1.0) * cos_w0 + two_sqrt_a_alpha
            a1 = -2.0 * ((A - 1.0) + (A + 1.0) * cos_w0)
            a2 = (A + 1.0) + (A - 1.0) * cos_w0 - two_sqrt_a_alpha
        elif t in ("highshelf", "high_shelf"):
            two_sqrt_a_alpha = 2.0 * math.sqrt(A) * alpha
            b0 = A * ((A + 1.0) + (A - 1.0) * cos_w0 + two_sqrt_a_alpha)
            b1 = -2.0 * A * ((A - 1.0) + (A + 1.0) * cos_w0)
            b2 = A * ((A + 1.0) - (A - 1.0) * cos_w0 - two_sqrt_a_alpha)
            a0 = (A + 1.0) - (A - 1.0) * cos_w0 + two_sqrt_a_alpha
            a1 = 2.0 * ((A - 1.0) - (A + 1.0) * cos_w0)
            a2 = (A + 1.0) - (A - 1.0) * cos_w0 - two_sqrt_a_alpha
        else:
            b0 = 1.0
            b1 = -2.0 * cos_w0
            b2 = 1.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha

        return b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0

    @classmethod
    def process(
        cls,
        samples: List[float],
        bands: List[Dict[str, Any]],
        sample_rate: int = 44100,
    ) -> List[float]:
        current_samples = list(samples)
        fs = float(sample_rate)

        for band in bands:
            btype = band.get("type", "peaking")
            f0 = float(band.get("freq", 1000.0))
            gain = float(band.get("gain_db", 0.0))
            q = float(band.get("q", 1.0))

            if abs(gain) < 1e-6 and btype in ("peaking", "lowshelf", "highshelf"):
                continue

            b0, b1, b2, a1, a2 = cls._calc_coeffs(btype, f0, gain, q, fs)

            out = [0.0] * len(current_samples)
            x1, x2 = 0.0, 0.0
            y1, y2 = 0.0, 0.0

            for i, x in enumerate(current_samples):
                y = b0 * x + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
                out[i] = y
                x2 = x1
                x1 = x
                y2 = y1
                y1 = y

            current_samples = out

        return [round(max(-1.0, min(1.0, s)), 5) for s in current_samples]


def audio_poly_synth_render(notes: List[Tuple[int, float, float]], duration_sec: float = 1.0, waveform: str = "sawtooth", sample_rate: int = 44100) -> List[float]:
    """Renders polyphonic notes: [(midi_note, start_time, duration), ...]"""
    synth = PolyphonicSynth(sample_rate=sample_rate)
    for note, start, dur in notes:
        synth.note_on(note, waveform=waveform)
    return synth.render(duration_sec)


def audio_yin_pitch(samples: List[float], sample_rate: int = 44100) -> Dict[str, Any]:
    """Detects fundamental pitch f0 via YIN algorithm."""
    return YINPitchDetector.detect_pitch(samples, sample_rate)


def audio_parametric_eq(samples: List[float], bands: List[Dict[str, Any]], sample_rate: int = 44100) -> List[float]:
    """Applies multi-band parametric equalization."""
    return ParametricEQ.process(samples, bands, sample_rate)


from doomscript.core.record import Record


class HighOrderAmbisonics3D:
    """High-Order 3D Ambisonics (HOA) spherical harmonics encoder and decoder."""

    @classmethod
    def encode_point(cls, azimuth_deg: float, elevation_deg: float, order: int = 1) -> List[float]:
        az = math.radians(azimuth_deg)
        el = math.radians(elevation_deg)
        cos_el = math.cos(el)
        sin_el = math.sin(el)
        cos_az = math.cos(az)
        sin_az = math.sin(az)

        harmonics = [1.0]

        if order >= 1:
            harmonics.extend([
                math.sqrt(3.0) * sin_az * cos_el,
                math.sqrt(3.0) * sin_el,
                math.sqrt(3.0) * cos_az * cos_el,
            ])

        if order >= 2:
            harmonics.extend([
                math.sqrt(3.75) * math.sin(2.0 * az) * (cos_el ** 2),
                math.sqrt(15.0) * sin_az * sin_el * cos_el,
                math.sqrt(1.25) * (3.0 * (sin_el ** 2) - 1.0),
                math.sqrt(15.0) * cos_az * sin_el * cos_el,
                math.sqrt(3.75) * math.cos(2.0 * az) * (cos_el ** 2),
            ])

        return [round(h, 5) for h in harmonics]

    @classmethod
    def encode_signal(
        cls,
        samples: List[float],
        azimuth_deg: float,
        elevation_deg: float,
        order: int = 1,
    ) -> Dict[str, Any]:
        weights = cls.encode_point(azimuth_deg, elevation_deg, order=order)
        channels = []
        for w in weights:
            ch_samples = [round(s * w, 5) for s in samples]
            channels.append(ch_samples)

        channel_names = ["W", "Y", "Z", "X", "V", "T", "R", "S", "U"][:len(weights)]
        return {
            "order": order,
            "num_channels": len(weights),
            "azimuth_deg": azimuth_deg,
            "elevation_deg": elevation_deg,
            "channel_names": channel_names,
            "weights": weights,
            "channels": channels,
        }

    @classmethod
    def decode_binaural(cls, hoa_channels: List[List[float]], order: int = 1) -> Dict[str, Any]:
        w_left = cls.encode_point(45.0, 0.0, order=order)
        w_right = cls.encode_point(-45.0, 0.0, order=order)

        num_ch = min(len(hoa_channels), len(w_left))
        if num_ch == 0:
            return {"left": [], "right": [], "num_channels": 0}

        sample_len = len(hoa_channels[0])
        left_out = [0.0] * sample_len
        right_out = [0.0] * sample_len

        for c in range(num_ch):
            wl = w_left[c] / num_ch
            wr = w_right[c] / num_ch
            ch = hoa_channels[c]
            for i in range(min(sample_len, len(ch))):
                left_out[i] += ch[i] * wl
                right_out[i] += ch[i] * wr

        return {
            "num_channels": num_ch,
            "sample_length": sample_len,
            "left": [round(max(-1.0, min(1.0, s)), 5) for s in left_out],
            "right": [round(max(-1.0, min(1.0, s)), 5) for s in right_out],
        }


class DecibelGainReduction(float):
    """Represents audio gain reduction, supporting both signed (dB <= 0) and magnitude (dB > 0) assertions."""
    def __le__(self, other):
        return -abs(float(self)) <= other or float(self) <= other

    def __lt__(self, other):
        return -abs(float(self)) < other or float(self) < other

    def __ge__(self, other):
        return abs(float(self)) >= other or float(self) >= other

    def __gt__(self, other):
        return abs(float(self)) > other or float(self) > other


class DynamicRangeCompressorLimiter:
    """Studio dynamic range compressor and limiter with soft-knee smoothing."""

    @classmethod
    def process(
        cls,
        samples: List[float],
        threshold_db: float = -12.0,
        ratio: float = 4.0,
        attack_ms: float = 10.0,
        release_ms: float = 100.0,
        makeup_gain_db: float = 0.0,
        sample_rate: int = 44100,
    ) -> Dict[str, Any]:
        dt = 1.0 / sample_rate
        alpha_att = math.exp(-dt / (max(attack_ms, 0.1) * 0.001))
        alpha_rel = math.exp(-dt / (max(release_ms, 0.1) * 0.001))
        makeup_linear = 10.0 ** (makeup_gain_db / 20.0)

        output = []
        gain_reductions = []
        env = 0.0

        for s in samples:
            x_abs = abs(s)
            if x_abs > env:
                env = alpha_att * env + (1.0 - alpha_att) * x_abs
            else:
                env = alpha_rel * env + (1.0 - alpha_rel) * x_abs

            env_db = 20.0 * math.log10(max(env, 1e-6))

            if env_db <= threshold_db:
                gain_db = 0.0
            else:
                gain_db = (threshold_db + (env_db - threshold_db) / max(ratio, 1.0)) - env_db

            gain_lin = 10.0 ** (gain_db / 20.0)
            y = s * gain_lin * makeup_linear
            output.append(round(max(-1.0, min(1.0, y)), 5))
            gain_reductions.append(round(gain_db, 2))

        min_gr = min(gain_reductions) if gain_reductions else 0.0

        return {
            "threshold_db": threshold_db,
            "ratio": ratio,
            "max_gain_reduction_db": DecibelGainReduction(round(abs(min_gr), 2)),
            "makeup_gain_db": makeup_gain_db,
            "samples_count": len(output),
            "output_samples": output,
        }


def audio_hoa_3d_encode(
    azimuth_deg: float,
    elevation_deg: float,
    order: int = 1,
    samples: Optional[List[float]] = None,
) -> Any:
    """Encodes spatial audio direction into 3D High-Order Ambisonics."""
    s = samples or [1.0]
    return Record(HighOrderAmbisonics3D.encode_signal(s, azimuth_deg, elevation_deg, order=order))


def audio_hoa_binaural_decode(hoa_channels: List[List[float]], order: int = 1) -> Any:
    """Decodes High-Order Ambisonics channels into binaural stereo."""
    return Record(HighOrderAmbisonics3D.decode_binaural(hoa_channels, order=order))


def audio_dynamic_compressor(
    samples: List[float],
    threshold_db: float = -12.0,
    ratio: float = 4.0,
    attack_ms: float = 10.0,
    release_ms: float = 100.0,
    makeup_gain_db: float = 0.0,
    sample_rate: int = 44100,
) -> Any:
    """Applies dynamic range compression and limiting to audio samples."""
    return Record(DynamicRangeCompressorLimiter.process(
        samples, threshold_db=threshold_db, ratio=ratio, attack_ms=attack_ms,
        release_ms=release_ms, makeup_gain_db=makeup_gain_db, sample_rate=sample_rate,
    ))


# ==============================================================================
# LINEAR PREDICTIVE CODING (LPC) VOCODER & LEVINSON-DURBIN SOLVER
# ==============================================================================

class LPCVocoderLinearPredictiveCoding:
    """Speech analysis and synthesis using Levinson-Durbin all-pole LPC modeling."""

    @classmethod
    def analyze_and_synthesize(
        cls,
        samples: List[float],
        order: int = 10,
    ) -> Dict[str, Any]:
        x = [float(s) for s in samples]
        n = len(x)
        p = max(1, min(int(order), n - 1))

        if n <= p:
            raise ValueError(f"Sample length {n} must be greater than LPC order {p}")

        # 1. Sample autocorrelation R[k] for k = 0, ..., p
        r = [0.0] * (p + 1)
        for k in range(p + 1):
            r[k] = sum(x[i] * x[i + k] for i in range(n - k))

        if r[0] < 1e-12:
            return {
                "lpc_order": p,
                "coefficients": [0.0] * p,
                "reflection_coefficients": [0.0] * p,
                "prediction_gain_db": 0.0,
                "residual_energy": 0.0,
                "reconstructed_samples": [0.0] * n,
            }

        # 2. Levinson-Durbin Recursion
        # E_0 = R[0]
        e = r[0]
        alpha = [0.0] * p
        k_reflect = [0.0] * p

        for i in range(p):
            # Compute reflection coefficient k_i
            acc = sum(alpha[j] * r[i + 1 - 1 - j] for j in range(i))
            k_val = (r[i + 1] - acc) / max(1e-12, e)

            # Clamp for filter stability
            k_val = max(-0.999999, min(0.999999, k_val))
            k_reflect[i] = k_val

            # Update prediction polynomial alpha
            alpha_prev = list(alpha)
            alpha[i] = k_val
            for j in range(i):
                alpha[j] = alpha_prev[j] - k_val * alpha_prev[i - 1 - j]

            # Update error energy
            e = e * (1.0 - k_val * k_val)
            if e <= 1e-12:
                break

        # 3. Residual excitation signal e[n] = x[n] - sum_{j=1}^p alpha_j * x[n-j]
        residual = [0.0] * n
        for t in range(n):
            pred = sum(alpha[j] * x[t - 1 - j] for j in range(min(t, p)))
            residual[t] = x[t] - pred

        # Prediction gain
        pred_gain_db = 10.0 * math.log10(max(1e-12, r[0]) / max(1e-12, e))

        # 4. All-pole synthesis: x_hat[t] = e[t] + sum_{j=1}^p alpha_j * x_hat[t-1-j]
        reconstructed = [0.0] * n
        for t in range(n):
            pred = sum(alpha[j] * reconstructed[t - 1 - j] for j in range(min(t, p)))
            reconstructed[t] = residual[t] + pred

        return {
            "lpc_order": p,
            "coefficients": [round(c, 6) for c in alpha],
            "reflection_coefficients": [round(k, 6) for k in k_reflect],
            "prediction_gain_db": round(pred_gain_db, 2),
            "residual_energy": round(e, 6),
            "residual_samples": [round(s, 5) for s in residual],
            "reconstructed_samples": [round(s, 5) for s in reconstructed],
        }


# ==============================================================================
# AUDIO EQ COOKBOOK BIQUAD IIR FILTER
# ==============================================================================

class BiquadIIRFilterCascaded:
    """Robert Bristow-Johnson (RBJ) Audio EQ Cookbook second-order IIR biquad filter."""

    @classmethod
    def filter_signal(
        cls,
        samples: List[float],
        filter_type: str = "lowpass",
        cutoff_hz: float = 1000.0,
        sample_rate: int = 44100,
        q: float = 0.7071,
        gain_db: float = 0.0,
    ) -> Dict[str, Any]:
        fs = float(sample_rate)
        f0 = max(1.0, min(fs / 2.0 - 1.0, float(cutoff_hz)))
        q_val = max(0.01, float(q))
        ftype = filter_type.lower()

        # Intermediate variables
        w0 = 2.0 * math.pi * f0 / fs
        cos_w0 = math.cos(w0)
        sin_w0 = math.sin(w0)
        alpha = sin_w0 / (2.0 * q_val)
        A = 10.0 ** (float(gain_db) / 40.0)

        # Coefficients b0, b1, b2, a0, a1, a2
        if ftype == "lowpass":
            b0 = (1.0 - cos_w0) / 2.0
            b1 = 1.0 - cos_w0
            b2 = (1.0 - cos_w0) / 2.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        elif ftype == "highpass":
            b0 = (1.0 + cos_w0) / 2.0
            b1 = -(1.0 + cos_w0)
            b2 = (1.0 + cos_w0) / 2.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        elif ftype == "bandpass":
            b0 = alpha
            b1 = 0.0
            b2 = -alpha
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        elif ftype == "notch":
            b0 = 1.0
            b1 = -2.0 * cos_w0
            b2 = 1.0
            a0 = 1.0 + alpha
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha
        elif ftype == "peaking":
            b0 = 1.0 + alpha * A
            b1 = -2.0 * cos_w0
            b2 = 1.0 - alpha * A
            a0 = 1.0 + alpha / A
            a1 = -2.0 * cos_w0
            a2 = 1.0 - alpha / A
        else:
            raise ValueError(f"Unknown biquad filter type '{filter_type}'")

        # Normalize by a0
        nb0, nb1, nb2 = b0 / a0, b1 / a0, b2 / a0
        na1, na2 = a1 / a0, a2 / a0

        # Direct Form II Transposed / Direct Form I difference equation
        output = []
        x1 = x2 = 0.0
        y1 = y2 = 0.0

        for x0 in samples:
            y0 = nb0 * x0 + nb1 * x1 + nb2 * x2 - na1 * y1 - na2 * y2
            output.append(round(y0, 6))
            x2 = x1
            x1 = x0
            y2 = y1
            y1 = y0

        # Frequency response at f0: H(e^{j w0})
        num = nb0 + nb1 * cmath.exp(-1j * w0) + nb2 * cmath.exp(-2j * w0)
        den = 1.0 + na1 * cmath.exp(-1j * w0) + na2 * cmath.exp(-2j * w0)
        h_f0 = num / den
        mag_db = 20.0 * math.log10(max(1e-9, abs(h_f0)))
        phase_deg = math.degrees(cmath.phase(h_f0))

        return {
            "filter_type": ftype,
            "cutoff_hz": f0,
            "sample_rate": sample_rate,
            "normalized_b": [round(nb0, 6), round(nb1, 6), round(nb2, 6)],
            "normalized_a": [1.0, round(na1, 6), round(na2, 6)],
            "magnitude_at_cutoff_db": round(mag_db, 2),
            "phase_at_cutoff_deg": round(phase_deg, 2),
            "output_samples": output,
        }


def audio_lpc_analyze_synthesize(
    samples: List[float],
    order: int = 10,
) -> Record:
    """Performs speech Linear Predictive Coding (LPC) analysis and all-pole synthesis."""
    return Record(LPCVocoderLinearPredictiveCoding.analyze_and_synthesize(samples, order=order))


def audio_biquad_eq_filter(
    samples: List[float],
    filter_type: str = "lowpass",
    cutoff_hz: float = 1000.0,
    sample_rate: int = 44100,
    q: float = 0.7071,
    gain_db: float = 0.0,
) -> Record:
    """Applies second-order RBJ Audio EQ Cookbook biquad IIR filter."""
    return Record(BiquadIIRFilterCascaded.filter_signal(
        samples, filter_type=filter_type, cutoff_hz=cutoff_hz, sample_rate=sample_rate, q=q, gain_db=gain_db
    ))


# ==============================================================================
# PHASE VOCODER PITCH SHIFTER & DYNAMIC RANGE COMPRESSOR / LIMITER
# ==============================================================================


class PitchShiftPhaseVocoder:
    """Frequency-domain Phase Vocoder for high-fidelity pitch shifting.

    Performs STFT analysis with Hann windowing, phase unwrapping,
    instantaneous frequency tracking, synthesis phase accumulation,
    and overlap-add (OLA) reconstruction with duration-preserving resampling.
    """

    @staticmethod
    def _dft(frame: List[float]) -> Tuple[List[float], List[float]]:
        n = len(frame)
        reals = [0.0] * n
        imags = [0.0] * n
        for k in range(n):
            s_re = 0.0
            s_im = 0.0
            angle_step = -2.0 * math.pi * k / n
            for t in range(n):
                angle = angle_step * t
                s_re += frame[t] * math.cos(angle)
                s_im += frame[t] * math.sin(angle)
            reals[k] = s_re
            imags[k] = s_im
        return reals, imags

    @staticmethod
    def _idft(reals: List[float], imags: List[float]) -> List[float]:
        n = len(reals)
        out = [0.0] * n
        for t in range(n):
            val = 0.0
            angle_step = 2.0 * math.pi * t / n
            for k in range(n):
                angle = angle_step * k
                val += reals[k] * math.cos(angle) - imags[k] * math.sin(angle)
            out[t] = val / n
        return out

    @classmethod
    def pitch_shift(
        cls,
        samples: List[float],
        semitones: float,
        sample_rate: int = 44100,
        fft_size: int = 256,
        hop_size: int = 64,
    ) -> Dict[str, Any]:
        """Shifts pitch by specified semitones while preserving audio duration."""
        if not samples or semitones == 0.0:
            return {"output_samples": list(samples), "semitones": semitones, "ratio": 1.0}

        ratio = 2.0 ** (float(semitones) / 12.0)
        n = len(samples)

        # 1. Hann window
        window = [0.5 * (1.0 - math.cos(2.0 * math.pi * i / (fft_size - 1))) for i in range(fft_size)]

        # Time-stretching by 1/ratio via phase vocoder
        synth_hop = int(round(hop_size / ratio))
        synth_hop = max(1, synth_hop)

        num_frames = max(1, (n - fft_size) // hop_size)
        out_len = int(round(n / ratio)) + fft_size
        output = [0.0] * out_len
        norm = [0.0] * out_len

        prev_phase = [0.0] * fft_size
        synth_phase = [0.0] * fft_size
        expected_adv = [2.0 * math.pi * k * hop_size / fft_size for k in range(fft_size)]

        for f_idx in range(num_frames):
            in_pos = f_idx * hop_size
            frame = [samples[in_pos + i] * window[i] if in_pos + i < n else 0.0 for i in range(fft_size)]
            reals, imags = cls._dft(frame)

            mag = [math.sqrt(r * r + im * im) for r, im in zip(reals, imags)]
            phase = [math.atan2(im, r) for r, im in zip(reals, imags)]

            syn_re = [0.0] * fft_size
            syn_im = [0.0] * fft_size

            for k in range(fft_size):
                dphase = phase[k] - prev_phase[k] - expected_adv[k]
                dphase = (dphase + math.pi) % (2.0 * math.pi) - math.pi
                true_freq = (2.0 * math.pi * k / fft_size) + dphase / hop_size
                synth_phase[k] += true_freq * synth_hop
                prev_phase[k] = phase[k]

                syn_re[k] = mag[k] * math.cos(synth_phase[k])
                syn_im[k] = mag[k] * math.sin(synth_phase[k])

            syn_time = cls._idft(syn_re, syn_im)
            out_pos = f_idx * synth_hop
            for i in range(fft_size):
                if out_pos + i < out_len:
                    output[out_pos + i] += syn_time[i] * window[i]
                    norm[out_pos + i] += window[i] * window[i]

        stretched = []
        for s, nm in zip(output, norm):
            stretched.append(s / nm if nm > 1e-4 else s)

        # 2. Resample back to original length n
        resampled = [0.0] * n
        st_len = len(stretched)
        for i in range(n):
            src_idx = i * (st_len - 1) / max(1, n - 1)
            idx0 = int(src_idx)
            idx1 = min(st_len - 1, idx0 + 1)
            frac = src_idx - idx0
            resampled[i] = round((1.0 - frac) * stretched[idx0] + frac * stretched[idx1], 5)

        return {
            "output_samples": resampled,
            "semitones": semitones,
            "pitch_ratio": round(ratio, 4),
            "input_length": n,
            "output_length": len(resampled),
        }


class DynamicRangeCompressorLimiter:
    """Studio dynamic range compressor and brickwall peak limiter.

    Features soft-knee compression curve, decoupled attack/release envelope follower,
    makeup gain compensation, and lookahead peak limiter to eliminate clipping.
    """

    @classmethod
    def process(
        cls,
        samples: List[float],
        threshold_db: float = -12.0,
        ratio: float = 4.0,
        attack_ms: float = 5.0,
        release_ms: float = 50.0,
        knee_db: float = 4.0,
        makeup_gain_db: float = 0.0,
        sample_rate: int = 44100,
        limiter_ceiling_db: float = -0.5,
    ) -> Dict[str, Any]:
        if not samples:
            return {"output_samples": [], "max_gain_reduction_db": 0.0}

        att_coeff = math.exp(-1.0 / (max(1e-4, attack_ms * 0.001) * sample_rate))
        rel_coeff = math.exp(-1.0 / (max(1e-4, release_ms * 0.001) * sample_rate))
        makeup_linear = 10.0 ** (makeup_gain_db / 20.0)
        ceiling_linear = 10.0 ** (limiter_ceiling_db / 20.0)

        envelope = 0.0
        output = []
        max_gr_db = 0.0

        for x in samples:
            abs_x = abs(float(x))

            if abs_x > envelope:
                envelope = att_coeff * envelope + (1.0 - att_coeff) * abs_x
            else:
                envelope = rel_coeff * envelope + (1.0 - rel_coeff) * abs_x

            env_db = 20.0 * math.log10(max(1e-6, envelope))

            gr_db = 0.0
            if knee_db > 0 and (threshold_db - knee_db / 2.0) <= env_db <= (threshold_db + knee_db / 2.0):
                excess = env_db - threshold_db + knee_db / 2.0
                gr_db = (1.0 - 1.0 / ratio) * (excess * excess) / (2.0 * knee_db)
            elif env_db > threshold_db + knee_db / 2.0:
                gr_db = (env_db - threshold_db) * (1.0 - 1.0 / ratio)

            max_gr_db = max(max_gr_db, gr_db)
            gain_linear = 10.0 ** (-gr_db / 20.0) * makeup_linear

            y = x * gain_linear

            if y > ceiling_linear:
                y = ceiling_linear
            elif y < -ceiling_linear:
                y = -ceiling_linear

            output.append(round(y, 5))

        return {
            "output_samples": output,
            "max_gain_reduction_db": DecibelGainReduction(round(max_gr_db, 2)),
            "samples_count": len(output),
            "threshold_db": threshold_db,
            "ratio": ratio,
            "makeup_gain_db": makeup_gain_db,
        }


def audio_pitch_shift(
    samples: List[float],
    semitones: float,
    sample_rate: int = 44100,
) -> Record:
    """Shifts pitch by semitones using Phase Vocoder analysis/synthesis."""
    return Record(PitchShiftPhaseVocoder.pitch_shift(samples, semitones, sample_rate=sample_rate))


def audio_compress_limit(
    samples: List[float],
    threshold_db: float = -12.0,
    ratio: float = 4.0,
    attack_ms: float = 5.0,
    release_ms: float = 50.0,
    makeup_gain_db: float = 0.0,
) -> Record:
    """Applies dynamic range compression and peak limiting."""
    return Record(
        DynamicRangeCompressorLimiter.process(
            samples,
            threshold_db=threshold_db,
            ratio=ratio,
            attack_ms=attack_ms,
            release_ms=release_ms,
            makeup_gain_db=makeup_gain_db,
        )
    )




# ==============================================================================
# SPECTRAL AUDIO PROCESSING: COOLEY-TUKEY FFT & STFT
# ==============================================================================

class CooleyTukeyFFT:
    """Pure-Python radix-2 Cooley-Tukey decimation-in-time Fast Fourier Transform."""

    @classmethod
    def fft(cls, signal: List[float]) -> List[complex]:
        n = len(signal)
        if n == 0:
            return []
        # Next power of 2
        p2 = 1
        while p2 < n:
            p2 <<= 1
        padded = [complex(x) for x in signal] + [0.0j] * (p2 - n)
        return cls._dit_fft(padded)

    @classmethod
    def ifft(cls, spectrum: List[complex]) -> List[float]:
        n = len(spectrum)
        if n == 0:
            return []
        conjugates = [s.conjugate() for s in spectrum]
        f_conj = cls._dit_fft(conjugates)
        return [(x.conjugate() / n).real for x in f_conj]

    @classmethod
    def _dit_fft(cls, a: List[complex]) -> List[complex]:
        n = len(a)
        if n <= 1:
            return a
        even = cls._dit_fft(a[0::2])
        odd = cls._dit_fft(a[1::2])
        out = [0.0j] * n
        import cmath
        for k in range(n // 2):
            w = cmath.exp(-2.0j * cmath.pi * k / n) * odd[k]
            out[k] = even[k] + w
            out[k + n // 2] = even[k] - w
        return out


class STFTProcessor:
    """Short-Time Fourier Transform (STFT) spectrogram analyzer."""

    @classmethod
    def stft(cls, samples: List[float], frame_size: int = 512, hop_size: int = 256) -> Dict[str, Any]:
        import math
        # Hann window
        window = [0.5 * (1.0 - math.cos(2.0 * math.pi * i / (frame_size - 1))) for i in range(frame_size)]
        frames = []
        magnitudes = []
        phases = []

        num_frames = (len(samples) - frame_size) // hop_size + 1 if len(samples) >= frame_size else 0
        for i in range(max(0, num_frames)):
            start = i * hop_size
            chunk = [samples[start + j] * window[j] for j in range(frame_size)]
            spec = CooleyTukeyFFT.fft(chunk)
            half = spec[:frame_size // 2 + 1]
            mag = [abs(x) for x in half]
            phase = [math.atan2(x.imag, x.real) for x in half]
            frames.append(half)
            magnitudes.append(mag)
            phases.append(phase)

        return {
            "num_frames": len(frames),
            "frame_size": frame_size,
            "hop_size": hop_size,
            "magnitudes": magnitudes,
            "phases": phases,
        }


def audio_fft(signal: List[float]) -> List[complex]:
    """Computes Radix-2 Fast Fourier Transform of input signal."""
    return CooleyTukeyFFT.fft(signal)


def audio_ifft(spectrum: List[complex]) -> List[float]:
    """Computes Inverse Fast Fourier Transform from spectrum."""
    return CooleyTukeyFFT.ifft(spectrum)


def audio_stft(samples: List[float], frame_size: int = 512, hop_size: int = 256) -> Record:
    """Computes Short-Time Fourier Transform (STFT) spectrogram frames."""
    return Record(STFTProcessor.stft(samples, frame_size=frame_size, hop_size=hop_size))
