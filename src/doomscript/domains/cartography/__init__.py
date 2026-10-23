from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.cartography.runtime import (
    CartographyRuntime, carto_haversine_distance, carto_initial_bearing,
    carto_mercator_projection, carto_utm_zone, carto_ground_distance,
    carto_tissot_indicatrix_distortion, carto_wgs84_to_ecef,
    carto_rhumb_line_distance
)
from doomscript.domains.cartography.parser import CartographyDomainParser
from doomscript.domains.cartography.exporter import CartographyASTExporter

class CartographyDomain(DomainContract):
    name = "cartography"
    aliases = ["carto", "map_projection", "geodesy"]
    description = "Deepened Cartography domain: Haversine distance, initial bearing, Mercator projection, UTM zones, map scales, WGS84 geodesy, and Rhumb lines"
    parser = CartographyDomainParser()
    runtime = CartographyRuntime()
    exporter = CartographyASTExporter()
    capabilities = ["haversine_distance", "initial_bearing", "mercator_projection", "utm_zone", "ground_distance", "tissot_distortion", "wgs84_ecef", "rhumb_line"]
    verbs = [
        VerbSpec(pattern="calculate haversine distance lat1 {lat1:expr} lon1 {lon1:expr} lat2 {lat2:expr} lon2 {lon2:expr} into {target:ident}", description="Haversine great circle distance"),
        VerbSpec(pattern="calculate initial bearing lat1 {lat1:expr} lon1 {lon1:expr} lat2 {lat2:expr} lon2 {lon2:expr} into {target:ident}", description="Initial spherical azimuth"),
        VerbSpec(pattern="calculate mercator projection lat {lat:expr} lon {lon:expr} into {target:ident}", description="Mercator forward projection"),
        VerbSpec(pattern="calculate utm zone lon {lon:expr} into {target:ident}", description="Universal Transverse Mercator zone"),
        VerbSpec(pattern="calculate ground distance map_cm {cm:expr} scale {scale:expr} into {target:ident}", description="Map scale to ground distance"),
        VerbSpec(pattern="calculate mercator distortion lat {lat:expr} into {target:ident}", description="Tissot indicatrix Mercator distortion"),
        VerbSpec(pattern="calculate wgs84 ecef lat {lat:expr} lon {lon:expr} height {h:expr} into {target:ident}", description="WGS84 geodetic to ECEF 3D Cartesian")
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate haversine distance ") or
            s.startswith("calculate initial bearing ") or
            s.startswith("calculate mercator projection ") or
            s.startswith("calculate utm zone ") or
            s.startswith("calculate ground distance ") or
            s.startswith("calculate mercator distortion ") or
            s.startswith("calculate wgs84 ecef ")
        )

CARTOGRAPHY_DOMAIN = CartographyDomain()
get_domain_registry().register(CARTOGRAPHY_DOMAIN)

__all__ = [
    "CARTOGRAPHY_DOMAIN", "CartographyDomain", "CartographyRuntime",
    "carto_haversine_distance", "carto_initial_bearing",
    "carto_mercator_projection", "carto_utm_zone",
    "carto_ground_distance", "carto_tissot_indicatrix_distortion",
    "carto_wgs84_to_ecef", "carto_rhumb_line_distance"
]
