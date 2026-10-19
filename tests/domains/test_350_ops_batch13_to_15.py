"""Comprehensive Test Suite for Group D (Batches 13–15) of 350 Domain Operations.
Covers:
- Batch 13: Geospatial Analysis & GIS (19 operations)
- Batch 14: Optimization & Combinatorics (19 operations)
- Batch 15: Autonomous Agents & Teams (19 operations)
Total: 57 operations.
"""

import os
import pytest
from doomscript.compiler.engine import execute


def test_batch13_geospatial_operations():
    """Batch 13: Geohash, Bearings, Midpoint, Cross-track, BBox overlap/union, Convex hull, Distance to line, Polyline simplification, GeoJSON, Perimeter, Buffers, UTM, Rhumb line."""
    source = """use geo

encode geohash lat 37.7749 lon -122.4194 with precision 8 into gh
decode geohash gh into gh_decoded
initial bearing from [37.7749, -122.4194] to [34.0522, -118.2437] into init_brng
final bearing from [37.7749, -122.4194] to [34.0522, -118.2437] into fin_brng
destination point from lat 37.7749 lon -122.4194 distance 100 bearing 90 into dest_pt
midpoint between [37.7749, -122.4194] and [34.0522, -118.2437] into mid_pt
cross track distance of [36.0, -120.0] from [37.7749, -122.4194] to [34.0522, -118.2437] into xtd
bounding box intersection of [0, 0, 10, 10] and [5, 5, 15, 15] into bbox_int
bounding box union of [0, 0, 10, 10] and [5, 5, 15, 15] into bbox_un
convex hull of [[0, 0], [1, 1], [2, 0], [1, 2], [0.5, 0.5]] into hull_pts
distance from point [0, 1] to line segment from [0, 0] to [2, 0] into ptl_dist
simplify polyline [[0, 0], [1, 0.1], [2, -0.1], [3, 0], [4, 0]] with tolerance 20.0 into simplified
convert coordinates [[[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]]] to geojson polygon into gj_poly
convert features [gj_poly] to geojson feature collection into gj_fc
calculate perimeter of polygon [[0, 0], [0, 1], [1, 1], [1, 0], [0, 0]] into poly_perim
circular buffer around [37.7749, -122.4194] with radius 10 and 16 points into circ_buf
utm zone for longitude -122.4194 into utm_z
rhumb line distance between [37.7749, -122.4194] and [34.0522, -118.2437] into rhumb_d
rhumb line bearing from [37.7749, -122.4194] to [34.0522, -118.2437] into rhumb_b
"""
    env = execute(source)
    assert len(env["gh"]) == 8
    assert isinstance(env["gh_decoded"], dict)
    assert abs(env["gh_decoded"]["latitude"] - 37.7749) < 0.01
    assert 0 <= env["init_brng"] <= 360
    assert 0 <= env["fin_brng"] <= 360
    assert isinstance(env["dest_pt"], (list, tuple))
    assert isinstance(env["mid_pt"], (list, tuple))
    assert isinstance(env["xtd"], float)
    assert env["bbox_int"] == [5, 5, 10, 10]
    assert env["bbox_un"] == [0, 0, 15, 15]
    assert len(env["hull_pts"]) >= 3
    assert abs(env["ptl_dist"] - 111.1951) < 0.1
    assert len(env["simplified"]) < 5
    assert env["gj_poly"]["type"] == "Feature"
    assert env["gj_fc"]["type"] == "FeatureCollection"
    assert env["poly_perim"] > 0
    assert len(env["circ_buf"]) == 17  # 16 points closed ring
    assert env["utm_z"] == 10
    assert env["rhumb_d"] > 0
    assert 0 <= env["rhumb_b"] <= 360


