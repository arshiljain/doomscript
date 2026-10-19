"""Runtime execution engine for Geospatial Analytics domain."""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.geo.spec import (
    GeoPointSpec,
    GeoPolygonSpec,
    GeoDistanceSpec,
    GeoContainmentSpec,
    GeoBoundingBoxSpec,
    GeoSpatialJoinSpec,
)

EARTH_RADIUS_KM = 6371.0088


def point(lat: float, lon: float) -> Dict[str, Any]:
    """Creates a GeoJSON-compatible Point dictionary with lat/lon coordinates."""
    lat_f = float(lat)
    lon_f = float(lon)
    return {
        "type": "Point",
        "coordinates": [round(lon_f, 6), round(lat_f, 6)],
        "lat": round(lat_f, 6),
        "lon": round(lon_f, 6),
    }


def polygon(coordinates: List[List[float]]) -> Dict[str, Any]:
    """Creates a GeoJSON-compatible Polygon dictionary from an exterior coordinate ring."""
    if not isinstance(coordinates, list) or len(coordinates) < 3:
        raise ValueError("Polygon requires at least 3 coordinate points")

    clean_ring = []
    for pt in coordinates:
        if isinstance(pt, dict) and "lon" in pt and "lat" in pt:
            clean_ring.append([float(pt["lon"]), float(pt["lat"])])
        elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
            clean_ring.append([float(pt[0]), float(pt[1])])
        else:
            raise TypeError(f"Invalid polygon coordinate format: {pt}")

    # Ensure closed ring
    if clean_ring[0] != clean_ring[-1]:
        clean_ring.append(clean_ring[0])

    return {
        "type": "Polygon",
        "coordinates": [clean_ring],
    }


def _extract_lat_lon(pt: Any) -> Tuple[float, float]:
    """Extracts (lat, lon) from GeoPoint dict, (lat, lon) tuple, or list."""
    if isinstance(pt, dict):
        if "lat" in pt and "lon" in pt:
            return float(pt["lat"]), float(pt["lon"])
        if pt.get("type") == "Point" and "coordinates" in pt:
            coords = pt["coordinates"]
            return float(coords[1]), float(coords[0])
    if isinstance(pt, (list, tuple)) and len(pt) >= 2:
        return float(pt[0]), float(pt[1])
    raise TypeError(f"Cannot extract lat/lon from geometry: {pt}")


def distance_between(p1: Any, p2: Any, unit: str = "km") -> float:
    """Computes great-circle distance between two points using the Haversine formula."""
    lat1, lon1 = _extract_lat_lon(p1)
    lat2, lon2 = _extract_lat_lon(p2)

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    dist_km = EARTH_RADIUS_KM * c

    unit_clean = unit.lower().strip()
    if unit_clean in ("mile", "miles", "mi"):
        return round(dist_km * 0.621371192, 4)
    elif unit_clean in ("meter", "meters", "m"):
        return round(dist_km * 1000.0, 2)
    return round(dist_km, 4)


def is_point_in_polygon(pt: Any, poly: Any) -> bool:
    """Ray casting algorithm to determine if a point is inside a polygon."""
    lat, lon = _extract_lat_lon(pt)

    # Extract polygon ring
    if isinstance(poly, dict) and poly.get("type") == "Polygon" and "coordinates" in poly:
        ring = poly["coordinates"][0]
    elif isinstance(poly, (list, tuple)):
        ring = poly
    else:
        raise TypeError(f"Invalid polygon for containment check: {poly}")

    # Ray casting: test against horizontal ray from (lon, lat)
    inside = False
    n = len(ring)
    for i in range(n):
        j = (i - 1) % n
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]

        intersect = ((yi > lat) != (yj > lat)) and (
            lon < (xj - xi) * (lat - yi) / (yj - yi) + xi
        )
        if intersect:
            inside = not inside

    return inside


def bounding_box(geometries: Any) -> Dict[str, Any]:
    """Computes minimum bounding box [min_lon, min_lat, max_lon, max_lat] for geometries."""
    pts = []
    if isinstance(geometries, list):
        for g in geometries:
            if isinstance(g, dict) and g.get("type") == "Point":
                pts.append((g["lat"], g["lon"]))
            elif isinstance(g, dict) and g.get("type") == "Polygon":
                for coord in g["coordinates"][0]:
                    pts.append((coord[1], coord[0]))
            elif isinstance(g, (list, tuple)) and len(g) >= 2:
                pts.append((g[0], g[1]))
    elif isinstance(geometries, dict):
        if geometries.get("type") == "Polygon":
            for coord in geometries["coordinates"][0]:
                pts.append((coord[1], coord[0]))
        elif "lat" in geometries and "lon" in geometries:
            pts.append((geometries["lat"], geometries["lon"]))

    if not pts:
        return {"min_lat": 0.0, "max_lat": 0.0, "min_lon": 0.0, "max_lon": 0.0, "bbox": [0, 0, 0, 0]}

    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]

    min_lat, max_lat = min(lats), max(lats)
    min_lon, max_lon = min(lons), max(lons)

    return {
        "min_lat": round(min_lat, 6),
        "max_lat": round(max_lat, 6),
        "min_lon": round(min_lon, 6),
        "max_lon": round(max_lon, 6),
        "bbox": [round(min_lon, 6), round(min_lat, 6), round(max_lon, 6), round(max_lat, 6)],
    }


def spatial_join(points: List[Any], polygons: List[Any]) -> List[Dict[str, Any]]:
    """Performs spatial join matching each point to containing polygons."""
    matches = []
    if not isinstance(points, list):
        points = [points]
    if not isinstance(polygons, list):
        polygons = [polygons]

    for p_idx, pt in enumerate(points):
        for poly_idx, poly in enumerate(polygons):
            if is_point_in_polygon(pt, poly):
                matches.append({
                    "point": pt,
                    "polygon": poly,
                    "point_index": p_idx,
                    "polygon_index": poly_idx,
                })
    return matches


def to_geojson(geom: Any) -> Dict[str, Any]:
    """Wraps a point or polygon into an RFC 7946 GeoJSON Feature."""
    if isinstance(geom, dict) and "type" in geom:
        return {
            "type": "Feature",
            "geometry": geom,
            "properties": {},
        }
    raise TypeError(f"Cannot serialize to GeoJSON: {geom}")


class GeoRuntime(DomainRuntime):
    """Runtime engine for Geospatial Analytics domain."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if isinstance(ir, GeoPointSpec):
            lat = scope.get(ir.lat_expr, ir.lat_expr)
            lon = scope.get(ir.lon_expr, ir.lon_expr)
            res = point(float(lat), float(lon))
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, GeoPolygonSpec):
            coords = scope.get(ir.coords_expr, ir.coords_expr)
            res = polygon(coords)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, GeoDistanceSpec):
            p1 = scope.get(ir.p1_expr, ir.p1_expr)
            p2 = scope.get(ir.p2_expr, ir.p2_expr)
            res = distance_between(p1, p2, unit=ir.unit)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, GeoContainmentSpec):
            p = scope.get(ir.point_expr, ir.point_expr)
            poly = scope.get(ir.polygon_expr, ir.polygon_expr)
            res = is_point_in_polygon(p, poly)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, GeoBoundingBoxSpec):
            geoms = scope.get(ir.geom_expr, ir.geom_expr)
            res = bounding_box(geoms)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, GeoSpatialJoinSpec):
            pts = scope.get(ir.points_expr, ir.points_expr)
            polys = scope.get(ir.polygons_expr, ir.polygons_expr)
            res = spatial_join(pts, polys)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        raise TypeError(f"Unknown Geo IR: {type(ir).__name__}")
