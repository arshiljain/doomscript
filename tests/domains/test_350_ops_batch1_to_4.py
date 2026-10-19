"""Comprehensive Test Suite for Group A of 350 Domain Operations.
Covers:
- Batch 1: Advanced DSA & Algorithmic Optimizations (19 operations)
- Batch 2: Data Engineering & Tabular Transformations (20 operations)
- Batch 3: Machine Learning & Statistical Modeling (20 operations)
- Batch 4: Quantitative Finance & Risk Analysis (20 operations)
Total: 79 operations.
"""

import pytest
from doomscript.compiler.engine import execute


def test_batch1_dsa_trie_dsu_lru():
    """Batch 1: Trie, DSU, and LRU Cache."""
    source = """use dsa

# Trie
create prefix tree into t
insert word "apple" into prefix tree t
insert word "app" into prefix tree t
search word "apple" in prefix tree t into has_apple
search word "appl" in prefix tree t into has_appl
check if prefix tree t starts with "app" into starts_app
check if prefix tree t starts with "bat" into starts_bat

# DSU
create disjoint set with size 5 into dsu
union sets 0 and 1 in disjoint set dsu into u1
union sets 1 and 2 in disjoint set dsu into u2
find root of 2 in disjoint set dsu into root2
find root of 0 in disjoint set dsu into root0
find root of 4 in disjoint set dsu into root4

# LRU Cache
create lru cache with capacity 2 into lru
put key "a" with value 100 into lru cache lru
put key "b" with value 200 into lru cache lru
get key "a" from lru cache lru into got_a
put key "c" with value 300 into lru cache lru
get key "b" from lru cache lru with default -1 into got_b
get key "c" from lru cache lru into got_c
"""
    env = execute(source)
    assert env["has_apple"] is True
    assert env["has_appl"] is False
    assert env["starts_app"] is True
    assert env["starts_bat"] is False

    assert env["root2"] == env["root0"]
    assert env["root4"] != env["root0"]

    assert env["got_a"] == 100
    assert env["got_b"] == -1  # evicted
    assert env["got_c"] == 300


def test_batch1_dsa_binary_search_and_arrays():
    """Batch 1: Binary search variants, QuickSelect, 2D Kadane, Inversion count."""
    source = """use dsa

set arr to [1, 2, 4, 4, 4, 6, 8]
binary search leftmost 4 in arr into bsl
binary search rightmost 4 in arr into bsr

set unsorted to [12, 3, 5, 7, 4, 19, 26]
quickselect 2nd smallest from unsorted into qs_elem

set grid to [[1, 2, -1], [-3, 4, 2], [1, 1, 1]]
maximum sum 2d subgrid in grid into kad2

set inv_arr to [2, 4, 1, 3, 5]
count inversions in inv_arr into inv_count

next lexicographical permutation of [1, 2, 3] into next_p
previous lexicographical permutation of [1, 3, 2] into prev_p
"""
    env = execute(source)
    assert env["bsl"] == 2
    assert env["bsr"] == 5
    assert env["qs_elem"] == 5  # sorted: [3, 4, 5, 7, 12, 19, 26] -> index 2 is 5
    assert env["kad2"]["max_sum"] == 9  # subgrid of bottom 2 rows cols 1..2: (4+2)+(1+1)=8, or whole rows...
    assert env["inv_count"] == 3  # (2,1), (4,1), (4,3)
    assert env["next_p"] == [1, 3, 2]
    assert env["prev_p"] == [1, 2, 3]


def test_batch1_dsa_strings_and_graphs():
    """Batch 1: Rabin-Karp, Manacher, and Tarjan Bridges."""
    source = """use dsa

rabin karp search for "ana" in "banana" into rk_matches
longest palindromic substring in "babad" into pal_sub

set edge_list to [[0, 1], [1, 2], [2, 0], [1, 3]]
find bridges in graph edge_list into brg
"""
    env = execute(source)
    assert env["rk_matches"] == [1, 3]
    assert env["pal_sub"] in ("bab", "aba")
    assert env["brg"] == [(1, 3)]


