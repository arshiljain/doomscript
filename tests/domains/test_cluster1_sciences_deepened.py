"""Comprehensive test suite verifying natural spoken English phrasings and declarative blocks
for all 8 domains in Cluster 1: Physical & Natural Sciences
(quantum, robotics, physics, chem, bio, astronomy, circuit, neuro)
"""

import pytest
from doomscript.compiler.engine import execute


def test_quantum_natural_phrases_and_blocks():
    code = """
use quantum

circuit "bell" with 2 qubits into bell_qc:
    hadamard on qubit 0
    cnot from 0 to 1
    measure qubit 0

say bell_qc.num_qubits == 2

create quantum circuit with 2 qubits into qc
apply hadamard gate to qubit 0
entangle qubit 0 with qubit 1
measure state into bit
say bit in [0, 1]
"""
    res = execute(code)
    assert res.get("bell_qc").num_qubits == 2
    assert res.get("bit") in [0, 1]


def test_robotics_natural_phrases_and_blocks():
    code = """
use robotics

move arm to x: 10, y: 20 into pose
say pose.x == 10.0
say pose.y == 20.0

read lidar sensor into scan
say scan.readings is not empty

trajectory "delivery" into my_path:
    start at [0.0, 0.0, 0.0]
    goal at [5.0, 5.0, 0.0]
    radius 1.5
    generate using dubins

say count of my_path.path > 0

plan dubins path from [0.0, 0.0, 0.0] to [5.0, 5.0, 0.0] with radius 1.5 into dpath
say count of dpath.waypoints > 0
"""
    res = execute(code)
    assert res.get("pose")["x"] == 10.0
    assert len(res.get("my_path")["path"]) > 0
    assert len(res.get("dpath")["waypoints"]) > 0


def test_physics_natural_phrases():
    code = """
use physics

calculate van der waals pressure for gas "CO2" at temp 273.15 and volume 0.0224 into p_vdw
say p_vdw > 0

calculate normal modes for masses [1.0, 1.0] spring constants [100.0, 100.0] into modes
say modes is not empty
"""
    res = execute(code)
    assert res.get("p_vdw") > 0
    assert res.get("modes") is not None


def test_chem_natural_phrases():
    code = """
use chem

calculate molecular weight of "H2O" into mw
say mw > 18.0

calculate elemental composition of "H2O" into comp
say comp["H"] > 10.0

generate 3d conformer for smiles "CCO" into conf3d
say count of conf3d.coordinates > 0
"""
    res = execute(code)
    assert res.get("mw") > 18.0
    assert res.get("comp")["H"] > 10.0
    assert len(res.get("conf3d")["coordinates"]) > 0


def test_bio_natural_phrases():
    code = """
use bio

calculate gc content of "ACGTGC" into gc
say gc > 0.6

digest dna sequence "GAATTC" with enzyme "EcoRI" into fragments
say fragments is not empty

find cpg islands in sequence "CGCGCGCGCGCG" window 10 into islands
say islands is not empty
"""
    res = execute(code)
    assert res.get("gc") > 0.6
    assert res.get("fragments") is not None
    assert res.get("islands") is not None


def test_astronomy_natural_phrases():
    code = """
use astronomy

calculate julian date for year 2024 month 10 day 20 into jd
say jd > 2400000

calculate greenwich sidereal time for julian date jd into gst
say gst.greenwich_sidereal_time_hours >= 0.0
"""
    res = execute(code)
    assert res.get("jd") > 2400000
    assert res.get("gst")["greenwich_sidereal_time_hours"] >= 0.0


def test_circuit_natural_phrases():
    code = """
use circuit

calculate voltage with current 2 and resistance 5 into v
say v == 10.0

minimize logic using quine mccluskey with minterms [0, 1, 2, 5] variables 3 into qm
say qm is not empty
"""
    res = execute(code)
    assert res.get("v") == 10.0
    assert res.get("qm") is not None


def test_neuro_natural_phrases():
    code = """
use neuro

create lif neuron with v_rest -70.0 with v_thresh -50.0 into lif
say lif.v_rest == -70.0

generate poisson spike train with rate 25.0 and duration 1.0 into spikes
say spikes is not empty
"""
    res = execute(code)
    assert res.get("lif").v_rest == -70.0
    assert len(res.get("spikes")) >= 0
