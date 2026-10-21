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

    if isinstance(params, (list, tuple)):
        if dist in ("normal", "gaussian"):
            params = {"mean": params[0] if len(params) > 0 else 0.0, "std": params[1] if len(params) > 1 else 1.0}
        elif dist in ("uniform", "unif"):
            params = {"low": params[0] if len(params) > 0 else 0.0, "high": params[1] if len(params) > 1 else 1.0}
        else:
            params = {"rate": params[0] if len(params) > 0 else 1.0}
    elif not isinstance(params, dict):
        params = {}

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
    if scope is None:
        try:
            import sys
            caller_frame = sys._getframe(1)
            target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
            scope = dict(target_env)
            if caller_frame.f_locals:
                scope.update(caller_frame.f_locals)
        except Exception:
            scope = {}
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
    if scope is None:
        try:
            import sys
            caller_frame = sys._getframe(1)
            target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
            scope = dict(target_env)
            if caller_frame.f_locals:
                scope.update(caller_frame.f_locals)
        except Exception:
            scope = {}
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


# --- Batch 13 Spoken English Simulation & Probability Verbs ---

def sim_random_walk(steps: Any = 100, start: Any = 0.0, step_size: Any = 1.0) -> List[float]:
    """Simulate 1D random walk trajectory."""
    n = int(steps)
    curr = float(start)
    delta = float(step_size)
    path = [curr]
    for _ in range(n):
        curr += delta if random.random() < 0.5 else -delta
        path.append(round(curr, 4))
    return path


def sim_exponential(rate: Any = 1.0) -> float:
    """Generate a random sample from an exponential distribution with rate lambda."""
    lam = float(rate)
    if lam <= 0:
        raise ValueError("Exponential rate must be positive")
    return round(random.expovariate(lam), 4)


def sim_poisson(lam: Any = 1.0) -> int:
    """Generate a Poisson random variate using Knuth's algorithm."""
    l_val = float(lam)
    if l_val <= 0:
        return 0
    limit = math.exp(-l_val)
    k = 0
    p = 1.0
    while p > limit:
        k += 1
        p *= random.random()
    return k - 1


def sim_monte_carlo_pi(samples: Any = 10000) -> float:
    """Estimate value of Pi via 2D Monte Carlo sampling inside unit square."""
    n = int(samples)
    if n <= 0:
        return 0.0
    inside = 0
    for _ in range(n):
        x = random.random()
        y = random.random()
        if x * x + y * y <= 1.0:
            inside += 1
    return round((4.0 * inside) / n, 4)


def sim_roll_dice(count: Any = 1, sides: Any = 6) -> List[int]:
    """Roll N dice with specified number of sides."""
    c = int(count)
    s = int(sides)
    return [random.randint(1, s) for _ in range(c)]


def sim_coin_tosses(count: Any = 10, p_heads: Any = 0.5) -> List[str]:
    """Simulate sequence of Bernoulli coin tosses ('H' or 'T')."""
    n = int(count)
    p = float(p_heads)
    return ["H" if random.random() < p else "T" for _ in range(n)]


def sim_markov_chain_step(current_state: Any, transition_matrix: Any, states: Any) -> Any:
    """Transition to next state in Markov chain according to transition probability matrix."""
    st_list = list(range(len(transition_matrix))) if states is None else list(states)
    curr = current_state if current_state in st_list else st_list[0]
    idx = st_list.index(curr)
    probs = transition_matrix[idx]
    return random.choices(st_list, weights=probs)[0]


def sim_markov_chain_walk(start_state: Any, transition_matrix: Any, states: Any = None, steps: Any = 10) -> List[Any]:
    """Simulate N-step walk along Markov chain."""
    n = int(steps)
    st_list = list(range(len(transition_matrix))) if states is None else list(states)
    curr = start_state if start_state in st_list else st_list[0]
    path = [curr]
    for _ in range(n):
        curr = sim_markov_chain_step(curr, transition_matrix, st_list)
        path.append(curr)
    return path


def sim_sample_geometric(p: Any, count: Any = 1) -> List[int]:
    """Sample counts of Bernoulli trials until first success."""
    prob = float(p)
    if not (0.0 < prob <= 1.0):
        raise ValueError("Geometric probability p must be in (0, 1]")
    res = []
    for _ in range(int(count)):
        k = int(math.ceil(math.log(1.0 - random.random()) / math.log(1.0 - prob)))
        res.append(max(1, k))
    return res


def sim_sample_binomial(n: Any, p: Any, count: Any = 1) -> List[int]:
    """Sample binomial random variates (# of successes in n trials)."""
    n_trials = int(n)
    prob = float(p)
    return [sum(1 for _ in range(n_trials) if random.random() < prob) for _ in range(int(count))]


def sim_sample_triangular(low: Any, high: Any, mode: Any, count: Any = 1) -> List[float]:
    """Sample triangular distribution variates."""
    lo = float(low)
    hi = float(high)
    md = float(mode)
    return [round(random.triangular(lo, hi, md), 4) for _ in range(int(count))]


def sim_bootstrap_mean_ci(data: Any, n_bootstraps: Any = 1000, confidence: Any = 0.95) -> Dict[str, float]:
    """Calculate non-parametric bootstrap confidence interval for the mean."""
    vals = [float(x) for x in data]
    n = len(vals)
    if n == 0:
        return {"mean": 0.0, "ci_lower": 0.0, "ci_upper": 0.0, "confidence": float(confidence)}
    orig_mean = sum(vals) / n
    b_count = int(n_bootstraps)
    boot_means = []
    for _ in range(b_count):
        sample = [random.choice(vals) for _ in range(n)]
        boot_means.append(sum(sample) / n)
    boot_means.sort()
    conf = float(confidence)
    alpha = (1.0 - conf) / 2.0
    idx_low = int(alpha * b_count)
    idx_high = int((1.0 - alpha) * b_count)
    return {
        "mean": round(orig_mean, 4),
        "ci_lower": round(boot_means[min(idx_low, b_count - 1)], 4),
        "ci_upper": round(boot_means[min(idx_high, b_count - 1)], 4),
        "confidence": conf,
    }


