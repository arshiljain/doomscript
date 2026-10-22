from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.electromagnetics.runtime import (
    em_biot_savart_wire, em_skin_depth,
    em_poynting_vector_magnitude, em_coaxial_characteristic_impedance,
    em_plane_wave_attenuation, em_faraday_induced_emf
)
from doomscript.domains.electromagnetics.parser import ElectromagneticsDomainParser
from doomscript.domains.electromagnetics.exporter import ElectromagneticsASTExporter

class ElectromagneticsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class ElectromagneticsDomain(DomainContract):
    name = "electromagnetics"
    aliases = ["em", "emag", "maxwell"]
    description = "Electromagnetics: Biot-Savart law, conductor skin depth, Poynting vector, coaxial impedance, plane wave attenuation, and Faraday induced EMF"
    parser = ElectromagneticsDomainParser()
    runtime = ElectromagneticsRuntime()
    exporter = ElectromagneticsASTExporter()
    capabilities = ["biot_savart_wire", "skin_depth", "poynting_vector", "coax_impedance", "wave_attenuation", "faraday_emf"]
    verbs = [
        VerbSpec(pattern="calculate magnetic field wire current {i:expr} distance {r:expr} into {target:ident}", description="Biot-Savart magnetic field"),
        VerbSpec(pattern="calculate skin depth freq {f:expr} conductivity {s:expr} perm {ur:expr} into {target:ident}", description="Conductor skin depth"),
        VerbSpec(pattern="calculate poynting vector efield {e:expr} hfield {h:expr} into {target:ident}", description="Poynting power flux"),
        VerbSpec(pattern="calculate coax impedance inner {a:expr} outer {b:expr} eps {er:expr} into {target:ident}", description="Coaxial line impedance"),
        VerbSpec(pattern="calculate wave attenuation freq {f:expr} conductivity {s:expr} eps {er:expr} perm {ur:expr} into {target:ident}", description="Plane wave attenuation"),
        VerbSpec(pattern="calculate faraday emf turns {n:expr} flux {dphi:expr} time {dt:expr} into {target:ident}", description="Faraday induced EMF")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate magnetic field wire ") or s.startswith("calculate skin depth ") or s.startswith("calculate poynting vector ") or s.startswith("calculate coax impedance ") or s.startswith("calculate wave attenuation ") or s.startswith("calculate faraday emf ")

ELECTROMAGNETICS_DOMAIN = ElectromagneticsDomain()
get_domain_registry().register(ELECTROMAGNETICS_DOMAIN)

__all__ = [
    "ElectromagneticsDomain", "ELECTROMAGNETICS_DOMAIN", "ElectromagneticsRuntime",
    "em_biot_savart_wire", "em_skin_depth",
    "em_poynting_vector_magnitude", "em_coaxial_characteristic_impedance",
    "em_plane_wave_attenuation", "em_faraday_induced_emf"
]
