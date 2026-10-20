"""Comprehensive test suite for Cluster XIV deepened engines (Signals, Telecom, Quantum, Robotics, Chem).

Validates pure Python runtime engines and end-to-end spoken English .doom scripts.
"""

import math
import pytest
from doomscript.compiler.engine import execute

# Import runtime classes & functions
from doomscript.domains.signals.runtime import (
    ChirpZTransformCZT,
    LevinsonDurbinLPC,
    signals_czt,
    signals_levinson_durbin,
)
from doomscript.domains.telecom.runtime import (
    OFDMModulationEngine,
    ViterbiConvolutionalDecoder,
    telecom_ofdm_modulate,
    telecom_ofdm_demodulate,
    telecom_viterbi_encode,
    telecom_viterbi_decode,
)
from doomscript.domains.quantum.runtime import (
    QuantumPhaseEstimationQPE,
    QuantumKeyDistributionBB84,
    quantum_qpe_estimate,
    quantum_bb84_simulate,
)
from doomscript.domains.robotics.runtime import (
    RapidlyExploringRandomTreeStar3D,
    DynamicWindowApproachDWA,
    robotics_rrt_star_3d,
    robotics_dwa_velocity,
)
from doomscript.domains.chem.runtime import (
    AutocatalyticOregonatorSimulator,
    ArrheniusEyringTransitionState,
    chem_oregonator_simulate,
    chem_eyring_transition_state,
)


# ==============================================================================
# SIGNALS DOMAIN TESTS
# ==============================================================================

def test_signals_czt():
    # Unit impulse signal
    sig = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    res = ChirpZTransformCZT.compute(sig, m_bins=8)
    assert res["num_bins"] == 8
    # For impulse at n=0, CZT is identically 1.0 for all frequencies
    for mag in res["magnitudes"]:
        assert mag == pytest.approx(1.0, abs=1e-4)


def test_signals_levinson_durbin():
    # Autocorrelation of an AR(1) process with parameter a1 = -0.5, r[k] = 0.5^|k|
    autocorr = [1.0, 0.5, 0.25, 0.125]
    res = LevinsonDurbinLPC.solve(autocorr, order=2)
    assert res["order"] == 2
    # For AR(1), order 1 reflection coefficient is -0.5, order 2 is ~0.0
    assert res["reflection_coefficients"][0] == pytest.approx(-0.5, abs=1e-4)
    assert abs(res["reflection_coefficients"][1]) < 1e-4
    assert res["prediction_error"] < 1.0


def test_signals_spoken_english():
    code = """use signals
set raw_sig to [1.0, 0.5, 0.25, 0.125, 0.0, 0.0, 0.0, 0.0]
compute czt of raw_sig with 8 bins into czt_res
set ac to [1.0, 0.6, 0.36]
levinson durbin for ac with order 2 into lpc_res
"""
    env = execute(code)
    assert env["czt_res"].num_bins == 8
    assert env["lpc_res"].order == 2


# ==============================================================================
# TELECOM DOMAIN TESTS
# ==============================================================================

def test_telecom_ofdm():
    # 16 QPSK constellation symbols
    symbols = [complex(1.0, 1.0), complex(-1.0, 1.0), complex(-1.0, -1.0), complex(1.0, -1.0)] * 4
    mod = OFDMModulationEngine.modulate(symbols, n_fft=16, n_cp=4)
    assert mod["num_frames"] == 1
    assert mod["samples_count"] == 20  # 16 + 4

    # Demodulate without channel distortion -> perfect recovery
    demod = OFDMModulationEngine.demodulate(mod["time_samples"], n_fft=16, n_cp=4)
    assert demod["symbols_count"] == 16
    for orig, rec in zip(symbols, demod["recovered_symbols"]):
        assert rec.real == pytest.approx(orig.real, abs=1e-3)
        assert rec.imag == pytest.approx(orig.imag, abs=1e-3)


def test_telecom_viterbi():
    msg_bits = [1, 0, 1, 1, 0, 0, 1, 0]
    encoded = ViterbiConvolutionalDecoder.encode(msg_bits)
    assert len(encoded) == 16

    # Decode without errors
    dec = ViterbiConvolutionalDecoder.decode(encoded, original_bits=msg_bits)
    assert dec["decoded_bits"] == msg_bits
    assert dec["bit_errors"] == 0

    # Introduce a bit flip error
    corrupted = list(encoded)
    corrupted[3] ^= 1  # 1 bit flipped in codeword
    dec_err = ViterbiConvolutionalDecoder.decode(corrupted, original_bits=msg_bits)
    # Viterbi corrects the error!
    assert dec_err["decoded_bits"] == msg_bits


def test_telecom_spoken_english():
    code = """use telecom
set my_bits to [1, 1, 0, 1, 0, 0, 1]
encode convolutional bits my_bits into enc_bits
decode viterbi bits enc_bits into dec_res
"""
    env = execute(code)
    assert env["dec_res"].decoded_bits == [1, 1, 0, 1, 0, 0, 1]
    assert env["dec_res"].pairs_count == 7


