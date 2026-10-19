"""Unit and integration tests for Graph Analytics & Network Science domain (use graph)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.graph.runtime import (
    DoomGraph,
    create_graph,
    add_graph_node,
    add_graph_edge,
    graph_shortest_path,
    graph_pagerank,
    graph_degrees,
    graph_communities,
)


def test_graph_runtime_direct():
    g = create_graph(directed=False)
    add_graph_node(g, "A")
    add_graph_node(g, "B")
    add_graph_node(g, "C")
    add_graph_edge(g, "A", "B", weight=1.0)
    add_graph_edge(g, "B", "C", weight=2.0)
    add_graph_edge(g, "A", "C", weight=10.0)

    # Shortest path
    sp = graph_shortest_path(g, "A", "C")
    assert sp == ["A", "B", "C"]

    # Degrees
    degs = graph_degrees(g)
    assert degs["B"] == 2
    assert degs["A"] == 2

    # PageRank
    pr = graph_pagerank(g)
    assert "A" in pr and "B" in pr and "C" in pr
    assert abs(sum(pr.values()) - 1.0) < 0.05

    # Communities
    comms = graph_communities(g)
    assert len(comms) == 1
    assert set(comms[0]) == {"A", "B", "C"}


def test_graph_domain_script_execution():
    source = """use graph

create directed graph into net
connect "A" to "B" with weight 1.5 in net
connect "B" to "C" with weight 2.0 in net
connect "C" to "D" with weight 1.0 in net
connect "A" to "D" with weight 10.0 in net

shortest path from "A" to "D" in net into best_route
pagerank of net into pr_scores
degrees of nodes in net into degree_map
detect communities in net into clusters
"""
    env = execute(source)
    assert env["best_route"] == ["A", "B", "C", "D"]
    assert "A" in env["pr_scores"]
    assert env["degree_map"]["A"] == 2
    assert len(env["clusters"]) >= 1


def test_graph_domain_python_export():
    source = """use graph

create graph into g
connect "X" to "Y" with weight 3 in g
shortest path from "X" to "Y" in g into sp
"""
    py_code = export_to_python(source)
    assert "create_graph" in py_code
    assert "add_graph_edge" in py_code
    assert "graph_shortest_path" in py_code
