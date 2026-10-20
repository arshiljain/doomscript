"""Runtime execution engine for Geospatial Analytics domain."""

import math
from typing import Any, Dict, List, Optional, Tuple, Union
from doomscript.core.record import Record
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


def _extract_polygon_ring(poly: Any) -> List[List[float]]:
    """Extracts a list of [lon, lat] coordinates from GeoPolygon dict or nested lists."""
    if isinstance(poly, dict) and poly.get("type") == "Polygon" and "coordinates" in poly:
        ring = poly["coordinates"][0]
    elif isinstance(poly, (list, tuple)):
        ring = poly
    else:
        ring = []
    clean = []
    for p in ring:
        if isinstance(p, dict) and "lon" in p and "lat" in p:
            clean.append([float(p["lon"]), float(p["lat"])])
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            clean.append([float(p[0]), float(p[1])])
    return clean


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


# --- Batch 14 Spoken English Geospatial Verbs ---

def geo_haversine_distance(p1: Any, p2: Any, unit: str = "km") -> float:
    """Calculate Haversine great-circle distance between two coordinates."""
    return distance_between(p1, p2, unit=unit)


def geo_bounding_box_contains(bbox: Any, pt: Any) -> bool:
    """Check if bounding box [min_lat, min_lon, max_lat, max_lon] contains point [lat, lon]."""
    lat, lon = _extract_lat_lon(pt)
    if isinstance(bbox, dict):
        min_lat, min_lon = bbox.get("min_lat", -90.0), bbox.get("min_lon", -180.0)
        max_lat, max_lon = bbox.get("max_lat", 90.0), bbox.get("max_lon", 180.0)
    elif isinstance(bbox, (list, tuple)) and len(bbox) >= 4:
        min_lat, min_lon, max_lat, max_lon = float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3])
    else:
        return False
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def geo_centroid(coordinates: Any) -> List[float]:
    """Calculate arithmetic mean centroid of coordinates list [lat, lon]."""
    coords = list(coordinates)
    if not coords:
        return [0.0, 0.0]
    lats, lons = [], []
    for c in coords:
        lt, ln = _extract_lat_lon(c)
        lats.append(lt)
        lons.append(ln)
    return [round(sum(lats) / len(lats), 6), round(sum(lons) / len(lons), 6)]


def geo_polygon_area(coordinates: Any) -> float:
    """Calculate planar polygon area using Shoelace formula."""
    if isinstance(coordinates, dict) and "coordinates" in coordinates:
        ring = coordinates["coordinates"][0]
    else:
        ring = list(coordinates)
    if len(ring) < 3:
        return 0.0
    pts = []
    for p in ring:
        pts.append(_extract_lat_lon(p))
    n = len(pts)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += pts[i][0] * pts[j][1]
        area -= pts[j][0] * pts[i][1]
    return round(abs(area) / 2.0, 6)


def geo_to_geojson_point(coord: Any) -> Dict[str, Any]:
    """Convert coordinate [lat, lon] or dict to standard GeoJSON Point Feature."""
    lat, lon = _extract_lat_lon(coord)
    return {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [round(lon, 6), round(lat, 6)],
        },
        "properties": {},
    }


def geo_nearest_coordinate(target_pt: Any, candidates: Any) -> Any:
    """Find closest coordinate from candidates to target point using Haversine distance."""
    pts = list(candidates)
    if not pts:
        return None
    best_pt = None
    min_d = float("inf")
    for cand in pts:
        d = distance_between(target_pt, cand)
        if d < min_d:
            min_d = d
            best_pt = cand
    return best_pt


# --- 350-Expansion 19 Geospatial Operations ---

_GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
_GEOHASH_DECODE = {c: i for i, c in enumerate(_GEOHASH_BASE32)}


def geo_encode_geohash(lat: Any, lon: Any, precision: Any = 12) -> str:
    """Encode latitude and longitude into Geohash string."""
    lt, ln = float(lat), float(lon)
    prec = int(precision)
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    geohash = []
    is_even = True
    bit = 0
    ch = 0

    while len(geohash) < prec:
        if is_even:
            mid = (lon_interval[0] + lon_interval[1]) / 2.0
            if ln >= mid:
                ch |= (1 << (4 - bit))
                lon_interval[0] = mid
            else:
                lon_interval[1] = mid
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2.0
            if lt >= mid:
                ch |= (1 << (4 - bit))
                lat_interval[0] = mid
            else:
                lat_interval[1] = mid
        is_even = not is_even
        if bit < 4:
            bit += 1
        else:
            geohash.append(_GEOHASH_BASE32[ch])
            bit = 0
            ch = 0
    return "".join(geohash)


def geo_decode_geohash(geohash: Any) -> Dict[str, float]:
    """Decode Geohash string into latitude, longitude, and bounding errors."""
    gh = str(geohash).strip().lower()
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    is_even = True

    for c in gh:
        cd = _GEOHASH_DECODE.get(c, 0)
        for mask in [16, 8, 4, 2, 1]:
            if is_even:
                mid = (lon_interval[0] + lon_interval[1]) / 2.0
                if cd & mask:
                    lon_interval[0] = mid
                else:
                    lon_interval[1] = mid
            else:
                mid = (lat_interval[0] + lat_interval[1]) / 2.0
                if cd & mask:
                    lat_interval[0] = mid
                else:
                    lat_interval[1] = mid
            is_even = not is_even

    lat = (lat_interval[0] + lat_interval[1]) / 2.0
    lon = (lon_interval[0] + lon_interval[1]) / 2.0
    err_lat = (lat_interval[1] - lat_interval[0]) / 2.0
    err_lon = (lon_interval[1] - lon_interval[0]) / 2.0
    return {
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "error_lat": round(err_lat, 6),
        "error_lon": round(err_lon, 6),
    }


