"""Comprehensive test suite for Cluster B: Machine Learning, AI & Optimization.

Covers deepened features across:
- ml: LinearSVM (SMO), KMeansPlusPlus, TinyConvNet, GradientBoostedTreesExact
- agent: ReActAgent, TreeOfThoughts, MultiAgentDebate
- opt: PrimalDualInteriorPoint, BranchAndBoundMILP, AdaptiveSimulatedAnnealing
- sim: AgentBasedModel2D, MCMCSampler, JacksonQueuingNetwork
- nlp: BytePairEncoder, HMMPOSTagger, Word2VecCBOW
"""

import math
import pytest
from doomscript.domains.ml.runtime import (
    LinearSVM,
    KMeansPlusPlus,
    TinyConvNet,
    GradientBoostedTreesExact,
    ml_svm_train,
    ml_kmeans_plus_plus,
    ml_tiny_convnet,
    ml_xgboost_exact,
)
from doomscript.domains.agent.runtime import (
    ReActAgent,
    TreeOfThoughts,
    MultiAgentDebate,
    agent_react_run,
    agent_tree_of_thoughts_search,
    agent_run_debate,
)
from doomscript.domains.opt.runtime import (
    PrimalDualInteriorPoint,
    BranchAndBoundMILP,
    AdaptiveSimulatedAnnealing,
    opt_solve_interior_point,
    opt_branch_and_bound_milp,
    opt_adaptive_simulated_annealing,
)
from doomscript.domains.sim.runtime import (
    AgentBasedModel2D,
    MCMCSampler,
    JacksonQueuingNetwork,
    sim_create_abm_2d,
    sim_mcmc_sample,
    sim_jackson_network,
)
from doomscript.domains.nlp.runtime import (
    BytePairEncoder,
    HMMPOSTagger,
    Word2VecCBOW,
    nlp_bpe_train,
    nlp_hmm_pos_tagger,
    nlp_cbow_word2vec,
)


# ============================================================================
# 1. ML Deepened Tests
# ============================================================================

def test_linear_svm_smo():
    # Linearly separable 2D dataset
    X = [
        [1.0, 1.0], [1.5, 1.2], [2.0, 1.8], [0.8, 1.4], # Class 0
        [5.0, 5.0], [5.5, 4.8], [6.0, 5.2], [4.8, 5.5], # Class 1
    ]
    y = [0, 0, 0, 0, 1, 1, 1, 1]

    svm = LinearSVM(C=1.0, max_passes=10, seed=42)
    svm.fit(X, y)

    preds = svm.predict(X)
    assert preds == y
    # Predict new unseen points
    test_pts = [[1.2, 1.1], [5.2, 5.1]]
    test_preds = svm.predict(test_pts)
    assert test_preds == [0, 1]


def test_kmeans_plus_plus():
    # 2 distinct clusters
    cluster1 = [[1.0 + 0.1 * i, 1.0 + 0.1 * i] for i in range(5)]
    cluster2 = [[10.0 + 0.1 * i, 10.0 + 0.1 * i] for i in range(5)]
    X = cluster1 + cluster2

    km = KMeansPlusPlus(n_clusters=2, seed=42)
    km.fit(X)

    labels = km.predict(X)
    assert len(labels) == 10
    # First 5 should have same label, last 5 should have same label
    assert len(set(labels[:5])) == 1
    assert len(set(labels[5:])) == 1
    assert labels[0] != labels[5]
    assert km.inertia_ < 5.0

    # Test auto elbow method
    elbow = KMeansPlusPlus.auto_find_k(X, k_range=(2, 4))
    assert "optimal_k" in elbow
    assert elbow["optimal_k"] in (2, 3)


def test_tiny_convnet():
    # Tiny 6x6 image
    img = [[0.1 * (r + c) for c in range(6)] for r in range(6)]
    net = TinyConvNet(in_shape=(6, 6), num_classes=2, seed=42)

    probs, cache = net.forward(img)
    assert len(probs) == 2
    assert abs(sum(probs) - 1.0) < 1e-4

    # Perform a few training steps on class 1
    initial_loss = net.train_step(img, target_class=1, lr=0.1)
    for _ in range(5):
        loss = net.train_step(img, target_class=1, lr=0.1)
    assert loss <= initial_loss


