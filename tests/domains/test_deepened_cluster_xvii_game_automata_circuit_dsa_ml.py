"""Comprehensive test suite for Cluster XVII deepened engines (Game, Automata, Circuit, DSA, ML).

Validates pure Python runtime engines and end-to-end spoken English .doom scripts.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Import runtime classes & functions
from doomscript.domains.game.runtime import (
    HexagonalGridCoordinates,
    HierarchicalFiniteStateMachineHFSM,
    game_hex_distance,
    game_hex_line,
    game_hex_range,
    game_hfsm_create,
    game_hfsm_trigger,
)
from doomscript.domains.automata.runtime import (
    HopcroftDFAMinimizer,
    MarkovDecisionProcessValueIteration,
    automata_hopcroft_minimize,
    automata_mdp_value_iteration,
)
from doomscript.domains.circuit.runtime import (
    QuineMcCluskeyBooleanMinimizer,
    SmallSignalDiodeBJTAnalyzer,
    circuit_quine_mccluskey_minimize,
    circuit_bjt_operating_point,
)
from doomscript.domains.dsa.runtime import (
    VanEmdeBoasTreeVEB,
    HeavyLightDecompositionHLD,
    dsa_veb_tree_ops,
    dsa_hld_tree,
    dsa_hld_query_path,
    dsa_hld_update_node,
)
from doomscript.domains.ml.runtime import (
    IsolationForestAnomalyDetector,
    DBSCANClusteringEngine,
    ml_isolation_forest,
    ml_dbscan,
)


# ==============================================================================
# GAME DOMAIN TESTS
# ==============================================================================

def test_game_hex_coordinates():
    # Distance in axial coordinates
    assert HexagonalGridCoordinates.distance(0, 0, 2, -2) == 2
    assert HexagonalGridCoordinates.distance(0, 0, 0, 3) == 3

    # Line drawing
    line = HexagonalGridCoordinates.line_draw(0, 0, 3, 0)
    assert len(line) == 4
    assert line[0] == (0, 0)
    assert line[-1] == (3, 0)

    # Range query: radius 2 on hex grid has 1 + 6 + 12 = 19 hexes
    cells = HexagonalGridCoordinates.range_query(0, 0, 2)
    assert len(cells) == 19


def test_game_hfsm():
    states_def = {
        "Combat": {"initial_substate": "Melee"},
        "Melee": {"parent": "Combat"},
        "Ranged": {"parent": "Combat"},
        "Flee": {},
    }
    transitions = [
        {"from": "Melee", "to": "Ranged", "event": "distance_gained"},
        {"from": "Combat", "to": "Flee", "event": "low_health"},
    ]
    hfsm = HierarchicalFiniteStateMachineHFSM("Melee", states_def, transitions)
    assert hfsm.current_leaf_state == "Melee"
    assert "Combat" in hfsm.active_chain

    # Event matching parent state 'Combat' transitions from Melee to Flee
    res = hfsm.trigger_event("low_health")
    assert res["transition_fired"] is True
    assert hfsm.current_leaf_state == "Flee"
    assert hfsm.active_chain == ["Flee"]


def test_game_spoken_english():
    code = """use game