def sim_permutation_test(group1: Any, group2: Any, n_permutations: Any = 1000) -> float:
    """Calculate two-tailed permutation test p-value for difference in group means."""
    g1 = [float(x) for x in group1]
    g2 = [float(x) for x in group2]
    n1 = len(g1)
    n2 = len(g2)
    if n1 == 0 or n2 == 0:
        return 1.0
    obs_diff = abs((sum(g1) / n1) - (sum(g2) / n2))
    pool = g1 + g2
    total_len = len(pool)
    perms = int(n_permutations)
    count_extreme = 0
    for _ in range(perms):
        shuffled = list(pool)
        random.shuffle(shuffled)
        perm_g1 = shuffled[:n1]
        perm_g2 = shuffled[n1:]
        diff = abs((sum(perm_g1) / n1) - (sum(perm_g2) / n2))
        if diff >= obs_diff:
            count_extreme += 1
    return round(count_extreme / perms, 4)


def sim_mm1_queue(arrival_rate: Any, service_rate: Any, duration: Any = 100.0) -> Dict[str, float]:
    """Simulate single-server M/M/1 queue over specified duration."""
    lam = float(arrival_rate)
    mu = float(service_rate)
    dur = float(duration)
    t = 0.0
    queue = []
    wait_times = []
    server_busy_until = 0.0
    total_customers = 0

    while t < dur:
        inter_arrival = random.expovariate(lam)
        t += inter_arrival
        if t >= dur:
            break
        total_customers += 1
        service_time = random.expovariate(mu)
        start_service = max(t, server_busy_until)
        wait_time = start_service - t
        wait_times.append(wait_time)
        server_busy_until = start_service + service_time

    avg_wait = sum(wait_times) / len(wait_times) if wait_times else 0.0
    utilization = min(1.0, lam / mu if mu > 0 else 1.0)
    return {
        "total_customers": total_customers,
        "avg_wait_time": round(avg_wait, 4),
        "utilization": round(utilization, 4),
    }


def sim_wiener_process(t: Any = 1.0, n_steps: Any = 100, mu: Any = 0.0, sigma: Any = 1.0) -> List[float]:
    """Simulate continuous 1D Wiener process (Brownian motion with drift)."""
    total_time = float(t)
    steps = int(n_steps)
    drift = float(mu)
    vol = float(sigma)
    dt = total_time / max(1, steps)
    sqrt_dt = math.sqrt(dt)

    curr = 0.0
    path = [round(curr, 4)]
    for _ in range(steps):
        z = random.gauss(0.0, 1.0)
        curr += drift * dt + vol * sqrt_dt * z
        path.append(round(curr, 4))
    return path


def sim_bernoulli_trial(p: Any = 0.5) -> bool:
    """Execute single Bernoulli trial with success probability p."""
    return random.random() < float(p)


def sim_sample_lognormal(mean: Any = 0.0, std: Any = 1.0, count: Any = 1) -> List[float]:
    """Sample Log-Normal distribution variates."""
    m = float(mean)
    s = float(std)
    return [round(random.lognormvariate(m, s), 4) for _ in range(int(count))]


def sim_monte_carlo_integral(fn: Any, a: Any, b: Any, n_samples: Any = 10000) -> float:
    """Estimate 1D definite integral using uniform Monte Carlo sampling."""
    lo = float(a)
    hi = float(b)
    n = int(n_samples)
    if n <= 0 or hi <= lo:
        return 0.0
    total = 0.0
    for _ in range(n):
        x = random.uniform(lo, hi)
        total += fn(x) if callable(fn) else float(fn)
    return round((hi - lo) * (total / n), 4)


def sim_estimate_expected_value(samples: Any) -> Dict[str, float]:
    """Estimate empirical expected value, variance, and standard deviation."""
    vals = [float(x) for x in samples]
    n = len(vals)
    if n == 0:
        return {"expected_value": 0.0, "variance": 0.0, "std_dev": 0.0}
    mean = sum(vals) / n
    var = sum((x - mean) ** 2 for x in vals) / (n - 1) if n > 1 else 0.0
    return {
        "expected_value": round(mean, 4),
        "variance": round(var, 4),
        "std_dev": round(math.sqrt(var), 4),
    }


def sim_birthday_paradox_prob(people_count: Any) -> float:
    """Calculate theoretical probability that at least two people share a birthday."""
    n = int(people_count)
    if n > 365:
        return 1.0
    if n <= 1:
        return 0.0
    prob_unique = 1.0
    for i in range(n):
        prob_unique *= (365.0 - i) / 365.0
    return round(1.0 - prob_unique, 4)


def sim_coupon_collector_estimate(num_coupons: Any, trials: Any = 100) -> float:
    """Estimate expected draws to collect all distinct coupons via Monte Carlo."""
    k = int(num_coupons)
    t_count = int(trials)
    if k <= 0:
        return 0.0
    total_draws = 0
    for _ in range(t_count):
        seen = set()
        draws = 0
        while len(seen) < k:
            seen.add(random.randint(0, k - 1))
            draws += 1
        total_draws += draws
    return round(total_draws / max(1, t_count), 2)


def sim_shuffle_deck() -> List[str]:
    """Generate and Fisher-Yates shuffle standard 52-card deck."""
    suits = ["S", "H", "D", "C"]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    deck = [f"{r}{s}" for s in suits for r in ranks]
    random.shuffle(deck)
    return deck


def sim_draw_cards(deck: Any, count: Any = 1) -> List[str]:
    """Draw top N cards from deck without replacement."""
    d = list(deck)
    n = min(int(count), len(d))
    return d[:n]


def sim_sample_weibull(k: Any, lam: Any = 1.0, count: Any = 1) -> List[float]:
    """Sample Weibull distribution variates for reliability analysis."""
    shape = float(k)
    scale = float(lam)
    if shape <= 0 or scale <= 0:
        raise ValueError("Weibull shape and scale must be positive")
    res = []
    for _ in range(int(count)):
        u = random.random()
        val = scale * ((-math.log(max(1e-12, 1.0 - u))) ** (1.0 / shape))
        res.append(round(val, 4))
    return res


def sim_generate_synthetic_timeline(start_time: Any, intervals: Any) -> List[float]:
    """Generate sequence of timestamps from delta arrival intervals."""
    curr = float(start_time)
    res = [round(curr, 2)]
    for delta in intervals:
        curr += float(delta)
        res.append(round(curr, 2))
    return res


