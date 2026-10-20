"""Runtime execution engine for Graph Analytics & Network Science domain."""

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import heapq
from doomscript.runtime import Record
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


# --- Batch 7 Spoken English Graph Verbs ---

def _ensure_graph(g: Any) -> DoomGraph:
    """Coerce various graph representations into a DoomGraph instance."""
    if isinstance(g, DoomGraph):
        return g
    graph = DoomGraph(directed=False)
    if isinstance(g, dict):
        for u, neighbors in g.items():
            graph.add_node(u)
            if isinstance(neighbors, dict):
                for v, w in neighbors.items():
                    graph.add_edge(u, v, weight=float(w))
            elif isinstance(neighbors, (list, tuple, set)):
                for v in neighbors:
                    graph.add_edge(u, v, weight=1.0)
    elif isinstance(g, (list, tuple)):
        for edge in g:
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                w = float(edge[2]) if len(edge) > 2 else 1.0
                graph.add_edge(edge[0], edge[1], weight=w)
    return graph


def graph_degree_centrality(g: Any) -> Dict[str, float]:
    """Calculate normalized degree centrality for all nodes."""
    graph = _ensure_graph(g)
    n = len(graph.nodes)
    if n <= 1:
        return {nid: 1.0 for nid in graph.nodes}
    denom = float(n - 1)
    return {nid: round(len(graph.adj.get(nid, {})) / denom, 4) for nid in graph.nodes}


def graph_betweenness_centrality(g: Any) -> Dict[str, float]:
    """Compute Brandes betweenness centrality for all nodes."""
    from collections import deque
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    cb = {v: 0.0 for v in nodes}
    n = len(nodes)
    if n <= 2:
        return {v: 0.0 for v in nodes}

    for s in nodes:
        S = []
        P: Dict[str, List[str]] = {w: [] for w in nodes}
        sigma = {w: 0 for w in nodes}
        sigma[s] = 1
        d = {w: -1 for w in nodes}
        d[s] = 0
        Q = deque([s])

        while Q:
            v = Q.popleft()
            S.append(v)
            for w in graph.adj.get(v, {}):
                if d[w] < 0:
                    Q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    P[w].append(v)

        delta = {w: 0.0 for w in nodes}
        while S:
            w = S.pop()
            for v in P[w]:
                if sigma[w] != 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]

    scale = 1.0 / ((n - 1) * (n - 2)) if not graph.directed else 1.0 / ((n - 1) * (n - 2))
    if not graph.directed:
        for v in cb:
            cb[v] = round(cb[v] * 0.5 * scale * 2.0, 4)
    else:
        for v in cb:
            cb[v] = round(cb[v] * scale, 4)
    return cb


def graph_closeness_centrality(g: Any) -> Dict[str, float]:
    """Compute closeness centrality for each node."""
    from collections import deque
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    n = len(nodes)
    closeness = {}
    for s in nodes:
        dists = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            for v in graph.adj.get(u, {}):
                if v not in dists:
                    dists[v] = dists[u] + 1
                    q.append(v)
        reachable = len(dists) - 1
        tot_dist = sum(dists.values())
        if tot_dist > 0 and reachable > 0:
            score = (reachable / float(n - 1)) * (reachable / float(tot_dist))
            closeness[s] = round(score, 4)
        else:
            closeness[s] = 0.0
    return closeness


def graph_is_bipartite(g: Any) -> bool:
    """Check if graph is 2-colorable (bipartite) using BFS."""
    from collections import deque
    graph = _ensure_graph(g)
    color: Dict[str, int] = {}
    for start in graph.nodes:
        if start not in color:
            color[start] = 0
            q = deque([start])
            while q:
                u = q.popleft()
                for v in graph.adj.get(u, {}):
                    if v not in color:
                        color[v] = 1 - color[u]
                        q.append(v)
                    elif color[v] == color[u]:
                        return False
    return True


def graph_find_eulerian_path(g: Any) -> List[str]:
    """Find Eulerian path or circuit using Hierholzer's algorithm."""
    graph = _ensure_graph(g)
    if not graph.nodes:
        return []

    # Count degrees
    adj_copy: Dict[str, List[str]] = {u: list(neighbors.keys()) for u, neighbors in graph.adj.items()}
    deg = {u: len(neighbors) for u, neighbors in adj_copy.items()}
    odd_nodes = [u for u, d in deg.items() if d % 2 != 0]

    if len(odd_nodes) not in (0, 2):
        return []

    start = odd_nodes[0] if odd_nodes else next(iter(graph.nodes))
    curr_path = [start]
    circuit = []

    while curr_path:
        curr_v = curr_path[-1]
        if adj_copy.get(curr_v):
            next_v = adj_copy[curr_v].pop()
            if not graph.directed and curr_v in adj_copy.get(next_v, []):
                adj_copy[next_v].remove(curr_v)
            curr_path.append(next_v)
        else:
            circuit.append(curr_path.pop())

    circuit.reverse()
    return circuit


def graph_strongly_connected_components(g: Any) -> List[List[str]]:
    """Find strongly connected components using Tarjan's algorithm."""
    graph = _ensure_graph(g)
    index = 0
    indices: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    on_stack: Set[str] = set()
    stack: List[str] = []
    sccs: List[List[str]] = []

    def strongconnect(v: str):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in graph.adj.get(v, {}):
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
            sccs.append(sorted(scc))

    for node in graph.nodes:
        if node not in indices:
            strongconnect(node)

    return sccs


def graph_diameter(g: Any) -> int:
    """Calculate the maximum shortest path distance across all connected components."""
    from collections import deque
    graph = _ensure_graph(g)
    if not graph.nodes:
        return 0
    max_d = 0
    for s in graph.nodes:
        dists = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            d = dists[u]
            if d > max_d:
                max_d = d
            for v in graph.adj.get(u, {}):
                if v not in dists:
                    dists[v] = d + 1
                    q.append(v)
    return max_d


# 350-Expansion Graph Algorithms

def graph_eigenvector_centrality(g: Any, max_iter: int = 100) -> Dict[str, float]:
    """Compute eigenvector centrality using power iteration."""
    import math
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    n = len(nodes)
    if n == 0:
        return {}
    x = {nid: 1.0 / math.sqrt(n) for nid in nodes}
    for _ in range(max_iter):
        x_new = {nid: sum(graph.adj.get(nid, {}).get(nbr, 1.0) * x[nbr] for nbr in graph.adj.get(nid, {})) for nid in nodes}
        norm = math.sqrt(sum(v * v for v in x_new.values())) or 1.0
        x = {nid: x_new[nid] / norm for nid in nodes}
    return {k: round(v, 4) for k, v in x.items()}


def graph_dijkstra_shortest_path(g: Any, start: Any, end: Any) -> Dict[str, Any]:
    """Dijkstra shortest path with total distance."""
    import heapq
    graph = _ensure_graph(g)
    s, e = str(start), str(end)
    if s not in graph.nodes or e not in graph.nodes:
        return {"path": [], "distance": float("inf")}
    if s == e:
        return {"path": [s], "distance": 0.0}
    distances = {s: 0.0}
    previous: Dict[str, Optional[str]] = {s: None}
    pq = [(0.0, s)]
    visited = set()
    while pq:
        d, cur = heapq.heappop(pq)
        if cur == e:
            break
        if cur in visited:
            continue
        visited.add(cur)
        for nbr, w in graph.adj.get(cur, {}).items():
            if nbr in visited:
                continue
            new_d = d + w
            if nbr not in distances or new_d < distances[nbr]:
                distances[nbr] = new_d
                previous[nbr] = cur
                heapq.heappush(pq, (new_d, nbr))
    if e not in previous:
        return {"path": [], "distance": float("inf")}
    path = []
    curr = e
    while curr is not None:
        path.append(curr)
        curr = previous[curr]
    path.reverse()
    return {"path": path, "distance": round(distances[e], 4)}


def graph_bellman_ford(g: Any, start: Any) -> Dict[str, Any]:
    """Bellman-Ford shortest paths supporting arbitrary edge weights."""
    graph = _ensure_graph(g)
    s = str(start)
    nodes = list(graph.nodes.keys())
    dists = {n: float("inf") for n in nodes}
    dists[s] = 0.0
    edges = []
    for u in graph.nodes:
        for v, w in graph.adj.get(u, {}).items():
            edges.append((u, v, w))
    for _ in range(max(1, len(nodes) - 1)):
        for u, v, w in edges:
            if dists[u] != float("inf") and dists[u] + w < dists[v]:
                dists[v] = dists[u] + w
    has_neg_cycle = False
    for u, v, w in edges:
        if dists[u] != float("inf") and dists[u] + w < dists[v]:
            has_neg_cycle = True
            break
    clean_dists = {k: (round(v, 4) if v != float("inf") else None) for k, v in dists.items()}
    return {"distances": clean_dists, "has_negative_cycle": has_neg_cycle}


