import pytest
from doomscript.compiler.engine import execute

def test_batch12_net():
    code = """
use net

ping host "127.0.0.1" into ping_res
resolve dns "localhost" into resolved_ip
check port 80 on host "127.0.0.1" with timeout 0.5 into port_res
create basic auth header for "admin" with "secret123" into basic_auth
create bearer auth header with token "my_token_abc" into bearer_auth
check internet connectivity into online_status
"""
    result = execute(code)
    assert "ping_res" in result
    assert isinstance(result["ping_res"], bool)
    
    assert "resolved_ip" in result
    assert isinstance(result["resolved_ip"], list)
    assert len(result["resolved_ip"]) > 0
    
    assert "port_res" in result
    assert isinstance(result["port_res"], bool)
    
    assert "Authorization" in result["basic_auth"]
    assert result["basic_auth"]["Authorization"].startswith("Basic ")
    assert result["bearer_auth"] == {"Authorization": "Bearer my_token_abc"}
    assert isinstance(result["online_status"], bool)

def test_batch13_sim():
    code = """
use sim

simulate random walk with 10 steps starting at 5 into walk
generate exponential sample with rate 2.0 into exp_val
generate poisson sample with lambda 3.0 into poi_val
estimate pi with 1000 monte carlo samples into pi_estimate
roll 4 dice with 6 sides into dice_rolls
simulate 8 coin tosses with probability 0.5 into coin_flips
"""
    result = execute(code)
    assert len(result["walk"]) == 11
    assert result["walk"][0] == 5
    
    assert isinstance(result["exp_val"], float)
    assert result["exp_val"] >= 0.0
    
    assert isinstance(result["poi_val"], int)
    assert result["poi_val"] >= 0
    
    assert 2.0 < result["pi_estimate"] < 4.0
    
    assert len(result["dice_rolls"]) == 4
    assert all(1 <= d <= 6 for d in result["dice_rolls"])
    
    assert len(result["coin_flips"]) == 8
    assert all(c in ("H", "T") for c in result["coin_flips"])

def test_batch14_geo():
    code = """
use geo

calculate haversine distance from [40.7128, -74.0060] to [34.0522, -118.2437] into dist_km
check if bounding box [0, 0, 10, 10] contains [5, 5] into is_inside
calculate centroid of coordinates [[0, 0], [10, 0], [10, 10], [0, 10]] into centroid_pt
calculate polygon area for coordinates [[0, 0], [10, 0], [10, 10], [0, 10]] into area_val
convert coordinate [40.7128, -74.0060] to geojson point into geo_pt
find nearest coordinate to [5, 5] from [[0, 0], [4, 4], [20, 20]] into nearest_coord
"""
    result = execute(code)
    assert result["dist_km"] > 3000
    assert result["is_inside"] is True
    assert result["centroid_pt"] == [5.0, 5.0]
    assert result["area_val"] == 100.0
    assert result["geo_pt"]["type"] == "Feature"
    assert result["geo_pt"]["geometry"]["type"] == "Point"
    assert result["geo_pt"]["geometry"]["coordinates"] == [-74.006, 40.7128]
    assert result["nearest_coord"] == [4, 4]

def test_batch15_opt():
    code = """
use opt

def quad(x):
    return (x - 3.0) * (x - 3.0)

minimize 1d function quad from 0 to 6 with tolerance 0.01 into min_x
grid search params {"x": [1, 2, 3]} with quad into best_param
solve fractional knapsack weights [10, 20, 30] values [60, 100, 120] capacity 50 into knap_val
schedule activities with [1, 3, 0, 5, 8, 5] and [2, 4, 6, 7, 9, 9] into selected_acts
gradient descent step at 10.0 with gradient 2.0 lr 0.1 into next_w

def linear_fn(x):
    return x - 2.5

find root of function linear_fn between 0 and 5 with tolerance 0.001 into root_res
"""
    result = execute(code)
    assert abs(result["min_x"] - 3.0) < 0.1
    assert result["best_param"]["best_params"] == {"x": 3}
    assert result["best_param"]["best_score"] == 0.0
    assert result["knap_val"]["total_value"] == 240.0
    assert len(result["selected_acts"]) == 4
    assert abs(result["next_w"] - 9.8) < 1e-5
    assert abs(result["root_res"] - 2.5) < 0.01
