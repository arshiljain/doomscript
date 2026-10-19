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
