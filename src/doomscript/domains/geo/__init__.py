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
    geo_haversine_distance,
    geo_bounding_box_contains,
    geo_centroid,
    geo_polygon_area,
    geo_to_geojson_point,
    geo_nearest_coordinate,
    geo_encode_geohash,
    geo_decode_geohash,
    geo_initial_bearing,
    geo_final_bearing,
    geo_destination_point,
    geo_midpoint,
    geo_cross_track_distance,
    geo_bounding_box_intersection,
    geo_bounding_box_union,
    geo_convex_hull_graham,
    geo_point_to_line_distance,
    geo_simplify_douglas_peucker,
    geo_to_geojson_polygon,
    geo_to_geojson_feature_collection,
    geo_polygon_perimeter,
    geo_buffer_point_circle,
    geo_utm_zone_number,
    geo_rhumb_line_distance,
    geo_rhumb_line_bearing,
    geo_vincenty_distance,
    geo_point_in_polygon,
    geo_polygon_area_sq_km,
    geo_geohash_encode,
    geo_geohash_decode,
    SpatialRTree,
    DelaunayTriangulator,
    WebMercatorProjection,
    IsochroneContour,
    VincentyGeodesicDistance,
    DouglasPeuckerSimplifier,
    PolygonClippingSutherlandHodgman,
    geo_douglas_peucker,
    geo_sutherland_hodgman_clip,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.geo.exporter import GeoASTExporter
from doomscript.domains.registry import get_domain_registry


class GeoDomain(DomainContract):
    """Geospatial Analytics domain pack providing points, polygons, distance, spatial joins, and containment."""

    name = "geo"
    aliases = ["geospatial", "spatial", "gis"]
    description = "Geospatial operations, geodesic distances, polygon containment, spatial joins, and GeoJSON"
    parser = GeoDomainParser()
    runtime = GeoRuntime()
    exporter = GeoASTExporter()
    capabilities = ["geodesic", "polygon", "spatial_join", "geojson", "bounding_box"]
    optional_dependencies = ["shapely", "geopandas"]

    verbs = [
        VerbSpec(
            name="point",
            pattern="point at lat {lat:expr} and lon {lon:expr} into {target:ident}",
            arg_schema={"lat": "expr", "lon": "expr", "target": "ident"},
            returns="Record",
            description="Create coordinate point object",
        ),
        VerbSpec(
            name="polygon",
            pattern="polygon from {coords:expr} into {target:ident}",
            arg_schema={"coords": "expr", "target": "ident"},
            returns="Record",
            description="Create 2D geographic polygon from vertex list",
        ),
        VerbSpec(
            name="distance_between",
            pattern="distance between {p1:ident} and {p2:ident} [in (km|miles|meters)] into {target:ident}",
            arg_schema={"p1": "ident", "p2": "ident", "target": "ident"},
            returns="float",
            description="Compute Great-Circle / Haversine distance between two coordinates",
        ),
        VerbSpec(
            name="point_in_polygon",
            pattern="is {pt:ident} inside {poly:ident} into {target:ident}",
            arg_schema={"pt": "ident", "poly": "ident", "target": "ident"},
            returns="bool",
            description="Test point-in-polygon ray-casting containment",
        ),
        VerbSpec(
            name="bounding_box",
            pattern="bounding box of {geom:ident} into {target:ident}",
            arg_schema={"geom": "ident", "target": "ident"},
            returns="Record",
            description="Compute minimum bounding envelope for geometry",
        ),
        VerbSpec(
            name="spatial_join",
            pattern="spatial join {points:ident} and {polys:ident} into {target:ident}",
            arg_schema={"points": "ident", "polys": "ident", "target": "ident"},
            returns="Table",
            description="Relational spatial join between points and polygon boundaries",
        ),
        VerbSpec(
            name="to_geojson",
            pattern="convert {geom:ident} to geojson into {target:ident}",
            arg_schema={"geom": "ident", "target": "ident"},
            returns="Record",
            description="Export geometry to RFC 7946 GeoJSON format",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
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
            or s.startswith("calculate haversine distance ")
            or s.startswith("haversine distance ")
            or s.startswith("check if bounding box ")
            or s.startswith("calculate centroid ")
            or s.startswith("centroid of ")
            or s.startswith("calculate polygon area ")
            or s.startswith("polygon area ")
            or s.startswith("convert coordinate ")
            or s.startswith("find nearest coordinate ")
            or s.startswith("encode geohash ")
            or s.startswith("decode geohash ")
            or s.startswith("cross track distance ")
            or s.startswith("destination point ")
            or s.startswith("initial bearing ")
            or s.startswith("final bearing ")
            or s.startswith("midpoint between ")
            or s.startswith("bounding box intersection ")
            or s.startswith("bounding box union ")
            or s.startswith("convex hull ")
            or (s.startswith("distance from point ") and " to line segment " in s)
            or s.startswith("simplify polyline ")
            or s.startswith("convert coordinates ")
            or s.startswith("convert features ")
            or s.startswith("calculate perimeter of polygon ")
            or s.startswith("perimeter of polygon ")
            or s.startswith("circular buffer around ")
            or s.startswith("utm zone for longitude ")
            or s.startswith("rhumb line distance ")
            or s.startswith("rhumb line bearing ")
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
    "geo_haversine_distance",
    "geo_bounding_box_contains",
    "geo_centroid",
    "geo_polygon_area",
    "geo_to_geojson_point",
    "geo_nearest_coordinate",
    "geo_encode_geohash",
    "geo_decode_geohash",
    "geo_initial_bearing",
    "geo_final_bearing",
    "geo_destination_point",
    "geo_midpoint",
    "geo_cross_track_distance",
    "geo_bounding_box_intersection",
    "geo_bounding_box_union",
    "geo_convex_hull_graham",
    "geo_point_to_line_distance",
    "geo_simplify_douglas_peucker",
    "geo_to_geojson_polygon",
    "geo_to_geojson_feature_collection",
    "geo_polygon_perimeter",
    "geo_buffer_point_circle",
    "geo_utm_zone_number",
    "geo_rhumb_line_distance",
    "geo_rhumb_line_bearing",
    "geo_vincenty_distance",
    "geo_point_in_polygon",
    "geo_polygon_area_sq_km",
    "geo_geohash_encode",
    "geo_geohash_decode",
    "SpatialRTree",
    "QuadTree",
    "QuadTreeNode",
    "geo_quadtree",
    "DelaunayTriangulator",
    "WebMercatorProjection",
    "IsochroneContour",
    "VincentyGeodesicDistance",
    "DouglasPeuckerSimplifier",
    "PolygonClippingSutherlandHodgman",
    "geo_douglas_peucker",
    "geo_sutherland_hodgman_clip",
]

