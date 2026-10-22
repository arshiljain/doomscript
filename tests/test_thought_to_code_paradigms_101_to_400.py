"""
Test Suite for DoomScript Thought-to-Code Paradigms (Paradigms 101-400).
Tests domain routing, zero-import execution, and semantic lowering across all 15 cognitive clusters.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute


def test_cluster_11_agentic_swarms():
    code = textwrap.dedent("""
    domain agent
    agent Auditor with role "Security Engineer", capabilities ["code_audit"] into sec_agent
    swarm debate "Zero Trust Architecture" with [sec_agent] into debate_out
    decompose goal "Deploy Microservice" into subtasks using sec_agent into tasks
    agent sec_agent reflects on "draft code" until quality >= 0.85 into refined
    swarm vote on proposal "Enforce MFA" using majority into vote_res
    """).strip()
    env = execute(code)
    assert env["sec_agent"]["name"] == "Auditor"
    assert "Zero Trust Architecture" in env["debate_out"]["consensus"]
    assert len(env["tasks"]) == 3
    assert env["refined"]["quality_score"] >= 0.85
    assert env["vote_res"]["approved"] is True


def test_cluster_12_financial_calculus():
    code = textwrap.dedent("""
    domain finance
    compound interest on 5000 at 7% over 5 years into interest_res
    amortize loan 100000 at 5% over 15 years into loan_res
    net present value of cashflows [-1000, 300, 400, 500] at discount 10% into npv_res
    sharpe ratio of returns [0.05, 0.08, -0.02, 0.12] with risk_free 0.02 into sharpe_res
    """).strip()
    env = execute(code)
    assert env["interest_res"] == 7012.76
    assert env["loan_res"]["monthly_payment"] > 0
    assert isinstance(env["npv_res"], float)
    assert isinstance(env["sharpe_res"], float)


def test_cluster_13_data_cleaning():
    code = textwrap.dedent("""
    domain data
    left join [{id: 1, name: "Alice"}, {id: 2, name: "Bob"}] and [{id: 1, dept: "Eng"}] on "id" into merged_users
    """).strip()
    env = execute(code)
    assert len(env["merged_users"]) == 2
    assert env["merged_users"][0].get("dept") == "Eng"
    assert env["merged_users"][1].get("dept") is None


def test_cluster_14_spatial_geometry():
    code = textwrap.dedent("""
    domain math3d
    euclidean distance between point [0, 0] and point [6, 8] into d
    dot product of vector [1, 2, 3] and vector [4, 5, 6] into dot_res
    """).strip()
    env = execute(code)
    assert env["d"] == 10.0
    assert env["dot_res"] == 32.0


def test_cluster_15_graph_topology():
    code = textwrap.dedent("""
    domain graph
    shortest path dijkstra in {"A": {"B": 1, "C": 4}, "B": {"C": 2}} from "A" to "C" into route
    """).strip()
    env = execute(code)
    route = env["route"]
    assert route is not None
    assert route["path"] == ["A", "B", "C"]
    assert route["cost"] == 3.0


def test_cluster_17_machine_learning():
    code = textwrap.dedent("""
    domain ml
    cosine similarity between [1.0, 0.0] and [1.0, 0.0] into sim_perfect
    cosine similarity between [1.0, 0.0] and [0.0, 1.0] into sim_ortho
    """).strip()
    env = execute(code)
    assert env["sim_perfect"] == 1.0
    assert env["sim_ortho"] == 0.0


def test_cluster_18_cryptography():
    code = textwrap.dedent("""
    domain sec
    hash sha256 "doomscript" into hash_val
    """).strip()
    env = execute(code)
    assert len(env["hash_val"]) == 64


def test_cluster_21_chemistry():
    code = textwrap.dedent("""
    domain chem
    molecular mass of "H2O" into water_mass
    balance equation "H2 + O2 -> H2O" into balanced_rxn
    molarity of 1.0 moles in 2.0 liters into molar_conc
    pH from hydronium 1.0e-7 into ph_val
    """).strip()
    env = execute(code)
    assert env["water_mass"] == 18.015
    assert env["balanced_rxn"] == "2 H2 + O2 -> 2 H2O"
    assert env["molar_conc"] == 0.5
    assert env["ph_val"] == 7.0


def test_cluster_22_bioinformatics():
    code = textwrap.dedent("""
    domain bio
    transcribe dna "ATGCGATCG" into rna
    translate mrna "AUGUUCUCGUAA" into protein
    gc content of "GCGC" into gc
    """).strip()
    env = execute(code)
    assert env["rna"] == "AUGCGAUCG"
    assert env["protein"] == "MFS"
    assert env["gc"] == 1.0


def test_cluster_23_robotics():
    code = textwrap.dedent("""
    domain robotics
    pid update with setpoint 50.0, measurement 45.0, dt 0.1 into effort
    """).strip()
    env = execute(code)
    assert isinstance(env["effort"], float)


def test_cluster_24_ui_design_tokens():
    code = textwrap.dedent("""
    domain web
    bind design token "font.heading" to "Inter, sans-serif" into font_token
    verify contrast between "#000000" and "#FFFFFF" meets "WCAG_AA" into contrast_res
    """).strip()
    env = execute(code)
    assert env["font_token"]["css_variable"] == "--ds-font-heading"
    assert env["contrast_res"]["meets_aa"] is True


def test_cluster_25_office_presentation():
    code = textwrap.dedent("""
    domain office
    compile markdown presentation to slides with theme "Modern Light" into deck
    format currency 54321.00 for locale "en_US" into usd
    """).strip()
    env = execute(code)
    assert env["deck"]["theme"] == "Modern Light"
    assert env["usd"] == "$54,321.00"


def test_zero_import_auto_routing():
    code = textwrap.dedent("""
    balance equation "H2 + O2 -> H2O" into auto_rxn
    molecular mass of "CH4" into auto_methane
    compound interest on 1000 at 10% over 1 years into auto_compound
    """).strip()
    env = execute(code)
    assert env["auto_rxn"] == "2 H2 + O2 -> 2 H2O"
    assert env["auto_methane"] == 16.043
    assert env["auto_compound"] == 1100.0
