"""Cartography Domain Runtime: Haversine distance, initial bearing, Mercator projection, UTM zones, Tissot indicatrix, WGS84 ellipsoidal geodesy, and Rhumb lines."""
import math
from typing import Dict, Any, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime

EARTH_RADIUS_KM = 6371.0
WGS84_A = 6378137.0         # semi-major axis (meters)
WGS84_F = 1.0 / 298.257223563 # flattening
WGS84_E2 = 2.0 * WGS84_F - (WGS84_F ** 2) # first eccentricity squared

# ============================================================================
# 1. PRESERVED EXISTING EQUATIONS
# ============================================================================

def carto_haversine_distance(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float, earth_radius_km: float = 6371.0) -> float:
    """Calculates great-circle distance between two coordinates in kilometers using Haversine formula."""
    phi1 = math.radians(float(lat1_deg))
    phi2 = math.radians(float(lat2_deg))
    delta_phi = math.radians(float(lat2_deg) - float(lat1_deg))
    delta_lambda = math.radians(float(lon2_deg) - float(lon1_deg))

    a = (math.sin(delta_phi / 2.0) ** 2) + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(float(earth_radius_km) * c, 2)

def carto_initial_bearing(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float) -> float:
    """Calculates initial compass bearing/azimuth from point 1 to point 2 in degrees [0, 360)."""
    phi1 = math.radians(float(lat1_deg))
    phi2 = math.radians(float(lat2_deg))
    delta_lambda = math.radians(float(lon2_deg) - float(lon1_deg))

    y = math.sin(delta_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
    bearing_rad = math.atan2(y, x)
    bearing_deg = (math.degrees(bearing_rad) + 360.0) % 360.0
    return round(bearing_deg, 2)

def carto_mercator_projection(lat_deg: float, lon_deg: float, r_km: float = 6371.0) -> Dict[str, float]:
    """Forward spherical Mercator projection: x = R * lambda, y = R * ln(tan(pi/4 + phi/2))."""
    phi = math.radians(max(-85.05, min(85.05, float(lat_deg))))
    lam = math.radians(float(lon_deg))
    r = float(r_km)
    x = r * lam
    y = r * math.log(math.tan(math.pi / 4.0 + phi / 2.0))
    return {"x_km": round(x, 2), "y_km": round(y, 2)}

def carto_utm_zone(lon_deg: float) -> int:
    """Calculates Universal Transverse Mercator (UTM) longitudinal zone number (1-60)."""
    lon = float(lon_deg)
    zone = int(math.floor((lon + 180.0) / 6.0)) + 1
    if zone > 60:
        zone = 60
    elif zone < 1:
        zone = 1
    return zone

def carto_ground_distance(map_distance_cm: float, scale_ratio: float) -> float:
    """Calculates real-world ground distance in meters given map distance in cm and scale denominator (e.g. 1:50,000)."""
    cm = float(map_distance_cm)
    scale = float(scale_ratio)
    ground_m = (cm * scale) / 100.0
    return round(ground_m, 2)

def carto_tissot_indicatrix_distortion(lat_deg: float) -> Dict[str, float]:
    """Calculates Mercator scale factor distortion k = sec(phi) and areal deformation factor."""
    phi = math.radians(min(85.0, abs(float(lat_deg))))
    k = 1.0 / math.cos(phi)
    area_scale = k ** 2
    return {"linear_scale_factor": round(k, 3), "area_scale_factor": round(area_scale, 3)}

# ============================================================================
# 2. DEEPENED WGS84 GEODESY & RHUMB LINES
# ============================================================================

def carto_wgs84_to_ecef(lat_deg: float, lon_deg: float, height_m: float = 0.0) -> Dict[str, float]:
    """Converts WGS84 ellipsoidal coordinates (lat, lon, height) to Earth-Centered, Earth-Fixed (ECEF) X, Y, Z meters."""
    phi = math.radians(float(lat_deg))
    lam = math.radians(float(lon_deg))
    h = float(height_m)

    # Prime vertical radius of curvature N(phi)
    n_phi = WGS84_A / math.sqrt(1.0 - WGS84_E2 * (math.sin(phi) ** 2))
    x = (n_phi + h) * math.cos(phi) * math.cos(lam)
    y = (n_phi + h) * math.cos(phi) * math.sin(lam)
    z = (n_phi * (1.0 - WGS84_E2) + h) * math.sin(phi)

    return {
        "x_m": round(x, 2),
        "y_m": round(y, 2),
        "z_m": round(z, 2)
    }

def carto_rhumb_line_distance(lat1_deg: float, lon1_deg: float, lat2_deg: float, lon2_deg: float) -> Dict[str, float]:
    """Calculates constant course Rhumb Line (Loxodrome) distance (km) and true heading (degrees)."""
    phi1 = math.radians(float(lat1_deg))
    phi2 = math.radians(float(lat2_deg))
    d_phi = phi2 - phi1
    d_lam = math.radians(float(lon2_deg) - float(lon1_deg))

    # Projected latitude difference
    delta_psi = math.log(math.tan(math.pi / 4.0 + phi2 / 2.0) / math.tan(math.pi / 4.0 + phi1 / 2.0))
    q = (d_phi / delta_psi) if abs(delta_psi) > 1e-12 else math.cos(phi1)

    # If crossing antimeridian
    if abs(d_lam) > math.pi:
        d_lam = -(2.0 * math.pi - d_lam) if d_lam > 0 else (2.0 * math.pi + d_lam)

    dist_km = math.sqrt(d_phi ** 2 + (q * d_lam) ** 2) * EARTH_RADIUS_KM
    heading_deg = (math.degrees(math.atan2(d_lam, delta_psi)) + 360.0) % 360.0

    return {
        "distance_km": round(dist_km, 2),
        "constant_heading_deg": round(heading_deg, 2)
    }

class CartographyRuntime(DomainRuntime):
    """Runtime engine for Cartography domain calculations."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def haversine(self, lat1: float, lon1: float, lat2: float, lon2: float, r: float = 6371.0) -> float:
        return carto_haversine_distance(lat1, lon1, lat2, lon2, r)
    def bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return carto_initial_bearing(lat1, lon1, lat2, lon2)
    def mercator(self, lat: float, lon: float, r: float = 6371.0) -> Dict[str, float]:
        return carto_mercator_projection(lat, lon, r)
    def utm(self, lon: float) -> int:
        return carto_utm_zone(lon)
    def scale(self, cm: float, s: float) -> float:
        return carto_ground_distance(cm, s)
    def distortion(self, lat: float) -> Dict[str, float]:
        return carto_tissot_indicatrix_distortion(lat)
    def ecef(self, lat: float, lon: float, h: float = 0.0) -> Dict[str, float]:
        return carto_wgs84_to_ecef(lat, lon, h)
    def rhumb_line(self, lat1: float, lon1: float, lat2: float, lon2: float) -> Dict[str, float]:
        return carto_rhumb_line_distance(lat1, lon1, lat2, lon2)
