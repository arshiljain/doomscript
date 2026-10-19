"""Tests for advanced simulation capabilities: seed control, uncertainty quantification, multi-trial experiments, and parameter sweeps."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.sim.runtime import summarize_uncertainty


def test_summarize_uncertainty_pure_python():
    # Known dataset
    data = [10.0, 12.0, 11.0, 13.0, 14.0]
    unc = summarize_uncertainty(data)
    assert unc["count"] == 5
    assert unc["mean"] == 12.0
    assert unc["std_dev"] > 0
    assert unc["std_error"] > 0
    assert unc["ci_95"][0] < unc["mean"] < unc["ci_95"][1]
    assert unc["margin_of_error"] > 0
    assert abs(unc["ci_95"][1] - (unc["mean"] + unc["margin_of_error"])) < 1e-4


def test_simulation_reproducible_seed():
    source1 = """use sim

simulate reproducible_q:
    arrivals: poisson with rate 10
    service: exponential with rate 12
    duration: 150 events
    seed: 12345
"""
    source2 = """use sim

simulate reproducible_q:
    arrivals: poisson with rate 10
    service: exponential with rate 12
    duration: 150 events
    seed: 12345
"""
    env1 = execute(source1)
    env2 = execute(source2)

    assert env1["reproducible_q"]["waiting_time"] == env2["reproducible_q"]["waiting_time"]
    assert env1["reproducible_q"]["server_utilization"] == env2["reproducible_q"]["server_utilization"]


def test_simulation_uncertainty_and_trials():
    source = """use sim

simulate hospital_queue:
    arrivals: poisson with rate 8
    service: exponential with rate 10
    duration: 100 events
    servers: 1
    seed: 42

summarize uncertainty of waiting_time into wait_unc
run 5 trials of hospital_queue into hospital_trials
"""
    env = execute(source)
    assert "wait_unc" in env
    unc = env["wait_unc"]
    assert unc["count"] == 100
    assert "mean" in unc
    assert "ci_95" in unc
    assert len(unc["ci_95"]) == 2

    assert "hospital_trials" in env
    trials = env["hospital_trials"]
    assert trials["trials"] == 5
    assert len(trials["runs"]) == 5
    assert "uncertainty" in trials
    assert "waiting_time" in trials["uncertainty"]
    assert trials["mean_waiting_time"] >= 0.0


def test_simulation_parameter_sweep():
    source = """use sim

simulate bank:
    arrivals: poisson with rate 15
    service: exponential with rate 10
    duration: 80 events
    servers: 1

sweep servers over [1, 2, 3] for bank into server_sweep
"""
    env = execute(source)
    assert "server_sweep" in env
    sweep = env["server_sweep"]
    assert len(sweep) == 3
    # With 1 server and arrival 15 > service 10, utilization is very high; with 2 or 3 servers, utilization drops
    assert sweep[0]["value"] == 1
    assert sweep[1]["value"] == 2
    assert sweep[2]["value"] == 3
    assert sweep[0]["mean_utilization"] >= sweep[2]["mean_utilization"]
