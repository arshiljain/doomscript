from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.geophysics.runtime import (
    geo_epicentral_distance, geo_richter_magnitude, geo_moment_magnitude,
    geo_snell_refraction_angle, geo_bouguer_anomaly,
    geo_apparent_resistivity_wenner, geo_geothermal_heat_flow
)
from doomscript.domains.geophysics.parser import GeophysicsDomainParser
from doomscript.domains.geophysics.exporter import GeophysicsASTExporter

class GeophysicsRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class GeophysicsDomain(DomainContract):
    name = "geophysics"
    aliases = ["seismology", "earth_physics", "geodynamics"]
    description = "Geophysical analytics: Wadati epicentral distance, Richter/Moment magnitude, Snell refraction, Bouguer anomaly, and resistivity"
    parser = GeophysicsDomainParser()
    runtime = GeophysicsRuntime()
    exporter = GeophysicsASTExporter()
    capabilities = ["epicentral_distance", "richter_magnitude", "moment_magnitude", "snell_refraction", "bouguer_anomaly", "apparent_resistivity", "geothermal_heat_flow"]
    verbs = [
        VerbSpec(pattern="calculate epicentral distance for p arrival {tp:expr} s arrival {ts:expr} into {target:ident}", description="Epicentral distance"),
        VerbSpec(pattern="calculate moment magnitude area {a:expr} slip {s:expr} into {target:ident}", description="Moment magnitude"),
        VerbSpec(pattern="calculate apparent resistivity spacing {a:expr} resistance {r:expr} into {target:ident}", description="Apparent resistivity")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate epicentral distance ") or s.startswith("calculate richter magnitude ") or s.startswith("calculate moment magnitude ") or s.startswith("calculate seismic refraction ") or s.startswith("calculate bouguer anomaly ") or s.startswith("calculate apparent resistivity ") or s.startswith("calculate geothermal heat flow ")

GEOPHYSICS_DOMAIN = GeophysicsDomain()
get_domain_registry().register(GEOPHYSICS_DOMAIN)

__all__ = [
    "GeophysicsDomain", "GEOPHYSICS_DOMAIN", "GeophysicsRuntime",
    "geo_epicentral_distance", "geo_richter_magnitude", "geo_moment_magnitude",
    "geo_snell_refraction_angle", "geo_bouguer_anomaly",
    "geo_apparent_resistivity_wenner", "geo_geothermal_heat_flow"
]