def graph_floyd_warshall(g: Any) -> Dict[str, Dict[str, Any]]:
    """All-pairs shortest paths via Floyd-Warshall."""
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    dist = {u: {v: float("inf") for v in nodes} for u in nodes}
    for u in nodes:
        dist[u][u] = 0.0
        for v, w in graph.adj.get(u, {}).items():
            dist[u][v] = min(dist[u][v], w)
    for k in nodes:
        for i in nodes:
            for j in nodes:
                if dist[i][k] != float("inf") and dist[k][j] != float("inf"):
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return {u: {v: (round(dist[u][v], 4) if dist[u][v] != float("inf") else None) for v in nodes} for u in nodes}


def graph_kruskal_mst(g: Any) -> Dict[str, Any]:
    """Minimum Spanning Tree via Kruskal's algorithm with DSU."""
    graph = _ensure_graph(g)
    edges = []
    seen = set()
    for u in graph.nodes:
        for v, w in graph.adj.get(u, {}).items():
            edge_key = tuple(sorted([u, v]))
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append((w, u, v))
    edges.sort(key=lambda x: x[0])
    parent = {n: n for n in graph.nodes}
    def _find(x):
        if parent[x] != x:
            parent[x] = _find(parent[x])
        return parent[x]
    mst_edges = []
    tot_weight = 0.0
    for w, u, v in edges:
        root_u, root_v = _find(u), _find(v)
        if root_u != root_v:
            parent[root_v] = root_u
            mst_edges.append([u, v, w])
            tot_weight += w
    return {"edges": mst_edges, "total_weight": round(tot_weight, 4)}


def graph_prim_mst(g: Any, start: Any = None) -> Dict[str, Any]:
    """Minimum Spanning Tree via Prim's algorithm."""
    import heapq
    graph = _ensure_graph(g)
    if not graph.nodes:
        return {"edges": [], "total_weight": 0.0}
    start_node = str(start) if start is not None and str(start) in graph.nodes else next(iter(graph.nodes))
    visited = {start_node}
    edges_pq = []
    for v, w in graph.adj.get(start_node, {}).items():
        heapq.heappush(edges_pq, (w, start_node, v))
    mst_edges = []
    tot_weight = 0.0
    while edges_pq and len(visited) < len(graph.nodes):
        w, u, v = heapq.heappop(edges_pq)
        if v in visited:
            continue
        visited.add(v)
        mst_edges.append([u, v, w])
        tot_weight += w
        for next_nbr, next_w in graph.adj.get(v, {}).items():
            if next_nbr not in visited:
                heapq.heappush(edges_pq, (next_w, v, next_nbr))
    return {"edges": mst_edges, "total_weight": round(tot_weight, 4)}


def graph_articulation_points(g: Any) -> List[str]:
    """Find all cut vertices / articulation points using Tarjan's algorithm."""
    graph = _ensure_graph(g)
    visited = set()
    tin: Dict[str, int] = {}
    low: Dict[str, int] = {}
    timer = 0
    is_cut = set()
    def _dfs(u: str, p: Optional[str] = None):
        nonlocal timer
        visited.add(u)
        timer += 1
        tin[u] = low[u] = timer
        children = 0
        for v in graph.adj.get(u, {}):
            if v == p:
                continue
            if v in visited:
                low[u] = min(low[u], tin[v])
            else:
                _dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] >= tin[u] and p is not None:
                    is_cut.add(u)
                children += 1
        if p is None and children > 1:
            is_cut.add(u)
    for node in graph.nodes:
        if node not in visited:
            _dfs(node)
    return sorted(list(is_cut))


def graph_bipartite_check(g: Any) -> bool:
    """Wrapper checking bipartite property."""
    return graph_is_bipartite(g)


def graph_max_flow_edmonds_karp(g: Any, source: Any, sink: Any) -> float:
    """Edmonds-Karp algorithm for maximum network flow."""
    from collections import deque
    graph = _ensure_graph(g)
    s, t = str(source), str(sink)
    res_adj: Dict[str, Dict[str, float]] = {u: dict(neighbors) for u, neighbors in graph.adj.items()}
    for u in graph.nodes:
        for v in graph.adj.get(u, {}):
            if v not in res_adj:
                res_adj[v] = {}
            if u not in res_adj[v]:
                res_adj[v][u] = 0.0
    max_flow = 0.0
    while True:
        parent: Dict[str, Optional[str]] = {s: None}
        q = deque([s])
        while q and t not in parent:
            u = q.popleft()
            for v, cap in res_adj.get(u, {}).items():
                if cap > 1e-9 and v not in parent:
                    parent[v] = u
                    q.append(v)
        if t not in parent:
            break
        path_flow = float("inf")
        curr = t
        while curr != s:
            prev = parent[curr]
            path_flow = min(path_flow, res_adj[prev][curr])
            curr = prev
        curr = t
        while curr != s:
            prev = parent[curr]
            res_adj[prev][curr] -= path_flow
            res_adj[curr][prev] += path_flow
            curr = prev
        max_flow += path_flow
    return round(max_flow, 4)


def graph_radius(g: Any) -> int:
    """Minimum eccentricity across connected components."""
    from collections import deque
    graph = _ensure_graph(g)
    if not graph.nodes:
        return 0
    min_ecc = float("inf")
    for s in graph.nodes:
        dists = {s: 0}
        q = deque([s])
        while q:
            u = q.popleft()
            d = dists[u]
            for v in graph.adj.get(u, {}):
                if v not in dists:
                    dists[v] = d + 1
                    q.append(v)
        if len(dists) == len(graph.nodes):
            ecc = max(dists.values())
            if ecc < min_ecc:
                min_ecc = ecc
    return int(min_ecc) if min_ecc != float("inf") else 0


def graph_clustering_coefficient(g: Any) -> float:
    """Average local clustering coefficient across nodes."""
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    if not nodes:
        return 0.0
    coeffs = []
    for u in nodes:
        nbrs = list(graph.adj.get(u, {}).keys())
        k = len(nbrs)
        if k < 2:
            coeffs.append(0.0)
            continue
        links = 0
        for i in range(k):
            for j in range(i + 1, k):
                if nbrs[j] in graph.adj.get(nbrs[i], {}):
                    links += 1
        coeffs.append((2.0 * links) / (k * (k - 1)))
    return round(sum(coeffs) / len(coeffs), 4)


def graph_transitivity(g: Any) -> float:
    """Global transitivity (fraction of all possible triangles present)."""
    graph = _ensure_graph(g)
    triangles = 0
    triads = 0
    nodes = list(graph.nodes.keys())
    for u in nodes:
        nbrs = list(graph.adj.get(u, {}).keys())
        k = len(nbrs)
        if k >= 2:
            triads += k * (k - 1) // 2
            for i in range(k):
                for j in range(i + 1, k):
                    if nbrs[j] in graph.adj.get(nbrs[i], {}):
                        triangles += 1
    triangles //= 3
    return round((3.0 * triangles) / triads, 4) if triads > 0 else 0.0


def graph_density(g: Any) -> float:
    """Graph density ratio of actual edges to possible edges."""
    graph = _ensure_graph(g)
    v = len(graph.nodes)
    if v <= 1:
        return 0.0
    total_edges = sum(len(nbrs) for nbrs in graph.adj.values())
    if not graph.directed:
        total_edges /= 2.0
        max_edges = v * (v - 1) / 2.0
    else:
        max_edges = v * (v - 1)
    return round(total_edges / max_edges, 4) if max_edges > 0 else 0.0


def graph_degree_histogram(g: Any) -> List[int]:
    """Degree frequency histogram."""
    graph = _ensure_graph(g)
    degrees = [len(nbrs) for nbrs in graph.adj.values()]
    if not degrees:
        return []
    max_deg = max(degrees)
    hist = [0] * (max_deg + 1)
    for d in degrees:
        hist[d] += 1
    return hist


def graph_jaccard_similarity(g: Any, u: Any, v: Any) -> float:
    """Jaccard similarity between neighbor sets of two nodes."""
    graph = _ensure_graph(g)
    uid, vid = str(u), str(v)
    nu = set(graph.adj.get(uid, {}).keys())
    nv = set(graph.adj.get(vid, {}).keys())
    if not nu and not nv:
        return 1.0
    union = nu | nv
    if not union:
        return 0.0
    return round(len(nu & nv) / len(union), 4)


graph_find_articulation_points = graph_articulation_points
graph_jaccard_coefficient = graph_jaccard_similarity
graph_average_clustering_coefficient = graph_clustering_coefficient


