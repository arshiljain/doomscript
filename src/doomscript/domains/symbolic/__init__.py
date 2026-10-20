"""Symbolic Mathematics & Computer Algebra Domain Pack for DoomScript.

Enables native spoken-English analytical differentiation, algebraic simplification,
and expression evaluation via 'use symbolic'.
"""

from typing import List, Optional, Dict, Any
from doomscript.domains.base import (
    DomainContract,
    DomainRuntime,
    DomainIR,
    VerbSpec,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.symbolic.runtime import (
    Expr,
    Constant,
    Symbol,
    Add,
    Mul,
    Pow,
    Sin,
    Cos,
    Ln,
    Exp,
    ExpressionParser,
    PolyOps,
    symbolic_parse,
    symbolic_diff,
    symbolic_simplify,
    symbolic_eval,
    symbolic_poly_gcd,
    SymbolicIntegrator,
    TaylorSeries,
    ExactRationalLinearSolver,
    symbolic_integrate,
    symbolic_taylor_series,
    symbolic_solve_rational_linear,
    PolynomialGCDAndRoots,
    BrentRootFinder,
    symbolic_polynomial_gcd,
    symbolic_rational_roots,
    symbolic_brent_root,
    UnivariatePolynomialEuclideanFactorizer,
    PadeApproximantGenerator,
    symbolic_square_free_factorization,
    symbolic_polynomial_resultant,
    symbolic_pade_approximant,
    GroebnerBasisBuchberger,
    symbolic_groebner_basis,
    symbolic_eliminate_variables,
    RischNormanSymbolicIntegrator,
    SymbolicDifferentialEquationODESolver,
    symbolic_risch_integrate,
    symbolic_ode_solve,
)
from doomscript.domains.symbolic.parser import SymbolicDomainParser
from doomscript.domains.symbolic.exporter import SymbolicASTExporter


class SymbolicRuntime(DomainRuntime):
    """Runtime coordinator for symbolic algebra routines."""

    def execute_ir(self, ir: DomainIR, env: Dict[str, Any]) -> Any:
        return None


class SymbolicDomain(DomainContract):
    """Domain contract for Symbolic Mathematics & Computer Algebra."""

    name = "symbolic"
    aliases = ["cas", "algebra", "calculus", "diff"]
    description = "Exact analytical differentiation, algebraic simplification, polynomial arithmetic, and GCD"
    parser = SymbolicDomainParser()
    runtime = SymbolicRuntime()
    exporter = SymbolicASTExporter()
    capabilities = ["diff", "simplify", "eval", "poly_gcd"]
    optional_dependencies = {}

    verbs = [
        VerbSpec(
            pattern="differentiate {expr:expr} with respect to {var:ident} into {target:ident}",
            description="Calculates exact analytical derivative using calculus rules",
        ),
        VerbSpec(
            pattern="simplify expression {expr:expr} into {target:ident}",
            description="Simplifies expression using algebraic equivalence laws",
        ),
        VerbSpec(
            pattern="evaluate expression {expr:expr} with {subs:expr} into {target:ident}",
            description="Evaluates expression numerically with variable substitutions",
        ),
    ]
    blocks = []

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("differentiate ")
            or s.startswith("simplify expression ")
            or s.startswith("evaluate expression ")
            or s.startswith("calculate polynomial gcd ")
            or s.startswith("find rational roots ")
            or s.startswith("find root for expression ")
            or s.startswith("factor square free polynomial ")
            or s.startswith("calculate resultant of polynomials ")
            or s.startswith("calculate pade approximant ")
        )

    def can_handle_block(self, header: str) -> bool:
        return False


SYMBOLIC_DOMAIN = SymbolicDomain()
get_domain_registry().register(SYMBOLIC_DOMAIN)

__all__ = [
    "SymbolicDomain",
    "SYMBOLIC_DOMAIN",
    "SymbolicRuntime",
    "Expr",
    "Constant",
    "Symbol",
    "Add",
    "Mul",
    "Pow",
    "Sin",
    "Cos",
    "Ln",
    "Exp",
    "ExpressionParser",
    "PolyOps",
    "symbolic_parse",
    "symbolic_diff",
    "symbolic_simplify",
    "symbolic_eval",
    "symbolic_poly_gcd",
    "SymbolicIntegrator",
    "TaylorSeries",
    "ExactRationalLinearSolver",
    "symbolic_integrate",
    "symbolic_taylor_series",
    "symbolic_solve_rational_linear",
    "PolynomialGCDAndRoots",
    "BrentRootFinder",
    "symbolic_polynomial_gcd",
    "symbolic_rational_roots",
    "symbolic_brent_root",
    "UnivariatePolynomialEuclideanFactorizer",
    "PadeApproximantGenerator",
    "symbolic_square_free_factorization",
    "symbolic_polynomial_resultant",
    "symbolic_pade_approximant",
    "GroebnerBasisBuchberger",
    "symbolic_groebner_basis",
    "symbolic_eliminate_variables",
    "RischNormanSymbolicIntegrator",
    "SymbolicDifferentialEquationODESolver",
    "symbolic_risch_integrate",
    "symbolic_ode_solve",
]
