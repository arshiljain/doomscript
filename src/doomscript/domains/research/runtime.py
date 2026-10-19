"""Runtime execution engine for Research & Scientific Graph Algorithms."""

from typing import Any, Dict, List, Optional, Set, Tuple
import hashlib
import heapq
from collections import deque
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.research.graph import (
    ResearchGraph,
    dijkstra_shortest_path as _core_dijkstra,
    bellman_ford as _core_bellman_ford,
    floyd_warshall as _core_floyd_warshall,
    topological_sort as _core_topological_sort,
    edmonds_karp_max_flow as _core_edmonds_karp,
    NegativeCycleError,
    NegativeEdgeWeightError,
)


def _to_research_graph(graph: Any) -> ResearchGraph:
    """Ensure input is a ResearchGraph instance, converting dict structures if necessary."""
    if isinstance(graph, ResearchGraph):
        return graph
    g = ResearchGraph()
    if isinstance(graph, dict):
        for u, neighbors in graph.items():
            g.add_node(u)
            if isinstance(neighbors, dict):
                for v, w in neighbors.items():
                    g.add_edge(u, v, float(w))
            elif isinstance(neighbors, (list, tuple, set)):
                for v in neighbors:
                    g.add_edge(u, v, 1.0)
    return g


def research_topological_sort(graph: Any) -> List[Any]:
    """Deterministic topological sort of a DAG with insertion-order tie-breaking."""
    g = _to_research_graph(graph)
    return _core_topological_sort(g)


def research_dijkstra_shortest_path(graph: Any, src: Any, dst: Any) -> Tuple[float, List[Any]]:
    """Dijkstra shortest path with deterministic tie-breaking. Returns (distance, path)."""
    g = _to_research_graph(graph)
    return _core_dijkstra(g, src, dst)


def research_bellman_ford(graph: Any, src: Any) -> Tuple[Dict[Any, float], Dict[Any, Optional[Any]]]:
    """Bellman-Ford single-source shortest paths with negative cycle detection."""
    g = _to_research_graph(graph)
    return _core_bellman_ford(g, src)


def research_floyd_warshall_all_pairs(graph: Any) -> Dict[Any, Dict[Any, float]]:
    """Floyd-Warshall all-pairs shortest paths matrix."""
    g = _to_research_graph(graph)
    return _core_floyd_warshall(g)


def research_edmonds_karp_max_flow(graph: Any, src: Any, sink: Any) -> float:
    """Maximum network flow from src to sink via Edmonds-Karp BFS augmenting paths."""
    g = _to_research_graph(graph)
    return _core_edmonds_karp(g, src, sink)


def research_hopcroft_karp_bipartite_matching(
    graph: Any, u_nodes: Any, v_nodes: Any
) -> Tuple[int, Dict[Any, Any]]:
    """
    Hopcroft-Karp algorithm for maximum cardinality bipartite matching in O(E sqrt(V)).
    Returns (matching_size, matching_dict).
    """
    g = _to_research_graph(graph)
    u_set = list(u_nodes)
    v_set = set(v_nodes)

    pair_u: Dict[Any, Optional[Any]] = {u: None for u in u_set}
    pair_v: Dict[Any, Optional[Any]] = {v: None for v in v_set}
    dist: Dict[Optional[Any], float] = {}

    def bfs() -> bool:
        queue = deque()
        for u in u_set:
            if pair_u[u] is None:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = float("inf")
        dist[None] = float("inf")

        while queue:
            u = queue.popleft()
            if dist[u] < dist[None]:
                for v in sorted(g.neighbors(u).keys(), key=lambda n: g.node_order(n)):
                    if v in v_set:
                        nxt = pair_v[v]
                        if dist.get(nxt, float("inf")) == float("inf"):
                            dist[nxt] = dist[u] + 1
                            queue.append(nxt)
        return dist[None] != float("inf")

    def dfs(u: Optional[Any]) -> bool:
        if u is not None:
            for v in sorted(g.neighbors(u).keys(), key=lambda n: g.node_order(n)):
                if v in v_set:
                    nxt = pair_v[v]
                    if dist.get(nxt, float("inf")) == dist[u] + 1:
                        if dfs(nxt):
                            pair_v[v] = u
                            pair_u[u] = v
                            return True
            dist[u] = float("inf")
            return False
        return True

    matching_size = 0
    while bfs():
        for u in u_set:
            if pair_u[u] is None and dfs(u):
                matching_size += 1

    matching = {u: v for u, v in pair_u.items() if v is not None}
    return matching_size, matching


