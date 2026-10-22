from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.acoustics.runtime import (
    acoustics_spl_db, acoustics_sabine_rt60, acoustics_eyring_rt60,
    acoustics_doppler_shift, acoustics_inverse_square_decay,
    acoustics_characteristic_impedance, acoustics_sound_transmission_loss
)
from doomscript.domains.acoustics.parser import AcousticsDomainParser
from doomscript.domains.acoustics.exporter import AcousticsASTExporter

class AcousticsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class AcousticsDomain(DomainContract):
    name = "acoustics"
    aliases = ["sound_engineering", "psychoacoustics", "reverberation"]
    description = "Physical acoustics & architectural audio: SPL decibels, Sabine and Eyring RT60, Doppler shift, distance decay, and transmission loss"
    parser = AcousticsDomainParser()
    runtime = AcousticsRuntime()
    exporter = AcousticsASTExporter()
    capabilities = ["spl_db", "sabine_rt60", "eyring_rt60", "doppler_shift", "inverse_square_decay", "sound_transmission_loss"]
    verbs = [
        VerbSpec(pattern="calculate spl pressure {p:expr} into {target:ident}", description="Sound pressure level (dB)"),
        VerbSpec(pattern="calculate sabine rt60 volume {v:expr} absorption {a:expr} into {target:ident}", description="Sabine reverberation time"),
        VerbSpec(pattern="calculate eyring rt60 volume {v:expr} area {s:expr} absorption {a:expr} into {target:ident}", description="Eyring reverberation time"),
        VerbSpec(pattern="calculate doppler shift freq {f:expr} source_v {vs:expr} into {target:ident}", description="Doppler shifted frequency"),
        VerbSpec(pattern="calculate sound decay spl {spl:expr} r1 {r1:expr} r2 {r2:expr} into {target:ident}", description="Distance SPL attenuation"),
        VerbSpec(pattern="calculate sound transmission loss mass {m:expr} freq {f:expr} into {target:ident}", description="Sound transmission loss")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate spl ") or s.startswith("calculate sabine rt60 ") or s.startswith("calculate eyring rt60 ") or s.startswith("calculate doppler shift ") or s.startswith("calculate sound decay ") or s.startswith("calculate sound transmission loss ")

ACOUSTICS_DOMAIN = AcousticsDomain()
get_domain_registry().register(ACOUSTICS_DOMAIN)

__all__ = [
    "AcousticsDomain", "ACOUSTICS_DOMAIN", "AcousticsRuntime",
    "acoustics_spl_db", "acoustics_sabine_rt60", "acoustics_eyring_rt60",
    "acoustics_doppler_shift", "acoustics_inverse_square_decay",
    "acoustics_characteristic_impedance", "acoustics_sound_transmission_loss"
]
