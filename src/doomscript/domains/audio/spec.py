"""Declarative specifications and Intermediate Representation for Audio domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class AudioLoadSpec(DomainIR):
    path_expr: str
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if not self.path_expr:
            errors.append("AudioLoadSpec requires a file path")
        if not self.target_var:
            errors.append("AudioLoadSpec requires a target variable")
        return errors


@dataclass
class AudioCreateSpec(DomainIR):
    duration: float
    sample_rate: int = 44100
    channels: int = 1
    target_var: str = "audio"

    def validate(self) -> List[str]:
        errors = []
        if self.duration <= 0:
            errors.append("Audio duration must be greater than zero")
        return errors


@dataclass
class AudioTrimSpec(DomainIR):
    audio_var: str
    start_sec: float
    end_sec: float
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if self.end_sec <= self.start_sec:
            errors.append("Audio trim end must be greater than start")
        return errors


@dataclass
class AudioFadeSpec(DomainIR):
    audio_var: str
    target_var: str
    fade_in_sec: float = 0.0
    fade_out_sec: float = 0.0

    def validate(self) -> List[str]:
        return []


@dataclass
class AudioVolumeSpec(DomainIR):
    audio_var: str
    db_change: float
    target_var: str

    def validate(self) -> List[str]:
        return []


@dataclass
class AudioCombineSpec(DomainIR):
    audio_list_var: str
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if not self.audio_list_var:
            errors.append("AudioCombineSpec requires a list of audio clips")
        return errors


@dataclass
class AudioSaveSpec(DomainIR):
    audio_var: str
    path_expr: str

    def validate(self) -> List[str]:
        errors = []
        if not self.path_expr:
            errors.append("AudioSaveSpec requires a destination file path")
        return errors