def graph_find_bridges(g: Any) -> List[List[str]]:
    """Find all bridge edges using Tarjan's algorithm."""
    graph = _ensure_graph(g)
    visited = set()
    tin: Dict[str, int] = {}
    low: Dict[str, int] = {}
    timer = 0
    bridges = []

    def _dfs(u: str, p: Optional[str] = None):
        nonlocal timer
        visited.add(u)
        timer += 1
        tin[u] = low[u] = timer
        for v in graph.adj.get(u, {}):
            if v == p:
                continue
            if v in visited:
                low[u] = min(low[u], tin[v])
            else:
                _dfs(v, u)
                low[u] = min(low[u], low[v])
                if low[v] > tin[u]:
                    bridges.append(sorted([u, v]))

    for node in graph.nodes:
        if node not in visited:
            _dfs(node)
    return sorted(bridges)


def graph_eccentricity(g: Any, node: Any) -> int:
    """Maximum distance from node to any other node."""
    from collections import deque
    graph = _ensure_graph(g)
    s = str(node)
    if s not in graph.nodes:
        return 0
    dists = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in graph.adj.get(u, {}):
            if v not in dists:
                dists[v] = dists[u] + 1
                q.append(v)
    return max(dists.values()) if dists else 0


def graph_center(g: Any) -> List[str]:
    """Nodes whose eccentricity equals graph radius."""
    graph = _ensure_graph(g)
    if not graph.nodes:
        return []
    rad = graph_radius(graph)
    return sorted([n for n in graph.nodes if graph_eccentricity(graph, n) == rad])


def graph_is_tree(g: Any) -> bool:
    """Check if undirected graph is a connected tree (v - 1 edges, no cycles, connected)."""
    from collections import deque
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    n = len(nodes)
    if n == 0:
        return True
    if n == 1:
        return True
    total_edges = sum(len(graph.adj.get(u, {})) for u in nodes) // 2
    if total_edges != n - 1:
        return False
    # Check connectivity
    visited = set()
    q = deque([nodes[0]])
    visited.add(nodes[0])
    while q:
        u = q.popleft()
        for v in graph.adj.get(u, {}):
            if v not in visited:
                visited.add(v)
                q.append(v)
    return len(visited) == n


def graph_transitive_closure(g: Any) -> Dict[str, List[str]]:
    """Reachability dictionary for every node."""
    from collections import deque
    graph = _ensure_graph(g)
    closure: Dict[str, List[str]] = {}
    for s in graph.nodes:
        visited = set()
        q = deque([s])
        while q:
            u = q.popleft()
            for v in graph.adj.get(u, {}):
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        closure[s] = sorted(list(visited))
    return closure


def graph_k_core(g: Any, k: int) -> List[str]:
    """Return nodes belonging to k-core (subgraph where all nodes have degree >= k)."""
    graph = _ensure_graph(g)
    deg = {u: len(graph.adj.get(u, {})) for u in graph.nodes}
    active = set(graph.nodes.keys())
    changed = True
    while changed:
        changed = False
        to_remove = [u for u in active if deg[u] < k]
        if to_remove:
            changed = True
            for u in to_remove:
                active.remove(u)
                for v in graph.adj.get(u, {}):
                    if v in deg:
                        deg[v] -= 1
    return sorted(list(active))


def graph_laplacian_matrix(g: Any) -> List[List[float]]:
    """Compute combinatorial Laplacian matrix (L = D - A)."""
    graph = _ensure_graph(g)
    nodes = sorted(list(graph.nodes.keys()))
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}
    L = [[0.0] * n for _ in range(n)]
    for i, u in enumerate(nodes):
        nbrs = graph.adj.get(u, {})
        L[i][i] = float(len(nbrs))
        for v, w in nbrs.items():
            j = idx[v]
            L[i][j] -= 1.0
    return L


# =========================================================================
# Deepened Network Science & Graph Theory Algorithms
# =========================================================================

def graph_bron_kerbosch_cliques(g: Any) -> List[List[str]]:
    """Find all maximal cliques using Bron-Kerbosch algorithm with pivoting."""
    graph = _ensure_graph(g)
    adj_sets = {u: set(graph.adj.get(u, {}).keys()) for u in graph.nodes}
    cliques = []

    def bron_kerbosch(r: Set[str], p: Set[str], x: Set[str]):
        if not p and not x:
            cliques.append(sorted(list(r)))
            return
        # Pivot choice: max degree in P | X
        u_pivot = max(p | x, key=lambda node: len(adj_sets.get(node, set())))
        for v in list(p - adj_sets.get(u_pivot, set())):
            nbrs = adj_sets.get(v, set())
            bron_kerbosch(r | {v}, p & nbrs, x & nbrs)
            p.remove(v)
            x.add(v)

    all_nodes = set(graph.nodes.keys())
    bron_kerbosch(set(), all_nodes, set())
    cliques.sort(key=lambda c: (-len(c), c))
    return cliques


def graph_betweenness_centrality(g: Any, normalized: bool = True) -> Dict[str, float]:
    """Compute Brandes betweenness centrality in O(V * E) time."""
    from collections import deque
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    cb = {node: 0.0 for node in nodes}

    for s in nodes:
        stack = []
        pred = {w: [] for w in nodes}
        sigma = {w: 0.0 for w in nodes}
        sigma[s] = 1.0
        dist = {w: -1 for w in nodes}
        dist[s] = 0
        q = deque([s])

        while q:
            v = q.popleft()
            stack.append(v)
            for w in graph.adj.get(v, {}):
                # Path discovery
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    q.append(w)
                # Path counting
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)

        delta = {w: 0.0 for w in nodes}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / (sigma[w] or 1.0)) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]

    # Halve for undirected graphs
    if not graph.directed:
        for node in cb:
            cb[node] /= 2.0

    n = len(nodes)
    if normalized and n > 2:
        denom = ((n - 1) * (n - 2)) / (2.0 if not graph.directed else 1.0)
        return {node: round(val / denom, 4) for node, val in cb.items()}

    return {node: round(val, 4) for node, val in cb.items()}


def graph_louvain_communities(g: Any, resolution: float = 1.0) -> List[List[str]]:
    """Louvain modularity community detection."""
    graph = _ensure_graph(g)
    nodes = sorted(list(graph.nodes.keys()))
    if not nodes:
        return []

    # Total weight of all edges
    m = 0.0
    k_i = {}
    for u in nodes:
        deg = sum(graph.adj.get(u, {}).values())
        k_i[u] = deg
        m += deg
    m /= 2.0
    if m <= 0.0:
        return [[n] for n in nodes]

    # Initial community assignment: each node in its own community
    community = {u: u for u in nodes}

    changed = True
    passes = 0
    while changed and passes < 20:
        changed = False
        passes += 1
        for u in nodes:
            current_c = community[u]
            k_u = k_i[u]

            # Temporarily remove u from current community
            community[u] = None

            nbrs = graph.adj.get(u, {})
            c_weights: Dict[str, float] = {}
            for v, w in nbrs.items():
                c_v = community[v]
                if c_v is not None:
                    c_weights[c_v] = c_weights.get(c_v, 0.0) + w

            best_c = current_c
            k_i_curr = c_weights.get(current_c, 0.0)
            tot_curr = sum(k_i[x] for x in nodes if community[x] == current_c)
            best_gain = (k_i_curr / m) - (resolution * tot_curr * k_u) / (2.0 * (m ** 2)) if k_i_curr > 0 else 0.0
            if best_gain < 0.0:
                best_gain = 0.0
                best_c = u

            for c_cand, k_i_in in c_weights.items():
                if c_cand == current_c:
                    continue
                tot_cand = sum(k_i[x] for x in nodes if community[x] == c_cand)
                gain = (k_i_in / m) - (resolution * tot_cand * k_u) / (2.0 * (m ** 2))
                if gain > best_gain:
                    best_gain = gain
                    best_c = c_cand

            community[u] = best_c
            if best_c != current_c:
                changed = True

    # Group into communities
    comm_groups: Dict[str, List[str]] = {}
    for u, c in community.items():
        comm_groups.setdefault(c, []).append(u)

    result = [sorted(grp) for grp in comm_groups.values()]
    result.sort(key=lambda grp: (-len(grp), grp[0]))
    return result


def graph_tarjan_scc(g: Any) -> List[List[str]]:
    """Tarjan's algorithm for Strongly Connected Components (directed graphs)."""
    graph = _ensure_graph(g)
    index = 0
    indices: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    on_stack: Set[str] = set()
    stack: List[str] = []
    sccs: List[List[str]] = []

    def strongconnect(u: str):
        nonlocal index
        indices[u] = index
        lowlink[u] = index
        index += 1
        stack.append(u)
        on_stack.add(u)

        for v in graph.adj.get(u, {}):
            if v not in indices:
                strongconnect(v)
                lowlink[u] = min(lowlink[u], lowlink[v])
            elif v in on_stack:
                lowlink[u] = min(lowlink[u], indices[v])

        if lowlink[u] == indices[u]:
            component = []
            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.append(w)
                if w == u:
                    break
            sccs.append(sorted(component))

    for node in graph.nodes:
        if node not in indices:
            strongconnect(node)

    sccs.sort(key=lambda c: (-len(c), c[0] if c else ""))
    return sccs


