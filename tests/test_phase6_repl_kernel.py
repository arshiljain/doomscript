"""
Tests for Phase 6: Multi-line REPL & Interactive Kernel
Validates cell execution with captured output, environment persistence,
and multi-line block continuation detection.
"""

from doomscript.kernel import run_cell, is_block_continuation_needed


def test_cell_execution_and_persistent_env():
    # Cell 1: define variables
    out1, env = run_cell('score = 50\nsay "Initial score:", score')
    assert "Initial score: 50" in out1
    assert env["score"] == 50

    # Cell 2: mutate variable from previous cell
    out2, env = run_cell('increase score by 25\nsay "Updated score:", score', env=env)
    assert "Updated score: 75" in out2
    assert env["score"] == 75

    # Cell 3: define and call function
    cell3_code = """
    to double_score with val:
        return val * 2
    doubled = double_score(score)
    say "Doubled:", doubled
    """
    out3, env = run_cell(cell3_code, env=env)
    assert "Doubled: 150" in out3
    assert env["doubled"] == 150


def test_block_continuation_detector():
    # Single-line complete statements
    assert not is_block_continuation_needed('say "Hello"')
    assert not is_block_continuation_needed('score = 100')

    # Block starters needing continuation
    assert is_block_continuation_needed('repeat 5 times:')
    assert is_block_continuation_needed('if score is greater than 10:')
    assert is_block_continuation_needed('for each item in items:')
    assert is_block_continuation_needed('to compute with x:')
    assert is_block_continuation_needed('try:')

    # Unclosed brackets
    assert is_block_continuation_needed('items = [1, 2,')
    assert is_block_continuation_needed('data = {name: "Doom",')
