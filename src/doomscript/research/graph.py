"""
Graph data structures and algorithms with deterministic tie-breaking.
"""

from __future__ import annotations
import heapq
from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Set


class NegativeEdgeWeightError(ValueError):
    """Raised when an algorithm that requires non-negative edge weights (like Dijkstra) encounters a negative weight."""
    pass


class NegativeCycleError(ValueError):
    """Raised when a graph contains a negative weight cycle reachable during shortest path search."""
    pass


class ResearchGraph:
    """
    Deterministic directed graph data structure with insertion-order tracking for reproducible tie-breaking.
    """

    def __init__(self, directed: bool = True):
        self.directed = directed
        self._nodes: Dict[Any, int] = {}  # node -> insertion_index
        self._adj: Dict[Any, Dict[Any, float]] = {}  # node -> {neighbor: weight}

    def add_node(self, node: Any) -> None:
        if node not in self._nodes:
            self._nodes[node] = len(self._nodes)
            self._adj[node] = {}

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        self.add_node(u)
        self.add_node(v)
        w = float(weight)
        self._adj[u][v] = w
        if not self.directed:
            self._adj[v][u] = w

    @property
    def nodes(self) -> List[Any]:
        """Returns nodes in insertion order."""
        return list(self._nodes.keys())

    def node_order(self, node: Any) -> int:
        return self._nodes.get(node, -1)

    def neighbors(self, node: Any) -> Dict[Any, float]:
        return dict(self._adj.get(node, {}))

    def has_node(self, node: Any) -> bool:
        return node in self._nodes

    def has_edge(self, u: Any, v: Any) -> bool:
        return u in self._adj and v in self._adj[u]

    def weight(self, u: Any, v: Any) -> Optional[float]:
        return self._adj.get(u, {}).get(v)

    def edges(self) -> List[Tuple[Any, Any, float]]:
        res = []
        for u in self.nodes:
            for v, w in self._adj[u].items():
                res.append((u, v, w))
        return res

    def __len__(self) -> int:
        return len(self._nodes)

    def __contains__(self, node: Any) -> bool:
        return node in self._nodes

    def __repr__(self) -> str:
        return f"ResearchGraph({len(self._nodes)} nodes, {len(self.edges())} edges)"


def dijkstra_shortest_path(graph: ResearchGraph, src: Any, dst: Any) -> Tuple[float, List[Any]]:
    """
    Finds shortest path between src and dst using Dijkstra's algorithm.
    Enforces non-negative edge weights and deterministic insertion-order tie-breaking.
    """
    if not graph.has_node(src) or not graph.has_node(dst):
        raise ValueError("Source or destination node not found in graph.")

    # Check for negative edges across the graph
    for u in graph.nodes:
        for v, w in graph.neighbors(u).items():
            if w < 0:
                raise NegativeEdgeWeightError(
                    f"Dijkstra does not support negative edge weights: found weight {w} between {u} and {v}"
                )

    if src == dst:
        return (0.0, [src])

    # Priority queue stores tuples of: (distance, node_insertion_order, node)
    dist: Dict[Any, float] = {node: float("inf") for node in graph.nodes}
    pred: Dict[Any, Optional[Any]] = {node: None for node in graph.nodes}
    dist[src] = 0.0

    pq: List[Tuple[float, int, Any]] = [(0.0, graph.node_order(src), src)]
    visited: Set[Any] = set()

    while pq:
        d, _, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)

        if u == dst:
            break

        # Iterate through neighbors in deterministic insertion order
        neighbor_items = sorted(graph.neighbors(u).items(), key=lambda item: graph.node_order(item[0]))
        for v, weight in neighbor_items:
            if v in visited:
                continue
            new_dist = d + weight
            if new_dist < dist[v]:
                dist[v] = new_dist
                pred[v] = u
                heapq.heappush(pq, (new_dist, graph.node_order(v), v))

    if dist[dst] == float("inf"):
        return (float("inf"), [])

    # Reconstruct path
    path = []
    curr = dst
    while curr is not None:
        path.append(curr)
        curr = pred[curr]
    path.reverse()
    return (dist[dst], path)


