"""Runtime execution engine and Simplex Linear Programming Solver."""

import math
import re
from typing import Any, Dict, List, Optional, Tuple, Set
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec


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
    if isinstance(spec_or_name, LinearProgramSpec):
        spec = spec_or_name
    elif isinstance(spec_or_name, dict) and "_spec" in spec_or_name:
        spec = spec_or_name["_spec"]
    elif isinstance(spec_or_name, str) and scope:
        val = scope.get(spec_or_name)
        if isinstance(val, LinearProgramSpec):
            spec = val
        elif isinstance(val, dict) and "_spec" in val:
            spec = val["_spec"]
        else:
            raise ValueError(f"Linear program '{spec_or_name}' not found in scope")
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
