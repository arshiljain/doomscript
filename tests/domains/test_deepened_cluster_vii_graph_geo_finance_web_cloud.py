"""Integration and verification test suite for Deepened Cluster VII:
Graph, Geospatial, Quantitative Finance, Web Scraping, and Cloud domains in DoomScript.

Validates pure Python algorithms and native spoken-English .doom code execution.
"""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# GRAPH TESTS
# ==============================================================================

def test_graph_hopcroft_karp_bipartite_matching():
    """Validates Hopcroft-Karp maximum cardinality bipartite matching."""
    code = """
use graph
set edges to [["u1", "v1"], ["u1", "v2"], ["u2", "v2"], ["u3", "v3"]]
compute bipartite matching for edges edges into match_res
assert match_res's matching_size equals 3
assert match_res's is_perfect is true
"""
    env = execute(code)
    m = env["match_res"]
    assert m.matching_size == 3
    assert m.is_perfect is True


def test_graph_tarjan_bridges_and_cuts():
    """Validates Tarjan discovery of bridge cut-edges and articulation vertices."""
    code = """
use graph
set adj to {"A": ["B"], "B": ["A", "C"], "C": ["B"]}
find bridges and articulation points in adj into cuts_res
assert cuts_res's num_bridges equals 2
assert cuts_res's num_cut_vertices equals 1
"""
    env = execute(code)
    c = env["cuts_res"]
    assert c.num_bridges == 2
    assert c.num_cut_vertices == 1


def test_graph_hierholzer_eulerian_trail():
    """Validates Hierholzer's cycle splicing for Eulerian circuits."""
    code = """
use graph
set edges to [["A", "B"], ["B", "C"], ["C", "A"]]
find eulerian trail for edges edges into euler_res
assert euler_res's has_eulerian_circuit is true
assert euler_res's trail_length equals 4
"""
    env = execute(code)
    e = env["euler_res"]
    assert e.has_eulerian_circuit is True
    assert e.trail_length == 4


# ==============================================================================
# GEOSPATIAL (GEO) TESTS
# ==============================================================================

def test_geo_vincenty_ellipsoidal_distance():
    """Validates Vincenty inverse geodesic calculation on WGS-84 ellipsoid."""
    code = """
use geo
calculate vincenty distance from lat 52.5200 lon 13.4050 to lat 48.8566 lon 2.3522 into vinc_res
assert vinc_res's distance_km is over 800.0
assert vinc_res's distance_km is under 950.0
assert vinc_res's converged is true
"""
    env = execute(code)
    res = env["vinc_res"]
    assert 800.0 < res.distance_km < 950.0
    assert res.converged is True


def test_geo_douglas_peucker_simplification():
    """Validates Ramer-Douglas-Peucker polyline vertex decimation."""
    code = """
use geo
set raw_pts to [[0, 0], [1, 0.05], [2, -0.05], [3, 0.02], [4, 5]]
simplify polyline raw_pts with epsilon 0.2 into simp_res
assert simp_res's simplified_count is under simp_res's original_count
assert simp_res's reduction_ratio is over 0.0
"""
    env = execute(code)
    s = env["simp_res"]
    assert s.simplified_count < s.original_count
    assert s.reduction_ratio > 0.0


def test_geo_sutherland_hodgman_polygon_clipping():
    """Validates Sutherland-Hodgman convex polygon clipping."""
    code = """
use geo
set subj to [[0, 0], [4, 0], [4, 4], [0, 4]]
set clip_poly to [[1, 1], [3, 1], [3, 3], [1, 3]]
clip polygon subj against clip_poly into clip_res
assert clip_res's num_vertices equals 4
"""
    env = execute(code)
    res = env["clip_res"]
    assert res.num_vertices == 4


# ==============================================================================
# FINANCE TESTS
# ==============================================================================

def test_finance_vasicek_interest_rate():
    """Validates Vasicek short rate path simulation and analytical yield curve."""
    code = """
use finance
simulate vasicek rate from r0 0.03 speed 0.15 mean 0.05 vol 0.01 expiry 1.0 into vas_res
assert vas_res's initial_rate equals 0.03
assert length of vas_res's yield_curve equals 10
"""
    env = execute(code)
    vas = env["vas_res"]
    assert vas.initial_rate == 0.03
    assert len(vas.yield_curve) == 10


