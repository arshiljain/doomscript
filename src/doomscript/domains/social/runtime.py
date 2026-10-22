"""Social Network Analysis Domain Runtime: Degree/Closeness/Betweenness centrality, PageRank, Network density, and Clustering."""
from collections import deque
from typing import Dict, List, Any

def social_degree_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Computes normalized degree centrality for each node in graph: deg(v) / (N - 1)."""
    n = len(graph)
    if n <= 1:
        return {node: 0.0 for node in graph}
    scale = 1.0 / (n - 1)
    return {node: round(len(neighbors) * scale, 4) for node, neighbors in graph.items()}

def social_closeness_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Computes closeness centrality for each node using BFS: (N - 1) / sum(d(u, v))."""
    n = len(graph)
    if n <= 1:
        return {node: 0.0 for node in graph}
    centrality = {}
    for node in graph:
        dist = {node: 0}
        q = deque([node])
        while q:
            curr = q.popleft()
            for neighbor in graph.get(curr, []):
                if neighbor not in dist:
                    dist[neighbor] = dist[curr] + 1
                    q.append(neighbor)
        total_dist = sum(dist.values())
        reachable = len(dist) - 1
        if reachable > 0 and total_dist > 0:
            c = (reachable / (n - 1)) * (reachable / total_dist)
            centrality[node] = round(c, 4)
        else:
            centrality[node] = 0.0
    return centrality

def social_betweenness_centrality(graph: Dict[Any, List[Any]]) -> Dict[Any, float]:
    """Computes betweenness centrality for all nodes using Brandes algorithm on unweighted graph."""
    nodes = list(graph.keys())
    cb = {v: 0.0 for v in nodes}
    for s in nodes:
        stack = []
        pred = {w: [] for w in nodes}
        sigma = {w: 0 for w in nodes}
        sigma[s] = 1
        d = {w: -1 for w in nodes}
        d[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            stack.append(v)
            for w in graph.get(v, []):
                if w not in d:
                    continue
                if d[w] < 0:
                    q.append(w)
                    d[w] = d[v] + 1
                if d[w] == d[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = {w: 0.0 for w in nodes}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                if sigma[w] != 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                cb[w] += delta[w]
    n = len(nodes)
    scale = 1.0 / ((n - 1) * (n - 2)) if n > 2 else 1.0
    return {v: round(cb[v] * scale, 4) for v in nodes}

def social_pagerank(graph: Dict[Any, List[Any]], damping: float = 0.85, max_iter: int = 50) -> Dict[Any, float]:
    """Computes PageRank vector via power iteration."""
    nodes = list(graph.keys())
    n = len(nodes)
    if n == 0:
        return {}
    ranks = {v: 1.0 / n for v in nodes}
    d = float(damping)
    for _ in range(max_iter):
        new_ranks = {v: (1.0 - d) / n for v in nodes}
        for u in nodes:
            out_neighbors = graph.get(u, [])
            if out_neighbors:
                share = (d * ranks[u]) / len(out_neighbors)
                for v in out_neighbors:
                    if v in new_ranks:
                        new_ranks[v] += share
            else:
                # Dangling node distributed evenly
                for v in nodes:
                    new_ranks[v] += (d * ranks[u]) / n
        ranks = new_ranks
    return {k: round(v, 4) for k, v in ranks.items()}

def social_network_density(graph: Dict[Any, List[Any]], directed: bool = False) -> float:
    """Computes edge density of the network: edges / max_possible_edges."""
    n = len(graph)
    if n <= 1:
        return 0.0
    total_edges = sum(len(neighbors) for neighbors in graph.values())
    if not directed:
        total_edges = total_edges / 2.0
        max_edges = n * (n - 1) / 2.0
    else:
        max_edges = float(n * (n - 1))
    return round(total_edges / max_edges, 4)

def social_clustering_coefficient(graph: Dict[Any, List[Any]]) -> float:
    """Computes average local clustering coefficient across all nodes."""
    n = len(graph)
    if n == 0:
        return 0.0
    coeffs = []
    for node, neighbors in graph.items():
        k = len(neighbors)
        if k < 2:
            coeffs.append(0.0)
            continue
        neighbor_set = set(neighbors)
        links = 0
        for u in neighbors:
            for v in graph.get(u, []):
                if v in neighbor_set and u != v:
                    links += 1
        links = links / 2.0
        coeffs.append(links / (k * (k - 1) / 2.0))
    return round(sum(coeffs) / n, 4)
