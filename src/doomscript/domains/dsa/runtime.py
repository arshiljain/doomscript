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
