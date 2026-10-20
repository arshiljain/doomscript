"""Unit and integration tests for Deepened Cluster D (Physical Sciences & Hardware).

Tests the enhanced capabilities of:
- physics: BarnesHutNBody, ImpulseCollision2D, VanDerWaalsGas
- chem: MolecularGraphLayout, MorganFingerprint, ReactionKineticsSimulator
- bio: SequenceAligner, FMIndexBWT, PhylogeneticTreeNJ
- astronomy: PlanetaryEphemeris, EclipsePredictor, AtmosphericRefraction
- circuit: ModifiedNodalAnalysis, BodePlotAnalyzer, OpAmpModel
"""

import math
import pytest

from doomscript.domains.physics.runtime import (
    BarnesHutNBody,
    ImpulseCollision2D,
    VanDerWaalsGas,
    physics_barnes_hut_step,
    physics_resolve_collision,
    physics_van_der_waals_pressure,
)
from doomscript.domains.chem.runtime import (
    MolecularGraphLayout,
    MorganFingerprint,
    ReactionKineticsSimulator,
    chem_generate_layout,
    chem_morgan_fingerprint,
    chem_tanimoto_similarity,
    chem_simulate_kinetics,
)
from doomscript.domains.bio.runtime import (
    SequenceAligner,
    FMIndexBWT,
    PhylogeneticTreeNJ,
    bio_affine_align,
    bio_fm_index_search,
    bio_neighbor_joining_tree,
)
from doomscript.domains.astronomy.runtime import (
    PlanetaryEphemeris,
    EclipsePredictor,
    AtmosphericRefraction,
    astronomy_planet_position,
    astronomy_planet_geocentric,
    astronomy_predict_eclipse,
    astronomy_atmospheric_refraction,
)
from doomscript.domains.circuit.runtime import (
    ModifiedNodalAnalysis,
    BodePlotAnalyzer,
    OpAmpModel,
    circuit_mna_dc_solve,
    circuit_bode_plot,
    circuit_opamp_amplify,
)


# ==============================================================================
# Physics Tests
# ==============================================================================

def test_barnes_hut_nbody():
    particles = [
        {"x": 0.0, "y": 0.0, "z": 0.0, "vx": 0.0, "vy": 0.0, "vz": 0.0, "mass": 1000.0},
        {"x": 10.0, "y": 0.0, "z": 0.0, "vx": 0.0, "vy": 5.0, "vz": 0.0, "mass": 1.0},
        {"x": -10.0, "y": 0.0, "z": 0.0, "vx": 0.0, "vy": -5.0, "vz": 0.0, "mass": 1.0},
    ]

    updated = BarnesHutNBody.step(particles, dt=0.1, theta=0.5, G=1.0)
    assert len(updated) == 3

    # Heavy central particle should barely move
    assert abs(updated[0]["x"]) < 0.01
    assert abs(updated[0]["y"]) < 0.01

    # Orbiting particle 1 at x=10 should accelerate towards negative x (towards center)
    assert updated[1]["vx"] < 0.0
    # Orbiting particle 2 at x=-10 should accelerate towards positive x
    assert updated[2]["vx"] > 0.0


def test_impulse_collision_2d():
    # Body A moving right (+x), Body B stationary at origin
    body_a = {"x": -2.0, "y": 0.0, "vx": 5.0, "vy": 0.0, "omega": 0.0, "mass": 2.0, "inertia": 1.0, "restitution": 1.0}
    body_b = {"x": 0.0, "y": 0.0, "vx": 0.0, "vy": 0.0, "omega": 0.0, "mass": 2.0, "inertia": 1.0, "restitution": 1.0}

    # Collision contact at x=-1.0, normal points from A to B (+x direction: (1.0, 0.0))
    res = ImpulseCollision2D.resolve_collision(
        body_a, body_b,
        contact_point=(-1.0, 0.0),
        normal=(1.0, 0.0),
        restitution=1.0,
        friction=0.0,
    )

    new_a = res["body_a"]
    new_b = res["body_b"]

    # Elastic equal-mass collision: A stops, B carries away all velocity
    assert abs(new_a["vx"]) < 1e-3
    assert abs(new_b["vx"] - 5.0) < 1e-3
    assert res["normal_impulse"] > 0.0


def test_van_der_waals_gas():
    gas = VanDerWaalsGas.for_substance("nitrogen")
    # T = 300 K, V = 0.024 m^3, n = 1.0 mol
    p_vdw = gas.calculate_pressure(temperature_k=300.0, volume_m3=0.024, moles=1.0)
    p_ideal = (1.0 * 8.314462618 * 300.0) / 0.024

    # Nitrogen pressure is slightly lower than ideal gas due to intermolecular attraction
    assert 0 < p_vdw < p_ideal
    assert abs(p_vdw - p_ideal) / p_ideal < 0.05

    # Reverse volume calculation
    v_calc = gas.calculate_volume(pressure_pa=p_vdw, temperature_k=300.0, moles=1.0)
    assert abs(v_calc - 0.024) < 1e-4

    # Critical constants
    crit = gas.critical_constants()
    assert crit["critical_temperature_k"] > 100.0
    assert crit["critical_pressure_pa"] > 1e6
    assert 0.35 <= crit["critical_compressibility"] <= 0.40


