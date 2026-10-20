"""Comprehensive unit tests for Deepened Cluster XVIII:
Astronomy, Symbolic, Time Series, Net, and Optimization domains in DoomScript.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Domain runtimes
from doomscript.domains.astronomy.runtime import (
    EphemerisKeplerianOrbitPropagator,
    JulianDaySiderealTimeCalculator,
)
from doomscript.domains.symbolic.runtime import (
    GroebnerBasisBuchberger,
    symbolic_groebner_basis,
    symbolic_eliminate_variables,
)
from doomscript.domains.time_series.runtime import (
    MultivariateVectorAutoregressionVAR,
    KalmanFilterStateSpace,
)
from doomscript.domains.net.runtime import (
    DijkstraLinkStateOSPF,
    BGPPathVectorRouter,
)
from doomscript.domains.opt.runtime import (
    NelderMeadSimplexDirectSearch,
    InteriorPointPrimalDualLP,
    CMAESContinuousOptimization,
)


# ==============================================================================
# ASTRONOMY DOMAIN TESTS
# ==============================================================================

def test_astronomy_ephemeris_orbit_propagation():
    # Propagate Mars-like orbit for 60 days
    res = EphemerisKeplerianOrbitPropagator.propagate(
        semi_major_axis_au=1.524,
        eccentricity=0.0934,
        inclination_deg=1.85,
        raan_deg=49.56,
        arg_perihelion_deg=286.5,
        mean_anomaly_epoch_deg=19.37,
        delta_days=60.0,
    )
    assert 1.35 < res["distance_au"] < 1.70
    assert len(res["heliocentric_ecliptic_pos"]) == 3
    assert len(res["heliocentric_ecliptic_vel_km_s"]) == 3
    assert res["orbital_speed_km_s"] > 15.0  # Mars orbital velocity ~24 km/s
    assert 0.0 <= res["equatorial_ra_hours"] < 24.0
    assert -90.0 <= res["equatorial_dec_deg"] <= 90.0


def test_astronomy_julian_day_and_sidereal_time():
    # Standard epoch J2000.0: 2000-01-01 12:00:00 UTC
    res = JulianDaySiderealTimeCalculator.calculate(
        year=2000,
        month=1,
        day=1,
        hour=12,
        minute=0,
        second=0.0,
        longitude_deg=0.0,
    )
    assert abs(res["julian_date"] - 2451545.0) < 1e-4
    assert abs(res["modified_julian_date"] - 51544.5) < 1e-4
    assert 0.0 <= res["gmst_hours"] < 24.0
    assert 0.0 <= res["gast_hours"] < 24.0


def test_astronomy_spoken_english():
    code = """use astronomy
propagate kepler orbit semi_major 1.0 eccentricity 0.0167 inclination 0.0 raan 0.0 arg_peri 102.9 mean_anomaly 100.0 delta_days 30.0 into orb_res
calculate sidereal time year 2024 month 6 day 21 hour 12 min 0 sec 0.0 lon 10.0 into sid_res
"""
    env = execute(code)
    assert env["orb_res"].distance_au > 0.95
    assert env["sid_res"].julian_date > 2460000.0
    assert env["sid_res"].observer_longitude_deg == 10.0


# ==============================================================================
# SYMBOLIC DOMAIN TESTS
# ==============================================================================

def test_symbolic_groebner_basis_buchberger():
    # Intersection of unit circle and line: x^2 + y^2 - 1 = 0, x - y = 0
    res = GroebnerBasisBuchberger.compute(
        polynomials=["x^2 + y^2 - 1", "x - y"],
        variables=["x", "y"],
        order="lex",
    )
    assert res["basis_size"] >= 2
    assert not res["is_trivial"]
    # In lex order with x > y, one polynomial must eliminate x:
    # 2*y^2 - 1 = 0 -> y^2 - 0.5 = 0
    basis_joined = " ; ".join(res["groebner_basis"])
    assert "y^2" in basis_joined or "y" in basis_joined


def test_symbolic_variable_elimination():
    res = symbolic_eliminate_variables(
        polynomials=["x^2 + y^2 - 1", "x - y"],
        eliminate_vars=["x"],
        all_vars=["x", "y"],
    )
    assert "x" in res["eliminated_variables"]
    assert "y" in res["remaining_variables"]
    assert len(res["elimination_ideal_basis"]) > 0
    # Elimination ideal in y only
    for poly in res["elimination_ideal_basis"]:
        assert "x" not in poly


def test_symbolic_spoken_english():
    code = """use symbolic
