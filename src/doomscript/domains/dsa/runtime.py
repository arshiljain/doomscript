"""Runtime execution engine for Testing & Algorithm Analysis (DSA)."""

import math
import random
import time
import tracemalloc
from typing import Any, Callable, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.dsa.spec import BenchmarkSpec, ComplexityReport


class ListNode:
    """Standard LeetCode singly-linked list node."""

    def __init__(self, val: int = 0, next: Optional["ListNode"] = None):
        self.val = val
        self.next = next

    def to_list(self) -> List[Any]:
        res = []
        curr = self
        while curr:
            res.append(curr.val)
            curr = curr.next
        return res

    @classmethod
    def from_list(cls, items: List[Any]) -> Optional["ListNode"]:
        if not items:
            return None
        head = cls(items[0])
        curr = head
        for x in items[1:]:
            curr.next = cls(x)
            curr = curr.next
        return head

    def __repr__(self):
        return f"ListNode({self.to_list()})"


class TreeNode:
    """Standard LeetCode binary tree node."""

    def __init__(
        self,
        val: int = 0,
        left: Optional["TreeNode"] = None,
        right: Optional["TreeNode"] = None,
    ):
        self.val = val
        self.left = left
        self.right = right

    def inorder(self) -> List[Any]:
        res = []
        if self.left:
            res.extend(self.left.inorder())
        res.append(self.val)
        if self.right:
            res.extend(self.right.inorder())
        return res

    def __repr__(self):
        return f"TreeNode({self.val})"


