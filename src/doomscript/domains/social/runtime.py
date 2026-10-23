"""Social Domain Runtime: Social network analysis, centrality metrics, community detection, and influence diffusion."""
import math
import random
from typing import List, Dict, Any, Tuple, Set, Optional
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED CENTRALITY & NETWORK METRICS
# ============================================================================

def social_degree_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Calculates normalized degree centrality for each node."""
    n = len(graph)
    if n <= 1:
        return {node: 0.0 for node in graph}
    scale = 1.0 / (n - 1)
    return {node: round(len(neighbors) * scale, 4) for node, neighbors in graph.items()}

def social_closeness_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Calculates closeness centrality based on reciprocal of shortest path distances."""
    n = len(graph)
    if n <= 1:
        return {node: 0.0 for node in graph}
    centrality = {}
    for source in graph:
        dist = {source: 0}
        q = [source]
        while q:
            curr = q.pop(0)
            for neighbor in graph.get(curr, []):
                if neighbor not in dist:
                    dist[neighbor] = dist[curr] + 1
                    q.append(neighbor)
        total_dist = sum(dist.values())
        reachable = len(dist) - 1
        if total_dist > 0 and reachable > 0:
            c = (reachable / (n - 1)) * (reachable / total_dist)
            centrality[source] = round(c, 4)
        else:
            centrality[source] = 0.0
    return centrality

