"""Unit and integration tests for Data aggregation and DSA benchmark export parity."""

import pytest
from doomscript.compiler.engine import execute, export_to_python


def test_data_aggregation_count_and_named_columns_export_parity():
    source = """use data

sales = [
    {"region": "North", "amount": 100},
    {"region": "North", "amount": 150},
    {"region": "South", "amount": 200}
]

pipeline "summary_pipe":
    read sales into sales_df
    group sales_df by region
    calculate total_rev as sum of amount
    calculate count_sales as count

summary = summary_pipe
"""
    # 1. Direct Execution
    env_direct = execute(source)
    assert "summary" in env_direct
    rows_direct = env_direct["summary"]
    assert len(rows_direct) == 2
    north_direct = next(r for r in rows_direct if r["region"] == "North")
    assert north_direct["total_rev"] == 250
    assert north_direct["count_sales"] == 2

    # 2. Python Export Execution
    exported_code = export_to_python(source)
    env_export = {}
    exec(exported_code, env_export)
    assert "summary" in env_export
    rows_export = env_export["summary"]
    assert len(rows_export) == 2
    north_export = next(r for r in rows_export if r["region"] == "North")
    assert north_export["total_rev"] == 250
    assert north_export["count_sales"] == 2


def test_dsa_benchmark_export_executes_microbenchmark():
    source = """use dsa

to fast_fn with arr:
    return len(arr)

benchmark fast_fn:
    input_sizes: [100, 500, 1000]
    repeat: 2
    measure: execution_time
    generator: sorted_integers
"""
    # 1. Direct Execution
    env_direct = execute(source)
    assert "fast_fn_benchmark" in env_direct
    assert "best_fit" in env_direct["fast_fn_benchmark"]
    assert "confidence_r2" in env_direct["fast_fn_benchmark"]

    # 2. Python Export Execution
    exported_code = export_to_python(source)
    env_export = {}
    exec(exported_code, env_export)
    assert "fast_fn_benchmark" in env_export
    bench_export = env_export["fast_fn_benchmark"]
    assert "best_fit" in bench_export
    assert "confidence_r2" in bench_export
    assert "timings" in bench_export
    assert len(bench_export["timings"]) == 3
