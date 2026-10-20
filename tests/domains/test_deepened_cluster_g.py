"""Comprehensive tests for Deepened Cluster G domains:
- finance: AnalyticalGreeks, BinomialCoxRossRubinstein, MarkowitzOptimizer
- time_series: ARIMASimulator, DynamicTimeWarping, CUSUMDetector
- chain: PatriciaMerkleTrie, SchnorrZKProtocol, RaftConsensusEngine
- quantum: QuantumErrorCorrection, GroverSearch, QuantumTeleportation
- sec: ShamirSecretSharing, TOTPGenerator, Secp256k1Curve
"""

import math
from doomscript.domains.finance.runtime import (
    AnalyticalGreeks,
    BinomialCoxRossRubinstein,
    MarkowitzOptimizer,
)
from doomscript.domains.time_series.runtime import (
    ARIMASimulator,
    DynamicTimeWarping,
    CUSUMDetector,
)
from doomscript.domains.chain.runtime import (
    PatriciaMerkleTrie,
    SchnorrZKProtocol,
    RaftConsensusEngine,
)
from doomscript.domains.quantum.runtime import (
    QuantumErrorCorrection,
    GroverSearch,
    QuantumTeleportation,
)
from doomscript.domains.sec.runtime import (
    ShamirSecretSharing,
    TOTPGenerator,
    Secp256k1Curve,
)
from doomscript.runtime import (
    finance_analytical_greeks,
    finance_binomial_price,
    finance_optimize_markowitz,
    time_series_arima_simulate,
    time_series_dtw,
    time_series_cusum,
    chain_patricia_trie,
    chain_schnorr_prove,
    chain_schnorr_verify,
    quantum_grover_search,
    quantum_teleport,
    sec_shamir_split,
    sec_shamir_recover,
    sec_generate_totp,
    sec_verify_totp,
    sec_secp256k1_public_key,
    sec_secp256k1_ecdh,
)


# --- 1. Finance Tests ---

def test_analytical_greeks():
    S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.2
    greeks_call = AnalyticalGreeks.all_greeks(S, K, T, r, sigma, "call")
    greeks_put = AnalyticalGreeks.all_greeks(S, K, T, r, sigma, "put")

    # Black-Scholes call price should be ~10.45
    assert 10.0 < greeks_call["price"] < 11.0
    # Delta of ATM call ~ 0.637
    assert 0.5 < greeks_call["delta"] < 0.7
    # Delta of ATM put ~ -0.363
    assert -0.5 < greeks_put["delta"] < -0.3
    # Gamma should be positive and identical
    assert greeks_call["gamma"] > 0
    assert abs(greeks_call["gamma"] - greeks_put["gamma"]) < 1e-5
    # Vega should be positive and identical
    assert greeks_call["vega"] > 0
    assert abs(greeks_call["vega"] - greeks_put["vega"]) < 1e-5

    # Put-Call Parity: C - P = S - K * exp(-r * T)
    lhs = greeks_call["price"] - greeks_put["price"]
    rhs = S - K * math.exp(-r * T)
    assert abs(lhs - rhs) < 1e-4

    # Test implied volatility recovery
    recovered_vol = AnalyticalGreeks.implied_volatility(greeks_call["price"], S, K, T, r, "call")
    assert abs(recovered_vol - sigma) < 1e-4


def test_binomial_crr_pricing():
    S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.2
    # European call comparison with Black-Scholes
    crr_euro = BinomialCoxRossRubinstein.price(S, K, T, r, sigma, steps=100, option_type="call", is_american=False)
    bs_price = AnalyticalGreeks.call_price(S, K, T, r, sigma)
    assert abs(crr_euro["price"] - bs_price) < 0.15

    # American put with high dividends or deep in the money should show early exercise
    crr_euro_put = BinomialCoxRossRubinstein.price(80.0, 100.0, 1.0, 0.10, 0.2, steps=100, option_type="put", is_american=False)
    crr_amer_put = BinomialCoxRossRubinstein.price(80.0, 100.0, 1.0, 0.10, 0.2, steps=100, option_type="put", is_american=True)
    assert crr_amer_put["price"] >= crr_euro_put["price"]


