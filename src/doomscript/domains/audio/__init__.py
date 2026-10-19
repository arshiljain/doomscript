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
from doomscript.domains.audio.exporter import AudioASTExporter
from doomscript.domains.registry import get_domain_registry


class AudioDomain(DomainContract):
    """Audio & Sound domain pack."""

    name = "audio"
    aliases = ["sound", "music"]
    parser = AudioDomainParser()
    runtime = AudioRuntime()
    exporter = AudioASTExporter()

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
