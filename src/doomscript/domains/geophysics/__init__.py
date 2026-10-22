from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.geophysics.runtime import (
    geo_epicentral_distance, geo_richter_magnitude,
    geo_snell_refraction_angle, geo_bouguer_anomaly,
    geo_geothermal_heat_flow
)
from doomscript.domains.geophysics.parser import GeophysicsDomainParser
from doomscript.domains.geophysics.exporter import GeophysicsASTExporter

class GeophysicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class GeophysicsDomain(DomainContract):
    name = "geophysics"
    aliases = ["seismology", "earth_physics", "geodynamics"]
    description = "Geophysical analytics: Epicentral distance, Richter magnitude, Snell refraction, Bouguer anomaly"
    parser = GeophysicsDomainParser()
    runtime = GeophysicsRuntime()
    exporter = GeophysicsASTExporter()
    capabilities = ["epicentral_distance", "richter_magnitude", "snell_refraction", "bouguer_anomaly", "geothermal_heat_flow"]
    verbs = [
        VerbSpec(pattern="calculate epicentral distance for p arrival {tp:expr} s arrival {ts:expr} into {target:ident}", description="Epicentral distance"),
        VerbSpec(pattern="calculate richter magnitude for amplitude {amp:expr} distance {dist:expr} into {target:ident}", description="Richter magnitude")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate epicentral distance ") or s.startswith("calculate richter magnitude ") or s.startswith("calculate seismic refraction ") or s.startswith("calculate bouguer anomaly ") or s.startswith("calculate geothermal heat flow ")

GEOPHYSICS_DOMAIN = GeophysicsDomain()
get_domain_registry().register(GEOPHYSICS_DOMAIN)

__all__ = [
    "GeophysicsDomain", "GEOPHYSICS_DOMAIN", "GeophysicsRuntime",
    "geo_epicentral_distance", "geo_richter_magnitude",
    "geo_snell_refraction_angle", "geo_bouguer_anomaly",
    "geo_geothermal_heat_flow"
]
