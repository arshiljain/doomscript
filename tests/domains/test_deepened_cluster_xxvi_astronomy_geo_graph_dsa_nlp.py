"""Unit tests for deepened Cluster XXVI domains:
- Astronomy (SGP4 Simplified Perturbations Propagator, Hohmann & Bi-Elliptic Orbital Transfer Planner)
- Geo (Fortune Sweepline Voronoi Diagram, Ordinary Kriging Spatial Interpolator)
- Graph (Edmonds Blossom Maximum Matching, PageRank with Random Walk Restart)
- DSA (Link-Cut Tree Dynamic Forest, Ukkonen Online Suffix Tree)
- NLP (Okapi BM25 Information Retrieval, CYK Probabilistic Context-Free Grammar Parser)
"""

import math
import textwrap
import unittest

from doomscript.compiler.engine import execute
from doomscript.domains.astronomy.runtime import (
    SGP4SimplifiedPerturbationsSatellitePropagator,
    HohmannAndBiEllipticOrbitalManeuverPlanner,
    astronomy_propagate_sgp4,
    astronomy_plan_orbital_transfer,
)
from doomscript.domains.geo.runtime import (
    VoronoiDiagramFortuneSweepline,
    KrigingSpatialInterpolator,
    geo_voronoi_partition,
    geo_kriging_interpolate,
)
from doomscript.domains.graph.runtime import (
    EdmondsBlossomMaximumWeightMatching,
    PageRankRandomWalkWithRestart,
    graph_edmonds_blossom_matching,
    graph_pagerank_calculate,
)
from doomscript.domains.dsa.runtime import (
    LinkCutTreeDynamicGraph,
    SuffixTreeUkkonen,
    dsa_create_link_cut_tree,
    dsa_lct_link,
    dsa_lct_cut,
    dsa_lct_connected,
    dsa_lct_path_sum,
    dsa_create_suffix_tree,
    dsa_suffix_tree_search,
    dsa_suffix_tree_longest_repeated,
)
from doomscript.domains.nlp.runtime import (
    BM25OkapiInformationRetrieval,
    CYKProbabilisticContextFreeGrammarPCFG,
    nlp_bm25_search,
    nlp_pcfg_parse,
)