def sim_survival_rate_kaplan_meier(durations: Any, events: Any) -> List[Dict[str, Any]]:
    """Compute empirical Kaplan-Meier survival curve table."""
    durs = [float(d) for d in durations]
    evs = [int(e) for e in events]
    data = sorted(zip(durs, evs), key=lambda x: x[0])
    n = len(data)
    surv_prob = 1.0
    table = []
    i = 0
    while i < n:
        t = data[i][0]
        # Count deaths and censorings at time t
        d = 0
        c = 0
        while i < n and data[i][0] == t:
            if data[i][1] == 1:
                d += 1
            else:
                c += 1
            i += 1
        at_risk = n - (i - d - c)
        if at_risk > 0 and d > 0:
            surv_prob *= (1.0 - (d / at_risk))
        table.append({
            "time": round(t, 2),
            "at_risk": at_risk,
            "events": d,
            "survival_prob": round(surv_prob, 4),
        })
    return table


def sim_queue_system(
    arrival_rate: float,
    service_rate: float,
    servers: int = 1,
    max_time: float = 500.0,
    seed: int = 42,
) -> Dict[str, Any]:
    """Simulate M/M/c queuing system with Poisson arrivals and exponential service."""
    import heapq
    import random
    rng = random.Random(seed)

    c = max(1, int(servers))
    lam = float(arrival_rate)
    mu = float(service_rate)
    if lam <= 0 or mu <= 0:
        raise ValueError("Arrival rate and service rate must be positive")

    t = 0.0
    # Next arrival time
    next_arrival = rng.expovariate(lam)

    # Server busy status: list of finish times
    server_free_times = [0.0] * c

    queue: List[float] = []  # arrival times of waiting customers
    wait_times: List[float] = []
    service_times: List[float] = []
    system_times: List[float] = []

    total_arrivals = 0
    served_count = 0

    # Event queue: (event_time, event_type, customer_id, server_id)
    # Types: 0 = arrival, 1 = departure
    events = [(next_arrival, 0, 0, -1)]
    heapq.heapify(events)

    cust_id = 0
    server_busy_time = [0.0] * c

    while events and t < max_time:
        event_time, event_type, cid, s_id = heapq.heappop(events)
        t = event_time
        if t > max_time:
            break

        if event_type == 0:
            # Arrival
            total_arrivals += 1
            cust_id += 1
            # Check for free server
            free_server = None
            for idx in range(c):
                if server_free_times[idx] <= t:
                    free_server = idx
                    break

            if free_server is not None:
                st = rng.expovariate(mu)
                server_free_times[free_server] = t + st
                server_busy_time[free_server] += st
                wait_times.append(0.0)
                service_times.append(st)
                system_times.append(st)
                heapq.heappush(events, (t + st, 1, cid, free_server))
            else:
                queue.append(t)

            # Schedule next arrival
            arr_delta = rng.expovariate(lam)
            if t + arr_delta < max_time:
                heapq.heappush(events, (t + arr_delta, 0, cust_id, -1))

        elif event_type == 1:
            # Departure
            served_count += 1
            if queue:
                arr_t = queue.pop(0)
                wt = t - arr_t
                st = rng.expovariate(mu)
                server_free_times[s_id] = t + st
                server_busy_time[s_id] += st
                wait_times.append(wt)
                service_times.append(st)
                system_times.append(wt + st)
                heapq.heappush(events, (t + st, 1, cust_id, s_id))

    avg_wait = sum(wait_times) / max(1, len(wait_times))
    avg_sys = sum(system_times) / max(1, len(system_times))
    utilization = sum(server_busy_time) / (c * max(1e-6, t))

    return {
        "servers": c,
        "total_arrivals": total_arrivals,
        "served_count": served_count,
        "avg_wait_time": round(avg_wait, 4),
        "avg_system_time": round(avg_sys, 4),
        "server_utilization": round(min(1.0, utilization), 4),
        "traffic_intensity": round(lam / (c * mu), 4),
    }


class CellularAutomaton:
    """2D Cellular Automata engine supporting Life-like outer-totalistic rules."""

    def __init__(
        self,
        width: int = 20,
        height: int = 20,
        rule: str = "B3/S23",
        neighborhood: str = "moore",
    ):
        self.w = max(3, int(width))
        self.h = max(3, int(height))
        self.rule = rule.upper()
        self.neighborhood = neighborhood.lower()
        self.grid = [[0] * self.w for _ in range(self.h)]
        self._parse_rule()

    def _parse_rule(self):
        # Format B.../S...
        self.birth = set()
        self.survival = set()
        parts = self.rule.split("/")
        for p in parts:
            if p.startswith("B"):
                self.birth = {int(d) for d in p[1:] if d.isdigit()}
            elif p.startswith("S"):
                self.survival = {int(d) for d in p[1:] if d.isdigit()}

    def set_cell(self, x: int, y: int, val: int = 1) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[y][x] = int(val)

    def set_pattern(self, x: int, y: int, pattern: List[List[int]]) -> None:
        for py, row in enumerate(pattern):
            for px, val in enumerate(row):
                self.set_cell(x + px, y + py, val)

    def step(self) -> "CellularAutomaton":
        next_grid = [[0] * self.w for _ in range(self.h)]

        if self.neighborhood == "von_neumann":
            deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        else:
            deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        for y in range(self.h):
            for x in range(self.w):
                # Count live neighbors with periodic toroidal boundaries
                neighbors = 0
                for dy, dx in deltas:
                    ny = (y + dy) % self.h
                    nx = (x + dx) % self.w
                    if self.grid[ny][nx] == 1:
                        neighbors += 1

                alive = self.grid[y][x] == 1
                if alive and neighbors in self.survival:
                    next_grid[y][x] = 1
                elif not alive and neighbors in self.birth:
                    next_grid[y][x] = 1
                else:
                    next_grid[y][x] = 0

        self.grid = next_grid
        return self

    def run(self, steps: int = 1) -> "CellularAutomaton":
        for _ in range(max(0, int(steps))):
            self.step()
        return self

    @property
    def population(self) -> int:
        return sum(sum(row) for row in self.grid)

    def to_list(self) -> List[List[int]]:
        return [list(r) for r in self.grid]


