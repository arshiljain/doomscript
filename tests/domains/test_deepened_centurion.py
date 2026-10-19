"""Tests for Deepened Capabilities across Existing Domains:
- dsa: RedBlackTree and SkipList
- ml: RandomForestModel
- finance: fin_monte_carlo_var
- graph: graph_johnson_apsp
- net: DNSWireProtocol
- sim: DiscreteEventSimulation
"""

import pytest
from doomscript.compiler.engine import execute


def test_dsa_red_black_tree():
    code = """
use dsa
rb = dsa_red_black_tree()
# Insert values in ascending order to test balancing rotations
for x in [10, 20, 30, 15, 25, 5, 1]:
    rb.insert(x, f"val_{x}")

search_20 = rb.search(20)
search_missing = rb.search(999)
min_val = rb.minimum()
max_val = rb.maximum()
inorder_keys = rb.inorder()
is_valid = rb.is_valid_rb()
"""
    env = execute(code)
    assert env["search_20"] == "val_20"
    assert env["search_missing"] is None
    assert env["min_val"] == 1
    assert env["max_val"] == 30
    assert env["inorder_keys"] == [1, 5, 10, 15, 20, 25, 30]
    assert env["is_valid"] is True


def test_dsa_skip_list():
    code = """
use dsa
sl = dsa_skip_list()
for x in [50, 20, 80, 10, 30, 70, 90]:
    sl.insert(x, f"item_{x}")

search_30 = sl.search(30)
search_missing = sl.search(999)
sorted_keys = sl.to_list()
del_res = sl.delete(20)
after_del_keys = sl.to_list()
"""
    env = execute(code)
    assert env["search_30"] == "item_30"
    assert env["search_missing"] is None
    assert env["sorted_keys"] == [10, 20, 30, 50, 70, 80, 90]
    assert env["del_res"] is True
    assert env["after_del_keys"] == [10, 30, 50, 70, 80, 90]


def test_ml_random_forest():
    code = """
use ml
# Synthetic binary classification: 2D distinct clusters
X = [
    [2.0, 2.0], [2.1, 1.9], [1.9, 2.2], [2.5, 2.0],
    [-2.0, -2.0], [-2.1, -1.9], [-1.9, -2.2], [-2.5, -2.0]
]
y = [1, 1, 1, 1, 0, 0, 0, 0]

rf = ml_train_random_forest(X, y, n_estimators=10, max_depth=3, seed=42)
preds = rf.predict([[2.0, 2.0], [1.8, 1.8], [-2.0, -2.0], [-1.8, -1.8]])
"""
    env = execute(code)
    assert env["preds"] == [1, 1, 0, 0]


def test_finance_monte_carlo_var():
    code = """
use finance
var_res = fin_monte_carlo_var(
    initial_portfolio_value=100000.0,
    expected_annual_return=0.08,
    annual_volatility=0.20,
    time_horizon_days=10,
    num_simulations=1000,
    seed=42
)
"""
    env = execute(code)
    res = env["var_res"]
    assert res["var_95"] > 0
    assert res["var_99"] > res["var_95"]
    assert res["cvar_95"] >= res["var_95"]
    assert res["cvar_99"] >= res["var_99"]
    assert res["mean_final_value"] > 90000.0


def test_graph_johnson_apsp():
    code = """
use graph
g = create_graph(directed=True)
# Directed triangle with negative edge (no negative cycle)
# 1 -> 2 (weight 3)
# 2 -> 3 (weight -2)
# 1 -> 3 (weight 5)
add_graph_edge(g, "1", "2", 3.0)
add_graph_edge(g, "2", "3", -2.0)
add_graph_edge(g, "1", "3", 5.0)

apsp_res = graph_johnson_apsp(g)
"""
    env = execute(code)
    assert env["apsp_res"]["has_negative_cycle"] is False
    dists = env["apsp_res"]["distances"]
    # 1 -> 3 shortest path is 1 -> 2 -> 3 with weight 3 + (-2) = 1.0
    assert dists["1"]["3"] == 1.0
    assert dists["1"]["2"] == 3.0
    assert dists["2"]["3"] == -2.0


def test_net_dns_wire_protocol():
    code = """
use net
query_bytes = net_dns_build_query("www.example.com", qtype="A", tx_id=22136)
parsed_query = net_dns_parse_packet(query_bytes)
"""
    env = execute(code)
    assert env["parsed_query"]["id"] == 22136
    assert env["parsed_query"]["is_response"] is False
    assert len(env["parsed_query"]["questions"]) == 1
    assert env["parsed_query"]["questions"][0]["name"] == "www.example.com"
    assert env["parsed_query"]["questions"][0]["type"] == "A"


def test_sim_discrete_event_simulation():
    code = """
use sim
sim_eng = sim_create_discrete_event_sim()
server = sim_eng.add_resource("server", capacity=1)

events_log = []

def process_job(job_id):
    t = round(sim_eng.current_time, 1)
    events_log.append(f"job_{job_id}_completed_at_{t}")
    nxt = server.release(sim_eng.current_time)
    if nxt:
        nxt[1]()

def handle_arrival(job_id, service_time):
    t = round(sim_eng.current_time, 1)
    events_log.append(f"job_{job_id}_arrived_at_{t}")
    acquired = server.request(
        sim_eng.current_time,
        job_id,
        lambda: sim_eng.schedule(service_time, process_job, 0, job_id)
    )
    if acquired:
        sim_eng.schedule(service_time, process_job, 0, job_id)

# Job 1 arrives at t=0, takes 5s
# Job 2 arrives at t=2, takes 4s (must wait in queue until t=5)
sim_eng.schedule(0.0, handle_arrival, 0, 1, 5.0)
sim_eng.schedule(2.0, handle_arrival, 0, 2, 4.0)

final_stats = sim_eng.run_until(15.0)
"""
    env = execute(code)
    assert env["final_stats"]["events_processed"] >= 4
    assert env["events_log"] == [
        "job_1_arrived_at_0.0",
        "job_2_arrived_at_2.0",
        "job_1_completed_at_5.0",
        "job_2_completed_at_9.0"
    ]
    # Job 2 waited from t=2 to t=5 (3.0s wait time)
    res_stats = env["final_stats"]["resources"]["server"]
    assert res_stats["total_served"] == 2
    assert res_stats["avg_wait_time"] == 1.5  # (0.0 + 3.0) / 2