def test_batch2_data_analytics():
    """Batch 2: Data Manipulation (Ranks, Windowing, Coalesce, Sort, Joins)."""
    source = """use data

set df to [{"name": "A", "score": 80}, {"name": "B", "score": 90}, {"name": "C", "score": 80}, {"name": "D", "score": 70}]
rank column "score" in df into ranked
lag column "score" in df by 1 into lagged
lead column "score" in df by 1 into leaded
cumulative sum of column "score" in df into cum_sum
cumulative max of column "score" in df into cum_max
cumulative min of column "score" in df into cum_min

set null_df to [{"c1": None, "c2": 10}, {"c1": 20, "c2": None}, {"c1": None, "c2": None}]
coalesce columns ["c1", "c2"] in null_df into column "chosen"

sort table df by [("score", True)] into sorted_df

set d1 to [{"x": 1}, {"x": 2}]
set d2 to [{"y": "a"}, {"y": "b"}]
cross join d1 and d2 into crossed
"""
    env = execute(source)
    assert len(env["ranked"]) == 4
    # Scores: 70 (rank 1), 80 & 80 (ranks 2 & 3 -> avg 2.5), 90 (rank 4)
    r_map = {r["name"]: r["score_rank"] for r in env["ranked"]}
    assert r_map["D"] == 1.0
    assert r_map["A"] == 2.5
    assert r_map["C"] == 2.5
    assert r_map["B"] == 4.0

    assert env["lagged"][0]["score_lag_1"] is None
    assert env["lagged"][1]["score_lag_1"] == 80
    assert env["leaded"][0]["score_lead_1"] == 90
    assert env["cum_sum"][1]["score_cumsum"] == 170.0
    assert env["cum_max"][1]["score_cummax"] == 90.0
    assert env["cum_min"][3]["score_cummin"] == 70.0

    assert env["null_df"][0]["chosen"] == 10
    assert env["null_df"][1]["chosen"] == 20
    assert env["null_df"][2]["chosen"] is None

    assert env["sorted_df"][0]["score"] == 70
    assert len(env["crossed"]) == 4


def test_batch2_data_cleaning_and_validation():
    """Batch 2: Schema validation, rename, clip, date formatting, strings, fills."""
    source = """use data

set raw_data to [{"val": 5, "dt": "2024-05-10", "txt": "  hello  "}, {"val": 150, "dt": "2023-11-20", "txt": "world"}]
clip column "val" in raw_data between 0 and 100 into clipped
format date column "dt" in raw_data as "%d/%m/%Y" into formatted_dt
trim whitespace in column "txt" of raw_data into trimmed
uppercase text in column "txt" of raw_data into uppercased
lowercase text in column "txt" of raw_data into lowercased
extract year from column "dt" in raw_data into with_year

validate schema of raw_data against {"val": int, "dt": str} into val_report
rename columns in raw_data using {"val": "metric"} into renamed

set null_seq to [{"v": 10}, {"v": None}, {"v": None}, {"v": 40}]
forward fill nulls in column "v" of null_seq into ffilled
backward fill nulls in column "v" of null_seq into bfilled

sample 0.5 fraction from raw_data into sampled
"""
    env = execute(source)
    assert env["clipped"][0]["val"] == 5.0
    assert env["clipped"][1]["val"] == 100.0  # clipped from 150
    assert env["formatted_dt"][0]["dt"] == "10/05/2024"
    assert env["trimmed"][0]["txt"] == "hello"
    assert env["uppercased"][1]["txt"] == "WORLD"
    assert env["with_year"][0]["dt_year"] == 2024
    assert env["with_year"][1]["dt_year"] == 2023
    assert env["val_report"]["valid"] is True
    assert "metric" in env["renamed"][0]

    assert [r["v"] for r in env["ffilled"]] == [10, 10, 10, 40]
    assert [r["v"] for r in env["bfilled"]] == [10, 40, 40, 40]
    assert len(env["sampled"]) == 1


