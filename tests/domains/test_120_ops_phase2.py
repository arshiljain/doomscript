"""Test Suite for Phase 2 of 120 Algorithmic & Spoken English Operations.
Covers:
- Batch 4: Finance & Indicators (7 operations)
- Batch 5: NLP & Text Intelligence (7 operations)
- Batch 6: Machine Learning Metrics & Preprocessing (7 operations)
- Batch 7: Graph Theory & Centrality (7 operations)
Total: 28 operations.
"""

import pytest
from doomscript.compiler.engine import execute


def test_batch4_finance_indicators():
    """Batch 4: Finance indicators (bollinger bands, rsi, macd, sharpe, max drawdown, var, cagr)."""
    source = """use finance

set price_series to [100.0, 102.0, 101.0, 105.0, 107.0, 106.0, 110.0, 112.0, 115.0, 114.0, 118.0, 120.0, 122.0, 121.0, 125.0, 124.0, 128.0, 130.0, 132.0, 135.0, 133.0]
bollinger bands for price_series with period 5, std 2 into bb
rsi for price_series with period 5 into rsi_vals
macd for price_series with fast 3, slow 6, signal 3 into macd_res

set returns_series to [0.01, -0.02, 0.03, 0.015, -0.01, 0.025, 0.04, -0.015]
sharpe ratio of returns_series with risk_free 0.01 into sharpe_val
maximum drawdown of price_series into max_dd
value at risk of returns_series at confidence 95 into var_val
cagr of price_series into cagr_val
"""
    env = execute(source)
    # Bollinger Bands
    assert len(env["bb"]["middle"]) > 0
    assert len(env["bb"]["upper"]) == len(env["bb"]["middle"])
    assert env["bb"]["upper"][0] >= env["bb"]["middle"][0] >= env["bb"]["lower"][0]

    # RSI
    assert len(env["rsi_vals"]) > 0
    assert all(0 <= r <= 100 for r in env["rsi_vals"])

    # MACD
    assert len(env["macd_res"]["macd"]) > 0
    assert len(env["macd_res"]["histogram"]) > 0

    # Sharpe ratio
    assert isinstance(env["sharpe_val"], float)

    # Max Drawdown
    assert isinstance(env["max_dd"], float)
    assert env["max_dd"] >= 0.0

    # Value at Risk
    assert isinstance(env["var_val"], float)

    # CAGR
    assert isinstance(env["cagr_val"], float)
    assert env["cagr_val"] > 0.0


def test_batch5_nlp_text_intelligence():
    """Batch 5: NLP (extractive summary, stopwords, word freq, text similarity, jaccard, keywords, regex matches)."""
    source = """use nlp

set doc to "DoomScript is a modern programming language designed for spoken English. It has high leverage operations. The compiler is fast and elegant. Developers love using spoken syntax for everyday tasks."
extractive summary of doc with 2 sentences into summary_doc

set sample_phrase to "This is a wonderful and awesome test of the stopword removal engine"
remove stopwords from sample_phrase into clean_sample

set wordy_text to "apple banana apple cherry apple banana date"
word frequencies of wordy_text into freqs

set phrase_a to "the quick brown fox jumps over the lazy dog"
set phrase_b to "a quick brown dog jumps over the lazy fox"
text similarity between phrase_a and phrase_b into cosine_sim
jaccard similarity of phrase_a and phrase_b into jaccard_sim

set tech_doc to "Python and DoomScript are both expressive programming languages. DoomScript focuses on algorithmic clarity and natural speech."
extract top 3 keywords from tech_doc into top_kw

set log_data to "Error 404 in line 12, Error 500 in line 88, Warning 200 in line 99"
extract all matches of pattern "Error \\d+" in log_data into error_matches
"""
    env = execute(source)
    # 1. Extractive summary
    assert len(env["summary_doc"]) > 0
    assert "DoomScript" in env["summary_doc"]

    # 2. Stopwords
    assert "wonderful" in env["clean_sample"]
    assert "this" not in env["clean_sample"].lower().split()

    # 3. Word frequencies
    assert env["freqs"]["apple"] == 3
    assert env["freqs"]["banana"] == 2

    # 4. Similarities
    assert env["cosine_sim"] > 0.8
    assert env["jaccard_sim"] > 0.7

    # 5. Keywords
    assert len(env["top_kw"]) == 3

    # 6. Regex matches
    assert env["error_matches"] == ["Error 404", "Error 500"]