def research_tarjan_strongly_connected(graph: Any) -> List[List[Any]]:
    """Tarjan's algorithm for Strongly Connected Components (SCCs) in a directed graph."""
    g = _to_research_graph(graph)
    idx = 0
    indices: Dict[Any, int] = {}
    lowlink: Dict[Any, int] = {}
    on_stack: Set[Any] = set()
    stack: List[Any] = []
    sccs: List[List[Any]] = []

    def strongconnect(v: Any):
        nonlocal idx
        indices[v] = idx
        lowlink[v] = idx
        idx += 1
        stack.append(v)
        on_stack.add(v)

        for w in sorted(g.neighbors(v).keys(), key=lambda n: g.node_order(n)):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                scc.append(w)
                if w == v:
                    break
            scc.reverse()
            sccs.append(scc)

    for node in g.nodes:
        if node not in indices:
            strongconnect(node)

    return sccs


def research_kruskal_minimum_spanning_tree(graph: Any) -> List[Tuple[Any, Any, float]]:
    """Kruskal's algorithm for Minimum Spanning Tree using Disjoint Set Union (DSU)."""
    g = _to_research_graph(graph)
    edges = g.edges()
    # Sort deterministically by weight, then u insertion order, then v insertion order
    sorted_edges = sorted(
        edges,
        key=lambda e: (e[2], g.node_order(e[0]), g.node_order(e[1])),
    )

    parent: Dict[Any, Any] = {n: n for n in g.nodes}

    def find(i: Any) -> Any:
        path = []
        curr = i
        while parent[curr] != curr:
            path.append(curr)
            curr = parent[curr]
        for node in path:
            parent[node] = curr
        return curr

    def union(i: Any, j: Any) -> bool:
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    mst = []
    for u, v, w in sorted_edges:
        if union(u, v):
            mst.append((u, v, w))

    return mst


def research_prim_minimum_spanning_tree(graph: Any) -> List[Tuple[Any, Any, float]]:
    """Prim's algorithm for Minimum Spanning Tree starting at the first node in insertion order."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    if not nodes:
        return []

    visited = {nodes[0]}
    mst = []
    pq: List[Tuple[float, int, int, Any, Any]] = []

    for v, w in g.neighbors(nodes[0]).items():
        heapq.heappush(pq, (w, g.node_order(nodes[0]), g.node_order(v), nodes[0], v))

    while pq and len(visited) < len(nodes):
        w, _, _, u, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        mst.append((u, v, w))

        for nxt, nxt_w in g.neighbors(v).items():
            if nxt not in visited:
                heapq.heappush(pq, (nxt_w, g.node_order(v), g.node_order(nxt), v, nxt))

    return mst


def research_graph_diameter(graph: Any) -> float:
    """Maximum shortest path distance between any pair of reachable nodes."""
    g = _to_research_graph(graph)
    dist = _core_floyd_warshall(g)
    max_d = 0.0
    for u in g.nodes:
        for v in g.nodes:
            if u != v:
                d = dist[u][v]
                if d != float("inf") and d > max_d:
                    max_d = d
    return max_d


def research_graph_radius(graph: Any) -> float:
    """Minimum eccentricity across all nodes in the graph."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    if not nodes:
        return 0.0
    dist = _core_floyd_warshall(g)
    eccentricities = []
    for u in nodes:
        reachable = [dist[u][v] for v in nodes if u != v and dist[u][v] != float("inf")]
        eccentricities.append(max(reachable) if reachable else 0.0)
    return min(eccentricities) if eccentricities else 0.0