calculate hex distance from q 0 r 0 to q 2 r -2 into hex_dist
draw hex line from q 0 r 0 to q 2 r 0 into hex_line
set hfsm_states to {"Combat": {"initial_substate": "Melee"}, "Melee": {"parent": "Combat"}, "Flee": {}}
set hfsm_trans to [{"from": "Combat", "to": "Flee", "event": "flee_event"}]
create hfsm initial "Melee" states hfsm_states transitions hfsm_trans into hfsm_mach
trigger hfsm event "flee_event" on hfsm_mach into hfsm_res
"""
    env = execute(code)
    assert env["hex_dist"] == 2
    assert len(env["hex_line"]) == 3
    assert env["hfsm_res"].current_state == "Flee"


# ==============================================================================
# AUTOMATA DOMAIN TESTS
# ==============================================================================

def test_automata_hopcroft():
    # DFA with 5 states, some equivalent
    states = ["A", "B", "C", "D", "E"]
    alphabet = ["0", "1"]
    q0 = "A"
    accept = ["C", "E"]
    transitions = {
        "A": {"0": "B", "1": "A"},
        "B": {"0": "B", "1": "C"},
        "C": {"0": "D", "1": "A"},
        "D": {"0": "B", "1": "E"},
        "E": {"0": "D", "1": "A"},
    }
    res = HopcroftDFAMinimizer.minimize(states, alphabet, q0, accept, transitions)
    assert res["minimal_states_count"] <= res["original_states_count"]
    assert res["minimal_states_count"] == 3


def test_automata_mdp_value_iteration():
    states = ["S0", "S1"]
    actions = ["a0", "a1"]
    transitions = {
        "S0": {"a0": {"S0": 1.0}, "a1": {"S1": 1.0}},
        "S1": {"a0": {"S0": 1.0}, "a1": {"S1": 1.0}},
    }
    rewards = {
        "S0": {"a0": 0.0, "a1": 1.0},
        "S1": {"a0": 0.0, "a1": 10.0},
    }
    res = MarkovDecisionProcessValueIteration.solve(states, actions, transitions, rewards, gamma=0.9)
    assert res["converged"] is True
    assert res["state_values"]["S1"] > res["state_values"]["S0"]
    assert res["optimal_policy"]["S0"] == "a1"
    assert res["optimal_policy"]["S1"] == "a1"


def test_automata_spoken_english():
    code = """use automata
set dfa_states to ["A", "B", "C", "D", "E"]
set dfa_alpha to ["0", "1"]
set dfa_trans to {"A": {"0": "B", "1": "A"}, "B": {"0": "B", "1": "C"}, "C": {"0": "D", "1": "A"}, "D": {"0": "B", "1": "E"}, "E": {"0": "D", "1": "A"}}
minimize hopcroft dfa states dfa_states alphabet dfa_alpha initial "A" accept ["C", "E"] transitions dfa_trans into hop_res
set mdp_states to ["S0", "S1"]
set mdp_acts to ["a0", "a1"]
set mdp_trans to {"S0": {"a0": {"S0": 1.0}, "a1": {"S1": 1.0}}, "S1": {"a0": {"S0": 1.0}, "a1": {"S1": 1.0}}}
set mdp_rew to {"S0": {"a0": 0.0, "a1": 1.0}, "S1": {"a0": 0.0, "a1": 10.0}}
solve mdp states mdp_states actions mdp_acts transitions mdp_trans rewards mdp_rew gamma 0.9 into mdp_res
"""
    env = execute(code)
    assert env["hop_res"].minimal_states_count == 3
    assert env["mdp_res"].converged is True


# ==============================================================================
# CIRCUIT DOMAIN TESTS
# ==============================================================================

def test_circuit_quine_mccluskey():
    # 3-variable Boolean function: m(0, 1, 2, 5, 6, 7)
    minterms = [0, 1, 2, 5, 6, 7]
    res = QuineMcCluskeyBooleanMinimizer.minimize(minterms, num_vars=3)
    assert res["terms_count"] > 0
    assert len(res["prime_implicants"]) > 0
    assert "+" in res["minimal_sop"] or len(res["minimal_sop"]) > 0


def test_circuit_bjt_operating_point():
    # Active mode BJT: Vcc=10V, Rb=200k, Rc=1k, Beta=100
    res = SmallSignalDiodeBJTAnalyzer.analyze_common_emitter(vcc=10.0, rb_kohm=200.0, rc_kohm=1.0, beta=100.0)
    assert res["operating_region"] == "Forward-Active"
    assert res["i_b_ua"] > 0.0
    assert res["i_c_ma"] > 0.0
    assert 0.2 < res["v_ce"] < 10.0
    assert res["voltage_gain"] < 0.0  # Inverting common-emitter gain


def test_circuit_spoken_english():
    code = """use circuit