def trace_recursion(fn_or_name: Any, *args, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Executes a recursive function while instrumenting call tree, depth, and frames."""
    import sys
    f = sys._getframe(1)
    if scope is None:
        target_dict = f.f_globals if (f.f_globals is not None and fn_or_name in f.f_globals) else f.f_locals
    else:
        target_dict = scope

    if isinstance(fn_or_name, str):
        fn = target_dict.get(fn_or_name)
        fn_name = fn_or_name
    else:
        fn = fn_or_name
        fn_name = getattr(fn, "__name__", "fn")

    if not callable(fn):
        raise ValueError(f"Target '{fn_or_name}' is not callable")

    events = []
    call_count = 0
    max_depth = 0
    current_depth = 0

    orig_fn = fn
    def wrapped(*call_args, **call_kwargs):
        nonlocal call_count, max_depth, current_depth
        call_count += 1
        current_depth += 1
        if current_depth > max_depth:
            max_depth = current_depth
        events.append({"type": "call", "depth": current_depth, "args": call_args})
        try:
            res = orig_fn(*call_args, **call_kwargs)
            events.append({"type": "return", "depth": current_depth, "result": res})
            return res
        finally:
            current_depth -= 1

    target_dict[fn_name] = wrapped
    try:
        final_res = wrapped(*args)
    finally:
        target_dict[fn_name] = orig_fn

    return {
        "fn_name": fn_name,
        "call_count": call_count,
        "max_depth": max_depth,
        "result": final_res,
        "events": events,
    }


def _generate_input(generator: str, size: int) -> List[int]:
    gen = generator.lower()
    if gen in ("sorted_integers", "sorted"):
        return list(range(size))
    elif gen in ("reversed_integers", "reversed"):
        return list(range(size, 0, -1))
    elif gen in ("random_integers", "random"):
        rng = random.Random(42)
        return [rng.randint(0, size * 10) for _ in range(size)]
    return list(range(size))


def fit_complexity(sizes: List[int], times: List[float]) -> Tuple[str, float, Dict[str, float]]:
    """Fits empirical timing data to theoretical Big-O curves and returns best fit and R2 scores."""
    if len(sizes) < 2:
        return "O(1)", 1.0, {"O(1)": 1.0}

    candidates = {
        "O(1)": [1.0 for _ in sizes],
        "O(log n)": [math.log2(max(s, 2)) for s in sizes],
        "O(n)": [float(s) for s in sizes],
        "O(n log n)": [float(s) * math.log2(max(s, 2)) for s in sizes],
        "O(n^2)": [float(s) ** 2 for s in sizes],
    }

    mean_y = sum(times) / len(times)
    ss_tot = sum((t - mean_y) ** 2 for t in times)
    if ss_tot == 0.0:
        return "O(1)", 1.0, {"O(1)": 1.0}

    r2_scores: Dict[str, float] = {}

    for name, f_vals in candidates.items():
        # Simple linear regression: y = slope * f_val + intercept
        n = len(sizes)
        mean_x = sum(f_vals) / n
        var_x = sum((x - mean_x) ** 2 for x in f_vals)
        cov_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(f_vals, times))

        if var_x == 0.0:
            r2_scores[name] = 1.0 if ss_tot == 0.0 else 0.0
            continue

        slope = cov_xy / var_x
        intercept = mean_y - slope * mean_x

        preds = [slope * x + intercept for x in f_vals]
        ss_res = sum((y - p) ** 2 for y, p in zip(times, preds))
        r2 = 1.0 - (ss_res / ss_tot)
        r2_scores[name] = max(0.0, min(1.0, r2))

    best_fit = max(r2_scores.items(), key=lambda it: it[1])[0]

    # If timings grew significantly (e.g., >= 1.8x between smallest and largest size),
    # sublinear O(log n) or O(1) is physically ruled out when sizes grow multifold.
    time_ratio = (times[-1] / max(times[0], 1e-9)) if len(times) >= 2 else 1.0
    if time_ratio >= 1.8 and best_fit in ("O(1)", "O(log n)") and "O(n)" in r2_scores and r2_scores["O(n)"] >= 0.70:
        best_fit = "O(n)"

    # If O(n) explains >= 85% of variance and is within 0.05 of O(n^2) or O(n log n), prefer O(n)
    if "O(n)" in r2_scores and r2_scores["O(n)"] >= 0.85:
        if best_fit in ("O(n^2)", "O(n log n)") and (r2_scores[best_fit] - r2_scores["O(n)"] <= 0.05):
            best_fit = "O(n)"

    return best_fit, r2_scores[best_fit], r2_scores


def run_benchmark(spec: BenchmarkSpec, scope: Dict[str, Any]) -> Dict[str, Any]:
    """Executes high-resolution timing and memory benchmark across multiple input sizes."""
    fn = scope.get(spec.fn_name)
    if not callable(fn):
        raise ValueError(f"Benchmark function '{spec.fn_name}' not found or not callable")

    timings: Dict[int, float] = {}
    peak_memory = 0

    measure_mem = spec.measure_memory
    if measure_mem:
        tracemalloc.start()

    for size in spec.input_sizes:
        data = _generate_input(spec.generator, size)

        # Warmup
        try:
            fn(data)
        except TypeError:
            fn(data, 0)
        except Exception:
            pass

        # Measurement iterations
        iter_times = []
        for _ in range(spec.repeat):
            test_data = list(data)
            t0 = time.perf_counter_ns()
            try:
                fn(test_data)
            except TypeError:
                fn(test_data, 0)
            except Exception:
                pass
            t1 = time.perf_counter_ns()
            iter_times.append((t1 - t0) / 1e9)  # seconds

        timings[size] = min(iter_times)

    if measure_mem:
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    sizes_list = list(timings.keys())
    times_list = list(timings.values())
    best_fit, r2, fits = fit_complexity(sizes_list, times_list)

    report = ComplexityReport(
        fn_name=spec.fn_name,
        best_fit=best_fit,
        confidence_r2=r2,
        timings=timings,
        peak_memory_bytes=peak_memory,
        fits=fits,
    )
    res_dict = report.to_dict()
    if spec.target_var:
        scope[spec.target_var] = res_dict
    return res_dict


def profile_memory_of_function(
    fn_name: str, input_expr: Any, scope: Dict[str, Any]
) -> Dict[str, Any]:
    """Level 2: Profiles peak and allocated memory for a single function execution."""
    fn = scope.get(fn_name)
    if not callable(fn):
        raise ValueError(f"Function '{fn_name}' not found or not callable")

    tracemalloc.start()
    t0 = time.perf_counter_ns()
    res = fn(input_expr)
    t1 = time.perf_counter_ns()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "function": fn_name,
        "peak_memory_bytes": peak,
        "current_memory_bytes": current,
        "execution_time_seconds": round((t1 - t0) / 1e9, 6),
        "result": res,
    }


class DsaRuntime(DomainRuntime):
    """Runtime engine for Algorithm Analysis and Benchmarking."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if not isinstance(ir, BenchmarkSpec):
            raise TypeError(f"DsaRuntime expects BenchmarkSpec, got {type(ir).__name__}")
        return run_benchmark(ir, scope)


# =========================================================================
# Advanced First-Class DSA Primitives & Algorithmic Engines
# =========================================================================

class _MaxHeapEntry:
    """Wrapper to invert comparisons for native max-heap without numeric negation."""

    def __init__(self, val: Any):
        self.val = val

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, _MaxHeapEntry):
            return self.val > other.val
        return self.val > other

    def __le__(self, other: Any) -> bool:
        if isinstance(other, _MaxHeapEntry):
            return self.val >= other.val
        return self.val >= other

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, _MaxHeapEntry):
            return self.val < other.val
        return self.val < other

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, _MaxHeapEntry):
            return self.val <= other.val
        return self.val <= other

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, _MaxHeapEntry):
            return self.val == other.val
        return self.val == other

    def __repr__(self) -> str:
        return repr(self.val)


