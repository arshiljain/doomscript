"""Integration and verification test suite for Deepened Cluster III:
Quantum, Physics, and Circuit domains in DoomScript.

Validates pure Python algorithms and native spoken-English .doom code execution.
"""

import pytest
from doomscript.compiler.engine import execute


# ==============================================================================
# QUANTUM COMPUTING TESTS
# ==============================================================================

def test_quantum_density_matrix():
    """Validates pure and mixed density matrix analysis, purity, and entropy."""
    code = """
use quantum
analyze density matrix for 2 qubits into dm_res
assert dm_res's is_pure is true
assert dm_res's purity equals 1.0
assert dm_res's dimension equals 4
"""
    env = execute(code)
    dm = env["dm_res"]
    assert dm.is_pure is True
    assert dm.purity == 1.0
    assert dm.dimension == 4


def test_quantum_fourier_transform():
    """Validates exact Discrete Quantum Fourier Transform circuit execution."""
    code = """
use quantum
create quantum register with 3 qubits into qreg
apply hadamard to qubit 0 in qreg
apply qft to qreg into qft_res
assert qft_res's num_qubits equals 3
assert qft_res's peak_probability is over 0.0
"""
    env = execute(code)
    qft = env["qft_res"]
    assert qft.num_qubits == 3
    assert qft.peak_probability > 0.0


def test_quantum_variational_eigensolver():
    """Validates VQE parameterized ansatz optimization for Hamiltonian ground state."""
    code = """
use quantum
set h_model to {"II": -1.0, "ZZ": 0.5, "XX": 0.2}
solve vqe ground state for hamiltonian h_model with iterations 30 into vqe_res
assert vqe_res's optimal_energy is under 0.0
assert vqe_res's iterations equals 30
"""
    env = execute(code)
    vqe = env["vqe_res"]
    assert vqe.optimal_energy < 0.0
    assert vqe.iterations == 30


# ==============================================================================
# PHYSICS TESTS
# ==============================================================================

def test_physics_cloth_lattice():
    """Validates mass-spring-damper cloth mesh simulation with Verlet integration."""
    code = """
use physics
simulate cloth with rows 4 cols 4 steps 30 into cloth_res
assert cloth_res's equilibrium is true
assert cloth_res's max_sag is over 0.0
assert cloth_res's rows equals 4
assert cloth_res's cols equals 4
"""
    env = execute(code)
    cloth = env["cloth_res"]
    assert cloth.equilibrium is True
    assert cloth.max_sag > 0.0


def test_physics_rigid_body_3d_rotation():
    """Validates 3D rotational mechanics solving Euler's equations via RK4."""
    code = """
use physics
simulate rigid body 3d with mass 2.0 inertia 1.0 2.0 3.0 torque [0.5, 0.0, 0.0] duration 1.0 into rb_res
assert rb_res's energy_changed is true
assert rb_res's angular_momentum_magnitude is over 0.0
"""
    env = execute(code)
    rb = env["rb_res"]
    assert rb.energy_changed is True
    assert rb.angular_momentum_magnitude > 0.0


def test_physics_sph_fluid():
    """Validates Smoothed Particle Hydrodynamics (SPH) fluid density and pressure."""
    code = """
use physics
simulate sph fluid with particles 16 steps 15 into sph_res
assert sph_res's simulated is true
assert sph_res's num_particles equals 16
"""
    env = execute(code)
    sph = env["sph_res"]
    assert sph.simulated is True
    assert sph.num_particles == 16


# ==============================================================================
# CIRCUIT & ELECTRONICS TESTS
# ==============================================================================

def test_circuit_nonlinear_diode_solver():
    """Validates Newton-Raphson non-linear Shockley diode operating point."""
    code = """
use circuit
solve diode circuit with v_source 5.0 and resistance 1000.0 into diode_res
assert diode_res's converged is true
assert diode_res's v_diode is over 0.5
assert diode_res's i_diode_mA is over 0.0
assert diode_res's power_diode_mW is over 0.0
"""
    env = execute(code)
    d = env["diode_res"]
    assert d.converged is True
    assert d.v_diode > 0.5
    assert d.i_diode_mA > 0.0


def test_circuit_transmission_line_rlgc():
    """Validates distributed RLGC transmission line impedance and VSWR."""
    code = """
use circuit
analyze transmission line r 0.1 l 0.00000025 g 0.0001 c 0.0000000001 frequency 1000000.0 with z_load 50.0 into tline_res
assert tline_res's z0_ohms_real is over 0.0
assert tline_res's vswr is at least 1.0
assert tline_res's return_loss_db is over 0.0
"""
    env = execute(code)
    tl = env["tline_res"]
    assert tl.z0_ohms_real > 0.0
    assert tl.vswr >= 1.0


def test_circuit_state_space_rlc_step():
    """Validates series RLC resonant circuit transient step response."""
    code = """
use circuit
simulate rlc step response with r 20.0 l 0.001 c 0.000001 with v_step 5.0 with duration 0.001 into rlc_res
assert rlc_res's resonant_freq_hz is over 0.0
assert rlc_res's damping_ratio is over 0.0
assert rlc_res's max_capacitor_voltage is over 0.0
"""
    env = execute(code)
    rlc = env["rlc_res"]
    assert rlc.resonant_freq_hz > 0.0
    assert rlc.damping_ratio > 0.0
    assert rlc.max_capacitor_voltage > 0.0
