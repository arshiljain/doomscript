"""Integration and verification test suite for Deepened Cluster IV:
Automata, Compiler, Symbolic Math, and Time Series domains in DoomScript.

Validates pure Python algorithms and native spoken-English .doom code execution.
"""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# AUTOMATA TESTS
# ==============================================================================

def test_automata_cellular_automata_1d():
    """Validates Wolfram Rule 30 chaotic cellular automaton evolution."""
    code = """
use automata
simulate cellular rule 30 with width 31 with generations 15 into ca_res
assert ca_res's rule equals 30
assert ca_res's final_active_count is over 0
assert ca_res's entropy is over 0.0
assert ca_res's generations equals 15
"""
    env = execute(code)
    ca = env["ca_res"]
    assert ca.rule == 30
    assert ca.final_active_count > 0
    assert ca.entropy > 0.0


def test_automata_conway_game_of_life_oscillator():
    """Validates Conway's Game of Life period-2 Blinker oscillator detection."""
    code = """
use automata
set blinker to [[2, 1], [2, 2], [2, 3]]
simulate game of life with rows 6 cols 6 live blinker with steps 6 into gol_res
assert gol_res's is_oscillating is true
assert gol_res's period equals 2
assert gol_res's rows equals 6
"""
    env = execute(code)
    gol = env["gol_res"]
    assert gol.is_oscillating is True
    assert gol.period == 2


# ==============================================================================
# COMPILER OPTIMIZATION TESTS
# ==============================================================================

def test_compiler_dce_and_constant_folding():
    """Validates Sparse Constant Folding and Dead Code Elimination pass."""
    code = """
use compiler
set insts to [
    {"op": "+", "target": "t0", "arg1": 10, "arg2": 20},
    {"op": "*", "target": "t1", "arg1": "t0", "arg2": 0},
    {"op": "+", "target": "dead_var", "arg1": 99, "arg2": 1},
    {"op": "return", "value": "t1"}
]
optimize instructions insts with dce and constant folding into opt_res
assert opt_res's constants_folded is at least 1
assert opt_res's dead_instructions_eliminated is at least 1
assert opt_res's instruction_count is at most 2
"""
    env = execute(code)
    opt = env["opt_res"]
    assert opt.constants_folded >= 1
    assert opt.dead_instructions_eliminated >= 1
    assert opt.instruction_count <= 2


def test_compiler_dominator_tree_and_loops():
    """Validates Control Flow Graph Dominator Tree and natural loop detection."""
    code = """
use compiler
set nodes to ["B0", "B1", "B2", "B3"]
set edges to [["B0", "B1"], ["B1", "B2"], ["B2", "B1"], ["B2", "B3"]]
build dominator tree with entry "B0" nodes nodes edges edges into dom_res
assert dom_res's entry equals "B0"
assert length of dom_res's natural_loops is at least 1
"""
    env = execute(code)
    dom = env["dom_res"]
    assert dom.entry == "B0"
    assert len(dom.natural_loops) >= 1
    assert dom.natural_loops[0]["header"] == "B1"


# ==============================================================================
# SYMBOLIC MATHEMATICS TESTS
# ==============================================================================

def test_symbolic_polynomial_gcd_and_roots():
    """Validates Euclidean polynomial GCD and Rational Root Theorem factoring."""
    code = """
use symbolic
calculate polynomial gcd for [1.0, -1.0] and [1.0, -2.0, 1.0] into gcd_res
assert gcd_res equals [1.0, -1.0]

find rational roots for polynomial [1, -6, 11, -6] into roots_res
assert roots_res equals [1.0, 2.0, 3.0]
"""
    env = execute(code)
    assert env["gcd_res"] == [1.0, -1.0]
    assert env["roots_res"] == [1.0, 2.0, 3.0]


def test_symbolic_brent_root_finding():
    """Validates Brent-Dekker hybrid non-linear root solver to high precision."""
    code = """
use symbolic
find root for expression "x**3 - x - 2" bracket 1.0 to 2.0 into brent_res
assert brent_res's converged is true
assert brent_res's root is over 1.5
assert brent_res's root is under 1.6
assert brent_res's iterations is at least 1
"""
    env = execute(code)
    brent = env["brent_res"]
    assert brent.converged is True
    assert 1.5 < brent.root < 1.6


# ==============================================================================
# TIME SERIES TESTS
# ==============================================================================

def test_timeseries_holt_winters_forecasting():
    """Validates Holt-Winters triple exponential smoothing multi-step forecasts."""
    code = """
use time_series
set quarterly_data to [10.0, 15.0, 20.0, 25.0, 12.0, 18.0, 24.0, 30.0, 15.0, 22.0, 28.0, 36.0]
forecast holt winters on quarterly_data with period 4 with steps 4 into hw_res
assert length of hw_res's forecasts equals 4
assert hw_res's rmse is at least 0.0
assert hw_res's final_level is over 0.0
"""
    env = execute(code)
    hw = env["hw_res"]
    assert len(hw.forecasts) == 4
    assert hw.rmse >= 0.0
    assert hw.final_level > 0.0


def test_timeseries_autoregressive_ar_model():
    """Validates Yule-Walker AR(p) model estimation and trajectory forecasting."""
    code = """
use time_series
set ar_data to [1.2, 1.5, 1.9, 2.4, 3.1, 3.9, 4.8, 5.9, 7.1, 8.4, 9.9, 11.5, 13.2]
forecast ar model on ar_data with order 2 with steps 3 into ar_res
assert length of ar_res's forecasts equals 3
assert ar_res's noise_variance is over 0.0
assert ar_res's order_p equals 2
"""
    env = execute(code)
    ar = env["ar_res"]
    assert len(ar.forecasts) == 3
    assert ar.noise_variance > 0.0
    assert ar.order_p == 2
