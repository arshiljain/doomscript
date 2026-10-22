from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.cartography.runtime import (
    carto_haversine_distance, carto_initial_bearing,
    carto_mercator_projection, carto_utm_zone,
    carto_ground_distance, carto_tissot_indicatrix_distortion
)
from doomscript.domains.cartography.parser import CartographyDomainParser
from doomscript.domains.cartography.exporter import CartographyASTExporter

class CartographyRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class CartographyDomain(DomainContract):
    name = "cartography"
    aliases = ["carto", "map_projection", "geodesy"]
    description = "Cartography and map projections: Haversine distance, initial bearing, Mercator projection, UTM zones, ground distance, and Tissot distortion"
    parser = CartographyDomainParser()
    runtime = CartographyRuntime()
    exporter = CartographyASTExporter()
    capabilities = ["haversine_distance", "initial_bearing", "mercator_projection", "utm_zone", "ground_distance", "tissot_distortion"]
    verbs = [
        VerbSpec(pattern="calculate haversine distance lat1 {la1:expr} lon1 {lo1:expr} lat2 {la2:expr} lon2 {lo2:expr} into {target:ident}", description="Haversine distance"),
        VerbSpec(pattern="calculate initial bearing lat1 {la1:expr} lon1 {lo1:expr} lat2 {la2:expr} lon2 {lo2:expr} into {target:ident}", description="Initial bearing"),
        VerbSpec(pattern="calculate mercator projection lat {la:expr} lon {lo:expr} into {target:ident}", description="Mercator projection"),
        VerbSpec(pattern="calculate utm zone lon {lo:expr} into {target:ident}", description="UTM zone"),
        VerbSpec(pattern="calculate ground distance map_cm {cm:expr} scale {ratio:expr} into {target:ident}", description="Ground distance"),
        VerbSpec(pattern="calculate mercator distortion lat {lat:expr} into {target:ident}", description="Mercator scale distortion")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate haversine distance ") or s.startswith("calculate initial bearing ") or s.startswith("calculate mercator projection ") or s.startswith("calculate utm zone ") or s.startswith("calculate ground distance ") or s.startswith("calculate mercator distortion ")

CARTOGRAPHY_DOMAIN = CartographyDomain()
get_domain_registry().register(CARTOGRAPHY_DOMAIN)

__all__ = [
    "CartographyDomain", "CARTOGRAPHY_DOMAIN", "CartographyRuntime",
    "carto_haversine_distance", "carto_initial_bearing",
    "carto_mercator_projection", "carto_utm_zone",
    "carto_ground_distance", "carto_tissot_indicatrix_distortion"
]