def test_batch3_ml_classifiers_and_clusters():
    """Batch 3: KNN, Decision Stump, Naive Bayes, KMeans, PCA."""
    source = """use ml

set tr to [{"f1": 1.0, "f2": 1.0, "y": 0}, {"f1": 1.2, "f2": 0.9, "y": 0}, {"f1": 5.0, "f2": 5.0, "y": 1}, {"f1": 5.2, "f2": 4.8, "y": 1}]
train knn classifier on tr predicting "y" with 1 neighbors into knn_m
fit decision stump on tr predicting "y" into stump_m
train gaussian naive bayes on tr predicting "y" into gnb_m

set bin_tr to [{"b1": 1, "b2": 0, "y": "cat"}, {"b1": 1, "b2": 1, "y": "cat"}, {"b1": 0, "b2": 1, "y": "dog"}]
train bernoulli naive bayes on bin_tr predicting "y" into bnb_m

set pts to [{"x": 1.0, "y": 1.0}, {"x": 1.5, "y": 1.2}, {"x": 8.0, "y": 8.0}, {"x": 8.5, "y": 8.2}]
cluster pts with kmeans into 2 clusters into km_res
reduce dimensionality of pts using pca to 1 components into pca_res
"""
    env = execute(source)
    assert env["knn_m"].predict([[1.1, 1.0]]) == [0]
    assert env["knn_m"].predict([[5.1, 4.9]]) == [1]
    assert env["stump_m"].predict([[1.0, 1.0]]) in ([0], [1])
    assert env["gnb_m"].predict([[1.0, 1.0]]) == [0]
    assert env["gnb_m"].predict([[5.0, 5.0]]) == [1]
    assert env["bnb_m"].predict([[1, 0]]) == ["cat"]

    clusters = env["km_res"]["clusters"]
    assert clusters[0]["cluster"] == clusters[1]["cluster"]
    assert clusters[2]["cluster"] == clusters[3]["cluster"]
    assert clusters[0]["cluster"] != clusters[2]["cluster"]
    assert "pca_1" in env["pca_res"][0]


def test_batch3_ml_metrics_and_preprocessing():
    """Batch 3: Log loss, Brier, F1, Precision/Recall, Polynomials, Target encode, Cosine decay, Splits."""
    source = """use ml

compute log loss between [1, 0, 1, 0] and [0.9, 0.1, 0.8, 0.2] into lloss
compute brier score between [1, 0] and [0.8, 0.2] into brier
compute f1 score between [1, 1, 0, 1] and [1, 0, 0, 1] into f1
compute precision and recall between [1, 1, 0, 1] and [1, 0, 0, 1] into pr_metrics

set num_data to [{"a": 2, "b": 3}]
generate polynomial features for num_data with degree 2 into poly_df

set cat_data to [{"team": "red", "score": 10}, {"team": "red", "score": 20}, {"team": "blue", "score": 5}]
target encode column "team" using "score" in cat_data into t_encoded

cosine decay learning rate from 0.1 at step 50 of 100 into decayed_lr

set split_data to [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}, {"id": 5}, {"id": 6}, {"id": 7}, {"id": 8}, {"id": 9}, {"id": 10}]
split split_data into train val test into splits

compute anomaly scores in num_data into anom_scores
compute hinge loss between [1, -1] and [0.8, -0.9] into h_loss
exponential moving average of weights [[1.0, 2.0], [2.0, 3.0]] with decay 0.5 into ema_w
clip gradients [3.0, 4.0] by norm 2.5 into clipped_grads
"""
    env = execute(source)
    assert env["lloss"] < 0.3
    assert env["brier"] < 0.1
    assert env["f1"] > 0.7
    assert env["pr_metrics"]["precision"] == 1.0
    assert "a_pow_2" in env["poly_df"][0]
    assert env["poly_df"][0]["a_pow_2"] == 4.0
    assert env["poly_df"][0]["a_x_b"] == 6.0
    assert "team_encoded" in env["t_encoded"][0]
    assert 0.04 < env["decayed_lr"] < 0.06  # at mid step (50/100), cos(pi/2)=0 -> lr * 0.5 = 0.05
    assert len(env["splits"]["train"]) >= 6
    assert len(env["anom_scores"]) == 1
    assert env["h_loss"] < 0.3
    assert env["ema_w"] == [1.5, 2.5]
    assert env["clipped_grads"] == [1.5, 2.0]  # norm was 5.0, scaled by 2.5/5.0 = 0.5