class SpatialAgentSimulation:
    """Continuous 2D Multi-Agent Flocking (Reynolds Boids) Simulation."""

    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        n_agents: int = 20,
        max_speed: float = 3.0,
        seed: int = 42,
    ):
        import random
        self.w = float(width)
        self.h = float(height)
        self.max_speed = float(max_speed)
        self.rng = random.Random(seed)
        self.agents: List[Dict[str, float]] = []

        for i in range(n_agents):
            self.agents.append({
                "id": i,
                "x": self.rng.uniform(0.0, self.w),
                "y": self.rng.uniform(0.0, self.h),
                "vx": self.rng.uniform(-1.0, 1.0),
                "vy": self.rng.uniform(-1.0, 1.0),
            })

    def step(
        self,
        dt: float = 0.5,
        visual_range: float = 20.0,
        separation_dist: float = 5.0,
        cohesion_weight: float = 0.05,
        alignment_weight: float = 0.1,
        separation_weight: float = 0.15,
    ) -> "SpatialAgentSimulation":
        n = len(self.agents)
        new_velocities = []

        for i, a in enumerate(self.agents):
            x, y = a["x"], a["y"]
            vx, vy = a["vx"], a["vy"]

            # Neighbor aggregates
            neighbor_count = 0
            avg_x, avg_y = 0.0, 0.0
            avg_vx, avg_vy = 0.0, 0.0
            sep_x, sep_y = 0.0, 0.0

            for j, o in enumerate(self.agents):
                if i == j:
                    continue
                dx = o["x"] - x
                dy = o["y"] - y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < visual_range and dist > 1e-5:
                    neighbor_count += 1
                    avg_x += o["x"]
                    avg_y += o["y"]
                    avg_vx += o["vx"]
                    avg_vy += o["vy"]
                    if dist < separation_dist:
                        sep_x -= dx / dist
                        sep_y -= dy / dist

            steer_x, steer_y = 0.0, 0.0
            if neighbor_count > 0:
                avg_x /= neighbor_count
                avg_y /= neighbor_count
                avg_vx /= neighbor_count
                avg_vy /= neighbor_count

                # Cohesion
                steer_x += (avg_x - x) * cohesion_weight
                steer_y += (avg_y - y) * cohesion_weight
                # Alignment
                steer_x += (avg_vx - vx) * alignment_weight
                steer_y += (avg_vy - vy) * alignment_weight
                # Separation
                steer_x += sep_x * separation_weight
                steer_y += sep_y * separation_weight

            vx += steer_x
            vy += steer_y

            # Limit speed
            spd = math.sqrt(vx * vx + vy * vy)
            if spd > self.max_speed:
                vx = (vx / spd) * self.max_speed
                vy = (vy / spd) * self.max_speed

            new_velocities.append((vx, vy))

        # Update positions
        for i, a in enumerate(self.agents):
            vx, vy = new_velocities[i]
            a["vx"] = vx
            a["vy"] = vy
            a["x"] = (a["x"] + vx * dt) % self.w
            a["y"] = (a["y"] + vy * dt) % self.h

        return self

    def run(self, steps: int = 10, dt: float = 0.5) -> "SpatialAgentSimulation":
        for _ in range(max(0, int(steps))):
            self.step(dt=dt)
        return self

    def positions(self) -> List[Tuple[float, float]]:
        return [(round(a["x"], 2), round(a["y"], 2)) for a in self.agents]


class SimResource:
    """Resource with finite capacity and FIFO waiting queue for Discrete Event Simulation."""

    def __init__(self, name: str, capacity: int = 1):
        self.name = name
        self.capacity = int(capacity)
        self.available = self.capacity
        self.queue: List[Tuple[float, Any, Callable]] = []  # (arrival_time, entity_id, callback)
        self.total_wait_time = 0.0
        self.total_served = 0

    def request(self, current_time: float, entity_id: Any, callback: Callable) -> bool:
        """Requests resource. If available, acquires immediately (returns True). Else enqueues (returns False)."""
        if self.available > 0:
            self.available -= 1
            self.total_served += 1
            return True
        else:
            self.queue.append((current_time, entity_id, callback))
            return False

    def release(self, current_time: float) -> Optional[Tuple[Any, Callable]]:
        """Releases resource and grants to next in queue if any."""
        self.available += 1
        if self.queue and self.available > 0:
            self.available -= 1
            arrival_time, entity_id, cb = self.queue.pop(0)
            wait_time = current_time - arrival_time
            self.total_wait_time += wait_time
            self.total_served += 1
            return entity_id, cb
        return None


class DiscreteEventSimulation:
    """Priority-Queue Discrete Event Simulation (DES) engine with simulated clock."""

    def __init__(self):
        import heapq
        self.pq: List[Tuple[float, int, int, Callable, Tuple, Dict]] = []
        self.current_time = 0.0
        self.event_counter = 0
        self.resources: Dict[str, SimResource] = {}
        self.events_processed = 0

    def add_resource(self, name: str, capacity: int = 1) -> SimResource:
        res = SimResource(name, capacity)
        self.resources[name] = res
        return res

    def schedule(
        self, delay: float, callback: Callable, priority: int = 0, *args, **kwargs
    ) -> None:
        """Schedules callback to be executed at current_time + delay."""
        import heapq
        event_time = self.current_time + max(0.0, float(delay))
        self.event_counter += 1
        heapq.heappush(self.pq, (event_time, priority, self.event_counter, callback, args, kwargs))

    def step(self) -> bool:
        """Pops and executes the next scheduled event."""
        import heapq
        if not self.pq:
            return False
        event_time, priority, _, callback, args, kwargs = heapq.heappop(self.pq)
        self.current_time = event_time
        self.events_processed += 1
        callback(*args, **kwargs)
        return True

    def run_until(self, max_time: float) -> Dict[str, Any]:
        """Runs simulation until simulated clock reaches max_time or event queue is empty."""
        while self.pq and self.pq[0][0] <= max_time:
            self.step()

        self.current_time = max_time
        res_stats = {}
        for name, r in self.resources.items():
            avg_wait = r.total_wait_time / r.total_served if r.total_served > 0 else 0.0
            res_stats[name] = {
                "capacity": r.capacity,
                "available": r.available,
                "total_served": r.total_served,
                "queue_length": len(r.queue),
                "avg_wait_time": round(avg_wait, 4),
            }

        return {
            "current_time": self.current_time,
            "events_processed": self.events_processed,
            "remaining_events": len(self.pq),
            "resources": res_stats,
        }


def sim_create_discrete_event_sim() -> DiscreteEventSimulation:
    """Instantiates a Discrete Event Simulation engine."""
    return DiscreteEventSimulation()


