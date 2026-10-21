"""Runtime execution engine for Testing & Algorithm Analysis (DSA)."""

import math
import random
import time
import tracemalloc
import hashlib
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
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
    fn_name: str, input_expr: Any, scope: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Level 2: Profiles peak and allocated memory for a single function execution."""
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
        scope = dict(target_env)
        if caller_frame.f_locals:
            scope.update(caller_frame.f_locals)
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
    if hasattr(g, "topological_sort") and callable(g.topological_sort):
        return g.topological_sort()
    try:
        from doomscript.research.graph import ResearchGraph, topological_sort as res_topo_sort
        if isinstance(g, ResearchGraph):
            return res_topo_sort(g)
    except Exception:
        pass
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

    def search(self, word: str) -> bool:
        return self.contains(word)

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


def dsa_trie_search(trie: Any, word: Any) -> bool:
    if isinstance(trie, DsaTrie):
        return trie.contains(str(word))
    return False


dsa_trie_create = dsa_create_trie
dsa_trie_contains = dsa_trie_search


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


# --- Advanced Trees & Sequence Algorithms ---

class DsaSegmentTree:
    """Segment Tree for efficient O(log n) range sum queries and point updates."""

    def __init__(self, arr: List[Any]):
        self.n = len(arr)
        self.tree = [0] * (4 * max(self.n, 1))
        self.arr = list(arr)
        if self.n > 0:
            self._build(1, 0, self.n - 1)

    def _build(self, node: int, start: int, end: int):
        if start == end:
            self.tree[node] = self.arr[start]
            return
        mid = (start + end) // 2
        self._build(2 * node, start, mid)
        self._build(2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def update(self, idx: int, val: Any):
        def _update(node: int, start: int, end: int):
            if start == end:
                self.arr[idx] = val
                self.tree[node] = val
                return
            mid = (start + end) // 2
            if start <= idx <= mid:
                _update(2 * node, start, mid)
            else:
                _update(2 * node + 1, mid + 1, end)
            self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]
        if 0 <= idx < self.n:
            _update(1, 0, self.n - 1)

    def query(self, l: int, r: int) -> Any:
        def _query(node: int, start: int, end: int, ql: int, qr: int) -> Any:
            if qr < start or end < ql:
                return 0
            if ql <= start and end <= qr:
                return self.tree[node]
            mid = (start + end) // 2
            return _query(2 * node, start, mid, ql, qr) + _query(2 * node + 1, mid + 1, end, ql, qr)
        if self.n == 0:
            return 0
        return _query(1, 0, self.n - 1, max(0, l), min(self.n - 1, r))


def dsa_create_segment_tree(arr: Any) -> DsaSegmentTree:
    return DsaSegmentTree(list(arr))


def dsa_segment_tree_query(st: Any, l: Any, r: Any) -> Any:
    if isinstance(st, DsaSegmentTree):
        return st.query(int(l), int(r))
    return 0


def dsa_segment_tree_update(st: Any, idx: Any, val: Any) -> Any:
    if isinstance(st, DsaSegmentTree):
        st.update(int(idx), val)
    return st


class DsaFenwickTree:
    """Binary Indexed Tree (Fenwick Tree) for O(log n) prefix sums and point updates."""

    def __init__(self, arr: List[Any]):
        self.n = len(arr)
        self.bit = [0] * (self.n + 1)
        for i, val in enumerate(arr):
            self.update(i, val)

    def update(self, idx: int, delta: Any):
        i = int(idx) + 1
        while i <= self.n:
            self.bit[i] += delta
            i += i & (-i)

    def prefix_sum(self, idx: int) -> Any:
        res = 0
        i = min(int(idx) + 1, self.n)
        while i > 0:
            res += self.bit[i]
            i -= i & (-i)
        return res


def dsa_create_fenwick_tree(arr: Any) -> DsaFenwickTree:
    return DsaFenwickTree(list(arr))


def dsa_fenwick_prefix_sum(bit: Any, idx: Any) -> Any:
    if isinstance(bit, DsaFenwickTree):
        return bit.prefix_sum(int(idx))
    return 0


def dsa_fenwick_update(bit: Any, idx: Any, delta: Any) -> Any:
    if isinstance(bit, DsaFenwickTree):
        bit.update(int(idx), delta)
    return bit


def dsa_reservoir_sample(stream: Any, k: Any, seed: int = 42) -> List[Any]:
    """Uniform random sampling of k elements from an unknown/infinite stream."""
    import random
    rng = random.Random(seed)
    k_int = int(k)
    reservoir = []
    for i, item in enumerate(stream):
        if i < k_int:
            reservoir.append(item)
        else:
            j = rng.randint(0, i)
            if j < k_int:
                reservoir[j] = item
    return reservoir


def dsa_lcs(a: Any, b: Any) -> str:
    """Compute the Longest Common Subsequence of two sequences in O(m * n) DP time."""
    s1, s2 = str(a), str(b)
    m, n = len(s1), len(s2)
    dp = [["" for _ in range(n + 1)] for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + s1[i - 1]
            else:
                dp[i][j] = dp[i - 1][j] if len(dp[i - 1][j]) >= len(dp[i][j - 1]) else dp[i][j - 1]
    return dp[m][n]


# --- Math & Statistics Operations ---

def dsa_correlation(x: Any, y: Any) -> float:
    """Pearson correlation coefficient between two numeric collections."""
    import math
    if not x or not y or len(x) != len(y) or len(x) < 2:
        return 0.0
    mx = sum(x) / len(x)
    my = sum(y) / len(y)
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    den = math.sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))
    return round(num / den, 4) if den != 0 else 0.0


def dsa_linear_regression(y: Any, x: Any) -> Dict[str, float]:
    """Ordinary Least Squares simple linear regression returning slope, intercept, and R^2."""
    n = len(x)
    if n < 2 or len(y) != n:
        return {"slope": 0.0, "intercept": 0.0, "r2": 0.0}
    mx, my = sum(x) / n, sum(y) / n
    cov_xy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    var_x = sum((a - mx) ** 2 for a in x)
    slope = cov_xy / var_x if var_x != 0 else 0.0
    intercept = my - slope * mx
    preds = [slope * a + intercept for a in x]
    ss_res = sum((b - p) ** 2 for b, p in zip(y, preds))
    ss_tot = sum((b - my) ** 2 for b in y)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 1.0
    return {"slope": round(slope, 4), "intercept": round(intercept, 4), "r2": round(r2, 4)}


def dsa_moving_median(arr: Any, w: Any) -> List[float]:
    """Rolling / moving median filter over a numeric sequence."""
    win = int(w)
    if not arr or win <= 0:
        return []
    res = []
    for i in range(len(arr) - win + 1):
        chunk = sorted(arr[i : i + win])
        mid = win // 2
        med = float(chunk[mid] if win % 2 != 0 else (chunk[mid - 1] + chunk[mid]) / 2.0)
        res.append(med)
    return res


def dsa_percentile(arr: Any, p: Any) -> float:
    """Calculate the p-th percentile of a numeric collection with linear interpolation."""
    import math
    if not arr:
        return 0.0
    s_arr = sorted(arr)
    k = (len(s_arr) - 1) * (float(p) / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(s_arr[int(k)])
    return round(float(s_arr[int(f)] * (c - k) + s_arr[int(c)] * (k - f)), 4)


def dsa_z_score_normalize(arr: Any) -> List[float]:
    """Standardize data to zero mean and unit variance."""
    import math
    if not arr:
        return []
    m = sum(arr) / len(arr)
    std = math.sqrt(sum((x - m) ** 2 for x in arr) / len(arr))
    if std == 0:
        return [0.0] * len(arr)
    return [round((x - m) / std, 4) for x in arr]


def dsa_min_max_scale(arr: Any) -> List[float]:
    """Rescale features to a [0, 1] range."""
    if not arr:
        return []
    mn, mx = min(arr), max(arr)
    if mx == mn:
        return [0.0] * len(arr)
    return [round((x - mn) / (mx - mn), 4) for x in arr]


def dsa_empirical_cdf(arr: Any, x: Any) -> float:
    """Evaluate empirical cumulative distribution function P(X <= x)."""
    if not arr:
        return 0.0
    count_le = sum(1 for v in arr if v <= float(x))
    return round(count_le / len(arr), 4)


# --- 350 Expansion Batch 1: Advanced DSA & String Algorithms ---


class DsaDSU:
    """Disjoint Set Union (Union-Find) with path compression and rank optimization."""
    def __init__(self, size: int):
        self.parent = list(range(int(size)))
        self.rank = [0] * int(size)

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(int(x)), self.find(int(y))
        if root_x == root_y:
            return False
        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x
        self.parent[root_y] = root_x
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        return True


def dsa_dsu_create(size: Any) -> DsaDSU:
    return DsaDSU(int(size))


def dsa_dsu_find(dsu: DsaDSU, x: Any) -> int:
    return dsu.find(int(x))


def dsa_dsu_union(dsu: DsaDSU, x: Any, y: Any) -> bool:
    return dsu.union(int(x), int(y))


from collections import OrderedDict

class DsaLRUCache:
    """O(1) Least Recently Used cache implementation."""
    def __init__(self, capacity: int = 128):
        self.capacity = max(1, int(capacity))
        self.cache: OrderedDict = OrderedDict()

    def get(self, key: Any, default: Any = None) -> Any:
        if key not in self.cache:
            return default
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)


def dsa_lru_create(capacity: Any = 128) -> DsaLRUCache:
    return DsaLRUCache(int(capacity))


def dsa_lru_get(cache: DsaLRUCache, key: Any, default: Any = None) -> Any:
    return cache.get(key, default)


def dsa_lru_put(cache: DsaLRUCache, key: Any, value: Any) -> DsaLRUCache:
    cache.put(key, value)
    return cache


def dsa_binary_search_left(arr: Any, target: Any) -> int:
    """Locate insertion point for target in arr to maintain sorted order (leftmost)."""
    import bisect
    return bisect.bisect_left(list(arr), target)


def dsa_binary_search_right(arr: Any, target: Any) -> int:
    """Locate insertion point for target in arr to maintain sorted order (rightmost)."""
    import bisect
    return bisect.bisect_right(list(arr), target)


def dsa_quickselect(arr: Any, k: Any) -> Any:
    """Select the k-th smallest element from an array in O(n) average time (0-indexed)."""
    k_idx = int(k)
    nums = list(arr)
    if not (0 <= k_idx < len(nums)):
        raise IndexError("k is out of bounds for quickselect")
    def _select(left, right, target_k):
        if left == right:
            return nums[left]
        pivot = nums[right]
        p_idx = left
        for i in range(left, right):
            if nums[i] <= pivot:
                nums[p_idx], nums[i] = nums[i], nums[p_idx]
                p_idx += 1
        nums[p_idx], nums[right] = nums[right], nums[p_idx]
        if p_idx == target_k:
            return nums[p_idx]
        elif p_idx < target_k:
            return _select(p_idx + 1, right, target_k)
        else:
            return _select(left, p_idx - 1, target_k)
    return _select(0, len(nums) - 1, k_idx)


def dsa_kadane_2d(matrix: Any) -> Dict[str, Any]:
    """Find maximum sum rectangular submatrix in 2D grid."""
    mat = [list(row) for row in matrix]
    if not mat or not mat[0]:
        return {"max_sum": 0, "bounds": {"top": 0, "bottom": 0, "left": 0, "right": 0}}
    R, C = len(mat), len(mat[0])
    max_sum = float("-inf")
    best_coords = {"top": 0, "bottom": 0, "left": 0, "right": 0}
    for left in range(C):
        temp = [0] * R
        for right in range(left, C):
            for i in range(R):
                temp[i] += mat[i][right]
            curr_sum = 0
            start_row = 0
            for r in range(R):
                curr_sum += temp[r]
                if curr_sum > max_sum:
                    max_sum = curr_sum
                    best_coords = {"top": start_row, "bottom": r, "left": left, "right": right}
                if curr_sum < 0:
                    curr_sum = 0
                    start_row = r + 1
    return {"max_sum": max_sum, "bounds": best_coords}


def dsa_count_inversions(arr: Any) -> int:
    """Count number of inversions in a sequence using divide-and-conquer."""
    nums = list(arr)
    def _merge_sort(a):
        if len(a) <= 1:
            return a, 0
        mid = len(a) // 2
        left, left_inv = _merge_sort(a[:mid])
        right, right_inv = _merge_sort(a[mid:])
        merged = []
        inv = left_inv + right_inv
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                inv += len(left) - i
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged, inv
    _, total_inv = _merge_sort(nums)
    return total_inv


def dsa_next_permutation(arr: Any) -> List[Any]:
    """Rearrange list into lexicographically next greater permutation."""
    nums = list(arr)
    i = len(nums) - 2
    while i >= 0 and nums[i] >= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] <= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])
    return nums


def dsa_prev_permutation(arr: Any) -> List[Any]:
    """Rearrange list into lexicographically previous smaller permutation."""
    nums = list(arr)
    i = len(nums) - 2
    while i >= 0 and nums[i] <= nums[i + 1]:
        i -= 1
    if i >= 0:
        j = len(nums) - 1
        while nums[j] >= nums[i]:
            j -= 1
        nums[i], nums[j] = nums[j], nums[i]
    nums[i + 1:] = reversed(nums[i + 1:])
    return nums


def dsa_rabin_karp_search(text: Any, pattern: Any) -> List[int]:
    """Search for pattern in text using Rabin-Karp polynomial rolling hash."""
    txt, pat = str(text), str(pattern)
    n, m = len(txt), len(pat)
    if m == 0 or n < m:
        return []
    base = 256
    mod = 1000000007
    p_hash = 0
    t_hash = 0
    h = pow(base, m - 1, mod)
    for i in range(m):
        p_hash = (base * p_hash + ord(pat[i])) % mod
        t_hash = (base * t_hash + ord(txt[i])) % mod
    matches = []
    for i in range(n - m + 1):
        if p_hash == t_hash:
            if txt[i:i + m] == pat:
                matches.append(i)
        if i < n - m:
            t_hash = (base * (t_hash - ord(txt[i]) * h) + ord(txt[i + m])) % mod
            t_hash = (t_hash + mod) % mod
    return matches


def dsa_manacher(text: Any) -> str:
    """Find longest palindromic substring in O(n) time using Manacher's algorithm."""
    s = str(text)
    if not s:
        return ""
    t = "^#" + "#".join(s) + "#$"
    p = [0] * len(t)
    c = r = 0
    for i in range(1, len(t) - 1):
        i_mirror = 2 * c - i
        if r > i:
            p[i] = min(r - i, p[i_mirror])
        while t[i + 1 + p[i]] == t[i - 1 - p[i]]:
            p[i] += 1
        if i + p[i] > r:
            c = i
            r = i + p[i]
    max_len, center_idx = max((n, i) for i, n in enumerate(p))
    start = (center_idx - max_len) // 2
    return s[start:start + max_len]


