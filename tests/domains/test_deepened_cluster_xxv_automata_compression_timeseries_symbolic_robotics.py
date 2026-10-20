"""Unit tests for deepened Cluster XXV domains:
- Automata (Glushkov Positional NFA, Linear Temporal Logic Model Checker)
- Compression (LZMA Pure Match Engine, Context Tree Weighting CTW)
- Time Series (Seasonal ARIMA SARIMA, Empirical Mode Decomposition EMD)
- Symbolic (Risch-Norman Indefinite Integrator, Analytical ODE Solver)
- Robotics (6-DOF Serial Manipulator FK/IK, State Lattice Motion Planner)
"""

import math
import textwrap
import unittest

from doomscript.compiler.engine import execute
from doomscript.domains.automata.runtime import (
    GlushkovPositionalNFA,
    LinearTemporalLogicModelChecker,
    automata_glushkov_compile,
    automata_glushkov_accepts,
    automata_ltl_model_check,
)
from doomscript.domains.compression.runtime import (
    LZMAPureEngine,
    ContextTreeWeightingCTW,
    compression_lzma_encode,
    compression_lzma_decode,
    compression_ctw_model,
)
from doomscript.domains.time_series.runtime import (
    SeasonalARIMASARIMA,
    EmpiricalModeDecompositionEMD,
    timeseries_sarima_forecast,
    timeseries_emd_decompose,
)
from doomscript.domains.symbolic.runtime import (
    RischNormanSymbolicIntegrator,
    SymbolicDifferentialEquationODESolver,
    symbolic_risch_integrate,
    symbolic_ode_solve,
)
from doomscript.domains.robotics.runtime import (
    SixDOFManipulatorKinematics,
    StateLatticeMotionPlanner,
    robotics_6dof_fk,
    robotics_6dof_ik,
    robotics_state_lattice_plan,
)


