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

        # create (directed|undirected|empty) graph into <target>
        m_create = re.match(
            r"^create\s+(?:empty\s+)?(directed|undirected)?\s*graph\s+into\s+([A-Za-z_]\w*)$",
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

        # degree centrality of <g> into <target>
        m_dc = re.match(
            r"^degree\s+centrality\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dc:
            g, target = m_dc.group(1).strip(), m_dc.group(2).strip()
            return f"set {target} to graph_degree_centrality({g})"

        # betweenness centrality of <g> into <target>
        m_bc = re.match(
            r"^betweenness\s+centrality\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bc:
            g, target = m_bc.group(1).strip(), m_bc.group(2).strip()
            return f"set {target} to graph_betweenness_centrality({g})"

        # closeness centrality of <g> into <target>
        m_cc = re.match(
            r"^closeness\s+centrality\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cc:
            g, target = m_cc.group(1).strip(), m_cc.group(2).strip()
            return f"set {target} to graph_closeness_centrality({g})"

        # check if <g> is bipartite into <target>
        m_bip = re.match(
            r"^(?:check\s+if\s+)?(.+?)\s+is\s+bipartite\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bip:
            g, target = m_bip.group(1).strip(), m_bip.group(2).strip()
            return f"set {target} to graph_is_bipartite({g})"

        # find eulerian path in <g> into <target>
        m_eul = re.match(
            r"^(?:find\s+)?eulerian\s+path\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eul:
            g, target = m_eul.group(1).strip(), m_eul.group(2).strip()
            return f"set {target} to graph_find_eulerian_path({g})"

        # strongly connected components of <g> into <target>
        m_scc = re.match(
            r"^strongly\s+connected\s+components\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_scc:
            g, target = m_scc.group(1).strip(), m_scc.group(2).strip()
            return f"set {target} to graph_strongly_connected_components({g})"

        # diameter of <g> into <target>
        m_diam = re.match(
            r"^diameter\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_diam:
            g, target = m_diam.group(1).strip(), m_diam.group(2).strip()
            return f"set {target} to graph_diameter({g})"

        # eigenvector centrality of <g> into <target>
        m_ec = re.match(
            r"^eigenvector\s+centrality\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ec:
            g, target = m_ec.group(1).strip(), m_ec.group(2).strip()
            return f"set {target} to graph_eigenvector_centrality({g})"

        # dijkstra shortest path in <g> from <u> to <v> into <target>
        m_dijk = re.match(
            r"^(?:dijkstra\s+shortest\s+path|shortest\s+path)\s+in\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dijk:
            g, u, v, target = m_dijk.group(1).strip(), m_dijk.group(2).strip(), m_dijk.group(3).strip(), m_dijk.group(4).strip()
            return f"set {target} to graph_dijkstra_shortest_path({g}, {u}, {v})"

        # bellman ford in <g> from <s> into <target>
        m_bf = re.match(
            r"^bellman\s+ford\s+(?:shortest\s+paths\s+)?in\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bf:
            g, s_node, target = m_bf.group(1).strip(), m_bf.group(2).strip(), m_bf.group(3).strip()
            return f"set {target} to graph_bellman_ford({g}, {s_node})"

        # floyd warshall in <g> into <target>
        m_fw = re.match(
            r"^(?:all\s+pairs\s+shortest\s+paths\s+using\s+)?floyd\s+warshall\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fw:
            g, target = m_fw.group(1).strip(), m_fw.group(2).strip()
            return f"set {target} to graph_floyd_warshall({g})"

        # kruskal mst of <g> into <target>
        m_krusk = re.match(
            r"^(?:minimum\s+spanning\s+tree\s+of|kruskal\s+(?:mst\s+)?of)\s+(.+?)(?:\s+using\s+kruskal)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_krusk:
            g, target = m_krusk.group(1).strip(), m_krusk.group(2).strip()
            return f"set {target} to graph_kruskal_mst({g})"

        # prim mst of <g> [starting at <s>] into <target>
        m_prim = re.match(
            r"^(?:minimum\s+spanning\s+tree\s+of|prim\s+(?:mst\s+)?of)\s+(.+?)(?:\s+using\s+prim)?(?:\s+starting\s+at\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_prim:
            g, start_n, target = m_prim.group(1).strip(), m_prim.group(2), m_prim.group(3).strip()
            start_arg = f", {start_n.strip()}" if start_n else ""
            return f"set {target} to graph_prim_mst({g}{start_arg})"

        # articulation points of <g> into <target>
        m_art = re.match(
            r"^(?:find\s+)?articulation\s+points\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_art:
            g, target = m_art.group(1).strip(), m_art.group(2).strip()
            return f"set {target} to graph_articulation_points({g})"

        # bridges in <g> into <target>
        m_br = re.match(
            r"^(?:find\s+)?bridges\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_br:
            g, target = m_br.group(1).strip(), m_br.group(2).strip()
            return f"set {target} to graph_find_bridges({g})"

        # maximum flow in <g> from <source> to <sink> into <target>
        m_mf = re.match(
            r"^(?:maximum|max)\s+flow\s+in\s+(.+?)\s+from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mf:
            g, src, snk, target = m_mf.group(1).strip(), m_mf.group(2).strip(), m_mf.group(3).strip(), m_mf.group(4).strip()
            return f"set {target} to graph_max_flow_edmonds_karp({g}, {src}, {snk})"

        # radius of <g> into <target>
        m_rad = re.match(
            r"^radius\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rad:
            g, target = m_rad.group(1).strip(), m_rad.group(2).strip()
            return f"set {target} to graph_radius({g})"

        # center of <g> into <target>
        m_ctr = re.match(
            r"^center\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ctr:
            g, target = m_ctr.group(1).strip(), m_ctr.group(2).strip()
            return f"set {target} to graph_center({g})"

        # clustering coefficient of <g> into <target>
        m_cc2 = re.match(
            r"^clustering\s+coefficient\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cc2:
            g, target = m_cc2.group(1).strip(), m_cc2.group(2).strip()
            return f"set {target} to graph_clustering_coefficient({g})"

        # transitivity of <g> into <target>
        m_trans = re.match(
            r"^transitivity\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_trans:
            g, target = m_trans.group(1).strip(), m_trans.group(2).strip()
            return f"set {target} to graph_transitivity({g})"

        # density of <g> into <target>
        m_dens = re.match(
            r"^density\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dens:
            g, target = m_dens.group(1).strip(), m_dens.group(2).strip()
            return f"set {target} to graph_density({g})"

        # degree histogram of <g> into <target>
        m_dh = re.match(
            r"^degree\s+histogram\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dh:
            g, target = m_dh.group(1).strip(), m_dh.group(2).strip()
            return f"set {target} to graph_degree_histogram({g})"

        # jaccard similarity between nodes <u> and <v> in <g> into <target>
        m_jacc = re.match(
            r"^jaccard\s+similarity\s+(?:between\s+nodes\s+|between\s+)?(.+?)\s+and\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jacc:
            u, v, g, target = m_jacc.group(1).strip(), m_jacc.group(2).strip(), m_jacc.group(3).strip(), m_jacc.group(4).strip()
            return f"set {target} to graph_jaccard_similarity({g}, {u}, {v})"

        # eccentricity of <node> in <g> into <target>
        m_ecc = re.match(
            r"^eccentricity\s+of\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ecc:
            node, g, target = m_ecc.group(1).strip(), m_ecc.group(2).strip(), m_ecc.group(3).strip()
            return f"set {target} to graph_eccentricity({g}, {node})"

        # check if <g> is tree into <target>
        m_tree = re.match(
            r"^(?:check\s+if\s+)?(.+?)\s+is\s+tree\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tree:
            g, target = m_tree.group(1).strip(), m_tree.group(2).strip()
            return f"set {target} to graph_is_tree({g})"

        # transitive closure of <g> into <target>
        m_tc = re.match(
            r"^transitive\s+closure\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tc:
            g, target = m_tc.group(1).strip(), m_tc.group(2).strip()
            return f"set {target} to graph_transitive_closure({g})"

        # k core of <g> with k <k> into <target>
        m_kc = re.match(
            r"^k\s+core\s+of\s+(.+?)\s+with\s+k\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kc:
            g, k, target = m_kc.group(1).strip(), m_kc.group(2).strip(), m_kc.group(3).strip()
            return f"set {target} to graph_k_core({g}, {k})"

        # laplacian matrix of <g> into <target>
        m_lap = re.match(
            r"^laplacian\s+matrix\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lap:
            g, target = m_lap.group(1).strip(), m_lap.group(2).strip()
            return f"set {target} to graph_laplacian_matrix({g})"

        # compute bipartite matching for edges <edges> into <target>
        m_bm = re.match(
            r"^compute\s+bipartite\s+matching\s+for\s+edges\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bm:
            edges, target = m_bm.group(1).strip(), m_bm.group(2).strip()
            return f"set {target} to graph_bipartite_matching({edges})"

        # find bridges and articulation points in <adj> into <target>
        m_br = re.match(
            r"^find\s+bridges\s+and\s+articulation\s+points\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_br:
            adj, target = m_br.group(1).strip(), m_br.group(2).strip()
            return f"set {target} to graph_find_bridges_and_cuts({adj})"

        # find eulerian trail for edges <edges> into <target>
        m_eul = re.match(
            r"^find\s+eulerian\s+trail\s+for\s+edges\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eul:
            edges, target = m_eul.group(1).strip(), m_eul.group(2).strip()
            return f"set {target} to graph_eulerian_trail({edges})"

        # calculate max flow push relabel nodes <nodes> edges <edges> source <source> sink <sink> into <target>
        m_pr = re.match(
            r"^calculate\s+max\s+flow\s+push\s+relabel\s+nodes\s+(.+?)\s+edges\s+(.+?)\s+source\s+(.+?)\s+sink\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pr:
            nodes, edges, src, snk, target = m_pr.group(1).strip(), m_pr.group(2).strip(), m_pr.group(3).strip(), m_pr.group(4).strip(), m_pr.group(5).strip()
            if not (src.startswith('"') or src.startswith("'")):
                src = f'"{src}"'
            if not (snk.startswith('"') or snk.startswith("'")):
                snk = f'"{snk}"'
            return f"set {target} to graph_push_relabel_max_flow({nodes}, {edges}, {src}, {snk})"

        # calculate johnson all pairs shortest paths nodes <nodes> edges <edges> into <target>
        m_jh = re.match(
            r"^calculate\s+johnson\s+all\s+pairs\s+shortest\s+paths\s+nodes\s+(.+?)\s+edges\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jh:
            nodes, edges, target = m_jh.group(1).strip(), m_jh.group(2).strip(), m_jh.group(3).strip()
            return f"set {target} to graph_johnson_all_pairs_paths({nodes}, {edges})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Graph domain does not currently define declarative blocks")
