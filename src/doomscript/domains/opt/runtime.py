"""Runtime execution engine and Simplex Linear Programming Solver."""

import math
import re
import random
from typing import Any, Callable, Dict, List, Optional, Tuple, Set, Union
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec
from doomscript.core.record import Record


def opt_create_linear_program(name: str = "lp") -> LinearProgramSpec:
    """Instantiates a new LinearProgramSpec."""
    return LinearProgramSpec(name=name, sense="maximize", objective="", constraints=[])


def parse_linear_expression(expr: str) -> Dict[str, float]:
    """Parses a linear expression string (e.g. '3 * x + 5 * y' or '2 * chairs - tables') into a variable-coefficient map."""
    clean = expr.replace(" ", "").strip()
    if not clean:
        return {}

    # Tokenize by '+' or '-'
    tokens = re.findall(r"[+-]?[^+-]+", clean)
    coef_map: Dict[str, float] = {}

    for tok in tokens:
        if not tok:
            continue
        tok = tok.strip()
        # Check sign
        sign = 1.0
        if tok.startswith("+"):
            tok = tok[1:]
        elif tok.startswith("-"):
            sign = -1.0
            tok = tok[1:]

        # Handle '3*x' or '3x' or 'x'
        if "*" in tok:
            parts = tok.split("*")
            val = float(parts[0]) * sign
            var = parts[1]
        else:
            # Check if leading number e.g. '3x'
            m = re.match(r"^(\d+(?:\.\d+)?)([A-Za-z_]\w*)$", tok)
            if m:
                val = float(m.group(1)) * sign
                var = m.group(2)
            else:
                val = 1.0 * sign
                var = tok

        coef_map[var] = coef_map.get(var, 0.0) + val

    return coef_map


def parse_constraint(constraint_str: str) -> Tuple[Dict[str, float], str, float]:
    """Parses a constraint string like '2 * x + y <= 100' into (coef_map, op, rhs)."""
    s = constraint_str.strip()
    m = re.search(r"(<=|>=|=|<|>)", s)
    if not m:
        raise ValueError(f"Constraint missing relational operator: {constraint_str}")

    op = m.group(1)
    lhs_str = s[: m.start()].strip()
    rhs_str = s[m.end() :].strip()

    coef_map = parse_linear_expression(lhs_str)
    rhs_val = float(rhs_str)

    # Normalize '<' to '<=' and '>' to '>='
    if op == "<":
        op = "<="
    elif op == ">":
        op = ">="

    return coef_map, op, rhs_val


class SimplexSolver:
    """Two-Phase Simplex / Dual Linear Programming Solver."""

    def __init__(
        self,
        sense: str,
        objective: Dict[str, float],
        constraints: List[Tuple[Dict[str, float], str, float]],
    ):
        self.sense = sense.lower()
        self.objective = objective
        self.raw_constraints = constraints

        # Collect all decision variables
        vars_set: Set[str] = set(objective.keys())
        for c_map, _, _ in constraints:
            vars_set.update(c_map.keys())
        self.var_names = sorted(list(vars_set))

    def solve(self) -> Dict[str, Any]:
        """Executes Simplex algorithm and returns status, optimal value, and variable assignments."""
        n_vars = len(self.var_names)
        var_to_col = {v: i for i, v in enumerate(self.var_names)}

        # Standardize: convert everything to maximization: max c^T x
        # If minimizing, max -c^T x
        c_sign = 1.0 if self.sense == "maximize" else -1.0
        c_vec = [self.objective.get(v, 0.0) * c_sign for v in self.var_names]

        # Standardize constraints: convert to A x <= b or handle >=
        # If minimization with all >= constraints and b >= 0, solve dual:
        is_all_ge = all(op in (">=", ">") for _, op, _ in self.raw_constraints)
        if self.sense == "minimize" and is_all_ge:
            return self._solve_dual_minimization(var_to_col, c_vec)

        # General standard tableau with slacks
        return self._solve_primal_tableau(var_to_col, c_vec)

    def _solve_dual_minimization(self, var_to_col: Dict[str, int], c_vec: List[float]) -> Dict[str, Any]:
        """Solves min c^T x s.t. A x >= b by solving dual max b^T y s.t. A^T y <= c."""
        # Dual:
        # max b^T y s.t. A^T y <= c
        # Primal variables are the dual slacks at optimality!
        m_constr = len(self.raw_constraints)
        n_prim = len(self.var_names)

        b_vec = [rhs for _, _, rhs in self.raw_constraints]
        # Check non-negativity of c_vec (for primal minimization)
        c_orig = [self.objective.get(v, 0.0) for v in self.var_names]

        # Matrix A (m_constr x n_prim)
        A = [[c_map.get(v, 0.0) for v in self.var_names] for c_map, _, _ in self.raw_constraints]

        # Dual has m_constr variables (y_1..y_m) and n_prim constraints (one per primal var)
        # Dual constraint j: sum_i A[i][j] * y_i <= c_orig[j]
        # Dual objective: max sum_i b_vec[i] * y_i
        dual_constraints = []
        for j in range(n_prim):
            row_map = {f"y_{i}": A[i][j] for i in range(m_constr)}
            dual_constraints.append((row_map, "<=", c_orig[j]))

        dual_obj = {f"y_{i}": b_vec[i] for i in range(m_constr)}
        dual_solver = SimplexSolver(sense="maximize", objective=dual_obj, constraints=dual_constraints)
        dual_res = dual_solver._solve_primal_tableau(
            {f"y_{i}": i for i in range(m_constr)}, [b_vec[i] for i in range(m_constr)]
        )

        if dual_res["status"] != "optimal":
            return dual_res

        # Primal solution corresponds to the reduced costs / slack coefficients of dual
        dual_slacks = dual_res.get("_slacks", [0.0] * n_prim)
        primal_vars = {}
        for j, v in enumerate(self.var_names):
            primal_vars[v] = round(dual_slacks[j], 4) if j < len(dual_slacks) else 0.0

        opt_val = round(dual_res["optimal_value"], 4)
        return {
            "status": "optimal",
            "optimal_value": opt_val,
            "objective_value": opt_val,
            "variables": primal_vars,
            "sense": self.sense,
        }

    def _solve_primal_tableau(self, var_to_col: Dict[str, int], c_vec: List[float]) -> Dict[str, Any]:
        """Solves standard maximization linear program using tableau simplex."""
        m_constr = len(self.raw_constraints)
        n_vars = len(self.var_names)

        # Tableau dimensions: (m_constr + 1) rows, (n_vars + m_constr + 1) cols
        tableau = []
        basis = []

        for i, (c_map, op, rhs) in enumerate(self.raw_constraints):
            row = [0.0] * (n_vars + m_constr + 1)
            # Decision variables
            for v, coef in c_map.items():
                if v in var_to_col:
                    row[var_to_col[v]] = coef

            if op in ("<=", "<"):
                row[n_vars + i] = 1.0  # slack variable
                row[-1] = rhs
                basis.append(n_vars + i)
            elif op in (">=", ">"):
                # Multiply by -1 for dual simplex formulation
                row = [-val for val in row]
                row[n_vars + i] = 1.0
                row[-1] = -rhs
                basis.append(n_vars + i)
            else:
                row[n_vars + i] = 1.0
                row[-1] = rhs
                basis.append(n_vars + i)

            tableau.append(row)

        # Objective row (bottom): -c_vec for maximization
        obj_row = [0.0] * (n_vars + m_constr + 1)
        for j in range(n_vars):
            obj_row[j] = -c_vec[j]
        tableau.append(obj_row)

        # Dual simplex if any RHS < 0
        max_dual_iter = 200
        for _ in range(max_dual_iter):
            min_rhs = 0.0
            pivot_row = -1
            for r in range(m_constr):
                if tableau[r][-1] < min_rhs - 1e-7:
                    min_rhs = tableau[r][-1]
                    pivot_row = r

            if pivot_row == -1:
                break  # Feasible!

            # Find pivot column
            pivot_col = -1
            min_ratio = float("inf")
            for c in range(n_vars + m_constr):
                if tableau[pivot_row][c] < -1e-7:
                    ratio = abs(tableau[-1][c] / tableau[pivot_row][c])
                    if ratio < min_ratio:
                        min_ratio = ratio
                        pivot_col = c

            if pivot_col == -1:
                return {"status": "infeasible", "optimal_value": 0.0, "variables": {}}

            self._pivot(tableau, basis, pivot_row, pivot_col)

        # Primal simplex
        max_iter = 500
        for _ in range(max_iter):
            # Find entering variable: most negative in objective row
            pivot_col = -1
            min_val = -1e-7
            for c in range(n_vars + m_constr):
                if tableau[-1][c] < min_val:
                    min_val = tableau[-1][c]
                    pivot_col = c

            if pivot_col == -1:
                break  # Optimal!

            # Minimum ratio test
            pivot_row = -1
            min_ratio = float("inf")
            for r in range(m_constr):
                entry = tableau[r][pivot_col]
                if entry > 1e-7:
                    ratio = tableau[r][-1] / entry
                    if ratio < min_ratio:
                        min_ratio = ratio
                        pivot_row = r

            if pivot_row == -1:
                return {"status": "unbounded", "optimal_value": float("inf"), "variables": {}}

            self._pivot(tableau, basis, pivot_row, pivot_col)

        # Read solution
        sol_vars: Dict[str, float] = {v: 0.0 for v in self.var_names}
        for r, b_idx in enumerate(basis):
            if b_idx < n_vars:
                var_name = self.var_names[b_idx]
                sol_vars[var_name] = round(max(0.0, tableau[r][-1]), 4)

        opt_val = tableau[-1][-1]
        if self.sense == "minimize":
            opt_val = -opt_val

        # Read slack reduced costs for dual recovery
        slacks = [tableau[-1][n_vars + i] for i in range(m_constr)]

        return {
            "status": "optimal",
            "optimal_value": round(opt_val, 4),
            "objective_value": round(opt_val, 4),
            "variables": sol_vars,
            "sense": self.sense,
            "_slacks": slacks,
        }

    def _pivot(self, tableau: List[List[float]], basis: List[int], p_row: int, p_col: int) -> None:
        """Pivots the simplex tableau on element (p_row, p_col)."""
        pivot_val = tableau[p_row][p_col]
        # Normalize pivot row
        tableau[p_row] = [val / pivot_val for val in tableau[p_row]]
        basis[p_row] = p_col

        # Eliminate pivot col from other rows
        n_rows = len(tableau)
        for r in range(n_rows):
            if r != p_row:
                factor = tableau[r][p_col]
                if abs(factor) > 1e-9:
                    tableau[r] = [
                        tableau[r][c] - factor * tableau[p_row][c]
                        for c in range(len(tableau[0]))
                    ]