def social_betweenness_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Calculates Brandes betweenness centrality for all nodes."""
    cb = {node: 0.0 for node in graph}
    nodes = list(graph.keys())
    for s in nodes:
        stack = []
        p: Dict[Any, List[Any]] = {w: [] for w in nodes}
        sigma = {w: 0 for w in nodes}
        sigma[s] = 1
        d = {w: -1 for w in nodes}
        d[s] = 0
        q = [s]
        while q:
            v = q.pop(0)
            stack.append(v)
            for w in graph.get(v, []):
                if d[w] < 0:
                    q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    p[w].append(v)
        delta = {w: 0.0 for w in nodes}
        while stack:
            w = stack.pop()
            for v in p[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]
    n = len(nodes)
    scale = 1.0 / ((n - 1) * (n - 2)) if n > 2 else 1.0
    return {k: round(v * scale, 4) for k, v in cb.items()}

def social_pagerank(graph: Dict[Any, List[Any]], damping: float = 0.85, max_iter: int = 50) -> Dict[Any, float]:
    """Computes PageRank vector via power iteration with teleportation."""
    nodes = list(graph.keys())
    for targets in graph.values():
        for t in targets:
            if t not in graph:
                nodes.append(t)
    nodes = list(set(nodes))
    n = len(nodes)
    if n == 0:
        return {}
    ranks = {u: 1.0 / n for u in nodes}
    for _ in range(max_iter):
        new_ranks = {}
        dangling_sum = sum(ranks[u] for u in nodes if not graph.get(u))
        for u in nodes:
            rank_sum = sum(ranks[v] / len(graph[v]) for v in nodes if u in graph.get(v, []))
            rank_sum += dangling_sum / n
            new_ranks[u] = (1.0 - damping) / n + damping * rank_sum
        diff = sum(abs(new_ranks[u] - ranks[u]) for u in nodes)
        ranks = new_ranks
        if diff < 1e-6:
            break
    return {u: round(r, 6) for u, r in sorted(ranks.items(), key=lambda x: x[1], reverse=True)}

def social_network_density(graph: Dict[Any, List[Any]], directed: bool = False) -> float:
    """Calculates network edge density."""
    n = len(graph)
    if n <= 1:
        return 0.0
    num_edges = sum(len(neighbors) for neighbors in graph.values())
    if not directed:
        num_edges = num_edges / 2.0
        max_edges = n * (n - 1) / 2.0
    else:
        max_edges = float(n * (n - 1))
    return round(num_edges / max_edges, 4)

def social_clustering_coefficient(graph: Dict[Any, List[Any]]) -> float:
    """Calculates average clustering coefficient across the network."""
    local_cc = []
    for u, neighbors in graph.items():
        k = len(neighbors)
        if k < 2:
            continue
        links = 0
        n_list = list(neighbors)
        for i in range(k):
            for j in range(i + 1, k):
                if n_list[j] in graph.get(n_list[i], []):
                    links += 1
        local_cc.append((2.0 * links) / (k * (k - 1)))
    return round(sum(local_cc) / len(local_cc), 4) if local_cc else 0.0

# ============================================================================
# 2. ADVANCED CENTRALITY & COMMUNITY DETECTION
# ============================================================================

def social_hits(graph: Dict[Any, List[Any]], max_iter: int = 50) -> Dict[str, Dict[Any, float]]:
    """Calculates HITS Hubs and Authorities scores for directed networks."""
    nodes = list(set(list(graph.keys()) + [t for targets in graph.values() for t in targets]))
    n = len(nodes)
    if n == 0:
        return {"hubs": {}, "authorities": {}}
    hubs = {u: 1.0 for u in nodes}
    auths = {u: 1.0 for u in nodes}
    for _ in range(max_iter):
        new_auths = {}
        for u in nodes:
            new_auths[u] = sum(hubs[v] for v in nodes if u in graph.get(v, []))
        norm_a = math.sqrt(sum(v * v for v in new_auths.values())) or 1.0
        auths = {u: v / norm_a for u, v in new_auths.items()}
        new_hubs = {}
        for u in nodes:
            new_hubs[u] = sum(auths[t] for t in graph.get(u, []))
        norm_h = math.sqrt(sum(v * v for v in new_hubs.values())) or 1.0
        hubs = {u: v / norm_h for u, v in new_hubs.items()}
    return {
        "hubs": {u: round(hubs[u], 5) for u in sorted(nodes, key=str)},
        "authorities": {u: round(auths[u], 5) for u in sorted(nodes, key=str)}
    }

def social_katz_centrality(graph: Dict[Any, List[Any]], alpha: float = 0.1, beta: float = 1.0, max_iter: int = 100) -> Dict[Any, float]:
    """Calculates Katz centrality incorporating path attenuation."""
    nodes = list(graph.keys())
    katz = {u: 0.0 for u in nodes}
    for _ in range(max_iter):
        new_katz = {}
        for u in nodes:
            incoming_sum = sum(katz[v] for v in nodes if u in graph.get(v, []))
            new_katz[u] = alpha * incoming_sum + beta
        diff = sum(abs(new_katz[u] - katz[u]) for u in nodes)
        katz = new_katz
        if diff < 1e-5:
            break
    norm = math.sqrt(sum(v * v for v in katz.values())) or 1.0
    return {u: round(v / norm, 4) for u, v in katz.items()}

def social_independent_cascade(graph: Dict[Any, List[Any]], seeds: List[Any], prob: float = 0.1, steps: int = 10) -> Dict[str, Any]:
    """Simulates information/epidemic spread via Independent Cascade model."""
    active = set(seeds)
    newly_active = set(seeds)
    history = [len(active)]
    for _ in range(steps):
        next_active = set()
        for u in newly_active:
            for v in graph.get(u, []):
                if v not in active:
                    if random.random() < prob:
                        next_active.add(v)
        if not next_active:
            break
        active.update(next_active)
        newly_active = next_active
        history.append(len(active))
    return {
        "total_activated": len(active),
        "seed_count": len(seeds),
        "activated_nodes": list(active),
        "spread_curve": history
    }

def social_adamic_adar(graph: Dict[Any, List[Any]], u: Any, v: Any) -> float:
    """Calculates Adamic-Adar link prediction score between two nodes."""
    neighbors_u = set(graph.get(u, []))
    neighbors_v = set(graph.get(v, []))
    common = neighbors_u.intersection(neighbors_v)
    score = 0.0
    for w in common:
        deg = len(graph.get(w, []))
        if deg > 1:
            score += 1.0 / math.log(deg)
    return round(score, 4)

def social_k_core(graph: Dict[Any, List[Any]], k: int = 2) -> Dict[str, Any]:
    """Extracts k-core subgraph where all vertices have degree at least k."""
    degrees = {u: len(graph.get(u, [])) for u in graph}
    remaining = set(graph.keys())
    changed = True
    while changed:
        changed = False
        to_remove = [u for u in remaining if degrees[u] < k]
        if to_remove:
            changed = True
            for u in to_remove:
                remaining.remove(u)
                for v in graph.get(u, []):
                    if v in degrees:
                        degrees[v] -= 1
    return {"k": k, "core_nodes": list(remaining), "core_size": len(remaining)}

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class SocialRuntime(DomainRuntime):
    """Unified runtime bridge for the Social computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def degree(self, g: Dict[Any, List[Any]]) -> Dict[Any, float]:
        return social_degree_centrality(g)
    def closeness(self, g: Dict[Any, List[Any]]) -> Dict[Any, float]:
        return social_closeness_centrality(g)
    def betweenness(self, g: Dict[Any, List[Any]]) -> Dict[Any, float]:
        return social_betweenness_centrality(g)
    def pagerank(self, g: Dict[Any, List[Any]], damping: float = 0.85) -> Dict[Any, float]:
        return social_pagerank(g, damping)
    def density(self, g: Dict[Any, List[Any]], directed: bool = False) -> float:
        return social_network_density(g, directed)
    def clustering(self, g: Dict[Any, List[Any]]) -> float:
        return social_clustering_coefficient(g)
    def hits(self, g: Dict[Any, List[Any]]) -> Dict[str, Dict[Any, float]]:
        return social_hits(g)
    def katz(self, g: Dict[Any, List[Any]], alpha: float = 0.1) -> Dict[Any, float]:
        return social_katz_centrality(g, alpha)
    def cascade(self, g: Dict[Any, List[Any]], seeds: List[Any], p: float = 0.1) -> Dict[str, Any]:
        return social_independent_cascade(g, seeds, p)
    def adamic_adar(self, g: Dict[Any, List[Any]], u: Any, v: Any) -> float:
        return social_adamic_adar(g, u, v)
    def k_core(self, g: Dict[Any, List[Any]], k: int = 2) -> Dict[str, Any]:
        return social_k_core(g, k)