def graph_mst(g: Any) -> Dict[str, Any]:
    """Kruskal's algorithm for Minimum Spanning Tree (MST)."""
    graph = _ensure_graph(g)
    # Collect all unique edges
    edge_list = []
    seen = set()
    for u in graph.nodes:
        for v, w in graph.adj.get(u, {}).items():
            pair = tuple(sorted([u, v]))
            if pair not in seen:
                seen.add(pair)
                edge_list.append((float(w), pair[0], pair[1]))

    edge_list.sort()

    parent = {u: u for u in graph.nodes}

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            return True
        return False

    mst_edges = []
    total_w = 0.0

    for w, u, v in edge_list:
        if union(u, v):
            mst_edges.append((u, v, w))
            total_w += w

    return {
        "edges": mst_edges,
        "total_weight": round(total_w, 4),
        "edge_count": len(mst_edges),
    }


def graph_johnson_apsp(g: Any) -> Dict[str, Any]:
    """Johnson's All-Pairs Shortest Path algorithm.
    Reweights edges via Bellman-Ford to handle negative weights, then executes Dijkstra for each vertex.
    Returns all-pairs shortest paths or flags negative cycle.
    """
    import heapq
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    if not nodes:
        return {"distances": {}, "has_negative_cycle": False}

    # 1. Add synthetic source q with weight 0 to all vertices
    q = "__johnson_source__"
    all_nodes = nodes + [q]
    edges = []
    for u in nodes:
        edges.append((q, u, 0.0))
        for v, w in graph.adj.get(u, {}).items():
            edges.append((u, v, float(w)))

    # 2. Bellman-Ford from q to compute potential function h
    h = {node: float("inf") for node in all_nodes}
    h[q] = 0.0

    for _ in range(len(all_nodes) - 1):
        updated = False
        for u, v, w in edges:
            if h[u] != float("inf") and h[u] + w < h[v]:
                h[v] = h[u] + w
                updated = True
        if not updated:
            break

    # Check for negative cycle
    for u, v, w in edges:
        if h[u] != float("inf") and h[u] + w < h[v]:
            return {"distances": {}, "has_negative_cycle": True}

    # 3. Reweight graph: w_hat(u, v) = w(u, v) + h(u) - h(v) >= 0
    reweighted_adj: Dict[str, Dict[str, float]] = {u: {} for u in nodes}
    for u in nodes:
        for v, w in graph.adj.get(u, {}).items():
            w_hat = float(w) + h[u] - h[v]
            reweighted_adj[u][v] = max(0.0, w_hat)

    # 4. Run Dijkstra from each vertex
    apsp: Dict[str, Dict[str, Optional[float]]] = {}
    for s in nodes:
        dist_hat = {v: float("inf") for v in nodes}
        dist_hat[s] = 0.0
        pq = [(0.0, s)]

        while pq:
            d_curr, u = heapq.heappop(pq)
            if d_curr > dist_hat[u]:
                continue
            for v, w_hat in reweighted_adj.get(u, {}).items():
                if dist_hat[u] + w_hat < dist_hat[v]:
                    dist_hat[v] = dist_hat[u] + w_hat
                    heapq.heappush(pq, (dist_hat[v], v))

        # Restore true distance: d(u, v) = d_hat(u, v) - h(u) + h(v)
        row: Dict[str, Optional[float]] = {}
        for v in nodes:
            if dist_hat[v] == float("inf"):
                row[v] = None
            else:
                true_d = dist_hat[v] - h[s] + h[v]
                row[v] = round(true_d, 4)
        apsp[s] = row

    return {"distances": apsp, "has_negative_cycle": False}


# =========================================================================
# Cluster A Deepened Graph Algorithms: Tarjan SCC, Hopcroft-Karp, Euler, Boruvka
# =========================================================================

class SCCResult(list):
    """List of SCC components that also supports dictionary-style key access."""

    def __init__(self, sccs: List[List[str]]):
        super().__init__(sccs)
        self.sccs = sccs
        self.count = len(sccs)
        self.is_strongly_connected = len(sccs) == 1 if sccs else False

    def __getitem__(self, key):
        if isinstance(key, str):
            if key == "sccs":
                return self.sccs
            elif key == "count":
                return self.count
            elif key == "is_strongly_connected":
                return self.is_strongly_connected
            raise KeyError(key)
        return super().__getitem__(key)

    def get(self, key, default=None):
        if key == "sccs":
            return self.sccs
        elif key == "count":
            return self.count
        elif key == "is_strongly_connected":
            return self.is_strongly_connected
        return default


def graph_tarjan_scc(g: Any) -> Any:
    """Computes Strongly Connected Components (SCC) using Tarjan's DFS algorithm."""
    graph = _ensure_graph(g)
    index = 0
    indices: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    on_stack: Dict[str, bool] = {}
    stack: List[str] = []
    sccs: List[List[str]] = []

    def strongconnect(v: str):
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack[v] = True

        for w in graph.adj.get(v, {}).keys():
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            scc = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                scc.append(w)
                if w == v:
                    break
            sccs.append(scc)

    for node in graph.nodes.keys():
        if node not in indices:
            strongconnect(node)

    return SCCResult(sccs)


def graph_hopcroft_karp(
    left_or_graph: Any,
    right_nodes: Optional[List[Any]] = None,
    edges: Optional[List[Tuple[Any, Any]]] = None,
    partition_u: Optional[List[Any]] = None,
) -> Dict[str, Any]:
    """Finds maximum cardinality bipartite matching in O(E * sqrt(V)) using Hopcroft-Karp."""
    if isinstance(left_or_graph, (DoomGraph, dict)) or partition_u is not None or right_nodes is None:
        graph = _ensure_graph(left_or_graph)
        all_nodes = set(graph.nodes.keys())
        if partition_u is not None:
            u_set = set(str(x) for x in partition_u)
            v_set = all_nodes - u_set
        else:
            bipartite_info = graph_bipartite_check(graph)
            if not bipartite_info.get("is_bipartite", False):
                raise ValueError("Graph is not bipartite")
            color_map = bipartite_info.get("coloring", {})
            u_set = {n for n, c in color_map.items() if c == 0}
            v_set = {n for n, c in color_map.items() if c == 1}

        left_nodes = sorted(list(u_set))
        right_nodes = sorted(list(v_set))
        edges = []
        for u in left_nodes:
            for v in graph.adj.get(u, {}):
                if v in v_set:
                    edges.append((u, v))
    else:
        left_nodes = left_or_graph
        right_nodes = right_nodes or []
        edges = edges or []

    u_nodes = [str(u) for u in left_nodes]
    v_nodes = [str(v) for v in right_nodes]
    adj: Dict[str, List[str]] = {u: [] for u in u_nodes}
    for u, v in edges:
        su, sv = str(u), str(v)
        if su in adj:
            adj[su].append(sv)

    pair_u: Dict[str, Optional[str]] = {u: None for u in u_nodes}
    pair_v: Dict[str, Optional[str]] = {v: None for v in v_nodes}
    dist: Dict[str, int] = {}

    def bfs() -> bool:
        from collections import deque
        queue = deque()
        for u in u_nodes:
            if pair_u[u] is None:
                dist[u] = 0
                queue.append(u)
            else:
                dist[u] = float("inf")

        found_augmenting = False
        while queue:
            u = queue.popleft()
            for v in adj.get(u, []):
                pu = pair_v.get(v)
                if pu is None:
                    found_augmenting = True
                elif dist.get(pu, float("inf")) == float("inf"):
                    dist[pu] = dist[u] + 1
                    queue.append(pu)
        return found_augmenting

    def dfs(u: str) -> bool:
        for v in adj.get(u, []):
            pu = pair_v.get(v)
            if pu is None or (dist.get(pu, float("inf")) == dist[u] + 1 and dfs(pu)):
                pair_u[u] = v
                pair_v[v] = u
                return True
        dist[u] = float("inf")
        return False

    matching_size = 0
    while bfs():
        for u in u_nodes:
            if pair_u[u] is None and dfs(u):
                matching_size += 1

    matches = [(u, v) for u, v in pair_u.items() if v is not None]
    return {
        "matching_size": matching_size,
        "matches": matches,
        "pair_u": pair_u,
        "pair_v": pair_v,
    }


