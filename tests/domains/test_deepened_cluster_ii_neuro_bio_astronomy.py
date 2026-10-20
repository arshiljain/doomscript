"""Integration and verification test suite for Deepened Cluster II:
Neuroscience, Bioinformatics, and Astronomy domains in DoomScript.

Validates pure Python algorithms and native spoken-English .doom code execution.
"""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# NEUROSCIENCE DOMAIN DEEPENED TESTS
# ==============================================================================

def test_neuro_hodgkin_huxley_simulation():
    """Validates 4-variable Hodgkin-Huxley biophysical action potential dynamics."""
    code = """
use neuro
simulate hodgkin huxley with current 10.0 duration 50.0 into hh_res
assert hh_res's spike_count is at least 1
assert hh_res's v_max is over 20.0
assert hh_res's duration_ms equals 50.0
"""
    env = execute(code)
    hh = env["hh_res"]
    assert hh.spike_count >= 1
    assert hh.v_max > 20.0


def test_neuro_wilson_cowan_population():
    """Validates coupled Excitatory-Inhibitory population limit cycle dynamics."""
    code = """
use neuro
simulate wilson cowan with p_ext 1.2 duration 60.0 into wc_res
assert wc_res's steps is at least 500
assert wc_res's final_e is over 0.0
assert wc_res's final_i is over 0.0
"""
    env = execute(code)
    wc = env["wc_res"]
    assert wc.steps >= 500
    assert wc.final_e > 0.0
    assert wc.final_i > 0.0


def test_neuro_eeg_bandpower_analysis():
    """Validates EEG spectral decomposition into Delta/Theta/Alpha/Beta/Gamma bands."""
    code = """
use neuro
set eeg_signal to [0.5, 1.2, 0.8, -0.4, -1.1, -0.6, 0.2, 1.0, 1.4, 0.7, -0.3, -0.9, -1.2, -0.5, 0.3, 1.1]
analyze eeg bands in eeg_signal with sample rate 250 into eeg_res
assert eeg_res's total_power is over 0.0
assert eeg_res's alpha_power is at least 0.0
assert eeg_res's theta_power is at least 0.0
"""
    env = execute(code)
    res = env["eeg_res"]
    assert res.total_power > 0.0


def test_neuro_psth_analysis():
    """Validates Peristimulus Time Histogram and time-resolved firing rate estimation."""
    code = """
use neuro
set trials to [[12.0, 45.0, 88.0], [15.0, 42.0, 91.0], [10.0, 48.0, 85.0]]
compute psth for trials trials duration 100.0 with bin width 20.0 into psth_res
assert psth_res's total_spikes equals 9
assert psth_res's mean_rate_hz is over 0.0
"""
    env = execute(code)
    psth = env["psth_res"]
    assert psth.total_spikes == 9
    assert psth.mean_rate_hz > 0.0


# ==============================================================================
# BIOINFORMATICS DOMAIN DEEPENED TESTS
# ==============================================================================

def test_bio_nussinov_rna_folding():
    """Validates Nussinov RNA secondary structure dynamic programming."""
    code = """
use bio
predict rna structure of "GCGCGAAGCG" with min loop 2 into fold_res
assert fold_res's pair_count is at least 2
assert fold_res's dot_bracket is not ""
assert fold_res's gc_pairs is at least 2
"""
    env = execute(code)
    fold = env["fold_res"]
    assert fold.pair_count >= 2
    assert "(" in fold.dot_bracket and ")" in fold.dot_bracket


def test_bio_restriction_enzyme_digestion():
    """Validates restriction endonuclease site recognition and gel migration."""
    code = """
use bio
set dna to "ATGCGAGAATTCCTAGGATCCGAT"
digest dna dna with enzyme "EcoRI" into digest_res
assert digest_res's enzyme equals "ECORI"
assert digest_res's fragment_count equals 2
assert length of digest_res's cut_positions equals 1
"""
    env = execute(code)
    res = env["digest_res"]
    assert res.enzyme == "ECORI"
    assert res.fragment_count == 2
    assert len(res.cut_positions) == 1


def test_bio_codon_adaptation_index():
    """Validates Codon Adaptation Index (CAI) calculation against E. coli weights."""
    code = """
use bio
set coding_seq to "ATGGCTAAACTGACCGGTTTC"
calculate cai of coding_seq into cai_res
assert cai_res's cai is over 0.5
assert cai_res's codon_count equals 7
assert cai_res's gc3_percent is at least 0.0
"""
    env = execute(code)
    res = env["cai_res"]
    assert res.cai > 0.5
    assert res.codon_count == 7


# ==============================================================================
# ASTRONOMY DOMAIN DEEPENED TESTS
# ==============================================================================

def test_astronomy_symplectic_n_body():
    """Validates symplectic Leapfrog N-body gravitational integrator."""
    code = """
use astronomy
set body1 to {"name": "star", "mass": 1.0e30, "x": 0.0, "y": 0.0, "z": 0.0, "vx": 0.0, "vy": 0.0, "vz": 0.0}
set body2 to {"name": "planet", "mass": 5.0e24, "x": 1.5e11, "y": 0.0, "z": 0.0, "vx": 0.0, "vy": 29780.0, "vz": 0.0}
set bodies to [body1, body2]
simulate n body system with bodies bodies duration 3600.0 with dt 60.0 into nbody_res
assert nbody_res's conserved is true
assert nbody_res's duration_sec equals 3600.0
assert nbody_res's steps equals 60
"""
    env = execute(code)
    res = env["nbody_res"]
    assert res.conserved is True
    assert res.steps == 60


def test_astronomy_orbital_transfers():
    """Validates Hohmann and Bi-elliptic orbital transfer mechanics."""
    code = """
use astronomy
calculate hohmann transfer from 6.678e6 to 4.2164e7 into hoh_res
assert hoh_res's total_delta_v_mps is over 3500.0
assert hoh_res's transfer_time_hours is over 5.0

calculate bi-elliptic transfer from 6.678e6 to 4.2164e7 via 1.0e8 into bi_res
assert bi_res's total_delta_v_mps is over 3000.0
assert bi_res's total_time_hours is over 10.0
"""
    env = execute(code)
    hoh = env["hoh_res"]
    bi = env["bi_res"]
    assert hoh.total_delta_v_mps > 3500.0
    assert bi.total_delta_v_mps > 3000.0


def test_astronomy_precession_and_rise_set():
    """Validates IAU Precession and Celestial Rise/Set ephemeris."""
    code = """
use astronomy
precess coordinates ra 83.633 dec 22.0145 to date 2459000.5 into prec_res
assert prec_res's ra_deg is over 80.0
assert prec_res's dec_deg is over 20.0

calculate celestial rise and set for ra 83.633 dec 22.0145 at lat 34.05 lon -118.25 on 2459000.5 into rs_res
assert rs_res's status equals "rises_and_sets"
assert rs_res's transit_ut_hour is at least 0.0
assert rs_res's rise_ut_hour is at least 0.0
assert rs_res's set_ut_hour is at least 0.0
"""
    env = execute(code)
    prec = env["prec_res"]
    rs = env["rs_res"]
    assert prec.ra_deg > 80.0
    assert rs.status == "rises_and_sets"
