"""Runtime execution engine for Simulation & Numerical Optimization."""

import copy
import heapq
import math
import random
from typing import Any, Callable, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.sim.spec import SimulationSpec, OptimizationSpec, TrialsSpec, SweepSpec


def summarize_metric(values: Any) -> Dict[str, Any]:
    """Level 1: Computes statistical summary (mean, median, percentiles, std) of a metric series."""
    if not isinstance(values, list) or not values:
        if isinstance(values, (int, float)):
            return {"count": 1, "mean": float(values), "median": float(values)}
        return {"count": 0, "mean": 0.0, "median": 0.0}

    clean_vals = sorted([float(v) for v in values if isinstance(v, (int, float))])
    if not clean_vals:
        return {"count": 0, "mean": 0.0, "median": 0.0}

    n = len(clean_vals)
    mean_val = sum(clean_vals) / n
    variance = sum((v - mean_val) ** 2 for v in clean_vals) / n
    std_val = math.sqrt(variance)

    def percentile(p: float) -> float:
        idx = int(p * (n - 1))
        return clean_vals[idx]

    return {
        "count": n,
        "mean": round(mean_val, 4),
        "median": round(percentile(0.5), 4),
        "min": round(clean_vals[0], 4),
        "max": round(clean_vals[-1], 4),
        "p90": round(percentile(0.9), 4),
        "p95": round(percentile(0.95), 4),
        "p99": round(percentile(0.99), 4),
        "std_dev": round(std_val, 4),
    }


def summarize_uncertainty(values: Any, confidence: float = 0.95) -> Dict[str, Any]:
    """Computes sample size, mean, std_dev, std_error, and 95% confidence intervals."""
    if not isinstance(values, list) or not values:
        if isinstance(values, (int, float)):
            v = float(values)
            return {
                "count": 1,
                "mean": v,
                "std_dev": 0.0,
                "std_error": 0.0,
                "margin_of_error": 0.0,
                "ci_95": [v, v],
                "ci_lower": v,
                "ci_upper": v,
            }
        return {
            "count": 0,
            "mean": 0.0,
            "std_dev": 0.0,
            "std_error": 0.0,
            "margin_of_error": 0.0,
            "ci_95": [0.0, 0.0],
            "ci_lower": 0.0,
            "ci_upper": 0.0,
        }

    clean_vals = [float(v) for v in values if isinstance(v, (int, float))]
    n = len(clean_vals)
    if n == 0:
        return {
            "count": 0,
            "mean": 0.0,
            "std_dev": 0.0,
            "std_error": 0.0,
            "margin_of_error": 0.0,
            "ci_95": [0.0, 0.0],
            "ci_lower": 0.0,
            "ci_upper": 0.0,
        }

    mean_val = sum(clean_vals) / n
    variance = sum((v - mean_val) ** 2 for v in clean_vals) / (n - 1) if n > 1 else 0.0
    std_val = math.sqrt(variance)
    std_err = std_val / math.sqrt(n) if n > 0 else 0.0
    # 95% critical z-score
    z = 1.96
    margin = round(z * std_err, 4)
    ci_lower = round(mean_val - margin, 4)
    ci_upper = round(mean_val + margin, 4)

    return {
        "count": n,
        "mean": round(mean_val, 4),
        "std_dev": round(std_val, 4),
        "std_error": round(std_err, 4),
        "margin_of_error": margin,
        "ci_95": [ci_lower, ci_upper],
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
    }


def sample_distribution(
    dist_name: str, params: Dict[str, float], count: int = 1000, seed: int = 42
) -> List[float]:
    """Level 2: Generates random samples from common theoretical distributions."""
    rng = random.Random(seed)
    dist = dist_name.lower()
    samples = []

    if dist in ("exponential", "exp"):
        rate = params.get("rate", 1.0)
        scale = 1.0 / rate if rate > 0 else 1.0
        for _ in range(count):
            u = rng.random()
            samples.append(-math.log(1.0 - u) * scale)

    elif dist in ("poisson", "pois"):
        rate = params.get("rate", 10.0)
        # Knuth's algorithm for Poisson generation
        L = math.exp(-rate) if rate < 700 else 1e-100
        for _ in range(count):
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= rng.random()
            samples.append(float(k - 1))

    elif dist in ("normal", "gaussian"):
        mu = params.get("mean", 0.0)
        sigma = params.get("std", 1.0)
        for _ in range(count):
            samples.append(rng.gauss(mu, sigma))

    elif dist in ("uniform", "unif"):
        low = params.get("low", params.get("min", 0.0))
        high = params.get("high", params.get("max", 1.0))
        for _ in range(count):
            samples.append(rng.uniform(low, high))
    else:
        for _ in range(count):
            samples.append(rng.random())

    return samples


