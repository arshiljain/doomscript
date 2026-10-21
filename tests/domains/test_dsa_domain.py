"""Unit and integration tests for Testing & Algorithm Analysis (use dsa)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.dsa.spec import BenchmarkSpec


def test_dsa_spec_validation():
    spec = BenchmarkSpec(fn_name="sort_algo", input_sizes=[100, 200], repeat=3)
    assert len(spec.validate()) == 0

    bad_spec = BenchmarkSpec(fn_name="", input_sizes=[], repeat=-1)
    assert len(bad_spec.validate()) == 3


def test_dsa_benchmark_and_empirical_complexity():
    source = """use dsa

to linear_scan with arr:
    total = 0
    for x in arr:
        total = total + x
    return total

benchmark linear_scan:
    input_sizes: [2000, 5000, 10000, 20000]
    repeat: 3
    measure: execution_time, memory
    generator: sorted_integers

complexity of linear_scan into scan_complexity
"""
    env = execute(source)
    assert "linear_scan_benchmark" in env
    bench = env["linear_scan_benchmark"]
    assert "best_fit" in bench
    assert bench["best_fit"] in ("O(n)", "O(n log n)", "O(log n)")
    assert bench["confidence_r2"] > 0.7
    assert len(bench["timings"]) == 4

    assert "scan_complexity" in env
    comp = env["scan_complexity"]
    assert "best_fit" in comp


def test_dsa_memory_profiling():
    source = """use dsa

to build_matrix with n:
    return [[i * j for j in [1, 2, 3, 4, 5]] for i in [1, 2, 3, 4, 5]]

profile memory of build_matrix with 5 into mem_info
"""
    env = execute(source)
    assert "mem_info" in env
    mem = env["mem_info"]
    assert "peak_memory_bytes" in mem
    assert "execution_time_seconds" in mem
    assert mem["result"] is not None


def test_dsa_ast_export():
    source = """use dsa

benchmark binary_search:
    input_sizes: [100, 1000]
    repeat: 5
"""
    py_code = export_to_python(source)
    assert "binary_search" in py_code
    assert "input_sizes" in py_code