def test_gradient_boosted_trees_exact():
    # Non-linear regression: y = 2 * x + 0.5 * x^2
    X = [[float(i)] for i in range(10)]
    y = [2.0 * i + 0.5 * (i ** 2) for i in range(10)]

    gbt = GradientBoostedTreesExact(n_estimators=10, max_depth=3, learning_rate=0.2)
    gbt.fit(X, y)

    preds = gbt.predict(X)
    # Mean absolute error should be low
    mae = sum(abs(preds[i] - y[i]) for i in range(10)) / 10.0
    assert mae < 5.0


# ============================================================================
# 2. Agent Deepened Tests
# ============================================================================

def test_react_agent_loop():
    tools = {
        "calculator": lambda query: "42",
        "search": lambda query: "The answer is in database row 10",
    }
    agent = ReActAgent(name="MathAgent", tools=tools, max_steps=4)

    res = agent.run("What is 6 * 7?")
    assert res["status"] == "success"
    assert len(res["trajectory"]) > 0
    assert "Resolved" in res["final_answer"] or "Completed" in res["final_answer"]


def test_tree_of_thoughts_search():
    def custom_generator(state: str, k: int) -> list:
        return [f"Branch_{i}" for i in range(k)]

    def custom_evaluator(goal: str, thought: str) -> float:
        # Give higher score to Branch_1
        return 1.0 if "Branch_1" in thought else 0.2

    tot = TreeOfThoughts(thought_generator=custom_generator, state_evaluator=custom_evaluator)
    res = tot.search(initial_state="Root", k_thoughts=3, max_depth=2, beam_width=2)

    assert "best_trajectory" in res
    assert res["best_score"] == 1.0
    assert res["depth_reached"] >= 1


def test_multi_agent_debate():
    debate = MultiAgentDebate()
    res = debate.run_debate(topic="Should we adopt Rust or Python for this microservice?", rounds=2)

    assert res["rounds_completed"] == 2
    assert len(res["rounds"]) == 2
    assert len(res["participants"]) == 2
    assert "Consensus after 2 rounds" in res["consensus"]


# ============================================================================
# 3. Opt Deepened Tests
# ============================================================================

def test_primal_dual_interior_point():
    # Min c^T x  s.t.  A x = b, x >= 0
    # min 2 * x1 + x2
    # s.t. x1 + x2 + s1 = 4
    #      x1 + 3 * x2 + s2 = 6
    c = [2.0, 1.0, 0.0, 0.0]
    A = [
        [1.0, 1.0, 1.0, 0.0],
        [1.0, 3.0, 0.0, 1.0],
    ]
    b = [4.0, 6.0]

    solver = PrimalDualInteriorPoint(max_iter=30, tol=1e-4)
    res = solver.solve(c, A, b)

    assert "optimal_x" in res
    assert len(res["optimal_x"]) == 4
    # Check all variables non-negative
    for val in res["optimal_x"]:
        assert val >= -1e-4


def test_branch_and_bound_milp():
    # Maximize 5 * x1 + 4 * x2
    # s.t. x1 + x2 <= 5
    #      10 * x1 + 6 * x2 <= 45
    #      x1, x2 in Z+
    c = [5.0, 4.0]
    A_ub = [
        [1.0, 1.0],
        [10.0, 6.0],
    ]
    b_ub = [5.0, 45.0]

    milp = BranchAndBoundMILP(max_nodes=100)
    res = milp.solve(c, A_ub, b_ub, integer_indices=[0, 1], maximize=True)

    assert res["success"]
    sol = res["solution"]
    # Check that solution variables are integer
    for val in sol:
        assert abs(val - round(val)) < 1e-4
    assert res["objective_value"] > 0


def test_adaptive_simulated_annealing():
    # Minimize sphere function f(x) = (x1 - 3)^2 + (x2 + 2)^2
    def sphere(x: list) -> float:
        return (x[0] - 3.0) ** 2 + (x[1] + 2.0) ** 2

    bounds = [(-10.0, 10.0), (-10.0, 10.0)]
    asa = AdaptiveSimulatedAnnealing(max_iter=300, seed=42)
    res = asa.minimize(sphere, bounds, x0=[0.0, 0.0])

    assert res["optimal_cost"] < 1.0
    assert abs(res["optimal_x"][0] - 3.0) < 1.0
    assert abs(res["optimal_x"][1] - (-2.0)) < 1.0