def bellman_ford(graph: ResearchGraph, src: Any) -> Tuple[Dict[Any, float], Dict[Any, Optional[Any]]]:
    """
    Bellman-Ford algorithm for single-source shortest paths on graphs with arbitrary edge weights.
    Detects reachable negative weight cycles.
    """
    if not graph.has_node(src):
        raise ValueError("Source node not found in graph.")

    nodes = graph.nodes
    dist: Dict[Any, float] = {n: float("inf") for n in nodes}
    pred: Dict[Any, Optional[Any]] = {n: None for n in nodes}
    dist[src] = 0.0

    # Sort edges deterministically by source and destination insertion orders
    edges = sorted(
        graph.edges(),
        key=lambda e: (graph.node_order(e[0]), graph.node_order(e[1])),
    )

    n_vertices = len(nodes)
    # Relax edges |V| - 1 times
    for _ in range(n_vertices - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                updated = True
        if not updated:
            break

    # |V|-th iteration: check for negative cycles
    for u, v, w in edges:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            raise NegativeCycleError(
                f"Graph contains a negative weight cycle reachable from source {src}"
            )

    return (dist, pred)


def floyd_warshall(graph: ResearchGraph) -> Dict[Any, Dict[Any, float]]:
    """
    Computes all-pairs shortest paths using Floyd-Warshall algorithm.
    """
    nodes = graph.nodes
    dist: Dict[Any, Dict[Any, float]] = {u: {v: float("inf") for v in nodes} for u in nodes}

    for u in nodes:
        dist[u][u] = 0.0
        for v, w in graph.neighbors(u).items():
            dist[u][v] = min(dist[u][v], w)

    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] != float("inf") and dist[k][j] != float("inf"):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]

    return dist


def topological_sort(graph: ResearchGraph) -> List[Any]:
    """
    Returns a topological sort of a DAG using Kahn's algorithm.
    Ties between in-degree 0 nodes are broken deterministically by node insertion order.
    Raises ValueError if a cycle is detected.
    """
    nodes = graph.nodes
    indegree: Dict[Any, int] = {n: 0 for n in nodes}
    for u in nodes:
        for v in graph.neighbors(u):
            indegree[v] += 1

    # Deterministic priority queue using insertion order
    zero_in = [(graph.node_order(n), n) for n in nodes if indegree[n] == 0]
    heapq.heapify(zero_in)

    order: List[Any] = []
    while zero_in:
        _, u = heapq.heappop(zero_in)
        order.append(u)
        for v in graph.neighbors(u):
            indegree[v] -= 1
            if indegree[v] == 0:
                heapq.heappush(zero_in, (graph.node_order(v), v))

    if len(order) != len(nodes):
        raise ValueError("Graph contains a cycle; topological sort undefined.")

    return order


def edmonds_karp_max_flow(graph: ResearchGraph, src: Any, sink: Any) -> float:
    """
    Computes maximum network flow from src to sink using Edmonds-Karp algorithm (BFS augmenting paths).
    """
    if not graph.has_node(src) or not graph.has_node(sink):
        raise ValueError("Source or sink not in graph.")
    if src == sink:
        return 0.0

    nodes = graph.nodes
    # Residual capacity map: res_cap[u][v]
    res_cap: Dict[Any, Dict[Any, float]] = {u: {v: 0.0 for v in nodes} for u in nodes}
    for u in nodes:
        for v, cap in graph.neighbors(u).items():
            res_cap[u][v] += max(0.0, cap)

    total_flow = 0.0

    while True:
        # BFS to find shortest augmenting path in terms of edge count
        parent: Dict[Any, Optional[Any]] = {n: None for n in nodes}
        visited: Set[Any] = {src}
        queue: deque[Any] = deque([src])

        path_found = False
        while queue:
            u = queue.popleft()
            if u == sink:
                path_found = True
                break

            # Visit neighbors in deterministic insertion order
            for v in nodes:
                if v not in visited and res_cap[u][v] > 1e-12:
                    visited.add(v)
                    parent[v] = u
                    queue.append(v)

        if not path_found:
            break

        # Find bottleneck capacity along path
        push_flow = float("inf")
        curr = sink
        while curr != src:
            p = parent[curr]
            push_flow = min(push_flow, res_cap[p][curr])
            curr = p

        # Augment flow along residual path
        curr = sink
        while curr != src:
            p = parent[curr]
            res_cap[p][curr] -= push_flow
            res_cap[curr][p] += push_flow
            curr = p

        total_flow += push_flow

    return total_flow