def graph_eulerian_path(g: Any) -> Dict[str, Any]:
    """Finds an Eulerian path or circuit using Hierholzer's algorithm."""
    graph = _ensure_graph(g)
    nodes = list(graph.nodes.keys())
    if not nodes:
        return {"has_eulerian_path": True, "has_eulerian_circuit": True, "path": []}

    is_directed = graph.directed
    # Calculate degrees
    if is_directed:
        out_deg = {n: len(graph.adj.get(n, {})) for n in nodes}
        in_deg = {n: 0 for n in nodes}
        for u in nodes:
            for v in graph.adj.get(u, {}).keys():
                in_deg[v] = in_deg.get(v, 0) + 1

        start_node = None
        end_node = None
        for n in nodes:
            diff = out_deg[n] - in_deg[n]
            if diff == 1:
                if start_node is not None:
                    return {"has_eulerian_path": False, "has_eulerian_circuit": False, "path": []}
                start_node = n
            elif diff == -1:
                if end_node is not None:
                    return {"has_eulerian_path": False, "has_eulerian_circuit": False, "path": []}
                end_node = n
            elif diff != 0:
                return {"has_eulerian_path": False, "has_eulerian_circuit": False, "path": []}

        if start_node is None:
            # Circuit: pick any node with out-degree > 0
            start_node = next((n for n in nodes if out_deg[n] > 0), nodes[0])
            is_circuit = (start_node is not None and in_deg == out_deg)
        else:
            is_circuit = False

        # Hierholzer's DFS
        adj_copy = {u: list(graph.adj.get(u, {}).keys()) for u in nodes}
        path = []
        stack = [start_node]
        while stack:
            curr = stack[-1]
            if adj_copy.get(curr):
                nxt = adj_copy[curr].pop()
                stack.append(nxt)
            else:
                path.append(stack.pop())
        path.reverse()
        return {
            "has_eulerian_path": True,
            "has_eulerian_circuit": is_circuit,
            "path": path,
        }
    else:
        # Undirected graph
        degrees = {n: len(graph.adj.get(n, {})) for n in nodes}
        odd_nodes = [n for n, d in degrees.items() if d % 2 != 0]
        if len(odd_nodes) not in (0, 2):
            return {"has_eulerian_path": False, "has_eulerian_circuit": False, "path": []}

        start_node = odd_nodes[0] if odd_nodes else next((n for n in nodes if degrees[n] > 0), nodes[0])
        is_circuit = (len(odd_nodes) == 0)

        # Build edge list copies with multi-edge count tracking
        edge_counts: Dict[Tuple[str, str], int] = {}
        for u in nodes:
            for v in graph.adj.get(u, {}).keys():
                edge_key = (min(u, v), max(u, v))
                edge_counts[edge_key] = edge_counts.get(edge_key, 0) + 1
        for k in edge_counts:
            edge_counts[k] = edge_counts[k] // 2  # Bidirectional

        adj_copy = {u: list(graph.adj.get(u, {}).keys()) for u in nodes}
        path = []
        stack = [start_node]
        while stack:
            curr = stack[-1]
            found = False
            while adj_copy.get(curr):
                nxt = adj_copy[curr].pop()
                k = (min(curr, nxt), max(curr, nxt))
                if edge_counts.get(k, 0) > 0:
                    edge_counts[k] -= 1
                    stack.append(nxt)
                    found = True
                    break
            if not found:
                path.append(stack.pop())
        path.reverse()
        return {
            "has_eulerian_path": True,
            "has_eulerian_circuit": is_circuit,
            "path": path,
        }


def graph_boruvka_mst(g: Any) -> Dict[str, Any]:
    """Finds Minimum Spanning Tree (MST) using Borůvka's component-contraction algorithm."""
    graph = _ensure_graph(g)
    nodes = sorted(list(graph.nodes.keys()))
    node_to_id = {n: i for i, n in enumerate(nodes)}
    id_to_node = {i: n for i, n in enumerate(nodes)}
    n_nodes = len(nodes)

    # Edge list (u, v, weight)
    edge_set = set()
    edges = []
    for u in nodes:
        for v, w in graph.adj.get(u, {}).items():
            if u != v:
                e_key = (min(u, v), max(u, v))
                if e_key not in edge_set:
                    edge_set.add(e_key)
                    edges.append((node_to_id[u], node_to_id[v], float(w)))

    # Union-Find for components
    parent = list(range(n_nodes))
    rank = [0] * n_nodes

    def find(i: int) -> int:
        if parent[i] != i:
            parent[i] = find(parent[i])
        return parent[i]

    def union(i: int, j: int) -> bool:
        root_i = find(i)
        root_j = find(j)
        if root_i == root_j:
            return False
        if rank[root_i] < rank[root_j]:
            parent[root_i] = root_j
        elif rank[root_i] > rank[root_j]:
            parent[root_j] = root_i
        else:
            parent[root_j] = root_i
            rank[root_i] += 1
        return True

    num_trees = n_nodes
    mst_edges: List[Dict[str, Any]] = []
    total_weight = 0.0

    while num_trees > 1:
        cheapest: List[Optional[Tuple[int, int, float]]] = [None] * n_nodes

        for u, v, w in edges:
            set_u = find(u)
            set_v = find(v)
            if set_u != set_v:
                if cheapest[set_u] is None or cheapest[set_u][2] > w:
                    cheapest[set_u] = (u, v, w)
                if cheapest[set_v] is None or cheapest[set_v][2] > w:
                    cheapest[set_v] = (u, v, w)

        added_edge = False
        for i in range(n_nodes):
            edge = cheapest[i]
            if edge is not None:
                u, v, w = edge
                set_u = find(u)
                set_v = find(v)
                if set_u != set_v:
                    union(set_u, set_v)
                    mst_edges.append({
                        "u": id_to_node[u],
                        "v": id_to_node[v],
                        "weight": w,
                    })
                    total_weight += w
                    num_trees -= 1
                    added_edge = True

        if not added_edge:
            break

    return {
        "mst_edges": mst_edges,
        "total_weight": round(total_weight, 4),
        "is_connected": len(mst_edges) == n_nodes - 1 if n_nodes > 0 else True,
    }


# ==============================================================================
# HOPCROFT-KARP MATCHING, TARJAN BRIDGES & HIERHOLZER EULERIAN TRAILS
# ==============================================================================

class HopcroftKarpBipartiteMatching:
    """O(E * sqrt(V)) Maximum Cardinality Bipartite Matching."""

    @classmethod
    def match(cls, edges: List[Tuple[Any, Any]]) -> Dict[str, Any]:
        adj_u: Dict[str, List[str]] = {}
        all_u: Set[str] = set()
        all_v: Set[str] = set()

        for u_raw, v_raw in edges:
            u, v = str(u_raw), str(v_raw)
            all_u.add(u)
            all_v.add(v)
            adj_u.setdefault(u, []).append(v)

        pair_u: Dict[Optional[str], Optional[str]] = {u: None for u in all_u}
        pair_v: Dict[Optional[str], Optional[str]] = {v: None for v in all_v}
        dist: Dict[Optional[str], float] = {}

        def bfs() -> bool:
            from collections import deque
            q: deque = deque()
            for u in all_u:
                if pair_u[u] is None:
                    dist[u] = 0
                    q.append(u)
                else:
                    dist[u] = float("inf")
            dist[None] = float("inf")

            while q:
                u = q.popleft()
                if dist[u] < dist[None]:
                    for v in adj_u.get(u, []):
                        nxt_u = pair_v[v]
                        if dist.get(nxt_u, float("inf")) == float("inf"):
                            dist[nxt_u] = dist[u] + 1
                            q.append(nxt_u)

            return dist[None] != float("inf")

        def dfs(u: Optional[str]) -> bool:
            if u is not None:
                for v in adj_u.get(u, []):
                    nxt_u = pair_v[v]
                    if dist.get(nxt_u, float("inf")) == dist[u] + 1:
                        if dfs(nxt_u):
                            pair_v[v] = u
                            pair_u[u] = v
                            return True
                dist[u] = float("inf")
                return False
            return True

        matching_size = 0
        while bfs():
            for u in sorted(list(all_u)):
                if pair_u[u] is None:
                    if dfs(u):
                        matching_size += 1

        pairs = {u: pair_u[u] for u in sorted(list(all_u)) if pair_u[u] is not None}
        return {
            "matching_size": matching_size,
            "pairs": pairs,
            "num_u": len(all_u),
            "num_v": len(all_v),
            "is_perfect": matching_size == min(len(all_u), len(all_v)) and len(all_u) == len(all_v),
        }


class TarjanBridgeAndArticulation:
    """Discovers all bridges (cut edges) and articulation points (cut vertices) in undirected graphs."""

    @classmethod
    def analyze(cls, adj: Dict[str, List[str]]) -> Dict[str, Any]:
        nodes = sorted(list(adj.keys()))
        disc: Dict[str, int] = {}
        low: Dict[str, int] = {}
        parent: Dict[str, Optional[str]] = {n: None for n in nodes}
        articulation_pts: Set[str] = set()
        bridges: List[List[str]] = []
        timer = [0]

        def dfs(u: str) -> None:
            timer[0] += 1
            disc[u] = low[u] = timer[0]
            children = 0

            for v in adj.get(u, []):
                if v not in disc:
                    children += 1
                    parent[v] = u
                    dfs(v)
                    low[u] = min(low[u], low[v])

                    # Articulation check for non-root
                    if parent[u] is not None and low[v] >= disc[u]:
                        articulation_pts.add(u)

                    # Bridge check
                    if low[v] > disc[u]:
                        bridges.append(sorted([u, v]))
                elif v != parent[u]:
                    low[u] = min(low[u], disc[v])

            # Articulation check for root
            if parent[u] is None and children > 1:
                articulation_pts.add(u)

        for n in nodes:
            if n not in disc:
                dfs(n)

        # Unique sorted bridges
        unique_bridges = sorted(list(set(tuple(b) for b in bridges)))
        return {
            "bridges": [list(b) for b in unique_bridges],
            "num_bridges": len(unique_bridges),
            "articulation_points": sorted(list(articulation_pts)),
            "num_cut_vertices": len(articulation_pts),
        }