def dsa_tarjan_bridges(adj_or_edges: Any, num_nodes: Optional[int] = None) -> List[Tuple[int, int]]:
    """Find all critical bridge edges in an undirected graph."""
    adj: Dict[int, List[int]] = {}
    if isinstance(adj_or_edges, dict):
        adj = {int(u): [int(v) for v in vs] for u, vs in adj_or_edges.items()}
    elif isinstance(adj_or_edges, (list, tuple)):
        for edge in adj_or_edges:
            u, v = int(edge[0]), int(edge[1])
            adj.setdefault(u, []).append(v)
            adj.setdefault(v, []).append(u)
    nodes = list(adj.keys())
    tin: Dict[int, int] = {}
    low: Dict[int, int] = {}
    timer = 0
    bridges: List[Tuple[int, int]] = []
    visited: Set[int] = set()

    def _dfs(v, p=-1):
        nonlocal timer
        visited.add(v)
        timer += 1
        tin[v] = low[v] = timer
        for to in adj.get(v, []):
            if to == p:
                continue
            if to in visited:
                low[v] = min(low[v], tin[to])
            else:
                _dfs(to, v)
                low[v] = min(low[v], low[to])
                if low[to] > tin[v]:
                    bridges.append((min(v, to), max(v, to)))

    for n in nodes:
        if n not in visited:
            _dfs(n)
    return sorted(bridges)


# ===========================================================================
# 1. Self-Balancing AVL Tree
# ===========================================================================

class AVLNode:
    """Node in an AVL self-balancing binary search tree."""

    def __init__(self, key: Any, val: Any = None):
        self.key = key
        self.val = val if val is not None else key
        self.height: int = 1
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None


class AVLTree:
    """AVL Tree maintaining strict logarithmic balance via rotations."""

    def __init__(self):
        self.root: Optional[AVLNode] = None
        self.size: int = 0

    def _height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._height(node.left), self._height(node.right))

    def _balance_factor(self, node: Optional[AVLNode]) -> int:
        return (self._height(node.left) - self._height(node.right)) if node else 0

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        assert x is not None
        T2 = x.right
        x.right = y
        y.left = T2
        self._update_height(y)
        self._update_height(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        assert y is not None
        T2 = y.left
        y.left = x
        x.right = T2
        self._update_height(x)
        self._update_height(y)
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        self._update_height(node)
        bf = self._balance_factor(node)
        if bf > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if bf < -1:
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key: Any, val: Any = None) -> None:
        def _ins(curr: Optional[AVLNode], k: Any, v: Any) -> AVLNode:
            if not curr:
                self.size += 1
                return AVLNode(k, v)
            if k < curr.key:
                curr.left = _ins(curr.left, k, v)
            elif k > curr.key:
                curr.right = _ins(curr.right, k, v)
            else:
                curr.val = v
                return curr
            return self._rebalance(curr)

        self.root = _ins(self.root, key, val)

    def _min_value_node(self, node: AVLNode) -> AVLNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def delete(self, key: Any) -> None:
        def _del(curr: Optional[AVLNode], k: Any) -> Optional[AVLNode]:
            if not curr:
                return None
            if k < curr.key:
                curr.left = _del(curr.left, k)
            elif k > curr.key:
                curr.right = _del(curr.right, k)
            else:
                self.size -= 1
                if not curr.left:
                    return curr.right
                elif not curr.right:
                    return curr.left
                temp = self._min_value_node(curr.right)
                curr.key = temp.key
                curr.val = temp.val
                self.size += 1
                curr.right = _del(curr.right, temp.key)
            return self._rebalance(curr)

        self.root = _del(self.root, key)

    def contains(self, key: Any) -> bool:
        curr = self.root
        while curr:
            if key == curr.key:
                return True
            curr = curr.left if key < curr.key else curr.right
        return False

    def inorder(self) -> List[Any]:
        res = []
        def _in(node: Optional[AVLNode]):
            if node:
                _in(node.left)
                res.append(node.key)
                _in(node.right)
        _in(self.root)
        return res

    def height(self) -> int:
        return self._height(self.root)


def dsa_avl_create(items: Optional[List[Any]] = None) -> AVLTree:
    tree = AVLTree()
    if items:
        for x in items:
            tree.insert(x)
    return tree

def dsa_avl_insert(tree: AVLTree, key: Any, val: Any = None) -> AVLTree:
    tree.insert(key, val)
    return tree

def dsa_avl_delete(tree: AVLTree, key: Any) -> AVLTree:
    tree.delete(key)
    return tree

def dsa_avl_contains(tree: AVLTree, key: Any) -> bool:
    return tree.contains(key)

def dsa_avl_inorder(tree: AVLTree) -> List[Any]:
    return tree.inorder()

def dsa_avl_height(tree: AVLTree) -> int:
    return tree.height()


# ===========================================================================
# 2. Suffix Automaton (Linear Time Substring Machine)
# ===========================================================================

class SAMState:
    """State in a Suffix Automaton."""

    def __init__(self, length: int = 0, link: int = -1):
        self.len = length
        self.link = link
        self.next: Dict[str, int] = {}


class SuffixAutomaton:
    """Linear time O(N) Directed Acyclic Word Graph representing all substrings."""

    def __init__(self, s: str = ""):
        self.states: List[SAMState] = [SAMState(0, -1)]
        self.last: int = 0
        if s:
            for ch in str(s):
                self.extend(ch)

    def extend(self, ch: str) -> None:
        cur = len(self.states)
        self.states.append(SAMState(self.states[self.last].len + 1))
        p = self.last
        while p != -1 and ch not in self.states[p].next:
            self.states[p].next[ch] = cur
            p = self.states[p].link

        if p == -1:
            self.states[cur].link = 0
        else:
            q = self.states[p].next[ch]
            if self.states[p].len + 1 == self.states[q].len:
                self.states[cur].link = q
            else:
                clone = len(self.states)
                clone_state = SAMState(self.states[p].len + 1, self.states[q].link)
                clone_state.next = dict(self.states[q].next)
                self.states.append(clone_state)
                while p != -1 and self.states[p].next.get(ch) == q:
                    self.states[p].next[ch] = clone
                    p = self.states[p].link
                self.states[q].link = clone
                self.states[cur].link = clone
        self.last = cur

    def contains_substring(self, sub: str) -> bool:
        curr = 0
        for ch in str(sub):
            if ch not in self.states[curr].next:
                return False
            curr = self.states[curr].next[ch]
        return True

    def count_distinct_substrings(self) -> int:
        return sum(self.states[i].len - self.states[self.states[i].link].len for i in range(1, len(self.states)))

    def longest_common_substring(self, s2: str) -> str:
        curr = 0
        cur_len = 0
        best_len = 0
        best_end = 0
        for i, ch in enumerate(str(s2)):
            while curr > 0 and ch not in self.states[curr].next:
                curr = self.states[curr].link
                cur_len = self.states[curr].len
            if ch in self.states[curr].next:
                curr = self.states[curr].next[ch]
                cur_len += 1
            if cur_len > best_len:
                best_len = cur_len
                best_end = i + 1
        return s2[best_end - best_len:best_end]