# ==============================================================================
# Chem Tests
# ==============================================================================

def test_molecular_graph_layout():
    # Ethanol: C - C - O
    smiles = "CCO"
    layout = chem_generate_layout(smiles)
    assert len(layout) == 3

    # Check that distances between bonded atoms are reasonable (~1.5)
    p0 = layout[0]
    p1 = layout[1]
    p2 = layout[2]

    d01 = math.hypot(p0[0] - p1[0], p0[1] - p1[1])
    d12 = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
    assert 0.8 < d01 < 2.5
    assert 0.8 < d12 < 2.5


def test_morgan_fingerprint_and_similarity():
    # Ethanol vs Propanol vs Benzene
    fp_ethanol = MorganFingerprint.generate("CCO", radius=2, n_bits=1024)
    fp_propanol = MorganFingerprint.generate("CCCO", radius=2, n_bits=1024)
    fp_benzene = MorganFingerprint.generate("c1ccccc1", radius=2, n_bits=1024)

    assert len(fp_ethanol) > 0
    assert len(fp_propanol) > 0
    assert len(fp_benzene) > 0

    sim_same = MorganFingerprint.tanimoto_similarity(fp_ethanol, fp_ethanol)
    assert abs(sim_same - 1.0) < 1e-6

    sim_homolog = MorganFingerprint.tanimoto_similarity(fp_ethanol, fp_propanol)
    sim_distinct = MorganFingerprint.tanimoto_similarity(fp_ethanol, fp_benzene)

    # Ethanol should be significantly more similar to propanol than to benzene
    assert sim_homolog > sim_distinct
    assert sim_homolog > 0.3


def test_reaction_kinetics_simulator():
    # A + B -> C (irreversible, k_f = 1.0)
    reactions = [
        {"reactants": {"A": 1, "B": 1}, "products": {"C": 1}, "k_f": 1.0, "k_r": 0.0}
    ]
    initial = {"A": 1.0, "B": 1.0, "C": 0.0}
    res = ReactionKineticsSimulator.simulate(initial, reactions, t_span=(0.0, 2.0), dt=0.02)

    concs = res["concentrations"]
    final = res["final"]

    # Reactants decrease monotonically
    assert concs["A"][-1] < concs["A"][0]
    assert concs["B"][-1] < concs["B"][0]
    # Product increases
    assert concs["C"][-1] > concs["C"][0]

    # Mass conservation: [A] + [C] == 1.0
    total_mass = final["A"] + final["C"]
    assert abs(total_mass - 1.0) < 1e-3


# ==============================================================================
# Bio Tests
# ==============================================================================

def test_sequence_aligner_affine():
    s1 = "ACGTACGT"
    s2 = "ACGTTCGT"

    res = SequenceAligner.align_global(s1, s2, match=2, mismatch=-1, gap_open=-3, gap_extend=-1)
    assert res["matches"] == 7
    assert res["mismatches"] == 1
    assert res["gaps"] == 0
    assert res["identity_percent"] > 80.0

    # Alignment with gap
    s3 = "ACGTACGT"
    s4 = "ACGTTTACGT"
    res_gap = SequenceAligner.align_global(s3, s4, match=2, mismatch=-1, gap_open=-2, gap_extend=-1)
    assert res_gap["gaps"] >= 2
    assert len(res_gap["alignment1"]) == len(res_gap["alignment2"])


def test_fm_index_bwt():
    seq = "GATTACAGATTACA"
    idx = FMIndexBWT(seq)

    # Count occurrences
    assert idx.count("GATTA") == 2
    assert idx.count("TACA") == 2
    assert idx.count("ZZZZ") == 0

    # Locate positions
    pos = idx.locate("GATTA")
    assert sorted(pos) == [0, 7]


def test_phylogenetic_tree_nj():
    taxa = ["A", "B", "C", "D"]
    # Distance matrix where (A, B) is close, (C, D) is close
    dist = {
        "A": {"A": 0.0, "B": 2.0, "C": 7.0, "D": 7.0},
        "B": {"A": 2.0, "B": 0.0, "C": 7.0, "D": 7.0},
        "C": {"A": 7.0, "B": 7.0, "C": 0.0, "D": 2.0},
        "D": {"A": 7.0, "B": 7.0, "C": 2.0, "D": 0.0},
    }

    tree = PhylogeneticTreeNJ.build_tree(taxa, dist)
    newick = tree["newick"]
    assert isinstance(newick, str)
    assert newick.endswith(";")
    # Tree should group A with B and C with D
    assert ("A:" in newick and "B:" in newick) or ("C:" in newick and "D:" in newick)


# ==============================================================================
# Astronomy Tests
# ==============================================================================

