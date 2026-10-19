"""Test Suite for Phase 1 of 120 Algorithmic & Spoken English Operations.
Covers:
- Batch 1: Advanced DSA & Trees (8 operations)
- Batch 2: Data Manipulation & Tables (8 operations)
- Batch 3: Math & Statistics (7 operations)
Total: 23 operations.
"""

import pytest
from doomscript.compiler.engine import execute


def test_batch1_segment_tree():
    """Batch 1: Segment Tree create, query range sum, update point."""
    source = """use dsa

set arr to [1, 3, 5, 7, 9, 11]
create segment tree from arr into st
query range sum in segment tree st from 1 to 3 into sum_1_3

update point in segment tree st at 1 with 10
query range sum in segment tree st from 1 to 3 into sum_1_3_updated
"""
    env = execute(source)
    assert env["sum_1_3"] == 15  # 3 + 5 + 7
    assert env["sum_1_3_updated"] == 22  # 10 + 5 + 7


def test_batch1_fenwick_tree():
    """Batch 1: Fenwick Tree (BIT) create, prefix sum, point update."""
    source = """use dsa

set arr to [2, 4, 6, 8, 10]
create fenwick tree from arr into bit
prefix sum in fenwick tree bit up to 2 into sum_0_2

update fenwick tree bit at 1 by 5
prefix sum in fenwick tree bit up to 2 into sum_0_2_updated
"""
    env = execute(source)
    assert env["sum_0_2"] == 12  # 2 + 4 + 6
    assert env["sum_0_2_updated"] == 17  # 12 + 5


def test_batch1_reservoir_sample_and_lcs():
    """Batch 1: Reservoir sampling and Longest Common Subsequence."""
    source = """use dsa

set stream to [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
sample 3 items from stream stream using reservoir into sample_items

longest common subsequence of "ABCDE" and "ACE" into common_sub
"""
    env = execute(source)
    assert len(env["sample_items"]) == 3
    assert all(x in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] for x in env["sample_items"])
    assert env["common_sub"] == "ACE"


def test_batch2_data_tabular_operations():
    """Batch 2: Data Manipulation (pivot, melt, fill missing, drop duplicates, stratified sample, rolling mean, explode, merge)."""
    source = """use data

set raw_sales to [
    {"region": "North", "rep": "Alice", "sales": 100},
    {"region": "North", "rep": "Bob", "sales": 150},
    {"region": "South", "rep": "Alice", "sales": 200},
    {"region": "South", "rep": "Bob", "sales": 50}
]
pivot table raw_sales with index "region", columns "rep", values "sales", agg "sum" into pivoted

set wide_table to [
    {"product": "Apples", "q1": 10, "q2": 15},
    {"product": "Bananas", "q1": 20, "q2": 25}
]
melt table wide_table with id_vars ["product"], value_vars ["q1", "q2"] into melted

set dirty_data to [
    {"id": 1, "score": 80},
    {"id": 2, "score": None},
    {"id": 3, "score": 90}
]
fill missing values in dirty_data for column "score" with "mean" into cleaned_scores

set dups_data to [
    {"name": "Alice", "dept": "HR"},
    {"name": "Bob", "dept": "Eng"},
    {"name": "Alice", "dept": "HR"}
]
drop duplicate rows in dups_data by subset ["name", "dept"] into deduped

set strat_data to [
    {"dept": "Eng", "emp": "A"},
    {"dept": "Eng", "emp": "B"},
    {"dept": "HR", "emp": "C"},
    {"dept": "HR", "emp": "D"}
]
sample 1 rows from strat_data stratified by "dept" into sampled_strat

set ts_data to [
    {"day": 1, "val": 10},
    {"day": 2, "val": 20},
    {"day": 3, "val": 30},
    {"day": 4, "val": 40}
]
rolling mean in ts_data for "val" with window 2 into ts_rolling

set nested_data to [
    {"order_id": 101, "items": ["apple", "pear"]},
    {"order_id": 102, "items": ["banana"]}
]
explode column "items" in nested_data into exploded_items

set users to [
    {"user_id": 1, "name": "Alice"},
    {"user_id": 2, "name": "Bob"}
]
set orders to [
    {"user_id": 1, "amount": 500},
    {"user_id": 2, "amount": 250}
]
merge tables users and orders on "user_id" with kind "inner" into merged_orders
"""
    env = execute(source)
    # 1. Pivot
    assert len(env["pivoted"]) == 2
    north = next(r for r in env["pivoted"] if r["region"] == "North")
    assert north["Alice"] == 100.0 and north["Bob"] == 150.0

    # 2. Melt
    assert len(env["melted"]) == 4

    # 3. Fill missing
    assert env["cleaned_scores"][1]["score"] == 85.0  # (80 + 90) / 2

    # 4. Drop duplicates
    assert len(env["deduped"]) == 2

    # 5. Stratified sample
    assert len(env["sampled_strat"]) == 2

    # 6. Rolling mean
    assert env["ts_rolling"][1]["val_rolling_mean"] == 15.0  # (10 + 20) / 2
    assert env["ts_rolling"][2]["val_rolling_mean"] == 25.0  # (20 + 30) / 2

    # 7. Explode column
    assert len(env["exploded_items"]) == 3
    assert env["exploded_items"][0]["items"] == "apple"
    assert env["exploded_items"][1]["items"] == "pear"

    # 8. Merge tables
    assert len(env["merged_orders"]) == 2
    assert env["merged_orders"][0]["name"] == "Alice"
    assert env["merged_orders"][0]["amount"] == 500


def test_batch3_math_statistics():
    """Batch 3: Math & Statistics (correlation, linear regression, moving median, percentile, z-score, min-max scale, empirical cdf)."""
    source = """use dsa

set x_vals to [1, 2, 3, 4, 5]
set y_vals to [2, 4, 6, 8, 10]
correlation between x_vals and y_vals into corr

linear regression of y_vals on x_vals into regression_res

set noise_series to [1, 5, 2, 8, 3, 9, 4]
moving median of noise_series with window 3 into medians

set distribution to [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
percentile 50 of distribution into p50
percentile 90 of distribution into p90

set raw_features to [10, 20, 30, 40, 50]
z-score normalize raw_features into z_scores
min-max scale raw_features into scaled

empirical cdf of distribution at 50 into ecdf_50
"""
    env = execute(source)
    # Correlation
    assert env["corr"] == 1.0

    # Linear regression
    assert env["regression_res"]["slope"] == 2.0
    assert env["regression_res"]["intercept"] == 0.0
    assert env["regression_res"]["r2"] == 1.0

    # Moving median
    assert env["medians"] == [2.0, 5.0, 3.0, 8.0, 4.0]

    # Percentiles
    assert env["p50"] == 55.0
    assert env["p90"] == 91.0

    # Z-scores
    assert env["z_scores"][2] == 0.0  # 30 is the mean of [10..50]

    # Min-max scale
    assert env["scaled"][0] == 0.0
    assert env["scaled"][-1] == 1.0

    # Empirical CDF
    assert env["ecdf_50"] == 0.5
