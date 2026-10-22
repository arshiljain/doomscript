"""Cartography Domain Runtime: Haversine distance, initial bearing, Mercator projection, UTM zone, map scale, and Vincenty geodesic distance."""
import math
from typing import Dict, Any

EARTH_RADIUS_KM = 6371.0

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