def dsa_suffix_automaton_create(s: str) -> SuffixAutomaton:
    return SuffixAutomaton(s)

def dsa_sam_contains_substring(sam: SuffixAutomaton, sub: str) -> bool:
    return sam.contains_substring(sub)

def dsa_sam_distinct_substrings(sam: SuffixAutomaton) -> int:
    return sam.count_distinct_substrings()

def dsa_sam_longest_common_substring(sam: SuffixAutomaton, s2: str) -> str:
    return sam.longest_common_substring(s2)


# ===========================================================================
# 3. Aho-Corasick Multi-Pattern Search Automaton
# ===========================================================================

class AhoCorasickNode:
    def __init__(self):
        self.children: Dict[str, AhoCorasickNode] = {}
        self.fail: Optional["AhoCorasickNode"] = None
        self.output: List[str] = []


class AhoCorasick:
    """Multi-pattern dictionary matching automaton with fail links."""

    def __init__(self, patterns: Optional[List[str]] = None):
        self.root = AhoCorasickNode()
        if patterns:
            for p in patterns:
                self.add_pattern(p)
            self.build()

    def add_pattern(self, pattern: str) -> None:
        p = str(pattern)
        if not p:
            return
        curr = self.root
        for ch in p:
            if ch not in curr.children:
                curr.children[ch] = AhoCorasickNode()
            curr = curr.children[ch]
        curr.output.append(p)

    def build(self) -> None:
        from collections import deque
        queue = deque()
        for ch, child in self.root.children.items():
            child.fail = self.root
            queue.append(child)

        while queue:
            curr = queue.popleft()
            for ch, child in curr.children.items():
                f = curr.fail
                while f and ch not in f.children:
                    f = f.fail
                child.fail = f.children[ch] if f and ch in f.children else self.root
                child.output.extend(child.fail.output)
                queue.append(child)

    def search(self, text: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        curr = self.root
        for idx, ch in enumerate(str(text)):
            while curr and ch not in curr.children:
                curr = curr.fail
            if not curr:
                curr = self.root
                continue
            curr = curr.children[ch]
            for pat in curr.output:
                results.append({
                    "pattern": pat,
                    "word": pat,
                    "start": idx - len(pat) + 1,
                    "end": idx + 1
                })
        return results


def dsa_aho_corasick_create(patterns: List[str]) -> AhoCorasick:
    return AhoCorasick(patterns)

def dsa_aho_corasick_search(ac: AhoCorasick, text: str) -> List[Dict[str, Any]]:
    return ac.search(text)


# ===========================================================================
# 4. Cartesian Treap (Randomized BST + Max-Heap)
# ===========================================================================

class TreapNode:
    def __init__(self, key: Any, val: Any = None, priority: Optional[float] = None):
        self.key = key
        self.val = val if val is not None else key
        self.priority = random.random() if priority is None else float(priority)
        self.left: Optional["TreapNode"] = None
        self.right: Optional["TreapNode"] = None
        self.size: int = 1

    def update_size(self):
        s = 1
        if self.left:
            s += self.left.size
        if self.right:
            s += self.right.size
        self.size = s


class Treap:
    """Randomized self-balancing Treap combining BST keys with Heap priorities."""

    def __init__(self):
        self.root: Optional[TreapNode] = None

    def _split(self, node: Optional[TreapNode], key: Any) -> Tuple[Optional[TreapNode], Optional[TreapNode]]:
        if not node:
            return None, None
        if node.key <= key:
            left, right = self._split(node.right, key)
            node.right = left
            node.update_size()
            return node, right
        else:
            left, right = self._split(node.left, key)
            node.left = right
            node.update_size()
            return left, node

    def _merge(self, left: Optional[TreapNode], right: Optional[TreapNode]) -> Optional[TreapNode]:
        if not left or not right:
            return left or right
        if left.priority > right.priority:
            left.right = self._merge(left.right, right)
            left.update_size()
            return left
        else:
            right.left = self._merge(left, right.left)
            right.update_size()
            return right

    def insert(self, key: Any, val: Any = None) -> None:
        left, right = self._split(self.root, key)
        new_node = TreapNode(key, val)
        self.root = self._merge(self._merge(left, new_node), right)

    def delete(self, key: Any) -> None:
        left, temp = self._split(self.root, key)
        # split temp by key - epsilon (exact key removal)
        l2, right = self._split(left, key - 1e-9 if isinstance(key, (int, float)) else key)
        self.root = self._merge(l2, temp)

    def contains(self, key: Any) -> bool:
        curr = self.root
        while curr:
            if curr.key == key:
                return True
            curr = curr.left if key < curr.key else curr.right
        return False

    def to_list(self) -> List[Any]:
        res = []
        def _in(node: Optional[TreapNode]):
            if node:
                _in(node.left)
                res.append(node.key)
                _in(node.right)
        _in(self.root)
        return res


def dsa_treap_create(items: Optional[List[Any]] = None) -> Treap:
    t = Treap()
    if items:
        for x in items:
            t.insert(x)
    return t

def dsa_treap_insert(t: Treap, key: Any) -> Treap:
    t.insert(key)
    return t

def dsa_treap_contains(t: Treap, key: Any) -> bool:
    return t.contains(key)

def dsa_treap_to_list(t: Treap) -> List[Any]:
    return t.to_list()


# ===========================================================================
# 5. Dinic's Algorithm (Fast Network Flow & Min Cut)
# ===========================================================================

class DinicFlowEdge:
    def __init__(self, u: int, v: int, cap: float, flow: float = 0.0):
        self.u = u
        self.v = v
        self.cap = cap
        self.flow = flow


class DinicMaxFlow:
    """Dinic's blocking flow algorithm with level graphs and push-relabel pointers."""

    def __init__(self, n: int):
        self.n = max(1, int(n))
        self.edges: List[DinicFlowEdge] = []
        self.adj: List[List[int]] = [[] for _ in range(self.n)]
        self.level: List[int] = [-1] * self.n
        self.ptr: List[int] = [0] * self.n

    def add_edge(self, u: int, v: int, cap: float) -> None:
        u_idx, v_idx = int(u), int(v)
        if 0 <= u_idx < self.n and 0 <= v_idx < self.n:
            e1 = len(self.edges)
            self.edges.append(DinicFlowEdge(u_idx, v_idx, float(cap)))
            self.adj[u_idx].append(e1)
            e2 = len(self.edges)
            self.edges.append(DinicFlowEdge(v_idx, u_idx, 0.0))
            self.adj[v_idx].append(e2)

    def _bfs(self, s: int, t: int) -> bool:
        from collections import deque
        self.level = [-1] * self.n
        self.level[s] = 0
        q = deque([s])
        while q:
            v = q.popleft()
            for edge_id in self.adj[v]:
                e = self.edges[edge_id]
                if e.cap - e.flow > 1e-9 and self.level[e.v] == -1:
                    self.level[e.v] = self.level[v] + 1
                    q.append(e.v)
        return self.level[t] != -1

    def _dfs(self, v: int, t: int, pushed: float) -> float:
        if pushed <= 1e-9 or v == t:
            return pushed
        for cid in range(self.ptr[v], len(self.adj[v])):
            self.ptr[v] = cid
            edge_id = self.adj[v][cid]
            e = self.edges[edge_id]
            tr = e.v
            if self.level[v] + 1 != self.level[tr] or e.cap - e.flow <= 1e-9:
                continue
            tr_pushed = self._dfs(tr, t, min(pushed, e.cap - e.flow))
            if tr_pushed > 1e-9:
                e.flow += tr_pushed
                self.edges[edge_id ^ 1].flow -= tr_pushed
                return tr_pushed
        return 0.0

    def compute_max_flow(self, s: int, t: int) -> float:
        flow = 0.0
        while self._bfs(int(s), int(t)):
            self.ptr = [0] * self.n
            while True:
                pushed = self._dfs(int(s), int(t), float("inf"))
                if pushed <= 1e-9:
                    break
                flow += pushed
        return round(flow, 4)

    max_flow = compute_max_flow


def dsa_dinic_max_flow(n: int, edges: List[Tuple[int, int, float]], source: int, sink: int) -> float:
    dinic = DinicMaxFlow(n)
    for e in edges:
        dinic.add_edge(e[0], e[1], e[2])
    return dinic.compute_max_flow(source, sink)


# ===========================================================================
# Advanced Balanced Search Structures: Red-Black Tree & Skip List
# ===========================================================================

class RBColor:
    RED = 0
    BLACK = 1


class RBNode:
    """Node in a self-balancing Red-Black binary search tree."""

    def __init__(self, key: Any, value: Any = None, color: int = RBColor.RED):
        self.key = key
        self.value = value if value is not None else key
        self.color = color
        self.left: Optional[RBNode] = None
        self.right: Optional[RBNode] = None
        self.parent: Optional[RBNode] = None

    def __repr__(self):
        c = "R" if self.color == RBColor.RED else "B"
        return f"RBNode({self.key}:{c})"


class RedBlackTree:
    """Self-Balancing Red-Black Binary Search Tree adhering to CLRS color invariants."""

    def __init__(self):
        # Sentinel NIL node
        self.NIL = RBNode(None, None, color=RBColor.BLACK)
        self.NIL.left = self.NIL
        self.NIL.right = self.NIL
        self.root = self.NIL
        self.size = 0

    def insert(self, key: Any, value: Any = None) -> None:
        """Inserts a key-value pair and restores Red-Black properties."""
        val = value if value is not None else key
        new_node = RBNode(key, val, color=RBColor.RED)
        new_node.left = self.NIL
        new_node.right = self.NIL

        parent = None
        curr = self.root
        while curr != self.NIL:
            parent = curr
            if key < curr.key:
                curr = curr.left
            elif key > curr.key:
                curr = curr.right
            else:
                curr.value = val
                return

        new_node.parent = parent
        if parent is None:
            self.root = new_node
        elif key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self.size += 1
        self._insert_fixup(new_node)

    def _insert_fixup(self, z: RBNode) -> None:
        while z.parent and z.parent.color == RBColor.RED:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right  # Uncle
                if y.color == RBColor.RED:
                    z.parent.color = RBColor.BLACK
                    y.color = RBColor.BLACK
                    z.parent.parent.color = RBColor.RED
                    z = z.parent.parent
                else:
                    if z == z.parent.right:
                        z = z.parent
                        self._left_rotate(z)
                    z.parent.color = RBColor.BLACK
                    z.parent.parent.color = RBColor.RED
                    self._right_rotate(z.parent.parent)
            else:
                y = z.parent.parent.left
                if y.color == RBColor.RED:
                    z.parent.color = RBColor.BLACK
                    y.color = RBColor.BLACK
                    z.parent.parent.color = RBColor.RED
                    z = z.parent.parent
                else:
                    if z == z.parent.left:
                        z = z.parent
                        self._right_rotate(z)
                    z.parent.color = RBColor.BLACK
                    z.parent.parent.color = RBColor.RED
                    self._left_rotate(z.parent.parent)
            if z == self.root:
                break
        self.root.color = RBColor.BLACK

    def _left_rotate(self, x: RBNode) -> None:
        y = x.right
        x.right = y.left
        if y.left != self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def _right_rotate(self, y: RBNode) -> None:
        x = y.left
        y.left = x.right
        if x.right != self.NIL:
            x.right.parent = y
        x.parent = y.parent
        if y.parent is None:
            self.root = x
        elif y == y.parent.right:
            y.parent.right = x
        else:
            y.parent.left = x
        x.right = y
        y.parent = x

    def search(self, key: Any) -> Optional[Any]:
        """Searches for key and returns associated value or None."""
        curr = self.root
        while curr != self.NIL:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def minimum(self, node: Optional[RBNode] = None) -> Optional[Any]:
        curr = node or self.root
        if curr == self.NIL:
            return None
        while curr.left != self.NIL:
            curr = curr.left
        return curr.key

    def maximum(self, node: Optional[RBNode] = None) -> Optional[Any]:
        curr = node or self.root
        if curr == self.NIL:
            return None
        while curr.right != self.NIL:
            curr = curr.right
        return curr.key

    def inorder(self) -> List[Any]:
        """Returns sorted list of keys."""
        res = []
        def _walk(node: RBNode):
            if node != self.NIL:
                _walk(node.left)
                res.append(node.key)
                _walk(node.right)
        _walk(self.root)
        return res

    def is_valid_rb(self) -> bool:
        """Verifies Red-Black tree properties."""
        if self.root == self.NIL:
            return True
        if self.root.color != RBColor.BLACK:
            return False

        def check(node: RBNode) -> Tuple[bool, int]:
            if node == self.NIL:
                return True, 1
            if node.color == RBColor.RED:
                if node.left.color == RBColor.RED or node.right.color == RBColor.RED:
                    return False, 0
            ok_l, bh_l = check(node.left)
            ok_r, bh_r = check(node.right)
            if not ok_l or not ok_r or bh_l != bh_r:
                return False, 0
            add_black = 1 if node.color == RBColor.BLACK else 0
            return True, bh_l + add_black

        valid, _ = check(self.root)
        return valid


class SkipListNode:
    """Node in a SkipList holding multi-level forward pointers."""

    def __init__(self, key: Any, value: Any, level: int):
        self.key = key
        self.value = value
        self.forward: List[Optional[SkipListNode]] = [None] * level


class SkipList:
    """Probabilistic ordered dictionary with expected O(log n) search, insert, and delete."""

    def __init__(self, max_level: int = 16, p: float = 0.5):
        self.max_level = max_level
        self.p = p
        self.header = SkipListNode(None, None, max_level)
        self.level = 1
        self.size = 0

    def _random_level(self) -> int:
        lvl = 1
        while random.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def insert(self, key: Any, value: Any = None) -> None:
        """Inserts or updates key-value pair."""
        val = value if value is not None else key
        update = [None] * self.max_level
        curr = self.header

        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and curr.forward[i].key < key:
                curr = curr.forward[i]
            update[i] = curr

        curr = curr.forward[0]
        if curr and curr.key == key:
            curr.value = val
            return

        new_lvl = self._random_level()
        if new_lvl > self.level:
            for i in range(self.level, new_lvl):
                update[i] = self.header
            self.level = new_lvl

        new_node = SkipListNode(key, val, new_lvl)
        for i in range(new_lvl):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

        self.size += 1

    def search(self, key: Any) -> Optional[Any]:
        """Searches for key and returns associated value or None."""
        curr = self.header
        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and curr.forward[i].key < key:
                curr = curr.forward[i]
        curr = curr.forward[0]
        if curr and curr.key == key:
            return curr.value
        return None

    def delete(self, key: Any) -> bool:
        """Deletes key from SkipList. Returns True if found and removed."""
        update = [None] * self.max_level
        curr = self.header

        for i in range(self.level - 1, -1, -1):
            while curr.forward[i] and curr.forward[i].key < key:
                curr = curr.forward[i]
            update[i] = curr

        curr = curr.forward[0]
        if not curr or curr.key != key:
            return False

        for i in range(self.level):
            if update[i].forward[i] != curr:
                break
            update[i].forward[i] = curr.forward[i]

        while self.level > 1 and self.header.forward[self.level - 1] is None:
            self.level -= 1

        self.size -= 1
        return True

    def to_list(self) -> List[Any]:
        """Returns sorted list of keys."""
        res = []
        curr = self.header.forward[0]
        while curr:
            res.append(curr.key)
            curr = curr.forward[0]
        return res


def dsa_red_black_tree() -> RedBlackTree:
    """Creates a new self-balancing Red-Black Tree."""
    return RedBlackTree()


def dsa_skip_list(max_level: int = 16) -> SkipList:
    """Creates a new Skip List."""
    return SkipList(max_level)


class BTreeNode:
    """A node in a B-Tree of minimum degree t."""

    def __init__(self, t: int, leaf: bool = True):
        self.t = t
        self.leaf = leaf
        self.keys: List[Any] = []
        self.values: List[Any] = []
        self.children: List["BTreeNode"] = []

    def find_key(self, k: Any) -> int:
        idx = 0
        while idx < len(self.keys) and self.keys[idx] < k:
            idx += 1
        return idx


class BTree:
    """Order-t self-balancing B-Tree for indexing and storage."""

    def __init__(self, t: int = 2):
        if t < 2:
            raise ValueError("B-Tree minimum degree t must be >= 2")
        self.t = t
        self.root = BTreeNode(t, leaf=True)

    def search(self, k: Any) -> Optional[Any]:
        return self._search(self.root, k)

    def _search(self, node: BTreeNode, k: Any) -> Optional[Any]:
        idx = node.find_key(k)
        if idx < len(node.keys) and node.keys[idx] == k:
            return node.values[idx]
        if node.leaf:
            return None
        return self._search(node.children[idx], k)

    def insert(self, k: Any, v: Any = None) -> None:
        root = self.root
        if len(root.keys) == (2 * self.t - 1):
            s = BTreeNode(self.t, leaf=False)
            self.root = s
            s.children.append(root)
            self._split_child(s, 0, root)
            self._insert_non_full(s, k, v)
        else:
            self._insert_non_full(root, k, v)

    def _insert_non_full(self, node: BTreeNode, k: Any, v: Any) -> None:
        i = len(node.keys) - 1
        if node.leaf:
            while i >= 0 and k < node.keys[i]:
                i -= 1
            if i >= 0 and node.keys[i] == k:
                node.values[i] = v
                return
            node.keys.insert(i + 1, k)
            node.values.insert(i + 1, v)
        else:
            while i >= 0 and k < node.keys[i]:
                i -= 1
            if i >= 0 and node.keys[i] == k:
                node.values[i] = v
                return
            i += 1
            if len(node.children[i].keys) == (2 * self.t - 1):
                self._split_child(node, i, node.children[i])
                if k > node.keys[i]:
                    i += 1
                elif k == node.keys[i]:
                    node.values[i] = v
                    return
            self._insert_non_full(node.children[i], k, v)

    def _split_child(self, parent: BTreeNode, i: int, child: BTreeNode) -> None:
        t = self.t
        z = BTreeNode(t, leaf=child.leaf)
        parent.children.insert(i + 1, z)
        parent.keys.insert(i, child.keys[t - 1])
        parent.values.insert(i, child.values[t - 1])

        z.keys = child.keys[t:]
        z.values = child.values[t:]
        child.keys = child.keys[: t - 1]
        child.values = child.values[: t - 1]

        if not child.leaf:
            z.children = child.children[t:]
            child.children = child.children[:t]

    def inorder(self) -> List[Any]:
        res = []
        def _inorder(node: BTreeNode):
            for i in range(len(node.keys)):
                if not node.leaf:
                    _inorder(node.children[i])
                res.append(node.keys[i])
            if not node.leaf:
                _inorder(node.children[len(node.keys)])
        _inorder(self.root)
        return res


class TrieNode:
    """A node in a Prefix Trie."""

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        self.value: Any = None


class PrefixTrie:
    """Trie with prefix auto-completion and wildcard search ('?')."""

    def __init__(self):
        self.root = TrieNode()
        self.size = 0

    def insert(self, word: str, value: Any = True) -> None:
        curr = self.root
        for ch in word:
            if ch not in curr.children:
                curr.children[ch] = TrieNode()
            curr = curr.children[ch]
        if not curr.is_end:
            self.size += 1
        curr.is_end = True
        curr.value = value

    def search(self, word: str) -> Optional[Any]:
        curr = self.root
        for ch in word:
            if ch not in curr.children:
                return None
            curr = curr.children[ch]
        return curr.value if curr.is_end else None

    def starts_with(self, prefix: str) -> bool:
        curr = self.root
        for ch in prefix:
            if ch not in curr.children:
                return False
            curr = curr.children[ch]
        return True

    def find_words_with_prefix(self, prefix: str) -> List[str]:
        curr = self.root
        for ch in prefix:
            if ch not in curr.children:
                return []
            curr = curr.children[ch]
        results = []
        def _collect(node: TrieNode, path: List[str]):
            if node.is_end:
                results.append("".join(path))
            for char, nxt in sorted(node.children.items()):
                _collect(nxt, path + [char])
        _collect(curr, list(prefix))
        return results

    def wildcard_search(self, pattern: str) -> List[str]:
        results = []
        def _dfs(node: TrieNode, idx: int, path: List[str]):
            if idx == len(pattern):
                if node.is_end:
                    results.append("".join(path))
                return
            ch = pattern[idx]
            if ch == "?":
                for char, nxt in sorted(node.children.items()):
                    _dfs(nxt, idx + 1, path + [char])
            elif ch in node.children:
                _dfs(node.children[ch], idx + 1, path + [ch])
        _dfs(self.root, 0, [])
        return results


def dsa_btree(t: int = 2) -> BTree:
    """Creates a new B-Tree with minimum degree t."""
    return BTree(t=t)


def dsa_prefix_trie() -> PrefixTrie:
    """Creates a new Prefix Trie."""
    return PrefixTrie()


# =========================================================================
# Cluster A Deepened DSA Algorithms: Fibonacci Heap, DSU, Fenwick, Bloom
# =========================================================================

class FibonacciHeapNode:
    """A node in a Fibonacci Heap."""

    def __init__(self, key: Any, value: Any = None):
        self.key = key
        self.value = value
        self.degree = 0
        self.mark = False
        self.parent: Optional["FibonacciHeapNode"] = None
        self.child: Optional["FibonacciHeapNode"] = None
        self.left: "FibonacciHeapNode" = self
        self.right: "FibonacciHeapNode" = self


class FibonacciHeap:
    """Zero-dependency Fibonacci Heap with amortized O(1) insert/decrease-key and O(log n) extract-min."""

    def __init__(self):
        self.min_node: Optional[FibonacciHeapNode] = None
        self.total_nodes = 0

    def __len__(self) -> int:
        return self.total_nodes

    def is_empty(self) -> bool:
        return self.min_node is None

    def find_min(self) -> Optional[FibonacciHeapNode]:
        return self.min_node

    def insert(self, key: Any, value: Any = None) -> FibonacciHeapNode:
        node = FibonacciHeapNode(key, value)
        if self.min_node is None:
            self.min_node = node
        else:
            self._link_root(node)
            if node.key < self.min_node.key:
                self.min_node = node
        self.total_nodes += 1
        return node

    def minimum(self) -> Optional[Tuple[Any, Any]]:
        if self.min_node is None:
            return None
        return (self.min_node.key, self.min_node.value)

    def extract_min(self) -> Optional[Any]:
        z = self.min_node
        if z is None:
            return None

        # Add all children of z to the root list
        if z.child is not None:
            children = self._iterate_ring(z.child)
            for child in children:
                self._link_root(child)
                child.parent = None

        # Remove z from root list
        if z.right == z:
            self.min_node = None
        else:
            z.left.right = z.right
            z.right.left = z.left
            self.min_node = z.right
            self._consolidate()

        self.total_nodes -= 1

        class HeapMinResult(tuple):
            @property
            def key(self):
                return self[0]
            @property
            def value(self):
                return self[1]

        return HeapMinResult((z.key, z.value))

    def decrease_key(self, node: FibonacciHeapNode, new_key: Any) -> None:
        if new_key > node.key:
            raise ValueError(f"Cannot increase key in decrease_key: {new_key} > {node.key}")
        node.key = new_key
        p = node.parent
        if p is not None and node.key < p.key:
            self._cut(node, p)
            self._cascading_cut(p)
        if self.min_node is not None and node.key < self.min_node.key:
            self.min_node = node

    def union(self, other: "FibonacciHeap") -> "FibonacciHeap":
        if other.min_node is not None:
            if self.min_node is None:
                self.min_node = other.min_node
            else:
                self_right = self.min_node.right
                other_left = other.min_node.left

                self.min_node.right = other.min_node
                other.min_node.left = self.min_node
                self_right.left = other_left
                other_left.right = self_right

                if other.min_node.key < self.min_node.key:
                    self.min_node = other.min_node

            self.total_nodes += other.total_nodes

        other.min_node = None
        other.total_nodes = 0
        return self

    def _link_root(self, node: FibonacciHeapNode) -> None:
        if self.min_node is None:
            self.min_node = node
            node.left = node
            node.right = node
        else:
            node.right = self.min_node.right
            node.left = self.min_node
            self.min_node.right.left = node
            self.min_node.right = node

    def _cut(self, x: FibonacciHeapNode, y: FibonacciHeapNode) -> None:
        # Remove x from child list of y
        if x.right == x:
            y.child = None
        else:
            x.left.right = x.right
            x.right.left = x.left
            if y.child == x:
                y.child = x.right
        y.degree -= 1
        self._link_root(x)
        x.parent = None
        x.mark = False

    def _cascading_cut(self, y: FibonacciHeapNode) -> None:
        z = y.parent
        if z is not None:
            if not y.mark:
                y.mark = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)

    def _consolidate(self) -> None:
        max_deg = int(math.log(max(self.total_nodes, 1), 1.61803398875)) + 4
        A: List[Optional[FibonacciHeapNode]] = [None] * max_deg

        roots = self._iterate_ring(self.min_node)
        for w in roots:
            x = w
            d = x.degree
            while d < len(A) and A[d] is not None:
                y = A[d]
                if y is not None:
                    if x.key > y.key:
                        x, y = y, x
                    self._heap_link(y, x)
                    A[d] = None
                    d += 1
            if d < len(A):
                A[d] = x

        self.min_node = None
        for i in range(len(A)):
            node = A[i]
            if node is not None:
                if self.min_node is None:
                    self.min_node = node
                    node.left = node
                    node.right = node
                else:
                    self._link_root(node)
                    if node.key < self.min_node.key:
                        self.min_node = node

    def _heap_link(self, y: FibonacciHeapNode, x: FibonacciHeapNode) -> None:
        y.left.right = y.right
        y.right.left = y.left
        y.parent = x
        if x.child is None:
            x.child = y
            y.left = y
            y.right = y
        else:
            y.right = x.child.right
            y.left = x.child
            x.child.right.left = y
            x.child.right = y
        x.degree += 1
        y.mark = False

    def _iterate_ring(self, start: Optional[FibonacciHeapNode]) -> List[FibonacciHeapNode]:
        if start is None:
            return []
        nodes = []
        curr = start
        while True:
            nodes.append(curr)
            curr = curr.right
            if curr == start:
                break
        return nodes