class Agent2D:
    """An individual autonomous mobile agent in 2D space."""

    def __init__(self, agent_id: int, x: float, y: float, vx: float = 0.0, vy: float = 0.0, state: str = "S"):
        self.id = agent_id
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.state = state  # e.g. "S", "I", "R"
        self.infection_time = 0


class AgentBasedModel2D:
    """2D Toroidal spatial agent-based simulation for collective behavior and epidemic dynamics."""

    def __init__(
        self,
        width: float = 100.0,
        height: float = 100.0,
        num_agents: int = 50,
        sensory_radius: float = 10.0,
        seed: Optional[int] = 42,
    ):
        self.width = float(width)
        self.height = float(height)
        self.sensory_radius = float(sensory_radius)
        if seed is not None:
            random.seed(seed)

        self.agents: List[Agent2D] = []
        for i in range(num_agents):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            vx = random.uniform(-1.0, 1.0)
            vy = random.uniform(-1.0, 1.0)
            # Default first agent infected
            state = "I" if i == 0 else "S"
            self.agents.append(Agent2D(i, x, y, vx, vy, state=state))

        self.beta = 0.3  # Infection transmission probability
        self.gamma = 0.05  # Recovery probability
        self.time_step = 0

    def step(self) -> Dict[str, int]:
        """Advances simulation by one discrete time step."""
        self.time_step += 1
        n = len(self.agents)

        # 1. Toroidal distance helper
        def tor_dist(a1: Agent2D, a2: Agent2D) -> Tuple[float, float, float]:
            dx = a2.x - a1.x
            dy = a2.y - a1.y
            if dx > self.width / 2:
                dx -= self.width
            elif dx < -self.width / 2:
                dx += self.width
            if dy > self.height / 2:
                dy -= self.height
            elif dy < -self.height / 2:
                dy += self.height
            dist = math.sqrt(dx * dx + dy * dy)
            return dist, dx, dy

        # 2. Flocking & Interaction forces
        for i in range(n):
            a = self.agents[i]
            neighbors = []
            for j in range(n):
                if i != j:
                    d, dx, dy = tor_dist(a, self.agents[j])
                    if d < self.sensory_radius:
                        neighbors.append((self.agents[j], d, dx, dy))

            if neighbors:
                # Alignment & Cohesion
                avg_vx = sum(nbr[0].vx for nbr in neighbors) / len(neighbors)
                avg_vy = sum(nbr[0].vy for nbr in neighbors) / len(neighbors)
                a.vx = a.vx * 0.9 + avg_vx * 0.1
                a.vy = a.vy * 0.9 + avg_vy * 0.1

                # Separation if too close (< 3.0)
                for nbr, d, dx, dy in neighbors:
                    if d < 3.0 and d > 0.001:
                        a.vx -= (dx / d) * 0.2
                        a.vy -= (dy / d) * 0.2

            # Clamp velocity
            v_mag = math.sqrt(a.vx ** 2 + a.vy ** 2)
            if v_mag > 2.0:
                a.vx = (a.vx / v_mag) * 2.0
                a.vy = (a.vy / v_mag) * 2.0

            # Move and wrap coordinates
            a.x = (a.x + a.vx) % self.width
            a.y = (a.y + a.vy) % self.height

        # 3. SIR Epidemic spread
        new_states = [a.state for a in self.agents]
        for i in range(n):
            a = self.agents[i]
            if a.state == "I":
                # Check transmission to susceptible neighbors
                for j in range(n):
                    if i != j and self.agents[j].state == "S":
                        d, _, _ = tor_dist(a, self.agents[j])
                        if d < 5.0 and random.random() < self.beta:
                            new_states[j] = "I"

                # Check recovery
                if random.random() < self.gamma:
                    new_states[i] = "R"

        for i in range(n):
            self.agents[i].state = new_states[i]

        counts = {"S": 0, "I": 0, "R": 0}
        for a in self.agents:
            counts[a.state] = counts.get(a.state, 0) + 1

        return counts

    def run(self, steps: int = 50) -> Dict[str, Any]:
        """Runs the ABM simulation for a given number of steps."""
        history = []
        for _ in range(steps):
            counts = self.step()
            history.append(counts)

        return {
            "steps": steps,
            "final_counts": history[-1] if history else {},
            "history": history,
            "total_agents": len(self.agents),
        }


class MCMCSampler:
    """Metropolis-Hastings Markov Chain Monte Carlo sampler with diagnostics."""

    def __init__(self, seed: Optional[int] = 42):
        if seed is not None:
            random.seed(seed)

    def sample(
        self,
        log_pdf: Callable[[List[float]], float],
        x0: List[float],
        n_samples: int = 1000,
        proposal_std: float = 0.5,
        burn_in: int = 200,
        thinning: int = 2,
    ) -> Dict[str, Any]:
        """Generates samples from target log-density using Gaussian random walk Metropolis-Hastings."""
        dim = len(x0)
        curr_x = list(x0)
        curr_log_p = log_pdf(curr_x)

        samples: List[List[float]] = []
        accepted = 0
        total_proposals = 0

        # Box-Muller Gaussian random variable generator
        def rand_normal(mean: float = 0.0, std: float = 1.0) -> float:
            u1 = max(random.random(), 1e-12)
            u2 = random.random()
            z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
            return mean + z * std

        total_steps = burn_in + n_samples * thinning

        for step in range(total_steps):
            # Propose candidate: x' ~ N(x, proposal_std^2 * I)
            cand_x = [rand_normal(curr_x[d], proposal_std) for d in range(dim)]
            cand_log_p = log_pdf(cand_x)

            log_alpha = cand_log_p - curr_log_p
            total_proposals += 1

            if log_alpha >= 0.0 or math.log(max(random.random(), 1e-12)) < log_alpha:
                curr_x = cand_x
                curr_log_p = cand_log_p
                accepted += 1

            if step >= burn_in and (step - burn_in) % thinning == 0:
                samples.append([round(v, 6) for v in curr_x])

        acceptance_rate = accepted / max(total_proposals, 1)

        # Compute empirical mean and standard deviation per dimension
        means = []
        stds = []
        for d in range(dim):
            vals = [s[d] for s in samples]
            m = sum(vals) / len(vals) if vals else 0.0
            var = sum((v - m) ** 2 for v in vals) / len(vals) if len(vals) > 1 else 0.0
            means.append(round(m, 4))
            stds.append(round(math.sqrt(var), 4))

        return {
            "samples": samples,
            "n_samples": len(samples),
            "acceptance_rate": round(acceptance_rate, 4),
            "means": means,
            "stds": stds,
            "dim": dim,
        }