class DsaHeap:
    """Universal min/max priority queue supporting any comparable objects."""

    def __init__(self, kind: str = "min"):
        import heapq
        self.kind = kind.lower()
        self._data: List[Any] = []

    def push(self, item: Any) -> None:
        import heapq
        if self.kind == "max":
            heapq.heappush(self._data, _MaxHeapEntry(item))
        else:
            heapq.heappush(self._data, item)

    def pop(self) -> Any:
        import heapq
        if not self._data:
            return None
        res = heapq.heappop(self._data)
        if self.kind == "max":
            return res.val
        return res

    def peek(self) -> Any:
        if not self._data:
            return None
        item = self._data[0]
        if self.kind == "max":
            return item.val
        return item

    def __len__(self) -> int:
        return len(self._data)

    def __bool__(self) -> bool:
        return len(self._data) > 0

    def to_list(self) -> List[Any]:
        if self.kind == "max":
            return [x.val for x in self._data]
        return list(self._data)

    def __repr__(self) -> str:
        return f"DsaHeap(kind={self.kind}, size={len(self)})"


def dsa_create_heap(kind: str = "min") -> DsaHeap:
    """Create a new universal min or max heap."""
    return DsaHeap(kind=kind)


def dsa_create_deque() -> Any:
    """Create a double-ended queue."""
    from collections import deque
    return deque()


def dsa_peek_min(coll: Any) -> Any:
    """Peek the minimum element from a heap or list without removing."""
    if isinstance(coll, DsaHeap):
        return coll.peek()
    if isinstance(coll, (list, tuple)) and coll:
        return min(coll)
    return None


def dsa_peek_max(coll: Any) -> Any:
    """Peek the maximum element from a heap or list without removing."""
    if isinstance(coll, DsaHeap):
        return coll.peek()
    if isinstance(coll, (list, tuple)) and coll:
        return max(coll)
    return None


def dsa_peek_left(coll: Any) -> Any:
    """Peek the first/left element without removing."""
    from collections import deque
    if isinstance(coll, (list, deque)) and len(coll) > 0:
        return coll[0]
    return None


def dsa_pop_right(coll: Any) -> Any:
    """Pop the last/right element from a deque or list."""
    from collections import deque
    if isinstance(coll, deque):
        return coll.pop() if coll else None
    if isinstance(coll, list):
        return coll.pop() if coll else None
    return None


def dsa_push_left(coll: Any, item: Any) -> Any:
    """Push an item to the left/front of a deque or list."""
    from collections import deque
    if isinstance(coll, deque):
        coll.appendleft(item)
    elif isinstance(coll, list):
        coll.insert(0, item)
    return coll


# --- Grids & Connected Components ---

def dsa_create_grid(rows: Any, cols: Any, fill: Any = 0) -> List[List[Any]]:
    """Safely allocate a 2D matrix without list-multiplication reference duplication."""
    r = int(rows)
    c = int(cols)
    return [[fill for _ in range(c)] for _ in range(r)]


def dsa_is_inside_grid(r: Any, c: Any, grid: Any) -> bool:
    """Verify if row and col coordinates fall within grid bounds."""
    if not isinstance(grid, list) or not grid:
        return False
    rows = len(grid)
    cols = len(grid[0]) if isinstance(grid[0], list) else 0
    return 0 <= int(r) < rows and 0 <= int(c) < cols


def dsa_connected_components_grid(
    grid: List[List[Any]], cell_val: Any, connectivity: Any = 4
) -> List[List[Tuple[int, int]]]:
    """Find connected coordinate groups in a 2D grid using 4-way or 8-way traversal."""
    if not isinstance(grid, list) or not grid:
        return []
    rows = len(grid)
    cols = len(grid[0]) if isinstance(grid[0], list) else 0
    visited = set()
    components: List[List[Tuple[int, int]]] = []

    conn_int = int(connectivity) if str(connectivity).isdigit() else 4
    if conn_int == 8:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    else:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == cell_val and (r, c) not in visited:
                comp = []
                queue = [(r, c)]
                visited.add((r, c))
                while queue:
                    curr_r, curr_c = queue.pop(0)
                    comp.append((curr_r, curr_c))
                    for dr, dc in directions:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] == cell_val and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                components.append(comp)
    return components


def dsa_count_connected_components_grid(
    grid: List[List[Any]], cell_val: Any, connectivity: Any = 4
) -> int:
    """Count connected coordinate groups in a 2D grid."""
    return len(dsa_connected_components_grid(grid, cell_val, connectivity))


# --- Graphs: Cycle Detection, Topological Sort, Shortest Path ---

