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
    graph_eigenvector_centrality,
    graph_dijkstra_shortest_path,
    graph_bellman_ford,
    graph_floyd_warshall,
    graph_kruskal_mst,
    graph_prim_mst,
    graph_articulation_points,
    graph_bipartite_check,
    graph_max_flow_edmonds_karp,
    graph_radius,
    graph_clustering_coefficient,
    graph_transitivity,
    graph_density,
    graph_degree_histogram,
    graph_jaccard_similarity,
    graph_find_articulation_points,
    graph_jaccard_coefficient,
    graph_average_clustering_coefficient,
    graph_find_bridges,
    graph_eccentricity,
    graph_center,
    graph_is_tree,
    graph_transitive_closure,
    graph_k_core,
    graph_laplacian_matrix,
    graph_bron_kerbosch_cliques,
    graph_louvain_communities,
    graph_betweenness_centrality,
    graph_tarjan_scc,
    graph_mst,
    graph_johnson_apsp,
    graph_hopcroft_karp,
    graph_eulerian_path,
    graph_boruvka_mst,
    HopcroftKarpBipartiteMatching,
    TarjanBridgeAndArticulation,
    HierholzerEulerianCircuit,
    graph_bipartite_matching,
    graph_find_bridges_and_cuts,
    graph_eulerian_trail,
    PushRelabelMaxFlow,
    JohnsonsAllPairsShortestPaths,
    graph_push_relabel_max_flow,
    graph_johnson_all_pairs_paths,
    BronKerboschMaximalCliques,
    LengauerTarjanDominatorTree,
    graph_bron_kerbosch_degeneracy_cliques,
    graph_lengauer_tarjan_dominators,
    EdmondsBlossomMaximumWeightMatching,
    PageRankRandomWalkWithRestart,
    graph_edmonds_blossom_matching,
    graph_pagerank_calculate,
    graph_pagerank_calculate_graph,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.graph.exporter import GraphASTExporter
from doomscript.domains.registry import get_domain_registry