def solve_linear_program(spec_or_name: Any, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Solves a LinearProgramSpec or named linear program in scope using Simplex."""
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
    if isinstance(spec_or_name, LinearProgramSpec):
        spec = spec_or_name
    elif isinstance(spec_or_name, dict) and "_spec" in spec_or_name:
        spec = spec_or_name["_spec"]
    elif isinstance(spec_or_name, str):
        from doomscript.domains.registry import get_domain_registry
        spec = get_domain_registry().get_spec_by_name(spec_or_name)
        if spec is None and scope:
            val = scope.get(spec_or_name)
            if isinstance(val, LinearProgramSpec):
                spec = val
            elif isinstance(val, dict) and "_spec" in val:
                spec = val["_spec"]
        if spec is None:
            raise ValueError(f"Linear program '{spec_or_name}' not found in registry or scope")
    else:
        raise TypeError(f"Cannot resolve LinearProgramSpec from {spec_or_name}")

    obj_map = parse_linear_expression(spec.objective)
    parsed_constraints = [parse_constraint(c) for c in spec.constraints]

    solver = SimplexSolver(sense=spec.sense, objective=obj_map, constraints=parsed_constraints)
    res = solver.solve()
    res["name"] = spec.name
    return res


class OptRuntime(DomainRuntime):
    """Runtime engine for Optimization & Operations Research domain."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if isinstance(ir, LinearProgramSpec):
            if ir.name == "direct_lp":
                res = solve_linear_program(ir, scope=scope)
                if ir.target_var:
                    scope[ir.target_var] = res
                return res
            # Store spec in scope
            res = {"name": ir.name, "_spec": ir}
            scope[ir.name] = res
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        elif isinstance(ir, SolveLPSpec):
            res = solve_linear_program(ir.lp_name, scope=scope)
            if ir.target_var:
                scope[ir.target_var] = res
            return res
        raise TypeError(f"Unknown Opt IR: {type(ir).__name__}")


# --- Batch 15 Spoken English Mathematical Optimization Verbs ---

def opt_minimize_1d(fn: Any, a: Any, b: Any, tol: Any = 1e-4) -> float:
    """Minimize 1D scalar function on interval [a, b] using Golden Section Search."""
    f = fn if callable(fn) else eval(f"lambda x: {fn}")
    left, right = float(a), float(b)
    t = float(tol)
    invphi = (math.sqrt(5) - 1) / 2
    invphi2 = (3 - math.sqrt(5)) / 2

    c = left + invphi2 * (right - left)
    d = left + invphi * (right - left)
    fc = f(c)
    fd = f(d)

    while (right - left) > t:
        if fc < fd:
            right = d
            d = c
            fd = fc
            c = left + invphi2 * (right - left)
            fc = f(c)
        else:
            left = c
            c = d
            fc = fd
            d = left + invphi * (right - left)
            fd = f(d)
    return round((left + right) / 2.0, 6)


def opt_grid_search(param_grid: Any, score_fn: Any) -> Dict[str, Any]:
    """Exhaustive grid search across parameter dictionary to minimize score_fn."""
    import itertools
    grid = dict(param_grid)
    keys = list(grid.keys())
    values_list = [list(grid[k]) for k in keys]
    best_params = None
    best_score = float("inf")

    for combo in itertools.product(*values_list):
        candidate = dict(zip(keys, combo))
        try:
            score = float(score_fn(candidate))
        except TypeError:
            score = float(score_fn(**candidate))
        if score < best_score:
            best_score = score
            best_params = candidate
    return {"best_params": best_params, "best_score": round(best_score, 6)}


def opt_fractional_knapsack(weights: Any, values: Any, capacity: Any) -> Dict[str, Any]:
    """Solve classic fractional knapsack problem optimally via greedy value-to-weight ratio."""
    w = [float(x) for x in weights]
    v = [float(x) for x in values]
    cap = float(capacity)
    items = sorted(range(len(w)), key=lambda i: v[i] / w[i] if w[i] > 0 else float("inf"), reverse=True)

    total_val = 0.0
    fractions = [0.0] * len(w)
    rem = cap

    for i in items:
        if rem <= 0:
            break
        take_w = min(w[i], rem)
        frac = take_w / w[i] if w[i] > 0 else 1.0
        fractions[i] = round(frac, 4)
        total_val += frac * v[i]
        rem -= take_w

    return {"total_value": round(total_val, 4), "fractions": fractions}


def opt_activity_selection(start_times: Any, end_times: Any) -> List[int]:
    """Optimal greedy activity selection maximizing non-overlapping activities."""
    s = [float(x) for x in start_times]
    e = [float(x) for x in end_times]
    activities = sorted(range(len(s)), key=lambda i: e[i])

    selected = []
    last_end = -float("inf")
    for i in activities:
        if s[i] >= last_end:
            selected.append(i)
            last_end = e[i]
    return selected


def opt_gradient_descent_step(point: Any, gradient: Any, learning_rate: Any = 0.01) -> Any:
    """Perform a gradient descent update step: x_next = x - lr * grad (supports scalars and vectors)."""
    lr = float(learning_rate)
    if isinstance(point, (int, float)) and isinstance(gradient, (int, float)):
        return round(float(point) - lr * float(gradient), 6)
    pt = [float(x) for x in point]
    grad = [float(g) for g in gradient]
    return [round(pt[i] - lr * grad[i], 6) for i in range(min(len(pt), len(grad)))]


def opt_bisection_root(fn: Any, a: Any, b: Any, tol: Any = 1e-5) -> float:
    """Find root of continuous 1D function f(x) = 0 on [a, b] using Bolzano's bisection method."""
    f = fn if callable(fn) else eval(f"lambda x: {fn}")
    left, right = float(a), float(b)
    t = float(tol)
    fa, fb = f(left), f(right)
    if fa * fb > 0:
        raise ValueError(f"Function must have opposite signs at interval endpoints: f({left})={fa}, f({right})={fb}")

    while (right - left) / 2.0 > t:
        mid = (left + right) / 2.0
        fmid = f(mid)
        if abs(fmid) < 1e-12:
            return round(mid, 6)
        if fa * fmid < 0:
            right = mid
            fb = fmid
        else:
            left = mid
            fa = fmid
    return round((left + right) / 2.0, 6)


def _make_callable_1d(fn_or_expr: Any) -> Callable:
    """Safely convert string expressions or lambdas to callables."""
    if callable(fn_or_expr):
        return fn_or_expr
    s = str(fn_or_expr).strip()
    if s.startswith("lambda"):
        return eval(s)
    return eval(f"lambda x: {s}")


def opt_simulated_annealing(cost_fn: Any, initial_state: Any, neighbor_fn: Any = None, temp: Any = 100.0, cooling_rate: Any = 0.95, max_iter: Any = 100) -> Any:
    """Simulated Annealing heuristic search for minimizing an objective cost function."""
    import random
    fn = _make_callable_1d(cost_fn)
    t = float(temp)
    alpha = float(cooling_rate)
    iterations = int(max_iter)

    current_state = initial_state
    current_cost = fn(current_state)
    best_state = current_state
    best_cost = current_cost

    for _ in range(iterations):
        if t <= 1e-8:
            break
        # Generate neighbor
        if neighbor_fn is not None:
            n_fn = _make_callable_1d(neighbor_fn)
            next_state = n_fn(current_state)
        elif isinstance(current_state, (int, float)):
            next_state = current_state + random.uniform(-1.0, 1.0)
        elif isinstance(current_state, list):
            next_state = list(current_state)
            if len(next_state) > 1:
                i, j = random.sample(range(len(next_state)), 2)
                next_state[i], next_state[j] = next_state[j], next_state[i]
        else:
            next_state = current_state

        next_cost = fn(next_state)
        delta = next_cost - current_cost

        if delta < 0 or random.random() < math.exp(-delta / t):
            current_state = next_state
            current_cost = next_cost
            if current_cost < best_cost:
                best_cost = current_cost
                best_state = current_state

        t *= alpha

    return best_state


def opt_golden_section_search(fn: Any, a: Any, b: Any, tol: Any = 1e-5) -> float:
    """1D unimodal function minimizer on [a, b] using Golden Section Search."""
    f = _make_callable_1d(fn)
    left, right = float(a), float(b)
    t = float(tol)
    phi = (math.sqrt(5.0) - 1.0) / 2.0  # ~0.6180339887

    c = right - phi * (right - left)
    d = left + phi * (right - left)
    fc = f(c)
    fd = f(d)

    while abs(right - left) > t:
        if fc < fd:
            right = d
            d = c
            fd = fc
            c = right - phi * (right - left)
            fc = f(c)
        else:
            left = c
            c = d
            fc = fd
            d = left + phi * (right - left)
            fd = f(d)

    return round((left + right) / 2.0, 6)


def opt_knapsack_01_dp(weights: List[int], values: List[float], capacity: int) -> Dict[str, Any]:
    """Exact 0/1 knapsack optimization using dynamic programming."""
    n = len(weights)
    cap = int(capacity)
    w_list = [int(w) for w in weights]
    v_list = [float(v) for v in values]

    dp = [[0.0] * (cap + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wi = w_list[i - 1]
        vi = v_list[i - 1]
        for w in range(cap + 1):
            if wi <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wi] + vi)
            else:
                dp[i][w] = dp[i - 1][w]

    # Backtrace
    selected = []
    curr_w = cap
    for i in range(n, 0, -1):
        if dp[i][curr_w] != dp[i - 1][curr_w]:
            selected.append(i - 1)
            curr_w -= w_list[i - 1]
    selected.reverse()

    return {
        "max_value": round(dp[n][cap], 4),
        "selected_indices": selected,
    }


def opt_longest_increasing_subsequence(arr: List[Any]) -> List[Any]:
    """Find the longest increasing subsequence in O(n log n) using patience sorting."""
    import bisect
    if not arr:
        return []

    tails = []
    tail_indices = []
    parent = [-1] * len(arr)

    for i, x in enumerate(arr):
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
            tail_indices.append(i)
        else:
            tails[idx] = x
            tail_indices[idx] = i

        if idx > 0:
            parent[i] = tail_indices[idx - 1]

    # Reconstruct LIS
    curr = tail_indices[-1]
    lis = []
    while curr != -1:
        lis.append(arr[curr])
        curr = parent[curr]
    lis.reverse()
    return lis


def opt_coin_change_minimum(coins: List[int], amount: int) -> int:
    """Fewest coins needed to make change for amount, or -1 if impossible."""
    amt = int(amount)
    if amt < 0:
        return -1
    if amt == 0:
        return 0

    dp = [float("inf")] * (amt + 1)
    dp[0] = 0

    for c in coins:
        c_val = int(c)
        for i in range(c_val, amt + 1):
            if dp[i - c_val] != float("inf"):
                dp[i] = min(dp[i], dp[i - c_val] + 1)

    return int(dp[amt]) if dp[amt] != float("inf") else -1


def opt_coin_change_combinations(coins: List[int], amount: int) -> int:
    """Total distinct combinations to make change for amount."""
    amt = int(amount)
    if amt < 0:
        return 0
    dp = [0] * (amt + 1)
    dp[0] = 1

    for c in coins:
        c_val = int(c)
        for i in range(c_val, amt + 1):
            dp[i] += dp[i - c_val]

    return int(dp[amt])


def opt_job_scheduling_deadline(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Maximize profit for jobs with integer deadlines and single-slot execution."""
    if not jobs:
        return {"total_profit": 0.0, "scheduled_jobs": []}

    parsed_jobs = []
    for j in jobs:
        if isinstance(j, dict):
            j_id = j.get("id", j.get("name", "job"))
            dl = int(j.get("deadline", 1))
            profit = float(j.get("profit", 0.0))
        elif isinstance(j, (list, tuple)) and len(j) >= 3:
            j_id, dl, profit = j[0], int(j[1]), float(j[2])
        else:
            continue
        parsed_jobs.append({"id": j_id, "deadline": dl, "profit": profit})

    # Sort descending by profit
    parsed_jobs.sort(key=lambda x: x["profit"], reverse=True)
    max_deadline = max(j["deadline"] for j in parsed_jobs) if parsed_jobs else 0
    slots = [None] * (max_deadline + 1)

    total_profit = 0.0
    scheduled = []

    for job in parsed_jobs:
        for t in range(min(max_deadline, job["deadline"]), 0, -1):
            if slots[t] is None:
                slots[t] = job["id"]
                total_profit += job["profit"]
                scheduled.append(job["id"])
                break

    return {
        "total_profit": round(total_profit, 4),
        "scheduled_jobs": scheduled,
    }


def opt_huffman_encoding(char_frequencies: Dict[str, int]) -> Dict[str, str]:
    """Generate optimal prefix Huffman codes for character frequency mapping."""
    import heapq
    if not char_frequencies:
        return {}
    if len(char_frequencies) == 1:
        char = next(iter(char_frequencies))
        return {char: "0"}

    # Heap elements: (frequency, counter, node)
    heap = []
    counter = 0
    for ch, freq in char_frequencies.items():
        heapq.heappush(heap, (int(freq), counter, ch))
        counter += 1

    tree = {}
    while len(heap) > 1:
        f1, _, left = heapq.heappop(heap)
        f2, _, right = heapq.heappop(heap)
        parent_id = f"node_{counter}"
        tree[parent_id] = (left, right)
        heapq.heappush(heap, (f1 + f2, counter, parent_id))
        counter += 1

    # Traverse tree to extract codes
    codes = {}
    root = heap[0][2]

    def _traverse(node: str, code_str: str):
        if node in tree:
            left, right = tree[node]
            _traverse(left, code_str + "0")
            _traverse(right, code_str + "1")
        else:
            codes[node] = code_str

    _traverse(root, "")
    return codes


def opt_matrix_chain_multiplication(dimensions: List[int]) -> Dict[str, Any]:
    """Find minimum scalar multiplications order for a sequence of matrix dimensions."""
    dims = [int(d) for d in dimensions]
    n = len(dims) - 1
    if n <= 1:
        return {"min_multiplications": 0, "dimensions": dims}

    dp = [[0] * (n + 1) for _ in range(n + 1)]

    for length in range(2, n + 1):
        for i in range(1, n - length + 2):
            j = i + length - 1
            dp[i][j] = float("inf")
            for k in range(i, j):
                q = dp[i][k] + dp[k + 1][j] + dims[i - 1] * dims[k] * dims[j]
                if q < dp[i][j]:
                    dp[i][j] = q

    return {
        "min_multiplications": int(dp[1][n]),
        "dimensions": dims,
    }


def opt_levenshtein_alignment(s1: str, s2: str) -> Dict[str, Any]:
    """Compute global sequence alignment backtrace between two strings."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

    # Backtrace
    align1 = []
    align2 = []
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and s1[i - 1] == s2[j - 1]:
            align1.append(s1[i - 1])
            align2.append(s2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            align1.append(s1[i - 1])
            align2.append(s2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            align1.append(s1[i - 1])
            align2.append("-")
            i -= 1
        else:
            align1.append("-")
            align2.append(s2[j - 1])
            j -= 1

    return {
        "aligned_s1": "".join(reversed(align1)),
        "aligned_s2": "".join(reversed(align2)),
        "distance": int(dp[m][n]),
    }


def opt_subset_sum_exists(arr: List[int], target_sum: int) -> bool:
    """Check if any subset of integer elements sums exactly to target_sum."""
    target = int(target_sum)
    if target == 0:
        return True
    int_arr = [int(x) for x in arr]
    if target < 0:
        return False

    possible = 1
    for x in int_arr:
        if x >= 0:
            possible |= (possible << x)
    return bool((possible >> target) & 1)


def opt_subset_sum_find(arr: List[int], target_sum: int) -> List[int]:
    """Find a subset of elements summing to target_sum, or empty list if none."""
    target = int(target_sum)
    int_arr = [int(x) for x in arr]
    if target == 0:
        return []
    if target < 0:
        return []

    dp = {0: []}
    for x in int_arr:
        new_dp = dict(dp)
        for s, subset in dp.items():
            new_s = s + x
            if new_s == target:
                return subset + [x]
            if new_s < target and new_s not in new_dp:
                new_dp[new_s] = subset + [x]
        dp = new_dp

    return dp.get(target, [])


def opt_rod_cutting(prices: List[float], rod_length: int) -> Dict[str, Any]:
    """Maximum revenue rod cutting dynamic programming."""
    length = int(rod_length)
    if length <= 0 or not prices:
        return {"max_revenue": 0.0, "cuts": []}

    dp = [0.0] * (length + 1)
    first_cut = [0] * (length + 1)

    for j in range(1, length + 1):
        max_val = -float("inf")
        for i in range(1, min(j, len(prices)) + 1):
            val = float(prices[i - 1]) + dp[j - i]
            if val > max_val:
                max_val = val
                first_cut[j] = i
        dp[j] = max_val

    # Reconstruct cuts
    cuts = []
    rem = length
    while rem > 0:
        cuts.append(first_cut[rem])
        rem -= first_cut[rem]

    return {
        "max_revenue": round(dp[length], 4),
        "cuts": cuts,
    }


def opt_two_opt_tsp(coords: List[List[float]], max_iterations: Any = 100) -> Dict[str, Any]:
    """2-opt Traveling Salesperson heuristic tour optimization."""
    n = len(coords)
    if n <= 1:
        return {"tour": list(range(n)), "distance": 0.0}

    def _dist(p1, p2):
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    tour = list(range(n)) + [0]

    def _tour_distance(t):
        return sum(_dist(coords[t[i]], coords[t[i + 1]]) for i in range(len(t) - 1))

    improved = True
    iteration = 0
    max_iter = int(max_iterations)

    while improved and iteration < max_iter:
        improved = False
        iteration += 1
        for i in range(1, n - 1):
            for j in range(i + 1, n):
                old_d = _dist(coords[tour[i - 1]], coords[tour[i]]) + _dist(coords[tour[j]], coords[tour[j + 1]])
                new_d = _dist(coords[tour[i - 1]], coords[tour[j]]) + _dist(coords[tour[i]], coords[tour[j + 1]])
                if new_d < old_d - 1e-9:
                    tour[i:j + 1] = reversed(tour[i:j + 1])
                    improved = True
                    break
            if improved:
                break

    return {
        "tour": tour[:-1],
        "distance": round(_tour_distance(tour), 4),
    }


def opt_linear_interpolation(x_points: List[float], y_points: List[float], target_x: float) -> float:
    """1D piecewise linear interpolation at target_x."""
    tx = float(target_x)
    pairs = sorted(zip([float(x) for x in x_points], [float(y) for y in y_points]), key=lambda p: p[0])
    if not pairs:
        return 0.0
    if tx <= pairs[0][0]:
        return round(pairs[0][1], 6)
    if tx >= pairs[-1][0]:
        return round(pairs[-1][1], 6)

    for i in range(len(pairs) - 1):
        x1, y1 = pairs[i]
        x2, y2 = pairs[i + 1]
        if x1 <= tx <= x2:
            if abs(x2 - x1) < 1e-12:
                return round(y1, 6)
            interpolated = y1 + (tx - x1) * (y2 - y1) / (x2 - x1)
            return round(interpolated, 6)

    return round(pairs[-1][1], 6)


def opt_weighted_interval_scheduling(intervals_with_weights: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Dynamic programming weighted interval scheduling."""
    if not intervals_with_weights:
        return {"max_weight": 0.0, "selected_intervals": []}

    items = []
    for it in intervals_with_weights:
        if isinstance(it, dict):
            s = float(it.get("start", 0))
            e = float(it.get("end", 0))
            w = float(it.get("weight", 0))
        elif isinstance(it, (list, tuple)) and len(it) >= 3:
            s, e, w = float(it[0]), float(it[1]), float(it[2])
        else:
            continue
        items.append({"start": s, "end": e, "weight": w, "raw": it})

    # Sort by end time
    items.sort(key=lambda x: x["end"])
    n = len(items)

    # Precompute p(j) - latest non-conflicting interval
    p = [-1] * n
    for j in range(n):
        for k in range(j - 1, -1, -1):
            if items[k]["end"] <= items[j]["start"]:
                p[j] = k
                break

    dp = [0.0] * (n + 1)
    for j in range(1, n + 1):
        incl = items[j - 1]["weight"] + (dp[p[j - 1] + 1] if p[j - 1] != -1 else 0.0)
        excl = dp[j - 1]
        dp[j] = max(incl, excl)

    # Backtrace
    selected = []
    curr = n
    while curr > 0:
        incl = items[curr - 1]["weight"] + (dp[p[curr - 1] + 1] if p[curr - 1] != -1 else 0.0)
        if incl >= dp[curr - 1]:
            selected.append(items[curr - 1]["raw"])
            curr = p[curr - 1] + 1 if p[curr - 1] != -1 else 0
        else:
            curr -= 1

    selected.reverse()
    return {
        "max_weight": round(dp[n], 4),
        "selected_intervals": selected,
    }


def opt_pareto_frontier(points: List[List[float]]) -> List[List[float]]:
    """Extract non-dominated Pareto optimal frontier points (assuming maximization)."""
    clean_points = [[float(c) for c in pt] for pt in points]
    frontier = []

    for i, p1 in enumerate(clean_points):
        dominated = False
        for j, p2 in enumerate(clean_points):
            if i == j:
                continue
            # p2 dominates p1 if all coords of p2 >= p1 and at least one > p1
            if all(c2 >= c1 for c1, c2 in zip(p1, p2)) and any(c2 > c1 for c1, c2 in zip(p1, p2)):
                dominated = True
                break
        if not dominated:
            frontier.append(p1)

    return frontier


def opt_hungarian_assignment(cost_matrix: List[List[float]]) -> Dict[str, Any]:
    """Optimal bipartite assignment min-cost matching via Kuhn-Munkres algorithm."""
    # Build clean square matrix
    rows = len(cost_matrix)
    cols = len(cost_matrix[0]) if rows > 0 else 0
    n = max(rows, cols)
    if n == 0:
        return {"min_cost": 0.0, "assignment": []}

    mat = [[0.0] * n for _ in range(n)]
    for r in range(rows):
        for c in range(cols):
            mat[r][c] = float(cost_matrix[r][c])

    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)

    for i in range(1, n + 1):
        p[0] = i
        j0 = 0
        minv = [float("inf")] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float("inf")
            j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = mat[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    assignment = []
    total_cost = 0.0
    for j in range(1, n + 1):
        if p[j] <= rows and j <= cols:
            r_idx = p[j] - 1
            c_idx = j - 1
            assignment.append((r_idx, c_idx))
            total_cost += float(cost_matrix[r_idx][c_idx])

    assignment.sort(key=lambda x: x[0])
    return {
        "min_cost": round(total_cost, 4),
        "assignment": assignment,
    }


def opt_binary_search_peak_1d(arr: List[float]) -> Dict[str, Any]:
    """Find a local peak element index in O(log n)."""
    vals = [float(x) for x in arr]
    n = len(vals)
    if n == 0:
        return {"index": -1, "value": None}
    if n == 1:
        return {"index": 0, "value": vals[0]}

    low, high = 0, n - 1
    while low <= high:
        mid = (low + high) // 2
        left_val = vals[mid - 1] if mid > 0 else -float("inf")
        right_val = vals[mid + 1] if mid < n - 1 else -float("inf")

        if vals[mid] >= left_val and vals[mid] >= right_val:
            return {"index": mid, "value": vals[mid]}
        elif mid < n - 1 and vals[mid] < vals[mid + 1]:
            low = mid + 1
        else:
            high = mid - 1

    return {"index": low, "value": vals[low]}


class SAResult(float):
    """Simulated Annealing result that behaves as a float (best scalar) and a dict."""

    def __new__(cls, val, best_state=None, best_cost=None, history=None):
        obj = super().__new__(cls, float(val))
        obj.best_state = best_state or [float(val)]
        obj.best_cost = float(best_cost) if best_cost is not None else float(val)
        obj.history = history or [float(val)]
        return obj

    def __getitem__(self, key: str) -> Any:
        if key == "best_state":
            return self.best_state
        elif key == "best_cost":
            return self.best_cost
        elif key == "history":
            return self.history
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in ("best_state", "best_cost", "history")

    def get(self, key: str, default: Any = None) -> Any:
        if key in self:
            return self[key]
        return default


def opt_simulated_annealing(
    cost_fn: Any,
    initial_state: Union[List[float], float],
    bounds: Optional[List[Tuple[float, float]]] = None,
    temp_max: float = 100.0,
    cooling_rate: float = 0.95,
    temp_min: float = 1e-4,
    steps_per_temp: int = 15,
    step_size: float = 0.5,
    seed: int = 42,
) -> SAResult:
    """Simulated Annealing global optimization for non-convex or noisy objectives."""
    import random
    rng = random.Random(seed)

    if isinstance(cost_fn, str):
        fn = eval(cost_fn)
    else:
        fn = cost_fn

    is_scalar = isinstance(initial_state, (int, float))
    curr_state = [float(x) for x in (initial_state if isinstance(initial_state, list) else [initial_state])]
    dim = len(curr_state)

    def eval_fn(st: List[float]) -> float:
        if is_scalar:
            try:
                return float(fn(st[0]))
            except Exception:
                return float(fn(st))
        else:
            try:
                return float(fn(st))
            except Exception:
                return float(fn(*st))

    curr_cost = eval_fn(curr_state)
    best_state = list(curr_state)
    best_cost = curr_cost

    temp = float(temp_max)
    history = [best_cost]

    while temp > temp_min:
        for _ in range(steps_per_temp):
            # Propose neighbor
            cand = list(curr_state)
            for d in range(dim):
                delta = rng.gauss(0.0, step_size)
                cand[d] += delta
                if bounds and d < len(bounds):
                    b_low, b_high = bounds[d]
                    cand[d] = max(b_low, min(b_high, cand[d]))

            cand_cost = eval_fn(cand)
            diff = cand_cost - curr_cost

            # Acceptance criterion
            if diff < 0.0 or rng.random() < math.exp(-min(500.0, max(-500.0, diff / temp))):
                curr_state = cand
                curr_cost = cand_cost
                if curr_cost < best_cost:
                    best_state = list(curr_state)
                    best_cost = curr_cost

        temp *= cooling_rate
        history.append(best_cost)

    best_val = best_state[0] if is_scalar else best_cost
    rounded_state = [round(x, 4) for x in best_state]
    return SAResult(best_val, best_state=rounded_state, best_cost=round(best_cost, 6), history=history)



def opt_genetic_algorithm(
    fitness_fn: Callable[[List[float]], float],
    bounds: List[Tuple[float, float]],
    population_size: int = 40,
    generations: int = 40,
    crossover_prob: float = 0.8,
    mutation_prob: float = 0.15,
    elitism_count: int = 2,
    maximize: bool = False,
    seed: int = 42,
) -> Dict[str, Any]:
    """Continuous Genetic Algorithm (selection, crossover, Gaussian mutation, elitism)."""
    import random
    rng = random.Random(seed)
    dim = len(bounds)

    # Initialize population uniformly inside bounds
    population = []
    for _ in range(population_size):
        ind = [rng.uniform(low, high) for low, high in bounds]
        population.append(ind)

    def evaluate(ind: List[float]) -> float:
        val = float(fitness_fn(ind))
        return val if maximize else -val

    best_ind = list(population[0])
    best_score = evaluate(best_ind)
    score_history = []

    for gen in range(generations):
        scores = [evaluate(ind) for ind in population]
        ranked_indices = sorted(range(population_size), key=lambda i: scores[i], reverse=True)

        if scores[ranked_indices[0]] > best_score:
            best_score = scores[ranked_indices[0]]
            best_ind = list(population[ranked_indices[0]])

        actual_best = best_score if maximize else -best_score
        score_history.append(actual_best)

        # Elites
        next_gen = [list(population[i]) for i in ranked_indices[:elitism_count]]

        # Tournament selection
        def select():
            k_inds = rng.sample(range(population_size), 3)
            best_k = max(k_inds, key=lambda i: scores[i])
            return population[best_k]

        while len(next_gen) < population_size:
            p1 = select()
            p2 = select()

            # Blend Crossover (BLX-alpha)
            if rng.random() < crossover_prob:
                c1, c2 = [], []
                for d in range(dim):
                    alpha = rng.random()
                    val1 = alpha * p1[d] + (1.0 - alpha) * p2[d]
                    val2 = (1.0 - alpha) * p1[d] + alpha * p2[d]
                    c1.append(val1)
                    c2.append(val2)
            else:
                c1, c2 = list(p1), list(p2)

            # Mutation
            for child in (c1, c2):
                if len(next_gen) >= population_size:
                    break
                for d in range(dim):
                    if rng.random() < mutation_prob:
                        span = bounds[d][1] - bounds[d][0]
                        child[d] += rng.gauss(0.0, span * 0.1)
                    child[d] = max(bounds[d][0], min(bounds[d][1], child[d]))
                next_gen.append(child)

        population = next_gen

    final_best = best_score if maximize else -best_score
    return {
        "best_state": [round(x, 4) for x in best_ind],
        "best_cost": round(final_best, 6),
        "history": [round(h, 6) for h in score_history],
    }


def opt_particle_swarm(
    cost_fn: Callable[[List[float]], float],
    bounds: List[Tuple[float, float]],
    n_particles: int = 30,
    iterations: int = 40,
    w: float = 0.729,
    c1: float = 1.494,
    c2: float = 1.494,
    seed: int = 42,
) -> Dict[str, Any]:
    """Particle Swarm Optimization (PSO) with inertia and cognitive/social acceleration."""
    import random
    rng = random.Random(seed)
    dim = len(bounds)

    particles = []
    velocities = []
    pbest_positions = []
    pbest_costs = []

    gbest_position = None
    gbest_cost = float("inf")

    for _ in range(n_particles):
        pos = [rng.uniform(low, high) for low, high in bounds]
        vel = [rng.uniform(-(high - low) * 0.1, (high - low) * 0.1) for low, high in bounds]
        cost = float(cost_fn(pos))

        particles.append(pos)
        velocities.append(vel)
        pbest_positions.append(list(pos))
        pbest_costs.append(cost)

        if cost < gbest_cost:
            gbest_cost = cost
            gbest_position = list(pos)

    history = [round(gbest_cost, 6)]

    for it in range(iterations):
        for i in range(n_particles):
            for d in range(dim):
                r1 = rng.random()
                r2 = rng.random()
                cog = c1 * r1 * (pbest_positions[i][d] - particles[i][d])
                soc = c2 * r2 * (gbest_position[d] - particles[i][d])
                velocities[i][d] = w * velocities[i][d] + cog + soc

                # Clamp velocity
                span = bounds[d][1] - bounds[d][0]
                max_v = span * 0.2
                velocities[i][d] = max(-max_v, min(max_v, velocities[i][d]))

                # Update position
                particles[i][d] += velocities[i][d]
                particles[i][d] = max(bounds[d][0], min(bounds[d][1], particles[i][d]))

            cost = float(cost_fn(particles[i]))
            if cost < pbest_costs[i]:
                pbest_costs[i] = cost
                pbest_positions[i] = list(particles[i])
                if cost < gbest_cost:
                    gbest_cost = cost
                    gbest_position = list(particles[i])

        history.append(round(gbest_cost, 6))

    return {
        "best_state": [round(x, 4) for x in gbest_position] if gbest_position else [],
        "best_cost": round(gbest_cost, 6),
        "history": history,
    }


def opt_nelder_mead(
    cost_fn: Callable[[List[float]], float],
    initial_point: List[float],
    step: float = 0.5,
    alpha: float = 1.0,
    gamma: float = 2.0,
    rho: float = 0.5,
    sigma: float = 0.5,
    max_iter: int = 150,
    tol: float = 1e-6,
) -> Dict[str, Any]:
    """Nelder-Mead downhill simplex direct search optimization."""
    x0 = [float(x) for x in initial_point]
    n = len(x0)
    if n == 0:
        return {"best_state": [], "best_cost": 0.0, "iterations": 0}

    # Initialize simplex of n+1 vertices
    simplex = [list(x0)]
    for i in range(n):
        vertex = list(x0)
        vertex[i] += step
        simplex.append(vertex)

    costs = [float(cost_fn(v)) for v in simplex]
    iterations = 0

    for it in range(max_iter):
        iterations += 1
        # Sort simplex vertices by cost
        order = sorted(range(n + 1), key=lambda i: costs[i])
        simplex = [simplex[i] for i in order]
        costs = [costs[i] for i in order]

        # Check termination condition
        mean_cost = sum(costs) / (n + 1)
        var = sum((c - mean_cost) ** 2 for c in costs) / (n + 1)
        if math.sqrt(var) < tol:
            break

        # Centroid of all vertices except worst
        centroid = [sum(simplex[i][d] for i in range(n)) / n for d in range(n)]

        # 1. Reflection
        xr = [centroid[d] + alpha * (centroid[d] - simplex[n][d]) for d in range(n)]
        fxr = float(cost_fn(xr))

        if costs[0] <= fxr < costs[n - 1]:
            simplex[n] = xr
            costs[n] = fxr
            continue

        # 2. Expansion
        if fxr < costs[0]:
            xe = [centroid[d] + gamma * (xr[d] - centroid[d]) for d in range(n)]
            fxe = float(cost_fn(xe))
            if fxe < fxr:
                simplex[n] = xe
                costs[n] = fxe
            else:
                simplex[n] = xr
                costs[n] = fxr
            continue

        # 3. Contraction
        if fxr < costs[n]:
            # Outside contraction
            xc = [centroid[d] + rho * (xr[d] - centroid[d]) for d in range(n)]
            fxc = float(cost_fn(xc))
            if fxc <= fxr:
                simplex[n] = xc
                costs[n] = fxc
                continue
        else:
            # Inside contraction
            xcc = [centroid[d] + rho * (simplex[n][d] - centroid[d]) for d in range(n)]
            fxcc = float(cost_fn(xcc))
            if fxcc < costs[n]:
                simplex[n] = xcc
                costs[n] = fxcc
                continue

        # 4. Shrink
        for i in range(1, n + 1):
            simplex[i] = [simplex[0][d] + sigma * (simplex[i][d] - simplex[0][d]) for d in range(n)]
            costs[i] = float(cost_fn(simplex[i]))

    best_idx = 0
    return {
        "best_state": [round(x, 4) for x in simplex[best_idx]],
        "best_cost": round(costs[best_idx], 6),
        "iterations": iterations,
    }


def opt_hungarian_algorithm(cost_matrix: List[List[float]]) -> Dict[str, Any]:
    """Solves the optimal bipartite assignment problem using the Kuhn-Munkres (Hungarian) algorithm in O(N^3).

    Given an N x M cost matrix, finds row-to-column matching that minimizes total cost.
    Supports non-square matrices by zero-padding.
    """
    if not cost_matrix or not cost_matrix[0]:
        return {"assignment": [], "row_to_col": [], "total_cost": 0.0}

    n_rows = len(cost_matrix)
    n_cols = len(cost_matrix[0])
    dim = max(n_rows, n_cols)

    grid = [[0.0] * dim for _ in range(dim)]
    for r in range(n_rows):
        for c in range(n_cols):
            grid[r][c] = float(cost_matrix[r][c])

    u = [0.0] * (dim + 1)
    v = [0.0] * (dim + 1)
    p = [0] * (dim + 1)
    way = [0] * (dim + 1)

    for i in range(1, dim + 1):
        p[0] = i
        j0 = 0
        minv = [float("inf")] * (dim + 1)
        used = [False] * (dim + 1)

        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float("inf")
            j1 = 0
            for j in range(1, dim + 1):
                if not used[j]:
                    cur = grid[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j

            for j in range(dim + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            j0 = j1
            if p[j0] == 0:
                break

        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    ans = [-1] * n_rows
    total_cost = 0.0
    for j in range(1, dim + 1):
        r_idx = p[j] - 1
        c_idx = j - 1
        if 0 <= r_idx < n_rows and 0 <= c_idx < n_cols:
            ans[r_idx] = c_idx
            total_cost += cost_matrix[r_idx][c_idx]

    assignment = [{"row": r, "col": ans[r], "cost": cost_matrix[r][ans[r]]} for r in range(n_rows) if ans[r] != -1]
    return {
        "assignment": assignment,
        "row_to_col": ans,
        "total_cost": round(total_cost, 6),
    }


class PrimalDualInteriorPoint:
    """Predictor-Corrector Primal-Dual Interior Point solver for Linear Programming."""

    def __init__(self, max_iter: int = 50, tol: float = 1e-6):
        self.max_iter = max_iter
        self.tol = tol

    def solve(
        self,
        c: List[float],
        A: List[List[float]],
        b: List[float],
    ) -> Dict[str, Any]:
        """
        Solves standard LP: min c^T x  s.t.  A x = b, x >= 0.
        Uses pure-Python Gaussian elimination for linear Newton system.
        """
        m = len(A)  # number of constraints
        n = len(c)  # number of variables

        # Strictly positive initial point
        x = [1.0] * n
        s = [1.0] * n
        y = [0.0] * m

        def solve_linear_system(M_mat: List[List[float]], rhs: List[float]) -> Optional[List[float]]:
            """Solves M * z = rhs using Gaussian elimination with partial pivoting."""
            dim = len(M_mat)
            aug = [list(M_mat[r]) + [rhs[r]] for r in range(dim)]

            for col in range(dim):
                pivot_row = max(range(col, dim), key=lambda r: abs(aug[r][col]))
                if abs(aug[pivot_row][col]) < 1e-12:
                    return None
                aug[col], aug[pivot_row] = aug[pivot_row], aug[col]

                pivot = aug[col][col]
                for c_idx in range(col, dim + 1):
                    aug[col][c_idx] /= pivot

                for r in range(dim):
                    if r != col:
                        factor = aug[r][col]
                        for c_idx in range(col, dim + 1):
                            aug[r][c_idx] -= factor * aug[col][c_idx]

            return [aug[r][dim] for r in range(dim)]

        for it in range(self.max_iter):
            # Compute residuals
            # r_p = b - A * x
            r_p = [b[i] - sum(A[i][j] * x[j] for j in range(n)) for i in range(m)]
            # r_d = c - A^T * y - s
            r_d = [c[j] - sum(A[i][j] * y[i] for i in range(m)) - s[j] for j in range(n)]

            primal_res_norm = math.sqrt(sum(v ** 2 for v in r_p))
            dual_res_norm = math.sqrt(sum(v ** 2 for v in r_d))
            mu = sum(x[j] * s[j] for j in range(n)) / n

            if primal_res_norm < self.tol and dual_res_norm < self.tol and mu < self.tol:
                break

            # Normal equations for dy:
            # (A * X * S^{-1} * A^T) dy = r_p + A * S^{-1} * (X r_d - mu * e)
            sigma = 0.2
            # D = X * S^{-1}
            d = [x[j] / s[j] for j in range(n)]

            M = [[0.0] * m for _ in range(m)]
            for i in range(m):
                for k in range(m):
                    M[i][k] = sum(A[i][j] * d[j] * A[k][j] for j in range(n))

            rhs_dy = [0.0] * m
            for i in range(m):
                term_s = sum(
                    A[i][j] * (x[j] * r_d[j] - (x[j] * s[j] - sigma * mu)) / s[j]
                    for j in range(n)
                )
                rhs_dy[i] = r_p[i] + term_s

            dy = solve_linear_system(M, rhs_dy)
            if dy is None:
                # Regularization fallback
                for i in range(m):
                    M[i][i] += 1e-4
                dy = solve_linear_system(M, rhs_dy)
                if dy is None:
                    break

            # Backsolve dx and ds
            # ds = r_d - A^T dy
            ds = [r_d[j] - sum(A[i][j] * dy[i] for i in range(m)) for j in range(n)]
            # dx = (sigma * mu - X * S - X * ds) / S
            dx = [(sigma * mu - x[j] * s[j] - x[j] * ds[j]) / s[j] for j in range(n)]

            # Step sizes to maintain x > 0 and s > 0
            alpha_p = 1.0
            for j in range(n):
                if dx[j] < 0:
                    alpha_p = min(alpha_p, -0.995 * x[j] / dx[j])

            alpha_d = 1.0
            for j in range(n):
                if ds[j] < 0:
                    alpha_d = min(alpha_d, -0.995 * s[j] / ds[j])

            step_size = min(alpha_p, alpha_d)
            for j in range(n):
                x[j] += step_size * dx[j]
                s[j] += step_size * ds[j]
            for i in range(m):
                y[i] += step_size * dy[i]

        obj_val = sum(c[j] * x[j] for j in range(n))
        return {
            "optimal_x": [round(val, 6) for val in x],
            "objective_value": round(obj_val, 6),
            "iterations": it + 1,
            "duality_gap": round(mu, 8),
            "converged": mu < self.tol,
        }


def opt_simplex_solve(c: List[float], A_ub: List[List[float]], b_ub: List[float], maximize: bool = True) -> Dict[str, Any]:
    """Solves LP max/min c^T x s.t. A_ub x <= b_ub, x >= 0 via SimplexSolver."""
    var_names = [f"x{i}" for i in range(len(c))]
    sense = "maximize" if maximize else "minimize"
    obj_dict = {f"x{i}": float(c[i]) for i in range(len(c))}
    constraints = []
    for row, rhs in zip(A_ub, b_ub):
        c_map = {f"x{i}": float(row[i]) for i in range(len(row)) if abs(row[i]) > 1e-12}
        constraints.append((c_map, "<=", float(rhs)))

    solver = SimplexSolver(sense, obj_dict, constraints)
    res = solver.solve()
    if res.get("status") in ("optimal", "bounded", "solved"):
        sol_map = res.get("variables", {})
        sol_vec = [float(sol_map.get(f"x{i}", 0.0)) for i in range(len(c))]
        return {
            "success": True,
            "solution": sol_vec,
            "objective_value": float(res.get("optimal_value", 0.0)),
        }
    return {"success": False, "solution": [], "objective_value": 0.0}


class BranchAndBoundMILP:
    """Branch and Bound solver for Mixed-Integer Linear Programs (MILP)."""

    def __init__(self, max_nodes: int = 500, tol: float = 1e-4):
        self.max_nodes = max_nodes
        self.tol = tol

    def solve(
        self,
        c: List[float],
        A_ub: List[List[float]],
        b_ub: List[float],
        integer_indices: Optional[List[int]] = None,
        maximize: bool = True,
    ) -> Dict[str, Any]:
        """
        Solves: max c^T x  s.t.  A_ub x <= b_ub, x >= 0, x_i in Z for i in integer_indices.
        """
        n_vars = len(c)
        int_vars = set(integer_indices if integer_indices is not None else range(n_vars))
        obj_mult = 1.0 if maximize else -1.0
        c_eff = [val * obj_mult for val in c]

        # Use dual simplex relaxation solver from opt runtime
        from doomscript.domains.opt.runtime import opt_simplex_solve

        best_obj = float("-inf")
        best_x: Optional[List[float]] = None
        nodes_explored = 0

        # Stack of subproblems: (additional_constraints)
        # constraint: (var_idx, op '<=' or '>=', bound_val)
        stack: List[List[Tuple[int, str, float]]] = [[]]

        while stack and nodes_explored < self.max_nodes:
            nodes_explored += 1
            curr_bounds = stack.pop()

            # Build augmented LP problem
            A_curr = [list(row) for row in A_ub]
            b_curr = list(b_ub)

            for v_idx, op, bnd in curr_bounds:
                row = [0.0] * n_vars
                if op == "<=":
                    row[v_idx] = 1.0
                    A_curr.append(row)
                    b_curr.append(bnd)
                elif op == ">=":
                    row[v_idx] = -1.0
                    A_curr.append(row)
                    b_curr.append(-bnd)

            # Solve LP relaxation: max c_eff^T x  s.t.  A_curr x <= b_curr
            lp_res = opt_simplex_solve(c_eff, A_curr, b_curr, maximize=True)
            if not lp_res.get("success", False):
                # Infeasible or unbounded branch -> prune
                continue

            rel_obj = lp_res["objective_value"]
            rel_x = lp_res["solution"]

            # Bound prune: if relaxation cannot beat best integer solution
            if rel_obj <= best_obj + self.tol:
                continue

            # Check integrality of int_vars
            fractional_var = None
            max_frac_dist = 0.0
            for idx in int_vars:
                val = rel_x[idx]
                dist = abs(val - round(val))
                if dist > self.tol:
                    if dist > max_frac_dist:
                        max_frac_dist = dist
                        fractional_var = idx

            if fractional_var is None:
                # All integer variables are integer! Candidate found.
                if rel_obj > best_obj:
                    best_obj = rel_obj
                    best_x = [round(val, 6) for val in rel_x]
            else:
                # Branch on fractional_var
                v_val = rel_x[fractional_var]
                floor_bnd = math.floor(v_val)
                ceil_bnd = math.ceil(v_val)

                branch_left = list(curr_bounds) + [(fractional_var, "<=", float(floor_bnd))]
                branch_right = list(curr_bounds) + [(fractional_var, ">=", float(ceil_bnd))]

                stack.append(branch_left)
                stack.append(branch_right)

        final_obj = (best_obj if maximize else -best_obj) if best_x is not None else None
        return {
            "success": best_x is not None,
            "solution": best_x,
            "objective_value": round(final_obj, 6) if final_obj is not None else None,
            "nodes_explored": nodes_explored,
            "maximize": maximize,
        }


class AdaptiveSimulatedAnnealing:
    """Adaptive Simulated Annealing (ASA) with dynamic temperature and step size scaling."""

    def __init__(
        self,
        t_init: float = 100.0,
        t_min: float = 1e-4,
        alpha: float = 0.95,
        max_iter: int = 1000,
        seed: Optional[int] = 42,
    ):
        self.t_init = float(t_init)
        self.t_min = float(t_min)
        self.alpha = float(alpha)
        self.max_iter = int(max_iter)
        self.seed = seed

    def minimize(
        self,
        cost_func: Callable[[List[float]], float],
        bounds: List[Tuple[float, float]],
        x0: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Minimizes cost_func within coordinate bounds using adaptive annealing."""
        if self.seed is not None:
            random.seed(self.seed)

        n_dims = len(bounds)
        if x0 is not None:
            curr_x = list(x0)
        else:
            curr_x = [random.uniform(b[0], b[1]) for b in bounds]

        curr_cost = cost_func(curr_x)
        best_x = list(curr_x)
        best_cost = curr_cost

        T = self.t_init
        step_scale = 1.0
        accepted_moves = 0
        total_moves = 0

        for it in range(self.max_iter):
            if T < self.t_min:
                break

            # Propose candidate
            cand_x = []
            for i in range(n_dims):
                span = (bounds[i][1] - bounds[i][0]) * 0.1 * step_scale
                delta = random.uniform(-span, span)
                new_val = min(bounds[i][1], max(bounds[i][0], curr_x[i] + delta))
                cand_x.append(new_val)

            cand_cost = cost_func(cand_x)
            d_cost = cand_cost - curr_cost

            # Metropolis acceptance criterion
            total_moves += 1
            if d_cost < 0 or random.random() < math.exp(-d_cost / max(T, 1e-9)):
                curr_x = cand_x
                curr_cost = cand_cost
                accepted_moves += 1

                if curr_cost < best_cost:
                    best_x = list(curr_x)
                    best_cost = curr_cost

            # Dynamic step scale adaptation (every 20 steps)
            if total_moves % 20 == 0:
                acc_ratio = accepted_moves / 20.0
                accepted_moves = 0
                if acc_ratio > 0.5:
                    step_scale = min(2.0, step_scale * 1.1)
                elif acc_ratio < 0.2:
                    step_scale = max(0.1, step_scale * 0.9)

            # Cool temperature
            T *= self.alpha

        return {
            "optimal_x": [round(val, 6) for val in best_x],
            "optimal_cost": round(best_cost, 6),
            "iterations": total_moves,
            "final_temperature": round(T, 8),
        }


def opt_solve_interior_point(c: List[float], A: List[List[float]], b: List[float]) -> Dict[str, Any]:
    """Solves LP min c^T x s.t. Ax = b, x >= 0 via Primal-Dual Interior Point."""
    solver = PrimalDualInteriorPoint()
    return solver.solve(c, A, b)


def opt_branch_and_bound_milp(
    c: List[float],
    A_ub: List[List[float]],
    b_ub: List[float],
    integer_indices: Optional[List[int]] = None,
    maximize: bool = True,
) -> Dict[str, Any]:
    """Solves Mixed-Integer Linear Program using Branch and Bound."""
    milp = BranchAndBoundMILP()
    return milp.solve(c, A_ub, b_ub, integer_indices, maximize=maximize)


def opt_adaptive_simulated_annealing(
    cost_func: Callable[[List[float]], float],
    bounds: List[Tuple[float, float]],
    x0: Optional[List[float]] = None,
    max_iter: int = 500,
) -> Dict[str, Any]:
    """Runs adaptive simulated annealing optimizer."""
    asa = AdaptiveSimulatedAnnealing(max_iter=max_iter)
    return asa.minimize(cost_func, bounds, x0=x0)


class ParticleSwarmOptimizer:
    """Global swarm intelligence optimizer for continuous non-convex objective landscapes."""

    @classmethod
    def optimize(
        cls,
        objective_expr: str,
        bounds: List[List[float]],
        num_particles: int = 30,
        max_iterations: int = 50,
        c1: float = 1.5,
        c2: float = 1.5,
    ) -> Dict[str, Any]:
        dim = len(bounds)
        if dim == 0:
            return {"best_cost": 0.0, "best_position": [], "num_particles": 0, "iterations_completed": 0}

        low = [float(b[0]) for b in bounds]
        high = [float(b[1]) for b in bounds]
        v_max = [(high[i] - low[i]) * 0.2 for i in range(dim)]

        safe_globals = {
            "math": math,
            "sin": math.sin,
            "cos": math.cos,
            "exp": math.exp,
            "sqrt": math.sqrt,
            "pi": math.pi,
            "abs": abs,
        }

        compiled_expr = compile(objective_expr, "<pso_objective>", "eval")

        def evaluate(pos: List[float]) -> float:
            try:
                val = eval(compiled_expr, safe_globals, {"x": pos})
                return float(val)
            except Exception:
                return float("inf")

        import random
        rng = random.Random(42)

        positions = []
        velocities = []
        pbest_pos = []
        pbest_cost = []

        gbest_pos = None
        gbest_cost = float("inf")

        for _ in range(num_particles):
            pos = [low[i] + rng.random() * (high[i] - low[i]) for i in range(dim)]
            vel = [rng.uniform(-v_max[i], v_max[i]) for i in range(dim)]
            cost = evaluate(pos)

            positions.append(pos)
            velocities.append(vel)
            pbest_pos.append(list(pos))
            pbest_cost.append(cost)

            if cost < gbest_cost:
                gbest_cost = cost
                gbest_pos = list(pos)

        w_start, w_end = 0.9, 0.4
        for it in range(max_iterations):
            w = w_start - (w_start - w_end) * (it / max(max_iterations - 1, 1))

            for i in range(num_particles):
                for d in range(dim):
                    r1 = rng.random()
                    r2 = rng.random()
                    cog = c1 * r1 * (pbest_pos[i][d] - positions[i][d])
                    soc = c2 * r2 * (gbest_pos[d] - positions[i][d])
                    new_v = w * velocities[i][d] + cog + soc
                    new_v = max(-v_max[d], min(v_max[d], new_v))
                    velocities[i][d] = new_v

                    new_x = positions[i][d] + new_v
                    new_x = max(low[d], min(high[d], new_x))
                    positions[i][d] = new_x

                c_val = evaluate(positions[i])
                if c_val < pbest_cost[i]:
                    pbest_cost[i] = c_val
                    pbest_pos[i] = list(positions[i])
                    if c_val < gbest_cost:
                        gbest_cost = c_val
                        gbest_pos = list(positions[i])

        return {
            "best_cost": round(gbest_cost, 6),
            "best_position": [round(x, 6) for x in gbest_pos] if gbest_pos else [],
            "num_particles": num_particles,
            "iterations_completed": max_iterations,
            "dimensions": dim,
        }


class ActiveSetQuadraticProgramming:
    """Solves Convex Quadratic Programs via the Active Set Method."""

    @classmethod
    def solve(
        cls,
        q_matrix: List[List[float]],
        c_vec: List[float],
        ineq_matrix: Optional[List[List[float]]] = None,
        ineq_vec: Optional[List[float]] = None,
        eq_matrix: Optional[List[List[float]]] = None,
        eq_vec: Optional[List[float]] = None,
        max_iter: int = 40,
    ) -> Dict[str, Any]:
        n = len(c_vec)
        Q = [[float(x) for x in row] for row in q_matrix]
        c = [float(x) for x in c_vec]

        A_ineq = [[float(x) for x in row] for row in (ineq_matrix or [])]
        b_ineq = [float(x) for x in (ineq_vec or [])]
        m_ineq = len(b_ineq)

        A_eq = [[float(x) for x in row] for row in (eq_matrix or [])]
        b_eq = [float(x) for x in (eq_vec or [])]
        m_eq = len(b_eq)

        def solve_linear(A_mat: List[List[float]], b_v: List[float]) -> Optional[List[float]]:
            sz = len(b_v)
            mat = [list(row) for row in A_mat]
            rhs = list(b_v)
            for i in range(sz):
                piv = i
                for r in range(i + 1, sz):
                    if abs(mat[r][i]) > abs(mat[piv][i]):
                        piv = r
                if abs(mat[piv][i]) < 1e-12:
                    return None
                mat[i], mat[piv] = mat[piv], mat[i]
                rhs[i], rhs[piv] = rhs[piv], rhs[i]

                for r in range(i + 1, sz):
                    factor = mat[r][i] / mat[i][i]
                    for c_col in range(i + 1, sz):
                        mat[r][c_col] -= factor * mat[i][c_col]
                    rhs[r] -= factor * rhs[i]

            x_sol = [0.0] * sz
            for i in range(sz - 1, -1, -1):
                s = sum(mat[i][j] * x_sol[j] for j in range(i + 1, sz))
                x_sol[i] = (rhs[i] - s) / mat[i][i]
            return x_sol

        # Check if unconstrained minimizer is feasible
        x_unc = solve_linear(Q, [-v for v in c]) or [0.0] * n
        is_unc_feasible = True
        for i in range(m_ineq):
            if sum(A_ineq[i][j] * x_unc[j] for j in range(n)) > b_ineq[i] + 1e-8:
                is_unc_feasible = False
                break
        for i in range(m_eq):
            if abs(sum(A_eq[i][j] * x_unc[j] for j in range(n)) - b_eq[i]) > 1e-8:
                is_unc_feasible = False
                break

        if is_unc_feasible:
            final_obj = 0.5 * sum(x_unc[i] * Q[i][j] * x_unc[j] for i in range(n) for j in range(n)) + sum(c[i] * x_unc[i] for i in range(n))
            return {
                "optimal_x": [round(v, 6) for v in x_unc],
                "optimal_value": round(final_obj, 6),
                "active_constraints_count": 0,
                "converged": True,
            }

        x = [0.0] * n
        is_zero_feasible = True
        for i in range(m_ineq):
            if b_ineq[i] < -1e-8:
                is_zero_feasible = False
                break
        for i in range(m_eq):
            if abs(b_eq[i]) > 1e-8:
                is_zero_feasible = False
                break

        if not is_zero_feasible:
            for i in range(m_ineq):
                val = sum(A_ineq[i][j] * x[j] for j in range(n))
                if val > b_ineq[i]:
                    norm_sq = sum(a * a for a in A_ineq[i]) or 1.0
                    viol = val - b_ineq[i]
                    for j in range(n):
                        x[j] -= (viol / norm_sq) * A_ineq[i][j]

        working_set = []

        for _ in range(max_iter):
            g = [sum(Q[i][j] * x[j] for j in range(n)) + c[i] for i in range(n)]

            active_rows = [A_eq[i] for i in range(m_eq)] + [A_ineq[i] for i in working_set]
            m_active = len(active_rows)

            kkt_dim = n + m_active
            KKT = [[0.0] * kkt_dim for _ in range(kkt_dim)]
            kkt_rhs = [0.0] * kkt_dim

            for r in range(n):
                for col in range(n):
                    KKT[r][col] = Q[r][col]
                kkt_rhs[r] = -g[r]

            for idx, a_row in enumerate(active_rows):
                for col in range(n):
                    KKT[n + idx][col] = a_row[col]
                    KKT[col][n + idx] = a_row[col]
                kkt_rhs[n + idx] = 0.0

            sol = solve_linear(KKT, kkt_rhs)
            if sol is None:
                break

            p = sol[:n]
            lambdas = sol[n:]

            p_norm = math.sqrt(sum(v * v for v in p))
            if p_norm < 1e-7:
                ineq_lambdas = lambdas[m_eq:]
                min_lam = 0.0
                drop_idx = -1
                for j, lam in enumerate(ineq_lambdas):
                    if lam < min_lam:
                        min_lam = lam
                        drop_idx = j

                if drop_idx == -1 or min_lam >= -1e-6:
                    break
                else:
                    del working_set[drop_idx]
            else:
                alpha = 1.0
                blocking = -1
                for i in range(m_ineq):
                    if i not in working_set:
                        ap = sum(A_ineq[i][j] * p[j] for j in range(n))
                        if ap > 1e-9:
                            dist = (b_ineq[i] - sum(A_ineq[i][j] * x[j] for j in range(n))) / ap
                            if dist < alpha:
                                alpha = max(0.0, dist)
                                blocking = i

                for j in range(n):
                    x[j] += alpha * p[j]

                if blocking != -1:
                    working_set.append(blocking)

        final_obj = 0.5 * sum(x[i] * Q[i][j] * x[j] for i in range(n) for j in range(n)) + sum(c[i] * x[i] for i in range(n))

        return {
            "optimal_x": [round(v, 6) for v in x],
            "optimal_value": round(final_obj, 6),
            "active_constraints_count": len(working_set),
            "converged": True,
        }


def opt_particle_swarm_optimize(
    objective_expr: str,
    bounds: List[List[float]],
    num_particles: int = 30,
    max_iterations: int = 50,
) -> Any:
    """Optimizes continuous objective function using Particle Swarm Optimization."""
    return Record(ParticleSwarmOptimizer.optimize(
        objective_expr, bounds, num_particles=num_particles, max_iterations=max_iterations
    ))


def opt_solve_quadratic_program_active_set(
    q_matrix: List[List[float]],
    c_vec: List[float],
    ineq_matrix: Optional[List[List[float]]] = None,
    ineq_vec: Optional[List[float]] = None,
    eq_matrix: Optional[List[List[float]]] = None,
    eq_vec: Optional[List[float]] = None,
) -> Any:
    """Solves quadratic program using active set algorithm."""
    return Record(ActiveSetQuadraticProgramming.solve(
        q_matrix, c_vec, ineq_matrix=ineq_matrix, ineq_vec=ineq_vec, eq_matrix=eq_matrix, eq_vec=eq_vec
    ))


# ==============================================================================
# NELDER-MEAD SIMPLEX DIRECT SEARCH MINIMIZATION
# ==============================================================================

class NelderMeadSimplexDirectSearch:
    """Derivative-free multi-dimensional non-linear function minimization."""

    @staticmethod
    def _evaluate_fn(fn_or_expr: Any, pt: List[float]) -> float:
        if callable(fn_or_expr):
            return float(fn_or_expr(pt))
        if isinstance(fn_or_expr, str):
            # Parse variables e.g. x0, x1 or x, y, z
            env = {f"x{i}": pt[i] for i in range(len(pt))}
            if len(pt) >= 1:
                env["x"] = pt[0]
            if len(pt) >= 2:
                env["y"] = pt[1]
            if len(pt) >= 3:
                env["z"] = pt[2]
            env["math"] = math
            return float(eval(fn_or_expr, {"__builtins__": {}}, env))
        raise ValueError(f"Objective must be callable or expression string, got {type(fn_or_expr)}")

    @classmethod
    def minimize(
        cls,
        objective: Any,
        initial_point: List[float],
        step_size: float = 0.05,
        tol: float = 1e-6,
        max_iter: int = 200,
        alpha: float = 1.0,   # Reflection
        gamma: float = 2.0,   # Expansion
        beta: float = 0.5,    # Contraction
        delta: float = 0.5,   # Shrink
    ) -> Dict[str, Any]:
        x0 = [float(v) for v in initial_point]
        n = len(x0)

        # Initialize n+1 vertices
        vertices = [list(x0)]
        for i in range(n):
            v = list(x0)
            v[i] += step_size if abs(v[i]) < 1e-6 else (v[i] * step_size)
            vertices.append(v)

        values = [cls._evaluate_fn(objective, v) for v in vertices]

        iterations = 0
        converged = False

        while iterations < max_iter:
            iterations += 1

            # Order vertices: values[0] is best, values[-1] is worst
            order = sorted(range(n + 1), key=lambda idx: values[idx])
            vertices = [vertices[idx] for idx in order]
            values = [values[idx] for idx in order]

            # Standard deviation check on function values
            mean_val = sum(values) / (n + 1)
            variance = sum((v - mean_val) ** 2 for v in values) / (n + 1)
            std_dev = math.sqrt(variance)

            if std_dev < tol:
                converged = True
                break

            # Centroid of best n vertices (excluding worst vertex n)
            x_bar = [sum(vertices[i][d] for i in range(n)) / n for d in range(n)]

            # 1. Reflection
            x_worst = vertices[n]
            f_worst = values[n]
            f_second_worst = values[n - 1]
            f_best = values[0]

            x_r = [x_bar[d] + alpha * (x_bar[d] - x_worst[d]) for d in range(n)]
            f_r = cls._evaluate_fn(objective, x_r)

            if f_best <= f_r < f_second_worst:
                # Accept reflection
                vertices[n] = x_r
                values[n] = f_r
                continue

            # 2. Expansion
            if f_r < f_best:
                x_e = [x_bar[d] + gamma * (x_r[d] - x_bar[d]) for d in range(n)]
                f_e = cls._evaluate_fn(objective, x_e)
                if f_e < f_r:
                    vertices[n] = x_e
                    values[n] = f_e
                else:
                    vertices[n] = x_r
                    values[n] = f_r
                continue

            # 3. Contraction
            if f_r < f_worst:
                # Outside contraction
                x_c = [x_bar[d] + beta * (x_r[d] - x_bar[d]) for d in range(n)]
                f_c = cls._evaluate_fn(objective, x_c)
                if f_c <= f_r:
                    vertices[n] = x_c
                    values[n] = f_c
                    continue
            else:
                # Inside contraction
                x_c = [x_bar[d] - beta * (x_bar[d] - x_worst[d]) for d in range(n)]
                f_c = cls._evaluate_fn(objective, x_c)
                if f_c < f_worst:
                    vertices[n] = x_c
                    values[n] = f_c
                    continue

            # 4. Shrink all towards best vertex vertices[0]
            for i in range(1, n + 1):
                vertices[i] = [vertices[0][d] + delta * (vertices[i][d] - vertices[0][d]) for d in range(n)]
                values[i] = cls._evaluate_fn(objective, vertices[i])

        best_idx = 0
        return {
            "optimal_x": [round(v, 6) for v in vertices[best_idx]],
            "optimal_value": round(values[best_idx], 6),
            "iterations": iterations,
            "converged": converged,
            "standard_deviation": round(std_dev, 8),
        }


# ==============================================================================
# PRIMAL-DUAL INTERIOR POINT METHOD FOR LINEAR PROGRAMMING
# ==============================================================================

class InteriorPointPrimalDualLP:
    """Mehrotra Predictor-Corrector style Primal-Dual Interior Point Method for min c^T x s.t. Ax = b, x >= 0."""

    @staticmethod
    def _solve_system(A: List[List[float]], b: List[float]) -> List[float]:
        """Solves A x = b via Gaussian elimination with partial pivoting."""
        n = len(A)
        aug = [list(A[i]) + [b[i]] for i in range(n)]

        for c in range(n):
            pivot = max(range(c, n), key=lambda r: abs(aug[r][c]))
            if abs(aug[pivot][c]) < 1e-12:
                # Add small ridge
                aug[c][c] += 1e-6
            else:
                aug[c], aug[pivot] = aug[pivot], aug[c]

            pv = aug[c][c]
            for j in range(c, n + 1):
                aug[c][j] /= pv

            for r in range(n):
                if r != c:
                    factor = aug[r][c]
                    for j in range(c, n + 1):
                        aug[r][j] -= factor * aug[c][j]

        return [aug[i][n] for i in range(n)]

    @classmethod
    def solve(
        cls,
        c_vec: List[float],
        a_matrix: List[List[float]],
        b_vec: List[float],
        max_iter: int = 100,
        tol: float = 1e-6,
    ) -> Dict[str, Any]:
        """Solves standard form linear program: min c^T x s.t. A x = b, x >= 0."""
        c = [float(v) for v in c_vec]
        b = [float(v) for v in b_vec]
        A = [[float(v) for v in row] for row in a_matrix]

        m = len(A)     # Number of equality constraints
        n = len(c)     # Number of variables

        # Strictly feasible interior starting point (x > 0, s > 0)
        x = [1.0] * n
        y = [0.0] * m
        s = [1.0] * n

        iterations = 0
        converged = False

        while iterations < max_iter:
            iterations += 1

            # Primal residual: r_p = b - A*x
            rp = [b[i] - sum(A[i][j] * x[j] for j in range(n)) for i in range(m)]

            # Dual residual: r_d = c - A^T*y - s
            rd = [c[j] - sum(A[i][j] * y[i] for i in range(m)) - s[j] for j in range(n)]

            # Complementarity gap: mu = (x^T * s) / n
            mu = sum(x[j] * s[j] for j in range(n)) / n

            norm_rp = math.sqrt(sum(v * v for v in rp))
            norm_rd = math.sqrt(sum(v * v for v in rd))

            if mu < tol and norm_rp < tol and norm_rd < tol:
                converged = True
                break

            # Normal matrix M = A * S^(-1) * X * A^T
            # D = X / S
            d = [x[j] / max(1e-12, s[j]) for j in range(n)]

            # Predictor step (affine scaling, sigma = 0)
            # r_xs = -x .* s
            r_xs = [-x[j] * s[j] for j in range(n)]

            # Form normal equations: M * dy = rhs
            # rhs = rp + A * S^(-1) * (r_xs - X * rd) = rp + A * (S^(-1)*r_xs - D * rd)
            # S^(-1)*r_xs = -x
            vec_temp = [-x[j] - d[j] * rd[j] for j in range(n)]
            rhs = [rp[i] + sum(A[i][j] * vec_temp[j] for j in range(n)) for i in range(m)]

            M = [[sum(A[i][k] * d[k] * A[j][k] for k in range(n)) for j in range(m)] for i in range(m)]
            # Ridge regularization for positive definiteness
            for i in range(m):
                M[i][i] += 1e-9

            dy_aff = cls._solve_system(M, rhs)
            ds_aff = [rd[j] - sum(A[i][j] * dy_aff[i] for i in range(m)) for j in range(n)]
            dx_aff = [(-r_xs[j] - x[j] * ds_aff[j]) / max(1e-12, s[j]) for j in range(n)]

            # Step lengths for affine scaling
            alpha_p_aff = 1.0
            alpha_d_aff = 1.0
            for j in range(n):
                if dx_aff[j] < 0:
                    alpha_p_aff = min(alpha_p_aff, -x[j] / dx_aff[j])
                if ds_aff[j] < 0:
                    alpha_d_aff = min(alpha_d_aff, -s[j] / ds_aff[j])

            # Centering parameter sigma via Mehrotra heuristic
            mu_aff = sum((x[j] + alpha_p_aff * dx_aff[j]) * (s[j] + alpha_d_aff * ds_aff[j]) for j in range(n)) / n
            sigma = (mu_aff / max(1e-12, mu)) ** 3
            sigma = min(1.0, max(0.0, sigma))

            # Corrector + Centering step
            # r_xs_comb = sigma*mu - x.*s - dx_aff .* ds_aff
            r_xs_comb = [sigma * mu - x[j] * s[j] - dx_aff[j] * ds_aff[j] for j in range(n)]
            vec_temp2 = [(r_xs_comb[j] - x[j] * rd[j]) / max(1e-12, s[j]) for j in range(n)]
            rhs2 = [rp[i] + sum(A[i][j] * vec_temp2[j] for j in range(n)) for i in range(m)]

            dy = cls._solve_system(M, rhs2)
            ds = [rd[j] - sum(A[i][j] * dy[i] for i in range(m)) for j in range(n)]
            dx = [(r_xs_comb[j] - x[j] * ds[j]) / max(1e-12, s[j]) for j in range(n)]

            # Safe step length with fraction-to-boundary rule (gamma = 0.99)
            gamma_step = 0.99
            alpha_p = 1.0
            alpha_d = 1.0
            for j in range(n):
                if dx[j] < 0:
                    alpha_p = min(alpha_p, gamma_step * (-x[j] / dx[j]))
                if ds[j] < 0:
                    alpha_d = min(alpha_d, gamma_step * (-s[j] / ds[j]))

            # Update iterates
            for j in range(n):
                x[j] = max(1e-12, x[j] + alpha_p * dx[j])
                s[j] = max(1e-12, s[j] + alpha_d * ds[j])
            for i in range(m):
                y[i] += alpha_d * dy[i]

        opt_val = sum(c[j] * x[j] for j in range(n))

        return {
            "optimal_x": [round(v, 6) for v in x],
            "optimal_value": round(opt_val, 6),
            "dual_y": [round(v, 6) for v in y],
            "slack_s": [round(v, 6) for v in s],
            "duality_gap": round(mu, 8),
            "iterations": iterations,
            "converged": converged,
        }


def opt_nelder_mead_minimize(
    objective: Any,
    initial_point: List[float],
    step_size: float = 0.05,
    tol: float = 1e-6,
    max_iter: int = 200,
) -> Record:
    """Minimizes continuous function using derivative-free Nelder-Mead simplex algorithm."""
    return Record(NelderMeadSimplexDirectSearch.minimize(
        objective, initial_point, step_size=step_size, tol=tol, max_iter=max_iter
    ))


def opt_interior_point_solve_lp(
    c_vec: List[float],
    a_matrix: List[List[float]],
    b_vec: List[float],
    max_iter: int = 100,
    tol: float = 1e-6,
) -> Record:
    """Solves canonical linear program min c^T x s.t. Ax = b, x >= 0 via Primal-Dual Interior Point."""
    return Record(InteriorPointPrimalDualLP.solve(
        c_vec, a_matrix, b_vec, max_iter=max_iter, tol=tol
    ))


# ==============================================================================
# COVARIANCE MATRIX ADAPTATION EVOLUTION STRATEGY (CMA-ES)
# ==============================================================================

class CMAESContinuousOptimization:
    """Covariance Matrix Adaptation Evolution Strategy for non-convex continuous optimization."""

    @staticmethod
    def _evaluate_fn(fn_or_expr: Any, pt: List[float]) -> float:
        if callable(fn_or_expr):
            return float(fn_or_expr(pt))
        if isinstance(fn_or_expr, str):
            env = {f"x{i}": pt[i] for i in range(len(pt))}
            if len(pt) >= 1:
                env["x"] = pt[0]
            if len(pt) >= 2:
                env["y"] = pt[1]
            if len(pt) >= 3:
                env["z"] = pt[2]
            env["math"] = math
            return float(eval(fn_or_expr, {"__builtins__": {}}, env))
        raise ValueError(f"Objective must be callable or expression string, got {type(fn_or_expr)}")

    @classmethod
    def optimize(
        cls,
        objective: Any,
        initial_mean: List[float],
        initial_sigma: float = 0.5,
        population_size: int = 12,
        max_generations: int = 40,
    ) -> Dict[str, Any]:
        dim = len(initial_mean)
        m = [float(v) for v in initial_mean]
        sigma = float(initial_sigma)
        lam = max(4, int(population_size))
        mu = lam // 2

        # Recombination weights
        raw_weights = [math.log(mu + 0.5) - math.log(i + 1) for i in range(mu)]
        sum_w = sum(raw_weights)
        weights = [w / sum_w for w in raw_weights]
        mueff = 1.0 / sum(w ** 2 for w in weights)

        # Strategy parameters
        cc = (4.0 + mueff / dim) / (dim + 4.0 + 2.0 * mueff / dim)
        cs = (mueff + 2.0) / (dim + mueff + 5.0)
        c1 = 2.0 / ((dim + 1.3) ** 2 + mueff)
        cmu = min(1.0 - c1, 2.0 * (mueff - 2.0 + 1.0 / mueff) / ((dim + 2.0) ** 2 + mueff))
        damps = 1.0 + 2.0 * max(0.0, math.sqrt((mueff - 1.0) / (dim + 1.0)) - 1.0) + cs
        chi_n = math.sqrt(dim) * (1.0 - 1.0 / (4.0 * dim) + 1.0 / (21.0 * (dim ** 2)))

        # Evolution paths
        ps = [0.0] * dim
        pc = [0.0] * dim

        # Covariance matrix C initialized to identity
        C = [[1.0 if i == j else 0.0 for j in range(dim)] for i in range(dim)]

        best_x = list(m)
        best_val = cls._evaluate_fn(objective, m)
        history = []

        rnd = random.Random(42)

        for gen in range(1, max_generations + 1):
            # Sample lambda candidates: x_k = m + sigma * y_k
            # Approximation: sample standard normals and scale by diagonal approximation / C
            # Using Cholesky approximation of C:
            # L such that L L^T = C
            L = [[0.0] * dim for _ in range(dim)]
            for i in range(dim):
                for j in range(i + 1):
                    s_sum = sum(L[i][k] * L[j][k] for k in range(j))
                    if i == j:
                        val = C[i][i] - s_sum
                        L[i][j] = math.sqrt(max(1e-9, val))
                    else:
                        L[i][j] = (C[i][j] - s_sum) / max(1e-9, L[j][j])

            pop = []
            z_vectors = []
            for _ in range(lam):
                z = [rnd.gauss(0.0, 1.0) for _ in range(dim)]
                # y = L * z
                y = [sum(L[i][j] * z[j] for j in range(i + 1)) for i in range(dim)]
                cand = [m[i] + sigma * y[i] for i in range(dim)]
                f_val = cls._evaluate_fn(objective, cand)
                pop.append((cand, y, f_val))
                z_vectors.append(z)

            # Sort population by fitness
            pop.sort(key=lambda item: item[2])
            if pop[0][2] < best_val:
                best_val = pop[0][2]
                best_x = list(pop[0][0])

            history.append(round(best_val, 6))

            # Update mean: m_new = m + sigma * sum(w_i * y_i)
            y_w = [sum(weights[i] * pop[i][1][d] for i in range(mu)) for d in range(dim)]
            m = [m[d] + sigma * y_w[d] for d in range(dim)]

            # Update evolution paths
            # ps = (1 - cs)*ps + sqrt(cs*(2-cs)*mueff) * z_w
            z_w = [sum(weights[i] * z_vectors[i][d] for i in range(mu)) for d in range(dim)]
            for d in range(dim):
                ps[d] = (1.0 - cs) * ps[d] + math.sqrt(cs * (2.0 - cs) * mueff) * z_w[d]

            norm_ps = math.sqrt(sum(v * v for v in ps))

            # Threshold for pc update
            h_sig = 1.0 if (norm_ps / math.sqrt(1.0 - (1.0 - cs) ** (2.0 * gen))) < (1.4 + 2.0 / (dim + 1.0)) * chi_n else 0.0

            for d in range(dim):
                pc[d] = (1.0 - cc) * pc[d] + h_sig * math.sqrt(cc * (2.0 - cc) * mueff) * y_w[d]

            # Update Covariance matrix C
            # C = (1 - c1 - cmu)*C + c1*(pc*pc^T + (1-h_sig)*cc*(2-cc)*C) + cmu*sum(w_i * y_i * y_i^T)
            for i in range(dim):
                for j in range(dim):
                    rank_mu_term = sum(weights[k] * pop[k][1][i] * pop[k][1][j] for k in range(mu))
                    C[i][j] = (
                        (1.0 - c1 - cmu) * C[i][j]
                        + c1 * (pc[i] * pc[j] + (1.0 - h_sig) * cc * (2.0 - cc) * C[i][j])
                        + cmu * rank_mu_term
                    )

            # Update step size sigma
            sigma *= math.exp((cs / damps) * (norm_ps / chi_n - 1.0))
            sigma = max(1e-12, min(100.0, sigma))

        return {
            "optimal_x": [round(v, 6) for v in best_x],
            "optimal_value": round(best_val, 6),
            "final_sigma": round(sigma, 6),
            "generations": max_generations,
            "convergence_history": history,
        }


def opt_cma_es_optimize(
    objective: Any,
    initial_mean: List[float],
    initial_sigma: float = 0.5,
    population_size: int = 12,
    max_generations: int = 40,
) -> Record:
    """Optimizes continuous objective using Covariance Matrix Adaptation Evolution Strategy (CMA-ES)."""
    return Record(CMAESContinuousOptimization.optimize(
        objective, initial_mean, initial_sigma=initial_sigma, population_size=population_size, max_generations=max_generations
    ))


class NelderMeadSimplexOptimizer:
    """Direct search Nelder-Mead Downhill Simplex Optimization Algorithm.

    Solves unconstrained continuous non-linear minimization problems without requiring
    derivatives using geometric simplex reflection, expansion, contraction, and shrink operations.
    """

    @classmethod
    def _eval(cls, func: Any, x: List[float]) -> float:
        if callable(func):
            return float(func(x))
        if isinstance(func, str):
            env = {f"x{i}": x[i] for i in range(len(x))}
            if len(x) >= 1:
                env["x"] = x[0]
            if len(x) >= 2:
                env["y"] = x[1]
            if len(x) >= 3:
                env["z"] = x[2]
            env["math"] = math
            expr = func.replace("^", "**")
            return float(eval(expr, {"__builtins__": {}}, env))
        return 0.0

    @classmethod
    def minimize(
        cls,
        objective: Any,
        initial_point: List[float],
        step_size: float = 1.0,
        tol: float = 1e-6,
        max_iter: int = 250,
        alpha: float = 1.0,   # Reflection
        gamma: float = 2.0,   # Expansion
        rho: float = 0.5,     # Contraction
        sigma: float = 0.5,   # Shrink
    ) -> Dict[str, Any]:
        """Minimizes objective starting from initial_point."""
        n = len(initial_point)
        # 1. Initialize simplex with n+1 vertices
        simplex: List[List[float]] = [list(initial_point)]
        for i in range(n):
            vertex = list(initial_point)
            vertex[i] += step_size if vertex[i] == 0.0 else vertex[i] * 0.05 + step_size * 0.1
            simplex.append(vertex)

        values = [cls._eval(objective, v) for v in simplex]
        iterations = 0

        for it in range(max_iter):
            iterations += 1
            # Sort simplex vertices by objective value ascending
            order = sorted(range(n + 1), key=lambda idx: values[idx])
            simplex = [simplex[idx] for idx in order]
            values = [values[idx] for idx in order]

            f_best = values[0]
            f_worst = values[-1]
            f_second_worst = values[-2]

            # Check convergence: simplex standard deviation
            mean_f = sum(values) / (n + 1)
            std_f = math.sqrt(sum((v - mean_f) ** 2 for v in values) / (n + 1))
            if std_f < tol:
                break

            # Centroid of best n vertices (excluding worst)
            x0 = [sum(simplex[i][d] for i in range(n)) / n for d in range(n)]

            # 2. Reflection
            xr = [x0[d] + alpha * (x0[d] - simplex[-1][d]) for d in range(n)]
            fr = cls._eval(objective, xr)

            if f_best <= fr < f_second_worst:
                simplex[-1] = xr
                values[-1] = fr
                continue

            # 3. Expansion
            if fr < f_best:
                xe = [x0[d] + gamma * (xr[d] - x0[d]) for d in range(n)]
                fe = cls._eval(objective, xe)
                if fe < fr:
                    simplex[-1] = xe
                    values[-1] = fe
                else:
                    simplex[-1] = xr
                    values[-1] = fr
                continue

            # 4. Contraction
            if fr < f_worst:
                # Outside contraction
                xc = [x0[d] + rho * (xr[d] - x0[d]) for d in range(n)]
                fc = cls._eval(objective, xc)
                if fc <= fr:
                    simplex[-1] = xc
                    values[-1] = fc
                    continue
            else:
                # Inside contraction
                xc = [x0[d] - rho * (x0[d] - simplex[-1][d]) for d in range(n)]
                fc = cls._eval(objective, xc)
                if fc < f_worst:
                    simplex[-1] = xc
                    values[-1] = fc
                    continue

            # 5. Shrink towards best vertex
            for i in range(1, n + 1):
                simplex[i] = [simplex[0][d] + sigma * (simplex[i][d] - simplex[0][d]) for d in range(n)]
                values[i] = cls._eval(objective, simplex[i])

        best_x = simplex[0]
        best_val = values[0]
        radius = max(math.hypot(*(simplex[i][d] - simplex[0][d] for d in range(n))) for i in range(1, n + 1))

        return {
            "optimal_x": [round(coord, 6) for coord in best_x],
            "optimal_value": round(best_val, 6),
            "iterations": iterations,
            "converged": iterations < max_iter,
            "simplex_radius": round(radius, 6),
        }


class SequentialQuadraticProgrammingSQP:
    """Sequential Quadratic Programming (SQP) Non-Linear Constrained Optimizer.

    Solves non-linear optimization problems with general non-linear equality and
    inequality constraints using iterative quadratic subproblems and BFGS Hessian updates.
    """

    @classmethod
    def _eval(cls, func: Any, x: List[float]) -> float:
        if callable(func):
            return float(func(x))
        if isinstance(func, str):
            env = {f"x{i}": x[i] for i in range(len(x))}
            if len(x) >= 1:
                env["x"] = x[0]
            if len(x) >= 2:
                env["y"] = x[1]
            if len(x) >= 3:
                env["z"] = x[2]
            env["math"] = math
            expr = func.replace("^", "**")
            return float(eval(expr, {"__builtins__": {}}, env))
        return 0.0

    @classmethod
    def _gradient(cls, func: Any, x: List[float], h: float = 1e-6) -> List[float]:
        n = len(x)
        grad = [0.0] * n
        for i in range(n):
            xp = list(x)
            xm = list(x)
            xp[i] += h
            xm[i] -= h
            grad[i] = (cls._eval(func, xp) - cls._eval(func, xm)) / (2.0 * h)
        return grad

    @classmethod
    def optimize(
        cls,
        objective: Any,
        initial_point: List[float],
        eq_constraints: Optional[List[Any]] = None,
        ineq_constraints: Optional[List[Any]] = None,
        max_iter: int = 50,
        tol: float = 1e-5,
    ) -> Dict[str, Any]:
        """Performs SQP constrained optimization."""
        x = [float(v) for v in initial_point]
        n = len(x)
        eqs = eq_constraints or []
        ineqs = ineq_constraints or []

        # Initialize Hessian approximation B as identity matrix
        B = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

        converged = False
        iterations = 0

        for it in range(max_iter):
            iterations += 1
            f_val = cls._eval(objective, x)
            grad_f = cls._gradient(objective, x)

            # Evaluate constraints
            h_vals = [cls._eval(c, x) for c in eqs]
            g_vals = [cls._eval(c, x) for c in ineqs]

            max_violation = max(
                ([abs(v) for v in h_vals] + [max(0.0, v) for v in g_vals]) if (h_vals or g_vals) else [0.0]
            )

            grad_norm = math.sqrt(sum(g ** 2 for g in grad_f))
            if grad_norm < tol and max_violation < tol:
                converged = True
                break

            # Compute constraint gradients (Jacobian)
            A_eq = [cls._gradient(c, x) for c in eqs]
            A_ineq = [cls._gradient(c, x) for c in ineqs]

            # Solve QP direction via active set penalty formulation
            # Minimize 0.5 * d^T B d + grad_f^T d + penalty * (eq_viol^2 + ineq_viol^2)
            # Analytic regularized least-squares direction d
            penalty = 100.0
            M = [[B[i][j] for j in range(n)] for i in range(n)]
            rhs = [-grad_f[i] for i in range(n)]

            # Add equality constraint linearization penalty: penalty * (A_eq^T A_eq) d = -penalty * A_eq^T h
            for k in range(len(eqs)):
                ak = A_eq[k]
                hk = h_vals[k]
                for i in range(n):
                    rhs[i] -= penalty * ak[i] * hk
                    for j in range(n):
                        M[i][j] += penalty * ak[i] * ak[j]

            # Add active inequality constraint linearization penalty
            for k in range(len(ineqs)):
                gk = g_vals[k]
                ak = A_ineq[k]
                if gk > -1e-4:  # Active or violated
                    for i in range(n):
                        rhs[i] -= penalty * ak[i] * max(0.0, gk)
                        for j in range(n):
                            M[i][j] += penalty * ak[i] * ak[j]

            # Add Tikhonov regularization
            for i in range(n):
                M[i][i] += 1e-4

            # Solve M * d = rhs via Gaussian elimination
            aug = [M[i] + [rhs[i]] for i in range(n)]
            d = [0.0] * n
            for i in range(n):
                piv = aug[i][i]
                if abs(piv) < 1e-9:
                    piv = 1e-4
                for c in range(i, n + 1):
                    aug[i][c] /= piv
                for r in range(n):
                    if r != i:
                        fact = aug[r][i]
                        for c in range(i, n + 1):
                            aug[r][c] -= fact * aug[i][c]
            d = [aug[i][n] for i in range(n)]

            # Backtracking line search with L1 merit function
            alpha_step = 1.0
            merit_penalty = 10.0 + max_violation * 5.0
            merit_x = f_val + merit_penalty * (sum(abs(v) for v in h_vals) + sum(max(0.0, v) for v in g_vals))

            best_x_trial = list(x)
            for _ in range(12):
                x_trial = [x[i] + alpha_step * d[i] for i in range(n)]
                f_trial = cls._eval(objective, x_trial)
                h_trial = [cls._eval(c, x_trial) for c in eqs]
                g_trial = [cls._eval(c, x_trial) for c in ineqs]
                merit_trial = f_trial + merit_penalty * (
                    sum(abs(v) for v in h_trial) + sum(max(0.0, v) for v in g_trial)
                )
                if merit_trial < merit_x or alpha_step < 1e-4:
                    best_x_trial = x_trial
                    break
                alpha_step *= 0.5

            s = [best_x_trial[i] - x[i] for i in range(n)]
            x = best_x_trial

            # BFGS update of Hessian B
            grad_new = cls._gradient(objective, x)
            y = [grad_new[i] - grad_f[i] for i in range(n)]

            Bs = [sum(B[i][j] * s[j] for j in range(n)) for i in range(n)]
            sBs = sum(s[i] * Bs[i] for i in range(n))
            sy = sum(s[i] * y[i] for i in range(n))

            if sy > 1e-6 and sBs > 1e-6:
                for i in range(n):
                    for j in range(n):
                        B[i][j] += (y[i] * y[j]) / sy - (Bs[i] * Bs[j]) / sBs

        final_f = cls._eval(objective, x)
        final_h = [round(cls._eval(c, x), 5) for c in eqs]
        final_g = [round(cls._eval(c, x), 5) for c in ineqs]
        max_viol = max(([abs(v) for v in final_h] + [max(0.0, v) for v in final_g]) if (final_h or final_g) else [0.0])

        return {
            "optimal_x": [round(val, 6) for val in x],
            "optimal_value": round(final_f, 6),
            "equality_violations": final_h,
            "inequality_violations": final_g,
            "max_constraint_violation": round(max_viol, 6),
            "iterations": iterations,
            "converged": max_viol < 0.05 and iterations < max_iter,
        }


def opt_nelder_mead_minimize(
    objective: Any,
    initial_point: List[float],
    step_size: float = 1.0,
    tol: float = 1e-6,
    max_iter: int = 250,
) -> Record:
    """Minimizes continuous objective via Nelder-Mead simplex algorithm."""
    return Record(NelderMeadSimplexOptimizer.minimize(
        objective, initial_point, step_size=step_size, tol=tol, max_iter=max_iter
    ))


def opt_sqp_optimize(
    objective: Any,
    initial_point: List[float],
    eq_constraints: Optional[List[Any]] = None,
    ineq_constraints: Optional[List[Any]] = None,
    max_iter: int = 50,
    tol: float = 1e-5,
) -> Record:
    """Solves non-linear constrained optimization via Sequential Quadratic Programming (SQP)."""
    return Record(SequentialQuadraticProgrammingSQP.optimize(
        objective, initial_point, eq_constraints=eq_constraints, ineq_constraints=ineq_constraints, max_iter=max_iter, tol=tol
    ))








def execute_opt_ir(spec: Any) -> Any:
    """Executes an optimization IR spec in the caller's scope."""
    import sys
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = OptRuntime().execute_ir(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


# ==============================================================================
# GLOBAL OPTIMIZATION: DIFFERENTIAL EVOLUTION (DE/rand/1/bin) & TSP SOLVER
# ==============================================================================

class DifferentialEvolutionOptimizer:
    """Storn & Price DE/rand/1/bin continuous global optimization algorithm."""

    @classmethod
    def optimize(
        cls,
        objective_func,
        bounds: List[Tuple[float, float]],
        pop_size: int = 15,
        f_mut: float = 0.8,
        cr: float = 0.7,
        max_generations: int = 60,
        seed: int = 42,
    ) -> Dict[str, Any]:
        import random
        rng = random.Random(seed)
        dims = len(bounds)
        if dims == 0:
            return {"best_vector": [], "best_fitness": 0.0}

        # Initialize population
        pop = []
        for _ in range(pop_size):
            ind = [bounds[d][0] + rng.random() * (bounds[d][1] - bounds[d][0]) for d in range(dims)]
            pop.append(ind)

        fitness = [float(objective_func(ind)) for ind in pop]
        best_idx = min(range(pop_size), key=lambda i: fitness[i])
        best_vector = list(pop[best_idx])
        best_fitness = fitness[best_idx]

        for _gen in range(max_generations):
            for i in range(pop_size):
                # Pick 3 distinct random candidates != i
                idxs = [idx for idx in range(pop_size) if idx != i]
                r1, r2, r3 = rng.sample(idxs, 3)

                # Mutation: mutant = x_r1 + F * (x_r2 - x_r3)
                mutant = []
                for d in range(dims):
                    val = pop[r1][d] + f_mut * (pop[r2][d] - pop[r3][d])
                    # Bound clamping
                    val = max(bounds[d][0], min(bounds[d][1], val))
                    mutant.append(val)

                # Crossover
                j_rand = rng.randint(0, dims - 1)
                trial = []
                for d in range(dims):
                    if rng.random() < cr or d == j_rand:
                        trial.append(mutant[d])
                    else:
                        trial.append(pop[i][d])

                # Selection
                trial_fitness = float(objective_func(trial))
                if trial_fitness <= fitness[i]:
                    pop[i] = trial
                    fitness[i] = trial_fitness
                    if trial_fitness < best_fitness:
                        best_fitness = trial_fitness
                        best_vector = list(trial)

        return {
            "best_solution": best_vector,
            "best_value": best_fitness,
            "generations": max_generations,
        }


def opt_differential_evolution(objective_func, bounds: List[Tuple[float, float]], max_iter: int = 50) -> Record:
    """Optimizes continuous objective function using Differential Evolution."""
    return Record(DifferentialEvolutionOptimizer.optimize(objective_func, bounds, max_generations=max_iter))
