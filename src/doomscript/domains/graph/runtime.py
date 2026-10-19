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