class TestDeepenedClusterXXV(unittest.TestCase):
    """Test suite for Cluster XXV deepened domain implementations."""

    # =========================================================================
    # Automata
    # =========================================================================

    def test_automata_glushkov_direct(self):
        nfa = GlushkovPositionalNFA.compile("(a|b)*a")
        self.assertEqual(nfa["positions_count"], 3)
        self.assertFalse(nfa["is_nullable"])
        self.assertEqual(nfa["first_set"], [1, 2, 3])
        self.assertEqual(nfa["last_set"], [3])
        self.assertTrue(GlushkovPositionalNFA.accepts(nfa, "a"))
        self.assertTrue(GlushkovPositionalNFA.accepts(nfa, "ba"))
        self.assertTrue(GlushkovPositionalNFA.accepts(nfa, "ababa"))
        self.assertFalse(GlushkovPositionalNFA.accepts(nfa, "b"))
        self.assertFalse(GlushkovPositionalNFA.accepts(nfa, "ab"))

    def test_automata_ltl_model_check_direct(self):
        # Request-Response liveness: G(req -> F ack)
        res_ok = LinearTemporalLogicModelChecker.check(
            states=["idle", "request", "acknowledge"],
            initial_states=["idle"],
            transitions={
                "idle": ["request", "idle"],
                "request": ["acknowledge"],
                "acknowledge": ["idle"],
            },
            labels={
                "idle": [],
                "request": ["req"],
                "acknowledge": ["ack"],
            },
            formula="G (req -> F ack)",
        )
        self.assertTrue(res_ok["satisfied"])

        # Safety violation: G safe
        res_fail = LinearTemporalLogicModelChecker.check(
            states=["s0", "s1", "err"],
            initial_states=["s0"],
            transitions={"s0": ["s1"], "s1": ["err"], "err": ["err"]},
            labels={"s0": ["safe"], "s1": ["safe"], "err": ["un在此"]},
            formula="G safe",
        )
        self.assertFalse(res_fail["satisfied"])
        self.assertEqual(res_fail["counterexample_path"], ["s0", "s1", "err"])

    def test_automata_spoken_english(self):
        code = textwrap.dedent("""
            use automata
            build glushkov nfa for regex "(0|1)*1" into nfa_odd
            test glushkov nfa nfa_odd on text "101" into match_101
            test glushkov nfa nfa_odd on text "100" into match_100
            model check ltl formula "G safe" on kripke system states ["ok1", "ok2"] initial ["ok1"] transitions {"ok1": ["ok2"], "ok2": ["ok2"]} labels {"ok1": ["safe"], "ok2": ["safe"]} into ltl_res
            set is_valid to ltl_res's satisfied
        """).strip()
        env = execute(code)
        self.assertTrue(env["match_101"])
        self.assertFalse(env["match_100"])
        self.assertTrue(env["is_valid"])

    # =========================================================================
    # Compression
    # =========================================================================

    def test_compression_lzma_direct(self):
        text = "TOBEORNOTTOBEORTOBEORNOT"
        enc = LZMAPureEngine.encode(text)
        self.assertGreater(enc["match_count"], 0)
        dec = LZMAPureEngine.decode(enc)
        self.assertEqual(dec, text)

    def test_compression_ctw_direct(self):
        # Repetitive binary sequence should compress to low bit rate
        seq = "01010101010101010101" * 5
        res = ContextTreeWeightingCTW.analyze_sequence(seq, max_depth=3)
        self.assertEqual(res["total_bits"], 100)
        self.assertLess(res["bits_per_symbol"], 0.2)
        self.assertGreater(res["compression_ratio"], 5.0)

    def test_compression_spoken_english(self):
        code = textwrap.dedent("""
            use compression
            compress lzma text "ABRACADABRABRACADABRA" into lzma_res
            decompress lzma record lzma_res into reconstructed
            model ctw context for sequence "0000000011111111" with depth 2 into ctw_res
            set ctw_bits to ctw_res's code_length_bits
        """).strip()
        env = execute(code)
        self.assertEqual(env["reconstructed"], "ABRACADABRABRACADABRA")
        self.assertGreater(env["lzma_res"]["match_count"], 0)
        self.assertGreater(env["ctw_bits"], 0.0)

    # =========================================================================
    # Time Series
    # =========================================================================

    def test_timeseries_sarima_direct(self):
        data = [10.0 + 1.2 * i + 2.0 * math.sin(i * 1.57) for i in range(24)]
        res = SeasonalARIMASARIMA.fit_and_forecast(data, p=1, d=1, q=0, forecast_steps=4)
        self.assertEqual(len(res["forecast"]), 4)
        # Should continue upward trend
        self.assertGreater(res["forecast"][-1], data[0])

    def test_timeseries_emd_direct(self):
        # Composite wave
        sig = [math.sin(0.4 * math.pi * i) + 0.5 * math.sin(0.1 * math.pi * i) for i in range(40)]
        res = EmpiricalModeDecompositionEMD.decompose(sig, max_imfs=2)
        self.assertGreaterEqual(res["total_imfs"], 1)
        self.assertEqual(len(res["residual"]), 40)

    def test_timeseries_spoken_english(self):
        code = textwrap.dedent("""
            use time_series
            set dat to [20.0, 22.0, 25.0, 28.0, 31.0, 34.0, 37.0, 40.0]
            fit sarima on dat order 1 1 0 seasonal 0 0 0 4 forecast 3 into sar_res
            set fcast to sar_res's forecast
            set wave to [1.0, 2.0, 1.0, -1.0, -2.0, -1.0, 1.0, 2.0, 1.0, -1.0, -2.0, -1.0]
            decompose emd series wave max imfs 2 into emd_res
            set imf_count to emd_res's total_imfs
        """).strip()
        env = execute(code)
        self.assertEqual(len(env["fcast"]), 3)
        self.assertGreater(env["fcast"][0], 35.0)
        self.assertGreaterEqual(env["imf_count"], 1)

    # =========================================================================
    # Symbolic
    # =========================================================================

    def test_symbolic_risch_integrate_direct(self):
        # Polynomial: 3*x^2 + 4*x - 5 -> x^3 + 2.0*x^2 - 5.0*x + C
        p_res = RischNormanSymbolicIntegrator.integrate("3*x^2 + 4*x - 5", var="x")
        self.assertTrue(p_res["is_elementary"])
        self.assertIn("x^3", p_res["antiderivative"])

        # Rational: 1 / (x + 2) -> ln(abs(x+2)) + C
        l_res = RischNormanSymbolicIntegrator.integrate("1/(x + 2)", var="x")
        self.assertIn("ln(abs(x+2))", l_res["antiderivative"])

        # Exponential: exp(2*x) -> 0.5*exp(2*x) + C
        e_res = RischNormanSymbolicIntegrator.integrate("exp(2*x)", var="x")
        self.assertIn("0.5*exp(2*x)", e_res["antiderivative"])

    def test_symbolic_ode_direct(self):
        # 2nd-order homogeneous: y'' - 5y' + 6y = 0 -> roots 3.0, 2.0
        ode2 = SymbolicDifferentialEquationODESolver.solve("y'' - 5y' + 6y = 0", dep_var="y", indep_var="x")
        self.assertEqual(ode2["order"], 2)
        self.assertEqual(ode2["characteristic_roots"], [3.0, 2.0])
        self.assertIn("exp(3*x)", ode2["general_solution"])

        # 1st-order linear: y' + 2y = 4 -> yp = 2.0
        ode1 = SymbolicDifferentialEquationODESolver.solve("y' + 2y = 4", dep_var="y", indep_var="x")
        self.assertEqual(ode1["order"], 1)
        self.assertEqual(ode1["particular_solution"], 2.0)

    def test_symbolic_spoken_english(self):
        code = textwrap.dedent("""
            use symbolic
            integrate risch expression "6*x^2 - 2*x" var x into int_res
            set antideriv to int_res's antiderivative
            solve ode equation "y'' - 5y' + 6y = 0" dependent y independent x into ode_res
            set sol to ode_res's general_solution
        """).strip()
        env = execute(code)
        self.assertIn("2.0*x^3", env["antideriv"])
        self.assertIn("C1*exp", env["sol"])

    # =========================================================================
    # Robotics
    # =========================================================================

    def test_robotics_6dof_kinematics_direct(self):
        ur5_dh = [
            {"a": 0.0, "alpha": math.pi / 2, "d": 0.089, "theta_offset": 0.0},
            {"a": -0.425, "alpha": 0.0, "d": 0.0, "theta_offset": 0.0},
            {"a": -0.392, "alpha": 0.0, "d": 0.0, "theta_offset": 0.0},
            {"a": 0.0, "alpha": math.pi / 2, "d": 0.109, "theta_offset": 0.0},
            {"a": 0.0, "alpha": -math.pi / 2, "d": 0.094, "theta_offset": 0.0},
            {"a": 0.0, "alpha": 0.0, "d": 0.082, "theta_offset": 0.0},
        ]
        q = [0.0, -math.pi / 2, math.pi / 2, 0.0, 0.0, 0.0]
        fk = SixDOFManipulatorKinematics.forward_kinematics(ur5_dh, q)
        ee_pos = fk["end_effector_position"]
        self.assertAlmostEqual(ee_pos[0], -0.392, places=2)
        self.assertAlmostEqual(ee_pos[1], -0.191, places=2)
        self.assertAlmostEqual(ee_pos[2], 0.420, places=2)

        # Inverse Kinematics
        ik = SixDOFManipulatorKinematics.inverse_kinematics_dls(
            ur5_dh, ee_pos, initial_q=[0.1, -1.4, 1.4, 0.0, 0.0, 0.0]
        )
        self.assertTrue(ik["success"])
        self.assertLess(ik["position_error_m"], 0.01)

    def test_robotics_state_lattice_direct(self):
        start = (0.0, 0.0, 0.0)
        goal = (6.0, 0.0, 0.0)
        obs = [{"x": 3.0, "y": 0.0, "radius": 0.8}]
        plan = StateLatticeMotionPlanner.plan(start, goal, obstacles=obs, step_len=1.0)
        self.assertTrue(plan["success"])
        self.assertGreater(len(plan["waypoints"]), 4)

    def test_robotics_spoken_english(self):
        code = textwrap.dedent("""
            use robotics
            set dh to [
                {"a": 0.0, "alpha": 1.5708, "d": 0.089, "theta_offset": 0.0},
                {"a": -0.425, "alpha": 0.0, "d": 0.0, "theta_offset": 0.0},
                {"a": -0.392, "alpha": 0.0, "d": 0.0, "theta_offset": 0.0},
                {"a": 0.0, "alpha": 1.5708, "d": 0.109, "theta_offset": 0.0},
                {"a": 0.0, "alpha": -1.5708, "d": 0.094, "theta_offset": 0.0},
                {"a": 0.0, "alpha": 0.0, "d": 0.082, "theta_offset": 0.0}
            ]
            set q to [0.0, -1.5708, 1.5708, 0.0, 0.0, 0.0]
            calculate 6dof fk dh params dh joint angles q into fk_res
            set ee_z to fk_res's end_effector_position's 2
            plan state lattice path from (0.0, 0.0, 0.0) to (5.0, 0.0, 0.0) obstacles [] step 1.0 into lat_res
            set path_ok to lat_res's success
        """).strip()
        # Note: In DoomScript possessives, ee_pos is a list, so we can access directly or test in python
        # Let's adjust to avoid indexing list with 's
        code_clean = textwrap.dedent("""
            use robotics
            set dh to [
                {"a": 0.0, "alpha": 1.5708, "d": 0.089, "theta_offset": 0.0},
                {"a": -0.425, "alpha": 0.0, "d": 0.0, "theta_offset": 0.0},
                {"a": -0.392, "alpha": 0.0, "d": 0.0, "theta_offset": 0.0},
                {"a": 0.0, "alpha": 1.5708, "d": 0.109, "theta_offset": 0.0},
                {"a": 0.0, "alpha": -1.5708, "d": 0.094, "theta_offset": 0.0},
                {"a": 0.0, "alpha": 0.0, "d": 0.082, "theta_offset": 0.0}
            ]
            set q to [0.0, -1.5708, 1.5708, 0.0, 0.0, 0.0]
            calculate 6dof fk dh params dh joint angles q into fk_res
            set pos to fk_res's end_effector_position
            plan state lattice path from (0.0, 0.0, 0.0) to (5.0, 0.0, 0.0) obstacles [] step 1.0 into lat_res
            set path_ok to lat_res's success
        """).strip()
        env = execute(code_clean)
        self.assertAlmostEqual(env["pos"][2], 0.420, places=2)
        self.assertTrue(env["path_ok"])


if __name__ == "__main__":
    unittest.main()