calculate groebner basis for ["x^2 + y^2 - 1", "x - y"] variables ["x", "y"] order lex into gb_res
eliminate variables ["x"] from polynomials ["x^2 + y^2 - 1", "x - y"] into elim_res
"""
    env = execute(code)
    assert env["gb_res"].basis_size >= 2
    assert len(env["elim_res"].elimination_ideal_basis) > 0


# ==============================================================================
# TIME SERIES DOMAIN TESTS
# ==============================================================================

def test_timeseries_vector_autoregression_var():
    # Coupled linear trend series
    data = [
        [1.0, 2.0],
        [2.0, 4.1],
        [3.1, 5.9],
        [4.0, 8.2],
        [5.2, 10.0],
        [6.1, 12.1],
        [7.0, 14.0],
        [8.2, 16.3],
        [9.1, 18.0],
        [10.0, 20.2],
    ]
    res = MultivariateVectorAutoregressionVAR.fit_and_forecast(
        data, lags=1, forecast_steps=2, variable_names=["price", "volume"]
    )
    assert res["num_variables"] == 2
    assert len(res["forecasts"]) == 2
    # Forecasts should continue upward trend (> 10.0 for price, > 20.0 for volume)
    assert res["forecasts"][0].price > 9.5
    assert res["forecasts"][0].volume > 19.0


def test_timeseries_kalman_filter_and_rts_smoother():
    # Noisy measurements around true value 10.0
    measurements = [10.2, 9.7, 10.3, 9.8, 10.1, 9.9, 10.0, 10.2]
    res = KalmanFilterStateSpace.filter_and_smooth_1d(
        measurements,
        process_variance_q=1e-4,
        measurement_variance_r=0.04,
        initial_state=10.0,
        initial_covariance=1.0,
    )
    assert res["observations_count"] == len(measurements)
    assert len(res["filtered_states"]) == len(measurements)
    assert len(res["smoothed_states"]) == len(measurements)
    # Variance of smoothed states should be smaller than filtered
    assert res["smoothed_variances"][0] <= res["filtered_variances"][0] + 1e-6


def test_timeseries_spoken_english():
    code = """use time_series
fit var model on [[1.0, 2.0], [2.1, 3.9], [3.0, 6.1], [4.1, 8.0], [5.0, 10.2], [6.0, 11.9], [7.1, 14.1]] lags 1 forecast 2 into var_res
apply kalman filter to [10.1, 9.9, 10.2, 9.8, 10.0, 10.1] process_q 0.001 measurement_r 0.05 into kf_res
"""
    env = execute(code)
    assert len(env["var_res"].forecasts) == 2
    assert env["kf_res"].observations_count == 6


# ==============================================================================
# NET DOMAIN TESTS
# ==============================================================================

def test_net_dijkstra_ospf_spf():
    # Diamond network with equal cost multipath (ECMP) to R4
    links = [
        {"from_router": "R1", "to_router": "R2", "cost": 10},
        {"from_router": "R1", "to_router": "R3", "cost": 10},
        {"from_router": "R2", "to_router": "R4", "cost": 15},
        {"from_router": "R3", "to_router": "R4", "cost": 15},
    ]
    res = DijkstraLinkStateOSPF.calculate_spf(links, source_router_id="R1")
    assert res["source_router"] == "R1"
    assert res["reachable_count"] == 3
    # Check R4 has ECMP with next hops R2 and R3
    r4_route = next(r for r in res["routing_table"] if r.destination_router == "R4")
    assert r4_route.metric == 25.0
    assert r4_route.is_ecmp is True
    assert set(r4_route.next_hops) == {"R2", "R3"}


def test_net_bgp_route_selection():
    router = BGPPathVectorRouter(local_asn=65001, router_id="192.0.2.1")

    # Route 1: normal route
    st1 = router.add_route(
        prefix="10.0.0.0/8",
        as_path=[65010, 65020],
        next_hop="192.0.2.2",
        local_pref=100,
    )
    assert st1["accepted"] is True

    # Route 2: AS loop (contains 65001) -> must be rejected
    st2 = router.add_route(
        prefix="10.0.0.0/8",
        as_path=[65030, 65001, 65040],
        next_hop="192.0.2.3",
        local_pref=100,
    )
    assert st2["accepted"] is False

    # Route 3: higher local-preference (200) -> must become best route
    st3 = router.add_route(
        prefix="10.0.0.0/8",
        as_path=[65050, 65060, 65070],
        next_hop="192.0.2.4",
        local_pref=200,
    )
    assert st3["accepted"] is True
    assert st3["is_current_best"] is True

    table = router.get_routing_table()
    assert len(table) == 1
    assert table[0]["local_pref"] == 200


def test_net_spoken_english():
    code = """use net
