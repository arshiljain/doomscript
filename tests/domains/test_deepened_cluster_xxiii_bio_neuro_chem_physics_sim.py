"""Unit tests for Cluster XXIII Deepened Domains:
Bio, Neuro, Chem, Physics, and Sim.
"""

import sys
import os
sys.path.insert(0, os.path.abspath("src"))

import math
import textwrap
import unittest
from doomscript.compiler.engine import execute

from doomscript.domains.bio.runtime import (
    NussinovRNAFoldingDynamicProgramming,
    SmithWatermanLocalAlignment,
    bio_nussinov_rna_fold,
    bio_smith_waterman_align,
)
from doomscript.domains.neuro.runtime import (
    ContinuousAttractorNeuralNetworkCANN,
    HopfieldNetworkAssociativeMemory,
    neuro_cann_simulate,
    neuro_hopfield_recall,
)
from doomscript.domains.chem.runtime import (
    ChemicalStoichiometryBalancer,
    LennardJonesMolecularDynamics,
    chem_balance_reaction,
    chem_lennard_jones_md,
)
from doomscript.domains.physics.runtime import (
    BarnesHutNBodySimulation,
    RelativisticLorentzKinematics,
    physics_barnes_hut_nbody,
    physics_lorentz_transform,
)
from doomscript.domains.sim.runtime import (
    DiscreteEventSimulationDESEngine,
    CellularAutomataLatticeGasHydrodynamics,
    sim_des_queue,
    sim_lattice_gas,
)


