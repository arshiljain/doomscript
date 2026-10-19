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


