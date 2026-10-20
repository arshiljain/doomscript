"""Integration and verification test suite for Deepened Cluster VI:
Databases, Data Engineering, Machine Learning, and Metrics domains in DoomScript.

Validates pure Python algorithms and native spoken-English .doom code execution.
"""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# DATABASE (DB) B+ TREE TESTS
# ==============================================================================

def test_db_bplus_tree_index_and_range_scan():
    """Validates B+ Tree insertion, node splitting, search, and range scanning."""
    code = """
use db
create bplus tree index with order 4 into bpt
insert key 10 with value "ten" into bplus tree bpt
insert key 20 with value "twenty" into bplus tree bpt
insert key 30 with value "thirty" into bplus tree bpt
insert key 40 with value "forty" into bplus tree bpt
insert key 50 with value "fifty" into bplus tree bpt

search key 30 in bplus tree bpt into val30
assert val30 equals "thirty"

scan range from 15 to 45 in bplus tree bpt into scanned_items
assert length of scanned_items equals 3
"""
    env = execute(code)
    assert env["val30"] == "thirty"
    items = env["scanned_items"]
    assert len(items) == 3
    assert [item["key"] for item in items] == [20, 30, 40]
    assert [item["value"] for item in items] == ["twenty", "thirty", "forty"]


# ==============================================================================
# DATA STREAMING & SKETCH TESTS
# ==============================================================================

def test_data_hyperloglog_cardinality():
    """Validates HyperLogLog distinct items cardinality estimation."""
    code = """
use data
create hyperloglog with precision 10 into hll
add items ["user_1", "user_2", "user_3", "user_1", "user_4", "user_2"] to hyperloglog hll
estimate cardinality of hyperloglog hll into card_est
assert card_est is over 2
assert card_est is under 6
"""
    env = execute(code)
    assert 3 <= env["card_est"] <= 5


def test_data_count_min_sketch():
    """Validates Count-Min Sketch frequency estimation for streaming tokens."""
    code = """
use data
create count min sketch with width 500 and depth 5 into cms
update count min sketch cms with items ["apple", "banana", "apple", "cherry", "apple", "banana"]
estimate frequency of item "apple" in count min sketch cms into apple_count
estimate frequency of item "cherry" in count min sketch cms into cherry_count
assert apple_count equals 3
assert cherry_count equals 1
"""
    env = execute(code)
    assert env["apple_count"] == 3
    assert env["cherry_count"] == 1


def test_data_reservoir_sampling():
    """Validates uniform random reservoir sampling from data streams."""
    code = """
use data
set stream_data to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
sample 4 items from stream stream_data using reservoir sampling into sampled_items
assert length of sampled_items equals 4
"""
    env = execute(code)
    sample = env["sampled_items"]
    assert len(sample) == 4
    for val in sample:
        assert val in range(1, 13)


# ==============================================================================
# MACHINE LEARNING (ML) TESTS
# ==============================================================================

def test_ml_gaussian_mixture_model_em():
    """Validates GMM Expectation-Maximization clustering and convergence."""
    code = """
use ml
set data_pts to [[1.0, 1.1], [1.2, 0.9], [0.9, 1.0], [8.0, 8.1], [8.2, 7.9], [7.9, 8.0]]
fit gaussian mixture model with 2 components on data_pts into gmm_res
assert gmm_res's num_components equals 2
assert gmm_res's converged is true

predict gmm cluster for [[1.1, 1.0], [8.1, 8.0]] using gmm_res into cluster_preds
assert cluster_preds[0] does not equal cluster_preds[1]
"""
    env = execute(code)
    res = env["gmm_res"]
    preds = env["cluster_preds"]
    assert res.num_components == 2
    assert res.converged is True
    assert preds[0] != preds[1]


def test_ml_pca_dimensionality_reduction():
    """Validates Principal Component Analysis projection."""
    code = """
use ml
set high_dim to [[2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0], [2.3, 2.7]]
compute pca with 1 components on high_dim into pca_model
assert pca_model's n_components equals 1

project data high_dim with pca pca_model into projected_dim
assert length of projected_dim equals 6
"""
    env = execute(code)
    pca = env["pca_model"]
    proj = env["projected_dim"]
    assert pca.n_components == 1
    assert len(proj) == 6
    assert len(proj[0]) == 1


# ==============================================================================
# METRICS & STATISTICAL INFERENCE TESTS
# ==============================================================================

def test_metrics_mann_whitney_u_test():
    """Validates two-sample non-parametric Mann-Whitney U test."""
    code = """
use metrics
set sample_a to [10, 12, 11, 14, 13, 15, 12]
set sample_b to [25, 28, 27, 26, 30, 29, 31]
calculate mann whitney u test between sample_a and sample_b into mwu_out
assert mwu_out's significant_05 is true
assert mwu_out's p_value is under 0.05
assert mwu_out's n1 equals 7
assert mwu_out's n2 equals 7
"""
    env = execute(code)
    mwu = env["mwu_out"]
    assert mwu.significant_05 is True
    assert mwu.p_value < 0.05
    assert mwu.n1 == 7
    assert mwu.n2 == 7


def test_metrics_kolmogorov_smirnov_2samp():
    """Validates two-sample Kolmogorov-Smirnov test."""
    code = """
use metrics
set dist_a to [1, 2, 3, 4, 5, 6, 7]
set dist_b to [20, 21, 22, 23, 24, 25, 26]
calculate kolmogorov smirnov test between dist_a and dist_b into ks_out
assert ks_out's d_statistic equals 1.0
assert ks_out's significant_05 is true
assert ks_out's p_value is under 0.05
"""
    env = execute(code)
    ks = env["ks_out"]
    assert ks.d_statistic == 1.0
    assert ks.significant_05 is True
    assert ks.p_value < 0.05


def test_metrics_kernel_density_estimation():
    """Validates 1D non-parametric Kernel Density Estimation (KDE)."""
    code = """
use metrics
set sample_pts to [1.0, 1.5, 2.0, 2.2, 7.8, 8.0, 8.5]
compute kernel density estimation for sample_pts with bandwidth 0.8 into kde_est
assert kde_est's n_samples equals 7

evaluate kde kde_est at points [1.8, 8.1, 15.0] into densities
assert densities[0] is over 0.05
assert densities[1] is over 0.05
assert densities[2] is under 0.01
"""
    env = execute(code)
    kde = env["kde_est"]
    d = env["densities"]
    assert kde.n_samples == 7
    assert d[0] > 0.05
    assert d[1] > 0.05
    assert d[2] < 0.01