class DsaGraph:
    """Algorithmic graph engine supporting edge parsing, cycle checks, and topological sort."""

    def __init__(self, directed: bool = True):
        self.directed = directed
        self.adj: Dict[Any, List[Tuple[Any, float]]] = {}
        self.nodes: Set[Any] = set()

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        self.nodes.add(u)
        self.nodes.add(v)
        if u not in self.adj:
            self.adj[u] = []
        self.adj[u].append((v, weight))
        if not self.directed:
            if v not in self.adj:
                self.adj[v] = []
            self.adj[v].append((u, weight))

    def has_cycle(self) -> bool:
        """Cycle detection using 3-color DFS traversal."""
        visited: Dict[Any, int] = {node: 0 for node in self.nodes}

        def dfs(u: Any) -> bool:
            visited[u] = 1  # in-progress
            for v, _ in self.adj.get(u, []):
                if visited.get(v, 0) == 1:
                    return True
                if visited.get(v, 0) == 0:
                    if dfs(v):
                        return True
            visited[u] = 2  # finished
            return False

        for node in list(self.nodes):
            if visited[node] == 0:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> List[Any]:
        """Kahn's algorithm for topological ordering."""
        in_degree: Dict[Any, int] = {node: 0 for node in self.nodes}
        for u in self.adj:
            for v, _ in self.adj[u]:
                in_degree[v] = in_degree.get(v, 0) + 1

        queue = [node for node in self.nodes if in_degree[node] == 0]
        order = []
        while queue:
            u = queue.pop(0)
            order.append(u)
            for v, _ in self.adj.get(u, []):
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        if len(order) < len(self.nodes):
            return []  # Cycle present
        return order

    def shortest_path(self, start: Any, end: Any) -> Optional[List[Any]]:
        """Dijkstra's shortest path from start to end."""
        import heapq
        if start not in self.nodes:
            return None
        pq = [(0.0, start, [start])]
        visited = set()
        while pq:
            cost, curr, path = heapq.heappop(pq)
            if curr == end:
                return path
            if curr in visited:
                continue
            visited.add(curr)
            for neighbor, weight in self.adj.get(curr, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (cost + weight, neighbor, path + [neighbor]))
        return None

    def connected_components(self) -> List[List[Any]]:
        """Find connected components treating graph as undirected connectivity."""
        visited = set()
        comps = []
        for node in self.nodes:
            if node not in visited:
                comp = []
                queue = [node]
                visited.add(node)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    neighbors = [v for v, _ in self.adj.get(curr, [])]
                    for u in self.adj:
                        for v, _ in self.adj[u]:
                            if v == curr:
                                neighbors.append(u)
                    for nbr in neighbors:
                        if nbr not in visited:
                            visited.add(nbr)
                            queue.append(nbr)
                comps.append(comp)
        return comps


def dsa_build_graph(edges: Any, directed: bool = True) -> DsaGraph:
    """Build a DsaGraph directly from an edge list or pairs."""
    g = DsaGraph(directed=directed)
    if isinstance(edges, (list, tuple)):
        for edge in edges:
            if isinstance(edge, (list, tuple)):
                if len(edge) >= 3:
                    g.add_edge(edge[0], edge[1], float(edge[2]))
                elif len(edge) == 2:
                    g.add_edge(edge[0], edge[1], 1.0)
                elif len(edge) == 1:
                    g.nodes.add(edge[0])
            else:
                g.nodes.add(edge)
    return g


def dsa_graph_has_cycle(g: Any) -> bool:
    if isinstance(g, DsaGraph):
        return g.has_cycle()
    return False


def dsa_graph_topological_sort(g: Any) -> List[Any]:
    if isinstance(g, DsaGraph):
        return g.topological_sort()
    return []


def dsa_graph_shortest_path(g: Any, start: Any, end: Any) -> Optional[List[Any]]:
    if isinstance(g, DsaGraph):
        return g.shortest_path(start, end)
    return None


def dsa_graph_connected_components(g: Any) -> List[List[Any]]:
    if isinstance(g, DsaGraph):
        return g.connected_components()
    return []


# --- Memoization ---

