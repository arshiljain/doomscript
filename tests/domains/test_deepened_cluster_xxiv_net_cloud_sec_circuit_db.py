"""Unit tests for Cluster XXIV Deepened Domains:
Net, Cloud, Sec, Circuit, and DB.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import textwrap
import unittest
from doomscript.compiler.engine import execute

from doomscript.domains.net.runtime import (
    TCPCongestionControlBBR,
    DiffServTokenBucketPolicer,
    net_bbr_congestion_control,
    net_diffserv_trtcm_police,
)
from doomscript.domains.cloud.runtime import (
    PaxosConsensusProtocolStateReplication,
    RaftLeaderElectionLogReplication,
    cloud_paxos_simulate_round,
    cloud_raft_simulate_cluster,
)
from doomscript.domains.sec.runtime import (
    ZeroKnowledgeSchnorrIdentificationProtocol,
    PBKDF2KeyDerivationFunctionPure,
    sec_schnorr_zkp_prove_verify,
    sec_pbkdf2_sha256,
)
from doomscript.domains.circuit.runtime import (
    ModifiedNodalAnalysisMNASolver,
    DigitalStaticTimingAnalyzerSTA,
    circuit_mna_solve,
    circuit_static_timing_analysis,
)
from doomscript.domains.db.runtime import (
    BTreeStorageEnginePure,
    CostBasedQueryOptimizerCBO,
    db_btree_index_benchmark,
    db_cost_based_join_optimizer,
)


class TestDeepenedClusterXXIV(unittest.TestCase):

    # =========================================================================
    # NET
    # =========================================================================

    def test_net_bbr_direct(self):
        del_rates = [1e6, 2e6, 4e6, 8e6, 8.1e6, 8.2e6, 8.2e6, 8.2e6] * 2
        rtts = [0.04, 0.04, 0.042, 0.045, 0.046, 0.045, 0.044, 0.04] * 2
        res = TCPCongestionControlBBR.simulate(del_rates, rtts, mss=1460)
        self.assertGreater(res["final_cwnd_bytes"], 1460)
        self.assertIn(res["final_state"], ("STARTUP", "DRAIN", "PROBE_BW"))

    def test_net_diffserv_trtcm_direct(self):
        pkts = [1500, 1500, 1500, 1500, 5000, 5000, 1500, 1500]
        res = DiffServTokenBucketPolicer.police(
            pkts, cir_bps=1_000_000, cbs_bytes=4000, pir_bps=2_000_000, pbs_bytes=8000
        )
        self.assertEqual(len(res["marked_colors"]), 8)
        self.assertGreater(res["green_count"], 0)

    def test_net_spoken_english(self):
        code = textwrap.dedent("""
            use net
            set d_rates to [1000000.0, 2000000.0, 4000000.0, 4100000.0, 4100000.0]
            set rtt_vals to [0.02, 0.02, 0.025, 0.025, 0.022]
            simulate tcp bbr rates d_rates rtts rtt_vals mss 1460 into bbr_res
            set cwnd to bbr_res's final_cwnd_bytes
            set pkts to [1000, 2000, 1500, 4000, 1000]
            police diffserv trtcm packets pkts cir 800000.0 cbs 5000 pir 1600000.0 pbs 10000 into trtcm_res
            set g_cnt to trtcm_res's green_count
        """).strip()
        env = execute(code)
        self.assertGreater(env["cwnd"], 0)
        self.assertGreater(env["g_cnt"], 0)

    # =========================================================================
    # CLOUD
    # =========================================================================

    def test_cloud_paxos_direct(self):
        props = [
            {"proposer_id": 1, "proposal_num": 1, "value": "TX_A"},
            {"proposer_id": 2, "proposal_num": 2, "value": "TX_B"},
        ]
        res = PaxosConsensusProtocolStateReplication.run_consensus(num_acceptors=5, proposals=props)
        self.assertTrue(res["consensus_achieved"])
        self.assertIn(res["chosen_value"], ("TX_A", "TX_B"))

    def test_cloud_raft_direct(self):
        res = RaftLeaderElectionLogReplication.simulate_cluster(num_nodes=5, commands=["CMD1", "CMD2"])
        self.assertTrue(res["leader_elected"])
        self.assertEqual(res["commands_committed"], 2)

    def test_cloud_spoken_english(self):
        code = textwrap.dedent("""
            use cloud
            set props to [
                {"proposer_id": 1, "proposal_num": 10, "value": "DECISION_1"}
            ]
            simulate paxos consensus acceptors 5 proposals props into paxos_res
            set is_paxos_done to paxos_res's consensus_achieved
            set dec_val to paxos_res's chosen_value
            set cmds to ["SET a=1", "SET b=2"]
            simulate raft cluster nodes 5 commands cmds into raft_res
            set is_leader to raft_res's leader_elected
        """).strip()
        env = execute(code)
        self.assertTrue(env["is_paxos_done"])
        self.assertEqual(env["dec_val"], "DECISION_1")
        self.assertTrue(env["is_leader"])

    # =========================================================================
    # SEC
    # =========================================================================

    def test_sec_schnorr_zkp_direct(self):
        secret = 987654321
        res = ZeroKnowledgeSchnorrIdentificationProtocol.prove_and_verify(secret)
        self.assertTrue(res["verified"])
        self.assertTrue(res["soundness_verified"])

    def test_sec_pbkdf2_direct(self):
        res = PBKDF2KeyDerivationFunctionPure.derive_key("password123", "salt_value", iterations=500, dklen=32)
        self.assertEqual(res["key_length_bytes"], 32)
        self.assertIsInstance(res["derived_key_hex"], str)

    def test_sec_spoken_english(self):
        code = textwrap.dedent("""
            use sec
            prove schnorr zkp secret 424242 into zkp_res
            set is_valid to zkp_res's verified
            derive pbkdf2 key password "SecretPass" salt "RandomSalt" iterations 200 length 32 into kdf_res
            set k_len to kdf_res's key_length_bytes
        """).strip()
        env = execute(code)
        self.assertTrue(env["is_valid"])
        self.assertEqual(env["k_len"], 32)

    # =========================================================================
    # CIRCUIT
    # =========================================================================

    def test_circuit_mna_direct(self):
        # Simple voltage divider: V1=10V between node 1 and 0, R1=100 ohm between 1 and 2, R2=100 ohm between 2 and 0
        comps = [
            {"type": "V", "name": "V1", "node1": 1, "node2": 0, "value": 10.0},
            {"type": "R", "node1": 1, "node2": 2, "value": 100.0},
            {"type": "R", "node1": 2, "node2": 0, "value": 100.0},
        ]
        res = ModifiedNodalAnalysisMNASolver.solve(comps, ground_node=0)
        self.assertAlmostEqual(res["node_voltages"]["1"], 10.0, places=2)
        self.assertAlmostEqual(res["node_voltages"]["2"], 5.0, places=2)

    def test_circuit_sta_direct(self):
        gates = [
            {"id": "G1", "inputs": [], "delay_ns": 2.0},
            {"id": "G2", "inputs": ["G1"], "delay_ns": 3.0},
            {"id": "G3", "inputs": ["G2"], "delay_ns": 1.5},
        ]
        res = DigitalStaticTimingAnalyzerSTA.analyze(gates, clock_period_ns=10.0)
        self.assertAlmostEqual(res["max_arrival_time_ns"], 6.5, places=2)
        self.assertFalse(res["timing_violation"])
        self.assertEqual(res["critical_path"], ["G1", "G2", "G3"])

    def test_circuit_spoken_english(self):
        code = textwrap.dedent("""
            use circuit
            set comps to [
                {"type": "V", "name": "V1", "node1": 1, "node2": 0, "value": 12.0},
                {"type": "R", "node1": 1, "node2": 2, "value": 200.0},
                {"type": "R", "node1": 2, "node2": 0, "value": 400.0}
            ]
            solve circuit mna components comps ground 0 into mna_res
            set v_mid to mna_res's node_voltages's n2
            set gates to [
                {"id": "A", "inputs": [], "delay_ns": 1.0},
                {"id": "B", "inputs": ["A"], "delay_ns": 2.0}
            ]
            analyze digital static timing gates gates clock period 10.0 into sta_res
            set fmax to sta_res's max_frequency_mhz
        """).strip()
        env = execute(code)
        # Voltage divider: 12V * (400 / 600) = 8V
        self.assertAlmostEqual(env["v_mid"], 8.0, places=2)
        self.assertGreater(env["fmax"], 0.0)

    # =========================================================================
    # DB
    # =========================================================================

    def test_db_btree_direct(self):
        btree = BTreeStorageEnginePure(order=4)
        for i in range(15):
            btree.insert(f"k_{i:02d}", i)
        self.assertEqual(btree.search("k_07"), 7)
        self.assertEqual(btree.total_keys, 15)
        range_res = btree.range_scan("k_03", "k_06")
        self.assertEqual(len(range_res), 4)

    def test_db_cbo_direct(self):
        tables = {
            "users": {"rows": 10000, "pages": 200, "ndv": 10000, "indexes": ["id"]},
            "orders": {"rows": 100000, "pages": 1500, "ndv": 10000, "indexes": ["user_id"]},
        }
        joins = [{"left_table": "users", "right_table": "orders", "join_col": "user_id"}]
        res = CostBasedQueryOptimizerCBO.optimize(tables, joins)
        self.assertGreater(res["total_cost"], 0.0)
        self.assertIn(res["root_operator"], ("HashJoin", "NestedLoopJoin"))

    def test_db_spoken_english(self):
        code = textwrap.dedent("""
            use db
            benchmark btree index order 4 keys 15 into btree_res
            set n_keys to btree_res's total_keys
            set tbls to {
                "t1": {"rows": 1000, "pages": 50, "ndv": 1000, "indexes": ["id"]},
                "t2": {"rows": 5000, "pages": 200, "ndv": 1000, "indexes": ["t1_id"]}
            }
            set jns to [{"left_table": "t1", "right_table": "t2"}]
            optimize join query tables tbls joins jns into cbo_res
            set cbo_cost to cbo_res's total_cost
        """).strip()
        env = execute(code)
        self.assertEqual(env["n_keys"], 15)
        self.assertGreater(env["cbo_cost"], 0.0)


if __name__ == "__main__":
    unittest.main()
