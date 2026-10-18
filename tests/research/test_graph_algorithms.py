"""
Tests for DoomScript Research graph algorithms and dynamic programming.
"""

import pytest
from doomscript.research.graph import (
    ResearchGraph,
    dijkstra_shortest_path,
    bellman_ford,
    floyd_warshall,
    topological_sort,
    edmonds_karp_max_flow,
    NegativeEdgeWeightError,
    NegativeCycleError,
)
from doomscript.research.algorithms import (
    levenshtein_distance,
    longest_common_subsequence,
    knapsack_01,
)


def test_dijkstra_negative_edge_rejection():
    g = ResearchGraph()
    g.add_edge("A", "B", -2.0)
    with pytest.raises(NegativeEdgeWeightError, match="Dijkstra does not support negative edge weights"):
        dijkstra_shortest_path(g, "A", "B")


def test_dijkstra_shortest_path_and_tie_breaking():
    g = ResearchGraph()
    # Add nodes in specific order
    g.add_node("A")
    g.add_node("B")
    g.add_node("C")
    g.add_node("D")

    # A -> B (weight 1), A -> C (weight 1)
    # B -> D (weight 2), C -> D (weight 2)
    # Both A -> B -> D and A -> C -> D have total weight 3.
    # Because B was inserted before C, B should be expanded first and tie-break to A -> B -> D.
    g.add_edge("A", "B", 1.0)
    g.add_edge("A", "C", 1.0)
    g.add_edge("B", "D", 2.0)
    g.add_edge("C", "D", 2.0)

    dist, path = dijkstra_shortest_path(g, "A", "D")
    assert dist == 3.0
    assert path == ["A", "B", "D"]


def test_bellman_ford_shortest_paths():
    g = ResearchGraph()
    g.add_edge("A", "B", 4.0)
    g.add_edge("A", "C", 2.0)
    g.add_edge("C", "B", 1.0)
    g.add_edge("B", "D", 5.0)
    g.add_edge("C", "D", 8.0)
    g.add_edge("C", "E", 10.0)
    g.add_edge("D", "E", -2.0)

    distances, predecessors = bellman_ford(g, "A")
    assert distances["A"] == 0.0
    assert distances["B"] == 3.0
    assert distances["C"] == 2.0
    assert distances["D"] == 8.0
    assert distances["E"] == 6.0


def test_bellman_ford_negative_cycle():
    g = ResearchGraph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -2.0)
    g.add_edge("C", "A", -1.0)
    with pytest.raises(NegativeCycleError, match="negative weight cycle"):
        bellman_ford(g, "A")


def test_floyd_warshall_all_pairs():
    g = ResearchGraph()
    g.add_edge("A", "B", 3.0)
    g.add_edge("A", "C", 8.0)
    g.add_edge("B", "C", 2.0)
    g.add_edge("C", "A", 1.0)

    dist_matrix = floyd_warshall(g)
    assert dist_matrix["A"]["B"] == 3.0
    assert dist_matrix["A"]["C"] == 5.0
    assert dist_matrix["C"]["B"] == 4.0
    assert dist_matrix["B"]["A"] == 3.0


def test_topological_sort_deterministic():
    g = ResearchGraph()
    # Nodes in insertion order
    for n in ["Task1", "Task2", "Task3", "Task4"]:
        g.add_node(n)

    # Task1 -> Task3, Task2 -> Task4
    # Valid topological sorts: [Task1, Task2, Task3, Task4], [Task2, Task1, Task4, Task3], etc.
    # Deterministic tie-breaking by insertion order guarantees Task1 before Task2.
    g.add_edge("Task1", "Task3")
    g.add_edge("Task2", "Task4")

    order = topological_sort(g)
    assert order == ["Task1", "Task2", "Task3", "Task4"]

    # Cycle detection
    g_cycle = ResearchGraph()
    g_cycle.add_edge("X", "Y")
    g_cycle.add_edge("Y", "X")
    with pytest.raises(ValueError, match="cycle"):
        topological_sort(g_cycle)


def test_edmonds_karp_max_flow():
    g = ResearchGraph()
    # Classic flow network: S -> A (10), S -> C (10), A -> B (4), A -> C (2), A -> D (8),
    # C -> D (9), B -> T (10), D -> T (10)
    g.add_edge("S", "A", 10.0)
    g.add_edge("S", "C", 10.0)
    g.add_edge("A", "B", 4.0)
    g.add_edge("A", "C", 2.0)
    g.add_edge("A", "D", 8.0)
    g.add_edge("C", "D", 9.0)
    g.add_edge("B", "T", 10.0)
    g.add_edge("D", "T", 10.0)

    max_flow = edmonds_karp_max_flow(g, "S", "T")
    assert max_flow == 14.0

    # CLRS Figure 26.1 classic 6-node network: max flow = 23
    clrs = ResearchGraph()
    clrs.add_edge("s", "v1", 16.0)
    clrs.add_edge("s", "v2", 13.0)
    clrs.add_edge("v1", "v3", 12.0)
    clrs.add_edge("v2", "v1", 4.0)
    clrs.add_edge("v2", "v4", 14.0)
    clrs.add_edge("v3", "v2", 9.0)
    clrs.add_edge("v3", "t", 20.0)
    clrs.add_edge("v4", "v3", 7.0)
    clrs.add_edge("v4", "t", 4.0)
    assert edmonds_karp_max_flow(clrs, "s", "t") == 23.0


def test_dp_algorithms():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("rosettacode", "raisethysword") == 8
    assert levenshtein_distance("", "abc") == 3
    assert levenshtein_distance("abc", "abc") == 0

    assert longest_common_subsequence("ABCBDAB", "BDCAB") == "BCAB"
    assert longest_common_subsequence("AGGTAB", "GXTXAYB") == "GTAB"

    max_val, items = knapsack_01([2, 3, 4], [3, 4, 5], capacity=5)
    assert max_val == 7
    assert set(items) == {0, 1}