class TestDeepenedClusterXXIII(unittest.TestCase):

    # =========================================================================
    # BIO
    # =========================================================================

    def test_bio_nussinov_direct(self):
        seq = "GGGAAACCC"
        res = NussinovRNAFoldingDynamicProgramming.fold(seq, min_loop_length=1)
        self.assertGreater(res["pair_count"], 0)
        self.assertIn("(", res["dot_bracket"])
        self.assertIn(")", res["dot_bracket"])
        self.assertEqual(res["length"], len(seq))

    def test_bio_smith_waterman_direct(self):
        s1 = "ACGTACGT"
        s2 = "CGTAC"
        res = SmithWatermanLocalAlignment.align(s1, s2, match_score=2.0, mismatch_penalty=-1.0)
        self.assertGreater(res["score"], 0.0)
        self.assertGreater(res["identity_percent"], 80.0)

    def test_bio_spoken_english(self):
        code = textwrap.dedent("""
            use bio
            set rna_seq to "GCUUCGGC"
            fold rna secondary structure sequence rna_seq min loop 1 into fold_res
            set pairs to fold_res's pair_count
            set s1 to "HEAGAWGHEE"
            set s2 to "PAWHEAE"
            align sequences s1 and s2 with smith waterman match 3.0 mismatch -1.0 gap open 2.0 gap extend 1.0 into sw_res
            set sw_score to sw_res's score
        """).strip()
        env = execute(code)
        self.assertGreater(env["pairs"], 0)
        self.assertGreater(env["sw_score"], 0.0)

    # =========================================================================
    # NEURO
    # =========================================================================

    def test_neuro_cann_direct(self):
        res = ContinuousAttractorNeuralNetworkCANN.simulate(num_neurons=24, stimulus_angle=0.0, steps=30)
        self.assertEqual(res["num_neurons"], 24)
        self.assertGreater(res["peak_firing_rate"], 0.0)
        self.assertAlmostEqual(res["bump_center_rad"], 0.0, places=1)

    def test_neuro_hopfield_direct(self):
        pat1 = [1, 1, -1, -1, 1, 1, -1, -1]
        pat2 = [-1, -1, 1, 1, -1, -1, 1, 1]
        probe = [1, 1, -1, -1, 1, -1, -1, -1]  # 1 bit flipped from pat1
        res = HopfieldNetworkAssociativeMemory.train_and_recall([pat1, pat2], probe)
        self.assertTrue(res["converged"])
        self.assertEqual(res["recalled_pattern"], pat1)
        self.assertEqual(res["best_matching_pattern_index"], 0)

    def test_neuro_spoken_english(self):
        code = textwrap.dedent("""
            use neuro
            simulate continuous attractor network neurons 24 stimulus 0.0 steps 30 into cann_res
            set peak_r to cann_res's peak_firing_rate
            set p1 to [1, 1, -1, -1, 1, 1]
            set p2 to [-1, -1, 1, 1, -1, -1]
            set probe_vec to [1, 1, -1, -1, 1, -1]
            recall hopfield memory for probe probe_vec from patterns [p1, p2] max steps 20 into hop_res
            set is_conv to hop_res's converged
            set recalled to hop_res's recalled_pattern
        """).strip()
        env = execute(code)
        self.assertGreater(env["peak_r"], 0.0)
        self.assertTrue(env["is_conv"])
        self.assertEqual(env["recalled"], [1, 1, -1, -1, 1, 1])

    # =========================================================================
    # CHEM
    # =========================================================================

    def test_chem_balance_reaction_direct(self):
        res1 = ChemicalStoichiometryBalancer.balance("H2 + O2 -> H2O")
        self.assertEqual(res1["reactant_coefficients"]["H2"], 2)
        self.assertEqual(res1["reactant_coefficients"]["O2"], 1)
        self.assertEqual(res1["product_coefficients"]["H2O"], 2)

        res2 = ChemicalStoichiometryBalancer.balance("C6H12O6 + O2 -> CO2 + H2O")
        self.assertEqual(res2["reactant_coefficients"]["C6H12O6"], 1)
        self.assertEqual(res2["reactant_coefficients"]["O2"], 6)
        self.assertEqual(res2["product_coefficients"]["CO2"], 6)
        self.assertEqual(res2["product_coefficients"]["H2O"], 6)

    def test_chem_lennard_jones_md_direct(self):
        res = LennardJonesMolecularDynamics.simulate(num_particles=8, box_length=4.0, steps=30, dt=0.005)
        self.assertEqual(res["num_particles"], 8)
        self.assertGreater(res["temperature"], 0.0)
        self.assertIsInstance(res["total_energy"], float)

    def test_chem_spoken_english(self):
        code = textwrap.dedent("""
            use chem
            balance chemical reaction "Fe + O2 -> Fe2O3" into bal_res
            set is_conserved to bal_res's elements_conserved
            simulate molecular dynamics lennard jones particles 8 box 4.0 steps 20 into md_res
            set md_temp to md_res's temperature
        """).strip()
        env = execute(code)
        self.assertTrue(env["is_conserved"])
        self.assertGreater(env["md_temp"], 0.0)

    # =========================================================================
    # PHYSICS
    # =========================================================================

    def test_physics_barnes_hut_direct(self):
        bodies = [
            {"m": 10.0, "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0},
            {"m": 1.0, "x": 1.0, "y": 0.0, "vx": 0.0, "vy": 3.0},
            {"m": 1.0, "x": -1.0, "y": 0.0, "vx": 0.0, "vy": -3.0},
        ]
        res = BarnesHutNBodySimulation.simulate(bodies, theta=0.5, steps=10, dt=0.01)
        self.assertEqual(res["num_bodies"], 3)
        self.assertGreater(res["kinetic_energy"], 0.0)

    def test_physics_lorentz_direct(self):
        # Event at (ct=10, x=6, y=0, z=0), boost with v=(0.6, 0, 0), c=1.0
        # beta = 0.6, gamma = 1 / sqrt(1 - 0.36) = 1.25
        # ct' = 1.25 * (10 - 0.6 * 6) = 1.25 * 6.4 = 8.0
        # x' = 1.25 * (6 - 0.6 * 10) = 1.25 * 0 = 0.0
        # Invariant s^2 = 100 - 36 = 64 = 8^2 - 0^2 = 64
        res = RelativisticLorentzKinematics.boost_event([10.0, 6.0, 0.0, 0.0], [0.6, 0.0, 0.0], c=1.0)
        self.assertAlmostEqual(res["gamma"], 1.25, places=3)
        self.assertAlmostEqual(res["boosted_event"][0], 8.0, places=3)
        self.assertAlmostEqual(res["boosted_event"][1], 0.0, places=3)
        self.assertTrue(res["invariance_preserved"])

    def test_physics_spoken_english(self):
        code = textwrap.dedent("""
            use physics
            set bodies to [
                {"m": 10.0, "x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0},
                {"m": 1.0, "x": 2.0, "y": 0.0, "vx": 0.0, "vy": 2.0}
            ]
            simulate barnes hut nbody bodies theta 0.5 steps 10 dt 0.01 into bh_res
            set tot_e to bh_res's total_energy
            set evt to [10.0, 6.0, 0.0, 0.0]
            set vel to [0.6, 0.0, 0.0]
            boost lorentz event evt with velocity vel speed of light 1.0 into lor_res
            set gam to lor_res's gamma
        """).strip()
        env = execute(code)
        self.assertIsInstance(env["tot_e"], float)
        self.assertAlmostEqual(env["gam"], 1.25, places=2)

    # =========================================================================
    # SIM
    # =========================================================================

    def test_sim_des_queue_direct(self):
        traffic = [(1.0, 2.0), (0.5, 1.5), (2.0, 3.0), (1.0, 1.0)]
        res = DiscreteEventSimulationDESEngine.simulate_queue(traffic, num_servers=1)
        self.assertEqual(res["total_customers_served"], 4)
        self.assertGreater(res["server_utilization_ratio"], 0.0)
        self.assertGreater(res["simulation_duration"], 0.0)

    def test_sim_lattice_gas_direct(self):
        res = CellularAutomataLatticeGasHydrodynamics.simulate(width=12, height=12, steps=20, initial_density=0.25)
        self.assertTrue(res["mass_conserved"])
        self.assertGreater(res["total_particles"], 0)
        self.assertEqual(res["width"], 12)

    def test_sim_spoken_english(self):
        code = textwrap.dedent("""
            use sim
            set traffic to [(1.0, 2.0), (0.5, 1.5), (2.0, 3.0), (1.0, 1.0)]
            simulate discrete event queue traffic servers 1 into des_res
            set cust_count to des_res's total_customers_served
            simulate lattice gas hydrodynamics width 12 height 12 steps 20 density 0.25 into lga_res
            set mass_ok to lga_res's mass_conserved
        """).strip()
        env = execute(code)
        self.assertEqual(env["cust_count"], 4)
        self.assertTrue(env["mass_ok"])


if __name__ == "__main__":
    unittest.main()
