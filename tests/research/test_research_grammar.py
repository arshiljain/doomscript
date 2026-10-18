"""
Tests for DoomScript English research syntax and grammar integration.
"""

import pytest
from doomscript.compiler.engine import execute


def test_welch_t_test_in_english(capsys):
    code = """
use research
a = a list of 10.0, 11.0, 12.0, 10.5
b = a list of 20.0, 21.0, 20.5, 22.0
test that means of a and b are equal using welch t test into res
p = res's p value
say "P-value is under 0.01:", p is under 0.01
verify that p is under 0.001 otherwise "Significantly different"
"""
    execute(code)
    captured = capsys.readouterr()
    assert "P-value is under 0.01: True" in captured.out


def test_confidence_interval_expression(capsys):
    code = """
use research
data = a list of 10.0, 12.0, 11.0, 13.0, 10.5
ci = confidence interval of data at 95 percent
say "CI computed:", count of ci is 2
"""
    execute(code)
    captured = capsys.readouterr()
    assert "CI computed: True" in captured.out


def test_graph_and_dijkstra_in_english(capsys):
    code = """
use research
create a research graph into g
add edge from "A" to "B" with weight 4.0 to g
add edge from "A" to "C" with weight 2.0 to g
add edge from "C" to "B" with weight 1.0 to g
find shortest path from "A" to "B" in g using dijkstra into res
dist = item 1 of res
path = item 2 of res
say "Shortest distance is:", dist
"""
    execute(code)
    captured = capsys.readouterr()
    assert "Shortest distance is: 3.0" in captured.out


def test_dynamic_programming_in_english(capsys):
    code = """
use research
edit distance between "kitten" and "sitting" into d
lcs = longest common subsequence between "ABCBDAB" and "BDCAB"
say "Edit distance:", d
say "LCS:", lcs
"""
    execute(code)
    captured = capsys.readouterr()
    assert "Edit distance: 3" in captured.out
    assert "LCS: BCAB" in captured.out


def test_autograd_and_optimizer_in_english(capsys):
    code = """
use research
w = a scalar with value 5.0
create adam optimizer for a list of w with learning rate 0.1 into opt
compute gradient of (w - 1.0) ** 2
grad = w's gradient
say "Gradient:", grad > 0.0
step opt
say "Optimized:", w's value < 5.0
"""
    execute(code)
    captured = capsys.readouterr()
    assert "Gradient: True" in captured.out
    assert "Optimized: True" in captured.out