def geo_initial_bearing(p1: Any, p2: Any) -> float:
    """Calculate initial compass bearing from point 1 to point 2 in degrees [0, 360)."""
    lat1, lon1 = _extract_lat_lon(p1)
    lat2, lon2 = _extract_lat_lon(p2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    theta = math.atan2(y, x)
    return round((math.degrees(theta) + 360.0) % 360.0, 2)


def geo_final_bearing(p1: Any, p2: Any) -> float:
    """Calculate final compass bearing arriving at point 2 from point 1."""
    return round((geo_initial_bearing(p2, p1) + 180.0) % 360.0, 2)


def geo_destination_point(lat: Any, lon: Any, distance_km: Any, bearing_deg: Any) -> List[float]:
    """Calculate destination coordinate given starting point, distance in km, and bearing in degrees."""
    lt, ln = float(lat), float(lon)
    d = float(distance_km)
    brng = math.radians(float(bearing_deg))
    phi1 = math.radians(lt)
    lambda1 = math.radians(ln)
    delta = d / EARTH_RADIUS_KM

    phi2 = math.asin(
        math.sin(phi1) * math.cos(delta)
        + math.cos(phi1) * math.sin(delta) * math.cos(brng)
    )
    lambda2 = lambda1 + math.atan2(
        math.sin(brng) * math.sin(delta) * math.cos(phi1),
        math.cos(delta) - math.sin(phi1) * math.sin(phi2),
    )
    return [round(math.degrees(phi2), 6), round(math.degrees(lambda2), 6)]


def geo_midpoint(p1: Any, p2: Any) -> List[float]:
    """Calculate great-circle spherical midpoint between two coordinates [lat, lon]."""
    lat1, lon1 = _extract_lat_lon(p1)
    lat2, lon2 = _extract_lat_lon(p2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    lambda1 = math.radians(lon1)
    delta_lambda = math.radians(lon2 - lon1)

    bx = math.cos(phi2) * math.cos(delta_lambda)
    by = math.cos(phi2) * math.sin(delta_lambda)
    phi_m = math.atan2(
        math.sin(phi1) + math.sin(phi2),
        math.sqrt((math.cos(phi1) + bx) ** 2 + by ** 2),
    )
    lambda_m = lambda1 + math.atan2(by, math.cos(phi1) + bx)
    return [round(math.degrees(phi_m), 6), round(math.degrees(lambda_m), 6)]


def geo_cross_track_distance(pt: Any, start_pt: Any, end_pt: Any) -> float:
    """Calculate perpendicular cross-track distance of point from great-circle line in km."""
    d13 = distance_between(start_pt, pt) / EARTH_RADIUS_KM
    theta13 = math.radians(geo_initial_bearing(start_pt, pt))
    theta12 = math.radians(geo_initial_bearing(start_pt, end_pt))
    dxt = math.asin(math.sin(d13) * math.sin(theta13 - theta12)) * EARTH_RADIUS_KM
    return round(abs(dxt), 4)


def geo_bounding_box_intersection(box1: Any, box2: Any) -> Optional[List[float]]:
    """Compute overlapping bounding box intersection [min_lat, min_lon, max_lat, max_lon]."""
    b1 = [float(x) for x in box1]
    b2 = [float(x) for x in box2]
    min_lat = max(b1[0], b2[0])
    min_lon = max(b1[1], b2[1])
    max_lat = min(b1[2], b2[2])
    max_lon = min(b1[3], b2[3])
    if min_lat > max_lat or min_lon > max_lon:
        return None
    return [round(min_lat, 6), round(min_lon, 6), round(max_lat, 6), round(max_lon, 6)]


def geo_bounding_box_union(box1: Any, box2: Any) -> List[float]:
    """Compute enclosing union of two bounding boxes [min_lat, min_lon, max_lat, max_lon]."""
    b1 = [float(x) for x in box1]
    b2 = [float(x) for x in box2]
    return [
        round(min(b1[0], b2[0]), 6),
        round(min(b1[1], b2[1]), 6),
        round(max(b1[2], b2[2]), 6),
        round(max(b1[3], b2[3]), 6),
    ]


def geo_convex_hull_graham(coords: Any) -> List[List[float]]:
    """Calculate 2D convex hull of coordinates using Graham scan."""
    pts = [_extract_lat_lon(p) for p in coords]
    if len(pts) <= 3:
        return [[p[0], p[1]] for p in pts]

    # Find pivot with lowest lat (then lowest lon)
    pivot = min(pts, key=lambda p: (p[0], p[1]))

    def polar_angle_dist(p):
        dy = p[0] - pivot[0]
        dx = p[1] - pivot[1]
        return math.atan2(dy, dx), dy * dy + dx * dx

    sorted_pts = sorted(pts, key=polar_angle_dist)

    def cross_prod(o, a, b):
        return (a[1] - o[1]) * (b[0] - o[0]) - (a[0] - o[0]) * (b[1] - o[1])

    hull = []
    for p in sorted_pts:
        while len(hull) >= 2 and cross_prod(hull[-2], hull[-1], p) <= 0:
            hull.pop()
        hull.append(p)
    return [[p[0], p[1]] for p in hull]


def geo_point_to_line_distance(pt: Any, line_start: Any, line_end: Any) -> float:
    """Calculate perpendicular Euclidean distance from point to segment in km."""
    p = _extract_lat_lon(pt)
    a = _extract_lat_lon(line_start)
    b = _extract_lat_lon(line_end)
    dx = b[1] - a[1]
    dy = b[0] - a[0]
    line_len_sq = dx * dx + dy * dy
    if line_len_sq == 0:
        return distance_between(p, a)
    t = max(0.0, min(1.0, ((p[1] - a[1]) * dx + (p[0] - a[0]) * dy) / line_len_sq))
    proj = [a[0] + t * dy, a[1] + t * dx]
    return distance_between(p, proj)


def geo_simplify_douglas_peucker(coords: Any, epsilon: Any) -> List[Any]:
    """Simplify polyline coordinates using Douglas-Peucker algorithm."""
    pts = list(coords)
    if len(pts) <= 2:
        return pts
    eps = float(epsilon)

    def dpeucker(point_list):
        if len(point_list) <= 2:
            return point_list
        start = point_list[0]
        end = point_list[-1]
        max_dist = 0.0
        index = 0
        for i in range(1, len(point_list) - 1):
            d = geo_point_to_line_distance(point_list[i], start, end)
            if d > max_dist:
                max_dist = d
                index = i
        if max_dist > eps:
            left = dpeucker(point_list[: index + 1])
            right = dpeucker(point_list[index:])
            return left[:-1] + right
        else:
            return [start, end]

    return dpeucker(pts)


def geo_to_geojson_polygon(coords: Any) -> Dict[str, Any]:
    """Convert coordinate ring to standard GeoJSON Polygon Feature."""
    if coords and isinstance(coords[0], (list, tuple)) and coords[0] and isinstance(coords[0][0], (list, tuple)):
        rings = coords
    else:
        rings = [coords]

    json_rings = []
    for r in rings:
        ring = [_extract_lat_lon(p) for p in r]
        if ring and ring[0] != ring[-1]:
            ring.append(ring[0])
        json_rings.append([[round(p[1], 6), round(p[0], 6)] for p in ring])

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": json_rings,
        },
        "properties": {},
    }


def geo_to_geojson_feature_collection(features: Any) -> Dict[str, Any]:
    """Package list of GeoJSON Features into standard FeatureCollection."""
    return {
        "type": "FeatureCollection",
        "features": list(features),
    }


def geo_polygon_perimeter(coords: Any) -> float:
    """Calculate total boundary perimeter of polygon in km."""
    ring = [_extract_lat_lon(p) for p in coords]
    if len(ring) < 2:
        return 0.0
    total = 0.0
    for i in range(len(ring)):
        j = (i + 1) % len(ring)
        total += distance_between(ring[i], ring[j])
    return round(total, 4)


def geo_buffer_point_circle(center_pt: Any, radius_km: Any, num_points: Any = 32) -> List[List[float]]:
    """Generate perimeter coordinates of circular buffer around center point."""
    lat, lon = _extract_lat_lon(center_pt)
    r = float(radius_km)
    n = max(8, int(num_points))
    circle_pts = []
    for i in range(n):
        bearing = (360.0 / n) * i
        pt = geo_destination_point(lat, lon, r, bearing)
        circle_pts.append(pt)
    circle_pts.append(circle_pts[0])
    return circle_pts


def geo_utm_zone_number(lon: Any) -> int:
    """Calculate standard Universal Transverse Mercator (UTM) zone number (1-60)."""
    ln = float(lon)
    return int((ln + 180.0) / 6.0) % 60 + 1


