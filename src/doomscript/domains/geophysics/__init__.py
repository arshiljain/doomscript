from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.geophysics.runtime import (
    GeophysicsRuntime, geo_epicentral_distance, geo_richter_magnitude,
    geo_moment_magnitude, geo_snell_refraction_angle, geo_bouguer_anomaly,
    geo_apparent_resistivity_wenner, geo_geothermal_heat_flow,
    geo_seismic_refraction_layer, geo_geomagnetic_dipole, geo_isostasy_root_thickness
)
from doomscript.domains.geophysics.parser import GeophysicsDomainParser
from doomscript.domains.geophysics.exporter import GeophysicsASTExporter

class GeophysicsDomain(DomainContract):
    name = "geophysics"
    aliases = ["seismology", "earth_physics", "geodynamics"]
    description = "Deepened Geophysics domain: Epicentral distance, Richter/Moment magnitude, seismic refraction, Bouguer anomaly, geomagnetic dipole, and apparent resistivity"
    parser = GeophysicsDomainParser()
    runtime = GeophysicsRuntime()
    exporter = GeophysicsASTExporter()
    capabilities = ["epicentral_distance", "richter_magnitude", "moment_magnitude", "snell_refraction", "bouguer_anomaly", "apparent_resistivity", "geothermal_heat_flow", "seismic_refraction_layer", "geomagnetism", "isostasy"]
    verbs = [
        VerbSpec(pattern="calculate epicentral distance for p arrival {tp:expr} s arrival {ts:expr} into {target:ident}", description="Wadati epicentral distance"),
        VerbSpec(pattern="calculate richter magnitude amplitude {a:expr} distance {d:expr} into {target:ident}", description="Richter magnitude ML"),
        VerbSpec(pattern="calculate moment magnitude area {a:expr} slip {s:expr} into {target:ident}", description="Moment magnitude Mw"),
        VerbSpec(pattern="calculate seismic refraction angle {inc:expr} v1 {v1:expr} v2 {v2:expr} into {target:ident}", description="Seismic Snell refraction"),
        VerbSpec(pattern="calculate bouguer anomaly obs {obs:expr} theo {theo:expr} elevation {h:expr} density {rho:expr} into {target:ident}", description="Simple Bouguer anomaly"),
        VerbSpec(pattern="calculate apparent resistivity spacing {a:expr} resistance {r:expr} into {target:ident}", description="Wenner apparent resistivity"),
        VerbSpec(pattern="calculate geothermal heat flow conductivity {k:expr} gradient {g:expr} into {target:ident}", description="Terrestrial geothermal heat flow")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate epicentral distance ") or
            s.startswith("calculate richter magnitude ") or
            s.startswith("calculate moment magnitude ") or
            s.startswith("calculate seismic refraction ") or
            s.startswith("calculate bouguer anomaly ") or
            s.startswith("calculate apparent resistivity ") or
            s.startswith("calculate geothermal heat flow ")
        )

GEOPHYSICS_DOMAIN = GeophysicsDomain()
get_domain_registry().register(GEOPHYSICS_DOMAIN)

__all__ = [
    "GEOPHYSICS_DOMAIN", "GeophysicsDomain", "GeophysicsRuntime",
    "geo_epicentral_distance", "geo_richter_magnitude", "geo_moment_magnitude",
    "geo_snell_refraction_angle", "geo_bouguer_anomaly",
    "geo_apparent_resistivity_wenner", "geo_geothermal_heat_flow",
    "geo_seismic_refraction_layer", "geo_geomagnetic_dipole", "geo_isostasy_root_thickness"
]