# ==============================================================================
# QUANTUM DOMAIN TESTS
# ==============================================================================

def test_quantum_qpe():
    # True eigenphase theta = 0.25 = 1/4 = binary 0.0100
    res = QuantumPhaseEstimationQPE.estimate_phase(0.25, counting_qubits=4)
    assert res["true_theta"] == 0.25
    assert res["estimated_theta"] == pytest.approx(0.25, abs=1e-3)
    assert res["measured_index"] == 4  # 4 / 16 = 0.25
    assert res["probability"] > 0.9


def test_quantum_bb84():
    # Without Eve: QBER is 0.0, key accepted
    no_eve = QuantumKeyDistributionBB84.simulate(num_bits=48, eve_present=False, seed=123)
    assert no_eve["qber"] == 0.0
    assert no_eve["key_accepted"] is True
    assert len(no_eve["shared_key"]) > 0

    # With Eve: Eve disturbs bases, QBER ~ 0.25 > 0.11, key rejected
    with_eve = QuantumKeyDistributionBB84.simulate(num_bits=128, eve_present=True, seed=42)
    assert with_eve["qber"] > 0.11
    assert with_eve["key_accepted"] is False


def test_quantum_spoken_english():
    code = """use quantum
estimate quantum phase for theta 0.5 with 4 qubits into qpe_res
simulate bb84 protocol with 32 bits with eve False into bb84_res
"""
    env = execute(code)
    assert env["qpe_res"].estimated_theta == pytest.approx(0.5, abs=1e-3)
    assert env["bb84_res"].key_accepted is True


# ==============================================================================
# ROBOTICS DOMAIN TESTS
# ==============================================================================

def test_robotics_rrt_star_3d():
    start = (0.0, 0.0, 0.0)
    goal = (3.0, 3.0, 3.0)
    # Sphere obstacle not blocking direct line
    obstacles = [{"center": (10.0, 10.0, 10.0), "radius": 1.0}]
    res = RapidlyExploringRandomTreeStar3D.plan(
        start, goal, obstacles=obstacles, max_iter=100, step_size=1.0, goal_threshold=1.5, seed=42
    )
    assert res["nodes_count"] > 1
    assert len(res["path"]) >= 2
    assert res["path"][0] == (0.0, 0.0, 0.0)


def test_robotics_dwa_velocity():
    # Current state: at origin facing +x (0 rad), stopped
    current_state = (0.0, 0.0, 0.0, 0.0, 0.0)
    goal = (5.0, 0.0)  # Straight ahead
    res = DynamicWindowApproachDWA.calculate_velocity(current_state, goal, max_speed=1.0)
    # Commanded forward velocity should be positive
    assert res["best_linear_velocity"] > 0.0
    assert len(res["trajectory_points"]) > 0


def test_robotics_spoken_english():
    code = """use robotics
plan rrt star 3d path from [0.0, 0.0, 0.0] to [2.0, 2.0, 2.0] with step 1.0 into rrt_res
set robot_state to [0.0, 0.0, 0.0, 0.0, 0.0]
compute dwa velocity for state robot_state and goal [3.0, 0.0] with speed 1.0 into dwa_res
"""
    env = execute(code)
    assert env["rrt_res"].nodes_count > 1
    assert env["dwa_res"].best_linear_velocity > 0.0


# ==============================================================================
# CHEM DOMAIN TESTS
# ==============================================================================

def test_chem_oregonator():
    res = AutocatalyticOregonatorSimulator.simulate(duration=20.0, dt=0.005)
    assert res["duration"] == 20.0
    assert res["final_x"] >= 0.0
    assert res["final_z"] >= 0.0
    assert res["max_x"] > res["min_x"]


def test_chem_eyring_transition_state():
    # Known reaction data: T in Kelvin, rate constants k in 1/s
    temps = [298.15, 308.15, 318.15, 328.15]
    # Synthetic Eyring rate constants for Delta H# = 50 kJ/mol, Delta S# = -50 J/(mol*K)
    r = 8.314462618
    kb_h = 2.083661912e10
    rates = [kb_h * t * math.exp(-50000.0 / (r * t) - 50.0 / r) for t in temps]

    res = ArrheniusEyringTransitionState.fit(temps, rates)
    assert res["delta_h_activation_kj"] == pytest.approx(50.0, abs=0.5)
    assert res["delta_s_activation_j_k"] == pytest.approx(-50.0, abs=1.0)
    assert res["r_squared"] > 0.99


def test_chem_spoken_english():
    code = """use chem
simulate oregonator reaction for duration 10.0 into oreg_res
set test_temps to [300.0, 310.0, 320.0]
set test_rates to [0.01, 0.03, 0.08]
fit eyring kinetics for temperatures test_temps and rates test_rates into eyring_res
"""
    env = execute(code)
    assert env["oreg_res"].duration == 10.0
    assert env["eyring_res"].temperatures_count == 3
    assert env["eyring_res"].delta_h_activation_kj > 0.0
