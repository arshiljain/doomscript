"""3D Spatial Audio, Ambisonics & Psychoacoustics Domain Pack for DoomScript.

Enables native spoken-English binaural ITD/ILD spatialization, Ambisonics B-format,
Doppler shifting, and Schroeder algorithmic reverb via 'use spatial_audio'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.spatial_audio.runtime import (
    BinauralPanner,
    AmbisonicsBFormat,
    DopplerEffect,
    SchroederReverberator,
    spatial_audio_binaural,
    spatial_audio_ambisonics_encode,
    spatial_audio_ambisonics_decode_stereo,
    spatial_audio_doppler,
    spatial_audio_schroeder_reverb,
    HigherOrderAmbisonics,
    AcousticRaytracer,
    HRTFConvolution,
    VectorBaseAmplitudePanning,
    AtmosphericAttenuation,
    spatial_audio_hoa_encode,
    spatial_audio_room_impulse_response,
    spatial_audio_hrtf_binaural,
    spatial_audio_vbap_2d,
    spatial_audio_distance_attenuate,
    RoomImageSourceEarlyReflections,
    ConvolveImpulseResponse,
    spatial_audio_early_reflections,
    spatial_audio_convolve_ir,
    HigherOrderSphericalHarmonics3D,
    AcousticRayTracingShoebox,
    spatial_audio_spherical_harmonics_encode,
    spatial_audio_ray_trace_room,
    BinauralRoomImpulseResponseBRIRGenerator,
    AmbisonicsBFormatBinauralDecoder,
    spatial_generate_brir,
    spatial_ambisonics_binaural_decode,
)
from doomscript.domains.spatial_audio.parser import SpatialAudioDomainParser
from doomscript.domains.spatial_audio.exporter import SpatialAudioASTExporter


class SpatialAudioRuntime(DomainRuntime):
    """Runtime coordinator for spatial audio routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class SpatialAudioDomain(DomainContract):
    """Domain contract for 3D Spatial Audio & Ambisonics."""

    name = "spatial_audio"
    aliases = ["spatialaudio", "binaural", "ambisonics", "hrtf"]
    description = "Binaural audio rendering, Woodworth ITD, First-Order Ambisonics, Doppler shifting, and Schroeder reverb"
    parser = SpatialAudioDomainParser()
    runtime = SpatialAudioRuntime()
    exporter = SpatialAudioASTExporter()
    capabilities = ["binaural", "ambisonics", "doppler", "reverb"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="spatialize audio {sig:expr} at azimuth {az:expr} into {target:ident}",
            description="Pans mono audio into binaural stereo channels using ITD/ILD",
        ),
        VerbSpec(
            pattern="encode ambisonics {sig:expr} at azimuth {az:expr} elevation {el:expr} into {target:ident}",
            description="Encodes audio into Ambisonics B-format (W, X, Y, Z)",
        ),
        VerbSpec(
            pattern="apply reverb to {sig:expr} with rt60 {rt60:expr} into {target:ident}",
            description="Applies Schroeder algorithmic reverberation",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("spatialize audio ")
            or s.startswith("encode ambisonics ")
            or s.startswith("apply reverb to ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


SPATIAL_AUDIO_DOMAIN = SpatialAudioDomain()
get_domain_registry().register(SPATIAL_AUDIO_DOMAIN)

__all__ = [
    "SpatialAudioDomain",
    "SPATIAL_AUDIO_DOMAIN",
    "SpatialAudioRuntime",
    "BinauralPanner",
    "AmbisonicsBFormat",
    "DopplerEffect",
    "SchroederReverberator",
    "spatial_audio_binaural",
    "spatial_audio_ambisonics_encode",
    "spatial_audio_ambisonics_decode_stereo",
    "spatial_audio_doppler",
    "spatial_audio_schroeder_reverb",
    "HigherOrderAmbisonics",
    "AcousticRaytracer",
    "HRTFConvolution",
    "spatial_audio_hoa_encode",
    "spatial_audio_room_impulse_response",
    "spatial_audio_hrtf_binaural",
    "spatial_audio_vbap_2d",
    "spatial_audio_distance_attenuate",
    "RoomImageSourceEarlyReflections",
    "ConvolveImpulseResponse",
    "spatial_audio_early_reflections",
    "spatial_audio_convolve_ir",
    "HigherOrderSphericalHarmonics3D",
    "AcousticRayTracingShoebox",
    "spatial_audio_spherical_harmonics_encode",
    "spatial_audio_ray_trace_room",
    "BinauralRoomImpulseResponseBRIRGenerator",
    "AmbisonicsBFormatBinauralDecoder",
    "spatial_generate_brir",
    "spatial_ambisonics_binaural_decode",
]