def dsa_memoize(fn_name_or_fn: Any, scope: Optional[Dict[str, Any]] = None) -> Any:
    """Automatically memoize a recursive or heavy function, handling unhashable inputs."""
    if scope is None:
        import sys
        f = sys._getframe(1)
        scope = f.f_globals if (f.f_globals is not None and fn_name_or_fn in f.f_globals) else f.f_locals

    if isinstance(fn_name_or_fn, str):
        fn = scope.get(fn_name_or_fn)
        name = fn_name_or_fn
    else:
        fn = fn_name_or_fn
        name = getattr(fn, "__name__", "memoized_fn")

    if not callable(fn):
        raise ValueError(f"Target '{fn_name_or_fn}' is not callable")

    cache: Dict[Tuple[Any, ...], Any] = {}

    def _to_key(arg: Any) -> Any:
        if isinstance(arg, list):
            return tuple(_to_key(x) for x in arg)
        if isinstance(arg, dict):
            return tuple(sorted((k, _to_key(v)) for k, v in arg.items()))
        return arg

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (tuple(_to_key(a) for a in args), tuple(sorted((k, _to_key(v)) for k, v in kwargs.items())))
        if key in cache:
            return cache[key]
        res = fn(*args, **kwargs)
        cache[key] = res
        return res

    wrapper.__name__ = name
    wrapper.cache = cache
    if scope is not None and isinstance(fn_name_or_fn, str):
        scope[fn_name_or_fn] = wrapper
    return wrapper


# --- Intervals ---

def dsa_merge_intervals(intervals: Any) -> List[List[Any]]:
    """Merge overlapping intervals in O(n log n) time."""
    if not isinstance(intervals, (list, tuple)) or not intervals:
        return []
    sorted_int = sorted(intervals, key=lambda x: x[0])
    merged = [list(sorted_int[0])]
    for current in sorted_int[1:]:
        prev = merged[-1]
        if current[0] <= prev[1]:
            prev[1] = max(prev[1], current[1])
        else:
            merged.append(list(current))
    return merged


def dsa_intersect_intervals(a: Any, b: Any) -> List[List[Any]]:
    """Compute the interval intersections of two sorted interval lists."""
    if not a or not b:
        return []
    i = 0
    j = 0
    res = []
    while i < len(a) and j < len(b):
        start = max(a[i][0], b[j][0])
        end = min(a[i][1], b[j][1])
        if start <= end:
            res.append([start, end])
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return res


# --- Frequency Maps & Sliding Window ---

def dsa_frequency_map(collection: Any) -> Dict[Any, int]:
    """Compute element counts/frequencies in O(n) time."""
    freq: Dict[Any, int] = {}
    if collection is None:
        return freq
    for item in collection:
        freq[item] = freq.get(item, 0) + 1
    return freq


def dsa_sliding_window_max(arr: Any, k: Any) -> List[Any]:
    """Compute sliding window maximum using an optimal O(n) monotonic queue."""
    from collections import deque
    if not arr or int(k) <= 0:
        return []
    window_k = min(int(k), len(arr))
    q: deque[int] = deque()
    res = []
    for i in range(len(arr)):
        if q and q[0] < i - window_k + 1:
            q.popleft()
        while q and arr[q[-1]] < arr[i]:
            q.pop()
        q.append(i)
        if i >= window_k - 1:
            res.append(arr[q[0]])
    return res


# =========================================================================
# 13 Additional Algorithmic Powers
# =========================================================================

# 1. Trie Engine
class DsaTrie:
    """Prefix tree data structure for string dictionary and autocomplete."""

    def __init__(self):
        self.root: Dict[str, Any] = {}
        self.end_symbol = "__END__"

    def insert(self, word: str) -> None:
        curr = self.root
        for char in str(word):
            if char not in curr:
                curr[char] = {}
            curr = curr[char]
        curr[self.end_symbol] = True

    def contains(self, word: str) -> bool:
        curr = self.root
        for char in str(word):
            if char not in curr:
                return False
            curr = curr[char]
        return self.end_symbol in curr

    def starts_with(self, prefix: str) -> bool:
        curr = self.root
        for char in str(prefix):
            if char not in curr:
                return False
            curr = curr[char]
        return True

    def all_words_with_prefix(self, prefix: str) -> List[str]:
        curr = self.root
        for char in str(prefix):
            if char not in curr:
                return []
            curr = curr[char]
        words: List[str] = []

        def dfs(node: Dict[str, Any], path: str):
            if self.end_symbol in node:
                words.append(path)
            for ch, child in node.items():
                if ch != self.end_symbol:
                    dfs(child, path + ch)

        dfs(curr, str(prefix))
        return words


def dsa_create_trie() -> DsaTrie:
    return DsaTrie()


def dsa_trie_insert(trie: Any, word: Any) -> Any:
    if isinstance(trie, DsaTrie):
        trie.insert(str(word))
    return trie


def dsa_trie_contains(trie: Any, word: Any) -> bool:
    if isinstance(trie, DsaTrie):
        return trie.contains(str(word))
    return False


def dsa_trie_starts_with(trie: Any, prefix: Any) -> bool:
    if isinstance(trie, DsaTrie):
        return trie.starts_with(str(prefix))
    return False


def dsa_trie_words_with_prefix(trie: Any, prefix: Any) -> List[str]:
    if isinstance(trie, DsaTrie):
        return trie.all_words_with_prefix(str(prefix))
    return []