def geo_rhumb_line_distance(p1: Any, p2: Any) -> float:
    """Calculate constant-bearing Rhumb line (loxodrome) distance between coordinates in km."""
    lat1, lon1 = _extract_lat_lon(p1)
    lat2, lon2 = _extract_lat_lon(p2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = phi2 - phi1
    delta_lambda = math.radians(abs(lon2 - lon1))
    if delta_lambda > math.pi:
        delta_lambda = 2.0 * math.pi - delta_lambda

    # Project on Mercator
    delta_psi = math.log(
        math.tan(math.pi / 4.0 + phi2 / 2.0)
        / math.tan(math.pi / 4.0 + phi1 / 2.0)
    ) if abs(phi2 - phi1) > 1e-12 else 0.0

    q = (delta_phi / delta_psi) if abs(delta_psi) > 1e-12 else math.cos(phi1)
    dist = math.sqrt(delta_phi * delta_phi + q * q * delta_lambda * delta_lambda) * EARTH_RADIUS_KM
    return round(dist, 4)


def geo_rhumb_line_bearing(p1: Any, p2: Any) -> float:
    """Calculate constant compass heading along Rhumb line in degrees [0, 360)."""
    lat1, lon1 = _extract_lat_lon(p1)
    lat2, lon2 = _extract_lat_lon(p2)
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_lambda = math.radians(lon2 - lon1)
    if delta_lambda > math.pi:
        delta_lambda -= 2.0 * math.pi
    elif delta_lambda < -math.pi:
        delta_lambda += 2.0 * math.pi

    delta_psi = math.log(
        math.tan(math.pi / 4.0 + phi2 / 2.0)
        / math.tan(math.pi / 4.0 + phi1 / 2.0)
    ) if abs(phi2 - phi1) > 1e-12 else 0.0

    theta = math.atan2(delta_lambda, delta_psi)
    return round((math.degrees(theta) + 360.0) % 360.0, 2)


def geo_vincenty_distance(p1: Any, p2: Any, max_iter: int = 100, tol: float = 1e-12) -> float:
    """High-precision Vincenty inverse solution on WGS-84 ellipsoid (distance in km)."""
    lat1, lon1 = _extract_lat_lon(p1)
    lat2, lon2 = _extract_lat_lon(p2)

    # WGS-84 ellipsoid constants
    a = 6378137.0  # equatorial radius in meters
    f = 1.0 / 298.257223563  # flattening
    b = (1.0 - f) * a

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    L = math.radians(lon2 - lon1)

    u1 = math.atan((1.0 - f) * math.tan(phi1))
    u2 = math.atan((1.0 - f) * math.tan(phi2))
    sin_u1, cos_u1 = math.sin(u1), math.cos(u1)
    sin_u2, cos_u2 = math.sin(u2), math.cos(u2)

    lam = L
    for _ in range(max_iter):
        sin_lam, cos_lam = math.sin(lam), math.cos(lam)
        sin_sigma = math.sqrt(
            (cos_u2 * sin_lam) ** 2 + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lam) ** 2
        )
        if sin_sigma == 0.0:
            return 0.0  # coincident points

        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lam
        sigma = math.atan2(sin_sigma, cos_sigma)

        sin_alpha = (cos_u1 * cos_u2 * sin_lam) / sin_sigma
        cos2_alpha = 1.0 - sin_alpha ** 2

        cos_2sigma_m = cos_sigma - (2.0 * sin_u1 * sin_u2) / cos2_alpha if cos2_alpha != 0.0 else 0.0

        C = (f / 16.0) * cos2_alpha * (4.0 + f * (4.0 - 3.0 * cos2_alpha))
        lam_prev = lam
        lam = L + (1.0 - C) * f * sin_alpha * (
            sigma + C * sin_sigma * (cos_2sigma_m + C * cos_sigma * (-1.0 + 2.0 * (cos_2sigma_m ** 2)))
        )
        if abs(lam - lam_prev) < tol:
            break

    u_sq = cos2_alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1.0 + (u_sq / 16384.0) * (4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq)))
    B = (u_sq / 1024.0) * (256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq)))
    delta_sigma = B * sin_sigma * (
        cos_2sigma_m + (B / 4.0) * (
            cos_sigma * (-1.0 + 2.0 * (cos_2sigma_m ** 2))
            - (B / 6.0) * cos_2sigma_m * (-3.0 + 4.0 * (sin_sigma ** 2)) * (-3.0 + 4.0 * (cos_2sigma_m ** 2))
        )
    )

    s = b * A * (sigma - delta_sigma)  # meters
    return round(s / 1000.0, 4)  # km


def geo_point_in_polygon(point_pt: Any, polygon_obj: Any) -> bool:
    """Ray casting point-in-polygon containment test."""
    lat, lon = _extract_lat_lon(point_pt)
    ring = _extract_polygon_ring(polygon_obj)
    if len(ring) < 3:
        return False

    inside = False
    n = len(ring)
    p1x, p1y = ring[0][0], ring[0][1]  # lon, lat

    for i in range(1, n + 1):
        p2x, p2y = ring[i % n][0], ring[i % n][1]
        if lat > min(p1y, p2y):
            if lat <= max(p1y, p2y):
                if lon <= max(p1x, p2x):
                    if p1y != p2y:
                        x_inters = (lat - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or lon <= x_inters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside


def geo_polygon_area_sq_km(polygon_obj: Any) -> float:
    """Compute polygon surface area on spherical Earth in square kilometers."""
    ring = _extract_polygon_ring(polygon_obj)
    if len(ring) < 3:
        return 0.0

    # Spherical excess using Girard's formula or trapezoidal projection
    total = 0.0
    r_meters = EARTH_RADIUS_KM * 1000.0

    for i in range(len(ring) - 1):
        p1_lon, p1_lat = ring[i]
        p2_lon, p2_lat = ring[i + 1]

        phi1 = math.radians(p1_lat)
        phi2 = math.radians(p2_lat)
        lam1 = math.radians(p1_lon)
        lam2 = math.radians(p2_lon)

        total += (lam2 - lam1) * (2.0 + math.sin(phi1) + math.sin(phi2))

    area = abs(total * (r_meters ** 2) / 2.0)
    return round(area / 1_000_000.0, 4)  # sq km


_GEOHASH_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
_GEOHASH_DECODE_MAP = {c: i for i, c in enumerate(_GEOHASH_BASE32)}


def geo_geohash_encode(lat: float, lon: float, precision: int = 9) -> str:
    """Encode latitude and longitude into Base32 Geohash string."""
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    geohash = []
    bits = 0
    ch = 0
    is_even = True

    while len(geohash) < precision:
        if is_even:
            mid = (lon_range[0] + lon_range[1]) / 2.0
            if lon >= mid:
                ch = (ch << 1) | 1
                lon_range[0] = mid
            else:
                ch = (ch << 1) | 0
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2.0
            if lat >= mid:
                ch = (ch << 1) | 1
                lat_range[0] = mid
            else:
                ch = (ch << 1) | 0
                lat_range[1] = mid

        is_even = not is_even
        bits += 1

        if bits == 5:
            geohash.append(_GEOHASH_BASE32[ch])
            bits = 0
            ch = 0

    return "".join(geohash)


def geo_geohash_decode(geohash: str) -> Dict[str, Any]:
    """Decode Geohash string into latitude, longitude, and bounding box."""
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    is_even = True

    for c in geohash.lower():
        val = _GEOHASH_DECODE_MAP.get(c, 0)
        for bit_idx in (16, 8, 4, 2, 1):
            bit = 1 if (val & bit_idx) else 0
            if is_even:
                mid = (lon_range[0] + lon_range[1]) / 2.0
                if bit == 1:
                    lon_range[0] = mid
                else:
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2.0
                if bit == 1:
                    lat_range[0] = mid
                else:
                    lat_range[1] = mid
            is_even = not is_even

    lat = (lat_range[0] + lat_range[1]) / 2.0
    lon = (lon_range[0] + lon_range[1]) / 2.0
    return {
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "lat_error": round((lat_range[1] - lat_range[0]) / 2.0, 6),
        "lon_error": round((lon_range[1] - lon_range[0]) / 2.0, 6),
        "bounds": {
            "min_lat": round(lat_range[0], 6),
            "max_lat": round(lat_range[1], 6),
            "min_lon": round(lon_range[0], 6),
            "max_lon": round(lon_range[1], 6),
        },
    }


class SpatialRTree:
    """Pure-Python 2D Spatial Index Tree for fast bounding box range queries."""

    def __init__(self, max_entries: int = 16):
        self.max_entries = max(4, int(max_entries))
        # Entries: list of (min_x, min_y, max_x, max_y, item_data)
        self.entries: List[Tuple[float, float, float, float, Any]] = []

    def insert(self, min_x: float, min_y: float, max_x: float, max_y: float, data: Any) -> None:
        self.entries.append((
            min(min_x, max_x),
            min(min_y, max_y),
            max(min_x, max_x),
            max(min_y, max_y),
            data,
        ))

    def query(self, q_min_x: float, q_min_y: float, q_max_x: float, q_max_y: float) -> List[Any]:
        """Return all items whose bounding box intersects query rectangle."""
        q_min_x, q_max_x = min(q_min_x, q_max_x), max(q_min_x, q_max_x)
        q_min_y, q_max_y = min(q_min_y, q_max_y), max(q_min_y, q_max_y)

        results = []
        for x1, y1, x2, y2, data in self.entries:
            # Overlap test
            if not (x2 < q_min_x or x1 > q_max_x or y2 < q_min_y or y1 > q_max_y):
                results.append(data)
        return results

    def __len__(self) -> int:
        return len(self.entries)


class QuadTreeNode:
    """A single node/cell in a 2D spatial QuadTree."""

    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float, capacity: int = 4):
        self.min_x = float(min_x)
        self.min_y = float(min_y)
        self.max_x = float(max_x)
        self.max_y = float(max_y)
        self.capacity = max(1, int(capacity))
        self.points: List[Tuple[float, float, Any]] = []
        self.divided = False
        self.nw: Optional["QuadTreeNode"] = None
        self.ne: Optional["QuadTreeNode"] = None
        self.sw: Optional["QuadTreeNode"] = None
        self.se: Optional["QuadTreeNode"] = None

    def contains_point(self, x: float, y: float) -> bool:
        return self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y

    def subdivide(self) -> None:
        mid_x = (self.min_x + self.max_x) / 2.0
        mid_y = (self.min_y + self.max_y) / 2.0
        c = self.capacity
        self.nw = QuadTreeNode(self.min_x, mid_y, mid_x, self.max_y, c)
        self.ne = QuadTreeNode(mid_x, mid_y, self.max_x, self.max_y, c)
        self.sw = QuadTreeNode(self.min_x, self.min_y, mid_x, mid_y, c)
        self.se = QuadTreeNode(mid_x, self.min_y, self.max_x, mid_y, c)
        self.divided = True

    def insert(self, x: float, y: float, data: Any) -> bool:
        if not self.contains_point(x, y):
            return False

        if len(self.points) < self.capacity and not self.divided:
            self.points.append((x, y, data))
            return True

        if not self.divided:
            self.subdivide()
            # Push existing points down
            old_pts = list(self.points)
            self.points = []
            for px, py, pdata in old_pts:
                self._insert_children(px, py, pdata)

        return self._insert_children(x, y, data)

    def _insert_children(self, x: float, y: float, data: Any) -> bool:
        if self.nw.insert(x, y, data):
            return True
        if self.ne.insert(x, y, data):
            return True
        if self.sw.insert(x, y, data):
            return True
        if self.se.insert(x, y, data):
            return True
        return False

    def query_range(self, q_min_x: float, q_min_y: float, q_max_x: float, q_max_y: float, found: List[Any]) -> None:
        # Check bounding box intersection
        if self.max_x < q_min_x or self.min_x > q_max_x or self.max_y < q_min_y or self.min_y > q_max_y:
            return

        for px, py, data in self.points:
            if q_min_x <= px <= q_max_x and q_min_y <= py <= q_max_y:
                found.append(data)

        if self.divided:
            self.nw.query_range(q_min_x, q_min_y, q_max_x, q_max_y, found)
            self.ne.query_range(q_min_x, q_min_y, q_max_x, q_max_y, found)
            self.sw.query_range(q_min_x, q_min_y, q_max_x, q_max_y, found)
            self.se.query_range(q_min_x, q_min_y, q_max_x, q_max_y, found)


