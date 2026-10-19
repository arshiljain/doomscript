"""Unit and integration tests for Geospatial Analytics domain (use geo)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.geo.runtime import (
    point,
    polygon,
    distance_between,
    is_point_in_polygon,
    bounding_box,
    spatial_join,
    to_geojson,
)


def test_geo_runtime_point_and_distance():
    # New York City (approx 40.7128, -74.0060)
    nyc = point(40.7128, -74.0060)
    assert nyc["lat"] == 40.7128
    assert nyc["lon"] == -74.0060
    assert nyc["type"] == "Point"
    assert nyc["coordinates"] == [-74.0060, 40.7128]

    # London (approx 51.5074, -0.1278)
    london = point(51.5074, -0.1278)

    # Great-circle distance between NYC and London is ~5570 km
    d_km = distance_between(nyc, london, unit="km")
    assert 5500 < d_km < 5650

    d_miles = distance_between(nyc, london, unit="miles")
    assert 3400 < d_miles < 3550


def test_geo_runtime_polygon_and_containment():
    # Square around (0, 0)
    coords = [[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0], [-1.0, -1.0]]
    sq = polygon(coords)
    assert sq["type"] == "Polygon"

    # Inside
    p_inside = point(0.0, 0.0)
    assert is_point_in_polygon(p_inside, sq) is True

    # Outside
    p_outside = point(2.0, 2.0)
    assert is_point_in_polygon(p_outside, sq) is False


def test_geo_runtime_bounding_box_and_geojson():
    coords = [[0.0, 10.0], [5.0, 15.0], [2.0, 20.0]]
    pts = [point(c[0], c[1]) for c in coords]
    bbox = bounding_box(pts)
    assert bbox["min_lat"] == 0.0
    assert bbox["max_lat"] == 5.0
    assert bbox["min_lon"] == 10.0
    assert bbox["max_lon"] == 20.0

    p = point(37.7749, -122.4194)
    gj = to_geojson(p)
    assert gj["type"] == "Feature"
    assert gj["geometry"]["type"] == "Point"
    assert gj["geometry"]["coordinates"] == [-122.4194, 37.7749]


def test_geo_domain_execution():
    source = """use geo

point at 40.7128, -74.0060 into nyc
point at 51.5074, -0.1278 into london

distance between nyc and london in km into flight_dist
bounding box of [nyc, london] into ny_lon_box
"""
    env = execute(source)
    assert "nyc" in env
    assert "london" in env
    assert "flight_dist" in env
    assert 5500 < env["flight_dist"] < 5650
    assert "ny_lon_box" in env
    assert env["ny_lon_box"]["min_lat"] == 40.7128
    assert env["ny_lon_box"]["max_lat"] == 51.5074


def test_geo_spatial_join_execution():
    source = """use geo

square_coords = [[-2.0, -2.0], [2.0, -2.0], [2.0, 2.0], [-2.0, 2.0], [-2.0, -2.0]]
polygon from square_coords into boundary

point at 0.5, 0.5 into p_in
point at 5.0, 5.0 into p_out

check if p_in is inside boundary into in_res
check if p_out is inside boundary into out_res

spatial join [p_in, p_out] with [boundary] into matched
"""
    env = execute(source)
    assert env["in_res"] is True
    assert env["out_res"] is False
    assert len(env["matched"]) == 1


def test_geo_ast_export():
    source = """use geo

point at 10.0, 20.0 into p1
point at 15.0, 25.0 into p2
distance between p1 and p2 in km into d
"""
    py_code = export_to_python(source)
    assert "distance_between" in py_code or "point" in py_code