class HierholzerEulerianCircuit:
    """Finds Eulerian circuit or path in directed graph using Hierholzer's cycle splicing algorithm."""

    @classmethod
    def find_eulerian_trail(cls, edges: List[Tuple[Any, Any]]) -> Dict[str, Any]:
        from collections import defaultdict
        adj = defaultdict(list)
        in_degree = defaultdict(int)
        out_degree = defaultdict(int)
        all_nodes: Set[str] = set()

        for u_raw, v_raw in edges:
            u, v = str(u_raw), str(v_raw)
            adj[u].append(v)
            out_degree[u] += 1
            in_degree[v] += 1
            all_nodes.add(u)
            all_nodes.add(v)

        if not edges:
            return {
                "has_eulerian_circuit": False,
                "has_eulerian_path": False,
                "trail": [],
                "trail_length": 0,
            }

        start_node = None
        end_node = None
        start_count = 0
        end_count = 0

        for n in all_nodes:
            out_d = out_degree[n]
            in_d = in_degree[n]
            if out_d - in_d == 1:
                start_node = n
                start_count += 1
            elif in_d - out_d == 1:
                end_node = n
                end_count += 1
            elif in_d != out_d:
                return {
                    "has_eulerian_circuit": False,
                    "has_eulerian_path": False,
                    "trail": [],
                    "trail_length": 0,
                }

        is_circuit = (start_count == 0 and end_count == 0)
        is_path = is_circuit or (start_count == 1 and end_count == 1)

        if not is_path:
            return {
                "has_eulerian_circuit": False,
                "has_eulerian_path": False,
                "trail": [],
                "trail_length": 0,
            }

        if start_node is None:
            # Pick any node with positive out-degree
            for n in sorted(list(all_nodes)):
                if out_degree[n] > 0:
                    start_node = n
                    break

        # Hierholzer DFS traversal with stack
        curr_adj = {n: list(adj[n]) for n in adj}
        stack = [start_node]
        trail = []

        while stack:
            curr = stack[-1]
            if curr_adj.get(curr):
                nxt = curr_adj[curr].pop()
                stack.append(nxt)
            else:
                trail.append(stack.pop())

        trail.reverse()
        valid = len(trail) == len(edges) + 1

        return {
            "has_eulerian_circuit": is_circuit and valid,
            "has_eulerian_path": is_path and valid,
            "trail": trail if valid else [],
            "trail_length": len(trail) if valid else 0,
        }


def graph_bipartite_matching(bipartite_edges: List[Tuple[Any, Any]]) -> Any:
    """Computes maximum cardinality bipartite matching using Hopcroft-Karp algorithm."""
    return Record(HopcroftKarpBipartiteMatching.match(bipartite_edges))


def graph_find_bridges_and_cuts(adj_list: Dict[str, List[str]]) -> Any:
    """Finds all bridges and articulation cut vertices using Tarjan's low-link algorithm."""
    return Record(TarjanBridgeAndArticulation.analyze(adj_list))


def graph_eulerian_trail(edges: List[Tuple[Any, Any]]) -> Any:
    """Finds an Eulerian path or circuit using Hierholzer's cycle splicing algorithm."""
    return Record(HierholzerEulerianCircuit.find_eulerian_trail(edges))


class PushRelabelMaxFlow:
    """Goldberg-Tarjan push-relabel maximum flow algorithm with FIFO vertex discharge."""

    @classmethod
    def compute(
        cls,
        nodes: List[str],
        edges: List[Dict[str, Any]],
        source: str,
        sink: str,
    ) -> Dict[str, Any]:
        node_list = [str(n) for n in nodes]
        n = len(node_list)
        idx_map = {node_list[i]: i for i in range(n)}
        if source not in idx_map or sink not in idx_map:
            raise ValueError("Source or sink not in node list")
        s = idx_map[source]
        t = idx_map[sink]

        capacity = [[0.0] * n for _ in range(n)]
        flow = [[0.0] * n for _ in range(n)]

        for e in edges:
            u_name = str(e.get("from", e.get("u", "")))
            v_name = str(e.get("to", e.get("v", "")))
            cap = float(e.get("capacity", e.get("cap", 1.0)))
            if u_name in idx_map and v_name in idx_map:
                capacity[idx_map[u_name]][idx_map[v_name]] += cap

        height = [0] * n
        height[s] = n
        excess = [0.0] * n

        for v in range(n):
            if capacity[s][v] > 0:
                c = capacity[s][v]
                flow[s][v] = c
                flow[v][s] = -c
                excess[v] = c
                excess[s] -= c

        pushes = 0
        relabels = 0

        active_nodes = [i for i in range(n) if i != s and i != t and excess[i] > 1e-9]

        while active_nodes:
            u = active_nodes.pop(0)

            while excess[u] > 1e-9:
                pushed = False
                for v in range(n):
                    res_cap = capacity[u][v] - flow[u][v]
                    if res_cap > 1e-9 and height[u] == height[v] + 1:
                        send = min(excess[u], res_cap)
                        flow[u][v] += send
                        flow[v][u] -= send
                        excess[u] -= send
                        excess[v] += send
                        pushes += 1
                        pushed = True
                        if v != s and v != t and v not in active_nodes and excess[v] > 1e-9:
                            active_nodes.append(v)
                        if excess[u] <= 1e-9:
                            break

                if not pushed:
                    min_h = float("inf")
                    for v in range(n):
                        if capacity[u][v] - flow[u][v] > 1e-9:
                            min_h = min(min_h, height[v])
                    if min_h < float("inf"):
                        height[u] = int(min_h) + 1
                        relabels += 1
                    else:
                        break

        total_flow = sum(flow[s][v] for v in range(n) if flow[s][v] > 0)
        flow_edge_records = []
        for u in range(n):
            for v in range(n):
                if flow[u][v] > 1e-9:
                    flow_edge_records.append({
                        "from": node_list[u],
                        "to": node_list[v],
                        "flow": round(flow[u][v], 4),
                        "capacity": capacity[u][v],
                    })

        return {
            "source": source,
            "sink": sink,
            "max_flow": round(total_flow, 4),
            "flow_edges_count": len(flow_edge_records),
            "flow_edges": [Record(f) for f in flow_edge_records],
            "pushes_count": pushes,
            "relabels_count": relabels,
        }