def research_connected_components(graph: Any) -> List[List[Any]]:
    """Connected components treating the graph as undirected."""
    g = _to_research_graph(graph)
    adj: Dict[Any, Set[Any]] = {n: set() for n in g.nodes}
    for u in g.nodes:
        for v in g.neighbors(u):
            adj[u].add(v)
            adj[v].add(u)

    visited = set()
    components = []

    for n in g.nodes:
        if n not in visited:
            comp = []
            queue = deque([n])
            visited.add(n)
            while queue:
                curr = queue.popleft()
                comp.append(curr)
                for neighbor in sorted(adj[curr], key=lambda x: g.node_order(x)):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            components.append(comp)

    return components


def research_pagerank(graph: Any, damping: Any = 0.85, max_iter: Any = 100) -> Dict[Any, float]:
    """Deterministic PageRank with damping factor."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    n = len(nodes)
    if n == 0:
        return {}

    d = float(damping)
    m_iter = int(max_iter)
    rank = {node: 1.0 / n for node in nodes}

    # Precalculate in-edges and out-degrees
    in_edges: Dict[Any, List[Any]] = {node: [] for node in nodes}
    out_degree: Dict[Any, int] = {}
    for u in nodes:
        nbrs = list(g.neighbors(u).keys())
        out_degree[u] = len(nbrs)
        for v in nbrs:
            in_edges[v].append(u)

    for _ in range(m_iter):
        dangling_sum = sum(rank[u] for u in nodes if out_degree[u] == 0)
        new_rank = {}
        for v in nodes:
            incoming_sum = sum(rank[u] / out_degree[u] for u in in_edges[v])
            new_rank[v] = ((1.0 - d) / n) + (d * (incoming_sum + dangling_sum / n))

        diff = sum(abs(new_rank[k] - rank[k]) for k in nodes)
        rank = new_rank
        if diff < 1e-9:
            break

    # Normalize to sum exactly to 1.0
    total = sum(rank.values())
    if total > 0:
        return {k: v / total for k, v in rank.items()}
    return rank


def research_hits_algorithm(graph: Any, max_iter: Any = 100) -> Tuple[Dict[Any, float], Dict[Any, float]]:
    """Hyperlink-Induced Topic Search (HITS) calculating hubs and authorities."""
    import math
    g = _to_research_graph(graph)
    nodes = g.nodes
    n = len(nodes)
    if n == 0:
        return {}, {}

    m_iter = int(max_iter)
    auth = {node: 1.0 for node in nodes}
    hubs = {node: 1.0 for node in nodes}

    in_edges: Dict[Any, List[Any]] = {node: [] for node in nodes}
    out_edges: Dict[Any, List[Any]] = {node: list(g.neighbors(node).keys()) for node in nodes}
    for u in nodes:
        for v in out_edges[u]:
            in_edges[v].append(u)

    for _ in range(m_iter):
        # Update authorities
        for v in nodes:
            auth[v] = sum(hubs[u] for u in in_edges[v])
        norm_a = math.sqrt(sum(v * v for v in auth.values())) or 1.0
        for v in nodes:
            auth[v] /= norm_a

        # Update hubs
        for u in nodes:
            hubs[u] = sum(auth[v] for v in out_edges[u])
        norm_h = math.sqrt(sum(v * v for v in hubs.values())) or 1.0
        for u in nodes:
            hubs[u] /= norm_h

    return hubs, auth


def research_eulerian_circuit_hierholzer(graph: Any) -> List[Any]:
    """Hierholzer's algorithm to compute an Eulerian circuit or path in a directed graph."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    if not nodes:
        return []

    # Copy adjacency
    adj = {u: deque(sorted(g.neighbors(u).keys(), key=lambda n: g.node_order(n))) for u in nodes}
    in_deg = {u: 0 for u in nodes}
    out_deg = {u: len(adj[u]) for u in nodes}
    for u in nodes:
        for v in adj[u]:
            in_deg[v] += 1

    # Start node: find one with out_deg > in_deg, or first with out_deg > 0
    start = nodes[0]
    for u in nodes:
        if out_deg[u] > in_deg[u]:
            start = u
            break
        if out_deg[u] > 0 and start == nodes[0]:
            start = u

    curr_path = [start]
    circuit = []

    while curr_path:
        curr = curr_path[-1]
        if adj[curr]:
            nxt = adj[curr].popleft()
            curr_path.append(nxt)
        else:
            circuit.append(curr_path.pop())

    circuit.reverse()
    return circuit