class DisjointSetUnion:
    """Disjoint Set Union (Union-Find) with path compression, union by rank, and rollback checkpoints."""

    def __init__(self, elements: Optional[Any] = None):
        self.parent: Dict[Any, Any] = {}
        self.rank: Dict[Any, int] = {}
        self.size: Dict[Any, int] = {}
        self.history: List[Tuple[Any, Any, int, int]] = []  # (root_y, root_x, old_rank_x, old_size_x)
        if elements is not None:
            for el in elements:
                self.make_set(el)

    @property
    def num_sets(self) -> int:
        if not self.parent:
            return 0
        return len(set(self.find(x) for x in self.parent))

    def make_set(self, x: Any) -> None:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.size[x] = 1

    def find(self, x: Any) -> Any:
        if x not in self.parent:
            self.make_set(x)
        curr = x
        while curr != self.parent[curr]:
            curr = self.parent[curr]
        return curr

    def union(self, x: Any, y: Any) -> bool:
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            root_x, root_y = root_y, root_x

        self.history.append((root_y, root_x, self.rank[root_x], self.size[root_x]))
        self.parent[root_y] = root_x
        self.size[root_x] += self.size[root_y]
        if self.rank[root_x] == self.rank[root_y]:
            self.rank[root_x] += 1
        return True

    def connected(self, x: Any, y: Any) -> bool:
        return self.find(x) == self.find(y)

    def get_size(self, x: Any) -> int:
        return self.size[self.find(x)]

    def checkpoint(self) -> int:
        return len(self.history)

    def rollback(self, checkpoint_id: int) -> None:
        target = max(0, min(len(self.history), int(checkpoint_id)))
        while len(self.history) > target:
            root_y, root_x, old_rank_x, old_size_x = self.history.pop()
            self.parent[root_y] = root_y
            self.rank[root_x] = old_rank_x
            self.size[root_x] = old_size_x


