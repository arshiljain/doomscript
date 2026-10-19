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


def test_dsa_btree():
    code = """
use dsa
tree = dsa_btree(t=2)
for x in [10, 20, 5, 6, 12, 30, 7, 17]:
    tree.insert(x, f"v_{x}")

search_12 = tree.search(12)
search_missing = tree.search(999)
sorted_keys = tree.inorder()
"""
    env = execute(code)
    assert env["search_12"] == "v_12"
    assert env["search_missing"] is None
    assert env["sorted_keys"] == [5, 6, 7, 10, 12, 17, 20, 30]


def test_dsa_prefix_trie():
    code = """
use dsa
trie = dsa_prefix_trie()
for w in ["cat", "car", "cart", "dog", "cot", "cost"]:
    trie.insert(w, len(w))

has_car = trie.search("car")
has_cow = trie.search("cow")
c_words = trie.find_words_with_prefix("ca")
wild_c_t = trie.wildcard_search("c?t")
"""
    env = execute(code)
    assert env["has_car"] == 3
    assert env["has_cow"] is None
    assert sorted(env["c_words"]) == ["car", "cart", "cat"]
    assert sorted(env["wild_c_t"]) == ["cat", "cot"]


def test_geo_quadtree():
    code = """
use geo
qt = geo_quadtree(min_x=-100.0, min_y=-100.0, max_x=100.0, max_y=100.0, capacity=2)
qt.insert(10.0, 10.0, "PointA")
qt.insert(12.0, 15.0, "PointB")
qt.insert(50.0, 50.0, "PointC")
qt.insert(-20.0, -20.0, "PointD")

# Query range around (0,0) to (20,20)
range_results = qt.query_range(0.0, 0.0, 20.0, 20.0)
# Query radius 10 around (10, 10)
radius_results = qt.query_radius(10.0, 10.0, 6.0)
"""
    env = execute(code)
    assert sorted(env["range_results"]) == ["PointA", "PointB"]
    assert "PointA" in env["radius_results"]
    assert "PointC" not in env["range_results"]


def test_nlp_kneser_ney():
    code = """
use nlp
corpus = [
    "the cat sat on the mat",
    "the dog sat on the rug",
    "the cat chased the dog"
]
kn = nlp_kneser_ney(order=3, discount=0.75)
kn.fit(corpus)

candidates = kn.predict_next(["the", "cat"], top_n=3)
top_word = candidates[0][0]
score = kn.score_sentence("the cat sat on the mat")
"""
    env = execute(code)
    assert env["top_word"] in ["sat", "chased"]
    assert env["score"] < 0  # valid negative log probability


def test_opt_hungarian_algorithm():
    code = """
use opt
# 3 workers, 3 tasks cost matrix
cost_mat = [
    [9, 2, 7],
    [6, 4, 3],
    [5, 8, 1]
]
res = opt_hungarian_algorithm(cost_mat)
"""
    env = execute(code)
    # Optimal matching: Worker 0 -> Task 1 (cost 2), Worker 1 -> Task 0 (cost 6) or Task 2, etc.
    # Worker 0 -> Col 1 (2), Worker 1 -> Col 0 (6) or Worker 1 -> Col 1..., min total cost is:
    # (0, 1) = 2, (1, 0) = 6, (2, 2) = 1 -> Total = 9. Or (0,1)=2, (1,2)=3, (2,0)=5 -> Total = 10.
    assert env["res"]["total_cost"] == 9.0
    assert len(env["res"]["assignment"]) == 3

