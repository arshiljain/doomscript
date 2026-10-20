"""Runtime execution engine for Research & Scientific Graph Algorithms."""

from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import math
import hashlib
import heapq
import re
from collections import deque
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.runtime import Record
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


class BibTeXEngine:
    """Zero-dependency BibTeX parser and multi-style citation formatter."""

    @staticmethod
    def parse(bibtex_str: str) -> List[Dict[str, Any]]:
        entries: List[Dict[str, Any]] = []
        # Match @type{key, fields...}
        entry_blocks = re.findall(r"@(\w+)\s*\{\s*([^,]+),\s*(.*?)\n\s*\}", bibtex_str, re.DOTALL)
        for entry_type, cite_key, body in entry_blocks:
            fields: Dict[str, str] = {"entry_type": entry_type.lower(), "cite_key": cite_key.strip()}
            # Extract key = {val} or key = "val"
            field_matches = re.findall(r'(\w+)\s*=\s*[\{"\'](.*?)[\}"\']\s*(?:,|$)', body, re.DOTALL)
            for k, v in field_matches:
                clean_val = re.sub(r"\s+", " ", v).strip()
                fields[k.lower()] = clean_val
            entries.append(fields)
        return entries

    @classmethod
    def format_citation(cls, entry: Dict[str, Any], style: str = "apa") -> str:
        s = style.lower()
        authors = entry.get("author", "Unknown Author")
        title = entry.get("title", "Untitled")
        year = entry.get("year", "n.d.")
        journal = entry.get("journal") or entry.get("booktitle", "")
        volume = entry.get("volume", "")
        pages = entry.get("pages", "")

        if s == "apa":
            # Author, A. (Year). Title. Journal, volume, pages.
            j_part = f" {journal}," if journal else ""
            v_part = f" {volume}," if volume else ""
            p_part = f" {pages}." if pages else "."
            return f"{authors} ({year}). {title}.{j_part}{v_part}{p_part}".strip()
        elif s == "ieee":
            # [1] Author, "Title," Journal, vol. X, pp. Y, Year.
            parts = [f'{authors}, "{title},"']
            if journal:
                parts.append(journal + ",")
            if volume:
                parts.append(f"vol. {volume},")
            if pages:
                parts.append(f"pp. {pages},")
            parts.append(f"{year}.")
            return " ".join(parts)
        elif s == "harvard":
            return f"{authors}, {year}. {title}. {journal}."
        return f"{authors} ({year}) {title}."


class CitationNetwork:
    """Scientometrics and Academic Citation Graph Analyzer."""

    def __init__(self):
        # adjacency: paper_id -> set of papers it cites
        self.cites: Dict[str, Set[str]] = {}
        # reverse: paper_id -> set of papers that cite it
        self.cited_by: Dict[str, Set[str]] = {}
        # metadata: paper_id -> {title, author, year}
        self.papers: Dict[str, Dict[str, Any]] = {}

    def add_paper(self, paper_id: str, title: str = "", author: str = "", year: int = 2024) -> None:
        pid = str(paper_id)
        if pid not in self.papers:
            self.papers[pid] = {"id": pid, "title": title, "author": author, "year": int(year)}
        else:
            if title:
                self.papers[pid]["title"] = title
            if author:
                self.papers[pid]["author"] = author
            if year != 2024 or self.papers[pid]["year"] == 2024:
                self.papers[pid]["year"] = int(year)
        self.cites.setdefault(pid, set())
        self.cited_by.setdefault(pid, set())

    def add_citation(self, citing_paper: str, cited_paper: str) -> None:
        p_from = str(citing_paper)
        p_to = str(cited_paper)
        self.add_paper(p_from)
        self.add_paper(p_to)
        self.cites[p_from].add(p_to)
        self.cited_by[p_to].add(p_from)

    def calculate_h_index(self, author: str) -> int:
        """Calculate Hirsch index for an author."""
        author_papers = [pid for pid, meta in self.papers.items() if meta["author"].lower() == author.lower()]
        citations = [len(self.cited_by.get(pid, set())) for pid in author_papers]
        citations.sort(reverse=True)
        h = 0
        for i, c in enumerate(citations, start=1):
            if c >= i:
                h = i
            else:
                break
        return h

    def calculate_i10_index(self, author: str) -> int:
        """Papers with at least 10 citations."""
        author_papers = [pid for pid, meta in self.papers.items() if meta["author"].lower() == author.lower()]
        return sum(1 for pid in author_papers if len(self.cited_by.get(pid, set())) >= 10)

    def compute_pagerank(self, damping: float = 0.85, max_iter: int = 50) -> Dict[str, float]:
        """Compute citation prestige / PageRank score for each paper."""
        nodes = list(self.papers.keys())
        n = len(nodes)
        if n == 0:
            return {}

        ranks = {node: 1.0 / n for node in nodes}
        for _ in range(max_iter):
            new_ranks = {}
            for u in nodes:
                incoming_sum = 0.0
                for v in self.cited_by.get(u, set()):
                    out_degree = len(self.cites.get(v, set()))
                    if out_degree > 0:
                        incoming_sum += ranks[v] / out_degree
                new_ranks[u] = (1.0 - damping) / n + damping * incoming_sum
            ranks = new_ranks

        # Normalize to sum to 1.0
        total = sum(ranks.values()) or 1.0
        return {k: round(v / total, 6) for k, v in ranks.items()}