def test_finance_bond_duration_and_convexity():
    """Validates Macaulay duration, modified duration, DV01, and convexity."""
    code = """
use finance
analyze bond duration with face 1000 coupon 0.06 maturity 5 ytm 0.05 into bond_res
assert bond_res's macaulay_duration is over 4.0
assert bond_res's modified_duration is over 3.9
assert bond_res's convexity is over 15.0
assert bond_res's dv01 is over 0.3
"""
    env = execute(code)
    b = env["bond_res"]
    assert b.macaulay_duration > 4.0
    assert b.modified_duration > 3.9
    assert b.convexity > 15.0
    assert b.dv01 > 0.3


def test_finance_heston_stochastic_volatility():
    """Validates Heston stochastic volatility path simulation."""
    code = """
use finance
simulate heston volatility spot 100 vol 0.04 kappa 2.0 theta 0.04 xi 0.3 rho -0.7 into heston_res
assert heston_res's initial_price equals 100
assert heston_res's initial_variance equals 0.04
assert length of heston_res's price_trajectory equals 101
"""
    env = execute(code)
    h = env["heston_res"]
    assert h.initial_price == 100
    assert h.initial_variance == 0.04
    assert len(h.price_trajectory) == 101


# ==============================================================================
# WEB TESTS
# ==============================================================================

def test_web_multipart_form_encode():
    """Validates RFC 7578 multipart/form-data encoding."""
    code = """
use web
encode multipart form fields {"username": "admin", "token": "xyz987"} into mp_res
assert mp_res's content_length is over 0
assert mp_res's boundary is not empty
"""
    env = execute(code)
    mp = env["mp_res"]
    assert mp.content_length > 0
    assert len(mp.boundary) > 0


def test_web_content_negotiate():
    """Validates RFC 7231 content type negotiation and q-values."""
    code = """
use web
set supported to ["application/json", "application/xml", "text/html"]
negotiate content type for header "text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8" from supported into best_type
assert best_type equals "text/html"
"""
    env = execute(code)
    assert env["best_type"] == "text/html"


def test_web_uri_template_expand():
    """Validates RFC 6570 Level 3 URI template expansion."""
    code = """
use web
set t_vars to {"id": "42", "format": "json"}
expand uri template "https://api.example.com/items{/id}{?format}" with variables t_vars into full_url
assert full_url equals "https://api.example.com/items/42?format=json"
"""
    env = execute(code)
    assert env["full_url"] == "https://api.example.com/items/42?format=json"


# ==============================================================================
# CLOUD TESTS
# ==============================================================================

def test_cloud_token_bucket_rate_limiter():
    """Validates Token Bucket rate limiter acquisition and token consumption."""
    code = """
use cloud
create rate limiter with capacity 5 and refill rate 1 into limiter
acquire 2 tokens from rate limiter limiter into acq1
acquire 2 tokens from rate limiter limiter into acq2
acquire 2 tokens from rate limiter limiter into acq3

assert acq1's allowed is true
assert acq2's allowed is true
assert acq3's allowed is false
"""
    env = execute(code)
    assert env["acq1"].allowed is True
    assert env["acq2"].allowed is True
    assert env["acq3"].allowed is False


def test_cloud_circuit_breaker():
    """Validates Circuit Breaker initial state and parameters."""
    code = """
use cloud
create circuit breaker with failure threshold 3 into cb
assert cb's state equals "CLOSED"
assert cb's failure_threshold equals 3
"""
    env = execute(code)
    cb = env["cb"]
    assert cb.state == "CLOSED"
    assert cb.failure_threshold == 3


def test_cloud_raft_consensus():
    """Validates Raft consensus candidate election and term advancement."""
    code = """
use cloud
create raft node "node_1" with peers ["node_1", "node_2", "node_3"] into raft
elect raft leader for raft into elect_res
assert elect_res's term equals 1
assert elect_res's role equals "CANDIDATE"
assert elect_res's votes_count equals 1
"""
    env = execute(code)
    el = env["elect_res"]
    assert el.term == 1
    assert el.role == "CANDIDATE"
    assert el.votes_count == 1
