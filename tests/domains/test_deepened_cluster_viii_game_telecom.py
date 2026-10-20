"""Tests for Deepened Cluster VIII: Game Mechanics & Telecommunications Domains."""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# GAME MECHANICS DEEPENED TESTS
# ==============================================================================

def test_game_minimax_search():
    """Validates adversarial alpha-beta minimax search in DoomScript."""
    code = """
use game
set state to {"legal_moves": [1, 2, 3], "score": 10.5}
search best move in state state with depth 3 using minimax into res
assert res's best_move equals 1
assert res's best_score equals 10.5
assert res's depth_reached equals 3
assert res's nodes_evaluated is greater than 0
"""
    env = execute(code)
    assert env["res"]["best_move"] == 1
    assert env["res"]["depth_reached"] == 3


def test_game_jump_point_search():
    """Validates Jump Point Search (JPS) pathfinding on 2D uniform grid."""
    code = """
use game
set grid to [
    [0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0],
    [0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0],
    [0, 0, 0, 0, 0]
]
set start_pos to [0, 0]
set goal_pos to [4, 4]
find jump point path in grid from start_pos to goal_pos into res
assert res's found is true
assert res's path_length is greater than 0
assert res's total_cost is greater than 0.0
"""
    env = execute(code)
    assert env["res"]["found"] is True
    assert env["res"]["path_length"] > 0
    assert len(env["res"]["jump_points"]) > 0


def test_game_boids_flocking():
    """Validates Craig Reynolds Boids flocking steering behavior simulation."""
    code = """
use game
set boids to [
    {"x": 10.0, "y": 10.0, "vx": 1.0, "vy": 0.5},
    {"x": 12.0, "y": 11.0, "vx": 0.8, "vy": 0.6},
    {"x": 15.0, "y": 15.0, "vx": 1.2, "vy": 0.4},
    {"x": 50.0, "y": 50.0, "vx": -1.0, "vy": 0.0}
]
simulate flock boids for 5 steps into res
assert res's count equals 4
assert res's steps_completed equals 5
assert res's mean_speed is greater than 0.0
"""
    env = execute(code)
    assert env["res"]["count"] == 4
    assert env["res"]["steps_completed"] == 5


def test_game_mcts_search():
    """Validates Monte Carlo Tree Search (MCTS) with UCT policy."""
    code = """
use game
set game_st to {"moves": [1, 2, 3], "history": []}
run mcts on state game_st with iterations 50 into res
assert res's total_simulations equals 50
assert res's visit_count is greater than 0
"""
    env = execute(code)
    assert env["res"]["total_simulations"] == 50
    assert env["res"]["best_move"] in [1, 2, 3]


# ==============================================================================
# TELECOM DEEPENED TESTS
# ==============================================================================

def test_telecom_secded_clean_transmission():
    """Validates error-free transmission and recovery via Hamming(8,4) SECDED."""
    code = """
use telecom
set original_bits to [1, 0, 1, 1]
encode bits original_bits with secded into codeword
assert len(codeword) equals 8
decode bits codeword with secded into result
assert result's success is true
assert result's single_error_count equals 0
assert result's double_error_count equals 0
assert result's data[0] equals 1
assert result's data[1] equals 0
assert result's data[2] equals 1
assert result's data[3] equals 1
"""
    env = execute(code)
    assert env["result"]["data"] == [1, 0, 1, 1]
    assert env["result"]["success"] is True


def test_telecom_secded_single_error_correction():
    """Validates detection and correction of single-bit error in SECDED."""
    code = """
use telecom
set original_bits to [0, 1, 1, 0]
encode bits original_bits with secded into codeword
set corrupted to codeword
set corrupted[2] to 1 - corrupted[2]
decode bits corrupted with secded into result
assert result's success is true
assert result's single_error_count equals 1
assert result's data[0] equals 0
assert result's data[1] equals 1
assert result's data[2] equals 1
assert result's data[3] equals 0
"""
    env = execute(code)
    assert env["result"]["data"] == [0, 1, 1, 0]
    assert env["result"]["single_error_count"] == 1


def test_telecom_qam_modulation_loop():
    """Validates QPSK / 16-QAM constellation modulation and symbol slicing."""
    code = """
use telecom
set raw_bits to [1, 0, 0, 1, 1, 1, 0, 0]
modulate bits raw_bits with "QPSK" into symbols
assert symbols's count equals 4
demodulate symbols symbols with "QPSK" into recovered
assert recovered[0] equals 1
assert recovered[1] equals 0
assert recovered[2] equals 0
assert recovered[3] equals 1
"""
    env = execute(code)
    assert len(env["symbols"]) == 4
    assert env["recovered"][:4] == [1, 0, 0, 1]


def test_telecom_awgn_simulation():
    """Validates AWGN channel simulation with SNR, BER, and EVM metrics."""
    code = """
use telecom
set test_stream to [1, 0, 1, 1, 0, 0, 1, 0]
simulate awgn on bits test_stream with scheme "QPSK" and snr 30.0 into sim_res
assert sim_res's original_bits_count equals 8
assert sim_res's ber equals 0.0
assert sim_res's transmitted_symbols equals 4
"""
    env = execute(code)
    assert env["sim_res"]["original_bits_count"] == 8
    assert env["sim_res"]["ber"] == 0.0


def test_telecom_custom_crc():
    """Validates parameterized CRC calculation with custom polynomial."""
    code = """
use telecom
compute custom crc of "DoomScript Protocol" with polynomial 79764919 into crc_res
assert crc_res's bytes_processed equals 19
assert crc_res's width equals 32
"""
    env = execute(code)
    assert env["crc_res"]["bytes_processed"] == 19
    assert env["crc_res"]["width"] == 32