class AcademicLiteratureSynthesizer:
    """Scientific literature clustering, keyword relevance ranking, and summarization."""

    def __init__(self):
        self.corpus: List[Dict[str, Any]] = []

    def add_document(self, doc_id: str, title: str, abstract: str) -> None:
        self.corpus.append({
            "id": str(doc_id),
            "title": str(title),
            "abstract": str(abstract),
        })

    def search_by_relevance(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        terms = set(re.findall(r"\b\w+\b", str(query).lower()))
        results = []

        for doc in self.corpus:
            title_words = set(re.findall(r"\b\w+\b", doc["title"].lower()))
            abs_words = re.findall(r"\b\w+\b", doc["abstract"].lower())

            # Title matches count triple
            title_hits = len(terms & title_words) * 3
            abs_hits = sum(1 for w in abs_words if w in terms)
            score = title_hits + abs_hits

            if score > 0:
                results.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "score": score,
                    "snippet": doc["abstract"][:120] + "...",
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


class SVDDecomposition:
    """Pure-Python Singular Value Decomposition (SVD): A = U * Sigma * V^T."""

    def __init__(self, max_sweeps: int = 40, tol: float = 1e-9):
        self.max_sweeps = max_sweeps
        self.tol = tol

    def decompose(self, A_mat: List[List[float]]) -> Dict[str, Any]:
        """
        Computes thin SVD using Hestenes one-sided Jacobi rotations on A.
        A (m x n) = U (m x n) * diag(sigma) * V^T (n x n).
        """
        import math
        m = len(A_mat)
        n = len(A_mat[0]) if m > 0 else 0
        if m == 0 or n == 0:
            return {"U": [], "singular_values": [], "Vt": []}

        # Initialize B = copy of A (m x n), V = I_n (n x n)
        B = [[float(A_mat[r][c]) for c in range(n)] for r in range(m)]
        V = [[1.0 if r == c else 0.0 for c in range(n)] for r in range(n)]

        # Hestenes Jacobi sweeps
        for sweep in range(self.max_sweeps):
            max_offdiag = 0.0
            for i in range(n):
                for j in range(i + 1, n):
                    # Compute dot products: a = B_i . B_i, b = B_j . B_j, c = B_i . B_j
                    alpha = sum(B[r][i] * B[r][i] for r in range(m))
                    beta = sum(B[r][j] * B[r][j] for r in range(m))
                    gamma = sum(B[r][i] * B[r][j] for r in range(m))

                    max_offdiag = max(max_offdiag, abs(gamma) / (math.sqrt(alpha * beta) or 1.0))

                    if abs(gamma) < self.tol * math.sqrt(alpha * beta):
                        continue

                    # Jacobi rotation angle
                    zeta = (beta - alpha) / (2.0 * gamma)
                    t = math.copysign(1.0 / (abs(zeta) + math.sqrt(1.0 + zeta ** 2)), zeta)
                    cs = 1.0 / math.sqrt(1.0 + t ** 2)
                    sn = cs * t

                    # Rotate columns i and j of B
                    for r in range(m):
                        bi = B[r][i]
                        bj = B[r][j]
                        B[r][i] = cs * bi - sn * bj
                        B[r][j] = sn * bi + cs * bj

                    # Rotate columns i and j of V
                    for r in range(n):
                        vi = V[r][i]
                        vj = V[r][j]
                        V[r][i] = cs * vi - sn * vj
                        V[r][j] = sn * vi + cs * vj

            if max_offdiag < self.tol:
                break

        # Singular values are norms of columns of B
        sigmas = []
        for c in range(n):
            norm = math.sqrt(sum(B[r][c] ** 2 for r in range(m)))
            sigmas.append(norm)

        # Sort singular values in descending order
        indices = sorted(range(n), key=lambda i: sigmas[i], reverse=True)
        sorted_sigmas = [round(sigmas[i], 6) for i in indices]

        # Normalized U matrix: U_i = B_i / sigma_i
        U = [[0.0] * n for _ in range(m)]
        for rank_idx, orig_i in enumerate(indices):
            s = sigmas[orig_i]
            for r in range(m):
                U[r][rank_idx] = round(B[r][orig_i] / s, 6) if s > 1e-12 else 0.0

        # Transpose of V: Vt (n x n)
        Vt = [[round(V[r][orig_c], 6) for r in range(n)] for orig_c in indices]

        return {
            "U": U,
            "singular_values": sorted_sigmas,
            "Vt": Vt,
            "rank": sum(1 for s in sorted_sigmas if s > 1e-6),
        }


class RungeKuttaFehlberg:
    """Adaptive step-size RKF45 Numerical Integrator for Systems of Ordinary Differential Equations."""

    def __init__(self, tol: float = 1e-5, h_min: float = 1e-6, h_max: float = 0.5):
        self.tol = tol
        self.h_min = h_min
        self.h_max = h_max

    def solve(
        self,
        ode_func: Callable[[float, List[float]], List[float]],
        y0: List[float],
        t_span: Tuple[float, float],
        initial_step: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Solves dy/dt = f(t, y) from t_span[0] to t_span[1] with adaptive step size.
        """
        t0, t_end = t_span
        t = t0
        y = list(y0)
        h = max(self.h_min, min(self.h_max, initial_step))
        dim = len(y)

        t_points = [t]
        y_trajectories = [[round(v, 6) for v in y]]

        while t < t_end - 1e-12:
            if t + h > t_end:
                h = t_end - t

            # Butcher Tableau for RKF45
            k1 = ode_func(t, y)

            y_k2 = [y[i] + h * (1.0 / 4.0) * k1[i] for i in range(dim)]
            k2 = ode_func(t + h * (1.0 / 4.0), y_k2)

            y_k3 = [y[i] + h * ((3.0 / 32.0) * k1[i] + (9.0 / 32.0) * k2[i]) for i in range(dim)]
            k3 = ode_func(t + h * (3.0 / 8.0), y_k3)

            y_k4 = [
                y[i] + h * ((1932.0 / 2197.0) * k1[i] - (7200.0 / 2197.0) * k2[i] + (7296.0 / 2197.0) * k3[i])
                for i in range(dim)
            ]
            k4 = ode_func(t + h * (12.0 / 13.0), y_k4)

            y_k5 = [
                y[i] + h * (
                    (439.0 / 216.0) * k1[i] - 8.0 * k2[i] + (3680.0 / 513.0) * k3[i] - (845.0 / 4104.0) * k4[i]
                )
                for i in range(dim)
            ]
            k5 = ode_func(t + h, y_k5)

            y_k6 = [
                y[i] + h * (
                    -(8.0 / 27.0) * k1[i] + 2.0 * k2[i] - (3544.0 / 2565.0) * k3[i]
                    + (1859.0 / 4104.0) * k4[i] - (11.0 / 40.0) * k5[i]
                )
                for i in range(dim)
            ]
            k6 = ode_func(t + h * 0.5, y_k6)

            # 4th-order estimate
            y4 = [
                y[i] + h * (
                    (25.0 / 216.0) * k1[i] + (1408.0 / 2565.0) * k3[i] + (2197.0 / 4104.0) * k4[i] - (1.0 / 5.0) * k5[i]
                )
                for i in range(dim)
            ]

            # 5th-order estimate
            y5 = [
                y[i] + h * (
                    (16.0 / 135.0) * k1[i] + (6656.0 / 12825.0) * k3[i] + (28561.0 / 56430.0) * k4[i]
                    - (9.0 / 50.0) * k5[i] + (2.0 / 55.0) * k6[i]
                )
                for i in range(dim)
            ]

            # Truncation error
            err = math.sqrt(sum((y5[i] - y4[i]) ** 2 for i in range(dim)))

            # Step adaptation
            if err <= self.tol or h <= self.h_min:
                t += h
                y = y5
                t_points.append(round(t, 6))
                y_trajectories.append([round(v, 6) for v in y])
                scale = 0.84 * ((self.tol / (err + 1e-12)) ** 0.25) if err > 0 else 1.5
                h = max(self.h_min, min(self.h_max, h * min(max(scale, 0.2), 2.0)))
            else:
                scale = 0.84 * ((self.tol / err) ** 0.25)
                h = max(self.h_min, h * max(scale, 0.1))

        return {
            "t": t_points,
            "y": y_trajectories,
            "final_y": y_trajectories[-1],
            "num_steps": len(t_points) - 1,
        }


class LevenbergMarquardt:
    """Non-linear least squares parameter optimization via damped Gauss-Newton."""

    def __init__(self, max_iter: int = 100, tol: float = 1e-6, lambda_init: float = 0.01):
        self.max_iter = max_iter
        self.tol = tol
        self.lambda_init = lambda_init

    def fit(
        self,
        model_func: Callable[[float, List[float]], float],
        x_data: List[float],
        y_data: List[float],
        p0: List[float],
    ) -> Dict[str, Any]:
        """
        Fits parameters p to minimize sum of squared residuals: sum (y_data[i] - model_func(x_data[i], p))^2.
        """
        p = [float(v) for v in p0]
        n_params = len(p)
        n_pts = len(x_data)
        lam = self.lambda_init

        def residuals(params: List[float]) -> List[float]:
            return [y_data[i] - model_func(x_data[i], params) for i in range(n_pts)]

        def cost(r_vec: List[float]) -> float:
            return sum(r ** 2 for r in r_vec)

        r = residuals(p)
        current_cost = cost(r)

        for it in range(self.max_iter):
            # Numerical Jacobian J (n_pts x n_params)
            eps = 1e-6
            J = [[0.0] * n_params for _ in range(n_pts)]
            for j in range(n_params):
                p_plus = list(p)
                p_plus[j] += eps
                r_plus = residuals(p_plus)
                for i in range(n_pts):
                    J[i][j] = -(r_plus[i] - r[i]) / eps

            # J^T * J and J^T * r
            JTJ = [[sum(J[i][r_idx] * J[i][c_idx] for i in range(n_pts)) for c_idx in range(n_params)] for r_idx in range(n_params)]
            JTr = [sum(J[i][r_idx] * r[i] for i in range(n_pts)) for r_idx in range(n_params)]

            # Damping: JTJ + lam * diag(JTJ)
            A = [[JTJ[r_idx][c_idx] + (lam * JTJ[r_idx][c_idx] if r_idx == c_idx else 0.0) for c_idx in range(n_params)] for r_idx in range(n_params)]

            # Solve A * dp = JTr via Gaussian elimination
            aug = [list(A[r_idx]) + [JTr[r_idx]] for r_idx in range(n_params)]
            singular = False
            for col in range(n_params):
                piv = max(range(col, n_params), key=lambda r_idx: abs(aug[r_idx][col]))
                if abs(aug[piv][col]) < 1e-12:
                    singular = True
                    break
                aug[col], aug[piv] = aug[piv], aug[col]
                pv = aug[col][col]
                for c_idx in range(col, n_params + 1):
                    aug[col][c_idx] /= pv
                for r_idx in range(n_params):
                    if r_idx != col:
                        factor = aug[r_idx][col]
                        for c_idx in range(col, n_params + 1):
                            aug[r_idx][c_idx] -= factor * aug[col][c_idx]

            if singular:
                lam *= 10.0
                continue

            dp = [aug[r_idx][n_params] for r_idx in range(n_params)]
            p_cand = [p[i] + dp[i] for i in range(n_params)]
            r_cand = residuals(p_cand)
            cand_cost = cost(r_cand)

            if cand_cost < current_cost:
                # Accept step, decrease damping
                p = p_cand
                r = r_cand
                current_cost = cand_cost
                lam = max(1e-7, lam * 0.1)
                if sum(abs(v) for v in dp) < self.tol:
                    break
            else:
                # Reject step, increase damping
                lam = min(1e7, lam * 10.0)

        return {
            "optimal_params": [round(val, 6) for val in p],
            "final_cost": round(current_cost, 6),
            "iterations": it + 1,
        }


def research_svd(matrix: List[List[float]]) -> Dict[str, Any]:
    """Computes Singular Value Decomposition of a matrix."""
    svd = SVDDecomposition()
    return svd.decompose(matrix)


def research_rkf45_solve(
    ode_func: Callable[[float, List[float]], List[float]],
    y0: List[float],
    t_span: Tuple[float, float],
) -> Dict[str, Any]:
    """Solves differential equation using adaptive RKF45."""
    rkf = RungeKuttaFehlberg()
    return rkf.solve(ode_func, y0, t_span)


def research_levenberg_marquardt(
    model_func: Callable[[float, List[float]], float],
    x_data: List[float],
    y_data: List[float],
    p0: List[float],
) -> Dict[str, Any]:
    """Fits non-linear model parameters via Levenberg-Marquardt algorithm."""
    lm = LevenbergMarquardt()
    return lm.fit(model_func, x_data, y_data, p0)


# ==============================================================================
# BIBLIOMETRICS (H-INDEX, G-INDEX) & BENJAMINI-HOCHBERG FDR CORRECTION
# ==============================================================================


class HIndexAndCitationBibliometrics:
    """Computes academic bibliometrics including Hirsch index (h-index),
    Egghe's g-index, i10-index, contemporary h-index, and citation summary.
    """

    @classmethod
    def compute(
        cls,
        citations: List[int],
        publication_years: Optional[List[int]] = None,
        current_year: int = 2026,
    ) -> Dict[str, Any]:
        if not citations:
            return {
                "total_publications": 0,
                "total_citations": 0,
                "h_index": 0,
                "g_index": 0,
                "i10_index": 0,
                "contemporary_h_index": 0,
                "average_citations_per_paper": 0.0,
            }

        c_sorted = sorted([int(c) for c in citations], reverse=True)
        total_pubs = len(c_sorted)
        total_cites = sum(c_sorted)

        # 1. Hirsch h-index: largest h where h papers have >= h citations
        h = 0
        for i, count in enumerate(c_sorted):
            if count >= i + 1:
                h = i + 1
            else:
                break

        # 2. Egghe's g-index: largest g where top g papers have >= g^2 citations
        g = 0
        cum_citations = 0
        for i, count in enumerate(c_sorted):
            cum_citations += count
            if cum_citations >= (i + 1) ** 2:
                g = i + 1

        # 3. i10-index: count of papers with >= 10 citations
        i10 = sum(1 for c in c_sorted if c >= 10)

        # 4. Contemporary h-index (h_c): age-decayed citation scores
        # Score_i = 4 * C_i / (Y_now - Y_pub + 1)
        h_c = 0
        if publication_years and len(publication_years) == total_pubs:
            decayed = []
            for c, y in zip(citations, publication_years):
                age = max(1, current_year - int(y) + 1)
                decayed.append(4.0 * c / age)
            decayed.sort(reverse=True)
            for i, score in enumerate(decayed):
                if score >= i + 1:
                    h_c = i + 1
                else:
                    break
        else:
            h_c = h

        avg_cites = round(total_cites / total_pubs, 2) if total_pubs > 0 else 0.0

        return {
            "total_publications": total_pubs,
            "total_citations": total_cites,
            "h_index": h,
            "g_index": g,
            "i10_index": i10,
            "contemporary_h_index": h_c,
            "average_citations_per_paper": avg_cites,
            "max_citations": c_sorted[0] if c_sorted else 0,
        }


class BenjaminiHochbergMultipleTesting:
    """Controls False Discovery Rate (FDR) and Family-Wise Error Rate (FWER)
    across multiple statistical hypothesis tests using Benjamini-Hochberg,
    Holm-Bonferroni, and Bonferroni adjustments.
    """

    @classmethod
    def correct(
        cls,
        p_values: List[float],
        alpha: float = 0.05,
    ) -> Dict[str, Any]:
        m = len(p_values)
        if m == 0:
            return {
                "total_hypotheses": 0,
                "significant_count": 0,
                "adjusted_q_values": [],
                "bonferroni_p_values": [],
                "holm_p_values": [],
            }

        # Sort p-values with original index preservation
        indexed = sorted(enumerate(p_values), key=lambda x: x[1])

        # 1. Benjamini-Hochberg FDR adjusted q-values
        q_vals = [0.0] * m
        min_q = 1.0
        for rank in range(m, 0, -1):
            orig_idx, p = indexed[rank - 1]
            q = min(1.0, (m / rank) * p)
            min_q = min(min_q, q)
            q_vals[orig_idx] = round(min_q, 6)

        # 2. Bonferroni FWER adjustment: min(1.0, m * p)
        bonf_vals = [round(min(1.0, p * m), 6) for p in p_values]

        # 3. Holm-Bonferroni step-down: p_adj_i = max_{k <= i} min(1.0, (m - k + 1) * p_(k))
        holm_vals = [0.0] * m
        max_holm = 0.0
        for rank in range(1, m + 1):
            orig_idx, p = indexed[rank - 1]
            p_holm = min(1.0, (m - rank + 1) * p)
            max_holm = max(max_holm, p_holm)
            holm_vals[orig_idx] = round(max_holm, 6)

        # Significant under FDR threshold alpha
        rejected = [q <= alpha for q in q_vals]
        sig_count = sum(1 for r in rejected if r)

        return {
            "total_hypotheses": m,
            "alpha_threshold": alpha,
            "significant_count": sig_count,
            "fdr_rejected": rejected,
            "adjusted_q_values": q_vals,
            "bonferroni_p_values": bonf_vals,
            "holm_p_values": holm_vals,
        }


def research_calculate_bibliometrics(
    citations: List[int],
    publication_years: Optional[List[int]] = None,
    current_year: int = 2026,
) -> Any:
    """Calculates h-index, g-index, i10-index, and citation profile."""
    return Record(
        HIndexAndCitationBibliometrics.compute(
            citations, publication_years=publication_years, current_year=current_year
        )
    )


def research_multiple_testing_correction(
    p_values: List[float],
    alpha: float = 0.05,
) -> Any:
    """Adjusts p-values for multiple hypothesis testing using Benjamini-Hochberg FDR and Holm-Bonferroni."""
    return Record(BenjaminiHochbergMultipleTesting.correct(p_values, alpha=alpha))