class DiscreteEventQueueEngine:
    """Discrete-event simulation engine for queueing systems (M/M/c)."""

    def __init__(self, spec: SimulationSpec, seed: Optional[int] = None):
        self.spec = spec
        actual_seed = seed if seed is not None else (spec.seed if spec.seed is not None else 42)
        self.rng = random.Random(actual_seed)

    def _sample_interval(self, dist: str, params: Dict[str, float]) -> float:
        rate = params.get("rate", 1.0)
        if rate <= 0:
            rate = 1.0
        # Exponential inter-arrival or service time
        u = max(self.rng.random(), 1e-10)
        return -math.log(u) / rate

    def run(self) -> Dict[str, Any]:
        spec = self.spec
        n_events = spec.duration
        c_servers = spec.servers

        current_time = 0.0
        server_free_times = [0.0] * c_servers

        waiting_times: List[float] = []
        service_times: List[float] = []
        queue_lengths: List[int] = []

        # Event queue: list of arrival times
        for _ in range(n_events):
            inter_arrival = self._sample_interval(spec.arrival_dist, spec.arrival_params)
            current_time += inter_arrival

            # Next available server
            earliest_server_idx = min(range(c_servers), key=lambda i: server_free_times[i])
            service_start = max(current_time, server_free_times[earliest_server_idx])
            wait = service_start - current_time
            waiting_times.append(wait)

            service_dur = self._sample_interval(spec.service_dist, spec.service_params)
            service_times.append(service_dur)

            server_free_times[earliest_server_idx] = service_start + service_dur

            # Queue length approximation
            q_len = sum(1 for st in server_free_times if st > current_time)
            queue_lengths.append(max(0, q_len - c_servers))

        total_sim_time = max(server_free_times)
        total_busy_time = sum(service_times)
        utilization = total_busy_time / (c_servers * total_sim_time) if total_sim_time > 0 else 0.0

        return {
            "name": spec.name,
            "_spec": spec,
            "total_events": n_events,
            "total_time": round(total_sim_time, 2),
            "server_utilization": round(min(1.0, utilization), 4),
            "utilization": round(min(1.0, utilization), 4),
            "waiting_time": waiting_times,
            "service_time": service_times,
            "queue_length": queue_lengths,
            "summary": {
                "waiting_time": summarize_metric(waiting_times),
                "service_time": summarize_metric(service_times),
                "queue_length": summarize_metric(queue_lengths),
            },
        }



class NelderMeadOptimizer:
    """Zero-dependency Nelder-Mead Downhill Simplex Optimizer."""

    def __init__(self, tol: float = 1e-4, max_iter: int = 500):
        self.tol = tol
        self.max_iter = max_iter

    def minimize(self, fn: Callable[[List[float]], float], x0: List[float]) -> Dict[str, Any]:
        dim = len(x0)
        # Build initial simplex
        simplex = [list(x0)]
        for i in range(dim):
            point = list(x0)
            point[i] += 0.05 if point[i] != 0.0 else 0.00025
            simplex.append(point)

        for _ in range(self.max_iter):
            simplex.sort(key=lambda pt: fn(pt))
            best = simplex[0]
            worst = simplex[-1]
            second_worst = simplex[-2]

            # Check convergence
            if abs(fn(worst) - fn(best)) < self.tol:
                break

            # Centroid of all points except worst
            centroid = [
                sum(simplex[i][d] for i in range(dim)) / dim for d in range(dim)
            ]

            # Reflection
            reflected = [centroid[d] + 1.0 * (centroid[d] - worst[d]) for d in range(dim)]
            f_ref = fn(reflected)

            if fn(best) <= f_ref < fn(second_worst):
                simplex[-1] = reflected
                continue

            # Expansion
            if f_ref < fn(best):
                expanded = [centroid[d] + 2.0 * (reflected[d] - centroid[d]) for d in range(dim)]
                if fn(expanded) < f_ref:
                    simplex[-1] = expanded
                else:
                    simplex[-1] = reflected
                continue

            # Contraction
            contracted = [centroid[d] + 0.5 * (worst[d] - centroid[d]) for d in range(dim)]
            if fn(contracted) < fn(worst):
                simplex[-1] = contracted
                continue

            # Shrink
            for i in range(1, dim + 1):
                simplex[i] = [best[d] + 0.5 * (simplex[i][d] - best[d]) for d in range(dim)]

        simplex.sort(key=lambda pt: fn(pt))
        opt_point = simplex[0]
        return {
            "optimal_point": [round(x, 4) for x in opt_point],
            "optimal_value": round(fn(opt_point), 6),
            "converged": True,
        }


