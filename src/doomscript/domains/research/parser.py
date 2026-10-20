"""Independent Domain Parser for Research & Scientific Graph Algorithms domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser, DomainIR


class ResearchDomainParser(DomainParser):
    """Independent parser for Research domain syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # topological sort of [research graph] <graph> into <target>
        m_topo = re.match(
            r"^(?:find\s+)?topological\s+sort\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_topo:
            g = m_topo.group(1).strip()
            target = m_topo.group(2).strip()
            return f"set {target} to research_topological_sort({g})"

        # find shortest path from <src> to <dst> in [research graph] <graph> [using dijkstra] into <target>
        m_dijk = re.match(
            r"^find\s+shortest\s+path\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)(?:\s+using\s+dijkstra)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dijk:
            src = m_dijk.group(1).strip()
            dst = m_dijk.group(2).strip()
            g = m_dijk.group(3).strip()
            target = m_dijk.group(4).strip()
            return f"set {target} to research_dijkstra_shortest_path({g}, {src}, {dst})"

        # find shortest paths from <src> in [research graph] <graph> [using bellman ford] into <target>
        m_bf = re.match(
            r"^find\s+shortest\s+paths\s+from\s+(.+?)\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)(?:\s+using\s+bellman\s+ford)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bf:
            src = m_bf.group(1).strip()
            g = m_bf.group(2).strip()
            target = m_bf.group(3).strip()
            return f"set {target} to research_bellman_ford({g}, {src})"

        # find all pairs shortest paths in [research graph] <graph> [using floyd warshall] into <target>
        m_fw = re.match(
            r"^find\s+all\s+pairs\s+shortest\s+paths\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)(?:\s+using\s+floyd\s+warshall)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fw:
            g = m_fw.group(1).strip()
            target = m_fw.group(2).strip()
            return f"set {target} to research_floyd_warshall_all_pairs({g})"

        # maximum flow from <src> to <sink> in [research graph] <graph> [using edmonds karp] into <target>
        m_flow = re.match(
            r"^(?:maximum|max)\s+flow\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)(?:\s+using\s+edmonds\s+karp)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_flow:
            src = m_flow.group(1).strip()
            sink = m_flow.group(2).strip()
            g = m_flow.group(3).strip()
            target = m_flow.group(4).strip()
            return f"set {target} to research_edmonds_karp_max_flow({g}, {src}, {sink})"

        # find bipartite matching in [research graph] <graph> between <u_nodes> and <v_nodes> into <target>
        m_bipartite = re.match(
            r"^find\s+bipartite\s+matching\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bipartite:
            g = m_bipartite.group(1).strip()
            u_nodes = m_bipartite.group(2).strip()
            v_nodes = m_bipartite.group(3).strip()
            target = m_bipartite.group(4).strip()
            return f"set {target} to research_hopcroft_karp_bipartite_matching({g}, {u_nodes}, {v_nodes})"

        # find strongly connected components in [research graph] <graph> [using tarjan] into <target>
        m_scc = re.match(
            r"^find\s+strongly\s+connected\s+components\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)(?:\s+using\s+tarjan)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_scc:
            g = m_scc.group(1).strip()
            target = m_scc.group(2).strip()
            return f"set {target} to research_tarjan_strongly_connected({g})"

        # find minimum spanning tree in [research graph] <graph> using kruskal into <target>
        m_kruskal = re.match(
            r"^find\s+minimum\s+spanning\s+tree\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+using\s+kruskal\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kruskal:
            g = m_kruskal.group(1).strip()
            target = m_kruskal.group(2).strip()
            return f"set {target} to research_kruskal_minimum_spanning_tree({g})"

        # find minimum spanning tree in [research graph] <graph> using prim into <target>
        m_prim = re.match(
            r"^find\s+minimum\s+spanning\s+tree\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+using\s+prim\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_prim:
            g = m_prim.group(1).strip()
            target = m_prim.group(2).strip()
            return f"set {target} to research_prim_minimum_spanning_tree({g})"

        # find/calculate diameter of [research graph] <graph> into <target>
        m_diam = re.match(
            r"^(?:find|calculate)\s+diameter\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_diam:
            g = m_diam.group(1).strip()
            target = m_diam.group(2).strip()
            return f"set {target} to research_graph_diameter({g})"

        # find/calculate radius of [research graph] <graph> into <target>
        m_rad = re.match(
            r"^(?:find|calculate)\s+radius\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rad:
            g = m_rad.group(1).strip()
            target = m_rad.group(2).strip()
            return f"set {target} to research_graph_radius({g})"

        # find connected components in [research graph] <graph> into <target>
        m_cc = re.match(
            r"^find\s+connected\s+components\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cc:
            g = m_cc.group(1).strip()
            target = m_cc.group(2).strip()
            return f"set {target} to research_connected_components({g})"

        # calculate pagerank of [research graph] <graph> [with damping <damping>] into <target>
        m_pr = re.match(
            r"^calculate\s+pagerank\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)(?:\s+with\s+damping\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pr:
            g = m_pr.group(1).strip()
            damping = m_pr.group(2).strip() if m_pr.group(2) else "0.85"
            target = m_pr.group(3).strip()
            return f"set {target} to research_pagerank({g}, {damping})"

        # calculate hits scores of [research graph] <graph> into <target>
        m_hits = re.match(
            r"^calculate\s+hits\s+(?:scores\s+)?of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hits:
            g = m_hits.group(1).strip()
            target = m_hits.group(2).strip()
            return f"set {target} to research_hits_algorithm({g})"

        # find eulerian circuit in [research graph] <graph> into <target>
        m_eul = re.match(
            r"^find\s+eulerian\s+circuit\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eul:
            g = m_eul.group(1).strip()
            target = m_eul.group(2).strip()
            return f"set {target} to research_eulerian_circuit_hierholzer({g})"

        # calculate isomorphism hash of [research graph] <graph> into <target>
        m_iso = re.match(
            r"^calculate\s+isomorphism\s+hash\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_iso:
            g = m_iso.group(1).strip()
            target = m_iso.group(2).strip()
            return f"set {target} to research_graph_isomorphism_hash({g})"

        # calculate transitive reduction of [research graph] <graph> into <target>
        m_tr = re.match(
            r"^calculate\s+transitive\s+reduction\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tr:
            g = m_tr.group(1).strip()
            target = m_tr.group(2).strip()
            return f"set {target} to research_transitive_reduction({g})"

        # find negative cycle in [research graph] <graph> into <target>
        m_neg = re.match(
            r"^find\s+negative\s+cycle\s+in\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_neg:
            g = m_neg.group(1).strip()
            target = m_neg.group(2).strip()
            return f"set {target} to research_find_negative_cycle({g})"

        # calculate degree distribution of [research graph] <graph> into <target>
        m_deg = re.match(
            r"^calculate\s+degree\s+distribution\s+of\s+(?:(?:a\s+)?research\s+graph\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_deg:
            g = m_deg.group(1).strip()
            target = m_deg.group(2).strip()
            return f"set {target} to research_degree_distribution({g})"

        # simulate distribution <dist> with <params> into <target>
        m_sim = re.match(
            r"^simulate\s+distribution\s+([A-Za-z_]\w*)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sim:
            dist = m_sim.group(1).strip()
            params = m_sim.group(2).strip()
            target = m_sim.group(3).strip()
            return f'set {target} to sample_distribution("{dist}", {params})'

        # calculate bibliometrics for citations <citations> [years <years>] into <target>
        m_bib = re.match(
            r"^calculate\s+bibliometrics\s+for\s+citations\s+(.+?)(?:\s+years\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bib:
            cites = m_bib.group(1).strip()
            years = m_bib.group(2).strip() if m_bib.group(2) else "None"
            target = m_bib.group(3).strip()
            return f"set {target} to research_calculate_bibliometrics({cites}, publication_years={years})"

        # correct p values <p_values> with fdr [alpha <alpha>] into <target>
        m_fdr = re.match(
            r"^correct\s+p\s+values\s+(.+?)\s+with\s+fdr(?:\s+alpha\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fdr:
            p_vals = m_fdr.group(1).strip()
            alpha = m_fdr.group(2).strip() if m_fdr.group(2) else "0.05"
            target = m_fdr.group(3).strip()
            return f"set {target} to research_multiple_testing_correction({p_vals}, alpha={alpha})"

        # Fallback to research registry normalization for existing syntax
        from doomscript.research.registry import apply_research_normalization
        return apply_research_normalization(line)

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[DomainIR, str]:
        raise NotImplementedError("Research domain does not use block structures directly.")
