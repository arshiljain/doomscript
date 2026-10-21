import pytest
import concurrent.futures
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


def test_block_routing_respects_active_domains():
    # Without 'use ml', a block header 'model my_model:' must not be hijacked by inactive ML domain
    code = """model my_fraud_model from transactions:
    target: risk
    features: amount
    algorithm: linear_regression
"""
    with pytest.raises(Exception):
        execute(code)


def test_concurrent_compilation_isolation():
    """Verifies that concurrent compilations across multiple threads maintain strict domain isolation without state corruption."""
    def run_sim():
        code = """use sim
trans_matrix = [[0.5, 0.5], [0.5, 0.5]]
simulate markov chain with transitions trans_matrix and steps 5 from state 0 into res
"""
        env = execute(code)
        assert len(env["res"]) == 6
        return True

    def run_unactivated():
        code = """simulate markov chain with transitions [[1.0]] and steps 1 from state 0 into h\n"""
        try:
            execute(code)
            return False  # Should have raised!
        except Exception:
            return True

    def run_arithmetic():
        code = """set x to 10
set y to 25
set z to x * y + 5
"""
        env = execute(code)
        assert env["z"] == 255
        return True

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for i in range(20):
            futures.append(executor.submit(run_sim))
            futures.append(executor.submit(run_unactivated))
            futures.append(executor.submit(run_arithmetic))

        for f in concurrent.futures.as_completed(futures):
            assert f.result() is True
