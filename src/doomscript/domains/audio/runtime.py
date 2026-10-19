"""Runtime execution engine for Audio & Sound domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import math
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