def test_markowitz_portfolio_optimization():
    expected_returns = [0.12, 0.18, 0.10]
    cov_matrix = [
        [0.04, 0.01, 0.005],
        [0.01, 0.09, 0.02],
        [0.005, 0.02, 0.025],
    ]

    min_var = MarkowitzOptimizer.minimum_variance_portfolio(expected_returns, cov_matrix, risk_free_rate=0.03)
    assert len(min_var["weights"]) == 3
    assert abs(sum(min_var["weights"]) - 1.0) < 1e-2

    max_sharpe = MarkowitzOptimizer.maximum_sharpe_portfolio(expected_returns, cov_matrix, risk_free_rate=0.03)
    assert abs(sum(max_sharpe["weights"]) - 1.0) < 1e-2
    assert max_sharpe["sharpe_ratio"] >= min_var["sharpe_ratio"]

    frontier = MarkowitzOptimizer.efficient_frontier(expected_returns, cov_matrix, num_points=5)
    assert len(frontier) == 5


# --- 2. Time Series Tests ---

def test_arima_simulator_and_fit():
    # Simulate AR(1) process with phi = 0.7
    series = ARIMASimulator.simulate(n=150, ar_params=[0.7], d=0, sigma=0.5, seed=42)
    assert len(series) == 150

    # Fit AR(1)
    coeffs = ARIMASimulator.fit_ar(series, p=1)
    assert len(coeffs) == 1
    # Coefficient should be positive and close to 0.7
    assert 0.4 < coeffs[0] < 0.9

    # Forecast 5 steps ahead
    fc = ARIMASimulator.forecast(series, p=1, d=0, steps=5, ar_params=coeffs)
    assert len(fc) == 5


def test_dynamic_time_warping():
    # Identity test
    s1 = [1.0, 2.0, 3.0, 2.0, 1.0]
    res_id = DynamicTimeWarping.align(s1, s1)
    assert res_id["distance"] == 0.0

    # Time-shifted series
    s2 = [0.0, 1.0, 2.0, 3.0, 2.0, 1.0, 0.0]
    res_shift = DynamicTimeWarping.align(s1, s2)
    assert res_shift["distance"] < 1.5
    assert res_shift["normalized_distance"] < 0.3
    assert res_shift["path"][0] == (0, 0)
    assert res_shift["path"][-1] == (len(s1) - 1, len(s2) - 1)


def test_cusum_detector():
    # Stable series of 10.0, then abrupt step up to 25.0
    stable = [10.0 + (i % 2) * 0.1 for i in range(20)]
    shifted = [25.0 + (i % 2) * 0.1 for i in range(20)]
    data = stable + shifted

    res = CUSUMDetector.detect(data, baseline_mean=10.0, std_dev=0.5, threshold_h=4.0)
    assert len(res["change_points"]) >= 1
    assert res["change_points"][0]["direction"] == "upward"
    assert res["change_points"][0]["index"] >= 20


# --- 3. Blockchain & Consensus Tests ---

def test_patricia_merkle_trie():
    trie = PatriciaMerkleTrie()
    trie.put("apple", "red_fruit")
    trie.put("app", "application")
    trie.put("banana", "yellow_fruit")

    assert trie.get("apple") == "red_fruit"
    assert trie.get("app") == "application"
    assert trie.get("banana") == "yellow_fruit"
    assert trie.get("orange") is None

    # Proof verification
    proof = trie.get_proof("apple")
    assert len(proof) > 0
    assert PatriciaMerkleTrie.verify_proof(trie.root_hash, "apple", "red_fruit", proof) is True


def test_schnorr_zk_protocol():
    secret_x = 1234567890123456789
    p = 2305843009213693951  # 2^61 - 1 Mersenne prime
    g = 7
    q = (p - 1) // 2
    public_y = pow(g, secret_x, p)

    proof = SchnorrZKProtocol.prove(secret_x, public_y, g=g, p=p, q=q, nonce_r=42)
    assert SchnorrZKProtocol.verify(public_y, proof, g=g, p=p, q=q) is True

    # Tampered public key should fail verification
    assert SchnorrZKProtocol.verify(public_y + 1, proof, g=g, p=p, q=q) is False


def test_raft_consensus_engine():
    nodes = ["node-1", "node-2", "node-3"]
    cluster = {nid: RaftConsensusEngine(nid, nodes) for nid in nodes}

    # Node 1 starts election
    rv_rpc = cluster["node-1"].start_election()
    assert cluster["node-1"].role == "Candidate"

    # Broadcast vote request to peers
    for peer in ["node-2", "node-3"]:
        resp = cluster[peer].handle_request_vote(rv_rpc)
        cluster["node-1"].receive_vote_response(resp)

    # Node 1 should now be leader (majority 2 of 3)
    assert cluster["node-1"].role == "Leader"
    assert cluster["node-1"].leader_id == "node-1"

    # Leader appends log entry
    entry = cluster["node-1"].append_command({"set": "x", "val": 42})
    assert entry.index == 1

    # Leader replicates to follower
    ae_rpc = cluster["node-1"].create_append_entries(follower_prev_index=0)
    ae_resp = cluster["node-2"].handle_append_entries(ae_rpc)
    assert ae_resp["success"] is True
    assert len(cluster["node-2"].log) == 1
    assert cluster["node-2"].log[0].command == {"set": "x", "val": 42}


