"""Comprehensive test suite for Cluster XV deepened engines (Bio, Neuro, Physics, Sim, Geo).

Validates pure Python runtime engines and end-to-end spoken English .doom scripts.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Import runtime classes & functions
from doomscript.domains.bio.runtime import (
    AffineGapGotohAligner,
    KozakConsensusScanner,
    bio_affine_align,
    bio_kozak_scan,
)
from doomscript.domains.neuro.runtime import (
    BienenstockCooperMunroBCM,
    AdaptiveExponentialAdExNeuron,
    neuro_bcm_train,
    neuro_adex_simulate,
)
from doomscript.domains.physics.runtime import (
    SymplecticStormerVerletIntegrator,
    BrachistochroneCycloidCalculator,
    physics_symplectic_verlet,
    physics_brachistochrone,
)
from doomscript.domains.sim.runtime import (
    AgentBasedEpidemicSEIRModel,
    GillespieExactSSA,
    sim_seir_epidemic,
    sim_gillespie_ssa,
)
from doomscript.domains.geo.runtime import (
    UniversalTransverseMercatorUTM,
    GeohashSpatialEncoder,
    geo_utm_forward,
    geo_utm_inverse,
    geo_geohash_encode,
    geo_geohash_decode,
)


# ==============================================================================
# BIO DOMAIN TESTS
# ==============================================================================

def test_bio_affine_align():
    res = AffineGapGotohAligner.align("ACGTACGT", "ACTACGT", match_score=2.0, mismatch_score=-1.0, gap_open=3.0, gap_extend=1.0)
    assert res["score"] > 0
    assert len(res["aligned_seq1"]) == len(res["aligned_seq2"])
    assert "-" in res["aligned_seq2"]


def test_bio_kozak_scan():
    seq = "NNNGCCACCATGGNNN"
    res = KozakConsensusScanner.scan(seq)
    assert res["sites_count"] >= 1
    best = res["candidate_sites"][0]
    assert best["codon"] == "AUG"
    assert best["strength"] == "strong"


def test_bio_spoken_english():
    code = """use bio
align sequences "ACGTACGT" and "ACTACGT" with affine gap open 3.0 extend 1.0 into aff_res
scan kozak consensus in sequence "GCCACCATGG" into koz_res
"""
    env = execute(code)
    assert env["aff_res"].score > 0
    assert env["koz_res"].sites_count >= 1


# ==============================================================================
# NEURO DOMAIN TESTS
# ==============================================================================

def test_neuro_bcm():
    pats = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
    res = BienenstockCooperMunroBCM.train(pats, epochs=25, eta=0.01)
    assert len(res["weights"]) == 2
    assert res["theta_m"] >= 0.0
    assert res["epochs"] == 25


def test_neuro_adex():
    res = AdaptiveExponentialAdExNeuron.simulate(duration_ms=60.0, dt_ms=0.1, current_i=350.0)
    assert res["duration_ms"] if "duration_ms" in res else True
    assert res["num_spikes"] >= 1
    assert len(res["spike_times"]) == res["num_spikes"]
    assert res["firing_frequency_hz"] > 0.0


def test_neuro_spoken_english():
    code = """use neuro
set train_pats to [[1.0, 0.0], [0.0, 1.0]]
train bcm synapses with patterns train_pats and epochs 15 into bcm_res
simulate adex neuron with current 350.0 and duration 50.0 into adex_res
"""
    env = execute(code)
    assert len(env["bcm_res"].weights) == 2
    assert env["adex_res"].num_spikes >= 1


# ==============================================================================
# PHYSICS DOMAIN TESTS
# ==============================================================================

def test_physics_symplectic_verlet():
    # Harmonic oscillator with energy conservation
    res = SymplecticStormerVerletIntegrator.simulate_harmonic_oscillator(x0=1.0, v0=0.0, duration=10.0, dt=0.01)
    assert res["steps_count"] == 1000
    # Energy drift should be very small for symplectic integrator
    assert res["max_energy_drift"] < 1e-3
    assert res["is_energy_conserved"] is True


def test_physics_brachistochrone():
    res = BrachistochroneCycloidCalculator.calculate(x_end=1.0, y_end=1.0)
    assert res["cycloid_time_sec"] > 0.0
    # Brachistochrone time should be strictly less than straight-line ramp time: t_ramp = sqrt(2*(x^2+y^2)/(g*y)) = sqrt(4/9.81) ~ 0.638s
    # Cycloid time ~ 0.583s
    assert res["cycloid_time_sec"] < res["straight_line_time_sec"]
    assert res["time_saved_percent"] > 0.0


def test_physics_spoken_english():
    code = """use physics
