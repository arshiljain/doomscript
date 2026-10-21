import pytest
from doomscript.domains.compiler.runtime import (
    LR1ParserGenerator,
    ASTOptimizerPass,
    compiler_lr1_parser,
    compiler_optimize_ast,
)
from doomscript.domains.automata.runtime import (
    TwoTapeTuringMachineSimulator,
    MealyMachine,
    automata_mealy_to_moore,
    automata_two_tape_tm,
)
from doomscript.domains.dsa.runtime import (
    SplayTree,
    CompactRadixTree,
    dsa_splay_tree,
    dsa_radix_tree,
)


def test_lr1_parser_generator():
    # Simple arithmetic grammar:
    # E -> E + T
    # E -> T
    # T -> num
    rules = [
        ("E", ["E", "+", "T"]),
        ("E", ["T"]),
        ("T", ["num"]),
    ]
    parser = LR1ParserGenerator(start_symbol="E", rules=rules)
    tokens = ["num", "+", "num", "+", "num"]
    ast = parser.parse(tokens)
    assert ast is not None
    assert ast["type"] == "E"


def test_ast_optimizer():
    # 1. Constant folding
    expr = {
        "type": "BinaryOp",
        "op": "+",
        "left": {"type": "Literal", "value": 14},
        "right": {"type": "Literal", "value": 28},
    }
    opt_expr = ASTOptimizerPass.optimize(expr)
    assert opt_expr == {"type": "Literal", "value": 42}

    # 2. Dead branch elimination
    if_stmt = {
        "type": "IfStatement",
        "cond": {"type": "Literal", "value": False},
        "then": {"type": "Literal", "value": "unreachable"},
        "else": {"type": "Literal", "value": "reachable"},
    }
    opt_if = compiler_optimize_ast(if_stmt)
    assert opt_if == {"type": "Literal", "value": "reachable"}


def test_two_tape_turing_machine():
    # Copies tape 1 input onto tape 2 simultaneously while moving right, then accepts
    # Transitions: (state, s1, s2) -> (next_state, w1, d1, w2, d2)
    transitions = {
        ("q0", "a", "_"): ("q0", "a", "R", "a", "R"),
        ("q0", "b", "_"): ("q0", "b", "R", "b", "R"),
        ("q0", "_", "_"): ("q_accept", "_", "S", "_", "S"),
    }
    tm = automata_two_tape_tm(
        states={"q0", "q_accept"},
        tape_alphabet={"a", "b", "_"},
        transitions=transitions,
        start_state="q0",
        accept_states={"q_accept"},
    )
    res = tm.execute("abba")
    assert res["accepted"] is True
    assert res["tape1"] == "abba"
    assert res["tape2"] == "abba"


def test_mealy_moore_converter():
    # Mealy machine: 1-bit inverter (0 -> 1, 1 -> 0)
    mealy = MealyMachine(
        states={"s0"},
        inputs={"0", "1"},
        outputs={"0", "1"},
        transitions={
            ("s0", "0"): ("s0", "1"),
            ("s0", "1"): ("s0", "0"),
        },
        start_state="s0",
    )
    assert mealy.transduce(["0", "1", "1", "0"]) == ["1", "0", "0", "1"]

    # Convert to Moore
    moore = automata_mealy_to_moore(mealy)
    # In Moore machine, output has initial state output at index 0 followed by outputs
    res = moore.transduce(["0", "1", "1", "0"])
    assert res[1:] == ["1", "0", "0", "1"]


def test_splay_tree():
    tree = dsa_splay_tree()
    tree.insert(50, "fifty")
    tree.insert(20, "twenty")
    tree.insert(80, "eighty")
    tree.insert(10, "ten")
    tree.insert(30, "thirty")

    # Search for 20 -> should be splayed to root
    assert tree.search(20) == "twenty"
    assert tree.root.key == 20

    # Delete 20
    assert tree.delete(20) is True
    assert tree.search(20) is None
    assert tree.size == 4


def test_compact_radix_tree():
    rt = dsa_radix_tree()
    words = ["romane", "romanus", "romulus", "rubens", "ruber", "rubicon", "rubicundus"]
    for w in words:
        rt.insert(w, f"val_{w}")

    # Exact search
    for w in words:
        assert rt.search(w) == f"val_{w}"
    assert rt.search("roman") is None

    # Prefix lookup
    rubi_matches = rt.find_by_prefix("rubi")
    keys = sorted([k for k, _ in rubi_matches])
    assert keys == ["rubicon", "rubicundus"]
