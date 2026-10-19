"""Comprehensive integration tests for deepened core domains (DSA, Data, ML, Finance)."""

import pytest
import math
from doomscript.domains.dsa.runtime import (
    AVLTree,
    SuffixAutomaton,
    AhoCorasick,
    Treap,
    DinicMaxFlow,
    dsa_avl_create,
    dsa_avl_insert,
    dsa_avl_contains,
    dsa_avl_delete,
    dsa_avl_inorder,
    dsa_avl_height,
    dsa_suffix_automaton_create,
    dsa_sam_contains_substring,
    dsa_sam_distinct_substrings,
    dsa_sam_longest_common_substring,
    dsa_aho_corasick_create,
    dsa_aho_corasick_search,
    dsa_treap_create,
    dsa_treap_insert,
    dsa_treap_contains,
    dsa_dinic_max_flow,
)
from doomscript.domains.data.runtime import (
    ColumnarTable,
    data_to_columnar,
    columnar_to_records,
    data_fuzzy_join,
    data_pivot_advanced,
    data_unpivot_melt,
    data_json_explode,
    data_window_rolling,
)
from doomscript.domains.ml.runtime import (
    MLPClassifier,
    MLPRegressor,
    CARTDecisionTree,
    GBDTModel,
    IsolationForestModel,
    ml_train_mlp,
    ml_train_cart,
    ml_train_gbdt,
    ml_train_isolation_forest,
)
from doomscript.domains.finance.runtime import (
    fin_black_litterman,
    fin_var_cvar_monte_carlo,
    fin_hull_white_trinomial,
    fin_ichimoku_cloud,
)
from doomscript.compiler.engine import execute


# =========================================================================
# 1. DSA Deepened Tests
# =========================================================================

def test_avl_tree_properties():
    avl = dsa_avl_create()
    for val in [50, 20, 70, 10, 30, 60, 80, 25]:
        dsa_avl_insert(avl, val)

    assert dsa_avl_contains(avl, 30) is True
    assert dsa_avl_contains(avl, 999) is False
    assert dsa_avl_inorder(avl) == [10, 20, 25, 30, 50, 60, 70, 80]

    # Deletion maintains BST and balance
    dsa_avl_delete(avl, 20)
    assert dsa_avl_contains(avl, 20) is False
    assert dsa_avl_inorder(avl) == [10, 25, 30, 50, 60, 70, 80]
    assert dsa_avl_height(avl) <= 4


def test_suffix_automaton():
    sam = dsa_suffix_automaton_create("banana")
    assert dsa_sam_contains_substring(sam, "ana") is True
    assert dsa_sam_contains_substring(sam, "nan") is True
    assert dsa_sam_contains_substring(sam, "apple") is False

    # Distinct substrings of "banana": "", "a", "b", "n", "an", "ba", "na", "ana", "ban", "nan", "anan", "bana", "nana", "anana", "banan", "banana" (15 non-empty)
    distinct = dsa_sam_distinct_substrings(sam)
    assert distinct == 15

    lcs = dsa_sam_longest_common_substring(sam, "cabana")
    assert lcs == "bana"


def test_aho_corasick_multi_pattern():
    ac = dsa_aho_corasick_create(["he", "she", "his", "hers"])
    matches = dsa_aho_corasick_search(ac, "ahishers")
    # Should detect: "his", "he", "she", "hers"
    matched_words = [m["word"] for m in matches]
    assert "his" in matched_words
    assert "he" in matched_words
    assert "she" in matched_words
    assert "hers" in matched_words


def test_treap_operations():
    treap = dsa_treap_create()
    for k in [15, 10, 20, 5, 12, 18, 25]:
        dsa_treap_insert(treap, k)

    assert dsa_treap_contains(treap, 12) is True
    assert dsa_treap_contains(treap, 99) is False
    assert treap.to_list() == [5, 10, 12, 15, 18, 20, 25]


def test_dinic_max_flow():
    # Standard flow network: S=0, T=3, intermediate 1, 2
    # 0 -> 1 (cap 10), 0 -> 2 (cap 10), 1 -> 2 (cap 2), 1 -> 3 (cap 4), 2 -> 3 (cap 9)
    dinic = DinicMaxFlow(4)
    dinic.add_edge(0, 1, 10)
    dinic.add_edge(0, 2, 10)
    dinic.add_edge(1, 2, 2)
    dinic.add_edge(1, 3, 4)
    dinic.add_edge(2, 3, 9)

    max_f = dinic.max_flow(0, 3)
    # Bottleneck at output: 4 + 9 = 13
    assert max_f == 13


