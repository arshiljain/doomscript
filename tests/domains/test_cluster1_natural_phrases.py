"""Tests for Cluster 1 (Physical & Natural Sciences) natural English phrases:
physics, chem, bio, astronomy, circuit, neuro, robotics, quantum
"""

from doomscript.compiler.engine import execute


def test_cluster1_physics_and_chem(capsys):
    code = """
use physics
create pid controller with kp 1.0 and ki 0.1 and kd 0.05 into my_pid
update pid my_pid with setpoint 10.0 and measurement 8.0 into out_val
say out_val > 0

use chem
calculate elemental composition of "H2O" into comp
say comp["H"] > 10.0
generate morgan fingerprint for "CCO" radius 2 bits 512 into fp
say count of fp > 0
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "True"


def test_cluster1_astronomy_and_circuit(capsys):
    code = """
use astronomy
calculate position of planet "Mars" at 2451545.0 into mars_pos
say mars_pos.heliocentric_radius_au > 0

use circuit
evaluate logic gate "AND" with inputs [1, 1] into gate_res
say gate_res
evaluate logic gate "OR" with inputs [0, 0] into or_res
say or_res
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "False"


def test_cluster1_neuro_bio_quantum(capsys):
    code = """
use neuro
create izhikevich neuron with preset "RS" into izh
say izh.a > 0

use bio
codon optimize sequence "ATGCGT" into opt_seq
say opt_seq.gc_content > 0

use quantum
create bell state of type "phi_plus" into b_state
say b_state.num_qubits
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "2"
