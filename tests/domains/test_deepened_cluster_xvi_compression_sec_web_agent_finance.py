"""Comprehensive test suite for Cluster XVI deepened engines (Compression, Sec, Web, Agent, Finance).

Validates pure Python runtime engines and end-to-end spoken English .doom scripts.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Import runtime classes & functions
from doomscript.domains.compression.runtime import (
    AsymmetricNumeralSystemsANS,
    PredictionByPartialMatchingPPM,
    compression_rans_encode,
    compression_rans_decode,
    compression_ppm_model,
)
from doomscript.domains.sec.runtime import (
    MerkleTreeInclusionProof,
    BlindSignatureChaumRSA,
    sec_merkle_build_tree,
    sec_merkle_generate_proof,
    sec_merkle_verify_proof,
    sec_chaum_blind_message,
    sec_chaum_sign_blinded,
    sec_chaum_unblind_signature,
    sec_chaum_verify_signature,
)
from doomscript.domains.web.runtime import (
    WebSocketFrameCodec,
    HttpChunkedTransferCodec,
    web_websocket_encode,
    web_websocket_decode,
    web_chunked_encode,
    web_chunked_decode,
)
from doomscript.domains.agent.runtime import (
    HierarchicalTaskNetworkHTNPlanner,
    MonteCarloTreeSearchMCTS,
    agent_htn_plan,
    agent_mcts_search,
)
from doomscript.domains.finance.runtime import (
    HullWhiteInterestRateTree,
    MertonJumpDiffusionModel,
    fin_hull_white_tree,
    fin_merton_jump_diffusion,
)


# ==============================================================================
# COMPRESSION DOMAIN TESTS
# ==============================================================================

def test_compression_rans():
    text = "TOBEORNOTTOBETHATISTHEQUESTION"
    encoded = AsymmetricNumeralSystemsANS.encode(text)
    assert encoded["state"] > 0
    assert encoded["length"] == len(text)
    assert encoded["compression_ratio"] > 0.0

    decoded = AsymmetricNumeralSystemsANS.decode(encoded)
    assert decoded == text


def test_compression_ppm():
    text = "THE QUICK BROWN FOX JUMPS OVER THE LAZY DOG"
    model = PredictionByPartialMatchingPPM.model(text, max_order=1)
    assert model["characters_processed"] == len(text)
    assert model["contexts_count"] > 0
    assert model["total_bits"] > 0.0
    assert model["bits_per_symbol"] < 8.0


def test_compression_spoken_english():
    code = """use compression
encode rans data "ABRACADABRA" into rans_enc
decode rans state rans_enc into rans_dec
model ppm context for "ABRACADABRA" with order 1 into ppm_res
"""
    env = execute(code)
    assert env["rans_dec"] == "ABRACADABRA"
    assert env["ppm_res"].characters_processed == 11


# ==============================================================================
# SEC DOMAIN TESTS
# ==============================================================================

def test_sec_merkle_tree():
    leaves = ["tx_alpha", "tx_beta", "tx_gamma", "tx_delta"]
    tree = MerkleTreeInclusionProof.build_tree(leaves)
    assert tree["depth"] == 2
    assert tree["leaves_count"] == 4
    assert len(tree["root"]) == 64

    # Generate proof for index 1 ("tx_beta")
    proof = MerkleTreeInclusionProof.generate_proof(leaves, 1)
    assert proof["leaf"] == "tx_beta"
    assert len(proof["proof_path"]) == 2

    # Verify proof against root
    is_valid = MerkleTreeInclusionProof.verify_proof("tx_beta", proof["proof_path"], tree["root"])
    assert is_valid is True

    # Tampered leaf should fail
    is_invalid = MerkleTreeInclusionProof.verify_proof("tx_tampered", proof["proof_path"], tree["root"])
    assert is_invalid is False


def test_sec_chaum_blind_signature():
    # Toy RSA keys: p=61, q=53 -> n=3233, phi=3120, e=17, d=2753
    e, d, n = 17, 2753, 3233
    r = 13  # Blinding factor coprime to n
    m = 42  # Secret message

    # 1. Blind message
    blinded_m = BlindSignatureChaumRSA.blind_message(m, e, n, r)
    assert blinded_m != m

    # 2. Signer signs blinded message
    blind_sig = BlindSignatureChaumRSA.sign_blinded(blinded_m, d, n)

    # 3. User unblinds signature
    signature = BlindSignatureChaumRSA.unblind_signature(blind_sig, r, n)

    # 4. Anyone verifies standard RSA signature
    assert BlindSignatureChaumRSA.verify_signature(signature, m, e, n) is True


def test_sec_spoken_english():
    code = """use sec
