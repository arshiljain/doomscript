from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.acoustics.runtime import (
    AcousticsRuntime, acoustics_spl_db, acoustics_sabine_rt60,
    acoustics_eyring_rt60, acoustics_doppler_shift,
    acoustics_inverse_square_decay, acoustics_characteristic_impedance,
    acoustics_sound_transmission_loss, acoustics_a_weighting,
    acoustics_phon_to_sone, acoustics_schroeder_frequency, acoustics_room_modes
)
from doomscript.domains.acoustics.parser import AcousticsDomainParser
from doomscript.domains.acoustics.exporter import AcousticsASTExporter

class AcousticsDomain(DomainContract):
    name = "acoustics"
    aliases = ["sound_engineering", "psychoacoustics", "reverberation"]
    description = "Deepened Acoustics domain: Sound Pressure Level, Sabine/Eyring RT60, Doppler shift, A-weighting, transmission loss, and room acoustics"
    parser = AcousticsDomainParser()
    runtime = AcousticsRuntime()
    exporter = AcousticsASTExporter()
    capabilities = ["spl_db", "sabine_rt60", "eyring_rt60", "doppler_shift", "sound_decay", "sound_transmission_loss", "a_weighting", "schroeder_frequency"]
    verbs = [
        VerbSpec(pattern="calculate spl pressure {p:expr} into {target:ident}", description="Sound pressure level (dB SPL)"),
        VerbSpec(pattern="calculate sabine rt60 volume {v:expr} absorption {a:expr} into {target:ident}", description="Sabine reverberation time"),
        VerbSpec(pattern="calculate eyring rt60 volume {v:expr} area {s:expr} absorption {alpha:expr} into {target:ident}", description="Eyring reverberation time"),
        VerbSpec(pattern="calculate doppler shift freq {f:expr} source_v {vs:expr} into {target:ident}", description="Doppler frequency shift"),
        VerbSpec(pattern="calculate sound decay spl {spl:expr} r1 {r1:expr} r2 {r2:expr} into {target:ident}", description="Inverse square sound drop"),
        VerbSpec(pattern="calculate sound transmission loss mass {m:expr} freq {f:expr} into {target:ident}", description="Sound transmission loss (mass law)"),
        VerbSpec(pattern="calculate a weighting freq {f:expr} into {target:ident}", description="IEC A-weighting filter"),
        VerbSpec(pattern="calculate schroeder frequency volume {v:expr} rt60 {rt:expr} into {target:ident}", description="Schroeder cutoff frequency")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate spl ") or
            s.startswith("calculate sabine rt60 ") or
            s.startswith("calculate eyring rt60 ") or
            s.startswith("calculate doppler shift ") or
            s.startswith("calculate sound decay ") or
            s.startswith("calculate sound transmission loss ") or
            s.startswith("calculate a weighting ") or
            s.startswith("calculate schroeder frequency ")
        )

ACOUSTICS_DOMAIN = AcousticsDomain()
get_domain_registry().register(ACOUSTICS_DOMAIN)

__all__ = [
    "ACOUSTICS_DOMAIN", "AcousticsDomain", "AcousticsRuntime",
    "acoustics_spl_db", "acoustics_sabine_rt60", "acoustics_eyring_rt60",
    "acoustics_doppler_shift", "acoustics_inverse_square_decay",
    "acoustics_characteristic_impedance", "acoustics_sound_transmission_loss",
    "acoustics_a_weighting", "acoustics_phon_to_sone",
    "acoustics_schroeder_frequency", "acoustics_room_modes"
]