class TestDeepenedClusterXXVI(unittest.TestCase):
    """Test suite for Cluster XXVI deepened domain implementations."""

    # =========================================================================
    # Astronomy
    # =========================================================================

    def test_astronomy_sgp4_direct(self):
        # ISS-like low Earth orbit
        elements = {
            "semi_major_axis_km": 6778.0,
            "eccentricity": 0.0005,
            "inclination_deg": 51.64,
            "raan_deg": 120.0,
            "arg_perigee_deg": 45.0,
            "mean_anomaly_deg": 0.0,
        }
        res = SGP4SimplifiedPerturbationsSatellitePropagator.propagate(elements, time_since_epoch_min=90.0)
        self.assertIn("r_teme_km", res)
        self.assertIn("v_teme_km_s", res)
        self.assertAlmostEqual(res["altitude_km"], 6778.0 - 6378.137, delta=15.0)
        self.assertGreater(res["velocity_km_s"], 7.0)

    def test_astronomy_transfer_direct(self):
        hohmann = HohmannAndBiEllipticOrbitalManeuverPlanner.plan_hohmann(
            r1_km=6778.0, r2_km=42164.0, inc_change_deg=28.5
        )
        self.assertGreater(hohmann["delta_v_total_km_s"], 3.5)
        self.assertGreater(hohmann["time_of_flight_s"], 18000.0)

        bi_ell = HohmannAndBiEllipticOrbitalManeuverPlanner.plan_bi_elliptic(
            r1_km=6778.0, r2_km=100000.0, r_intermediate_km=150000.0
        )
        self.assertEqual(len(bi_ell["burns"]), 3)
        self.assertGreater(bi_ell["delta_v_total_km_s"], 0.0)

    def test_astronomy_spoken_script(self):
        code = textwrap.dedent("""
            use astronomy
            set orbit to {"semi_major_axis_km": 7000.0, "eccentricity": 0.01, "inclination_deg": 28.5, "raan_deg": 0.0, "arg_perigee_deg": 0.0, "mean_anomaly_deg": 0.0}
            propagate sgp4 satellite orbit orbit after 60.0 minutes into sat_state
            plan hohmann transfer from 7000.0 to 42000.0 into transfer_plan
        """)
        env = execute(code)
        self.assertGreater(env["sat_state"]["altitude_km"], 500.0)
        self.assertGreater(env["transfer_plan"]["delta_v_total_km_s"], 3.0)

    # =========================================================================
    # Geo
    # =========================================================================

    def test_geo_voronoi_direct(self):
        pts = [(0.0, 0.0), (4.0, 0.0), (2.0, 3.0), (2.0, 1.0)]
        res = VoronoiDiagramFortuneSweepline.compute_cells(pts, bounding_box=(-5.0, -5.0, 10.0, 10.0))
        self.assertEqual(res["num_sites"], 4)
        self.assertEqual(len(res["cells"]), 4)
        self.assertGreater(max(c["area"] for c in res["cells"]), 0.0)

    def test_geo_kriging_direct(self):
        obs = [(0.0, 0.0, 10.0), (1.0, 0.0, 12.0), (0.0, 1.0, 15.0), (1.0, 1.0, 18.0)]
        targets = [(0.5, 0.5), (0.2, 0.8)]
        res = KrigingSpatialInterpolator.fit_predict(obs, targets, nugget=0.1, sill=2.0, range_param=1.5)
        self.assertEqual(len(res["predictions"]), 2)
        # Prediction at center (0.5, 0.5) should be around average ~ 13.75
        self.assertAlmostEqual(res["predictions"][0]["estimated_value"], 13.75, delta=1.5)

    def test_geo_spoken_script(self):
        code = textwrap.dedent("""
            use geo
            set sites to [[0.0, 0.0], [3.0, 0.0], [1.5, 2.5]]
            compute voronoi partition for points sites into vor_res
            set obs to [[0.0, 0.0, 5.0], [2.0, 0.0, 9.0], [1.0, 2.0, 7.0]]
            set query_pts to [[1.0, 1.0]]
            interpolate kriging points obs targets query_pts into krig_res
        """)
        env = execute(code)
        self.assertEqual(env["vor_res"]["num_sites"], 3)
        self.assertAlmostEqual(env["krig_res"]["first_prediction"]["estimated_value"], 7.0, delta=2.0)

    # =========================================================================
    # Graph
    # =========================================================================

    def test_graph_edmonds_blossom_direct(self):
        # Odd cycle C5: 0-1, 1-2, 2-3, 3-4, 4-0 plus chord 0-2
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)]
        res = EdmondsBlossomMaximumWeightMatching.max_matching(num_nodes=5, edges=edges)
        # Maximum matching on 5 nodes can at most match 4 nodes (2 disjoint edges)
        self.assertEqual(res["cardinality"], 2)
        self.assertEqual(len(res["matched_pairs"]), 2)

    def test_graph_pagerank_direct(self):
        # Small directed graph: 0->1, 0->2, 1->2, 2->0, 3->2
        adj = {
            "0": ["1", "2"],
            "1": ["2"],
            "2": ["0"],
            "3": ["2"],
        }
        res = PageRankRandomWalkWithRestart.compute(adj, damping=0.85)
        # Node 2 receives the most incoming links
        self.assertEqual(res["top_node"], "2")
        self.assertAlmostEqual(sum(res["ranks"].values()), 1.0, delta=1e-3)

    def test_graph_spoken_script(self):
        code = textwrap.dedent("""
            use graph
            set edge_list to [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]]
            find maximum matching blossom edges edge_list nodes 5 into match_res
            set g_adj to {"A": ["B", "C"], "B": ["C"], "C": ["A"]}
            compute pagerank graph g_adj into pr_res
        """)
        env = execute(code)
        self.assertEqual(env["match_res"]["cardinality"], 2)
        self.assertAlmostEqual(sum(env["pr_res"]["ranks"].values()), 1.0, delta=1e-3)

    # =========================================================================
    # DSA
    # =========================================================================

    def test_dsa_link_cut_tree_direct(self):
        lct = LinkCutTreeDynamicGraph(5, node_values=[10, 20, 30, 40, 50])
        # Initially disconnected
        self.assertFalse(lct.connected(0, 4))

        # Link 0-1, 1-2, 2-3, 3-4
        lct.link(0, 1)
        lct.link(1, 2)
        lct.link(2, 3)
        lct.link(3, 4)

        self.assertTrue(lct.connected(0, 4))
        # Path sum from 0 to 4: 10 + 20 + 30 + 40 + 50 = 150
        self.assertEqual(lct.path_sum(0, 4), 150.0)

        # Cut edge 2-3
        lct.cut(2, 3)
        self.assertFalse(lct.connected(0, 4))
        self.assertTrue(lct.connected(0, 2))
        self.assertEqual(lct.path_sum(0, 2), 60.0)

    def test_dsa_suffix_tree_direct(self):
        st = SuffixTreeUkkonen("banana")
        self.assertTrue(st.search("nan"))
        self.assertTrue(st.search("banana"))
        self.assertFalse(st.search("apple"))
        # Longest repeated substring in "banana" is "ana"
        self.assertEqual(st.longest_repeated_substring(), "ana")

    def test_dsa_spoken_script(self):
        code = textwrap.dedent("""
            use dsa
            create link cut tree with 4 nodes values [1, 2, 3, 4] into lct
            link lct nodes 0 and 1 in lct into link1
            link lct nodes 1 and 2 in lct into link2
            query lct connectivity between 0 and 2 in lct into is_conn
            query lct path sum between 0 and 2 in lct into path_tot
            build ukkonen suffix tree for "mississippi" into s_tree
            search suffix tree s_tree for "issi" into has_issi
            find longest repeated substring in suffix tree s_tree into lrs
        """)
        env = execute(code)
        self.assertTrue(env["is_conn"])
        self.assertEqual(env["path_tot"], 6.0)
        self.assertTrue(env["has_issi"])
        self.assertIn(env["lrs"], ["issi", "ssi"])

    # =========================================================================
    # NLP
    # =========================================================================

    def test_nlp_bm25_direct(self):
        corpus = [
            "The quick brown fox jumps over the lazy dog",
            "The dog barked at the mailman in the morning",
            "Artificial intelligence and natural language processing in Python",
            "Deep learning neural networks and machine learning models",
        ]
        bm25 = BM25OkapiInformationRetrieval(corpus)
        res = bm25.search("neural networks learning", top_k=2)
        self.assertEqual(res["best_doc_id"], 3)
        self.assertGreater(res["top_score"], 0.0)

    def test_nlp_pcfg_cyk_direct(self):
        rules = [
            {"lhs": "S", "rhs": ["NP", "VP"], "prob": 1.0},
            {"lhs": "NP", "rhs": ["Det", "N"], "prob": 0.8},
            {"lhs": "NP", "rhs": ["N"], "prob": 0.2},
            {"lhs": "VP", "rhs": ["V", "NP"], "prob": 0.9},
            {"lhs": "Det", "rhs": ["the"], "prob": 0.6},
            {"lhs": "Det", "rhs": ["a"], "prob": 0.4},
            {"lhs": "N", "rhs": ["dog"], "prob": 0.5},
            {"lhs": "N", "rhs": ["cat"], "prob": 0.5},
            {"lhs": "V", "rhs": ["saw"], "prob": 1.0},
        ]
        pcfg = CYKProbabilisticContextFreeGrammarPCFG(rules)
        res = pcfg.parse(["the", "dog", "saw", "a", "cat"])
        self.assertTrue(res["is_valid"])
        self.assertGreater(res["probability"], 0.0)
        self.assertIn("S", res["parse_tree"])
        self.assertIn("NP", res["parse_tree"])
        self.assertIn("VP", res["parse_tree"])

    def test_nlp_spoken_script(self):
        code = textwrap.dedent("""
            use nlp
            set docs to ["quantum computing systems", "high performance compiler design", "relational database indexing"]
            search bm25 corpus docs query "compiler optimization" top 1 into bm25_res
            set g_rules to [{"lhs": "S", "rhs": ["NP", "VP"], "prob": 1.0}, {"lhs": "NP", "rhs": ["cats"], "prob": 1.0}, {"lhs": "VP", "rhs": ["sleep"], "prob": 1.0}]
            parse pcfg grammar g_rules tokens ["cats", "sleep"] into pcfg_res
        """)
        env = execute(code)
        self.assertEqual(env["bm25_res"]["best_doc_id"], 1)
        self.assertTrue(env["pcfg_res"]["is_valid"])
        self.assertEqual(env["pcfg_res"]["parse_tree"], "(S (NP cats) (VP sleep))")


if __name__ == "__main__":
    unittest.main()