def test_batch14_optimization_and_combinatorics():
    """Batch 14: Simulated annealing, Golden section, Knapsack DP, LIS, Coin change, Job scheduling, Huffman, Matrix chain, Levenshtein alignment, Subset sum, Rod cutting, TSP 2-opt, Linear interp, Weighted interval scheduling, Pareto frontier, Hungarian, Peak."""
    source = """use opt

simulated annealing for "lambda x: (x - 3) ** 2" starting at 10.0 with temp 50.0 cooling 0.9 into sa_res
golden section search for "lambda x: (x - 2) ** 2" between 0.0 and 5.0 with tolerance 0.001 into gss_res
solve 01 knapsack weights [2, 3, 4, 5] values [3, 4, 5, 6] capacity 5 into ks_res
longest increasing subsequence of [10, 9, 2, 5, 3, 7, 101, 18] into lis_res
minimum coins for amount 11 with coins [1, 2, 5] into mc_res
coin combinations for amount 5 with coins [1, 2, 5] into cc_res
schedule jobs by deadline [{"id": "a", "deadline": 2, "profit": 100}, {"id": "b", "deadline": 1, "profit": 19}, {"id": "c", "deadline": 2, "profit": 27}] into sj_res
huffman encoding for frequencies {"a": 5, "b": 9, "c": 12, "d": 13, "e": 16, "f": 45} into he_res
matrix chain multiplication order for dimensions [10, 30, 5, 60] into mcm_res
levenshtein alignment between "kitten" and "sitting" into la_res
check if subset sum exists in [3, 34, 4, 12, 5, 2] for target 9 into sse_res
find subset summing to 9 from [3, 34, 4, 12, 5, 2] into ssf_res
solve rod cutting for length 4 with prices [1, 5, 8, 9, 10] into rc_res
optimize tsp with 2opt for coordinates [[0, 0], [0, 1], [1, 1], [1, 0]] iterations 50 into tsp_res
interpolate linear value at 2.5 from x [1, 2, 3, 4] and y [10, 20, 30, 40] into interp_res
weighted interval scheduling for [{"start": 1, "end": 3, "weight": 5}, {"start": 2, "end": 5, "weight": 6}, {"start": 4, "end": 6, "weight": 5}] into wis_res
find pareto frontier for [[1, 5], [2, 4], [3, 3], [1, 1], [0, 2]] into pf_res
hungarian assignment for cost matrix [[9, 2, 7], [6, 4, 3], [5, 8, 1]] into ha_res
find peak element in [1, 3, 20, 4, 1, 0] into pk_res
"""
    env = execute(source)
    assert isinstance(env["sa_res"], (int, float))
    assert abs(env["gss_res"] - 2.0) < 0.01
    assert env["ks_res"]["max_value"] == 7.0
    assert len(env["lis_res"]) == 4  # [2, 3, 7, 18] or [2, 5, 7, 18] etc
    assert env["mc_res"] == 3  # 5 + 5 + 1
    assert env["cc_res"] == 4
    assert env["sj_res"]["total_profit"] == 127.0
    assert len(env["he_res"]) == 6
    assert env["mcm_res"]["min_multiplications"] == 4500
    assert env["la_res"]["distance"] == 3
    assert env["sse_res"] is True
    assert sum(env["ssf_res"]) == 9
    assert env["rc_res"]["max_revenue"] == 10.0
    assert len(env["tsp_res"]["tour"]) == 4
    assert abs(env["interp_res"] - 25.0) < 1e-4
    assert env["wis_res"]["max_weight"] == 10.0
    assert len(env["pf_res"]) >= 1
    assert env["ha_res"]["min_cost"] == 9.0  # 2 + 6 + 1
    assert env["pk_res"]["value"] == 20.0


def test_batch15_agent_workflows():
    """Batch 15: Evaluation, Chat history, Memory summary, Keyword routing, Retry backoff, JSON schema, Action calls, CoT, Consensus, Debate, Breakdown, Date filter, Merge, Tools, Persona, Safety, Turns, Transcript."""
    source = """use agent

create agent "assistant" with role "researcher" into ag1
create agent "critic" with role "reviewer" into ag2

tell agent ag1 "The speed of light is 300,000 km/s"
evaluate response quality of "The speed of light is roughly 300000 km per second in vacuum." with rubric ["light", "speed"] into qual_res
format chat history of ag1 as "json" into fch_res
summarize memory of ag1 max tokens 200 into sm_res
route task "write a python script to sort numbers" using skills {"coder": ["python", "script"], "writer": ["essay"]} into route_res
retry task "hello agent" with agent ag1 max retries 2 into retry_res
validate json output of '{"status": "ok", "code": 200}' against schema {"required": ["status", "code"]} into vjo_res
extract action calls from "ACTION: search_web(query='quantum')" into acts_res
chain of thought prompt for task "solve riddle" with context "none" into cot_res
calculate consensus agreement among ["the answer is 42", "the answer is definitely 42"] into cons_res
debate topic "AI safety" between ag1 and ag2 for 1 rounds into deb_res
plan task breakdown for "build a web app" with agent ag1 into ptb_res
filter memory of ag1 from "2026-01-01" to "2026-12-31" into fmd_res
merge memories of ag1 and ag2 into ag1
inspect available tools of agent ag1 into tools_res
set persona of agent ag1 to role "expert" and instructions "be concise"
audit conversation safety of [{"role": "user", "content": "hello world"}] against ["malware", "virus"] into saf_res
count conversation turns of agent ag1 into turns_res
export chat transcript of agent ag1 to "test_transcript_ag.md" into exp_res
"""
    env = execute(source)
    assert env["qual_res"]["passed"] is True
    assert "The speed of light" in env["fch_res"]
    assert "turns_before" in env["sm_res"]
    assert env["route_res"] == "coder"
    assert env["retry_res"]["status"] == "success"
    assert env["vjo_res"]["valid"] is True
    assert len(env["acts_res"]) == 1
    assert env["acts_res"][0]["tool"] == "search_web"
    assert "Chain-of-Thought" in env["cot_res"]["technique"]
    assert env["cons_res"] > 0.5
    assert len(env["deb_res"]["transcript"]) == 2
    assert len(env["ptb_res"]["subtasks"]) >= 3
    assert isinstance(env["fmd_res"], list)
    assert env["saf_res"]["safe"] is True
    assert env["turns_res"]["total"] >= 1
    assert os.path.exists("test_transcript_ag.md")
    if os.path.exists("test_transcript_ag.md"):
        os.remove("test_transcript_ag.md")
