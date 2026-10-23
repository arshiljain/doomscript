from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.electromagnetics.runtime import (
    ElectromagneticsRuntime, em_biot_savart_wire, em_skin_depth,
    em_poynting_vector_magnitude, em_coaxial_characteristic_impedance,
    em_plane_wave_attenuation, em_faraday_induced_emf,
    em_vswr_reflection, em_cyclotron_resonance, em_solenoid_inductance
)
from doomscript.domains.electromagnetics.parser import ElectromagneticsDomainParser
from doomscript.domains.electromagnetics.exporter import ElectromagneticsASTExporter

class ElectromagneticsDomain(DomainContract):
    name = "electromagnetics"
    aliases = ["em", "emag", "maxwell"]
    description = "Deepened Electromagnetics domain: Maxwell equations, Biot-Savart, skin depth, Poynting vector, coax impedance, plane waves, and RF transmission"
    parser = ElectromagneticsDomainParser()
    runtime = ElectromagneticsRuntime()
    exporter = ElectromagneticsASTExporter()
    capabilities = ["biot_savart", "skin_depth", "poynting_vector", "coax_impedance", "plane_wave_attenuation", "faraday_emf", "vswr", "cyclotron", "solenoid_inductance"]
    verbs = [
        VerbSpec(pattern="calculate magnetic field wire current {i:expr} distance {r:expr} into {target:ident}", description="Biot-Savart straight wire magnetic field"),
        VerbSpec(pattern="calculate skin depth freq {f:expr} conductivity {sigma:expr} perm {ur:expr} into {target:ident}", description="Electromagnetic conductor skin depth"),
        VerbSpec(pattern="calculate poynting vector efield {e:expr} hfield {h:expr} into {target:ident}", description="Poynting power flux vector magnitude"),
        VerbSpec(pattern="calculate coax impedance inner {a:expr} outer {b:expr} eps {eps:expr} into {target:ident}", description="Coaxial cable characteristic impedance"),
        VerbSpec(pattern="calculate wave attenuation freq {f:expr} conductivity {sigma:expr} eps {eps:expr} perm {ur:expr} into {target:ident}", description="Lossy dielectric plane wave attenuation"),
        VerbSpec(pattern="calculate faraday emf turns {n:expr} flux {flux:expr} time {dt:expr} into {target:ident}", description="Faraday induced electromotive force"),
        VerbSpec(pattern="calculate vswr zl {zl:expr} z0 {z0:expr} into {target:ident}", description="RF transmission line VSWR and reflection")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate magnetic field wire ") or
            s.startswith("calculate skin depth ") or
            s.startswith("calculate poynting vector ") or
            s.startswith("calculate coax impedance ") or
            s.startswith("calculate wave attenuation ") or
            s.startswith("calculate faraday emf ") or
            s.startswith("calculate vswr ")
        )

ELECTROMAGNETICS_DOMAIN = ElectromagneticsDomain()
get_domain_registry().register(ELECTROMAGNETICS_DOMAIN)

__all__ = [
    "ELECTROMAGNETICS_DOMAIN", "ElectromagneticsDomain", "ElectromagneticsRuntime",
    "em_biot_savart_wire", "em_skin_depth",
    "em_poynting_vector_magnitude", "em_coaxial_characteristic_impedance",
    "em_plane_wave_attenuation", "em_faraday_induced_emf",
    "em_vswr_reflection", "em_cyclotron_resonance", "em_solenoid_inductance"
]
