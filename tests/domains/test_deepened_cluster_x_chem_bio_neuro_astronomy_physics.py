"""Tests for Deepened Cluster X: Chemistry, Biology, Neuroscience, Astronomy & Physics Domains."""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# CHEMISTRY TESTS
# ==============================================================================

def test_chem_gibbs_free_energy():
    """Validates reaction Gibbs free energy and spontaneity."""
    code = """
use chem
calculate gibbs free energy with delta h -100.0 and delta s -200.0 at temperature 25.0 into g_res
assert g_res's is_spontaneous is true
assert g_res's delta_g_kj is less than 0.0
assert g_res's temperature_k equals 298.15
"""
    env = execute(code)
    assert env["g_res"]["is_spontaneous"] is True
    assert env["g_res"]["delta_g_kj"] < 0.0


def test_chem_acid_base_ph():
    """Validates weak acid dissociation pH calculation."""
    code = """
use chem
calculate ph of weak acid 0.1 with ka 0.000018 into ph_res
assert ph_res's pH is greater than 2.0
assert ph_res's pH is less than 3.5
assert ph_res's dissociation_fraction is greater than 0.0
"""
    env = execute(code)
    assert 2.0 < env["ph_res"]["pH"] < 3.5


def test_chem_enzyme_kinetics():
    """Validates Michaelis-Menten V_max and K_m estimation via Lineweaver-Burk."""
    code = """
use chem
set s_vals to [1.0, 2.0, 5.0, 10.0]
set v_vals to [0.5, 0.8, 1.4, 1.8]
calculate enzyme kinetics for substrates s_vals and rates v_vals into enz_res
assert enz_res's v_max is greater than 1.5
assert enz_res's k_m is greater than 0.5
assert enz_res's data_points equals 4
"""
    env = execute(code)
    assert env["enz_res"]["v_max"] > 1.5
    assert env["enz_res"]["data_points"] == 4


# ==============================================================================
# BIOLOGY TESTS
# ==============================================================================

def test_bio_upgma_tree():
    """Validates UPGMA phylogenetic tree Newick format construction."""
    code = """
use bio
set dists to [
    [0.0, 2.0, 4.0],
    [2.0, 0.0, 4.0],
    [4.0, 4.0, 0.0]
]
set taxa to ["A", "B", "C"]
build upgma tree from distances dists and taxa taxa into tree_res
assert tree_res's taxa_count equals 3
assert tree_res's tree_height equals 2.0
"""
    env = execute(code)
    assert env["tree_res"]["taxa_count"] == 3
    assert env["tree_res"]["tree_height"] == 2.0
    assert "A" in env["tree_res"]["newick"]


def test_bio_bwt_transform_and_count():
    """Validates Burrows-Wheeler Transform and backward FM-index occurrence search."""
    code = """
use bio
compute bwt of sequence "BANANA" into bwt_res
assert bwt_res's original_length equals 6
count occurrences of "ANA" in bwt bwt_res's bwt into cnt_res
assert cnt_res's found is true
assert cnt_res's occurrences_count equals 2
"""
    env = execute(code)
    assert env["cnt_res"]["occurrences_count"] == 2
    assert env["cnt_res"]["found"] is True


def test_bio_cpg_islands():
    """Validates genomic CpG island detection."""
    code = """
use bio
set dna to "CGCGCGCGCGCGCGCGCGCGATATATAT"
find cpg islands in sequence dna into cpg_res
assert cpg_res's sequence_length equals 28
assert cpg_res's island_count is greater than 0
"""
    env = execute(code)
    assert env["cpg_res"]["island_count"] > 0


# ==============================================================================
# NEUROSCIENCE TESTS
# ==============================================================================

def test_neuro_fitzhugh_nagumo():
    """Validates 2D FitzHugh-Nagumo excitable neural action potential generation."""
    code = """
use neuro
simulate fitzhugh nagumo with current 0.6 duration 100.0 into fhn_res
assert fhn_res's duration_ms equals 100.0
assert fhn_res's spike_count is greater than 0
"""
    env = execute(code)
    assert env["fhn_res"]["spike_count"] > 0


def test_neuro_spike_cross_correlation():
    """Validates spike train cross-correlogram latency estimation."""
    code = """
use neuro
set t1 to [10.0, 20.0, 30.0, 40.0]
set t2 to [12.0, 22.0, 32.0, 42.0]
correlate spike trains t1 and t2 max lag 10.0 into xcorr_res
assert xcorr_res's total_coincidences equals 7
assert xcorr_res's peak_lag_ms equals 2.0
"""
    env = execute(code)
    assert env["xcorr_res"]["total_coincidences"] == 7
    assert env["xcorr_res"]["peak_lag_ms"] == 2.0


# ==============================================================================
# ASTRONOMY TESTS
# ==============================================================================

def test_astronomy_lambert_solve():
    """Validates Lambert's orbital boundary value problem solution."""
    code = """
use astronomy
set r1 to [149600000.0, 0.0, 0.0]
set r2 to [0.0, 227900000.0, 0.0]
solve lambert transfer from r1 to r2 with tof 17280000.0 into lamb_res
assert lamb_res's semi_major_axis_km is greater than 100000.0
assert lamb_res's chord_km is greater than 100000.0
"""
    env = execute(code)
    assert env["lamb_res"]["semi_major_axis_km"] > 100000.0


def test_astronomy_lagrange_points():
    """Validates Circular Restricted Three-Body Problem (CR3BP) Lagrange points."""
    code = """
use astronomy
calculate lagrange points for mass1 1.989e30 and mass2 5.972e24 at distance 149600000.0 into lag_res
assert lag_res's hill_radius_km is greater than 1000000.0
assert lag_res's mass_ratio is less than 0.001
"""
    env = execute(code)
    assert env["lag_res"]["hill_radius_km"] > 1000000.0


# ==============================================================================
# PHYSICS TESTS
# ==============================================================================

def test_physics_biot_savart_field():
    """Validates Biot-Savart magnetic field from circular current loop."""
    code = """
use physics
calculate biot savart field for current 10.0 and radius 0.1 at distance 0.05 into b_res
assert b_res's B_tesla is greater than 0.0
assert b_res's B_gauss is greater than 0.0
"""
    env = execute(code)
    assert env["b_res"]["B_tesla"] > 0.0


def test_physics_carnot_cycle():
    """Validates Carnot heat engine thermal efficiency and net work output."""
    code = """
use physics
calculate carnot efficiency for thot 500.0 and tcold 300.0 with heat 1000.0 into carnot_res
assert carnot_res's thermal_efficiency equals 0.4
assert carnot_res's net_work_kj equals 400.0
assert carnot_res's heat_rejected_kj equals 600.0
"""
    env = execute(code)
    assert env["carnot_res"]["thermal_efficiency"] == 0.4
    assert env["carnot_res"]["net_work_kj"] == 400.0


def test_physics_lorentz_factor():
    """Validates relativistic Lorentz factor gamma calculation."""
    code = """
use physics
calculate lorentz factor for velocity 200000000.0 into lor_res
assert lor_res's gamma is greater than 1.0
assert lor_res's fraction_speed_of_light is greater than 0.5
"""
    env = execute(code)
    assert env["lor_res"]["gamma"] > 1.0
    assert env["lor_res"]["fraction_speed_of_light"] > 0.5