class QuadTree:
    """Zero-dependency 2D Spatial QuadTree for points and spatial bounds."""

    def __init__(self, min_x: float = -180.0, min_y: float = -90.0, max_x: float = 180.0, max_y: float = 90.0, capacity: int = 4):
        self.root = QuadTreeNode(min_x, min_y, max_x, max_y, capacity=capacity)
        self.size = 0

    def insert(self, x: float, y: float, data: Any = None) -> bool:
        val = data if data is not None else (x, y)
        ok = self.root.insert(float(x), float(y), val)
        if ok:
            self.size += 1
        return ok

    def query_range(self, min_x: float, min_y: float, max_x: float, max_y: float) -> List[Any]:
        found = []
        self.root.query_range(min(min_x, max_x), min(min_y, max_y), max(min_x, max_x), max(min_y, max_y), found)
        return found

    def query_radius(self, cx: float, cy: float, radius: float) -> List[Any]:
        r = float(radius)
        candidates = self.query_range(cx - r, cy - r, cx + r, cy + r)
        # Refine by Euclidean distance
        res = []
        for item in candidates:
            # If item is (x, y) tuple or has coords
            if isinstance(item, (tuple, list)) and len(item) >= 2 and isinstance(item[0], (int, float)):
                d = math.hypot(item[0] - cx, item[1] - cy)
                if d <= r:
                    res.append(item)
            else:
                res.append(item)
        return res

    def __len__(self) -> int:
        return self.size


def geo_quadtree(min_x: float = -180.0, min_y: float = -90.0, max_x: float = 180.0, max_y: float = 90.0, capacity: int = 4) -> QuadTree:
    """Creates a new spatial QuadTree index."""
    return QuadTree(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y, capacity=capacity)





# --- Deepened Geospatial Systems: Delaunay Triangulation, Web Mercator & Isochrone Contours ---