class FenwickTree:
    """1D Binary Indexed Tree for prefix sums and point updates in O(log n)."""

    def __init__(self, size_or_values: Union[int, List[float]]):
        if isinstance(size_or_values, int):
            self.n = max(0, size_or_values)
            self.tree = [0.0] * (self.n + 1)
        else:
            vals = list(size_or_values)
            self.n = len(vals)
            self.tree = [0.0] * (self.n + 1)
            for i, val in enumerate(vals, start=1):
                self.add(i, val)

    def add(self, idx: int, delta: float) -> None:
        """Add delta to 1-based index."""
        i = int(idx)
        d = float(delta)
        while i <= self.n:
            self.tree[i] += d
            i += (i & -i)

    def update(self, idx: int, delta: float) -> None:
        """Alias for add."""
        self.add(idx, delta)

    def prefix_sum(self, idx: int) -> float:
        """Query sum of elements in 1-based range [1, idx]."""
        i = min(int(idx), self.n)
        s = 0.0
        while i > 0:
            s += self.tree[i]
            i -= (i & -i)
        return s

    def range_sum(self, left: int, right: int) -> float:
        """Query sum in 1-based range [left, right]."""
        if left > right:
            return 0.0
        return self.prefix_sum(right) - self.prefix_sum(left - 1)


class FenwickTree2D:
    """2D Binary Indexed Tree for rectangular 2D prefix sums and point updates in O(log n * log m)."""

    def __init__(self, rows: int, cols: int):
        self.rows = max(1, int(rows))
        self.cols = max(1, int(cols))
        self.tree = [[0.0] * (self.cols + 1) for _ in range(self.rows + 1)]

    def add(self, r: int, c: int, delta: float) -> None:
        """Add delta at 1-based (r, c)."""
        d = float(delta)
        i = int(r)
        while i <= self.rows:
            j = int(c)
            while j <= self.cols:
                self.tree[i][j] += d
                j += (j & -j)
            i += (i & -i)

    def update(self, r: int, c: int, delta: float) -> None:
        """Alias for add."""
        self.add(r, c, delta)

    def query(self, r: int, c: int) -> float:
        """Query 2D sum from (1, 1) to (r, c)."""
        return self.prefix_sum(r, c)

    def range_query(self, r1: int, c1: int, r2: int, c2: int) -> float:
        """Query sum in 2D rectangle [(r1, c1), (r2, c2)]."""
        return self.range_sum(r1, c1, r2, c2)

    def prefix_sum(self, r: int, c: int) -> float:
        """Query 2D sum from (1, 1) to (r, c)."""
        s = 0.0
        i = min(int(r), self.rows)
        while i > 0:
            j = min(int(c), self.cols)
            while j > 0:
                s += self.tree[i][j]
                j -= (j & -j)
            i -= (i & -i)
        return s

    def range_sum(self, r1: int, c1: int, r2: int, c2: int) -> float:
        """Query sum in 2D rectangle [(r1, c1), (r2, c2)]."""
        if r1 > r2 or c1 > c2:
            return 0.0
        return (
            self.prefix_sum(r2, c2)
            - self.prefix_sum(r1 - 1, c2)
            - self.prefix_sum(r2, c1 - 1)
            + self.prefix_sum(r1 - 1, c1 - 1)
        )