# =========================================================================
# 2. Data Deepened Tests
# =========================================================================

def test_columnar_table_store():
    records = [
        {"id": 1, "name": "Alice", "score": 90.0, "dept": "Eng"},
        {"id": 2, "name": "Bob", "score": 75.0, "dept": "HR"},
        {"id": 3, "name": "Charlie", "score": 85.0, "dept": "Eng"},
        {"id": 4, "name": "Diana", "score": 95.0, "dept": "Eng"},
    ]
    col_table = data_to_columnar(records)
    assert col_table.num_rows == 4
    assert col_table.num_cols == 4
    assert "score" in col_table.column_names

    # Columnar aggregation
    assert col_table.aggregate("score", "mean") == 86.25
    assert col_table.aggregate("score", "max") == 95.0
    assert col_table.aggregate("score", "min") == 75.0

    # Columnar filter
    eng_table = col_table.filter("dept", "==", "Eng")
    assert eng_table.num_rows == 3

    # Back to records
    recs = columnar_to_records(eng_table)
    assert len(recs) == 3
    assert all(r["dept"] == "Eng" for r in recs)


def test_fuzzy_join_approximate_matching():
    table_a = [
        {"cid": 101, "company": "Microsoft Corp", "region": "US"},
        {"cid": 102, "company": "Alphabet Inc", "region": "US"},
        {"cid": 103, "company": "Amazon AWS", "region": "US"},
    ]
    table_b = [
        {"bid": 1, "vendor_name": "Microsoft Corporation", "rating": 4.8},
        {"bid": 2, "vendor_name": "Alphabet Inc.", "rating": 4.9},
        {"bid": 3, "vendor_name": "Apple Computers", "rating": 4.7},
    ]

    joined = data_fuzzy_join(
        table_a,
        table_b,
        left_on="company",
        right_on="vendor_name",
        threshold=0.65,
        how="inner",
    )
    # Microsoft and Alphabet should match
    assert len(joined) >= 2
    matched_cids = {r["cid"] for r in joined}
    assert 101 in matched_cids
    assert 102 in matched_cids
    assert all("similarity_score" in r for r in joined)


def test_data_pivot_and_melt():
    raw = [
        {"region": "North", "quarter": "Q1", "revenue": 100},
        {"region": "North", "quarter": "Q2", "revenue": 150},
        {"region": "South", "quarter": "Q1", "revenue": 80},
        {"region": "South", "quarter": "Q2", "revenue": 120},
    ]
    pivoted = data_pivot_advanced(raw, index_col="region", columns_col="quarter", values_col="revenue", agg_fn="sum")
    assert len(pivoted) == 2
    north = [r for r in pivoted if r["region"] == "North"][0]
    assert north["Q1"] == 100
    assert north["Q2"] == 150

    melted = data_unpivot_melt(pivoted, id_vars=["region"], value_vars=["Q1", "Q2"])
    assert len(melted) == 4


def test_data_json_explode_and_window():
    orders = [
        {"order_id": 1, "items": ["apple", "banana"]},
        {"order_id": 2, "items": ["cherry"]},
    ]
    exploded = data_json_explode(orders, column="items")
    assert len(exploded) == 3
    assert [r["items"] for r in exploded] == ["apple", "banana", "cherry"]

    series = [{"val": 10}, {"val": 20}, {"val": 30}, {"val": 40}]
    rolling = data_window_rolling(series, column="val", window_size=2, stat="mean")
    assert rolling[0]["val_rolling_mean"] == 10.0
    assert rolling[1]["val_rolling_mean"] == 15.0
    assert rolling[2]["val_rolling_mean"] == 25.0


# =========================================================================
# 3. Machine Learning Deepened Tests
# =========================================================================

def test_mlp_classifier():
    # XOR problem
    X = [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]] * 10
    y = [0, 1, 1, 0] * 10
    mlp = ml_train_mlp(X, y, hidden_layers=(8, 8), is_classifier=True, lr=0.05, max_iter=300)
    preds = mlp.predict([[0.0, 1.0], [1.0, 0.0], [0.0, 0.0], [1.0, 1.0]])
    assert len(preds) == 4
    # Predictions are valid class labels
    assert all(p in (0, 1) for p in preds)