def test_batch4_finance_indicators_and_options():
    """Batch 4: VWAP, Stoch, Sortino, Treynor, Calmar, Beta, Alpha, Black-Scholes."""
    source = """use finance

set prices to [10.0, 11.0, 12.0, 11.5]
set vols to [100, 200, 150, 50]
volume weighted average price of prices with volumes vols into vwap_val

set hs to [12.0, 13.0, 14.0, 15.0, 16.0]
set ls to [9.0, 10.0, 11.0, 12.0, 13.0]
set cs to [11.0, 12.0, 13.5, 14.0, 15.5]
stochastic oscillator of hs ls cs with period 3 into stoch_res

set rets to [0.05, -0.02, 0.04, -0.01, 0.03]
set mkt_rets to [0.03, -0.01, 0.02, 0.0, 0.02]
sortino ratio of returns rets with risk free rate 0.01 into sortino_val
beta coefficient of rets vs mkt_rets into beta_val
treynor ratio of returns rets vs market mkt_rets with risk free rate 0.01 into treynor_val
jensen alpha of rets vs mkt_rets with risk free rate 0.01 into alpha_val
calmar ratio of returns rets into calmar_val

# Black-Scholes pricing
black scholes call price for spot 100 strike 100 expiry 1 rate 0.05 volatility 0.2 into bs_call
black scholes put price for spot 100 strike 100 expiry 1 rate 0.05 volatility 0.2 into bs_put
"""
    env = execute(source)
    assert 11.0 < env["vwap_val"] < 12.0
    assert len(env["stoch_res"]["percent_k"]) == 3
    assert env["sortino_val"] > 0
    assert env["beta_val"] > 0
    assert env["treynor_val"] != 0
    assert env["bs_call"] > 9.0  # Approx 10.45
    assert env["bs_put"] > 5.0   # Approx 5.57
    # Put-call parity check: C - P = S - K * exp(-rT) = 100 - 100*exp(-0.05) ~ 4.88
    assert abs((env["bs_call"] - env["bs_put"]) - (100 - 100 * 0.9512)) < 0.5


def test_batch4_finance_advanced_channels_and_risk():
    """Batch 4: ATR, Keltner, Williams %R, MFI, Rebalance, TWAP, Donchian, Info Ratio, Drawdown, IV, VaR."""
    source = """use finance

set hs to [12.0, 13.0, 14.0, 15.0, 16.0]
set ls to [9.0, 10.0, 11.0, 12.0, 13.0]
set cs to [11.0, 12.0, 13.5, 14.0, 15.5]
set vs to [1000, 1200, 1100, 1500, 1300]

average true range of hs ls cs with period 3 into atr_vals
keltner channels for hs ls cs into keltner_res
williams percent r of hs ls cs with period 3 into wr_vals
money flow index of hs ls cs vs with period 3 into mfi_vals

rebalance portfolio weights {"AAPL": 0.6, "GOOG": 0.4} to target {"AAPL": 0.5, "GOOG": 0.5} with value 10000 into reb_trades
time weighted average price of cs into twap_val
donchian channels for hs and ls with period 3 into donch_res

set a_rets to [0.03, 0.02, 0.01, 0.04]
set b_rets to [0.02, 0.02, 0.01, 0.02]
information ratio of a_rets vs benchmark b_rets into ir_val
drawdown series for returns [100, 120, 110, 130, 90] into dd_res

implied volatility of call for price 10.45 spot 100 strike 100 expiry 1 rate 0.05 into iv_val
historical value at risk of [-0.05, -0.02, 0.01, 0.03, 0.04] at confidence 0.80 into var_val
"""
    env = execute(source)
    assert len(env["atr_vals"]) == 5
    assert len(env["keltner_res"]["middle"]) == 5
    assert len(env["wr_vals"]) == 5
    assert len(env["mfi_vals"]) == 5
    assert env["reb_trades"]["AAPL"] == -1000.0
    assert env["reb_trades"]["GOOG"] == 1000.0
    assert env["twap_val"] > 10.0
    assert len(env["donch_res"]["upper"]) == 5
    assert env["ir_val"] > 0
    assert len(env["dd_res"]) == 5
    assert env["dd_res"][2] < 0  # 110 is drawdown from 120
    assert 0.18 < env["iv_val"] < 0.22  # Recovers ~0.20
    assert env["var_val"] > 0
