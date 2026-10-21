import pytest
from doomscript.domains.chem.runtime import (
    MolecularConformerGenerator3D,
    chem_generate_3d_conformer,
)
from doomscript.domains.astronomy.runtime import (
    VSOP87PlanetaryEphemeris,
    astronomy_planet_position,
)
from doomscript.domains.game.runtime import (
    MinimaxAlphaBetaTransposition,
    game_minimax_solver,
)
from doomscript.domains.office.runtime import (
    SpreadsheetFormulaEngine,
)


def test_molecular_conformer_3d():
    # Ethane: C-C bond
    atoms = ["C", "C"]
    bonds = [(0, 1, 1)]
    conf = MolecularConformerGenerator3D.generate_conformer(atoms, bonds, steps=80, lr=0.05)
    assert "atoms" in conf
    assert len(conf["atoms"]) == 2
    assert "total_steric_energy" in conf
    
    # Distance between carbon atoms should approach ~1.54 A
    a0 = conf["atoms"][0]
    a1 = conf["atoms"][1]
    dx = a0["x"] - a1["x"]
    dy = a0["y"] - a1["y"]
    dz = a0["z"] - a1["z"]
    dist = (dx**2 + dy**2 + dz**2) ** 0.5
    assert abs(dist - 1.54) < 0.2

    # Domain helper test
    rec = chem_generate_3d_conformer(atoms, bonds)
    assert len(rec["atoms"]) == 2


def test_vsop87_planetary_ephemeris():
    # Earth at J2000.0 (JD 2451545.0)
    jd_j2000 = 2451545.0
    res = VSOP87PlanetaryEphemeris.compute_heliocentric_coordinates("earth", jd_j2000)
    assert res["planet"] == "earth"
    # Earth's distance to Sun is ~1.0 AU
    assert abs(res["heliocentric_radius_au"] - 1.0) < 0.05
    assert "x_au" in res and "y_au" in res and "z_au" in res

    # Mars test via helper
    mars_rec = astronomy_planet_position("mars", jd_j2000)
    # Mars semi-major axis ~1.52 AU
    assert abs(mars_rec["heliocentric_radius_au"] - 1.52) < 0.2


def test_minimax_alpha_beta():
    # Nim game: heap of stones, can take 1 or 2 stones.
    # Player taking last stone wins (+100 for MAX, -100 for MIN)
    # State: (remaining_stones, next_player)
    def get_moves(state, is_max):
        stones, _ = state
        if stones <= 0:
            return []
        if stones == 1:
            return [1]
        return [1, 2]

    def apply_move(state, move):
        stones, player = state
        next_player = "MIN" if player == "MAX" else "MAX"
        return (stones - move, next_player)

    def is_terminal(state):
        stones, _ = state
        return stones <= 0

    def eval_state(state):
        stones, player = state
        if stones <= 0:
            # If next player is MIN, MAX just made the winning move
            return 100.0 if player == "MIN" else -100.0
        return 0.0

    solver = game_minimax_solver(get_moves, apply_move, is_terminal, eval_state)

    # From state (2, 'MAX'), move 2 wins immediately
    move, score = solver.search_best_move(state=(2, "MAX"), max_depth=3, is_maximizing=True)
    assert move == 2
    assert score == 100.0


def test_spreadsheet_formula_engine():
    data = {
        "A1": 10,
        "A2": 25,
        "A3": "=SUM(A1:A2)",
        "B1": "=A3 * 2",
    }
    evaluated = SpreadsheetFormulaEngine.evaluate_grid(data)
    assert evaluated["A1"] == 10
    assert evaluated["A2"] == 25
    assert evaluated["A3"] == 35.0
    assert evaluated["B1"] == 70.0

    # Cycle detection
    cyclic_data = {
        "A1": "=B1",
        "B1": "=A1",
    }
    with pytest.raises(ValueError, match="Circular dependency"):
        SpreadsheetFormulaEngine.evaluate_grid(cyclic_data)
