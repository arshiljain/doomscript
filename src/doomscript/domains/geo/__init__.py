"""Geospatial Analytics Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.geo.spec import (
    GeoPointSpec,
    GeoPolygonSpec,
    GeoDistanceSpec,
    GeoContainmentSpec,
    GeoBoundingBoxSpec,
    GeoSpatialJoinSpec,
)
from doomscript.domains.geo.parser import GeoDomainParser
from doomscript.domains.geo.runtime import (
    GeoRuntime,
    point,
    polygon,
    distance_between,
    is_point_in_polygon,
    bounding_box,
    spatial_join,
    to_geojson,
)
from doomscript.domains.geo.exporter import GeoASTExporter
from doomscript.domains.registry import get_domain_registry


class GeoDomain(DomainContract):
    """Geospatial Analytics domain pack providing points, polygons, distance, spatial joins, and containment."""

    name = "geo"
    aliases = ["geospatial", "spatial", "gis"]
    parser = GeoDomainParser()
    runtime = GeoRuntime()
    exporter = GeoASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("point ")
            or s.startswith("point at ")
            or s.startswith("polygon from ")
            or s.startswith("polygon with coords ")
            or s.startswith("distance between ")
            or s.startswith("distance from ")
            or s.startswith("check if ")
            or (s.startswith("is ") and " inside " in s)
            or s.startswith("bounding box of ")
            or s.startswith("spatial join ")
            or (s.startswith("convert ") and "to geojson" in s)
        )

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
GEO_DOMAIN = GeoDomain()
get_domain_registry().register(GEO_DOMAIN)

__all__ = [
    "GeoDomain",
    "GEO_DOMAIN",
    "GeoPointSpec",
    "GeoPolygonSpec",
    "GeoDistanceSpec",
    "GeoContainmentSpec",
    "GeoBoundingBoxSpec",
    "GeoSpatialJoinSpec",
    "GeoDomainParser",
    "GeoRuntime",
    "GeoASTExporter",
    "point",
    "polygon",
    "distance_between",
    "is_point_in_polygon",
    "bounding_box",
    "spatial_join",
    "to_geojson",
]