class BloomFilter:
    """Space-efficient probabilistic Bloom Filter for set membership with zero false negatives."""

    def __init__(self, expected_items: int = 1000, fp_rate: float = 0.01, capacity: Optional[int] = None, error_rate: Optional[float] = None):
        if capacity is not None:
            expected_items = capacity
        if error_rate is not None:
            fp_rate = error_rate
        n = max(1, int(expected_items))
        p = max(1e-6, min(0.5, float(fp_rate)))
        self.size = max(64, int(-n * math.log(p) / (math.log(2) ** 2)))
        self.num_hashes = max(1, int((self.size / n) * math.log(2)))
        self.bits = bytearray((self.size + 7) // 8)
        self.count = 0

    def _hashes(self, item: Any) -> List[int]:
        s = str(item).encode("utf-8")
        h1 = int(hashlib.md5(s).hexdigest(), 16)
        h2 = int(hashlib.sha256(s).hexdigest(), 16)
        return [(h1 + i * h2) % self.size for i in range(self.num_hashes)]

    def add(self, item: Any) -> None:
        for bit_idx in self._hashes(item):
            byte_idx = bit_idx // 8
            bit_pos = bit_idx % 8
            self.bits[byte_idx] |= (1 << bit_pos)
        self.count += 1

    def contains(self, item: Any) -> bool:
        for bit_idx in self._hashes(item):
            byte_idx = bit_idx // 8
            bit_pos = bit_idx % 8
            if not (self.bits[byte_idx] & (1 << bit_pos)):
                return False
        return True

    def __contains__(self, item: Any) -> bool:
        return self.contains(item)


class CountingBloomFilter:
    """Counting Bloom Filter supporting item deletion."""

    def __init__(self, expected_items: int = 1000, fp_rate: float = 0.01, capacity: Optional[int] = None, error_rate: Optional[float] = None):
        if capacity is not None:
            expected_items = capacity
        if error_rate is not None:
            fp_rate = error_rate
        n = max(1, int(expected_items))
        p = max(1e-6, min(0.5, float(fp_rate)))
        self.size = max(64, int(-n * math.log(p) / (math.log(2) ** 2)))
        self.num_hashes = max(1, int((self.size / n) * math.log(2)))
        self.counters = [0] * self.size
        self.count = 0

    def _hashes(self, item: Any) -> List[int]:
        s = str(item).encode("utf-8")
        h1 = int(hashlib.md5(s).hexdigest(), 16)
        h2 = int(hashlib.sha256(s).hexdigest(), 16)
        return [(h1 + i * h2) % self.size for i in range(self.num_hashes)]

    def add(self, item: Any) -> None:
        for bit_idx in self._hashes(item):
            self.counters[bit_idx] += 1
        self.count += 1

    def remove(self, item: Any) -> bool:
        if not self.contains(item):
            return False
        for bit_idx in self._hashes(item):
            if self.counters[bit_idx] > 0:
                self.counters[bit_idx] -= 1
        self.count -= 1
        return True

    def contains(self, item: Any) -> bool:
        for bit_idx in self._hashes(item):
            if self.counters[bit_idx] <= 0:
                return False
        return True

    def __contains__(self, item: Any) -> bool:
        return self.contains(item)


def dsa_fibonacci_heap() -> FibonacciHeap:
    """Creates a new Fibonacci Heap."""
    return FibonacciHeap()


def dsa_dsu() -> DisjointSetUnion:
    """Creates a new Disjoint Set Union (Union-Find) structure."""
    return DisjointSetUnion()


def dsa_fenwick_tree(size_or_values: Union[int, List[float]]) -> FenwickTree:
    """Creates a 1D Fenwick Tree (Binary Indexed Tree)."""
    return FenwickTree(size_or_values)


def dsa_fenwick_tree_2d(rows: int, cols: int) -> FenwickTree2D:
    """Creates a 2D Fenwick Tree (Binary Indexed Tree)."""
    return FenwickTree2D(rows, cols)


def dsa_bloom_filter(expected_items: int = 1000, fp_rate: float = 0.01) -> BloomFilter:
    """Creates a standard bit-array Bloom Filter."""
    return BloomFilter(expected_items=expected_items, fp_rate=fp_rate)


def dsa_counting_bloom_filter(expected_items: int = 1000, fp_rate: float = 0.01) -> CountingBloomFilter:
    """Creates a Counting Bloom Filter supporting deletions."""
    return CountingBloomFilter(expected_items=expected_items, fp_rate=fp_rate)


from doomscript.core.record import Record


class FibNode:
    def __init__(self, key: float, val: Any = None, node_id: Optional[str] = None):
        self.key = float(key)
        self.val = val if val is not None else key
        self.node_id = str(node_id) if node_id is not None else str(id(self))
        self.degree = 0
        self.marked = False
        self.parent: Optional["FibNode"] = None
        self.child: Optional["FibNode"] = None
        self.left = self
        self.right = self


class FibonacciHeapTree:
    """Fibonacci Heap implementation with O(1) amortized insert and O(log n) extract-min."""

    def __init__(self):
        self.min_node: Optional[FibNode] = None
        self.num_nodes = 0
        self.node_registry: Dict[str, FibNode] = {}

    def insert(self, key: float, val: Any = None, node_id: Optional[str] = None) -> str:
        node = FibNode(key, val, node_id)
        self.node_registry[node.node_id] = node
        if self.min_node is None:
            self.min_node = node
        else:
            node.left = self.min_node
            node.right = self.min_node.right
            self.min_node.right.left = node
            self.min_node.right = node
            if node.key < self.min_node.key:
                self.min_node = node
        self.num_nodes += 1
        return node.node_id

    def get_min(self) -> Optional[Dict[str, Any]]:
        if self.min_node is None:
            return None
        return {"node_id": self.min_node.node_id, "key": self.min_node.key, "val": self.min_node.val}

    def extract_min(self) -> Optional[Dict[str, Any]]:
        z = self.min_node
        if z is None:
            return None

        if z.child is not None:
            children = []
            curr = z.child
            while True:
                children.append(curr)
                curr = curr.right
                if curr == z.child:
                    break
            for ch in children:
                ch.parent = None
                ch.left = self.min_node
                ch.right = self.min_node.right
                self.min_node.right.left = ch
                self.min_node.right = ch

        z.left.right = z.right
        z.right.left = z.left

        if z == z.right:
            self.min_node = None
        else:
            self.min_node = z.right
            self._consolidate()

        self.num_nodes -= 1
        if z.node_id in self.node_registry:
            del self.node_registry[z.node_id]
        return {"node_id": z.node_id, "key": z.key, "val": z.val}

    def _consolidate(self):
        max_deg = int(math.log2(max(self.num_nodes, 1)) * 2) + 5
        A: List[Optional[FibNode]] = [None] * max_deg

        root_list = []
        if self.min_node is not None:
            curr = self.min_node
            while True:
                root_list.append(curr)
                curr = curr.right
                if curr == self.min_node:
                    break

        for w in root_list:
            x = w
            d = x.degree
            while d < len(A) and A[d] is not None:
                y = A[d]
                if y == x:
                    break
                if x.key > y.key:
                    x, y = y, x
                self._fib_heap_link(y, x)
                A[d] = None
                d += 1
            if d < len(A):
                A[d] = x

        self.min_node = None
        for i in range(len(A)):
            if A[i] is not None:
                if self.min_node is None:
                    self.min_node = A[i]
                    self.min_node.left = self.min_node
                    self.min_node.right = self.min_node
                else:
                    node = A[i]
                    node.left = self.min_node
                    node.right = self.min_node.right
                    self.min_node.right.left = node
                    self.min_node.right = node
                    if node.key < self.min_node.key:
                        self.min_node = node

    def _fib_heap_link(self, y: FibNode, x: FibNode):
        y.left.right = y.right
        y.right.left = y.left
        y.parent = x
        if x.child is None:
            x.child = y
            y.left = y
            y.right = y
        else:
            y.left = x.child
            y.right = x.child.right
            x.child.right.left = y
            x.child.right = y
        x.degree += 1
        y.marked = False

    def decrease_key(self, node_id: str, new_key: float):
        if node_id not in self.node_registry:
            raise KeyError(f"Node id {node_id} not found in Fibonacci heap")
        x = self.node_registry[node_id]
        if new_key > x.key:
            raise ValueError("New key is greater than current key")
        x.key = float(new_key)
        y = x.parent
        if y is not None and x.key < y.key:
            self._cut(x, y)
            self._cascading_cut(y)
        if self.min_node is None or x.key < self.min_node.key:
            self.min_node = x

    def _cut(self, x: FibNode, y: FibNode):
        if x.right == x:
            y.child = None
        else:
            x.left.right = x.right
            x.right.left = x.left
            if y.child == x:
                y.child = x.right
        y.degree -= 1
        x.left = self.min_node
        x.right = self.min_node.right
        self.min_node.right.left = x
        self.min_node.right = x
        x.parent = None
        x.marked = False

    def _cascading_cut(self, y: FibNode):
        z = y.parent
        if z is not None:
            if not y.marked:
                y.marked = True
            else:
                self._cut(y, z)
                self._cascading_cut(z)


class SplayTreeNode:
    def __init__(self, key: float, val: Any = None):
        self.key = float(key)
        self.val = val if val is not None else key
        self.left: Optional["SplayTreeNode"] = None
        self.right: Optional["SplayTreeNode"] = None
        self.parent: Optional["SplayTreeNode"] = None


class SplayTreeSelfBalancing:
    """Self-balancing binary search tree using Zig/Zig-Zig/Zig-Zag splay rotations."""

    def __init__(self):
        self.root: Optional[SplayTreeNode] = None
        self.total_rotations = 0
        self.size = 0

    def _rotate_right(self, x: SplayTreeNode):
        y = x.left
        if y is None:
            return
        x.left = y.right
        if y.right:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        self.total_rotations += 1

    def _rotate_left(self, x: SplayTreeNode):
        y = x.right
        if y is None:
            return
        x.right = y.left
        if y.left:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self.total_rotations += 1

    def splay(self, x: SplayTreeNode):
        while x.parent is not None:
            p = x.parent
            g = p.parent
            if g is None:
                if x == p.left:
                    self._rotate_right(p)
                else:
                    self._rotate_left(p)
            elif x == p.left and p == g.left:
                self._rotate_right(g)
                self._rotate_right(p)
            elif x == p.right and p == g.right:
                self._rotate_left(g)
                self._rotate_left(p)
            elif x == p.right and p == g.left:
                self._rotate_left(p)
                self._rotate_right(g)
            else:
                self._rotate_right(p)
                self._rotate_left(g)

    def insert(self, key: float, val: Any = None):
        node = SplayTreeNode(key, val)
        y = None
        x = self.root
        while x is not None:
            y = x
            if node.key < x.key:
                x = x.left
            elif node.key > x.key:
                x = x.right
            else:
                x.val = node.val
                self.splay(x)
                return
        node.parent = y
        if y is None:
            self.root = node
        elif node.key < y.key:
            y.left = node
        else:
            y.right = node
        self.splay(node)
        self.size += 1

    def find(self, key: float) -> Optional[Any]:
        curr = self.root
        last = None
        while curr is not None:
            last = curr
            if key < curr.key:
                curr = curr.left
            elif key > curr.key:
                curr = curr.right
            else:
                self.splay(curr)
                return curr.val
        if last is not None:
            self.splay(last)
        return None

    def inorder(self) -> List[float]:
        res = []
        def _in(n):
            if n:
                _in(n.left)
                res.append(n.key)
                _in(n.right)
        _in(self.root)
        return res

    def height(self) -> int:
        def _h(n):
            return 0 if n is None else 1 + max(_h(n.left), _h(n.right))
        return _h(self.root)


def dsa_fibonacci_heap_ops(operations: List[Dict[str, Any]]) -> Any:
    """Executes a sequence of operations on a Fibonacci Heap."""
    heap = FibonacciHeapTree()
    extracted = []
    min_history = []
    for op in operations:
        action = str(op.get("op", op.get("action", ""))).lower()
        if action == "insert":
            k = op.get("key", 0.0)
            v = op.get("val", k)
            nid = op.get("id")
            heap.insert(k, v, node_id=nid)
        elif action == "extract_min":
            ext = heap.extract_min()
            if ext:
                extracted.append(ext)
        elif action == "decrease_key":
            nid = str(op.get("id"))
            nk = op.get("new_key", 0.0)
            heap.decrease_key(nid, nk)
        min_history.append(heap.get_min())

    final_min = heap.get_min()
    return Record({
        "num_nodes": heap.num_nodes,
        "final_min_key": final_min["key"] if final_min else None,
        "extracted_nodes": [Record(e) for e in extracted],
        "extracted_count": len(extracted),
    })


def dsa_splay_tree_ops(operations: List[Dict[str, Any]]) -> Any:
    """Executes a sequence of operations on a Splay Tree."""
    tree = SplayTreeSelfBalancing()
    find_results = []
    for op in operations:
        action = str(op.get("op", op.get("action", ""))).lower()
        if action == "insert":
            tree.insert(op.get("key", 0.0), op.get("val"))
        elif action == "find":
            val = tree.find(op.get("key", 0.0))
            find_results.append(val)

    return Record({
        "size": tree.size,
        "tree_size": tree.size,
        "root_key": tree.root.key if tree.root else None,
        "total_rotations": tree.total_rotations,
        "tree_height": tree.height(),
        "inorder_keys": tree.inorder(),
        "find_results": find_results,
    })


# ==============================================================================
# VAN EMDE BOAS (vEB) TREE O(log log U) PRIORITY QUEUE
# ==============================================================================

class VanEmdeBoasTreeVEB:
    """Van Emde Boas recursive priority queue tree over universe size U = 2^(2^k)."""

    def __init__(self, u: int = 16):
        # Round up u to power of 2
        power = 1
        while power < u:
            power <<= 1
        self.u = max(2, power)

        self.min_val: Optional[int] = None
        self.max_val: Optional[int] = None

        if self.u == 2:
            self.summary = None
            self.clusters = None
        else:
            half_power = int(math.ceil(math.log2(self.u) / 2.0))
            self.u_upper = 1 << half_power
            self.u_lower = 1 << (int(math.log2(self.u)) - half_power)

            self.summary: Optional[VanEmdeBoasTreeVEB] = VanEmdeBoasTreeVEB(self.u_upper)
            self.clusters: Optional[List[VanEmdeBoasTreeVEB]] = [
                VanEmdeBoasTreeVEB(self.u_lower) for _ in range(self.u_upper)
            ]

    def _high(self, x: int) -> int:
        return x // self.u_lower

    def _low(self, x: int) -> int:
        return x % self.u_lower

    def _index(self, h: int, l: int) -> int:
        return h * self.u_lower + l

    def contains(self, x: int) -> bool:
        if x == self.min_val or x == self.max_val:
            return True
        if self.u == 2 or self.min_val is None:
            return False
        return self.clusters[self._high(x)].contains(self._low(x))

    def insert(self, x: int) -> None:
        if self.min_val is None:
            self.min_val = x
            self.max_val = x
            return

        if x < self.min_val:
            x, self.min_val = self.min_val, x

        if self.u > 2:
            h = self._high(x)
            l = self._low(x)
            if self.clusters[h].min_val is None:
                self.summary.insert(h)
                self.clusters[h].insert(l)
            else:
                self.clusters[h].insert(l)

        if x > self.max_val:
            self.max_val = x

    def successor(self, x: int) -> Optional[int]:
        if self.u == 2:
            if x == 0 and self.max_val == 1:
                return 1
            return None

        if self.min_val is not None and x < self.min_val:
            return self.min_val

        h = self._high(x)
        l = self._low(x)
        max_in_cluster = self.clusters[h].max_val

        if max_in_cluster is not None and l < max_in_cluster:
            offset = self.clusters[h].successor(l)
            return self._index(h, offset)

        succ_cluster = self.summary.successor(h)
        if succ_cluster is None:
            return None

        offset = self.clusters[succ_cluster].min_val
        return self._index(succ_cluster, offset)

    def delete(self, x: int) -> None:
        if self.min_val == self.max_val:
            if self.min_val == x:
                self.min_val = None
                self.max_val = None
            return

        if self.u == 2:
            if x == 0:
                self.min_val = 1
            else:
                self.min_val = 0
            self.max_val = self.min_val
            return

        if x == self.min_val:
            first_cluster = self.summary.min_val
            if first_cluster is None:
                self.min_val = None
                self.max_val = None
                return
            x = self._index(first_cluster, self.clusters[first_cluster].min_val)
            self.min_val = x

        h = self._high(x)
        l = self._low(x)
        self.clusters[h].delete(l)

        if self.clusters[h].min_val is None:
            self.summary.delete(h)
            if x == self.max_val:
                summary_max = self.summary.max_val
                if summary_max is None:
                    self.max_val = self.min_val
                else:
                    self.max_val = self._index(summary_max, self.clusters[summary_max].max_val)
        elif x == self.max_val:
            self.max_val = self._index(h, self.clusters[h].max_val)


# ==============================================================================
# HEAVY-LIGHT DECOMPOSITION (HLD) TREE SOLVER
# ==============================================================================

class HeavyLightDecompositionHLD:
    """Heavy-Light tree decomposition with iterative Segment Tree for path queries in O(log^2 N)."""

    def __init__(self, n: int, edges: List[Tuple[int, int]], values: Optional[List[float]] = None):
        self.n = max(1, int(n))
        self.adj: List[List[int]] = [[] for _ in range(self.n)]
        for u, v in edges:
            if 0 <= u < self.n and 0 <= v < self.n:
                self.adj[u].append(v)
                self.adj[v].append(u)

        self.parent = [-1] * self.n
        self.depth = [0] * self.n
        self.sz = [0] * self.n
        self.heavy = [-1] * self.n
        self.head = [0] * self.n
        self.pos = [0] * self.n
        self.cur_pos = 0

        # Initial DFS for sizes and heavy edges
        self._dfs_sz(0, -1, 0)
        # Second DFS for chain heads and flat position mapping
        self._dfs_hld(0, 0)

        # Build Segment Tree over flattened node values
        self.seg_tree = [0.0] * (2 * self.n)
        if values:
            for node_idx, val in enumerate(values[:self.n]):
                self.update_node(node_idx, float(val))

    def _dfs_sz(self, u: int, p: int, d: int) -> None:
        self.parent[u] = p
        self.depth[u] = d
        self.sz[u] = 1
        max_c_size = 0
        for v in self.adj[u]:
            if v != p:
                self._dfs_sz(v, u, d + 1)
                self.sz[u] += self.sz[v]
                if self.sz[v] > max_c_size:
                    max_c_size = self.sz[v]
                    self.heavy[u] = v

    def _dfs_hld(self, u: int, h: int) -> None:
        self.head[u] = h
        self.pos[u] = self.cur_pos
        self.cur_pos += 1
        if self.heavy[u] != -1:
            self._dfs_hld(self.heavy[u], h)
        for v in self.adj[u]:
            if v != self.parent[u] and v != self.heavy[u]:
                self._dfs_hld(v, v)

    def update_node(self, node: int, val: float) -> None:
        p = self.pos[node] + self.n
        self.seg_tree[p] = float(val)
        p >>= 1
        while p > 0:
            self.seg_tree[p] = max(self.seg_tree[p << 1], self.seg_tree[(p << 1) | 1])
            p >>= 1

    def _query_seg(self, left: int, right: int) -> float:
        l = left + self.n
        r = right + self.n + 1
        res = -float("inf")
        while l < r:
            if l & 1:
                res = max(res, self.seg_tree[l])
                l += 1
            if r & 1:
                r -= 1
                res = max(res, self.seg_tree[r])
            l >>= 1
            r >>= 1
        return res if res != -float("inf") else 0.0

    def query_path_max(self, u: int, v: int) -> float:
        """Finds maximum node value along unique path between u and v in O(log^2 N)."""
        res = -float("inf")
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] > self.depth[self.head[v]]:
                u, v = v, u
            res = max(res, self._query_seg(self.pos[self.head[v]], self.pos[v]))
            v = self.parent[self.head[v]]

        if self.depth[u] > self.depth[v]:
            u, v = v, u
        res = max(res, self._query_seg(self.pos[u], self.pos[v]))
        return res if res != -float("inf") else 0.0