simulate symplectic verlet with x 1.0 and v 0.0 duration 5.0 into verlet_res
calculate brachistochrone from origin to x 1.0 and y 1.0 into brach_res
"""
    env = execute(code)
    assert env["verlet_res"].steps_count > 0
    assert env["verlet_res"].is_energy_conserved is True
    assert env["brach_res"].cycloid_time_sec > 0.0


# ==============================================================================
# SIM DOMAIN TESTS
# ==============================================================================

def test_sim_seir_epidemic():
    res = AgentBasedEpidemicSEIRModel.simulate(num_agents=50, steps=30, transmission_prob=0.4)
    assert res["total_agents"] == 50
    assert res["steps_simulated"] == 30
    assert res["peak_infected"] >= 1


def test_sim_gillespie_ssa():
    res = GillespieExactSSA.simulate_predator_prey(initial_prey=100, initial_predators=20, max_time=5.0)
    assert res["reactions_fired"] >= 1
    assert res["final_time"] <= 5.1
    assert res["prey_count"] >= 0
    assert res["predator_count"] >= 0


def test_sim_spoken_english():
    code = """use sim
simulate seir epidemic with 40 agents and 20 steps into seir_res
simulate gillespie ssa with 80 prey and 25 predators max time 5.0 into ssa_res
"""
    env = execute(code)
    assert env["seir_res"].total_agents == 40
    assert env["ssa_res"].reactions_fired >= 1


# ==============================================================================
# GEO DOMAIN TESTS
# ==============================================================================

def test_geo_utm():
    # San Francisco: 37.7749 N, -122.4194 W -> UTM zone 10 North
    lat, lon = 37.7749, -122.4194
    fwd = UniversalTransverseMercatorUTM.forward(lat, lon)
    assert fwd["zone"] == 10
    assert fwd["northern"] is True
    assert 500000.0 < fwd["easting"] < 600000.0
    assert 4100000.0 < fwd["northing"] < 4200000.0

    # Invert back to lat/lon
    inv = UniversalTransverseMercatorUTM.inverse(fwd["easting"], fwd["northing"], fwd["zone"], northern=True)
    assert inv["latitude"] == pytest.approx(lat, abs=1e-4)
    assert inv["longitude"] == pytest.approx(lon, abs=1e-4)


def test_geo_geohash():
    lat, lon = 37.7749, -122.4194
    gh = GeohashSpatialEncoder.encode(lat, lon, precision=7)
    assert len(gh) == 7
    assert gh.startswith("9q8")

    dec = GeohashSpatialEncoder.decode(gh)
    assert dec["latitude"] == pytest.approx(lat, abs=0.01)
    assert dec["longitude"] == pytest.approx(lon, abs=0.01)


def test_geo_spoken_english():
    code = """use geo
project utm coordinates lat 37.7749 lon -122.4194 into utm_fwd
invert utm coordinates easting 551163.0 northing 4181050.0 zone 10 northern True into utm_inv
encode spatial geohash lat 37.7749 lon -122.4194 precision 7 into gh_code
decode spatial geohash gh_code into gh_dec
"""
    env = execute(code)
    assert env["utm_fwd"].zone == 10
    assert env["utm_inv"].latitude == pytest.approx(37.7749, abs=0.01)
    assert len(env["gh_code"]) == 7
    assert env["gh_dec"].latitude == pytest.approx(37.7749, abs=0.01)