def test_batch6_ml_metrics_and_preprocessing():
    """Batch 6: ML (train test split, confusion matrix, classification metrics, roc auc, mse, r2, one-hot encode)."""
    source = """use ml

set dataset to [
    {"x": 1, "y": 0}, {"x": 2, "y": 0}, {"x": 3, "y": 1},
    {"x": 4, "y": 1}, {"x": 5, "y": 0}, {"x": 6, "y": 1},
    {"x": 7, "y": 1}, {"x": 8, "y": 0}, {"x": 9, "y": 1}, {"x": 10, "y": 1}
]
split data dataset into train and test with test_size 0.3 into splits

set actuals to [1, 0, 1, 1, 0, 1, 0, 0]
set preds to [1, 0, 1, 0, 0, 1, 1, 0]
set probs to [0.9, 0.1, 0.85, 0.4, 0.2, 0.75, 0.65, 0.15]

confusion matrix of actuals and preds into conf_mat
classification metrics for actuals and preds into metrics
roc auc score of actuals and probs into auc_score

set reg_actuals to [2.0, 4.0, 6.0, 8.0, 10.0]
set reg_preds to [2.1, 3.9, 6.2, 7.8, 10.1]
mean squared error between reg_actuals and reg_preds into mse_val
r2 score between reg_actuals and reg_preds into r2_val

set cat_table to [
    {"id": 1, "color": "red"},
    {"id": 2, "color": "blue"},
    {"id": 3, "color": "red"}
]
one-hot encode column "color" in cat_table into encoded_table
"""
    env = execute(source)
    # Split
    assert len(env["splits"]["test"]) == 3
    assert len(env["splits"]["train"]) == 7

    # Confusion matrix & Metrics
    assert "matrix" in env["conf_mat"]
    assert env["metrics"]["accuracy"] == 0.75
    assert env["metrics"]["precision"] > 0
    assert env["metrics"]["recall"] > 0

    # ROC AUC
    assert env["auc_score"] > 0.8

    # MSE & R^2
    assert env["mse_val"] < 0.1
    assert env["r2_val"] > 0.95

    # One-hot encode
    assert "color_red" in env["encoded_table"][0]
    assert env["encoded_table"][0]["color_red"] == 1
    assert env["encoded_table"][0]["color_blue"] == 0
    assert env["encoded_table"][1]["color_blue"] == 1


def test_batch7_graph_theory_and_centrality():
    """Batch 7: Graph theory (degree, betweenness, closeness centrality, bipartite check, eulerian path, SCC, diameter)."""
    source = """use graph

create undirected graph into g
connect "A" to "B" in g
connect "B" to "C" in g
connect "C" to "D" in g
connect "D" to "A" in g
connect "B" to "D" in g

degree centrality of g into deg_cent
betweenness centrality of g into bet_cent
closeness centrality of g into clo_cent
g is bipartite into is_bip
diameter of g into diam_val

# Eulerian graph
create undirected graph into eg
connect "1" to "2" in eg
connect "2" to "3" in eg
connect "3" to "1" in eg
eulerian path in eg into eul_path

# Directed graph for SCC
create directed graph into dg
connect "X" to "Y" in dg
connect "Y" to "Z" in dg
connect "Z" to "X" in dg
connect "Z" to "W" in dg
strongly connected components of dg into sccs
"""
    env = execute(source)
    # Degree centrality
    assert "B" in env["deg_cent"]
    assert env["deg_cent"]["B"] == 1.0  # connected to A, C, D (3 / 3)

    # Betweenness & Closeness centrality
    assert env["bet_cent"]["B"] >= 0.0
    assert env["clo_cent"]["B"] > 0.0

    # Bipartite check (triangle ABD exists, so not bipartite)
    assert env["is_bip"] is False

    # Diameter
    assert env["diam_val"] <= 2

    # Eulerian path
    assert len(env["eul_path"]) == 4

    # Strongly connected components
    assert any("X" in comp and "Y" in comp and "Z" in comp for comp in env["sccs"])