def dsa_veb_tree_ops(universe_size: int, operations: List[Dict[str, Any]]) -> Record:
    """Executes operations on a Van Emde Boas Priority Queue tree."""
    veb = VanEmdeBoasTreeVEB(universe_size)
    results = []
    for op in operations:
        action = str(op.get("op", op.get("action", ""))).lower()
        val = int(op.get("val", op.get("x", 0)))
        if action == "insert":
            veb.insert(val)
        elif action == "delete":
            veb.delete(val)
        elif action == "contains":
            results.append(veb.contains(val))
        elif action == "successor":
            results.append(veb.successor(val))

    return Record({
        "universe_size": veb.u,
        "min": veb.min_val,
        "max": veb.max_val,
        "query_results": results,
    })


def dsa_hld_tree(n_nodes: int, edges: List[Any], initial_values: Optional[List[float]] = None) -> Record:
    """Initializes a Heavy-Light Tree Decomposition."""
    edge_pairs = []
    for e in edges:
        edge_pairs.append((int(e[0]), int(e[1])))
    hld = HeavyLightDecompositionHLD(n_nodes, edge_pairs, values=initial_values)
    return Record({
        "num_nodes": hld.n,
        "instance": hld,
    })


def dsa_hld_query_path(hld_record: Any, u: int, v: int) -> float:
    """Queries max node value along tree path from u to v."""
    inst = hld_record.instance if hasattr(hld_record, "instance") else hld_record
    return inst.query_path_max(int(u), int(v))


def dsa_hld_update_node(hld_record: Any, u: int, val: float) -> None:
    """Updates node value in HLD tree."""
    inst = hld_record.instance if hasattr(hld_record, "instance") else hld_record
    inst.update_node(int(u), float(val))