class JohnsonsAllPairsShortestPaths:
    """Johnson's algorithm for all-pairs shortest paths with negative weights and cycle detection."""

    @classmethod
    def compute(
        cls,
        nodes: List[str],
        edges: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        import heapq
        node_list = [str(n) for n in nodes]
        n = len(node_list)
        idx_map = {node_list[i]: i for i in range(n)}

        adj: Dict[int, List[Tuple[int, float]]] = {i: [] for i in range(n)}
        for e in edges:
            u_name = str(e.get("from", e.get("u", "")))
            v_name = str(e.get("to", e.get("v", "")))
            w = float(e.get("weight", e.get("w", 1.0)))
            if u_name in idx_map and v_name in idx_map:
                adj[idx_map[u_name]].append((idx_map[v_name], w))

        h = [0.0] * n
        has_negative_cycle = False
        for it in range(n):
            for u in range(n):
                for v, w in adj[u]:
                    if h[u] + w < h[v]:
                        h[v] = h[u] + w

        for u in range(n):
            for v, w in adj[u]:
                if h[u] + w < h[v] - 1e-9:
                    has_negative_cycle = True
                    break
            if has_negative_cycle:
                break

        if has_negative_cycle:
            return {
                "has_negative_cycle": True,
                "nodes_count": n,
                "distances": {},
            }

        INF = float("inf")
        dist_matrix: Dict[str, Dict[str, float]] = {}

        for src_idx in range(n):
            d_hat = [INF] * n
            d_hat[src_idx] = 0.0
            pq = [(0.0, src_idx)]

            while pq:
                d_curr, u = heapq.heappop(pq)
                if d_curr > d_hat[u]:
                    continue
                for v, w in adj[u]:
                    w_hat = w + h[u] - h[v]
                    if d_hat[u] + w_hat < d_hat[v]:
                        d_hat[v] = d_hat[u] + w_hat
                        heapq.heappush(pq, (d_hat[v], v))

            src_name = node_list[src_idx]
            dist_matrix[src_name] = {}
            for target_idx in range(n):
                tgt_name = node_list[target_idx]
                if d_hat[target_idx] < INF:
                    orig_dist = d_hat[target_idx] - h[src_idx] + h[target_idx]
                    dist_matrix[src_name][tgt_name] = round(orig_dist, 4)
                else:
                    dist_matrix[src_name][tgt_name] = None

        return {
            "has_negative_cycle": False,
            "nodes_count": n,
            "distances": {k: Record(v) for k, v in dist_matrix.items()},
        }


def graph_push_relabel_max_flow(
    nodes: List[str],
    edges: List[Dict[str, Any]],
    source: str,
    sink: str,
) -> Any:
    """Computes maximum network flow using Goldberg-Tarjan push-relabel algorithm."""
    return Record(PushRelabelMaxFlow.compute(nodes, edges, source, sink))


def graph_johnson_all_pairs_paths(
    nodes: List[str],
    edges: List[Dict[str, Any]],
) -> Any:
    """Computes all-pairs shortest paths using Johnson's algorithm with potential reweighting."""
    return Record(JohnsonsAllPairsShortestPaths.compute(nodes, edges))


# ==============================================================================
# BRON-KERBOSCH MAXIMAL CLIQUES & LENGAUER-TARJAN FAST DOMINATOR ENGINES
# ==============================================================================


class BronKerboschMaximalCliques:
    """Bron-Kerbosch maximal clique enumeration with Tomita pivoting and degeneracy ordering.

    Enumerates all maximal cliques in an undirected graph in optimal O(d * n * 3^(d/3)) time,
    where d is the graph degeneracy, and computes maximum clique and k-core metrics.
    """

    @classmethod
    def compute(
        cls,
        edges: List[Tuple[Any, Any]],
        weighted_nodes: Optional[Dict[Any, float]] = None,
    ) -> Dict[str, Any]:
        """Finds all maximal cliques and the maximum-weight clique."""
        adj: Dict[str, Set[str]] = {}
        for edge in edges:
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                u, v = str(edge[0]), str(edge[1])
                if u == v:
                    continue
                adj.setdefault(u, set()).add(v)
                adj.setdefault(v, set()).add(u)
            elif isinstance(edge, dict):
                u = str(edge.get("u") or edge.get("from") or edge.get("source"))
                v = str(edge.get("v") or edge.get("to") or edge.get("target"))
                if u == v or u is None or v is None:
                    continue
                adj.setdefault(u, set()).add(v)
                adj.setdefault(v, set()).add(u)

        nodes = sorted(list(adj.keys()))
        weights = {n: float(weighted_nodes.get(n, 1.0)) for n in nodes} if weighted_nodes else {n: 1.0 for n in nodes}

        # 1. Compute degeneracy ordering and k-core numbers
        degrees = {n: len(adj[n]) for n in nodes}
        core_numbers: Dict[str, int] = {}
        degeneracy_order: List[str] = []
        rem_nodes = set(nodes)

        while rem_nodes:
            min_node = min(rem_nodes, key=lambda n: degrees[n])
            core_numbers[min_node] = degrees[min_node]
            degeneracy_order.append(min_node)
            rem_nodes.remove(min_node)
            for neighbor in adj[min_node]:
                if neighbor in rem_nodes:
                    degrees[neighbor] -= 1

        degeneracy = max(core_numbers.values()) if core_numbers else 0

        # 2. Bron-Kerbosch with Tomita pivot
        all_cliques: List[List[str]] = []

        def bron_kerbosch_pivot(R: Set[str], P: Set[str], X: Set[str]) -> None:
            if not P and not X:
                all_cliques.append(sorted(list(R)))
                return

            # Tomita pivot selection: maximize |P ∩ N(u)|
            u = max(P | X, key=lambda n: len(P & adj.get(n, set())))
            candidates = list(P - adj.get(u, set()))

            for v in candidates:
                neighbors = adj.get(v, set())
                bron_kerbosch_pivot(R | {v}, P & neighbors, X & neighbors)
                P.remove(v)
                X.add(v)

        # Outer degeneracy loop
        for i, v in enumerate(degeneracy_order):
            future_neighbors = adj[v] & set(degeneracy_order[i + 1 :])
            past_neighbors = adj[v] & set(degeneracy_order[:i])
            bron_kerbosch_pivot({v}, future_neighbors, past_neighbors)

        # Sort cliques by size descending, then lexicographically
        all_cliques.sort(key=lambda c: (-len(c), c))
        max_clique = all_cliques[0] if all_cliques else []

        # Find maximum weight clique
        max_weight = -1.0
        max_weight_clique = []
        for c in all_cliques:
            w_sum = sum(weights.get(n, 1.0) for n in c)
            if w_sum > max_weight:
                max_weight = w_sum
                max_weight_clique = c

        return {
            "cliques": all_cliques,
            "clique_count": len(all_cliques),
            "maximum_clique": max_clique,
            "maximum_clique_size": len(max_clique),
            "maximum_weight_clique": max_weight_clique,
            "maximum_clique_weight": max_weight if max_weight >= 0 else 0.0,
            "degeneracy": degeneracy,
            "k_core_numbers": core_numbers,
        }


class LengauerTarjanDominatorTree:
    """Thomas Lengauer & Robert Endre Tarjan's algorithm for immediate dominators in directed flowgraphs.

    Computes immediate dominators (idom), dominator tree hierarchy, and dominance frontiers (DF)
    for control flow analysis, compiler SSA construction, and graph centrality in O(M log N) time.
    """

    @classmethod
    def compute(
        cls,
        entry: Any,
        edges: List[Tuple[Any, Any]],
    ) -> Dict[str, Any]:
        """Computes dominator tree and dominance frontiers from entry node."""
        entry_s = str(entry)
        succ: Dict[str, List[str]] = {}
        pred: Dict[str, List[str]] = {}

        for edge in edges:
            if isinstance(edge, (list, tuple)) and len(edge) >= 2:
                u, v = str(edge[0]), str(edge[1])
            elif isinstance(edge, dict):
                u = str(edge.get("u") or edge.get("from") or edge.get("source"))
                v = str(edge.get("v") or edge.get("to") or edge.get("target"))
            else:
                continue
            succ.setdefault(u, []).append(v)
            pred.setdefault(v, []).append(u)

        semi: Dict[str, int] = {}
        parent: Dict[str, str] = {}
        vertex: List[str] = []
        dfnum: Dict[str, int] = {}
        ancestor: Dict[str, Optional[str]] = {}
        label: Dict[str, str] = {}

        # 1. Depth-first search spanning tree
        def dfs(v: str) -> None:
            dfnum[v] = len(vertex)
            semi[v] = len(vertex)
            vertex.append(v)
            label[v] = v
            ancestor[v] = None
            for w in succ.get(v, []):
                if w not in dfnum:
                    parent[w] = v
                    dfs(w)

        dfs(entry_s)

        # DSU with path compression
        def compress(v: str) -> None:
            a = ancestor.get(v)
            if a is not None and ancestor.get(a) is not None:
                compress(a)
                if semi[label[ancestor[v]]] < semi[label[v]]:
                    label[v] = label[ancestor[v]]
                ancestor[v] = ancestor[a]

        def eval_node(v: str) -> str:
            if ancestor.get(v) is None:
                return v
            compress(v)
            return label[v]

        def link(v: str, w: str) -> None:
            ancestor[w] = v

        bucket: Dict[str, List[str]] = {v: [] for v in vertex}
        idom: Dict[str, Optional[str]] = {}

        # 2. Compute semidominators & preliminary idom
        for i in range(len(vertex) - 1, 0, -1):
            w = vertex[i]
            for v in pred.get(w, []):
                if v in dfnum:
                    u = eval_node(v)
                    if semi[u] < semi[w]:
                        semi[w] = semi[u]
            bucket[vertex[semi[w]]].append(w)
            link(parent[w], w)
            for v in bucket[parent[w]]:
                u = eval_node(v)
                idom[v] = parent[w] if semi[u] == semi[v] else u
            bucket[parent[w]] = []

        # 3. Finalize immediate dominators
        for i in range(1, len(vertex)):
            w = vertex[i]
            if idom[w] != vertex[semi[w]]:
                idom[w] = idom[idom[w]]

        idom[entry_s] = None

        # 4. Construct tree children
        tree_children: Dict[str, List[str]] = {v: [] for v in vertex}
        for v in vertex:
            parent_dom = idom.get(v)
            if parent_dom is not None and parent_dom in tree_children:
                tree_children[parent_dom].append(v)

        # 5. Compute dominance frontiers (DF)
        df: Dict[str, Set[str]] = {v: set() for v in vertex}
        for w in vertex:
            predecessors = [p for p in pred.get(w, []) if p in dfnum]
            if len(predecessors) >= 2:
                for p in predecessors:
                    runner: Optional[str] = p
                    while runner is not None and runner != idom.get(w):
                        df[runner].add(w)
                        runner = idom.get(runner)

        # 6. Compute strict dominators
        strict_dom: Dict[str, List[str]] = {v: [] for v in vertex}
        for v in vertex:
            curr = idom.get(v)
            while curr is not None:
                strict_dom[v].append(curr)
                curr = idom.get(curr)

        return {
            "entry": entry_s,
            "reachable_nodes_count": len(vertex),
            "idom": idom,
            "tree_children": tree_children,
            "dominance_frontiers": {k: sorted(list(v)) for k, v in df.items()},
            "strict_dominators": strict_dom,
        }


def graph_bron_kerbosch_degeneracy_cliques(
    edges: List[Tuple[Any, Any]],
    weighted_nodes: Optional[Dict[Any, float]] = None,
) -> Any:
    """Finds all maximal cliques using Bron-Kerbosch algorithm with Tomita pivot and degeneracy ordering."""
    return Record(BronKerboschMaximalCliques.compute(edges, weighted_nodes))


def graph_lengauer_tarjan_dominators(
    entry: Any,
    edges: List[Tuple[Any, Any]],
) -> Any:
    """Computes immediate dominators and dominance frontiers using Lengauer-Tarjan algorithm."""
    return Record(LengauerTarjanDominatorTree.compute(entry, edges))


class EdmondsBlossomMaximumWeightMatching:
    """Jack Edmonds' Blossom Algorithm for Maximum Matching on General Undirected Graphs.

    Finds maximum cardinality and maximum weight matchings on arbitrary (non-bipartite)
    graphs by detecting odd-length alternating cycles (blossoms), contracting them to
    pseudo-vertices, and expanding them along augmenting paths.
    """

    @classmethod
    def maximum_matching(cls, nodes: Any = None, edges: Any = None, num_nodes: Optional[int] = None) -> Dict[str, Any]:
        """Calculates maximum cardinality matching on general graph."""
        if num_nodes is not None and nodes is None:
            nodes = [str(i) for i in range(num_nodes)]
        elif isinstance(nodes, int):
            nodes = [str(i) for i in range(nodes)]
        elif nodes is None and edges:
            all_n = set()
            for u, v in edges:
                all_n.add(str(u))
                all_n.add(str(v))
            nodes = sorted(list(all_n))

        nodes = [str(n) for n in nodes]
        edges = [(str(u), str(v)) for u, v in (edges or [])]

        n = len(nodes)
        node_to_idx = {name: i for i, name in enumerate(nodes)}
        idx_to_node = {i: name for i, name in enumerate(nodes)}

        adj: List[List[int]] = [[] for _ in range(n)]
        for u_str, v_str in edges:
            if u_str in node_to_idx and v_str in node_to_idx:
                u, v = node_to_idx[u_str], node_to_idx[v_str]
                if u != v:
                    adj[u].append(v)
                    adj[v].append(u)

        match = [-1] * n

        def lca(base: List[int], p: List[int], a: int, b: int) -> int:
            used = [False] * n
            while True:
                a = base[a]
                used[a] = True
                if match[a] == -1:
                    break
                a = p[match[a]]
            while True:
                b = base[b]
                if used[b]:
                    return b
                b = p[match[b]]

        def mark_path(base: List[int], p: List[int], blossom: List[bool], v: int, b: int) -> None:
            cur = v
            while base[cur] != b:
                blossom[base[cur]] = True
                blossom[base[match[cur]]] = True
                cur = p[match[cur]]
            blossom[b] = True

        def find_augmenting_path(root: int) -> Tuple[int, List[int]]:
            p = [-1] * n
            base = list(range(n))
            used = [0] * n
            q = [root]
            used[root] = 1

            head = 0
            while head < len(q):
                v = q[head]
                head += 1

                for to in adj[v]:
                    if base[v] == base[to] or match[v] == to:
                        continue
                    if to == root or (match[to] != -1 and p[match[to]] != -1):
                        cur_base = lca(base, p, v, to)
                        blossom = [False] * n
                        mark_path(base, p, blossom, v, cur_base)
                        mark_path(base, p, blossom, to, cur_base)

                        for i in range(n):
                            if blossom[base[i]]:
                                base[i] = cur_base
                                if used[i] == 2:
                                    used[i] = 1
                                    q.append(i)
                    elif used[to] == 0:
                        p[to] = v
                        if match[to] == -1:
                            return to, p
                        used[to] = 2
                        used[match[to]] = 1
                        q.append(match[to])
            return -1, p

        for i in range(n):
            if match[i] == -1:
                v, p = find_augmenting_path(i)
                while v != -1:
                    pv = p[v]
                    ppv = match[pv] if pv != -1 else -1
                    match[v] = pv
                    match[pv] = v
                    v = ppv

        matching_dict: Dict[str, str] = {}
        matched_pairs: List[List[str]] = []
        for i in range(n):
            if match[i] != -1 and match[i] > i:
                u_name = idx_to_node[i]
                v_name = idx_to_node[match[i]]
                matching_dict[u_name] = v_name
                matching_dict[v_name] = u_name
                matched_pairs.append([u_name, v_name])

        return {
            "matching": matching_dict,
            "matched_pairs": matched_pairs,
            "matching_cardinality": len(matched_pairs),
            "cardinality": len(matched_pairs),
            "total_nodes": n,
            "is_perfect": len(matched_pairs) * 2 == n,
        }

    max_matching = maximum_matching


class PageRankRandomWalkWithRestart:
    """Google PageRank & Personalized Random Walk with Restart (RWR) Engine.

    Calculates stationary distribution of random surfer on directed web graphs
    with dangling node compensation and teleportation damping.
    """

    @classmethod
    def calculate(
        cls,
        nodes_or_adj: Any,
        edges: Optional[Any] = None,
        alpha: float = 0.85,
        damping: Optional[float] = None,
        personalization: Optional[Dict[str, float]] = None,
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, Any]:
        """Calculates PageRank vector via power iteration."""
        if damping is not None:
            alpha = damping

        if isinstance(nodes_or_adj, dict) and edges is None:
            nodes = list(nodes_or_adj.keys())
            edges = [(u, v) for u, targets in nodes_or_adj.items() for v in targets]
        else:
            nodes = list(nodes_or_adj)
            edges = list(edges) if edges else []

        n = len(nodes)
        if n == 0:
            return {"scores": {}, "top_ranked": [], "iterations": 0}

        node_set = sorted(list(set(nodes)))
        node_idx = {name: i for i, name in enumerate(node_set)}
        out_edges: Dict[str, List[str]] = {name: [] for name in node_set}

        for u, v in edges:
            if u in out_edges and v in node_idx:
                out_edges[u].append(v)

        if personalization:
            total_p = sum(personalization.get(name, 0.0) for name in node_set)
            if total_p > 0:
                p0 = [personalization.get(name, 0.0) / total_p for name in node_set]
            else:
                p0 = [1.0 / n] * n
        else:
            p0 = [1.0 / n] * n

        rank = list(p0)
        iterations = 0

        for it in range(max_iter):
            iterations += 1
            next_rank = [0.0] * n
            dangling_sum = 0.0

            for i, u in enumerate(node_set):
                succs = out_edges[u]
                if succs:
                    share = rank[i] / len(succs)
                    for v in succs:
                        next_rank[node_idx[v]] += share
                else:
                    dangling_sum += rank[i]

            diff = 0.0
            for i in range(n):
                val = alpha * (next_rank[i] + dangling_sum * p0[i]) + (1.0 - alpha) * p0[i]
                diff += abs(val - rank[i])
                rank[i] = val

            if diff < tol:
                break

        scores = {node_set[i]: round(rank[i], 6) for i in range(n)}
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "scores": scores,
            "ranks": scores,
            "top_ranked": [Record({"node": k, "pagerank": v}) for k, v in ranked],
            "highest_ranked_node": ranked[0][0] if ranked else "",
            "top_node": ranked[0][0] if ranked else "",
            "iterations": iterations,
            "damping_factor": alpha,
        }

    compute = calculate


def graph_edmonds_blossom_matching(nodes: Any, edges: Any) -> Record:
    """Computes maximum matching on general graph using Edmonds' blossom algorithm."""
    return Record(EdmondsBlossomMaximumWeightMatching.maximum_matching(nodes, edges))


def graph_pagerank_calculate_graph(g_adj: Any, alpha: float = 0.85) -> Record:
    """Calculates PageRank centrality directly from adjacency dictionary."""
    return Record(PageRankRandomWalkWithRestart.calculate(g_adj, alpha=alpha))


def graph_pagerank_calculate(
    nodes: List[str],
    edges: List[Tuple[str, str]],
    alpha: float = 0.85,
) -> Record:
    """Calculates PageRank centrality vector using power iteration."""
    return Record(PageRankRandomWalkWithRestart.calculate(nodes, edges, alpha=alpha))