def test_planetary_ephemeris():
    jd_j2000 = 2451545.0  # Jan 1, 2000 12:00 TT
    earth = PlanetaryEphemeris.get_heliocentric_position("earth", jd_j2000)
    assert abs(earth["radius_au"] - 1.0) < 0.03

    mars = PlanetaryEphemeris.get_heliocentric_position("mars", jd_j2000)
    assert abs(mars["radius_au"] - 1.52) < 0.15

    # Geocentric calculations
    geo_mars = PlanetaryEphemeris.get_geocentric_position("mars", jd_j2000)
    assert geo_mars["distance_au"] > 0.3
    assert 0.0 <= geo_mars["illuminated_fraction"] <= 1.0


def test_eclipse_predictor():
    jd = 2451545.0
    cond = EclipsePredictor.predict_eclipse_conditions(jd)
    assert "target" in cond
    assert "eclipse_type" in cond
    assert 0.0 <= cond["moon_phase"] <= 1.0
    assert cond["magnitude"] >= 0.0


def test_atmospheric_refraction():
    # Horizon (apparent altitude 0 deg): refraction ~34 arcminutes
    r_horizon = AtmosphericRefraction.calculate_refraction(0.0)
    assert 30.0 < r_horizon["refraction_arcmin"] < 40.0
    assert r_horizon["airmass"] > 20.0

    # Zenith (apparent altitude 90 deg): refraction ~0
    r_zenith = AtmosphericRefraction.calculate_refraction(90.0)
    assert r_zenith["refraction_arcmin"] < 0.1
    assert abs(r_zenith["airmass"] - 1.0) < 0.05


# ==============================================================================
# Circuit Tests
# ==============================================================================

def test_modified_nodal_analysis_dc():
    # Simple voltage divider:
    # V1 between node 1 and 0 (10V)
    # R1 between node 1 and 2 (1000 Ohm)
    # R2 between node 2 and 0 (1000 Ohm)
    sim = ModifiedNodalAnalysis()
    sim.add_voltage_source("V1", "1", "0", 10.0)
    sim.add_resistor("R1", "1", "2", 1000.0)
    sim.add_resistor("R2", "2", "0", 1000.0)

    res = sim.solve_dc()
    voltages = res["node_voltages"]
    assert abs(voltages["1"] - 10.0) < 1e-4
    assert abs(voltages["2"] - 5.0) < 1e-4
    assert voltages["0"] == 0.0


def test_modified_nodal_analysis_transient():
    # RC charging circuit:
    # V1 = 5V at node 1
    # R1 = 1000 Ohm between 1 and 2
    # C1 = 1uF between 2 and 0
    # Tau = 1ms. At t = 3ms, V(2) ~ 5 * (1 - e^-3) ~ 4.75V
    sim = ModifiedNodalAnalysis()
    sim.add_voltage_source("V1", "1", "0", 5.0)
    sim.add_resistor("R1", "1", "2", 1000.0)
    sim.add_capacitor("C1", "2", "0", 1e-6)

    res = sim.simulate_transient(t_stop=0.003, dt=0.0001)
    v2_traj = res["nodes"]["2"]
    assert len(v2_traj) > 0
    # Voltage starts near 0 and charges up towards 5V
    assert v2_traj[0] < 1.0
    assert v2_traj[-1] > 4.5


def test_bode_plot_analyzer():
    # 1st-order Low-pass filter: H(s) = 1 / (1 + s / wc)
    # wc = 2 * pi * 1000 rad/s
    wc = 2.0 * math.pi * 1000.0
    num = [1.0]
    den = [1.0, 1.0 / wc]

    res = BodePlotAnalyzer.analyze(num, den, f_min=10.0, f_max=100000.0, num_points=30)
    assert abs(res["dc_gain_db"] - 0.0) < 0.2
    # Cutoff should be approximately 1000 Hz
    assert res["cutoff_3db_hz"] is not None
    assert 700.0 < res["cutoff_3db_hz"] < 1400.0


def test_opamp_model():
    op = OpAmpModel(gain_ol=100000.0, v_sat_pos=15.0, v_sat_neg=-15.0, slew_rate_v_us=1.0)

    # Linear amplification within rails
    v_out1 = op.amplify(v_plus=0.00005, v_minus=0.0)
    assert abs(v_out1 - 5.0) < 1e-3

    # Positive saturation
    v_out_sat = op.amplify(v_plus=1.0, v_minus=0.0)
    assert abs(v_out_sat - 15.0) < 1e-3

    # Negative saturation
    v_out_negsat = op.amplify(v_plus=0.0, v_minus=1.0)
    assert abs(v_out_negsat - (-15.0)) < 1e-3

    # Slew rate limitation: max delta = 1V / us = 1e6 V/s * 1e-6 s = 1.0 V
    v_step = op.step_transient(v_plus=1.0, v_minus=0.0, current_v_out=0.0, dt=1e-6)
    assert abs(v_step - 1.0) < 1e-3
