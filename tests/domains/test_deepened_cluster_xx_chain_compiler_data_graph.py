"""Comprehensive unit tests for Deepened Cluster XX:
Chain, Compiler, Data, and Graph domains in DoomScript.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute

# Domain runtime classes & algorithms
from doomscript.domains.chain.runtime import (
    EVMBytecodeInterpreterStackMachine,
    ThresholdSignatureSchemeShamir,
    chain_evm_execute,
    chain_threshold_split,
    chain_threshold_reconstruct,
    chain_threshold_aggregate_sign,
)
from doomscript.domains.compiler.runtime import (
    SparseConditionalConstantPropagationSCCP,
    EarleyChartParser,
    compiler_sccp_optimize,
    compiler_earley_parse,
)
from doomscript.domains.data.runtime import (
    TDigestQuantileApproximator,
    RoaringBitmapPure,
    data_tdigest_create,
    data_tdigest_add,
    data_tdigest_quantile,
    data_tdigest_cdf,
    data_roaring_create,
    data_roaring_add,
    data_roaring_contains,
    data_roaring_operation,
    data_roaring_stats,
)
from doomscript.domains.graph.runtime import (
    BronKerboschMaximalCliques,
    LengauerTarjanDominatorTree,
    graph_bron_kerbosch_degeneracy_cliques,
    graph_lengauer_tarjan_dominators,
)


# ==============================================================================
# CHAIN DOMAIN TESTS
# ==============================================================================


def test_chain_evm_arithmetic_and_memory():
    # Bytecode: PUSH1 0x2A (42), PUSH1 0x08 (8), ADD (50), PUSH1 0x00, MSTORE, PUSH1 0x20, PUSH1 0x00, RETURN
    # 60 2a 60 08 01 60 00 52 60 20 60 00 f3
    bytecode = "602a60080160005260206000f3"
    vm = EVMBytecodeInterpreterStackMachine(bytecode)
    res = vm.run()

    assert res["status"] == "SUCCESS"
    assert res["gas_used"] > 0
    # Returned 32-byte word with 50 (0x32) at the end
    ret = res["return_data_hex"]
    assert ret.endswith("32")
    assert len(ret) == 2 + 64


def test_chain_evm_storage_and_jumps():
    # Bytecode:
    # PUSH1 0x01 (cond)
    # PUSH1 0x0A (target: pc=10)
    # JUMPI
    # PUSH1 0xFF PUSH1 0x00 SSTORE (skipped)
    # JUMPDEST (pc=10)
    # PUSH1 0x77 PUSH1 0x01 SSTORE
    # STOP
    bytecode = "6001600a5760ff6000555b607760015500"
    vm = EVMBytecodeInterpreterStackMachine(bytecode)
    res = vm.run()

    assert res["status"] == "SUCCESS"
    assert "0x0" not in res["storage"]
    assert res["storage"].get("0x1") == "0x77"


def test_chain_threshold_shamir_secret_sharing():
    secret = 888999111222333444555
    res = ThresholdSignatureSchemeShamir.split_secret(secret, threshold=3, total_shares=5)
    shares = res["shares"]
    assert len(shares) == 5

    # Reconstruct from shares (1, 3, 5)
    subset_a = [shares[0], shares[2], shares[4]]
    rec_a = ThresholdSignatureSchemeShamir.reconstruct_secret(subset_a, threshold=3)
    assert rec_a == secret

    # Reconstruct from shares (2, 3, 4)
    subset_b = [shares[1], shares[2], shares[3]]
    rec_b = ThresholdSignatureSchemeShamir.reconstruct_secret(subset_b, threshold=3)
    assert rec_b == secret

    # Sign message
    sig_res = ThresholdSignatureSchemeShamir.threshold_sign("ConsensusBlock#42", subset_a, threshold=3)
    assert sig_res["valid"] is True


def test_chain_spoken_english():
    script = textwrap.dedent("""
    use chain
    execute evm bytecode "600560030160005260206000f3" with calldata "" with gas 50000 into evm_res
    split secret 1234567 into 5 shares with threshold 3 into share_pack
    reconstruct secret from shares share_pack's shares with threshold 3 into restored_key
    threshold sign message "TestTx" with shares share_pack's shares and threshold 3 into sig_rec
    """).strip()
    env = execute(script)
    assert env["evm_res"]["status"] == "SUCCESS"
    assert env["restored_key"] == 1234567
    assert env["sig_rec"]["valid"] is True


# ==============================================================================
# COMPILER DOMAIN TESTS
# ==============================================================================


def test_compiler_sccp_optimization():
    cfg = {
        "entry": "B0",
        "blocks": {
            "B0": {
                "instructions": [
                    {"dest": "a", "op": "const", "value": 10},
                    {"dest": "b", "op": "const", "value": 20},
                    {"dest": "c", "op": "add", "args": ["a", "b"]},
                    {"dest": "cond", "op": "lt", "args": ["a", "b"]},
                    {"op": "br_cond", "cond": "cond", "true_target": "B1", "false_target": "B2"},
                ],
                "successors": ["B1", "B2"],
            },
            "B1": {
                "instructions": [
                    {"dest": "d", "op": "mul", "args": ["c", 2]},
                    {"op": "jump", "target": "B3"},
                ],
                "successors": ["B3"],
            },
            "B2": {
                "instructions": [
                    {"dest": "e", "op": "const", "value": 999},
                    {"op": "jump", "target": "B3"},
                ],
                "successors": ["B3"],
            },
            "B3": {
                "instructions": [
                    {"dest": "res", "op": "phi", "incoming": {"B1": "d", "B2": "e"}},
                ],
                "successors": [],
            },
        },
    }

    res = SparseConditionalConstantPropagationSCCP.optimize(cfg)
    assert res["constants"]["a"] == 10
    assert res["constants"]["b"] == 20
    assert res["constants"]["c"] == 30
    assert res["constants"]["cond"] is True
    assert res["constants"]["d"] == 60
    assert res["constants"]["res"] == 60

    assert "B2" in res["dead_blocks"]
    assert "B1" in res["executable_blocks"]


def test_compiler_earley_parser():
    grammar = {
        "E": [["E", "+", "T"], ["T"]],
        "T": [["T", "*", "F"], ["F"]],
        "F": [["(", "E", ")"], ["id"]],
    }
    tokens = ["id", "+", "id", "*", "id"]
    res = EarleyChartParser.parse(grammar, "E", tokens)
    assert res["accepted"] is True
    assert res["accepted_derivation_count"] >= 1
    assert res["tokens_length"] == 5

    res_bad = EarleyChartParser.parse(grammar, "E", ["id", "+", "*"])
    assert res_bad["accepted"] is False


def test_compiler_spoken_english():
    script = textwrap.dedent("""
    use compiler
    set test_ir to {"entry": "B0", "blocks": {"B0": {"instructions": [{"dest": "x", "op": "const", "value": 7}, {"dest": "y", "op": "mul", "args": ["x", 6]}], "successors": []}}}
    optimize ssa ir test_ir with sccp into opt_res

    set expr_grammar to {"S": [["NP", "VP"]], "NP": [["the", "cat"]], "VP": [["sleeps"]]}
    earley parse ["the", "cat", "sleeps"] with grammar expr_grammar starting at "S" into earley_res
    """).strip()
    env = execute(script)
    assert env["opt_res"]["constants"]["y"] == 42
    assert env["earley_res"]["accepted"] is True


# ==============================================================================
# DATA DOMAIN TESTS
# ==============================================================================


def test_data_tdigest_quantiles():
    td = TDigestQuantileApproximator(delta=100.0)
    data = [float(x) for x in range(1, 1001)]
    td.add_batch(data)

    p50 = td.quantile(0.50)
    p90 = td.quantile(0.90)
    p99 = td.quantile(0.99)

    assert 480.0 <= p50 <= 520.0
    assert 880.0 <= p90 <= 920.0
    assert 980.0 <= p99 <= 1000.0

    cdf_500 = td.cdf(500.0)
    assert 0.47 <= cdf_500 <= 0.53


def test_data_roaring_bitmap_operations():
    rb1 = RoaringBitmapPure([10, 20, 30, 70000, 150000])
    rb2 = RoaringBitmapPure([20, 30, 40, 70000, 200000])

    assert rb1.cardinality() == 5
    assert rb2.cardinality() == 5
    assert rb1.contains(70000) is True
    assert rb1.contains(40) is False

    union_rb = rb1.union(rb2)
    assert union_rb.cardinality() == 7

    inter_rb = rb1.intersection(rb2)
    assert inter_rb.cardinality() == 3

    diff_rb = rb1.difference(rb2)
    assert diff_rb.cardinality() == 2


def test_data_spoken_english():
    script = textwrap.dedent("""
    use data
    create tdigest with compression 100.0 into my_tdigest
    add values [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] to tdigest my_tdigest into td_summary
    estimate quantile 0.5 of tdigest my_tdigest into median_val

    create roaring bitmap from [1, 2, 3, 5000, 100000] into bm_a
    create roaring bitmap from [3, 4, 5, 5000, 200000] into bm_b
    roaring union between bm_a and bm_b into bm_union
    roaring intersection between bm_a and bm_b into bm_inter
    check if roaring bitmap bm_union contains 100000 into has_val
    """).strip()
    env = execute(script)
    assert 45.0 <= env["median_val"] <= 65.0
    assert env["bm_union"]["cardinality"] == 8
    assert env["bm_inter"]["cardinality"] == 2
    assert env["has_val"] is True


# ==============================================================================
# GRAPH DOMAIN TESTS
# ==============================================================================


def test_graph_bron_kerbosch_cliques():
    edges = [("A", "B"), ("B", "C"), ("A", "C"), ("C", "D"), ("E", "F")]
    res = BronKerboschMaximalCliques.compute(edges)

    assert res["clique_count"] == 3
    assert res["maximum_clique_size"] == 3
    assert set(res["maximum_clique"]) == {"A", "B", "C"}
    assert res["degeneracy"] >= 1


def test_graph_lengauer_tarjan_dominators():
    edges = [("R", "A"), ("R", "B"), ("A", "C"), ("B", "C"), ("C", "D")]
    res = LengauerTarjanDominatorTree.compute("R", edges)

    idom = res["idom"]
    assert idom["R"] is None
    assert idom["A"] == "R"
    assert idom["B"] == "R"
    assert idom["C"] == "R"
    assert idom["D"] == "C"

    assert "C" in res["dominance_frontiers"]["A"]
    assert "C" in res["dominance_frontiers"]["B"]


def test_graph_spoken_english():
    script = textwrap.dedent("""
    use graph
    set g_edges to [["1", "2"], ["2", "3"], ["1", "3"], ["3", "4"]]
    find maximal cliques in graph g_edges into clique_res

    set flow_edges to [["Entry", "B1"], ["Entry", "B2"], ["B1", "Join"], ["B2", "Join"], ["Join", "Exit"]]
    compute dominator tree for entry "Entry" with edges flow_edges into dom_res
    """).strip()
    env = execute(script)
    assert env["clique_res"]["maximum_clique_size"] == 3
    assert env["dom_res"]["idom"]["Join"] == "Entry"
    assert env["dom_res"]["idom"]["Exit"] == "Join"