class DelaunayTriangulator:
    """Bowyer-Watson incremental Delaunay Triangulation and Voronoi diagram generator in 2D."""

    class Triangle:
        def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float], p3: Tuple[float, float]):
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
            self.vertices = (p1, p2, p3)
            self.edges = (
                tuple(sorted((p1, p2))),
                tuple(sorted((p2, p3))),
                tuple(sorted((p3, p1))),
            )
            self._compute_circumcircle()

        def _compute_circumcircle(self) -> None:
            ax, ay = self.p1
            bx, by = self.p2
            cx, cy = self.p3
            d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if abs(d) < 1e-12:
                self.center = (ax, ay)
                self.radius_sq = float("inf")
                return

            ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
            uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
            self.center = (ux, uy)
            self.radius_sq = (ax - ux) ** 2 + (ay - uy) ** 2

        def contains_in_circumcircle(self, pt: Tuple[float, float]) -> bool:
            px, py = pt
            cx, cy = self.center
            dist_sq = (px - cx) ** 2 + (py - cy) ** 2
            return dist_sq <= (self.radius_sq + 1e-9)

    @classmethod
    def triangulate(cls, points: List[Tuple[float, float]]) -> List[Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]]]:
        """Triangulates 2D point cloud into non-overlapping Delaunay triangles."""
        if len(points) < 3:
            return []

        # Find bounding box
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        dx = max(1.0, max_x - min_x)
        dy = max(1.0, max_y - min_y)
        delta_max = max(dx, dy)
        mid_x = (min_x + max_x) / 2.0
        mid_y = (min_y + max_y) / 2.0

        # Construct super-triangle enclosing all points
        st_p1 = (mid_x - 20.0 * delta_max, mid_y - delta_max)
        st_p2 = (mid_x, mid_y + 20.0 * delta_max)
        st_p3 = (mid_x + 20.0 * delta_max, mid_y - delta_max)
        super_verts = {st_p1, st_p2, st_p3}

        triangles: List[DelaunayTriangulator.Triangle] = [cls.Triangle(st_p1, st_p2, st_p3)]

        # Incrementally add each point
        for pt in points:
            bad_triangles = []
            for tri in triangles:
                if tri.contains_in_circumcircle(pt):
                    bad_triangles.append(tri)

            # Find boundary edges of polygonal hole
            polygon = []
            for tri in bad_triangles:
                for edge in tri.edges:
                    # Edge is boundary if not shared by another bad triangle
                    shared = sum(1 for other in bad_triangles if edge in other.edges)
                    if shared == 1:
                        polygon.append(edge)

            # Remove bad triangles
            triangles = [tri for tri in triangles if tri not in bad_triangles]

            # Re-triangulate cavity with new point
            for e_p1, e_p2 in polygon:
                triangles.append(cls.Triangle(e_p1, e_p2, pt))

        # Remove triangles that share vertices with super-triangle
        result = []
        for tri in triangles:
            if not any(v in super_verts for v in tri.vertices):
                result.append(tri.vertices)

        return result

    @classmethod
    def voronoi_diagram(cls, points: List[Tuple[float, float]]) -> List[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Generates Voronoi dual edges connecting circumcenters of adjacent Delaunay triangles."""
        if len(points) < 3:
            return []

        triangles = [cls.Triangle(*v) for v in cls.triangulate(points)]
        edges = []
        n = len(triangles)
        for i in range(n):
            for j in range(i + 1, n):
                # If they share an edge, connect their circumcenters
                common_edges = set(triangles[i].edges).intersection(set(triangles[j].edges))
                if common_edges:
                    edges.append((triangles[i].center, triangles[j].center))
        return edges


class WebMercatorProjection:
    """EPSG:3857 (Spherical Mercator) <-> EPSG:4326 (WGS84) transforms & Slippy Map tile arithmetic."""

    A = 6378137.0  # WGS84 semi-major axis in meters
    MAX_LAT = 85.0511287798066

    @classmethod
    def lat_lon_to_xy(cls, lat: float, lon: float) -> Tuple[float, float]:
        """Projects (lat, lon) in degrees to EPSG:3857 (meters x, y)."""
        clamped_lat = max(-cls.MAX_LAT, min(cls.MAX_LAT, float(lat)))
        x = cls.A * math.radians(float(lon))
        lat_rad = math.radians(clamped_lat)
        y = cls.A * math.log(math.tan(math.pi / 4.0 + lat_rad / 2.0))
        return round(x, 2), round(y, 2)

    @classmethod
    def xy_to_lat_lon(cls, x: float, y: float) -> Tuple[float, float]:
        """Inverts EPSG:3857 (meters x, y) back to WGS84 (lat, lon) in degrees."""
        lon = math.degrees(float(x) / cls.A)
        lat = math.degrees(2.0 * math.atan(math.exp(float(y) / cls.A)) - math.pi / 2.0)
        return round(lat, 6), round(lon, 6)

    @classmethod
    def lat_lon_to_tile(cls, lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """Converts (lat, lon) to integer Slippy map tile coordinate (x, y) at given zoom level."""
        clamped_lat = max(-cls.MAX_LAT, min(cls.MAX_LAT, float(lat)))
        lat_rad = math.radians(clamped_lat)
        n = 1 << zoom
        xtile = int((float(lon) + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return max(0, min(n - 1, xtile)), max(0, min(n - 1, ytile))

    @classmethod
    def tile_to_bbox(cls, tile_x: int, tile_y: int, zoom: int) -> Dict[str, float]:
        """Computes bounding box (min_lat, min_lon, max_lat, max_lon) of a Slippy tile."""
        n = 1 << zoom
        min_lon = (tile_x / n) * 360.0 - 180.0
        max_lon = ((tile_x + 1) / n) * 360.0 - 180.0

        lat_rad_top = math.atan(math.sinh(math.pi * (1.0 - 2.0 * tile_y / n)))
        lat_rad_bottom = math.atan(math.sinh(math.pi * (1.0 - 2.0 * (tile_y + 1) / n)))

        max_lat = math.degrees(lat_rad_top)
        min_lat = math.degrees(lat_rad_bottom)

        return {
            "min_lat": round(min_lat, 6),
            "min_lon": round(min_lon, 6),
            "max_lat": round(max_lat, 6),
            "max_lon": round(max_lon, 6),
        }

    @classmethod
    def tile_to_quadkey(cls, tile_x: int, tile_y: int, zoom: int) -> str:
        """Encodes tile coordinate into Bing Maps quadkey string."""
        quadkey = []
        for i in range(zoom, 0, -1):
            digit = 0
            mask = 1 << (i - 1)
            if (tile_x & mask) != 0:
                digit += 1
            if (tile_y & mask) != 0:
                digit += 2
            quadkey.append(str(digit))
        return "".join(quadkey)


class IsochroneContour:
    """Computes travel-time reachability isochrone contours over road network graph."""

    @classmethod
    def compute_isochrone(
        cls,
        origin_node: str,
        nodes: Dict[str, Tuple[float, float]],  # node_id -> (lat, lon)
        edges: List[Dict[str, Any]],           # [{u, v, distance_km, speed_kmh}]
        max_time_minutes: float,
    ) -> Dict[str, Any]:
        """Computes all reachable nodes and the convex hull boundary polygon within travel time."""
        import heapq

        # Build adjacency graph: u -> [(v, travel_time_min)]
        adj: Dict[str, List[Tuple[str, float]]] = {nid: [] for nid in nodes}
        for e in edges:
            u, v = e["u"], e["v"]
            dist = float(e.get("distance_km", 1.0))
            speed = max(1.0, float(e.get("speed_kmh", 50.0)))
            time_min = (dist / speed) * 60.0

            if u in adj:
                adj[u].append((v, time_min))
            if v in adj and not e.get("one_way", False):
                adj[v].append((u, time_min))

        # Dijkstra shortest travel times
        dist_map: Dict[str, float] = {nid: float("inf") for nid in nodes}
        dist_map[origin_node] = 0.0
        pq: List[Tuple[float, str]] = [(0.0, origin_node)]

        while pq:
            d, u = heapq.heappop(pq)
            if d > dist_map[u]:
                continue
            for v, weight in adj.get(u, []):
                new_d = d + weight
                if new_d < dist_map[v] and new_d <= max_time_minutes:
                    dist_map[v] = new_d
                    heapq.heappush(pq, (new_d, v))

        reachable_nodes = [nid for nid, t in dist_map.items() if t <= max_time_minutes]
        reachable_pts = [nodes[nid] for nid in reachable_nodes]

        # Compute 2D convex hull of reachable points (monotone chain)
        def _cross(o: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> float:
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        hull_pts: List[Tuple[float, float]] = []
        if len(reachable_pts) >= 3:
            sorted_pts = sorted(set(reachable_pts))
            lower = []
            for p in sorted_pts:
                while len(lower) >= 2 and _cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)
            upper = []
            for p in reversed(sorted_pts):
                while len(upper) >= 2 and _cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)
            hull_pts = lower[:-1] + upper[:-1]
        elif reachable_pts:
            hull_pts = list(reachable_pts)

        return {
            "origin": origin_node,
            "max_time_minutes": max_time_minutes,
            "reachable_nodes_count": len(reachable_nodes),
            "reachable_nodes": reachable_nodes,
            "contour_polygon": hull_pts,
        }


# ==============================================================================
# VINCENTY ELLIPSOIDAL GEODESICS, DOUGLAS-PEUCKER & SUTHERLAND-HODGMAN CLIPPING
# ==============================================================================

class VincentyGeodesicDistance:
    """High-precision geodesic distance on WGS-84 ellipsoid using Vincenty's inverse formula."""

    A_WGS84 = 6378137.0  # meters
    F_WGS84 = 1.0 / 298.257223563
    B_WGS84 = 6356752.314245

    @classmethod
    def distance(cls, lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, Any]:
        if abs(lat1 - lat2) < 1e-11 and abs(lon1 - lon2) < 1e-11:
            return {"distance_meters": 0.0, "distance_km": 0.0, "converged": True}

        a = cls.A_WGS84
        f = cls.F_WGS84
        b = cls.B_WGS84

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        l_diff = math.radians(lon2 - lon1)

        u1 = math.atan((1.0 - f) * math.tan(phi1))
        u2 = math.atan((1.0 - f) * math.tan(phi2))
        sin_u1 = math.sin(u1)
        cos_u1 = math.cos(u1)
        sin_u2 = math.sin(u2)
        cos_u2 = math.cos(u2)

        lam = l_diff
        converged = False

        for _ in range(100):
            sin_lam = math.sin(lam)
            cos_lam = math.cos(lam)

            sin_sigma = math.sqrt(
                (cos_u2 * sin_lam) ** 2
                + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lam) ** 2
            )
            if sin_sigma < 1e-12:
                return {"distance_meters": 0.0, "distance_km": 0.0, "converged": True}

            cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lam
            sigma = math.atan2(sin_sigma, cos_sigma)

            sin_alpha = (cos_u1 * cos_u2 * sin_lam) / sin_sigma
            cos2_alpha = 1.0 - sin_alpha ** 2

            cos2_sigmam = (
                cos_sigma - (2.0 * sin_u1 * sin_u2) / cos2_alpha
                if abs(cos2_alpha) > 1e-12
                else 0.0
            )

            c_val = (f / 16.0) * cos2_alpha * (4.0 + f * (4.0 - 3.0 * cos2_alpha))
            lam_prev = lam
            lam = l_diff + (1.0 - c_val) * f * sin_alpha * (
                sigma
                + c_val
                * sin_sigma
                * (
                    cos2_sigmam
                    + c_val * cos_sigma * (-1.0 + 2.0 * (cos2_sigmam ** 2))
                )
            )

            if abs(lam - lam_prev) < 1e-12:
                converged = True
                break

        u_sq = cos2_alpha * ((a ** 2 - b ** 2) / (b ** 2))
        a_param = 1.0 + (u_sq / 16384.0) * (
            4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq))
        )
        b_param = (u_sq / 1024.0) * (
            256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq))
        )
        delta_sigma = (
            b_param
            * sin_sigma
            * (
                cos2_sigmam
                + (b_param / 4.0)
                * (
                    cos_sigma * (-1.0 + 2.0 * (cos2_sigmam ** 2))
                    - (b_param / 6.0)
                    * cos2_sigmam
                    * (-3.0 + 4.0 * (sin_sigma ** 2))
                    * (-3.0 + 4.0 * (cos2_sigmam ** 2))
                )
            )
        )

        dist_m = b * a_param * (sigma - delta_sigma)
        return {
            "distance_meters": round(dist_m, 3),
            "distance_km": round(dist_m / 1000.0, 4),
            "converged": converged,
        }


