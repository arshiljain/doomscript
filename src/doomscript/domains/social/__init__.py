from typing import Any, Dict
from doomscript.domains.base import DomainContract, DomainRuntime, VerbSpec
from doomscript.domains.registry import get_domain_registry
from doomscript.domains.social.runtime import (
    SocialRuntime, social_degree_centrality, social_closeness_centrality,
    social_betweenness_centrality, social_pagerank, social_network_density,
    social_clustering_coefficient, social_hits, social_katz_centrality,
    social_independent_cascade, social_adamic_adar, social_k_core
)
from doomscript.domains.social.parser import SocialDomainParser
from doomscript.domains.social.exporter import SocialASTExporter

class SocialDomain(DomainContract):
    name = "social"
    aliases = ["network_analysis", "graph_centrality", "sna"]
    description = "Social network analysis: Degree, Closeness, Betweenness centrality, PageRank, HITS, and clustering"
    parser = SocialDomainParser()
    runtime = SocialRuntime()
    exporter = SocialASTExporter()
    capabilities = [
        "degree_centrality", "closeness_centrality", "betweenness_centrality",
        "pagerank", "network_density", "clustering_coefficient", "hits",
        "katz_centrality", "independent_cascade", "adamic_adar", "k_core"
    ]
    verbs = [
        VerbSpec(pattern="calculate degree centrality for graph {g:expr} into {target:ident}", description="Degree centrality"),
        VerbSpec(pattern="calculate pagerank for graph {g:expr} into {target:ident}", description="PageRank algorithm"),
        VerbSpec(pattern="calculate hits for graph {g:expr} into {target:ident}", description="HITS algorithm")
    ]
    blocks = []
    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("calculate degree centrality ") or
            s.startswith("calculate closeness centrality ") or
            s.startswith("calculate betweenness centrality ") or
            s.startswith("calculate pagerank ") or
            s.startswith("calculate network density ") or
            s.startswith("calculate clustering coefficient ") or
            s.startswith("calculate hits ")
        )

SOCIAL_DOMAIN = SocialDomain()
get_domain_registry().register(SOCIAL_DOMAIN)

__all__ = [
    "SocialDomain", "SOCIAL_DOMAIN", "SocialRuntime",
    "social_degree_centrality", "social_closeness_centrality",
    "social_betweenness_centrality", "social_pagerank",
    "social_network_density", "social_clustering_coefficient",
    "social_hits", "social_katz_centrality", "social_independent_cascade",
    "social_adamic_adar", "social_k_core"
]
