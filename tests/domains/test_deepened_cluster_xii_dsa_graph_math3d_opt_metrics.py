"""Tests for Deepened Cluster XII Domains: DSA, Graph, Math3D, Optimization, Metrics.

Validates pure Python algorithms and native spoken-English DoomScript integration.
"""

from doomscript.compiler.engine import execute


def test_dsa_fibonacci_heap():
    code = """
use dsa
execute fibonacci heap operations [{"op": "insert", "key": 10.0, "id": "n1"}, {"op": "insert", "key": 5.0, "id": "n2"}, {"op": "insert", "key": 20.0, "id": "n3"}, {"op": "extract_min"}, {"op": "decrease_key", "id": "n3", "new_key": 2.0}] into fib
assert fib's num_nodes == 2
assert fib's final_min_key == 2.0
assert fib's extracted_count == 1
"""
    env = execute(code)
    fib = env.get("fib")
    assert fib["num_nodes"] == 2
    assert fib["final_min_key"] == 2.0
    assert fib["extracted_count"] == 1


def test_dsa_splay_tree():
    code = """
use dsa
execute splay tree operations [{"op": "insert", "key": 15.0, "val": "apple"}, {"op": "insert", "key": 10.0, "val": "banana"}, {"op": "insert", "key": 25.0, "val": "cherry"}, {"op": "find", "key": 10.0}] into splay
assert splay's tree_size == 3
assert splay's root_key == 10.0
assert splay's total_rotations is greater than 0
assert splay's find_results[0] == "banana"
"""
    env = execute(code)
    splay = env.get("splay")
    assert splay["tree_size"] == 3
    assert splay["root_key"] == 10.0
    assert splay["total_rotations"] > 0
    assert splay["find_results"][0] == "banana"


def test_graph_push_relabel_max_flow():
    code = """
use graph
calculate max flow push relabel nodes ["s", "a", "b", "t"] edges [{"from": "s", "to": "a", "capacity": 10.0}, {"from": "s", "to": "b", "capacity": 5.0}, {"from": "a", "to": "b", "capacity": 15.0}, {"from": "a", "to": "t", "capacity": 10.0}, {"from": "b", "to": "t", "capacity": 10.0}] source "s" sink "t" into pr
assert pr's max_flow == 15.0
assert pr's pushes_count is greater than 0
"""
    env = execute(code)
    pr = env.get("pr")
    assert pr["max_flow"] == 15.0
    assert pr["pushes_count"] > 0


def test_graph_johnson_all_pairs_paths():
    code = """
use graph
calculate johnson all pairs shortest paths nodes ["a", "b", "c"] edges [{"from": "a", "to": "b", "weight": -1.0}, {"from": "b", "to": "c", "weight": 2.0}, {"from": "a", "to": "c", "weight": 4.0}] into j_paths
assert j_paths's has_negative_cycle is false
assert j_paths's distances's a's c == 1.0
"""
    env = execute(code)
    j_paths = env.get("j_paths")
    assert j_paths["has_negative_cycle"] is False
    assert j_paths["distances"]["a"]["c"] == 1.0


def test_math3d_dual_quaternion_transform():
    code = """
use math3d
transform points with dual quaternion translation [1.0, 2.0, 3.0] rotation [1.0, 0.0, 0.0, 0.0] points [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]] into dq
assert dq's points_count == 2
assert dq's transformed_points[0][0] == 1.0
assert dq's transformed_points[0][1] == 2.0
assert dq's transformed_points[0][2] == 3.0
assert dq's transformed_points[1][0] == 2.0
"""
    env = execute(code)
    dq = env.get("dq")
    assert dq["points_count"] == 2
    assert dq["transformed_points"][0] == [1.0, 2.0, 3.0]
    assert dq["transformed_points"][1] == [2.0, 3.0, 4.0]


def test_math3d_dual_quaternion_sclerp():
    code = """
use math3d
interpolate dual quaternions trans1 [0.0, 0.0, 0.0] rot1 [1.0, 0.0, 0.0, 0.0] trans2 [10.0, 20.0, 30.0] rot2 [1.0, 0.0, 0.0, 0.0] at 0.5 into sc
assert sc's interpolated_translation[0] == 5.0
assert sc's interpolated_translation[1] == 10.0
assert sc's interpolated_translation[2] == 15.0
"""
    env = execute(code)
    sc = env.get("sc")
    assert sc["interpolated_translation"] == [5.0, 10.0, 15.0]


def test_opt_particle_swarm_optimize():
    code = """
use opt
optimize particle swarm objective "x[0]**2 + x[1]**2" bounds [[-5.0, 5.0], [-5.0, 5.0]] with particles 25 with iterations 40 into pso
assert pso's best_cost is less than 0.05
assert pso's dimensions == 2
"""
    env = execute(code)
    pso = env.get("pso")
    assert pso["best_cost"] < 0.05
    assert pso["dimensions"] == 2


def test_opt_active_set_quadratic_program():
    code = """
use opt
solve quadratic program active set q [[1.0, 0.0], [0.0, 1.0]] c [-2.0, -2.0] with ineq_matrix [[1.0, 1.0]] with ineq_vec [2.0] into qp
assert qp's converged is true
assert qp's optimal_x[0] is greater than 0.95
assert qp's optimal_x[0] is less than 1.05
assert qp's optimal_x[1] is greater than 0.95
assert qp's optimal_x[1] is less than 1.05
"""
    env = execute(code)
    qp = env.get("qp")
    assert qp["converged"] is True
    assert abs(qp["optimal_x"][0] - 1.0) < 0.05
    assert abs(qp["optimal_x"][1] - 1.0) < 0.05


def test_metrics_wasserstein_distance():
    code = """
use metrics
calculate wasserstein distance between [1.0, 2.0, 3.0] and [2.0, 3.0, 4.0] into w1
assert w1's wasserstein_distance == 1.0
assert w1's samples_u_count == 3
"""
    env = execute(code)
    w1 = env.get("w1")
    assert w1["wasserstein_distance"] == 1.0
    assert w1["samples_u_count"] == 3


def test_metrics_multiclass_roc_auc():
    code = """
use metrics
calculate multiclass roc auc true [0, 1, 2, 0, 1, 2] probs [[0.9, 0.05, 0.05], [0.1, 0.8, 0.1], [0.05, 0.05, 0.9], [0.85, 0.1, 0.05], [0.15, 0.75, 0.1], [0.1, 0.1, 0.8]] classes 3 into auc
assert auc's classes_count == 3
assert auc's macro_auc == 1.0
assert auc's micro_auc == 1.0
"""
    env = execute(code)
    auc = env.get("auc")
    assert auc["classes_count"] == 3
    assert auc["macro_auc"] == 1.0
    assert auc["micro_auc"] == 1.0