class GraphDomain(DomainContract):
    """Graph Analytics & Network Science domain pack."""

    name = "graph"
    aliases = ["network", "graph_theory"]
    description = "Graph Analytics, shortest paths, PageRank, degree centrality, community detection"
    parser = GraphDomainParser()
    runtime = GraphRuntime()
    exporter = GraphASTExporter()
    capabilities = ["graph", "pagerank", "shortest_path", "communities", "degrees"]
    optional_dependencies = ["networkx"]

    verbs = [
        VerbSpec(
            name="create_graph",
            pattern="create (graph|directed graph|undirected graph) into {target:ident}",
            arg_schema={"target": "ident"},
            returns="Graph",
            description="Create an empty directed or undirected graph",
        ),
        VerbSpec(
            name="add_node",
            pattern="add node {node_id:expr} to [graph] {g_var:ident}",
            arg_schema={"node_id": "expr", "g_var": "ident"},
            returns="None",
            description="Add node vertex to graph",
        ),
        VerbSpec(
            name="connect_nodes",
            pattern="connect [node] {u:expr} to [node] {v:expr} in [graph] {g_var:ident} [with weight {w:expr}]",
            arg_schema={"u": "expr", "v": "expr", "g_var": "ident"},
            returns="None",
            description="Add directed or undirected edge between two nodes",
        ),
        VerbSpec(
            name="shortest_path",
            pattern="shortest path from {u:expr} to {v:expr} in [graph] {g_var:ident} into {target:ident}",
            arg_schema={"u": "expr", "v": "expr", "g_var": "ident", "target": "ident"},
            returns="Collection",
            description="Compute Dijkstra / BFS shortest path node sequence",
        ),
        VerbSpec(
            name="pagerank",
            pattern="pagerank of [graph] {g_var:ident} into {target:ident}",
            arg_schema={"g_var": "ident", "target": "ident"},
            returns="Record",
            description="Compute Google PageRank centrality for all nodes",
        ),
        VerbSpec(
            name="degrees",
            pattern="degrees of nodes in [graph] {g_var:ident} into {target:ident}",
            arg_schema={"g_var": "ident", "target": "ident"},
            returns="Record",
            description="Compute degree distribution of graph",
        ),
        VerbSpec(
            name="communities",
            pattern="detect communities in [graph] {g_var:ident} into {target:ident}",
            arg_schema={"g_var": "ident", "target": "ident"},
            returns="Collection",
            description="Partition network into Louvain community clusters",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        if (
            s.startswith("create graph ")
            or s.startswith("create empty graph ")
            or s.startswith("create directed graph ")
            or s.startswith("create undirected graph ")
            or s.startswith("add node ")
            or s.startswith("pagerank of ")
            or s.startswith("degrees of nodes in ")
            or s.startswith("detect communities in ")
            or s.startswith("degree centrality of ")
            or s.startswith("betweenness centrality of ")
            or s.startswith("closeness centrality of ")
            or (" is bipartite into " in s)
            or s.startswith("find eulerian path in ")
            or s.startswith("eulerian path in ")
            or s.startswith("strongly connected components of ")
            or s.startswith("diameter of ")
            or s.startswith("eigenvector centrality of ")
            or s.startswith("bellman ford ")
            or s.startswith("floyd warshall in ")
            or s.startswith("all pairs shortest paths using floyd warshall in ")
            or s.startswith("minimum spanning tree of ")
            or s.startswith("kruskal ")
            or s.startswith("prim ")
            or s.startswith("articulation points of ")
            or s.startswith("find articulation points of ")
            or s.startswith("bridges in ")
            or s.startswith("find bridges in ")
            or s.startswith("maximum flow in ")
            or s.startswith("max flow in ")
            or s.startswith("radius of ")
            or s.startswith("center of ")
            or s.startswith("clustering coefficient of ")
            or s.startswith("transitivity of ")
            or s.startswith("density of ")
            or s.startswith("degree histogram of ")
            or s.startswith("jaccard similarity ")
            or s.startswith("eccentricity of ")
            or (" is tree into " in s)
            or s.startswith("transitive closure of ")
            or s.startswith("k core of ")
            or s.startswith("laplacian matrix of ")
        ):
            return True

        if s.startswith("connect ") and " to " in s and " in " in s:
            return True
        if s.startswith("shortest path ") and " in " in s:
            return True
        if s.startswith("dijkstra shortest path in ") and " in " in s:
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
    "graph_eigenvector_centrality",
    "graph_dijkstra_shortest_path",
    "graph_bellman_ford",
    "graph_floyd_warshall",
    "graph_kruskal_mst",
    "graph_prim_mst",
    "graph_articulation_points",
    "graph_bipartite_check",
    "graph_max_flow_edmonds_karp",
    "graph_radius",
    "graph_clustering_coefficient",
    "graph_transitivity",
    "graph_density",
    "graph_degree_histogram",
    "graph_jaccard_similarity",
    "graph_find_articulation_points",
    "graph_jaccard_coefficient",
    "graph_average_clustering_coefficient",
    "graph_find_bridges",
    "graph_eccentricity",
    "graph_center",
    "graph_is_tree",
    "graph_transitive_closure",
    "graph_k_core",
    "graph_laplacian_matrix",
    "graph_bron_kerbosch_cliques",
    "graph_louvain_communities",
    "graph_betweenness_centrality",
    "graph_tarjan_scc",
    "graph_mst",
    "graph_johnson_apsp",
    "graph_hopcroft_karp",
    "graph_eulerian_path",
    "graph_boruvka_mst",
    "HopcroftKarpBipartiteMatching",
    "TarjanBridgeAndArticulation",
    "HierholzerEulerianCircuit",
    "graph_bipartite_matching",
    "graph_find_bridges_and_cuts",
    "graph_eulerian_trail",
    "PushRelabelMaxFlow",
    "JohnsonsAllPairsShortestPaths",
    "graph_push_relabel_max_flow",
    "graph_johnson_all_pairs_paths",
    "BronKerboschMaximalCliques",
    "LengauerTarjanDominatorTree",
    "graph_bron_kerbosch_degeneracy_cliques",
    "graph_lengauer_tarjan_dominators",
    "EdmondsBlossomMaximumWeightMatching",
    "PageRankRandomWalkWithRestart",
    "graph_edmonds_blossom_matching",
    "graph_pagerank_calculate",
    "graph_pagerank_calculate_graph",
]