class LinkCutTreeDynamicGraph:
    """Sleator & Tarjan's Link-Cut Tree Dynamic Forest Data Structure.

    Maintains a dynamic forest of trees supporting tree linking, cutting,
    connectivity queries, and path aggregate queries in amortized O(log N) time.
    """

    class _Node:
        def __init__(self, key: int, val: int = 0) -> None:
            self.key = key
            self.val = val
            self.sum = val
            self.p: Optional[LinkCutTreeDynamicGraph._Node] = None
            self.ch: List[Optional[LinkCutTreeDynamicGraph._Node]] = [None, None]
            self.rev = False

    def __init__(self, n: int, initial_values: Optional[List[int]] = None, node_values: Optional[List[int]] = None) -> None:
        raw_vals = node_values if node_values is not None else initial_values
        vals = raw_vals if raw_vals and len(raw_vals) >= n else [i for i in range(n)]
        self.nodes = [self._Node(i, vals[i]) for i in range(n)]
        self.n = n

    def _is_root(self, x: _Node) -> bool:
        return x.p is None or (x.p.ch[0] != x and x.p.ch[1] != x)

    def _push(self, x: Optional[_Node]) -> None:
        if x and x.rev:
            x.ch[0], x.ch[1] = x.ch[1], x.ch[0]
            if x.ch[0]:
                x.ch[0].rev = not x.ch[0].rev
            if x.ch[1]:
                x.ch[1].rev = not x.ch[1].rev
            x.rev = False

    def _pull(self, x: Optional[_Node]) -> None:
        if x:
            x.sum = x.val
            if x.ch[0]:
                x.sum += x.ch[0].sum
            if x.ch[1]:
                x.sum += x.ch[1].sum

    def _rotate(self, x: _Node) -> None:
        y = x.p
        if not y:
            return
        z = y.p
        d = 1 if y.ch[1] == x else 0
        if not self._is_root(y) and z:
            z.ch[1 if z.ch[1] == y else 0] = x
        x.p = z

        y.ch[d] = x.ch[1 - d]
        if x.ch[1 - d]:
            x.ch[1 - d].p = y

        x.ch[1 - d] = y
        y.p = x

        self._pull(y)
        self._pull(x)

    def _splay(self, x: _Node) -> None:
        stack = []
        cur: Optional[LinkCutTreeDynamicGraph._Node] = x
        while cur and not self._is_root(cur):
            stack.append(cur)
            cur = cur.p
        if cur:
            stack.append(cur)
        while stack:
            self._push(stack.pop())

        while not self._is_root(x):
            y = x.p
            if not y:
                break
            z = y.p
            if not self._is_root(y) and z:
                if (y.ch[1] == x) ^ (z.ch[1] == y):
                    self._rotate(x)
                else:
                    self._rotate(y)
            self._rotate(x)

    def access(self, x: _Node) -> None:
        t: Optional[LinkCutTreeDynamicGraph._Node] = None
        cur: Optional[LinkCutTreeDynamicGraph._Node] = x
        while cur:
            self._splay(cur)
            cur.ch[1] = t
            self._pull(cur)
            t = cur
            cur = cur.p
        self._splay(x)

    def make_root(self, u: int) -> None:
        x = self.nodes[u]
        self.access(x)
        x.rev = not x.rev

    def find_root(self, u: int) -> int:
        x = self.nodes[u]
        self.access(x)
        while x.ch[0]:
            self._push(x)
            x = x.ch[0]
        self._splay(x)
        return x.key

    def link(self, u: int, v: int) -> bool:
        if self.connected(u, v):
            return False
        self.make_root(u)
        self.nodes[u].p = self.nodes[v]
        return True

    def cut(self, u: int, v: int) -> bool:
        self.make_root(u)
        self.access(self.nodes[v])
        if self.nodes[v].ch[0] == self.nodes[u] and self.nodes[u].ch[1] is None:
            self.nodes[v].ch[0] = None
            self.nodes[u].p = None
            self._pull(self.nodes[v])
            return True
        return False

    def connected(self, u: int, v: int) -> bool:
        return self.find_root(u) == self.find_root(v)

    def path_sum(self, u: int, v: int) -> int:
        self.make_root(u)
        self.access(self.nodes[v])
        return self.nodes[v].sum


class SuffixTreeUkkonen:
    """Esko Ukkonen's Online Linear-Time O(N) Suffix Tree Construction.

    Constructs implicit and explicit suffix tree with suffix links, supporting
    fast exact pattern searching, longest repeated substring, and suffix statistics.
    """

    class _Node:
        def __init__(self, start: int, end: Optional[List[int]]) -> None:
            self.start = start
            self.end = end
            self.children: Dict[str, SuffixTreeUkkonen._Node] = {}
            self.suffix_link: Optional[SuffixTreeUkkonen._Node] = None

    def __init__(self, text: str) -> None:
        self.raw_text = text
        self.text = text + "$"
        self.root = self._Node(-1, [-1])
        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0
        self.remaining = 0
        self.leaf_end = [-1]
        self._build()

    def _edge_length(self, node: _Node) -> int:
        if node.end is None:
            return 0
        return node.end[0] - node.start + 1

    def _build(self) -> None:
        n = len(self.text)
        for i in range(n):
            self.leaf_end[0] = i
            self.remaining += 1
            last_created_internal: Optional[SuffixTreeUkkonen._Node] = None

            while self.remaining > 0:
                if self.active_length == 0:
                    self.active_edge = i

                ch = self.text[self.active_edge]
                if ch not in self.active_node.children:
                    self.active_node.children[ch] = self._Node(i, self.leaf_end)
                    if last_created_internal:
                        last_created_internal.suffix_link = self.active_node
                        last_created_internal = None
                else:
                    nxt = self.active_node.children[ch]
                    edge_len = self._edge_length(nxt)
                    if self.active_length >= edge_len:
                        self.active_edge += edge_len
                        self.active_length -= edge_len
                        self.active_node = nxt
                        continue

                    if self.text[nxt.start + self.active_length] == self.text[i]:
                        self.active_length += 1
                        if last_created_internal:
                            last_created_internal.suffix_link = self.active_node
                        break

                    split_end = [nxt.start + self.active_length - 1]
                    split = self._Node(nxt.start, split_end)
                    self.active_node.children[ch] = split

                    split.children[self.text[i]] = self._Node(i, self.leaf_end)
                    nxt.start += self.active_length
                    split.children[self.text[nxt.start]] = nxt

                    if last_created_internal:
                        last_created_internal.suffix_link = split
                    last_created_internal = split

                self.remaining -= 1
                if self.active_node == self.root and self.active_length > 0:
                    self.active_length -= 1
                    self.active_edge = i - self.remaining + 1
                elif self.active_node != self.root:
                    self.active_node = self.active_node.suffix_link if self.active_node.suffix_link else self.root

    def search(self, pattern: str) -> bool:
        """Determines if pattern occurs as a substring."""
        node = self.root
        i = 0
        m = len(pattern)
        while i < m:
            ch = pattern[i]
            if ch not in node.children:
                return False
            nxt = node.children[ch]
            edge_len = self._edge_length(nxt)
            k = 0
            while k < edge_len and i < m:
                if self.text[nxt.start + k] != pattern[i]:
                    return False
                k += 1
                i += 1
            node = nxt
        return True

    def longest_repeated_substring(self) -> str:
        """Finds the longest repeated substring in the text."""
        best_str = ""

        def dfs(node: SuffixTreeUkkonen._Node, cur_path: str) -> None:
            nonlocal best_str
            if len(node.children) >= 2 and len(cur_path) > len(best_str):
                best_str = cur_path
            for ch, nxt in node.children.items():
                edge_len = self._edge_length(nxt)
                seg = self.text[nxt.start : nxt.start + edge_len]
                if "$" in seg:
                    seg = seg[: seg.find("$")]
                dfs(nxt, cur_path + seg)

        dfs(self.root, "")
        return best_str


def dsa_create_link_cut_tree(n_nodes: int, node_values: Optional[List[int]] = None) -> Record:
    """Initializes a Link-Cut Tree dynamic forest."""
    lct = LinkCutTreeDynamicGraph(int(n_nodes), initial_values=node_values)
    return Record({
        "num_nodes": n_nodes,
        "instance": lct,
    })


def dsa_lct_link(lct_record: Any, u: int, v: int) -> bool:
    """Links node u to node v in Link-Cut Tree."""
    inst = lct_record.instance if hasattr(lct_record, "instance") else lct_record
    return inst.link(int(u), int(v))


def dsa_lct_cut(lct_record: Any, u: int, v: int) -> bool:
    """Cuts edge between u and v in Link-Cut Tree."""
    inst = lct_record.instance if hasattr(lct_record, "instance") else lct_record
    return inst.cut(int(u), int(v))


def dsa_lct_connected(lct_record: Any, u: int, v: int) -> bool:
    """Checks if u and v are connected in the dynamic forest."""
    inst = lct_record.instance if hasattr(lct_record, "instance") else lct_record
    return inst.connected(int(u), int(v))


def dsa_lct_path_sum(lct_record: Any, u: int, v: int) -> int:
    """Calculates sum of node values along tree path between u and v."""
    inst = lct_record.instance if hasattr(lct_record, "instance") else lct_record
    return inst.path_sum(int(u), int(v))


def dsa_create_suffix_tree(text: str) -> Record:
    """Builds Ukkonen suffix tree from input text."""
    st = SuffixTreeUkkonen(text)
    return Record({
        "text": text,
        "instance": st,
    })


def dsa_suffix_tree_search(st_record: Any, pattern: str) -> bool:
    """Searches for pattern in Ukkonen suffix tree."""
    inst = st_record.instance if hasattr(st_record, "instance") else st_record
    return inst.search(pattern)


def dsa_suffix_tree_longest_repeated(st_record: Any) -> str:
    """Returns longest repeated substring using Ukkonen suffix tree."""
    inst = st_record.instance if hasattr(st_record, "instance") else st_record
    return inst.longest_repeated_substring()






def execute_dsa_ir(spec: Any) -> Any:
    """Executes a DSA Domain IR specification against the caller's scope."""
    import sys
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = DsaRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def run_dsa_benchmark(fn_name: str, input_sizes: List[int], repeat: int = 3, generator: str = "sorted_integers", measure_memory: bool = True) -> Any:
    """Executes a DSA benchmark against the caller's scope and returns the ComplexityReport dict."""
    import sys
    spec = BenchmarkSpec(
        fn_name=fn_name,
        input_sizes=input_sizes,
        repeat=repeat,
        generator=generator,
        measure_memory=measure_memory,
    )
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return run_benchmark(spec, scope)


def analyze_complexity(fn_name: str, input_sizes: Optional[List[int]] = None) -> Any:
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    spec = BenchmarkSpec(fn_name=fn_name, input_sizes=input_sizes or [100, 500, 1000, 2000])
    return run_benchmark(spec, scope)


def run_benchmark_with_sizes(fn_name: str, sizes: List[int]) -> Any:
    import sys
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    spec = BenchmarkSpec(fn_name=fn_name, input_sizes=sizes)
    return run_benchmark(spec, scope)





def dsa_push(container: Any, item: Any) -> Any:
    """Push an item into a heap, list, or deque."""
    from collections import deque
    if hasattr(container, "push") and callable(container.push):
        container.push(item)
    elif isinstance(container, deque):
        container.append(item)
    elif isinstance(container, list):
        container.append(item)
    return container


def dsa_heap_push(heap_list: Any, item: Any) -> Any:
    """Push an item into a min/max heap or list."""
    if hasattr(heap_list, "push") and callable(heap_list.push):
        heap_list.push(item)
        return heap_list
    import heapq
    heapq.heappush(heap_list, item)
    return heap_list


def dsa_heap_pop_min(heap_list: Any) -> Any:
    """Pop the minimum item from a min-heap or list."""
    if isinstance(heap_list, DsaHeap):
        return heap_list.pop()
    import heapq
    if not heap_list:
        return None
    return heapq.heappop(heap_list)


def dsa_heap_pop_max(heap_list: Any) -> Any:
    """Remove and return the maximum item from a max-heap or collection."""
    if isinstance(heap_list, DsaHeap) and getattr(heap_list, "kind", "") == "max":
        return heap_list.pop()
    if not heap_list:
        return None
    mx = max(heap_list)
    heap_list.remove(mx)
    return mx


def dsa_deque_pop_left(q: Any) -> Any:
    """Pop the first/left element from a deque or list."""
    from collections import deque
    if isinstance(q, deque):
        return q.popleft() if q else None
    if isinstance(q, list):
        return q.pop(0) if q else None
    return None
