"""Tests for natural English spoken phrases across specialized domains in DoomScript."""

from doomscript.compiler.engine import execute


def test_robotics_natural_phrases(capsys):
    code = """
use robotics
move arm to x: 0.5, y: 0.5 into pose
say pose.reached

move arm to x: 0.1, y: 0.2, z: 0.3 into pose3d
say count of pose3d.joint_angles

read lidar sensor into scan
say scan.num_beams
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "True"
    assert lines[1] == "3"
    assert lines[2] == "360"


def test_finance_natural_phrases(capsys):
    code = """
use finance
calculate black-scholes price for call option on asset 100 with strike 100, maturity 1.0, rate 0.05, vol 0.2 into call_price
say math_round(call_price, 2)

calculate greeks for call option on asset 100 with strike 100, maturity 1.0, rate 0.05, vol 0.2 into greeks
say math_round(greeks.delta, 2)
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "10.45"
    assert lines[1] == "0.64"


def test_quantum_natural_phrases(capsys):
    code = """
use quantum
create quantum circuit with 1 qubits into qc
apply hadamard gate to qubit 0 in circuit qc
measure state of qubit 0 in circuit qc into bit1
say bit1 in [0, 1]

create quantum circuit with 1 qubits into qc2
apply hadamard gate to qubit 0
measure state into bit2
say bit2 in [0, 1]
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "True"
    assert lines[1] == "True"


def test_ml_natural_phrases(capsys):
    code = """
use ml
dataset = [{x: 1, price: 10}, {x: 2, price: 20}, {x: 3, price: 30}]
train regression model on dataset with target "price" into reg
predict with model reg on [{x: 4}] into preds
say math_round(preds[0], 0)

train regression model on dataset with target "price"
predict with model on [{x: 5}] into preds2
say math_round(preds2[0], 0)
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "40"
    assert lines[1] == "50"


def test_bio_chem_physics_graph_sec_natural_phrases(capsys):
    code = """
use bio
calculate gc content of "ATGCGC" into gc
say math_round(gc, 2)
align sequences "ACGT" and "ACCT" into alignment
say alignment.score > 0

use chem
calculate molecular weight of "H2O" into mw
say math_round(mw, 1)

use physics
calculate kinetic energy with mass 2.0 and velocity 3.0 into ke
say ke

use sec
calculate password entropy for "Secret123!" into ent
say ent > 20
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "66.67"
    assert lines[1] == "True"
    assert lines[2] == "18.0"
    assert lines[3] == "9.0"
    assert lines[4] == "True"


def test_compiler_compression_symbolic_graph_natural_phrases(capsys):
    code = """
use compiler
assemble bytecode "LOAD_CONST 42\\nRETURN" into prog
execute bytecode prog into res
say res.halted

use compression
compress "hello world" with huffman into huff
say huff.compressed_bits > 0

use symbolic
simplify "x + x" into simp
say simp

use graph
create empty graph into g
add node "A" to graph g
add node "B" to graph g
add edge from "A" to "B" to graph g
find shortest path from "A" to "B" in graph g into p
say count of p
"""
    execute(code)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert lines[0] == "True"
    assert lines[1] == "True"
    assert lines[2] == "2 * x"
    assert lines[3] == "2"