# --- 4. Quantum Simulation Tests ---

def test_quantum_error_correction():
    # 3-qubit bit flip code: alpha|000> + beta|111>
    alpha, beta = 0.6 + 0.0j, 0.8 + 0.0j
    encoded = QuantumErrorCorrection.encode_bit_flip(alpha, beta)

    # Inject bit-flip error on qubit 1 (middle qubit)
    corrupted = QuantumErrorCorrection.inject_error(encoded, "X", target_qubit=1)
    # Target qubit 1 flipped: |000> -> |010>, |111> -> |101>
    assert abs(corrupted[2]) > 0.5  # |010> has amplitude 0.6

    # Detect syndrome and correct
    corrected, err_qubit = QuantumErrorCorrection.detect_and_correct_bit_flip(corrupted)
    assert err_qubit == 1
    # Check that state is restored
    assert abs(corrected[0] - alpha) < 1e-6
    assert abs(corrected[7] - beta) < 1e-6


def test_grover_search():
    # 3-qubit search space (N = 8), target state = 6 (|110>)
    grover = GroverSearch(num_qubits=3, target_state=6)
    res = grover.run_optimal()

    assert res["success"] is True
    assert res["measured_state"] == 6
    assert res["target_probability"] > 0.90


def test_quantum_teleportation():
    # Teleport arbitrary superposition state (alpha|0> + beta|1>)
    alpha = complex(1.0 / math.sqrt(3.0), 0.0)
    beta = complex(math.sqrt(2.0 / 3.0), 0.0)

    res = QuantumTeleportation.teleport(alpha, beta)
    assert res["perfect_fidelity_achieved"] is True
    for branch, data in res["measurement_outcomes"].items():
        assert data["fidelity"] == 1.0


# --- 5. Cybersecurity Tests ---

def test_shamir_secret_sharing():
    secret = 987654321012345
    n, k = 5, 3
    shares = ShamirSecretSharing.split_secret(secret, n=n, k=k)
    assert len(shares) == 5

    # Any 3 shares reconstruct secret
    recovered = ShamirSecretSharing.recover_secret(shares[:3])
    assert recovered == secret

    # Another subset of 3 shares
    recovered_alt = ShamirSecretSharing.recover_secret([shares[0], shares[2], shares[4]])
    assert recovered_alt == secret

    # Bytes secret sharing
    raw = b"DoomScript top-secret payload"
    byte_shares = ShamirSecretSharing.split_bytes(raw, n=4, k=2)
    recovered_bytes = ShamirSecretSharing.recover_bytes(byte_shares[1:3])
    assert recovered_bytes == raw


def test_totp_generator():
    secret = "JBSWY3DPEHPK3PXP"  # standard base32 test secret
    # Fixed timestamp
    t0 = 1234567890.0
    token = TOTPGenerator.generate_totp(secret, for_time=t0, digits=6)
    assert len(token) == 6
    assert token.isdigit()

    # Verification
    assert TOTPGenerator.verify_totp(secret, token, for_time=t0) is True
    assert TOTPGenerator.verify_totp(secret, "000000", for_time=t0) is False


def test_secp256k1_curve():
    # Check generator point is on curve
    assert Secp256k1Curve.is_on_curve((Secp256k1Curve.GX, Secp256k1Curve.GY)) is True

    # Derive public keys for Alice and Bob
    priv_alice = 0xABCD1234
    priv_bob = 0x5678EF01

    pub_alice = Secp256k1Curve.public_key(priv_alice)
    pub_bob = Secp256k1Curve.public_key(priv_bob)

    assert Secp256k1Curve.is_on_curve(pub_alice) is True
    assert Secp256k1Curve.is_on_curve(pub_bob) is True

    # Test ECDH key exchange: both sides derive identical shared secret
    secret_alice = Secp256k1Curve.ecdh_shared_secret(priv_alice, pub_bob)
    secret_bob = Secp256k1Curve.ecdh_shared_secret(priv_bob, pub_alice)

    assert secret_alice == secret_bob
    assert len(secret_alice) == 64  # SHA-256 hex string
