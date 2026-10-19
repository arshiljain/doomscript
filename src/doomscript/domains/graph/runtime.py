"""Runtime execution engine for Graph Analytics & Network Science domain."""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import heapq
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.graph.spec import (
    GraphCreateSpec,
    GraphAddNodeSpec,
    GraphAddEdgeSpec,
    GraphShortestPathSpec,
    GraphPageRankSpec,
    GraphDegreesSpec,
    GraphCommunitiesSpec,
)


class DoomGraph:
    """Ergonomic representation of directed or undirected graphs in DoomScript."""

    def __init__(self, directed: bool = False):
        self.directed = directed
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.adj: Dict[str, Dict[str, float]] = {}

    def add_node(self, node_id: Any, **attrs) -> None:
        nid = str(node_id)
        if nid not in self.nodes:
            self.nodes[nid] = {}
            self.adj[nid] = {}
        self.nodes[nid].update(attrs)

    def add_edge(self, u: Any, v: Any, weight: float = 1.0, **attrs) -> None:
        uid = str(u)
        vid = str(v)
        self.add_node(uid)
        self.add_node(vid)
        w = float(weight)
        self.adj[uid][vid] = w
        if not self.directed:
            self.adj[vid][uid] = w

    def shortest_path(self, start: Any, end: Any) -> List[str]:
        """Computes shortest path between start and end using Dijkstra's algorithm."""
        s = str(start)
        e = str(end)
        if s not in self.nodes or e not in self.nodes:
            return []
        if s == e:
            return [s]

        distances: Dict[str, float] = {s: 0.0}
        previous: Dict[str, Optional[str]] = {s: None}
        pq = [(0.0, s)]
        visited: Set[str] = set()

        while pq:
            d, cur = heapq.heappop(pq)
            if cur == e:
                break
            if cur in visited:
                continue
            visited.add(cur)

            for neighbor, weight in self.adj.get(cur, {}).items():
                if neighbor in visited:
                    continue
                new_d = d + weight
                if neighbor not in distances or new_d < distances[neighbor]:
                    distances[neighbor] = new_d
                    previous[neighbor] = cur
                    heapq.heappush(pq, (new_d, neighbor))

        if e not in previous:
            return []

        path = []
        curr = e
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()
        return path

    def pagerank(self, damping: float = 0.85, max_iter: int = 50) -> Dict[str, float]:
        """Computes PageRank centrality scores for all nodes."""
        n = len(self.nodes)
        if n == 0:
            return {}

        rank = {nid: 1.0 / n for nid in self.nodes}
        nodes_list = list(self.nodes.keys())

        for _ in range(max_iter):
            new_rank: Dict[str, float] = {nid: (1.0 - damping) / n for nid in nodes_list}
            for u in nodes_list:
                neighbors = self.adj.get(u, {})
                deg = len(neighbors)
                if deg > 0:
                    share = (damping * rank[u]) / deg
                    for v in neighbors:
                        new_rank[v] += share
                else:
                    # Dangling node distributed evenly
                    for v in nodes_list:
                        new_rank[v] += (damping * rank[u]) / n

            rank = new_rank

        return {k: round(v, 4) for k, v in rank.items()}

    def degrees(self) -> Dict[str, int]:
        """Returns node degree mapping."""
        return {nid: len(self.adj.get(nid, {})) for nid in self.nodes}

    def detect_communities(self) -> List[List[str]]:
        """Identifies connected components / graph clusters."""
        visited: Set[str] = set()
        components: List[List[str]] = []

        for nid in self.nodes:
            if nid not in visited:
                comp: List[str] = []
                queue = [nid]
                visited.add(nid)
                while queue:
                    cur = queue.pop(0)
                    comp.append(cur)
                    for neighbor in self.adj.get(cur, {}):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)

        return components

    def __repr__(self) -> str:
        kind = "Directed" if self.directed else "Undirected"
        return f"DoomGraph({kind}, nodes={len(self.nodes)}, edges={sum(len(e) for e in self.adj.values())})"


# Standalone Helper Functions
def create_graph(directed: bool = False) -> DoomGraph:
    return DoomGraph(directed=directed)


def add_graph_node(graph: DoomGraph, node_id: Any, **attrs) -> None:
    graph.add_node(node_id, **attrs)


def add_graph_edge(graph: DoomGraph, u: Any, v: Any, weight: float = 1.0, **attrs) -> None:
    graph.add_edge(u, v, weight=weight, **attrs)


def graph_shortest_path(graph: DoomGraph, start: Any, end: Any) -> List[str]:
    return graph.shortest_path(start, end)


def graph_pagerank(graph: DoomGraph) -> Dict[str, float]:
    return graph.pagerank()


def graph_degrees(graph: DoomGraph) -> Dict[str, int]:
    return graph.degrees()


def graph_communities(graph: DoomGraph) -> List[List[str]]:
    return graph.detect_communities()


class GraphRuntime(DomainRuntime):
    """Runtime execution engine for Graph Analytics specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Graph spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, GraphCreateSpec):
            return create_graph(directed=ir.directed)
        elif isinstance(ir, GraphAddNodeSpec):
            g = scope.get(ir.graph_var)
            add_graph_node(g, ir.node_id, **ir.attributes)
            return g
        elif isinstance(ir, GraphAddEdgeSpec):
            g = scope.get(ir.graph_var)
            add_graph_edge(g, ir.u, ir.v, weight=ir.weight, **ir.attributes)
            return g
        elif isinstance(ir, GraphShortestPathSpec):
            g = scope.get(ir.graph_var)
            return graph_shortest_path(g, ir.start_node, ir.end_node)
        elif isinstance(ir, GraphPageRankSpec):
            g = scope.get(ir.graph_var)
            return graph_pagerank(g)
        elif isinstance(ir, GraphDegreesSpec):
            g = scope.get(ir.graph_var)
            return graph_degrees(g)
        elif isinstance(ir, GraphCommunitiesSpec):
            g = scope.get(ir.graph_var)
            return graph_communities(g)

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_graph_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Graph spec not found: {spec_id}")
    return GraphRuntime().execute_ir(spec, {})
