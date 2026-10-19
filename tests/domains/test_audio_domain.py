"""Unit and integration tests for Audio & Sound domain (use audio)."""

import os
import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.audio.runtime import (
    DoomAudio,
    load_audio,
    create_blank_audio,
    audio_duration,
    trim_audio,
    fade_audio,
    adjust_audio_volume,
    combine_audio,
    save_audio,
)


def test_audio_runtime_direct(tmp_path):
    clip = create_blank_audio(1.5, sample_rate=44100, channels=2)
    assert abs(audio_duration(clip) - 1.5) < 0.01

    # Trim
    trimmed = trim_audio(clip, 0.5, 1.0)
    assert abs(audio_duration(trimmed) - 0.5) < 0.01

    # Fade
    faded = fade_audio(trimmed, fade_in_sec=0.1, fade_out_sec=0.1)
    assert faded is not None

    # Volume
    boosted = adjust_audio_volume(clip, 3.0)
    assert boosted is not None

    # Combine
    combined = combine_audio([clip, clip])
    assert abs(audio_duration(combined) - 3.0) < 0.01

    # Save & Load
    out_file = str(tmp_path / "test.wav")
    save_audio(clip, out_file)
    assert os.path.exists(out_file)
    assert os.path.getsize(out_file) > 44

    loaded = load_audio(out_file)
    assert abs(audio_duration(loaded) - 1.5) < 0.01


def test_audio_domain_script_execution(tmp_path):
    out_wav = str(tmp_path / "ambient.wav").replace("\\", "/")
    source = f"""use audio

create blank audio with duration 2.0 into sound
duration of sound into initial_dur
trim sound from 0.5 to 1.5 into short_clip
fade short_clip in 0.1 and fade out 0.1 into faded
adjust volume of faded by 3 into boosted
save audio boosted to "{out_wav}"
"""
    env = execute(source)
    assert abs(env["initial_dur"] - 2.0) < 0.01
    assert abs(audio_duration(env["short_clip"]) - 1.0) < 0.01
    assert os.path.exists(out_wav)


def test_audio_domain_python_export():
    source = """use audio

create blank audio with duration 1.0 into clip
trim clip from 0.2 to 0.8 into short_clip
save audio short_clip to "out.wav"
"""
    py_code = export_to_python(source)
    assert "create_blank_audio" in py_code
    assert "trim_audio" in py_code
    assert "save_audio" in py_code
