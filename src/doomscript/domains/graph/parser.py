"""Independent Domain Parser for Graph Analytics & Network Science domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.graph.spec import (
    GraphCreateSpec,
    GraphAddNodeSpec,
    GraphAddEdgeSpec,
    GraphShortestPathSpec,
    GraphPageRankSpec,
    GraphDegreesSpec,
    GraphCommunitiesSpec,
)


class GraphDomainParser(DomainParser):
    """Independent parser for Graph Analytics syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # shortest path from <u> to <v> in [graph] <g> into <target>
        m_sp = re.match(
            r"^shortest\s+path\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:graph\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sp:
            u_expr = m_sp.group(1).strip()
            v_expr = m_sp.group(2).strip()
            g_var = m_sp.group(3).strip()
            target = m_sp.group(4).strip()
            return f"set {target} to graph_shortest_path({g_var}, {u_expr}, {v_expr})"

        # pagerank of [graph] <g> into <target>
        m_pr = re.match(
            r"^pagerank\s+of\s+(?:graph\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pr:
            g_var = m_pr.group(1).strip()
            target = m_pr.group(2).strip()
            return f"set {target} to graph_pagerank({g_var})"

        # degrees of nodes in [graph] <g> into <target>
        m_deg = re.match(
            r"^degrees\s+of\s+nodes\s+in\s+(?:graph\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_deg:
            g_var = m_deg.group(1).strip()
            target = m_deg.group(2).strip()
            return f"set {target} to graph_degrees({g_var})"

        # detect communities in [graph] <g> into <target>
        m_com = re.match(
            r"^detect\s+communities\s+in\s+(?:graph\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_com:
            g_var = m_com.group(1).strip()
            target = m_com.group(2).strip()
            return f"set {target} to graph_communities({g_var})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # create (directed|undirected) graph into <target>
        m_create = re.match(
            r"^create\s+(directed|undirected)?\s*graph\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_create:
            is_directed = (m_create.group(1) or "").lower() == "directed"
            target = m_create.group(2).strip()
            return f"set {target} to create_graph(directed={is_directed})"

        # add node <id> to [graph] <g>
        m_node = re.match(
            r"^add\s+node\s+(.+?)\s+to\s+(?:graph\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_node:
            node_expr = m_node.group(1).strip()
            g_var = m_node.group(2).strip()
            return f"add_graph_node({g_var}, {node_expr})"

        # connect <u> to <v> [with weight <w>] in [graph] <g>
        m_edge = re.match(
            r"^connect\s+(.+?)\s+to\s+(.+?)(?:\s+with\s+weight\s+(\d+(?:\.\d+)?))?\s+in\s+(?:graph\s+)?([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_edge:
            u_expr = m_edge.group(1).strip()
            v_expr = m_edge.group(2).strip()
            w = m_edge.group(3).strip() if m_edge.group(3) else "1.0"
            g_var = m_edge.group(4).strip()
            return f"add_graph_edge({g_var}, {u_expr}, {v_expr}, weight={w})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Graph domain does not currently define declarative blocks")