# 2. Disjoint Set Union (DSU / Union-Find)
class DsaDisjointSet:
    """Disjoint Set Union (Union-Find) with path compression and rank optimization."""

    def __init__(self, size: int):
        n = int(size)
        self.parent = list(range(n))
        self.rank = [0] * n
        self.num_sets = n

    def find(self, x: int) -> int:
        idx = int(x)
        if self.parent[idx] != idx:
            self.parent[idx] = self.find(self.parent[idx])
        return self.parent[idx]

    def union(self, x: int, y: int) -> bool:
        rx = self.find(x)
        ry = self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1
        self.num_sets -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)

    def count(self) -> int:
        return self.num_sets


def dsa_create_disjoint_set(size: Any) -> DsaDisjointSet:
    return DsaDisjointSet(int(size))


def dsa_dsu_union(dsu: Any, x: Any, y: Any) -> bool:
    if isinstance(dsu, DsaDisjointSet):
        return dsu.union(int(x), int(y))
    return False


def dsa_dsu_find(dsu: Any, x: Any) -> int:
    if isinstance(dsu, DsaDisjointSet):
        return dsu.find(int(x))
    return int(x)


def dsa_dsu_connected(dsu: Any, x: Any, y: Any) -> bool:
    if isinstance(dsu, DsaDisjointSet):
        return dsu.connected(int(x), int(y))
    return False


def dsa_dsu_count(dsu: Any) -> int:
    if isinstance(dsu, DsaDisjointSet):
        return dsu.count()
    return 0


