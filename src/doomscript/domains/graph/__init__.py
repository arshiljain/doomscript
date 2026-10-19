"""Graph Analytics & Network Science Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.graph.spec import (
    GraphCreateSpec,
    GraphAddNodeSpec,
    GraphAddEdgeSpec,
    GraphShortestPathSpec,
    GraphPageRankSpec,
    GraphDegreesSpec,
    GraphCommunitiesSpec,
)
from doomscript.domains.graph.parser import GraphDomainParser
from doomscript.domains.graph.runtime import (
    DoomGraph,
    GraphRuntime,
    create_graph,
    add_graph_node,
    add_graph_edge,
    graph_shortest_path,
    graph_pagerank,
    graph_degrees,
    graph_communities,
    execute_graph_ir,
)
from doomscript.domains.graph.exporter import GraphASTExporter
from doomscript.domains.registry import get_domain_registry


class GraphDomain(DomainContract):
    """Graph Analytics & Network Science domain pack."""

    name = "graph"
    aliases = ["network", "graph_theory"]
    parser = GraphDomainParser()
    runtime = GraphRuntime()
    exporter = GraphASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("create graph ")
            or s.startswith("create directed graph ")
            or s.startswith("create undirected graph ")
            or s.startswith("add node ")
            or s.startswith("pagerank of ")
            or s.startswith("degrees of nodes in ")
            or s.startswith("detect communities in ")
        ):
            return True

        if s.startswith("connect ") and " to " in s and " in " in s:
            return True
        if s.startswith("shortest path from ") and " to " in s and " in " in s:
            return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
GRAPH_DOMAIN = GraphDomain()
get_domain_registry().register(GRAPH_DOMAIN)

__all__ = [
    "GraphDomain",
    "GRAPH_DOMAIN",
    "GraphCreateSpec",
    "GraphAddNodeSpec",
    "GraphAddEdgeSpec",
    "GraphShortestPathSpec",
    "GraphPageRankSpec",
    "GraphDegreesSpec",
    "GraphCommunitiesSpec",
    "GraphDomainParser",
    "GraphRuntime",
    "GraphASTExporter",
    "DoomGraph",
    "create_graph",
    "add_graph_node",
    "add_graph_edge",
    "graph_shortest_path",
    "graph_pagerank",
    "graph_degrees",
    "graph_communities",
    "execute_graph_ir",
]
