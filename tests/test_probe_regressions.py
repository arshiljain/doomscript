"""
Regression tests for user probe issues:
1. Membership test with 'in' (lists, dicts, memo sets)
2. Python-style methods (def / self in classes and generators)
3. Keyword collisions (random.seed(1), with open(...) as f:)
4. Builtin shadowing (sorted with key/reverse, min, max, sum, round, len)
5. Syntax gaps (f-strings, English expression standard deviation of xs)
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute


def run_code(code: str, custom_globals=None):
    if custom_globals is None:
        custom_globals = {}
    execute(textwrap.dedent(code).strip(), custom_globals=custom_globals)
    return custom_globals


def test_probe_1_membership_in():
    code = """
    xs = [1, 2, 3]
    d = {"a": 10, "b": 20}
    memo = {100: "cached"}

    in_xs = 2 in xs
    not_in_xs = 5 in xs
    in_d = "a" in d
    not_in_d = "z" in d
    in_memo = 100 in memo

    filtered = [x for x in xs if x in [2, 3]]
    """
    env = run_code(code)
    assert env["in_xs"] is True
    assert env["not_in_xs"] is False
    assert env["in_d"] is True
    assert env["not_in_d"] is False
    assert env["in_memo"] is True
    assert env["filtered"] == [2, 3]


def test_probe_2_python_def_and_self():
    code = """
    class Node:
        def __init__(self, v):
            self.v = v

    node = Node(42)
    val = node.v

    class Calculator:
        def add(self, a, b):
            return a + b

    calc = Calculator()
    res = calc.add(15, 25)

    def gen():
        yield 10
        yield 20

    items = list(gen())
    """
    env = run_code(code)
    assert env["val"] == 42
    assert env["res"] == 40
    assert env["items"] == [10, 20]


def test_probe_3_keyword_collisions_random_and_open(tmp_path):
    out_file = (tmp_path / "probe_output.txt").as_posix()
    code = f"""
    use python module random
    random.seed(42)
    rnd_val = random.randint(1, 100)

    # random number phrase still works
    random number between 1 and 10 into rolled

    # with open(...) as f: works
    with open("{out_file}", "w") as f:
        f.write("doomscript probe success")

    with open("{out_file}", "r") as f:
        read_back = f.read()
    """
    env = run_code(code)
    assert 1 <= env["rnd_val"] <= 100
    assert 1 <= env["rolled"] <= 10
    assert env["read_back"] == "doomscript probe success"


def test_probe_4_builtin_shadowing():
    code = """
    s_desc = sorted([3, 1, 2], key=lambda v: -v)
    s_rev = sorted([3, 1, 2], reverse=True)
    m_key = min([3, 1, 2], key=lambda v: -v)
    m_max = max([3, 1, 2], key=lambda v: -v)
    s_sum = sum([1, 2, 3], 100)
    r_val = round(3.14159, 2)
    l_val = len([10, 20, 30])
    """
    env = run_code(code)
    assert env["s_desc"] == [3, 2, 1]
    assert env["s_rev"] == [3, 2, 1]
    assert env["m_key"] == 3
    assert env["m_max"] == 1
    assert env["s_sum"] == 106
    assert env["r_val"] == 3.14
    assert env["l_val"] == 3


def test_probe_5_syntax_gaps():
    code = """
    name = "Citadel"
    greeting = f"Welcome to {name}!"
    title = f"{name} Station"

    xs = [1, 2, 3, 4]
    dev = standard deviation of xs
    var_val = variance of xs

    standard deviation of xs into stmt_dev
    """
    env = run_code(code)
    assert env["greeting"] == "Welcome to Citadel!"
    assert env["title"] == "Citadel Station"
    assert abs(env["dev"] - 1.290994) < 1e-4
    assert abs(env["var_val"] - 1.666666) < 1e-4
    assert abs(env["stmt_dev"] - 1.290994) < 1e-4