# 3. Binary Tree Operations
def dsa_build_binary_tree(vals: Any) -> Optional[TreeNode]:
    """Construct binary tree from level-order list representation with null values."""
    if not isinstance(vals, (list, tuple)) or not vals:
        return None
    root = TreeNode(vals[0])
    queue = [root]
    i = 1
    while i < len(vals) and queue:
        curr = queue.pop(0)
        if i < len(vals) and vals[i] is not None:
            curr.left = TreeNode(vals[i])
            queue.append(curr.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            curr.right = TreeNode(vals[i])
            queue.append(curr.right)
        i += 1
    return root


def dsa_level_order(root: Any) -> List[List[Any]]:
    """Level order (BFS) traversal of binary tree."""
    if not isinstance(root, TreeNode) or not root:
        return []
    levels: List[List[Any]] = []
    queue = [root]
    while queue:
        level_size = len(queue)
        curr_level = []
        for _ in range(level_size):
            node = queue.pop(0)
            curr_level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(curr_level)
    return levels


def dsa_preorder(root: Any) -> List[Any]:
    res: List[Any] = []
    def dfs(n: Any):
        if n:
            res.append(n.val)
            dfs(n.left)
            dfs(n.right)
    dfs(root)
    return res


def dsa_inorder(root: Any) -> List[Any]:
    res: List[Any] = []
    def dfs(n: Any):
        if n:
            dfs(n.left)
            res.append(n.val)
            dfs(n.right)
    dfs(root)
    return res


def dsa_postorder(root: Any) -> List[Any]:
    res: List[Any] = []
    def dfs(n: Any):
        if n:
            dfs(n.left)
            dfs(n.right)
            res.append(n.val)
    dfs(root)
    return res


def dsa_tree_max_depth(root: Any) -> int:
    if not isinstance(root, TreeNode) or not root:
        return 0
    return 1 + max(dsa_tree_max_depth(root.left), dsa_tree_max_depth(root.right))


def dsa_invert_binary_tree(root: Any) -> Any:
    if not isinstance(root, TreeNode) or not root:
        return None
    root.left, root.right = dsa_invert_binary_tree(root.right), dsa_invert_binary_tree(root.left)
    return root


# 4. Binary Search / Bisect Suite
def dsa_binary_search(arr: Any, target: Any) -> int:
    """Standard logarithmic binary search returning exact index or -1."""
    if not isinstance(arr, (list, tuple)):
        return -1
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def dsa_lower_bound(arr: Any, target: Any) -> int:
    """Find the first index where arr[i] >= target (bisect_left)."""
    if not isinstance(arr, (list, tuple)):
        return 0
    low, high = 0, len(arr)
    while low < high:
        mid = (low + high) // 2
        if arr[mid] < target:
            low = mid + 1
        else:
            high = mid
    return low


def dsa_upper_bound(arr: Any, target: Any) -> int:
    """Find the first index where arr[i] > target (bisect_right)."""
    if not isinstance(arr, (list, tuple)):
        return 0
    low, high = 0, len(arr)
    while low < high:
        mid = (low + high) // 2
        if arr[mid] <= target:
            low = mid + 1
        else:
            high = mid
    return low


# 5. Monotonic Stack Engine
def dsa_next_greater_elements(arr: Any) -> List[Any]:
    """Find the next greater element for each index in O(n) time."""
    if not isinstance(arr, (list, tuple)):
        return []
    n = len(arr)
    res = [-1] * n
    stack: List[int] = []
    for i in range(n):
        while stack and arr[stack[-1]] < arr[i]:
            idx = stack.pop()
            res[idx] = arr[i]
        stack.append(i)
    return res


def dsa_next_smaller_elements(arr: Any) -> List[Any]:
    """Find the next smaller element for each index in O(n) time."""
    if not isinstance(arr, (list, tuple)):
        return []
    n = len(arr)
    res = [-1] * n
    stack: List[int] = []
    for i in range(n):
        while stack and arr[stack[-1]] > arr[i]:
            idx = stack.pop()
            res[idx] = arr[i]
        stack.append(i)
    return res


def dsa_previous_greater_elements(arr: Any) -> List[Any]:
    """Find the previous greater element for each index in O(n) time."""
    if not isinstance(arr, (list, tuple)):
        return []
    n = len(arr)
    res = [-1] * n
    stack: List[Any] = []
    for i in range(n):
        while stack and stack[-1] <= arr[i]:
            stack.pop()
        if stack:
            res[i] = stack[-1]
        stack.append(arr[i])
    return res


# 6. Combinatorics & Power Set
def dsa_permutations(items: Any) -> List[List[Any]]:
    import itertools
    if not items:
        return []
    return [list(p) for p in itertools.permutations(items)]


def dsa_combinations(items: Any, k: Any) -> List[List[Any]]:
    import itertools
    if not items:
        return []
    return [list(c) for c in itertools.combinations(items, int(k))]


def dsa_power_set(items: Any) -> List[List[Any]]:
    import itertools
    if items is None:
        return []
    res = []
    lst = list(items)
    for r in range(len(lst) + 1):
        res.extend([list(c) for c in itertools.combinations(lst, r)])
    return res


# 7. Linked List Engine
def dsa_build_linked_list(items: Any) -> Optional[ListNode]:
    if not isinstance(items, (list, tuple)):
        return None
    return ListNode.from_list(list(items))


def dsa_reverse_linked_list(head: Any) -> Optional[ListNode]:
    prev = None
    curr = head
    while curr:
        nxt = curr.next
        curr.next = prev
        prev = curr
        curr = nxt
    return prev


def dsa_linked_list_has_cycle(head: Any) -> bool:
    slow = head
    fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False


def dsa_linked_list_to_list(head: Any) -> List[Any]:
    if isinstance(head, ListNode):
        return head.to_list()
    return []


# 8. Kadane's Algorithm
def dsa_max_subarray_sum(nums: Any) -> Any:
    """Maximum subarray sum in O(n) time and O(1) space."""
    if not isinstance(nums, (list, tuple)) or not nums:
        return 0
    max_so_far = nums[0]
    curr_max = nums[0]
    for x in nums[1:]:
        curr_max = max(x, curr_max + x)
        max_so_far = max(max_so_far, curr_max)
    return max_so_far


def dsa_max_subarray(nums: Any) -> List[Any]:
    """Retrieve the continuous subarray achieving the maximum sum."""
    if not isinstance(nums, (list, tuple)) or not nums:
        return []
    max_so_far = nums[0]
    curr_max = nums[0]
    start = end = s = 0
    for i, x in enumerate(nums[1:], 1):
        if x > curr_max + x:
            curr_max = x
            s = i
        else:
            curr_max += x
        if curr_max > max_so_far:
            max_so_far = curr_max
            start = s
            end = i
    return list(nums[start : end + 1])


# 9. Prefix Sums & 2D Prefix Sums
def dsa_prefix_sums(nums: Any) -> List[Any]:
    pref = [0]
    if nums:
        for x in nums:
            pref.append(pref[-1] + x)
    return pref


def dsa_range_sum(pref: Any, left: Any, right: Any) -> Any:
    l = int(left)
    r = int(right)
    return pref[r + 1] - pref[l]


def dsa_prefix_sums_2d(matrix: Any) -> List[List[Any]]:
    if not matrix or not matrix[0]:
        return []
    m, n = len(matrix), len(matrix[0])
    pref = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m):
        for j in range(n):
            pref[i + 1][j + 1] = matrix[i][j] + pref[i][j + 1] + pref[i + 1][j] - pref[i][j]
    return pref


def dsa_query_range_sum_2d(pref2d: Any, r1: Any, c1: Any, r2: Any, c2: Any) -> Any:
    row1, col1, row2, col2 = int(r1), int(c1), int(r2), int(c2)
    return pref2d[row2 + 1][col2 + 1] - pref2d[row1][col2 + 1] - pref2d[row2 + 1][col1] + pref2d[row1][col1]