def test_mlp_regressor():
    X = [[1.0], [2.0], [3.0], [4.0], [5.0]]
    y = [2.0, 4.0, 6.0, 8.0, 10.0]
    reg = ml_train_mlp(X, y, hidden_layers=(8,), is_classifier=False, lr=0.05, max_iter=300)
    preds = reg.predict([[3.0], [5.0]])
    assert len(preds) == 2
    assert all(isinstance(p, float) for p in preds)


def test_cart_decision_tree():
    X = [[1.0, 10.0], [1.2, 12.0], [8.0, 80.0], [8.5, 85.0]]
    y = ["Small", "Small", "Large", "Large"]
    tree = ml_train_cart(X, y, is_classifier=True, max_depth=3)
    preds = tree.predict([[1.1, 11.0], [9.0, 90.0]])
    assert preds == ["Small", "Large"]


def test_gbdt_ensemble():
    X = [[1.0], [2.0], [3.0], [4.0], [5.0], [6.0]]
    y = [1.5, 3.1, 4.4, 6.2, 7.9, 9.1]
    gbdt = ml_train_gbdt(X, y, is_classifier=False, n_estimators=10, lr=0.1)
    preds = gbdt.predict([[2.5], [5.0]])
    assert len(preds) == 2
    # Monotonically increasing check
    assert preds[1] > preds[0]


def test_isolation_forest_anomaly_detection():
    # 50 normal points clustered near (0, 0), and 2 extreme anomalies at (100, 100)
    import random
    rng = random.Random(42)
    normal = [[rng.gauss(0, 1), rng.gauss(0, 1)] for _ in range(50)]
    anomalies = [[100.0, 100.0], [-100.0, -100.0]]
    X = normal + anomalies

    iso = ml_train_isolation_forest(X, n_estimators=40, contamination=0.05)
    scores = iso.decision_function([[0.0, 0.0], [100.0, 100.0]])
    # Anomalous points have higher anomaly score
    assert scores[1] > scores[0]


# =========================================================================
# 4. Quantitative Finance Deepened Tests
# =========================================================================

def test_black_litterman_allocation():
    # 2 assets: US Equities, Emerging Markets
    market_weights = [0.70, 0.30]
    cov_matrix = [
        [0.04, 0.015],
        [0.015, 0.09],
    ]
    # View: Emerging Markets will outperform US Equities by 4%
    views_p = [[-1.0, 1.0]]
    views_q = [0.04]

    bl = fin_black_litterman(
        market_weights=market_weights,
        cov_matrix=cov_matrix,
        views_p=views_p,
        views_q=views_q,
        tau=0.05,
        risk_aversion=2.5,
    )
    assert "implied_equilibrium_returns" in bl
    assert "posterior_returns" in bl
    assert "posterior_weights" in bl
    assert len(bl["posterior_weights"]) == 2
    # Because of bullish view on Emerging Markets, its weight should increase relative to prior
    assert bl["posterior_weights"][1] > 0.30


def test_var_cvar_monte_carlo():
    mc = fin_var_cvar_monte_carlo(
        current_val=100000.0,
        mu=0.08,
        sigma=0.20,
        horizon_days=10,
        simulations=2000,
        confidence=0.95,
        seed=42,
    )
    assert "var" in mc
    assert "cvar" in mc
    # CVaR (Expected Shortfall) must strictly be greater than or equal to VaR
    assert mc["cvar"] >= mc["var"]
    assert mc["var"] > 0.0


def test_hull_white_trinomial_lattice():
    hw = fin_hull_white_trinomial(
        r0=0.05,
        a=0.1,
        sigma=0.015,
        n_steps=8,
        dt=0.25,
    )
    assert "bond_price" in hw
    # Bond price must be discounted between 0 and 1
    assert 0.0 < hw["bond_price"] < 1.0
    assert "yield_to_maturity" in hw


def test_ichimoku_cloud():
    # Synthetic 60-day price trend
    highs = [100.0 + i * 1.5 + (i % 3) for i in range(60)]
    lows = [95.0 + i * 1.5 - (i % 3) for i in range(60)]
    closes = [98.0 + i * 1.5 for i in range(60)]

    ichi = fin_ichimoku_cloud(highs, lows, closes)
    assert len(ichi["tenkan"]) == 60
    assert len(ichi["kijun"]) == 60
    assert len(ichi["senkou_a"]) == 60
    assert len(ichi["senkou_b"]) == 60
    assert len(ichi["chikou"]) == 60
