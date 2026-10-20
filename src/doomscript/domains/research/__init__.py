"""Research & Scientific Graph Algorithms Domain Pack for DoomScript."""

from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainIR,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.research.parser import ResearchDomainParser
from doomscript.domains.research.runtime import (
    ResearchGraph,
    research_topological_sort,
    research_dijkstra_shortest_path,
    research_bellman_ford,
    research_floyd_warshall_all_pairs,
    research_edmonds_karp_max_flow,
    research_hopcroft_karp_bipartite_matching,
    research_tarjan_strongly_connected,
    research_kruskal_minimum_spanning_tree,
    research_prim_minimum_spanning_tree,
    research_graph_diameter,
    research_graph_radius,
    research_connected_components,
    research_pagerank,
    research_hits_algorithm,
    research_eulerian_circuit_hierholzer,
    research_graph_isomorphism_hash,
    research_transitive_reduction,
    research_find_negative_cycle,
    research_degree_distribution,
    BibTeXEngine,
    CitationNetwork,
    AcademicLiteratureSynthesizer,
    SVDDecomposition,
    RungeKuttaFehlberg,
    LevenbergMarquardt,
    research_svd,
    research_rkf45_solve,
    research_levenberg_marquardt,
    HIndexAndCitationBibliometrics,
    BenjaminiHochbergMultipleTesting,
    research_calculate_bibliometrics,
    research_multiple_testing_correction,
)


class ResearchRuntime(DomainRuntime):
    """Bridge runtime for research operations."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        return ir


class ResearchDomain(DomainContract):
    """Research Domain Pack (Scientific graph algorithms, Autograd, Distributions, Stats)."""

    name = "research"
    aliases = ["autograd", "research_stats", "graph_research", "math"]
    description = "Research mathematical toolkit, automatic differentiation, statistical distributions, and graph algorithms"
    parser = ResearchDomainParser()
    runtime = ResearchRuntime()
    exporter = None
    capabilities = ["autograd", "differentiation", "distributions", "hypothesis_testing", "graphs"]
    optional_dependencies = ["numpy", "scipy", "torch"]

    verbs = [
        VerbSpec(
            name="gradient_of",
            pattern="gradient of {fn_name:ident} at {x_expr:expr} into {target:ident}",
            arg_schema={"fn_name": "ident", "x_expr": "expr", "target": "ident"},
            returns="float",
            description="Evaluate numerical or reverse-mode automatic differentiation gradient",
        ),
        VerbSpec(
            name="differentiate",
            pattern="differentiate {expr:expr} with respect to {var:ident} into {target:ident}",
            arg_schema={"expr": "expr", "var": "ident", "target": "ident"},
            returns="Any",
            description="Symbolic differentiation with respect to target variable",
        ),
        VerbSpec(
            name="simulate_distribution",
            pattern="simulate distribution {dist:ident} with {params:expr} into {target:ident}",
            arg_schema={"dist": "ident", "params": "expr", "target": "ident"},
            returns="Collection",
            description="Generate random variables from named distribution",
        ),
        VerbSpec(
            name="confidence_interval",
            pattern="confidence interval of {data:ident} [at {level:expr}] into {target:ident}",
            arg_schema={"data": "ident", "level": "expr", "target": "ident"},
            defaults={"level": 0.95},
            returns="Record",
            description="Compute Student-t or normal confidence intervals",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        if (
            s.startswith("topological sort of ")
            or s.startswith("find topological sort of ")
            or s.startswith("find shortest path from ")
            or s.startswith("find shortest paths from ")
            or s.startswith("find all pairs shortest paths ")
            or s.startswith("maximum flow from ")
            or s.startswith("max flow from ")
            or s.startswith("find bipartite matching ")
            or s.startswith("find strongly connected components ")
            or s.startswith("find minimum spanning tree ")
            or s.startswith("find diameter of ")
            or s.startswith("calculate diameter of ")
            or s.startswith("find radius of ")
            or s.startswith("calculate radius of ")
            or s.startswith("find connected components ")
            or s.startswith("calculate pagerank of ")
            or s.startswith("calculate hits ")
            or s.startswith("find eulerian circuit ")
            or s.startswith("calculate isomorphism hash ")
            or s.startswith("calculate transitive reduction ")
            or s.startswith("find negative cycle ")
            or s.startswith("calculate degree distribution ")
            or s.startswith("simulate distribution ")
            or s.startswith("gradient of ")
            or s.startswith("confidence interval of ")
            or s.startswith("differentiate ")
            or super().can_handle_line(line)
        ):
            return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register singleton with registry
RESEARCH_DOMAIN = ResearchDomain()
get_domain_registry().register(RESEARCH_DOMAIN)

__all__ = [
    "ResearchDomain",
    "RESEARCH_DOMAIN",
    "ResearchDomainParser",
    "ResearchRuntime",
    "ResearchGraph",
    "research_topological_sort",
    "research_dijkstra_shortest_path",
    "research_bellman_ford",
    "research_floyd_warshall_all_pairs",
    "research_edmonds_karp_max_flow",
    "research_hopcroft_karp_bipartite_matching",
    "research_tarjan_strongly_connected",
    "research_kruskal_minimum_spanning_tree",
    "research_prim_minimum_spanning_tree",
    "research_graph_diameter",
    "research_graph_radius",
    "research_connected_components",
    "research_pagerank",
    "research_hits_algorithm",
    "research_eulerian_circuit_hierholzer",
    "research_graph_isomorphism_hash",
    "research_transitive_reduction",
    "research_find_negative_cycle",
    "research_degree_distribution",
    "BibTeXEngine",
    "CitationNetwork",
    "AcademicLiteratureSynthesizer",
    "SVDDecomposition",
    "RungeKuttaFehlberg",
    "LevenbergMarquardt",
    "research_svd",
    "research_rkf45_solve",
    "research_levenberg_marquardt",
    "HIndexAndCitationBibliometrics",
    "BenjaminiHochbergMultipleTesting",
    "research_calculate_bibliometrics",
    "research_multiple_testing_correction",
]