minimize boolean function minterms [0, 1, 2, 5, 6, 7] variables 3 into qm_res
calculate bjt q point vcc 10.0 rb 200.0 rc 1.0 beta 100.0 into bjt_res
"""
    env = execute(code)
    assert env["qm_res"].terms_count > 0
    assert env["bjt_res"].operating_region == "Forward-Active"


# ==============================================================================
# DSA DOMAIN TESTS
# ==============================================================================

def test_dsa_veb_tree():
    veb = VanEmdeBoasTreeVEB(16)
    veb.insert(2)
    veb.insert(3)
    veb.insert(7)
    veb.insert(14)
    assert veb.contains(3) is True
    assert veb.contains(5) is False
    assert veb.successor(3) == 7
    assert veb.successor(7) == 14
    assert veb.min_val == 2
    assert veb.max_val == 14

    veb.delete(7)
    assert veb.contains(7) is False
    assert veb.successor(3) == 14


def test_dsa_heavy_light_decomposition():
    # Tree:
    #       0 (val=10)
    #      / \
    # (20)1   2(5)
    #    / \
    #(30)3 4(15)
    edges = [(0, 1), (0, 2), (1, 3), (1, 4)]
    values = [10.0, 20.0, 5.0, 30.0, 15.0]
    hld = HeavyLightDecompositionHLD(5, edges, values=values)
    # Path from 3 to 2: 3 -> 1 -> 0 -> 2. Values: 30, 20, 10, 5. Max = 30
    assert hld.query_path_max(3, 2) == 30.0
    # Update node 0 to 50
    hld.update_node(0, 50.0)
    assert hld.query_path_max(3, 2) == 50.0


def test_dsa_spoken_english():
    code = """use dsa
set veb_ops to [{"op": "insert", "val": 2}, {"op": "insert", "val": 7}, {"op": "successor", "val": 2}]
execute veb tree operations veb_ops with universe 16 into veb_res
set hld_edges to [[0, 1], [0, 2], [1, 3], [1, 4]]
set hld_vals to [10.0, 20.0, 5.0, 30.0, 15.0]
create hld tree nodes 5 edges hld_edges values hld_vals into hld_tree
query hld path from 3 to 2 in hld_tree into hld_query
"""
    env = execute(code)
    assert env["veb_res"].query_results[0] == 7
    assert env["hld_query"] == 30.0


# ==============================================================================
# ML DOMAIN TESTS
# ==============================================================================

def test_ml_isolation_forest():
    # Dense cluster near [0, 0] and single severe outlier at [50, 50]
    normal_pts = [[0.1 * i, 0.1 * (i % 3)] for i in range(20)]
    outlier = [[50.0, 50.0]]
    X = normal_pts + outlier

    iso = IsolationForestAnomalyDetector(n_trees=30, contamination=0.1, seed=42)
    iso.fit(X)
    scores = iso.score_samples(X)
    # Outlier score should be strictly higher than normal points
    assert scores[-1] > max(scores[:15])


def test_ml_dbscan():
    # 2 distinct clusters and 1 noise point
    c1 = [[0.0, 0.0], [0.1, 0.1], [0.1, 0.0], [0.0, 0.1]]
    c2 = [[10.0, 10.0], [10.1, 10.1], [10.0, 10.2], [10.2, 10.0]]
    noise = [[5.0, 5.0]]
    X = c1 + c2 + noise

    res = DBSCANClusteringEngine.fit(X, eps=0.5, min_samples=3)
    assert res["num_clusters"] == 2
    assert res["labels"][-1] == -1  # Noise


def test_ml_spoken_english():
    code = """use ml
set ml_data to [[0.0, 0.1], [0.1, 0.0], [0.2, 0.2], [0.1, 0.1], [10.0, 10.0]]
detect anomalies using isolation forest on ml_data trees 20 contamination 0.2 into if_res
cluster data using dbscan on ml_data eps 1.0 min samples 2 into db_res
"""
    env = execute(code)
    assert env["if_res"].num_trees == 20
    assert env["db_res"].num_clusters >= 1