# ============================================================================
# 4. Sim Deepened Tests
# ============================================================================

def test_agent_based_model_2d():
    abm = AgentBasedModel2D(width=50.0, height=50.0, num_agents=30, sensory_radius=8.0, seed=42)
    res = abm.run(steps=15)

    assert res["steps"] == 15
    assert len(res["history"]) == 15
    final_counts = res["final_counts"]
    # Total agents must remain exactly 30
    assert sum(final_counts.values()) == 30


def test_mcmc_sampler():
    # 1D Standard Gaussian: log p(x) = -0.5 * x^2
    def log_normal(x: list) -> float:
        return -0.5 * (x[0] ** 2)

    sampler = MCMCSampler(seed=42)
    res = sampler.sample(log_normal, x0=[5.0], n_samples=300, burn_in=100, proposal_std=0.8)

    assert res["n_samples"] == 300
    assert 0.15 < res["acceptance_rate"] < 0.85
    # Empirical mean should be near 0.0
    assert abs(res["means"][0]) < 0.5


def test_jackson_queuing_network():
    # 2-station Jackson Network
    # External arrivals: station 0 receives 2.0 cust/sec, station 1 receives 1.0 cust/sec
    # Service rates: mu0 = 5.0, mu1 = 4.0
    # Routing: P[0][1] = 0.5, P[1][0] = 0.2
    arrival_rates = [2.0, 1.0]
    service_rates = [5.0, 4.0]
    routing_matrix = [
        [0.0, 0.5],
        [0.2, 0.0],
    ]

    net = JacksonQueuingNetwork(arrival_rates, service_rates, routing_matrix)
    res = net.solve()

    assert res["is_stable"]
    assert len(res["stations"]) == 2
    for st in res["stations"]:
        assert st["utilization"] < 1.0
        assert st["mean_queue_length"] is not None
        assert st["mean_waiting_time"] is not None


# ============================================================================
# 5. NLP Deepened Tests
# ============================================================================

def test_byte_pair_encoder():
    corpus = [
        "low lower lowest",
        "wider widest",
        "new newer newest",
    ]
    bpe = BytePairEncoder(vocab_size=30)
    bpe.fit(corpus, num_merges=10)

    assert len(bpe.merges) > 0
    tokens = bpe.tokenize("lowest")
    assert len(tokens) > 0
    # Decode reconstructed text
    decoded = bpe.decode(tokens)
    assert "lowest" in decoded


def test_hmm_pos_tagger():
    tagged_data = [
        [("the", "DET"), ("cat", "NOUN"), ("sat", "VERB"), ("on", "PREP"), ("the", "DET"), ("mat", "NOUN")],
        [("a", "DET"), ("dog", "NOUN"), ("ran", "VERB"), ("in", "PREP"), ("the", "DET"), ("park", "NOUN")],
        [("the", "DET"), ("dog", "NOUN"), ("barked", "VERB")],
    ]
    tagger = HMMPOSTagger()
    tagger.fit(tagged_data)

    test_sent = ["the", "cat", "ran"]
    tagged = tagger.tag(test_sent)

    assert len(tagged) == 3
    assert tagged[0] == ("the", "DET")
    assert tagged[1] == ("cat", "NOUN")
    assert tagged[2] == ("ran", "VERB")


def test_word2vec_cbow():
    corpus = [
        "the king rules the kingdom with wisdom",
        "the queen rules the kingdom with grace",
        "the prince and princess live in the castle",
        "a king and a queen wear royal crowns",
    ]
    w2v = Word2VecCBOW(embedding_dim=8, window_size=2, seed=42)
    w2v.fit(corpus, epochs=15, lr=0.1)

    king_emb = w2v.get_embedding("king")
    assert king_emb is not None
    assert len(king_emb) == 8

    # Query most similar
    sims = w2v.most_similar("king", top_n=3)
    assert len(sims) > 0
    assert all(isinstance(t[1], float) for t in sims)