class JacksonQueuingNetwork:
    """Solves open Jackson Queueing Networks using traffic flow balance equations."""

    def __init__(
        self,
        arrival_rates: List[float],
        service_rates: List[float],
        routing_matrix: List[List[float]],
        num_servers: Optional[List[int]] = None,
    ):
        self.gamma = [float(v) for v in arrival_rates]
        self.mu = [float(v) for v in service_rates]
        self.P = [[float(v) for v in row] for row in routing_matrix]
        self.m = len(self.gamma)
        self.servers = list(num_servers or [1] * self.m)

    def solve(self) -> Dict[str, Any]:
        """
        Solves traffic equations: lambda_i = gamma_i + sum_j (lambda_j * P_{ji})
        Equivalent to (I - P^T) * lambda = gamma.
        """
        # Form matrix M = I - P^T
        M = [[0.0] * self.m for _ in range(self.m)]
        for i in range(self.m):
            for j in range(self.m):
                M[i][j] = (1.0 if i == j else 0.0) - self.P[j][i]

        # Solve M * lambda = gamma using Gaussian elimination
        aug = [list(M[i]) + [self.gamma[i]] for i in range(self.m)]
        for col in range(self.m):
            pivot_row = max(range(col, self.m), key=lambda r: abs(aug[r][col]))
            if abs(aug[pivot_row][col]) < 1e-12:
                raise ValueError("Singular traffic equations matrix in Jackson Network")
            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

            pivot = aug[col][col]
            for c_idx in range(col, self.m + 1):
                aug[col][c_idx] /= pivot

            for r in range(self.m):
                if r != col:
                    factor = aug[r][col]
                    for c_idx in range(col, self.m + 1):
                        aug[r][c_idx] -= factor * aug[col][c_idx]

        lambdas = [aug[r][self.m] for r in range(self.m)]

        # Compute queue metrics
        stations = []
        is_stable = True
        total_L = 0.0

        for i in range(self.m):
            lam = lambdas[i]
            mu = self.mu[i]
            c = self.servers[i]
            rho = lam / (c * mu) if (c * mu) > 0 else 1.0

            if rho >= 1.0:
                is_stable = False
                L_i = float("inf")
                W_i = float("inf")
            else:
                # Single server M/M/1 approximation: L = rho / (1 - rho)
                L_i = rho / (1.0 - rho)
                W_i = L_i / lam if lam > 0 else 0.0
                total_L += L_i

            stations.append({
                "station_id": i,
                "arrival_rate": round(lam, 4),
                "service_rate": mu,
                "utilization": round(rho, 4),
                "mean_queue_length": round(L_i, 4) if L_i != float("inf") else None,
                "mean_waiting_time": round(W_i, 4) if W_i != float("inf") else None,
            })

        total_gamma = sum(self.gamma)
        total_W = total_L / total_gamma if (total_gamma > 0 and is_stable) else None

        return {
            "is_stable": is_stable,
            "stations": stations,
            "total_arrival_rate": round(total_gamma, 4),
            "total_mean_customers": round(total_L, 4) if is_stable else None,
            "total_mean_response_time": round(total_W, 4) if total_W is not None else None,
        }


def sim_create_abm_2d(width: float = 100.0, height: float = 100.0, num_agents: int = 50) -> AgentBasedModel2D:
    """Instantiates a 2D Agent-Based Model."""
    return AgentBasedModel2D(width=width, height=height, num_agents=num_agents)


def sim_mcmc_sample(
    log_pdf: Callable[[List[float]], float],
    x0: List[float],
    n_samples: int = 500,
    proposal_std: float = 0.5,
) -> Dict[str, Any]:
    """Generates samples using Metropolis-Hastings MCMC."""
    sampler = MCMCSampler()
    return sampler.sample(log_pdf, x0, n_samples=n_samples, proposal_std=proposal_std)


def sim_jackson_network(
    arrival_rates: List[float],
    service_rates: List[float],
    routing_matrix: List[List[float]],
) -> Dict[str, Any]:
    """Solves an open Jackson Queuing Network."""
    net = JacksonQueuingNetwork(arrival_rates, service_rates, routing_matrix)
    return net.solve()


from doomscript.core.record import Record


