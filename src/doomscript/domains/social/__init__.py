from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.social.runtime import (
    social_degree_centrality, social_closeness_centrality,
    social_betweenness_centrality, social_pagerank,
    social_network_density, social_clustering_coefficient
)
from doomscript.domains.social.parser import SocialDomainParser
from doomscript.domains.social.exporter import SocialASTExporter

class SocialRuntime(DomainRuntime):
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

class SocialDomain(DomainContract):
    name = "social"
    aliases = ["network_analysis", "graph_centrality", "sna"]
    description = "Social network analysis: Degree, Closeness, Betweenness centrality, PageRank, and clustering"
    parser = SocialDomainParser()
    runtime = SocialRuntime()
    exporter = SocialASTExporter()
    capabilities = ["degree_centrality", "closeness_centrality", "betweenness_centrality", "pagerank", "network_density", "clustering_coefficient"]
    verbs = [
        VerbSpec(pattern="calculate degree centrality for graph {g:expr} into {target:ident}", description="Degree centrality"),
        VerbSpec(pattern="calculate pagerank for graph {g:expr} into {target:ident}", description="PageRank algorithm")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return s.startswith("calculate degree centrality ") or s.startswith("calculate closeness centrality ") or s.startswith("calculate betweenness centrality ") or s.startswith("calculate pagerank ") or s.startswith("calculate network density ") or s.startswith("calculate clustering coefficient ")

SOCIAL_DOMAIN = SocialDomain()
get_domain_registry().register(SOCIAL_DOMAIN)

__all__ = [
    "SocialDomain", "SOCIAL_DOMAIN", "SocialRuntime",
    "social_degree_centrality", "social_closeness_centrality",
    "social_betweenness_centrality", "social_pagerank",
    "social_network_density", "social_clustering_coefficient"
]
