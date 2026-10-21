import pytest
from doomscript.compiler.engine import execute


def test_unactivated_domain_does_not_hijack():
    # Without 'use sim', Markov chain simulation shouldn't be executed by domain matcher
    code = """trans_matrix = [[0.8, 0.2], [0.4, 0.6]]
simulate markov chain with transitions trans_matrix and steps 10 from state 0 into history
"""
    with pytest.raises(Exception):
        execute(code)


def test_activated_domain_works():
    code = """use sim
trans_matrix = [[0.8, 0.2], [0.4, 0.6]]
simulate markov chain with transitions trans_matrix and steps 10 from state 0 into history
"""
    env = execute(code)
    assert len(env["history"]) == 11


def test_compilation_unit_isolation():
    # 1. Run a script with 'use sim'
    execute("use sim\n")
    # 2. Next execution without 'use sim' must start with fresh active domains and fail
    code = "simulate markov chain with transitions [[1.0]] and steps 1 from state 0 into h\n"
    with pytest.raises(Exception):
        execute(code)