class DouglasPeuckerSimplifier:
    """Ramer-Douglas-Peucker polyline and polygon decimation algorithm."""

    @classmethod
    def _perpendicular_distance(
        cls, pt: List[float], line_start: List[float], line_end: List[float]
    ) -> float:
        dx = line_end[0] - line_start[0]
        dy = line_end[1] - line_start[1]
        mag_sq = dx * dx + dy * dy
        if mag_sq < 1e-12:
            return math.sqrt((pt[0] - line_start[0]) ** 2 + (pt[1] - line_start[1]) ** 2)
        num = abs(dx * (line_start[1] - pt[1]) - (line_start[0] - pt[0]) * dy)
        return num / math.sqrt(mag_sq)

    @classmethod
    def simplify(cls, points: List[List[float]], epsilon: float) -> Dict[str, Any]:
        eps = max(1e-9, float(epsilon))
        if len(points) <= 2:
            return {
                "simplified_coordinates": points,
                "original_count": len(points),
                "simplified_count": len(points),
                "reduction_ratio": 0.0,
            }

        def _rdp(pts: List[List[float]]) -> List[List[float]]:
            if len(pts) <= 2:
                return pts
            d_max = 0.0
            idx = 0
            start = pts[0]
            end = pts[-1]
            for i in range(1, len(pts) - 1):
                d = cls._perpendicular_distance(pts[i], start, end)
                if d > d_max:
                    d_max = d
                    idx = i

            if d_max > eps:
                rec_left = _rdp(pts[: idx + 1])
                rec_right = _rdp(pts[idx:])
                return rec_left[:-1] + rec_right
            else:
                return [start, end]

        simplified = _rdp(points)
        orig_len = len(points)
        simp_len = len(simplified)
        red_ratio = round((orig_len - simp_len) / orig_len, 4) if orig_len > 0 else 0.0

        return {
            "simplified_coordinates": simplified,
            "original_count": orig_len,
            "simplified_count": simp_len,
            "reduction_ratio": red_ratio,
        }


class PolygonClippingSutherlandHodgman:
    """Sutherland-Hodgman convex polygon clipping algorithm."""

    @classmethod
    def clip(
        cls, subject_polygon: List[List[float]], clip_polygon: List[List[float]]
    ) -> Dict[str, Any]:
        output_list = list(subject_polygon)

        def _is_inside(cp1: List[float], cp2: List[float], p: List[float]) -> bool:
            return (cp2[0] - cp1[0]) * (p[1] - cp1[1]) - (cp2[1] - cp1[1]) * (p[0] - cp1[0]) >= -1e-9

        def _intersection(
            cp1: List[float], cp2: List[float], s: List[float], e: List[float]
        ) -> List[float]:
            dc = [cp1[0] - cp2[0], cp1[1] - cp2[1]]
            dp = [s[0] - e[0], s[1] - e[1]]
            n1 = cp1[0] * cp2[1] - cp1[1] * cp2[0]
            n2 = s[0] * e[1] - s[1] * e[0]
            denom = dc[0] * dp[1] - dc[1] * dp[0]
            if abs(denom) < 1e-12:
                return [round(s[0], 4), round(s[1], 4)]
            x = (n1 * dp[0] - n2 * dc[0]) / denom
            y = (n1 * dp[1] - n2 * dc[1]) / denom
            return [round(x, 4), round(y, 4)]

        cp_len = len(clip_polygon)
        for i in range(cp_len):
            cp1 = clip_polygon[i]
            cp2 = clip_polygon[(i + 1) % cp_len]
            input_list = output_list
            output_list = []
            if not input_list:
                break

            s = input_list[-1]
            for e in input_list:
                if _is_inside(cp1, cp2, e):
                    if not _is_inside(cp1, cp2, s):
                        output_list.append(_intersection(cp1, cp2, s, e))
                    output_list.append(e)
                elif _is_inside(cp1, cp2, s):
                    output_list.append(_intersection(cp1, cp2, s, e))
                s = e

        return {
            "clipped_polygon": output_list,
            "num_vertices": len(output_list),
        }


def geo_vincenty_distance(*args, **kwargs) -> Any:
    """Computes high-precision WGS-84 ellipsoidal distance using Vincenty's formula."""
    if len(args) == 2 and not kwargs:
        p1, p2 = args
        lat1, lon1 = _extract_lat_lon(p1)
        lat2, lon2 = _extract_lat_lon(p2)
        res = VincentyGeodesicDistance.distance(lat1, lon1, lat2, lon2)
        return res["distance_km"]
    elif len(args) == 4:
        lat1, lon1, lat2, lon2 = args
        return Record(VincentyGeodesicDistance.distance(lat1, lon1, lat2, lon2))
    elif len(args) == 2:
        lat1, lon1 = _extract_lat_lon(args[0])
        lat2, lon2 = _extract_lat_lon(args[1])
        res = VincentyGeodesicDistance.distance(lat1, lon1, lat2, lon2)
        return Record(res)
    raise TypeError(f"geo_vincenty_distance expected 2 or 4 positional arguments, got {len(args)}")


def geo_douglas_peucker(points: List[List[float]], epsilon: float) -> Any:
    """Decimates polyline or polygon using the Douglas-Peucker algorithm."""
    return Record(DouglasPeuckerSimplifier.simplify(points, epsilon))


def geo_sutherland_hodgman_clip(
    subject_polygon: List[List[float]], clip_polygon: List[List[float]]
) -> Any:
    """Clips a polygon against a convex boundary using Sutherland-Hodgman."""
    return Record(PolygonClippingSutherlandHodgman.clip(subject_polygon, clip_polygon))


