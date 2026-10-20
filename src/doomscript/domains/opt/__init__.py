"""Optimization & Operations Research Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec
from doomscript.domains.opt.parser import OptDomainParser
from doomscript.domains.opt.runtime import (
    OptRuntime,
    SimplexSolver,
    parse_linear_expression,
    parse_constraint,
    solve_linear_program,
    opt_minimize_1d,
    opt_grid_search,
    opt_fractional_knapsack,
    opt_activity_selection,
    opt_gradient_descent_step,
    opt_bisection_root,
    opt_simulated_annealing,
    opt_golden_section_search,
    opt_knapsack_01_dp,
    opt_longest_increasing_subsequence,
    opt_coin_change_minimum,
    opt_coin_change_combinations,
    opt_job_scheduling_deadline,
    opt_huffman_encoding,
    opt_matrix_chain_multiplication,
    opt_levenshtein_alignment,
    opt_subset_sum_exists,
    opt_subset_sum_find,
    opt_rod_cutting,
    opt_two_opt_tsp,
    opt_linear_interpolation,
    opt_weighted_interval_scheduling,
    opt_pareto_frontier,
    opt_hungarian_assignment,
    opt_binary_search_peak_1d,
    opt_genetic_algorithm,
    opt_particle_swarm,
    opt_nelder_mead,
    PrimalDualInteriorPoint,
    BranchAndBoundMILP,
    AdaptiveSimulatedAnnealing,
    opt_solve_interior_point,
    opt_branch_and_bound_milp,
    opt_adaptive_simulated_annealing,
    ParticleSwarmOptimizer,
    ActiveSetQuadraticProgramming,
    opt_particle_swarm_optimize,
    opt_solve_quadratic_program_active_set,
    NelderMeadSimplexDirectSearch,
    InteriorPointPrimalDualLP,
    CMAESContinuousOptimization,
    opt_nelder_mead_minimize,
    opt_interior_point_solve_lp,
    opt_cma_es_optimize,
    NelderMeadSimplexOptimizer,
    SequentialQuadraticProgrammingSQP,
    opt_sqp_optimize,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.opt.exporter import OptASTExporter
from doomscript.domains.registry import get_domain_registry


class OptDomain(DomainContract):
    """Optimization & Operations Research domain pack providing linear programming and Simplex solving."""

    name = "opt"
    aliases = ["optimization", "operations_research", "lp"]
    description = "Linear programming, simplex algorithm, dual bounds, and operations research solvers"
    parser = OptDomainParser()
    runtime = OptRuntime()
    exporter = OptASTExporter()
    capabilities = ["linear_programming", "simplex", "optimization"]
    optional_dependencies = ["scipy"]

    verbs = [
        VerbSpec(
            name="solve_lp",
            pattern="solve [linear program] {lp_var:ident} into {target:ident}",
            arg_schema={"lp_var": "ident", "target": "ident"},
            returns="Record",
            description="Solve linear programming problem using Simplex method",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("create linear program ")
            or s.startswith("solve linear program ")
            or s.startswith("solve ")
            or s.startswith("minimize 1d ")
            or s.startswith("grid search ")
            or s.startswith("solve fractional knapsack ")
            or s.startswith("schedule activities ")
            or s.startswith("gradient descent step ")
            or s.startswith("find root of ")
            or s.startswith("simulated annealing for ")
            or s.startswith("golden section search for ")
            or s.startswith("solve 01 knapsack ")
            or s.startswith("longest increasing subsequence ")
            or s.startswith("minimum coins for amount ")
            or s.startswith("coin combinations for amount ")
            or s.startswith("schedule jobs by deadline ")
            or s.startswith("huffman encoding for frequencies ")
            or s.startswith("matrix chain multiplication ")
            or s.startswith("levenshtein alignment between ")
            or s.startswith("check if subset sum exists ")
            or s.startswith("find subset summing to ")
            or s.startswith("solve rod cutting for length ")
            or s.startswith("optimize tsp with 2opt ")
            or s.startswith("interpolate linear value at ")
            or s.startswith("weighted interval scheduling ")
            or s.startswith("find pareto frontier ")
            or s.startswith("hungarian assignment for cost matrix ")
            or s.startswith("find peak element in ")
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return (
            (
                s.startswith("linear program ")
                or s.startswith("optimize ")
                or s.startswith("maximize ")
                or s.startswith("minimize ")
            )
            and (":" in s)
        )


# Register with central registry
OPT_DOMAIN = OptDomain()
get_domain_registry().register(OPT_DOMAIN)

__all__ = [
    "OptDomain",
    "OPT_DOMAIN",
    "LinearProgramSpec",
    "SolveLPSpec",
    "OptDomainParser",
    "OptRuntime",
    "OptASTExporter",
    "SimplexSolver",
    "parse_linear_expression",
    "parse_constraint",
    "solve_linear_program",
    "opt_minimize_1d",
    "opt_grid_search",
    "opt_fractional_knapsack",
    "opt_activity_selection",
    "opt_gradient_descent_step",
    "opt_bisection_root",
    "opt_simulated_annealing",
    "opt_golden_section_search",
    "opt_knapsack_01_dp",
    "opt_longest_increasing_subsequence",
    "opt_coin_change_minimum",
    "opt_coin_change_combinations",
    "opt_job_scheduling_deadline",
    "opt_huffman_encoding",
    "opt_matrix_chain_multiplication",
    "opt_levenshtein_alignment",
    "opt_subset_sum_exists",
    "opt_subset_sum_find",
    "opt_rod_cutting",
    "opt_two_opt_tsp",
    "opt_linear_interpolation",
    "opt_weighted_interval_scheduling",
    "opt_pareto_frontier",
    "opt_hungarian_assignment",
    "opt_binary_search_peak_1d",
    "opt_genetic_algorithm",
    "opt_particle_swarm",
    "opt_nelder_mead",
    "PrimalDualInteriorPoint",
    "BranchAndBoundMILP",
    "AdaptiveSimulatedAnnealing",
    "opt_solve_interior_point",
    "opt_branch_and_bound_milp",
    "opt_adaptive_simulated_annealing",
    "ParticleSwarmOptimizer",
    "ActiveSetQuadraticProgramming",
    "opt_particle_swarm_optimize",
    "opt_solve_quadratic_program_active_set",
    "NelderMeadSimplexDirectSearch",
    "InteriorPointPrimalDualLP",
    "CMAESContinuousOptimization",
    "opt_nelder_mead_minimize",
    "opt_interior_point_solve_lp",
    "opt_cma_es_optimize",
    "NelderMeadSimplexOptimizer",
    "SequentialQuadraticProgrammingSQP",
    "opt_sqp_optimize",
]