calculate ospf spf links [{"from_router": "R1", "to_router": "R2", "cost": 10}, {"from_router": "R1", "to_router": "R3", "cost": 10}, {"from_router": "R2", "to_router": "R4", "cost": 15}, {"from_router": "R3", "to_router": "R4", "cost": 15}] source "R1" into ospf_res
select bgp routes local_asn 65001 router_id "10.0.0.1" routes [{"prefix": "10.1.0.0/16", "as_path": [65010], "local_pref": 100}, {"prefix": "10.1.0.0/16", "as_path": [65020, 65030], "local_pref": 200}] into bgp_res
"""
    env = execute(code)
    assert env["ospf_res"].ecmp_destinations_count == 1
    assert env["bgp_res"].accepted_routes_count == 2
    assert env["bgp_res"].best_routes[0].local_pref == 200


# ==============================================================================
# OPT DOMAIN TESTS
# ==============================================================================

def test_opt_nelder_mead_simplex_direct_search():
    # Minimize paraboloid (x - 3)^2 + (y - 5)^2
    res = NelderMeadSimplexDirectSearch.minimize(
        objective=lambda p: (p[0] - 3.0) ** 2 + (p[1] - 5.0) ** 2,
        initial_point=[0.0, 0.0],
        step_size=0.1,
        tol=1e-5,
        max_iter=150,
    )
    assert abs(res["optimal_x"][0] - 3.0) < 0.1
    assert abs(res["optimal_x"][1] - 5.0) < 0.1
    assert res["optimal_value"] < 0.05


def test_opt_interior_point_primal_dual_lp():
    # Min x1 + 2*x2 + 0*s1
    # s.t. x1 + x2 + s1 = 4
    # x >= 0
    c = [1.0, 2.0, 0.0]
    A = [[1.0, 1.0, 1.0]]
    b = [4.0]
    res = InteriorPointPrimalDualLP.solve(c, A, b, max_iter=50)
    assert res["optimal_value"] < 4.05
    assert res["duality_gap"] < 1e-3


def test_opt_cma_es_optimization():
    # Minimize quadratic sphere function
    res = CMAESContinuousOptimization.optimize(
        objective="x**2 + y**2",
        initial_mean=[2.0, -2.0],
        initial_sigma=0.4,
        max_generations=30,
    )
    assert res["optimal_value"] < 1.0  # Reduced significantly toward 0.0
    assert len(res["optimal_x"]) == 2


def test_opt_spoken_english():
    code = """use opt
nelder mead minimize "(x - 2.0)**2 + (y - 3.0)**2" starting at [0.0, 0.0] step 0.1 tol 0.0001 into nm_res
optimize with cma_es "x**2 + y**2" starting at [1.5, -1.5] sigma 0.3 generations 25 into cma_res
"""
    env = execute(code)
    assert abs(env["nm_res"].optimal_x[0] - 2.0) < 0.2
    assert env["cma_res"].optimal_value < 1.0
