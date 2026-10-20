"""Tests for Deepened Cluster XI Domains: Circuit, Automata, Compiler, Symbolic, Time Series.

Validates pure Python algorithms and native spoken-English DoomScript integration.
"""

import math
from doomscript.compiler.engine import execute


def test_circuit_sallen_key_filter():
    code = """
use circuit
design sallen key filter type "lowpass" cutoff 1000.0 with q 0.7071 with gain 1.0 into sk
assert sk's filter_type == "lowpass"
assert sk's target_cutoff_hz == 1000.0
assert sk's actual_cutoff_hz is greater than 800.0
assert sk's actual_cutoff_hz is less than 1200.0
assert sk's r1_e24_ohms is greater than 0.0
assert sk's r2_e24_ohms is greater than 0.0
"""
    env = execute(code)
    sk = env.get("sk")
    assert sk["filter_type"] == "lowpass"
    assert sk["target_cutoff_hz"] == 1000.0
    assert sk["actual_cutoff_hz"] > 800.0


def test_circuit_rlc_laplace_transient():
    code = """
use circuit
solve rlc laplace transient topology "series" r 100.0 l 0.1 c 0.000001 with v_step 5.0 with duration 0.01 into rlc
assert rlc's topology == "series"
assert rlc's v_step == 5.0
assert rlc's damping_factor_alpha == 500.0
assert rlc's samples_count == 50
assert rlc's regime == "underdamped"
assert rlc's peak_time is greater than 0.0
"""
    env = execute(code)
    rlc = env.get("rlc")
    assert rlc["regime"] == "underdamped"
    assert rlc["damping_factor_alpha"] == 500.0
    assert rlc["samples_count"] == 50


def test_automata_multitape_turing_machine():
    code = """
use automata
simulate multitape turing machine with tapes ["101", ""] state "q0" accept ["q_accept"] transitions [{"from": "q0", "read": ["1", " "], "to": "q0", "write": ["1", "1"], "move": ["R", "R"]}, {"from": "q0", "read": ["0", " "], "to": "q0", "write": ["0", "0"], "move": ["R", "R"]}, {"from": "q0", "read": [" ", " "], "to": "q_accept", "write": [" ", " "], "move": ["S", "S"]}] with max_steps 20 into tm
assert tm's is_accepted is true
assert tm's num_tapes == 2
assert tm's steps_executed == 4
assert tm's tapes_output[0] == "101"
assert tm's tapes_output[1] == "101"
"""
    env = execute(code)
    tm = env.get("tm")
    assert tm["is_accepted"] is True
    assert tm["tapes_output"][1] == "101"
    assert tm["steps_executed"] == 4


def test_automata_cyk_parsing():
    code = """
use automata
parse cyk grammar {"S": ["AB", "BC"], "A": ["BA", "a"], "B": ["CC", "b"], "C": ["AB", "a"]} start "S" tokens ["b", "a", "a", "b", "a"] into cyk
assert cyk's start_symbol == "S"
assert cyk's is_accepted is true
assert cyk's tokens_count == 5
assert cyk's table_cells_filled is greater than 0
"""
    env = execute(code)
    cyk = env.get("cyk")
    assert cyk["is_accepted"] is True
    assert cyk["tokens_count"] == 5


def test_compiler_ll1_table_generator():
    code = """
use compiler
build ll1 parse table start "E" grammar {"E": [["T", "E_prime"]], "E_prime": [["+", "T", "E_prime"], ["ε"]], "T": [["F", "T_prime"]], "T_prime": [["*", "F", "T_prime"], ["ε"]], "F": [["(", "E", ")"], ["id"]]} into ll1
assert ll1's start_symbol == "E"
assert ll1's is_ll1 is true
assert ll1's conflicts_count == 0
"""
    env = execute(code)
    ll1 = env.get("ll1")
    assert ll1["is_ll1"] is True
    assert ll1["conflicts_count"] == 0
    assert "+" in ll1["table"]["E_prime"]


def test_compiler_licm_optimization():
    code = """
use compiler
optimize loop invariants in blocks [{"label": "b0", "instructions": [{"op": "add", "dest": "t1", "args": ["10", "20"]}, {"op": "add", "dest": "t2", "args": ["i", "t1"]}, {"op": "add", "dest": "i", "args": ["i", "1"]}]}] header "b0" body ["b0"] into licm
assert licm's loop_header == "b0"
assert licm's hoisted_instructions_count == 1
assert licm's invariant_variables[0] == "t1"
"""
    env = execute(code)
    licm = env.get("licm")
    assert licm["hoisted_instructions_count"] == 1
    assert licm["invariant_variables"] == ["t1"]


def test_symbolic_square_free_factorization():
    code = """
use symbolic
factor square free polynomial [-2.0, 5.0, -4.0, 1.0] into sqf
assert sqf's is_square_free is false
assert sqf's factors_count == 2
"""
    env = execute(code)
    sqf = env.get("sqf")
    assert sqf["is_square_free"] is False
    assert sqf["factors_count"] == 2


def test_symbolic_polynomial_resultant():
    code = """
use symbolic
calculate resultant of polynomials [1.0, 0.0, 1.0] and [1.0, 1.0] into res
assert res's p_degree == 2
assert res's q_degree == 1
assert res's has_common_root is false
assert res's resultant == 2.0
"""
    env = execute(code)
    res = env.get("res")
    assert res["resultant"] == 2.0
    assert res["has_common_root"] is False


def test_symbolic_pade_approximant():
    code = """
use symbolic
calculate pade approximant coefficients [1.0, 1.0, 0.5, 0.166667, 0.041667] m 1 n 1 with eval [0.1, 0.2] into pade
assert pade's m_degree == 1
assert pade's n_degree == 1
assert pade's numerator_coeffs[0] == 1.0
assert pade's denominator_coeffs[0] == 1.0
"""
    env = execute(code)
    pade = env.get("pade")
    assert pade["m_degree"] == 1
    assert pade["n_degree"] == 1
    assert abs(pade["numerator_coeffs"][1] - 0.5) < 0.05
    assert abs(pade["denominator_coeffs"][1] - (-0.5)) < 0.05


def test_time_series_sakoe_chiba_dtw():
    code = """
use time_series
calculate sakoe chiba dtw between [1.0, 2.0, 3.0, 4.0, 5.0] and [1.0, 2.0, 3.0, 4.0, 5.0] with window 3 into dtw
assert dtw's alignment_cost == 0.0
assert dtw's path_length == 5
"""
    env = execute(code)
    dtw = env.get("dtw")
    assert dtw["alignment_cost"] == 0.0
    assert dtw["path_length"] == 5


def test_time_series_spectral_periodogram():
    signal = [round(math.sin(2.0 * math.pi * 0.1 * i), 4) for i in range(64)]
    code = f"""
use time_series
calculate spectral periodogram of {signal} with rate 1.0 with window "hann" with peaks 3 into spec
assert spec's sampling_rate == 1.0
assert spec's window_applied == "hann"
assert spec's total_power is greater than 0.0
assert spec's peak_frequencies[0]'s frequency_hz is greater than 0.08
assert spec's peak_frequencies[0]'s frequency_hz is less than 0.12
"""
    env = execute(code)
    spec = env.get("spec")
    assert spec["window_applied"] == "hann"
    assert spec["total_power"] > 0.0
    top_peak = spec["peak_frequencies"][0]
    assert abs(top_peak["frequency_hz"] - 0.1) < 0.02
