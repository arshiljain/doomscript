"""Social Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class SocialDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate degree centrality for graph <g> into <target>
        m_deg = re.match(r"^calculate\s+degree\s+centrality\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_deg:
            return f"set {m_deg.group(2)} to social_degree_centrality({m_deg.group(1)})"

        # calculate closeness centrality for graph <g> into <target>
        m_close = re.match(r"^calculate\s+closeness\s+centrality\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_close:
            return f"set {m_close.group(2)} to social_closeness_centrality({m_close.group(1)})"

        # calculate betweenness centrality for graph <g> into <target>
        m_bet = re.match(r"^calculate\s+betweenness\s+centrality\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bet:
            return f"set {m_bet.group(2)} to social_betweenness_centrality({m_bet.group(1)})"

        # calculate pagerank for graph <g> into <target>
        m_pr = re.match(r"^calculate\s+pagerank\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pr:
            return f"set {m_pr.group(2)} to social_pagerank({m_pr.group(1)})"

        # calculate network density for graph <g> into <target>
        m_den = re.match(r"^calculate\s+network\s+density\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_den:
            return f"set {m_den.group(2)} to social_network_density({m_den.group(1)})"

        # calculate clustering coefficient for graph <g> into <target>
        m_clust = re.match(r"^calculate\s+clustering\s+coefficient\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_clust:
            return f"set {m_clust.group(2)} to social_clustering_coefficient({m_clust.group(1)})"

        # calculate hits for graph <g> into <target>
        m_hits = re.match(r"^calculate\s+hits\s+for\s+graph\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hits:
            return f"set {m_hits.group(2)} to social_hits({m_hits.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Social domain does not define declarative blocks")