set tx_leaves to ["tx1", "tx2", "tx3", "tx4"]
build merkle tree for leaves tx_leaves into mt_tree
generate merkle proof for leaf index 1 from tx_leaves into mt_proof
verify merkle proof for leaf "tx2" proof mt_proof root mt_tree's root into is_valid_proof
blind message 42 with e 17 n 3233 r 13 into blinded_m
sign blinded message blinded_m with d 2753 n 3233 into blind_sig
unblind signature blind_sig with r 13 n 3233 into real_sig
verify blind signature real_sig for message 42 with e 17 n 3233 into is_sig_valid
"""
    env = execute(code)
    assert env["is_valid_proof"] is True
    assert env["is_sig_valid"] is True


# ==============================================================================
# WEB DOMAIN TESTS
# ==============================================================================

def test_web_websocket_frame():
    payload = "Hello WebSocket!"
    # Unmasked frame
    frame = WebSocketFrameCodec.encode(payload, opcode=1, mask=False)
    assert frame[0] == 0x81  # FIN=1, opcode=1
    assert len(frame) == 2 + len(payload)

    decoded = WebSocketFrameCodec.decode(frame)
    assert decoded["fin"] is True
    assert decoded["opcode"] == 1
    assert decoded["opcode_name"] == "text"
    assert decoded["payload_text"] == payload

    # Masked frame
    masked_frame = WebSocketFrameCodec.encode(payload, opcode=1, mask=True, mask_key=b"\xaa\xbb\xcc\xdd")
    assert masked_frame[1] & 0x80 == 0x80  # MASK=1
    decoded_m = WebSocketFrameCodec.decode(masked_frame)
    assert decoded_m["payload_text"] == payload


def test_web_chunked_transfer():
    chunks = ["HeaderChunk", "BodyData", "Footer"]
    encoded = HttpChunkedTransferCodec.encode(chunks, trailers={"X-Checksum": "abc123"})
    assert "0\r\n" in encoded
    assert "X-Checksum: abc123\r\n" in encoded

    decoded = HttpChunkedTransferCodec.decode(encoded)
    assert decoded["payload"] == "HeaderChunkBodyDataFooter"
    assert decoded["chunks_count"] == 3
    assert decoded["trailers"]["X-Checksum"] == "abc123"


def test_web_spoken_english():
    code = """use web