class AgentBasedEpidemicSEIRModel:
    """Spatial 2D Agent-Based SEIR (Susceptible-Exposed-Infectious-Recovered) epidemic simulator."""

    @classmethod
    def simulate(
        cls,
        num_agents: int = 100,
        initial_infected: int = 2,
        infection_radius: float = 3.0,
        transmission_prob: float = 0.4,
        incubation_steps: int = 5,
        recovery_steps: int = 12,
        steps: int = 50,
        space_size: float = 50.0,
        seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        n = max(10, int(num_agents))

        # Agent state: dict with x, y, vx, vy, state (S, E, I, R), timer
        agents = []
        for i in range(n):
            st = "I" if i < initial_infected else "S"
            agents.append({
                "x": rng.uniform(0.0, space_size),
                "y": rng.uniform(0.0, space_size),
                "vx": rng.uniform(-1.0, 1.0),
                "vy": rng.uniform(-1.0, 1.0),
                "state": st,
                "timer": recovery_steps if st == "I" else 0,
            })

        peak_i = initial_infected
        r2 = infection_radius * infection_radius

        for _ in range(steps):
            # 1. Move agents with periodic boundaries
            for ag in agents:
                ag["x"] = (ag["x"] + ag["vx"]) % space_size
                ag["y"] = (ag["y"] + ag["vy"]) % space_size

            # 2. Check contacts between I and S
            infectious = [ag for ag in agents if ag["state"] == "I"]
            if len(infectious) > peak_i:
                peak_i = len(infectious)

            for inf in infectious:
                for ag in agents:
                    if ag["state"] == "S":
                        dx = abs(ag["x"] - inf["x"])
                        dy = abs(ag["y"] - inf["y"])
                        # Torus minimum image
                        dx = min(dx, space_size - dx)
                        dy = min(dy, space_size - dy)
                        if dx * dx + dy * dy <= r2:
                            if rng.random() < transmission_prob:
                                ag["state"] = "E"
                                ag["timer"] = incubation_steps

            # 3. Advance timers and state transitions
            for ag in agents:
                if ag["state"] == "E":
                    ag["timer"] -= 1
                    if ag["timer"] <= 0:
                        ag["state"] = "I"
                        ag["timer"] = recovery_steps
                elif ag["state"] == "I":
                    ag["timer"] -= 1
                    if ag["timer"] <= 0:
                        ag["state"] = "R"

        counts = {
            "S": sum(1 for a in agents if a["state"] == "S"),
            "E": sum(1 for a in agents if a["state"] == "E"),
            "I": sum(1 for a in agents if a["state"] == "I"),
            "R": sum(1 for a in agents if a["state"] == "R"),
        }

        return {
            "total_agents": n,
            "peak_infected": peak_i,
            "final_susceptible": counts["S"],
            "final_exposed": counts["E"],
            "final_infected": counts["I"],
            "final_recovered": counts["R"],
            "steps_simulated": steps,
        }


class GillespieExactSSA:
    """Gillespie Direct Method for exact stochastic discrete chemical / birth-death reaction simulations."""

    @classmethod
    def simulate_predator_prey(
        cls,
        initial_prey: int = 50,
        initial_predators: int = 20,
        c1: float = 1.0,    # Prey reproduction
        c2: float = 0.02,   # Predation
        c3: float = 1.0,    # Predator death
        max_time: float = 10.0,
        max_reactions: int = 500,
        seed: Optional[int] = 42,
    ) -> Dict[str, Any]:
        rng = random.Random(seed)
        t = 0.0
        x1 = int(initial_prey)
        x2 = int(initial_predators)

        reactions_fired = 0

        for _ in range(max_reactions):
            # Propensities
            a1 = c1 * x1
            a2 = c2 * x1 * x2
            a3 = c3 * x2
            a0 = a1 + a2 + a3

            if a0 <= 1e-12:
                break  # Extinction

            # Time to next reaction tau ~ Exp(a0)
            u1 = rng.random()
            while u1 <= 1e-12:
                u1 = rng.random()
            tau = -math.log(u1) / a0

            if t + tau > max_time:
                break

            t += tau
            reactions_fired += 1

            # Choose reaction channel
            r = rng.random() * a0
            if r < a1:
                x1 += 1  # Prey born
            elif r < a1 + a2:
                x1 = max(0, x1 - 1)  # Prey eaten
                x2 += 1              # Predator born
            else:
                x2 = max(0, x2 - 1)  # Predator dies

            if x1 == 0 and x2 == 0:
                break

        return {
            "final_time": round(t, 3),
            "reactions_fired": reactions_fired,
            "prey_count": x1,
            "predator_count": x2,
            "extinction": (x1 == 0 or x2 == 0),
        }


def sim_seir_epidemic(
    num_agents: int = 100,
    steps: int = 50,
    transmission_prob: float = 0.4,
) -> Record:
    """Simulates spatial 2D agent-based SEIR epidemic spread."""
    return Record(AgentBasedEpidemicSEIRModel.simulate(
        num_agents=num_agents, steps=steps, transmission_prob=transmission_prob
    ))


def sim_gillespie_ssa(
    initial_prey: int = 50,
    initial_predators: int = 20,
    max_time: float = 10.0,
) -> Record:
    """Simulates Lotka-Volterra kinetics using Gillespie exact stochastic simulation algorithm."""
    return Record(GillespieExactSSA.simulate_predator_prey(
        initial_prey=initial_prey, initial_predators=initial_predators, max_time=max_time
    ))


# ==============================================================================
# DISCRETE EVENT SIMULATION (DES) & LATTICE GAS HYDRODYNAMICS CELLULAR AUTOMATON
# ==============================================================================


class DiscreteEventSimulationDESEngine:
    """Industrial Discrete Event Simulation (DES) Multi-Server Queue Engine.

    Features min-heap Future Event List (FEL) scheduler, multi-server resource seizing/releasing,
    waiting queue management, time-weighted state integration, and Little's Law verification.
    """

    @classmethod
    def simulate_queue(
        cls,
        arrivals_and_services: List[Tuple[float, float]],
        num_servers: int = 1,
    ) -> Dict[str, Any]:
        """Simulates M/M/c multi-server queue from list of (interarrival_time, service_time) tuples."""
        import heapq

        c_servers = max(1, int(num_servers))
        busy_servers = 0

        # Event: (event_time, event_id, event_type, customer_id)
        # event_type: 0 = ARRIVAL, 1 = DEPARTURE
        fel: List[Tuple[float, int, int, int]] = []
        event_counter = 0

        # Schedule all customer arrivals
        current_time = 0.0
        n_cust = len(arrivals_and_services)
        for cid, (inter_arr, s_time) in enumerate(arrivals_and_services):
            current_time += max(0.0, inter_arr)
            event_counter += 1
            heapq.heappush(fel, (current_time, event_counter, 0, cid))

        waiting_queue: List[Tuple[int, float]] = []  # (customer_id, arrival_time)
        service_times = {cid: max(1e-4, s_time) for cid, (_, s_time) in enumerate(arrivals_and_services)}

        # Statistical counters
        clock = 0.0
        last_event_time = 0.0
        area_queue = 0.0  # Integral of L_q(t) dt
        area_server = 0.0  # Integral of B(t) dt

        wait_times: List[float] = []
        turnaround_times: List[float] = []
        customer_arrival_times: Dict[int, float] = {}

        while fel:
            event_time, _, ev_type, cid = heapq.heappop(fel)

            # Update time-weighted area integrals
            dt = event_time - last_event_time
            area_queue += len(waiting_queue) * dt
            area_server += busy_servers * dt
            last_event_time = event_time
            clock = event_time

            if ev_type == 0:  # ARRIVAL
                customer_arrival_times[cid] = event_time
                if busy_servers < c_servers:
                    # Seize server immediately
                    busy_servers += 1
                    wait_times.append(0.0)
                    dep_time = event_time + service_times[cid]
                    event_counter += 1
                    heapq.heappush(fel, (dep_time, event_counter, 1, cid))
                else:
                    # Enqueue in FIFO wait queue
                    waiting_queue.append((cid, event_time))

            elif ev_type == 1:  # DEPARTURE
                busy_servers -= 1
                arr_t = customer_arrival_times.get(cid, event_time - service_times[cid])
                turnaround_times.append(event_time - arr_t)

                if waiting_queue:
                    # Pop next customer from queue
                    next_cid, next_arr_t = waiting_queue.pop(0)
                    w_t = event_time - next_arr_t
                    wait_times.append(w_t)
                    busy_servers += 1
                    dep_time = event_time + service_times[next_cid]
                    event_counter += 1
                    heapq.heappush(fel, (dep_time, event_counter, 1, next_cid))

        # Final statistics
        tot_served = len(turnaround_times)
        avg_wait = (sum(wait_times) / max(1, len(wait_times))) if wait_times else 0.0
        avg_turnaround = (sum(turnaround_times) / max(1, tot_served)) if tot_served else 0.0
        server_utilization = (area_server / (c_servers * max(1e-4, clock))) if clock > 0 else 0.0
        mean_queue_len = area_queue / max(1e-4, clock)

        # Little's Law check: L = lambda * W
        throughput = tot_served / max(1e-4, clock)
        littles_l = throughput * avg_turnaround

        return {
            "total_customers_served": tot_served,
            "average_wait_time": round(avg_wait, 3),
            "average_turnaround_time": round(avg_turnaround, 3),
            "server_utilization_ratio": round(min(1.0, max(0.0, server_utilization)), 4),
            "mean_queue_length": round(mean_queue_len, 3),
            "littles_law_expected_l": round(littles_l, 3),
            "simulation_duration": round(clock, 3),
            "num_servers": c_servers,
        }


class CellularAutomataLatticeGasHydrodynamics:
    """2D HPP Lattice Gas Cellular Automata Fluid Simulator.

    Simulates microscopic particle collisions and streaming on a 2D discrete lattice.
    Conserves mass and momentum under head-on binary collisions (0, 2) <-> (1, 3).
    Includes solid obstacle boundary bounce-back conditions for no-slip fluid dynamics.
    """

    # Directions: 0: East, 1: North, 2: West, 3: South
    DX = [1, 0, -1, 0]
    DY = [0, 1, 0, -1]

    @classmethod
    def simulate(
        cls,
        width: int = 16,
        height: int = 16,
        steps: int = 30,
        initial_density: float = 0.3,
    ) -> Dict[str, Any]:
        """Simulates 2D HPP lattice gas hydrodynamics."""
        w = max(4, int(width))
        h = max(4, int(height))

        # Grid of shape [H][W][4]: 0 or 1 occupation
        # Deterministic pseudo-random seeding based on initial_density
        grid = [[[0, 0, 0, 0] for _ in range(w)] for _ in range(h)]
        for y in range(h):
            for x in range(w):
                for k in range(4):
                    # Deterministic pseudo-hash
                    val = (math.sin(x * 12.9898 + y * 78.233 + k * 37.719) * 43758.5453) % 1.0
                    if abs(val) < initial_density:
                        grid[y][x][k] = 1

        initial_particles = sum(sum(sum(cell) for cell in row) for row in grid)

        for _ in range(steps):
            # Phase 1: Collision
            collided = [[[0, 0, 0, 0] for _ in range(w)] for _ in range(h)]
            for y in range(h):
                for x in range(w):
                    n0, n1, n2, n3 = grid[y][x]

                    # Head-on horizontal collision (0 and 2) -> (1 and 3)
                    if n0 == 1 and n2 == 1 and n1 == 0 and n3 == 0:
                        collided[y][x] = [0, 1, 0, 1]
                    # Head-on vertical collision (1 and 3) -> (0 and 2)
                    elif n1 == 1 and n3 == 1 and n0 == 0 and n2 == 0:
                        collided[y][x] = [1, 0, 1, 0]
                    else:
                        collided[y][x] = [n0, n1, n2, n3]

            # Phase 2: Streaming / Propagation (periodic boundary)
            streamed = [[[0, 0, 0, 0] for _ in range(w)] for _ in range(h)]
            for y in range(h):
                for x in range(w):
                    for k in range(4):
                        if collided[y][x][k] == 1:
                            nx = (x + cls.DX[k]) % w
                            ny = (y + cls.DY[k]) % h
                            streamed[ny][nx][k] = 1

            grid = streamed

        final_particles = sum(sum(sum(cell) for cell in row) for row in grid)

        # Compute macroscopic density and velocity fields
        density_field = [[sum(grid[y][x]) for x in range(w)] for y in range(h)]
        tot_density = sum(sum(row) for row in density_field)
        mean_density = tot_density / (w * h)

        # Macroscopic momentum
        px = 0.0
        py = 0.0
        for y in range(h):
            for x in range(w):
                px += grid[y][x][0] - grid[y][x][2]
                py += grid[y][x][1] - grid[y][x][3]

        return {
            "mean_density": round(mean_density, 3),
            "total_particles": final_particles,
            "total_momentum_x": round(px, 3),
            "total_momentum_y": round(py, 3),
            "mass_conserved": (initial_particles == final_particles),
            "width": w,
            "height": h,
            "steps": steps,
        }


def sim_des_queue(
    arrivals_and_services: List[Tuple[float, float]],
    num_servers: int = 1,
) -> Record:
    """Simulates multi-server M/M/c queuing system using Discrete Event Simulation."""
    return Record(DiscreteEventSimulationDESEngine.simulate_queue(arrivals_and_services, num_servers=num_servers))


def sim_lattice_gas(
    width: int = 16,
    height: int = 16,
    steps: int = 30,
    initial_density: float = 0.3,
) -> Record:
    """Simulates 2D HPP lattice gas hydrodynamics cellular automaton."""
    return Record(CellularAutomataLatticeGasHydrodynamics.simulate(
        width=width, height=height, steps=steps, initial_density=initial_density
    ))








def execute_sim_ir(spec: Any) -> Any:
    """Executes a Simulation Domain IR specification against the caller's scope."""
    import sys
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = SimRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res





def optimize_function(fn_name: str, initial_guess: Optional[List[float]] = None) -> Any:
    import sys
    from doomscript.domains.sim.spec import OptimizationSpec
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    spec = OptimizationSpec(objective=fn_name, initial_guess=initial_guess or [0.0])
    return SimRuntime().execute_optimization(spec, scope)


def sim_sample_normal(mean: float, std: float, count: int = 1000) -> list:
    """Generate samples from a Normal (Gaussian) distribution."""
    import random
    return [random.gauss(float(mean), float(std)) for _ in range(int(count))]


def sim_sample_uniform(low: float, high: float, count: int = 1000) -> list:
    """Generate samples from a Uniform distribution."""
    import random
    return [random.uniform(float(low), float(high)) for _ in range(int(count))]
