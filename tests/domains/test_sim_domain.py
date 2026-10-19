"""Unit and integration tests for the Simulation & Optimization domain pack (use sim)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.sim.spec import SimulationSpec, OptimizationSpec


def test_sim_spec_validation():
    spec = SimulationSpec(name="bank_queue", duration=1000, servers=2)
    assert len(spec.validate()) == 0

    bad_spec = SimulationSpec(name="", duration=-10, servers=0)
    assert len(bad_spec.validate()) == 3


def test_sim_queue_system_execution():
    source = """use sim

simulate queue_system:
    arrivals: poisson with rate 12
    service: exponential with rate 15
    duration: 300 events
    servers: 1

summarize waiting_time into wait_summary
inspect simulation queue_system into sim_info
"""
    env = execute(source)
    assert "queue_system" in env
    qs = env["queue_system"]
    assert qs["total_events"] == 300
    assert 0.0 < qs["server_utilization"] <= 1.0
    assert len(qs["waiting_time"]) == 300

    assert "wait_summary" in env
    summary = env["wait_summary"]
    assert summary["count"] == 300
    assert "mean" in summary
    assert "p95" in summary

    assert "sim_info" in env
    assert "waiting_time" in env["sim_info"]


def test_sim_sampling_and_nelder_mead_optimization():
    source = """use sim

sample exponential with rate 5.0 count 200 into exp_samples
summarize exp_samples into exp_summary

to loss_fn with pt:
    return (pt[0] - 3.0) ** 2 + (pt[1] - 4.0) ** 2

optimize loss_fn starting at [0.0, 0.0] into opt_res
"""
    env = execute(source)
    assert "exp_samples" in env
    assert len(env["exp_samples"]) == 200
    assert "mean" in env["exp_summary"]

    assert "opt_res" in env
    opt = env["opt_res"]
    assert opt["converged"] is True
    pt = opt["optimal_point"]
    assert abs(pt[0] - 3.0) < 0.1
    assert abs(pt[1] - 4.0) < 0.1
    assert opt["optimal_value"] < 0.05


def test_sim_ast_export():
    source = """use sim

simulate q:
    arrivals: poisson with rate 10
    service: exponential with rate 12
    duration: 100
"""
    py_code = export_to_python(source)
    assert "q" in py_code
    assert "waiting_time" in py_code
