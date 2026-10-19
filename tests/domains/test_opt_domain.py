"""Unit and integration tests for Optimization & Operations Research domain (use opt)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.opt.runtime import (
    solve_linear_program,
    parse_linear_expression,
    SimplexSolver,
)


def test_simplex_solver_production_plan():
    # Maximize 3x + 5y
    # Subject to:
    # 2x + y <= 100
    # x + 2y <= 80
    # x, y >= 0
    solver = SimplexSolver(
        sense="maximize",
        objective={"x": 3.0, "y": 5.0},
        constraints=[
            ({"x": 2.0, "y": 1.0}, "<=", 100.0),
            ({"x": 1.0, "y": 2.0}, "<=", 80.0),
        ],
    )
    res = solver.solve()
    assert res["status"] == "optimal"
    assert abs(res["variables"]["x"] - 40.0) < 1e-3
    assert abs(res["variables"]["y"] - 20.0) < 1e-3
    assert abs(res["optimal_value"] - 220.0) < 1e-3


def test_simplex_solver_diet_minimization():
    # Minimize 2x + 3y
    # Subject to:
    # x + y >= 10
    # 2x + y >= 12
    # x, y >= 0
    solver = SimplexSolver(
        sense="minimize",
        objective={"x": 2.0, "y": 3.0},
        constraints=[
            ({"x": 1.0, "y": 1.0}, ">=", 10.0),
            ({"x": 2.0, "y": 1.0}, ">=", 12.0),
        ],
    )
    res = solver.solve()
    assert res["status"] == "optimal"
    # At x=10, y=0: 2(10) + 3(0) = 20.
    # At x=2, y=8: 2(2) + 3(8) = 28.
    # At x=12, y=0: cost is 24.
    # Minimum is 20 at x=10, y=0
    assert abs(res["optimal_value"] - 20.0) < 1e-3
    assert abs(res["variables"]["x"] - 10.0) < 1e-3


def test_opt_domain_block_execution():
    source = """use opt

linear program factory_plan:
    maximize: 4 * chairs + 3 * tables
    subject to:
        2 * chairs + 1 * tables <= 40
        1 * chairs + 2 * tables <= 50

solve linear program factory_plan into optimal_factory
"""
    env = execute(source)
    assert "factory_plan" in env
    assert "optimal_factory" in env
    opt = env["optimal_factory"]
    assert opt["status"] == "optimal"
    assert "chairs" in opt["variables"]
    assert "tables" in opt["variables"]
    assert opt["optimal_value"] > 0


def test_opt_domain_ast_export():
    source = """use opt

linear program plan:
    maximize: 2 * x + 3 * y
    subject to:
        x + y <= 10

solve plan into res
"""
    py_code = export_to_python(source)
    assert "solve_linear_program" in py_code or "linprog" in py_code