encode websocket frame payload "hello doomscript" opcode 1 masked False into ws_frame
decode websocket frame bytes ws_frame into ws_res
set raw_chunks to ["hello ", "world!"]
encode chunked transfer chunks raw_chunks into chk_data
decode chunked transfer body chk_data into chk_res
"""
    env = execute(code)
    assert env["ws_res"].payload_text == "hello doomscript"
    assert env["chk_res"].payload == "hello world!"


# ==============================================================================
# AGENT DOMAIN TESTS
# ==============================================================================

def test_agent_htn_planning():
    initial_state = {"at": "home", "cash": 50}
    methods = {
        "travel_to_city": [
            {
                "preconditions": {"at": "home"},
                "subtasks": ["buy_ticket", "board_train"],
            }
        ]
    }
    operators = {
        "buy_ticket": {
            "preconditions": {"at": "home"},
            "add_list": {"has_ticket": True},
            "del_list": [],
            "cost": 10.0,
        },
        "board_train": {
            "preconditions": {"has_ticket": True},
            "add_list": {"at": "city"},
            "del_list": ["at"],
            "cost": 5.0,
        },
    }

    res = HierarchicalTaskNetworkHTNPlanner.plan(["travel_to_city"], initial_state, methods, operators)
    assert res["success"] is True
    assert res["plan"] == ["buy_ticket", "board_train"]
    assert res["total_cost"] == 15.0
    assert res["final_state"]["at"] == "city"


def test_agent_mcts_search():
    actions = ["left", "right", "jump"]
    res = MonteCarloTreeSearchMCTS.search("start", actions, iterations=40)
    assert res["best_action"] in actions
    assert res["iterations"] == 40
    assert len(res["action_statistics"]) == 3


def test_agent_spoken_english():
    code = """use agent
set htn_tasks to ["travel_to_city"]
set htn_state to {"at": "home", "cash": 50}
set htn_methods to {"travel_to_city": [{"preconditions": {"at": "home"}, "subtasks": ["buy_ticket", "board_train"]}]}
set htn_ops to {"buy_ticket": {"preconditions": {"at": "home"}, "add_list": {"has_ticket": True}, "del_list": [], "cost": 10.0}, "board_train": {"preconditions": {"has_ticket": True}, "add_list": {"at": "city"}, "del_list": ["at"], "cost": 5.0}}
plan htn tasks htn_tasks state htn_state methods htn_methods operators htn_ops into htn_res
set mcts_actions to ["left", "right", "jump"]
run mcts planning state "idle" actions mcts_actions iterations 30 exploration 1.4 into mcts_res
"""
    env = execute(code)
    assert env["htn_res"].success is True
    assert len(env["htn_res"].plan) == 2
    assert env["mcts_res"].iterations == 30


# ==============================================================================
# FINANCE DOMAIN TESTS
# ==============================================================================

def test_finance_hull_white():
    res = HullWhiteInterestRateTree.build_tree(a=0.1, sigma=0.015, num_steps=8, dt=0.25, initial_rate=0.03)
    assert res["num_steps"] == 8
    assert len(res["zero_bond_prices"]) == 9
    assert res["zero_bond_prices"][0] == 1.0
    # Zero bond prices must be strictly positive and decaying with time
    assert 0.0 < res["zero_bond_prices"][-1] < 1.0
    assert len(res["forward_rates"]) == 8


def test_finance_merton_jump():
    # In Merton model, adding positive jump intensity increases option price due to higher total variance / kurtosis
    base_res = MertonJumpDiffusionModel.price(
        spot=100.0, strike=100.0, rate=0.05, volatility=0.2,
        jump_intensity_lambda=0.0, jump_mean_mu_j=0.0, jump_vol_sigma_j=0.1,
        time_to_maturity=1.0, is_call=True
    )
    jump_res = MertonJumpDiffusionModel.price(
        spot=100.0, strike=100.0, rate=0.05, volatility=0.2,
        jump_intensity_lambda=1.0, jump_mean_mu_j=0.0, jump_vol_sigma_j=0.1,
        time_to_maturity=1.0, is_call=True
    )
    assert base_res["jump_premium"] == 0.0
    assert jump_res["option_price"] > base_res["option_price"]
    assert jump_res["jump_premium"] > 0.0


def test_finance_spoken_english():
    code = """use finance
build hull white tree mean reversion 0.1 vol 0.015 steps 8 dt 0.25 rate 0.03 into hw_tree
price merton jump option spot 100.0 strike 100.0 rate 0.05 vol 0.2 lambda 0.5 jump mean -0.05 jump vol 0.1 time 1.0 call True into merton_res
"""
    env = execute(code)
    assert env["hw_tree"].num_steps == 8
    assert env["merton_res"].option_price > 0.0
    assert env["merton_res"].is_call is True