class UniversalTransverseMercatorUTM:
    """Universal Transverse Mercator (UTM) ellipsoidal forward and inverse projection on WGS-84."""

    A = 6378137.0
    F = 1.0 / 298.257223563
    K0 = 0.9996

    @classmethod
    def forward(cls, lat: float, lon: float) -> Dict[str, Any]:
        phi = math.radians(lat)
        lam = math.radians(lon)

        # UTM zone 1-60
        zone = int((lon + 180.0) / 6.0) + 1
        lam0 = math.radians((zone - 1) * 6 - 180 + 3)

        e2 = 2.0 * cls.F - cls.F ** 2
        ep2 = e2 / (1.0 - e2)

        sin_phi = math.sin(phi)
        cos_phi = math.cos(phi)
        tan_phi = math.tan(phi)

        N = cls.A / math.sqrt(1.0 - e2 * (sin_phi ** 2))
        T = tan_phi ** 2
        C = ep2 * (cos_phi ** 2)
        A_diff = cos_phi * (lam - lam0)

        # Meridional arc M
        M = cls.A * (
            (1.0 - e2 / 4.0 - 3.0 * (e2 ** 2) / 64.0 - 5.0 * (e2 ** 3) / 256.0) * phi
            - (3.0 * e2 / 8.0 + 3.0 * (e2 ** 2) / 32.0 + 45.0 * (e2 ** 3) / 1024.0) * math.sin(2.0 * phi)
            + (15.0 * (e2 ** 2) / 256.0 + 45.0 * (e2 ** 3) / 1024.0) * math.sin(4.0 * phi)
            - (35.0 * (e2 ** 3) / 3072.0) * math.sin(6.0 * phi)
        )

        easting = cls.K0 * N * (
            A_diff
            + (1.0 - T + C) * (A_diff ** 3) / 6.0
            + (5.0 - 18.0 * T + (T ** 2) + 72.0 * C - 58.0 * ep2) * (A_diff ** 5) / 120.0
        ) + 500000.0

        northing = cls.K0 * (
            M
            + N * tan_phi * (
                (A_diff ** 2) / 2.0
                + (5.0 - T + 9.0 * C + 4.0 * (C ** 2)) * (A_diff ** 4) / 24.0
                + (61.0 - 58.0 * T + (T ** 2) + 600.0 * C - 330.0 * ep2) * (A_diff ** 6) / 720.0
            )
        )

        northern = (lat >= 0.0)
        if not northern:
            northing += 10000000.0

        return {
            "easting": round(easting, 2),
            "northing": round(northing, 2),
            "zone": zone,
            "northern": northern,
        }

    @classmethod
    def inverse(cls, easting: float, northing: float, zone: int, northern: bool = True) -> Dict[str, Any]:
        e2 = 2.0 * cls.F - cls.F ** 2
        ep2 = e2 / (1.0 - e2)
        e1 = (1.0 - math.sqrt(1.0 - e2)) / (1.0 + math.sqrt(1.0 - e2))

        x = float(easting) - 500000.0
        y = float(northing)
        if not northern:
            y -= 10000000.0

        M = y / cls.K0
        mu = M / (cls.A * (1.0 - e2 / 4.0 - 3.0 * (e2 ** 2) / 64.0 - 5.0 * (e2 ** 3) / 256.0))

        # Footprint latitude phi1
        phi1 = mu + (
            (3.0 * e1 / 2.0 - 27.0 * (e1 ** 3) / 32.0) * math.sin(2.0 * mu)
            + (21.0 * (e1 ** 2) / 16.0 - 55.0 * (e1 ** 4) / 32.0) * math.sin(4.0 * mu)
            + (151.0 * (e1 ** 3) / 96.0) * math.sin(6.0 * mu)
            + (1097.0 * (e1 ** 4) / 512.0) * math.sin(8.0 * mu)
        )

        sin_phi1 = math.sin(phi1)
        cos_phi1 = math.cos(phi1)
        tan_phi1 = math.tan(phi1)

        N1 = cls.A / math.sqrt(1.0 - e2 * (sin_phi1 ** 2))
        T1 = tan_phi1 ** 2
        C1 = ep2 * (cos_phi1 ** 2)
        R1 = cls.A * (1.0 - e2) / ((1.0 - e2 * (sin_phi1 ** 2)) ** 1.5)
        D = x / (N1 * cls.K0)

        lat = phi1 - (N1 * tan_phi1 / R1) * (
            (D ** 2) / 2.0
            - (5.0 + 3.0 * T1 + 10.0 * C1 - 4.0 * (C1 ** 2) - 9.0 * ep2) * (D ** 4) / 24.0
            + (61.0 + 90.0 * T1 + 298.0 * C1 + 45.0 * (T1 ** 2) - 252.0 * ep2 - 3.0 * (C1 ** 2)) * (D ** 6) / 720.0
        )

        lam0 = math.radians((zone - 1) * 6 - 180 + 3)
        lon = lam0 + (
            D
            - (1.0 + 2.0 * T1 + C1) * (D ** 3) / 6.0
            + (5.0 - 2.0 * C1 + 28.0 * T1 - 3.0 * (C1 ** 2) + 8.0 * ep2 + 24.0 * (T1 ** 2)) * (D ** 5) / 120.0
        ) / cos_phi1

        return {
            "latitude": round(math.degrees(lat), 6),
            "longitude": round(math.degrees(lon), 6),
            "zone": zone,
            "northern": northern,
        }


class GeohashSpatialEncoder:
    """Base-32 hierarchical spatial index encoding latitude and longitude into Morton order string."""

    BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
    DECODE_MAP = {c: i for i, c in enumerate(BASE32)}

    @classmethod
    def encode(cls, lat: float, lon: float, precision: int = 7) -> str:
        lat_range = [-90.0, 90.0]
        lon_range = [-180.0, 180.0]

        is_even = True
        bit = 0
        ch_idx = 0
        geohash = []

        while len(geohash) < precision:
            if is_even:
                mid = (lon_range[0] + lon_range[1]) * 0.5
                if lon >= mid:
                    ch_idx = (ch_idx << 1) | 1
                    lon_range[0] = mid
                else:
                    ch_idx = (ch_idx << 1) | 0
                    lon_range[1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) * 0.5
                if lat >= mid:
                    ch_idx = (ch_idx << 1) | 1
                    lat_range[0] = mid
                else:
                    ch_idx = (ch_idx << 1) | 0
                    lat_range[1] = mid

            is_even = not is_even
            bit += 1

            if bit == 5:
                geohash.append(cls.BASE32[ch_idx])
                bit = 0
                ch_idx = 0

        return "".join(geohash)

    @classmethod
    def decode(cls, geohash: str) -> Dict[str, Any]:
        lat_range = [-90.0, 90.0]
        lon_range = [-180.0, 180.0]
        is_even = True

        for c in str(geohash).lower():
            val = cls.DECODE_MAP.get(c, 0)
            for mask in (16, 8, 4, 2, 1):
                bit = 1 if (val & mask) else 0
                if is_even:
                    mid = (lon_range[0] + lon_range[1]) * 0.5
                    if bit == 1:
                        lon_range[0] = mid
                    else:
                        lon_range[1] = mid
                else:
                    mid = (lat_range[0] + lat_range[1]) * 0.5
                    if bit == 1:
                        lat_range[0] = mid
                    else:
                        lat_range[1] = mid
                is_even = not is_even

        center_lat = (lat_range[0] + lat_range[1]) * 0.5
        center_lon = (lon_range[0] + lon_range[1]) * 0.5

        return {
            "lat": round(center_lat, 6),
            "lon": round(center_lon, 6),
            "latitude": round(center_lat, 6),
            "longitude": round(center_lon, 6),
            "lat_min": round(lat_range[0], 6),
            "lat_max": round(lat_range[1], 6),
            "lon_min": round(lon_range[0], 6),
            "lon_max": round(lon_range[1], 6),
            "bounds": {
                "min_lat": round(lat_range[0], 6),
                "max_lat": round(lat_range[1], 6),
                "min_lon": round(lon_range[0], 6),
                "max_lon": round(lon_range[1], 6),
            },
        }


def geo_utm_forward(lat: float, lon: float) -> Record:
    """Projects geographic coordinates (lat, lon) into Universal Transverse Mercator (UTM)."""
    return Record(UniversalTransverseMercatorUTM.forward(lat, lon))


def geo_utm_inverse(easting: float, northing: float, zone: int, northern: bool = True) -> Record:
    """Inverts UTM coordinates back to geographic latitude and longitude."""
    return Record(UniversalTransverseMercatorUTM.inverse(easting, northing, zone, northern=northern))


def geo_geohash_encode(lat: float, lon: float, precision: int = 7) -> str:
    """Encodes latitude and longitude into Base-32 Geohash string."""
    return GeohashSpatialEncoder.encode(lat, lon, precision=precision)


def geo_geohash_decode(geohash: str) -> Record:
    """Decodes Geohash string into latitude/longitude bounding box and centroid."""
    return Record(GeohashSpatialEncoder.decode(geohash))


