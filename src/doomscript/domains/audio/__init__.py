"""Audio & Sound Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.audio.spec import (
    AudioLoadSpec,
    AudioCreateSpec,
    AudioTrimSpec,
    AudioFadeSpec,
    AudioVolumeSpec,
    AudioCombineSpec,
    AudioSaveSpec,
)
from doomscript.domains.audio.parser import AudioDomainParser
from doomscript.domains.audio.runtime import (
    DoomAudio,
    AudioRuntime,
    load_audio,
    create_blank_audio,
    audio_duration,
    trim_audio,
    fade_audio,
    adjust_audio_volume,
    combine_audio,
    save_audio,
    execute_audio_ir,
    audio_generate_square,
    audio_generate_sawtooth,
    audio_generate_triangle,
    audio_generate_white_noise,
    audio_adjust_gain_db,
    audio_trim_silence,
    audio_apply_fade_out,
    audio_mix_tracks,
    audio_pan_stereo,
    audio_low_pass_filter,
    audio_high_pass_filter,
    audio_peak_amplitude,
    audio_rms_energy,
    audio_zero_crossing_rate,
    audio_clip_samples,
    audio_loop_track,
    audio_delay_echo,
    audio_time_stretch_naive,
    audio_generate_silence,
    audio_fft,
    audio_ifft,
    audio_stft_spectrogram,
    audio_mel_spectrogram,
    audio_mfcc,
    audio_biquad_filter,
    PolyphonicSynth,
    YINPitchDetector,
    ParametricEQ,
    audio_poly_synth_render,
    audio_yin_pitch,
    audio_parametric_eq,
    HighOrderAmbisonics3D,
    DynamicRangeCompressorLimiter,
    audio_hoa_3d_encode,
    audio_hoa_binaural_decode,
    audio_dynamic_compressor,
    LPCVocoderLinearPredictiveCoding,
    BiquadIIRFilterCascaded,
    audio_lpc_analyze_synthesize,
    audio_biquad_eq_filter,
    PitchShiftPhaseVocoder,
    audio_pitch_shift,
    audio_compress_limit,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.audio.exporter import AudioASTExporter
from doomscript.domains.registry import get_domain_registry


class AudioDomain(DomainContract):
    """Audio & Sound domain pack."""

    name = "audio"
    aliases = ["sound", "music"]
    description = "Audio & Sound processing, waveform manipulation, trims, fades, volume, combination"
    parser = AudioDomainParser()
    runtime = AudioRuntime()
    exporter = AudioASTExporter()
    capabilities = ["audio", "waveform", "trim", "fade", "volume", "combine"]
    optional_dependencies = ["scipy", "soundfile"]

    verbs = [
        VerbSpec(
            name="load_audio",
            pattern="load audio [from] {path_expr:expr} into {target:ident}",
            arg_schema={"path_expr": "expr", "target": "ident"},
            returns="Audio",
            description="Load WAV, MP3, or FLAC audio file",
        ),
        VerbSpec(
            name="create_blank_audio",
            pattern="create blank audio of {duration_expr:expr} [seconds] into {target:ident}",
            arg_schema={"duration_expr": "expr", "target": "ident"},
            returns="Audio",
            description="Create silence or blank audio buffer",
        ),
        VerbSpec(
            name="trim_audio",
            pattern="trim [audio] {audio_var:ident} from {start_expr:expr} to {end_expr:expr} into {target:ident}",
            arg_schema={"audio_var": "ident", "start_expr": "expr", "end_expr": "expr", "target": "ident"},
            returns="Audio",
            description="Extract time slice of audio",
        ),
        VerbSpec(
            name="fade_audio",
            pattern="fade (in|out) [audio] {audio_var:ident} over {duration_expr:expr} [seconds] into {target:ident}",
            arg_schema={"audio_var": "ident", "duration_expr": "expr", "target": "ident"},
            returns="Audio",
            description="Apply linear or exponential volume envelope fade",
        ),
        VerbSpec(
            name="adjust_volume",
            pattern="adjust volume of [audio] {audio_var:ident} by {factor_expr:expr} into {target:ident}",
            arg_schema={"audio_var": "ident", "factor_expr": "expr", "target": "ident"},
            returns="Audio",
            description="Scale amplitude or dB gain",
        ),
        VerbSpec(
            name="combine_audio",
            pattern="combine audio {first_var:ident} and {second_var:ident} into {target:ident}",
            arg_schema={"first_var": "ident", "second_var": "ident", "target": "ident"},
            returns="Audio",
            description="Concatenate two audio buffers sequentially",
        ),
        VerbSpec(
            name="save_audio",
            pattern="save audio {audio_var:ident} to {path_expr:expr}",
            arg_schema={"audio_var": "ident", "path_expr": "expr"},
            returns="str",
            description="Write audio track to disk as WAV",
        ),
        VerbSpec(
            name="audio_duration",
            pattern="duration of [audio] {audio_var:ident} into {target:ident}",
            arg_schema={"audio_var": "ident", "target": "ident"},
            returns="float",
            description="Get duration of audio clip in seconds",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        if (
            s.startswith("load audio ")
            or s.startswith("create blank audio ")
            or s.startswith("combine audio ")
            or s.startswith("save audio ")
            or s.startswith("adjust volume of ")
            or s.startswith("generate sine tone ")
            or s.startswith("normalize audio ")
            or s.startswith("audio duration of ")
            or s.startswith("get duration of ")
            or s.startswith("fade in audio ")
            or s.startswith("apply fade in ")
            or s.startswith("reverse audio ")
            or s.startswith("concatenate audio ")
            or s.startswith("generate square wave ")
            or s.startswith("generate sawtooth wave ")
            or s.startswith("generate triangle wave ")
            or s.startswith("generate white noise ")
            or s.startswith("adjust gain of ")
            or s.startswith("trim silence from ")
            or s.startswith("apply fade out ")
            or s.startswith("fade out ")
            or s.startswith("mix audio tracks ")
            or s.startswith("mix tracks ")
            or s.startswith("pan audio ")
            or s.startswith("pan stereo ")
            or s.startswith("apply low pass filter ")
            or s.startswith("apply lowpass filter ")
            or s.startswith("low pass filter ")
            or s.startswith("lowpass filter ")
            or s.startswith("apply high pass filter ")
            or s.startswith("apply highpass filter ")
            or s.startswith("high pass filter ")
            or s.startswith("highpass filter ")
            or s.startswith("peak amplitude of ")
            or s.startswith("rms energy of ")
            or s.startswith("zero crossing rate of ")
            or s.startswith("clip audio ")
            or s.startswith("loop audio ")
            or s.startswith("apply echo delay ")
            or s.startswith("apply delay echo ")
            or s.startswith("time stretch ")
            or s.startswith("generate silence ")
            or s.startswith("pitch shift audio ")
            or s.startswith("apply dynamic range limiter ")
        ):
            return True

        if s.startswith("trim ") and "from" in s and "to" in s:
            return True
        if s.startswith("fade ") and ("in " in s or "out " in s):
            return True
        if s.startswith("duration of ") and ("audio" in s or "track" in s or "clip" in s):
            return True

        from doomscript.domains.registry import get_domain_registry
        if get_domain_registry().is_active("audio"):
            if s.startswith("duration of ") and " into " in s:
                return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
AUDIO_DOMAIN = AudioDomain()
get_domain_registry().register(AUDIO_DOMAIN)

__all__ = [
    "AudioDomain",
    "AUDIO_DOMAIN",
    "AudioLoadSpec",
    "AudioCreateSpec",
    "AudioTrimSpec",
    "AudioFadeSpec",
    "AudioVolumeSpec",
    "AudioCombineSpec",
    "AudioSaveSpec",
    "AudioDomainParser",
    "AudioRuntime",
    "AudioASTExporter",
    "DoomAudio",
    "load_audio",
    "create_blank_audio",
    "audio_duration",
    "trim_audio",
    "fade_audio",
    "adjust_audio_volume",
    "combine_audio",
    "save_audio",
    "execute_audio_ir",
    "audio_generate_square",
    "audio_generate_sawtooth",
    "audio_generate_triangle",
    "audio_generate_white_noise",
    "audio_adjust_gain_db",
    "audio_trim_silence",
    "audio_apply_fade_out",
    "audio_mix_tracks",
    "audio_pan_stereo",
    "audio_low_pass_filter",
    "audio_high_pass_filter",
    "audio_peak_amplitude",
    "audio_rms_energy",
    "audio_zero_crossing_rate",
    "audio_clip_samples",
    "audio_loop_track",
    "audio_delay_echo",
    "audio_time_stretch_naive",
    "audio_generate_silence",
    "audio_fft",
    "audio_ifft",
    "audio_stft_spectrogram",
    "audio_mel_spectrogram",
    "audio_mfcc",
    "audio_biquad_filter",
    "PolyphonicSynth",
    "YINPitchDetector",
    "ParametricEQ",
    "audio_poly_synth_render",
    "audio_yin_pitch",
    "audio_parametric_eq",
    "HighOrderAmbisonics3D",
    "DynamicRangeCompressorLimiter",
    "audio_hoa_3d_encode",
    "audio_hoa_binaural_decode",
    "audio_dynamic_compressor",
    "LPCVocoderLinearPredictiveCoding",
    "BiquadIIRFilterCascaded",
    "audio_lpc_analyze_synthesize",
    "audio_biquad_eq_filter",
    "PitchShiftPhaseVocoder",
    "audio_pitch_shift",
    "audio_compress_limit",
]

