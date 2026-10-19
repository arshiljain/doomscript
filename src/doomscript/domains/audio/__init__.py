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
        s = line.strip().lower()
        if (
            s.startswith("load audio ")
            or s.startswith("create blank audio ")
            or s.startswith("combine audio ")
            or s.startswith("save audio ")
            or s.startswith("adjust volume of ")
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
]