def research_graph_isomorphism_hash(graph: Any) -> str:
    """Weisfeiler-Lehman 1-WL color refinement hash for graph isomorphism check."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    # Initial color is node degree
    colors = {u: f"deg_{len(g.neighbors(u))}" for u in nodes}

    for _ in range(3):
        new_colors = {}
        for u in nodes:
            neighbor_colors = sorted(colors[v] for v in g.neighbors(u))
            combined = f"{colors[u]}|{','.join(neighbor_colors)}"
            new_colors[u] = hashlib.sha256(combined.encode("utf-8")).hexdigest()[:12]
        colors = new_colors

    canonical = sorted(colors.values())
    return hashlib.sha256(";".join(canonical).encode("utf-8")).hexdigest()[:16]


def research_transitive_reduction(graph: Any) -> List[Tuple[Any, Any]]:
    """Compute transitive reduction of a DAG, returning minimal edge list preserving reachability."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    # Check all pairs reachability via DFS
    def reachable(src: Any, dst: Any, excluded_edge: Tuple[Any, Any]) -> bool:
        visited = set()
        stack = [src]
        while stack:
            u = stack.pop()
            if u == dst and u != src:
                return True
            for v in g.neighbors(u):
                if (u, v) != excluded_edge and v not in visited:
                    visited.add(v)
                    stack.append(v)
        return False

    reduced_edges = []
    for u, v, _ in g.edges():
        if not reachable(u, v, (u, v)):
            reduced_edges.append((u, v))

    return reduced_edges


def research_find_negative_cycle(graph: Any) -> List[Any]:
    """Detect and extract vertices of a negative weight cycle in the graph."""
    g = _to_research_graph(graph)
    nodes = g.nodes
    if not nodes:
        return []

    dist = {u: 0.0 for u in nodes}
    pred: Dict[Any, Optional[Any]] = {u: None for u in nodes}
    edges = g.edges()

    cycle_start = None
    for i in range(len(nodes)):
        cycle_start = None
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
                if i == len(nodes) - 1:
                    cycle_start = v

    if cycle_start is None:
        return []

    # Follow predecessors back |V| steps to ensure we enter the cycle
    curr = cycle_start
    for _ in range(len(nodes)):
        if pred[curr] is not None:
            curr = pred[curr]

    # Trace cycle until node repeats
    cycle = []
    start_cycle = curr
    while True:
        cycle.append(curr)
        curr = pred[curr]
        if curr == start_cycle or len(cycle) > len(nodes) + 1:
            break
    cycle.reverse()
    return cycle


def research_degree_distribution(graph: Any) -> Dict[str, Dict[int, int]]:
    """Compute in-degree and out-degree frequency distributions."""
    g = _to_research_graph(graph)
    in_counts: Dict[int, int] = {}
    out_counts: Dict[int, int] = {}

    in_deg = {u: 0 for u in g.nodes}
    for u in g.nodes:
        out_d = len(g.neighbors(u))
        out_counts[out_d] = out_counts.get(out_d, 0) + 1
        for v in g.neighbors(u):
            in_deg[v] = in_deg.get(v, 0) + 1

    for d in in_deg.values():
        in_counts[d] = in_counts.get(d, 0) + 1

    return {"in_degrees": in_counts, "out_degrees": out_counts}