class VoronoiDiagramFortuneSweepline:
    """Voronoi Diagram Partitioning Engine via Delaunay Dual Circumcenters.

    Calculates exact polygonal Voronoi cell geometry, dual adjacency graphs,
    cell surface areas via the shoelace algorithm, and perimeter lengths.
    """

    @staticmethod
    def _circumcenter(
        p1: Tuple[float, float],
        p2: Tuple[float, float],
        p3: Tuple[float, float],
    ) -> Tuple[float, float]:
        ax, ay = p1
        bx, by = p2
        cx, cy = p3
        d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-12:
            return (ax, ay)
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return (ux, uy)

    @classmethod
    def generate(cls, sites: List[Any]) -> Dict[str, Any]:
        """Generates Voronoi partition cells for 2D generator sites."""
        sites = [tuple(s) for s in sites]
        triangles = DelaunayTriangulator.triangulate(sites)
        site_to_centers: Dict[Tuple[float, float], List[Tuple[float, float]]] = {tuple(s): [] for s in sites}
        site_neighbors: Dict[Tuple[float, float], Set[Tuple[float, float]]] = {tuple(s): set() for s in sites}

        for tri in triangles:
            cc = cls._circumcenter(tri[0], tri[1], tri[2])
            for s in tri:
                s_t = tuple(s)
                if s_t in site_to_centers:
                    site_to_centers[s_t].append(cc)
                    for other in tri:
                        o_t = tuple(other)
                        if o_t != s_t and o_t in site_neighbors:
                            site_neighbors[s_t].add(o_t)

        cells = []
        for s in sites:
            s_t = tuple(s)
            centers = site_to_centers[s_t]
            if len(centers) >= 3:
                sx, sy = s_t
                sorted_pts = sorted(centers, key=lambda c: math.atan2(c[1] - sy, c[0] - sx))
                n = len(sorted_pts)
                area = 0.5 * abs(sum(sorted_pts[i][0] * sorted_pts[(i + 1) % n][1] - sorted_pts[(i + 1) % n][0] * sorted_pts[i][1] for i in range(n)))
                perim = sum(math.hypot(sorted_pts[(i + 1) % n][0] - sorted_pts[i][0], sorted_pts[(i + 1) % n][1] - sorted_pts[i][1]) for i in range(n))
                cells.append({
                    "site": list(s_t),
                    "vertices": [[round(p[0], 3), round(p[1], 3)] for p in sorted_pts],
                    "area": round(area, 3),
                    "perimeter": round(perim, 3),
                    "neighbors_count": len(site_neighbors[s_t]),
                })
            else:
                cells.append({
                    "site": list(s_t),
                    "vertices": [[round(p[0], 3), round(p[1], 3)] for p in centers],
                    "area": 0.0,
                    "perimeter": 0.0,
                    "neighbors_count": len(site_neighbors[s_t]),
                })

        return {
            "cells": [Record(c) for c in cells],
            "total_cells": len(cells),
            "num_sites": len(sites),
            "sites_count": len(sites),
        }

    @classmethod
    def compute_cells(cls, sites: List[Tuple[float, float]], bounding_box: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, Any]:
        return cls.generate(sites)


class KrigingSpatialInterpolator:
    """Geostatistical Ordinary Kriging (BLUP) Spatial Interpolator.

    Constructs and solves Best Linear Unbiased Prediction linear system using
    semivariogram covariance kernels for continuous surface reconstruction.
    """

    @staticmethod
    def _exp_variogram(h: float, nugget: float, sill: float, range_a: float) -> float:
        if h <= 1e-9:
            return 0.0
        return nugget + sill * (1.0 - math.exp(-3.0 * h / max(1e-4, range_a)))

    @classmethod
    def interpolate(
        cls,
        known_points: Any,
        query_points: Any,
        nugget: float = 0.0,
        sill: float = 1.0,
        range_a: float = 10.0,
        range_param: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Interpolates values at query coordinates and computes Kriging estimation variance."""
        if range_param is not None:
            range_a = range_param

        normalized_known: List[Dict[str, float]] = []
        for p in known_points:
            if isinstance(p, dict):
                normalized_known.append(p)
            elif isinstance(p, (list, tuple)) and len(p) >= 3:
                normalized_known.append({"x": float(p[0]), "y": float(p[1]), "value": float(p[2])})

        n = len(normalized_known)
        if n == 0:
            return {"predictions": [], "kriging_variances": [], "first_prediction": Record({"estimated_value": 0.0})}

        m_dim = n + 1
        K = [[0.0] * m_dim for _ in range(m_dim)]
        for i in range(n):
            xi, yi = normalized_known[i]["x"], normalized_known[i]["y"]
            for j in range(i, n):
                xj, yj = normalized_known[j]["x"], normalized_known[j]["y"]
                d = math.hypot(xi - xj, yi - yj)
                val = cls._exp_variogram(d, nugget, sill, range_a)
                K[i][j] = val
                K[j][i] = val
            K[i][n] = 1.0
            K[n][i] = 1.0
        K[n][n] = 0.0

        inv_K = [[1.0 if i == j else 0.0 for j in range(m_dim)] for i in range(m_dim)]
        aug = [row[:] for row in K]

        for p in range(m_dim):
            max_r = p
            max_v = abs(aug[p][p])
            for r in range(p + 1, m_dim):
                if abs(aug[r][p]) > max_v:
                    max_v = abs(aug[r][p])
                    max_r = r
            if max_v < 1e-12:
                continue
            aug[p], aug[max_r] = aug[max_r], aug[p]
            inv_K[p], inv_K[max_r] = inv_K[max_r], inv_K[p]

            piv = aug[p][p]
            for c in range(m_dim):
                aug[p][c] /= piv
                inv_K[p][c] /= piv

            for r in range(m_dim):
                if r != p:
                    factor = aug[r][p]
                    for c in range(m_dim):
                        aug[r][c] -= factor * aug[p][c]
                        inv_K[r][c] -= factor * inv_K[p][c]

        predictions = []
        variances = []

        for q in query_points:
            qx, qy = q[0], q[1]
            k_vec = [
                cls._exp_variogram(math.hypot(qx - normalized_known[i]["x"], qy - normalized_known[i]["y"]), nugget, sill, range_a)
                for i in range(n)
            ] + [1.0]
            weights = [sum(inv_K[i][j] * k_vec[j] for j in range(m_dim)) for i in range(m_dim)]
            pred = sum(weights[i] * normalized_known[i]["value"] for i in range(n))
            var_k = sum(weights[i] * k_vec[i] for i in range(m_dim))

            rec = Record({
                "estimated_value": round(pred, 4),
                "variance": round(max(0.0, var_k), 4),
            })
            predictions.append(rec)
            variances.append(round(max(0.0, var_k), 4))

        return {
            "predictions": predictions,
            "first_prediction": predictions[0] if predictions else Record({"estimated_value": 0.0}),
            "kriging_variances": variances,
            "sample_count": n,
            "query_count": len(query_points),
        }

    @classmethod
    def fit_predict(
        cls,
        known_points: Any,
        query_points: Any,
        nugget: float = 0.0,
        sill: float = 1.0,
        range_a: float = 10.0,
        range_param: Optional[float] = None,
    ) -> Dict[str, Any]:
        return cls.interpolate(known_points, query_points, nugget=nugget, sill=sill, range_a=range_a, range_param=range_param)


def geo_voronoi_partition(sites: List[Tuple[float, float]]) -> Record:
    """Computes 2D Voronoi cell diagram from site coordinates."""
    return Record(VoronoiDiagramFortuneSweepline.generate(sites))


def geo_kriging_interpolate(
    known_points: List[Dict[str, float]],
    query_points: List[Tuple[float, float]],
    nugget: float = 0.0,
    sill: float = 1.0,
    range_a: float = 10.0,
) -> Record:
    """Calculates Ordinary Kriging spatial predictions and estimation variances."""
    return Record(KrigingSpatialInterpolator.interpolate(
        known_points, query_points, nugget=nugget, sill=sill, range_a=range_a
    ))