# 10. Two-Pointer Pairs & Triplets
def dsa_find_pair_sum(sorted_arr: Any, target: Any) -> Optional[List[Any]]:
    if not isinstance(sorted_arr, (list, tuple)):
        return None
    l, r = 0, len(sorted_arr) - 1
    t = target
    while l < r:
        s = sorted_arr[l] + sorted_arr[r]
        if s == t:
            return [sorted_arr[l], sorted_arr[r]]
        elif s < t:
            l += 1
        else:
            r -= 1
    return None


def dsa_find_triplets_sum(nums: Any, target: Any = 0) -> List[List[Any]]:
    if not isinstance(nums, (list, tuple)):
        return []
    arr = sorted(nums)
    triplets = []
    n = len(arr)
    t = target
    for i in range(n - 2):
        if i > 0 and arr[i] == arr[i - 1]:
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = arr[i] + arr[l] + arr[r]
            if s == t:
                triplets.append([arr[i], arr[l], arr[r]])
                while l < r and arr[l] == arr[l + 1]:
                    l += 1
                while l < r and arr[r] == arr[r - 1]:
                    r -= 1
                l += 1
                r -= 1
            elif s < t:
                l += 1
            else:
                r -= 1
    return triplets


# 11. Minimum Spanning Tree (MST)
def dsa_minimum_spanning_tree(g: Any) -> List[List[Any]]:
    if not isinstance(g, DsaGraph):
        return []
    edges = []
    for u in g.adj:
        for v, w in g.adj[u]:
            if g.directed or u < v:
                edges.append((w, u, v))
    edges.sort()
    nodes = list(g.nodes)
    node_to_idx = {node: i for i, node in enumerate(nodes)}
    dsu = DsaDisjointSet(len(nodes))
    mst_edges = []
    for w, u, v in edges:
        iu, iv = node_to_idx[u], node_to_idx[v]
        if dsu.union(iu, iv):
            mst_edges.append([u, v, w])
    return mst_edges


def dsa_minimum_spanning_tree_weight(g: Any) -> float:
    mst = dsa_minimum_spanning_tree(g)
    return sum(float(e[2]) for e in mst)


# 12. Knapsack & Coin Change DP
def dsa_solve_knapsack_01(weights: Any, values: Any, capacity: Any) -> int:
    cap = int(capacity)
    dp = [0] * (cap + 1)
    for w, v in zip(weights, values):
        w_int = int(w)
        v_int = int(v)
        for c in range(cap, w_int - 1, -1):
            dp[c] = max(dp[c], dp[c - w_int] + v_int)
    return dp[cap]


def dsa_min_coins(coins: Any, amount: Any) -> int:
    amt = int(amount)
    dp = [float("inf")] * (amt + 1)
    dp[0] = 0
    for coin in coins:
        c = int(coin)
        for x in range(c, amt + 1):
            dp[x] = min(dp[x], dp[x - c] + 1)
    return int(dp[amt]) if dp[amt] != float("inf") else -1


def dsa_coin_change_ways(coins: Any, amount: Any) -> int:
    amt = int(amount)
    dp = [0] * (amt + 1)
    dp[0] = 1
    for coin in coins:
        c = int(coin)
        for x in range(c, amt + 1):
            dp[x] += dp[x - c]
    return dp[amt]


# 13. String Palindromes & KMP Pattern Matching
def dsa_kmp_search(text: Any, pattern: Any) -> List[int]:
    txt = str(text)
    pat = str(pattern)
    if not pat or not txt:
        return []
    pi = [0] * len(pat)
    j = 0
    for i in range(1, len(pat)):
        while j > 0 and pat[i] != pat[j]:
            j = pi[j - 1]
        if pat[i] == pat[j]:
            j += 1
            pi[i] = j

    matches = []
    j = 0
    for i in range(len(txt)):
        while j > 0 and txt[i] != pat[j]:
            j = pi[j - 1]
        if txt[i] == pat[j]:
            j += 1
        if j == len(pat):
            matches.append(i - len(pat) + 1)
            j = pi[j - 1]
    return matches


def dsa_longest_palindromic_substring(text: Any) -> str:
    s = str(text)
    if not s:
        return ""
    start, max_len = 0, 1

    def expand(l: int, r: int):
        nonlocal start, max_len
        while l >= 0 and r < len(s) and s[l] == s[r]:
            if r - l + 1 > max_len:
                start = l
                max_len = r - l + 1
            l -= 1
            r += 1

    for i in range(len(s)):
        expand(i, i)
        expand(i, i + 1)
    return s[start : start + max_len]


def dsa_is_palindrome(text: Any) -> bool:
    s = str(text)
    return s == s[::-1]