def _resolve_spec(sim_or_name: Any, scope: Optional[Dict[str, Any]] = None) -> SimulationSpec:
    """Helper to resolve a SimulationSpec from an object, name, or execution scope."""
    if isinstance(sim_or_name, SimulationSpec):
        return sim_or_name
    if isinstance(sim_or_name, dict) and "_spec" in sim_or_name and isinstance(sim_or_name["_spec"], SimulationSpec):
        return sim_or_name["_spec"]
    if isinstance(sim_or_name, str) and scope:
        if f"_sim_spec_{sim_or_name}" in scope:
            return scope[f"_sim_spec_{sim_or_name}"]
        val = scope.get(sim_or_name)
        if isinstance(val, SimulationSpec):
            return val
        if isinstance(val, dict) and "_spec" in val and isinstance(val["_spec"], SimulationSpec):
            return val["_spec"]
    if scope:
        for v in scope.values():
            if isinstance(v, SimulationSpec):
                return v
            if isinstance(v, dict) and "_spec" in v and isinstance(v["_spec"], SimulationSpec):
                return v["_spec"]
    return SimulationSpec(name=str(sim_or_name) if sim_or_name else "default_sim")


def run_trials(
    sim_or_name: Any,
    trials: int = 100,
    seed: int = 42,
    scope: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Runs multiple stochastic replications of a simulation and computes uncertainty metrics."""
    spec = _resolve_spec(sim_or_name, scope)
    trial_runs = []
    waiting_time_means = []
    utilizations = []
    queue_length_means = []

    for i in range(trials):
        trial_seed = (seed + i * 37) if seed is not None else random.randint(1, 1000000)
        engine = DiscreteEventQueueEngine(spec, seed=trial_seed)
        res = engine.run()
        trial_runs.append(res)
        w_mean = res["summary"]["waiting_time"]["mean"]
        waiting_time_means.append(w_mean)
        utilizations.append(res["server_utilization"])
        q_mean = res["summary"]["queue_length"]["mean"]
        queue_length_means.append(q_mean)

    return {
        "trials": trials,
        "runs": trial_runs,
        "waiting_time_means": waiting_time_means,
        "utilizations": utilizations,
        "queue_length_means": queue_length_means,
        "uncertainty": {
            "waiting_time": summarize_uncertainty(waiting_time_means),
            "utilization": summarize_uncertainty(utilizations),
            "queue_length": summarize_uncertainty(queue_length_means),
        },
        "mean_waiting_time": round(sum(waiting_time_means) / trials, 4) if trials > 0 else 0.0,
        "mean_utilization": round(sum(utilizations) / trials, 4) if trials > 0 else 0.0,
    }


def sweep_parameter(
    sim_or_name: Any,
    param: str,
    values: List[Any],
    trials_per_value: int = 5,
    seed: int = 42,
    scope: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Sweeps a parameter across candidate values and records performance with uncertainty bounds."""
    spec = _resolve_spec(sim_or_name, scope)
    results = []

    for idx, val in enumerate(values):
        mod_spec = copy.deepcopy(spec)
        p_clean = param.lower().strip()
        if p_clean in ("servers", "server", "num_servers", "c"):
            mod_spec.servers = int(val)
        elif p_clean in ("arrival_rate", "arrivals", "arrival"):
            mod_spec.arrival_params["rate"] = float(val)
        elif p_clean in ("service_rate", "service"):
            mod_spec.service_params["rate"] = float(val)
        elif p_clean in ("duration", "events"):
            mod_spec.duration = int(val)
        else:
            if hasattr(mod_spec, p_clean):
                setattr(mod_spec, p_clean, val)

        run_res = run_trials(mod_spec, trials=trials_per_value, seed=seed + idx * 100, scope=scope)
        results.append({
            "param": param,
            "value": val,
            "mean_waiting_time": run_res["mean_waiting_time"],
            "mean_utilization": run_res["mean_utilization"],
            "uncertainty": run_res["uncertainty"],
        })
    return results


class SimRuntime(DomainRuntime):
    """Runtime engine for Simulation & Optimization domain."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if isinstance(ir, SimulationSpec):
            engine = DiscreteEventQueueEngine(ir)
            res = engine.run()
            # Bind metric series directly to scope for easy plotting / summarization
            scope["waiting_time"] = res["waiting_time"]
            scope["service_time"] = res["service_time"]
            scope["queue_length"] = res["queue_length"]
            scope[ir.name] = res
            scope[f"_sim_spec_{ir.name}"] = ir
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, TrialsSpec):
            res = run_trials(ir.sim_name, trials=ir.trials, seed=ir.seed, scope=scope)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, SweepSpec):
            res = sweep_parameter(
                ir.sim_name,
                ir.param_name,
                ir.values,
                trials_per_value=ir.trials_per_val,
                seed=ir.seed,
                scope=scope,
            )
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, OptimizationSpec):
            return self.execute_optimization(ir, scope)
        raise TypeError(f"Unknown Sim IR: {type(ir).__name__}")

    def execute_optimization(self, spec: OptimizationSpec, scope: Dict[str, Any]) -> Dict[str, Any]:
        fn = scope.get(spec.objective)
        if not callable(fn):
            raise ValueError(f"Objective function '{spec.objective}' not found or not callable")

        optimizer = NelderMeadOptimizer(tol=spec.tolerance, max_iter=spec.max_iterations)
        res = optimizer.minimize(fn, spec.initial_guess)
        if spec.target_var:
            scope[spec.target_var] = res
        return res

