"""End-to-End Regression Test Suite for Multi-Domain Showcases
Verifying cross-domain pipeline synthesis across multiple specialized domains:
1. Autonomous Lab Pipeline (chem + bio + robotics + ml)
2. Quant Trading Desk (finance + time_series + agent + office)
3. Spatial Game Engine (physics + game + graphics + spatial_audio)
"""

from pathlib import Path
import pytest
from doomscript.compiler.engine import execute


EXAMPLES_DIR = Path(__file__).parent.parent.parent / "examples"


def test_autonomous_lab_pipeline_showcase():
    doom_file = EXAMPLES_DIR / "autonomous_lab_pipeline.doom"
    assert doom_file.exists(), f"Missing showcase file: {doom_file}"
    code = doom_file.read_text(encoding="utf-8")
    res = execute(code)

    # Chemistry assertions
    comp = res.get("aspirin_comp")
    assert comp is not None
    assert comp["C"] > 50.0
    conf = res.get("conformer")
    assert conf is not None
    assert conf.num_atoms == 13

    # Biology assertions
    frags = res.get("frags")
    assert len(frags) >= 2
    cpgs = res.get("cpgs")
    assert len(cpgs) >= 1

    # Robotics assertions
    scan = res.get("scan")
    assert scan is not None
    assert scan.readings is not None
    plan = res.get("pipette_plan")
    assert plan is not None
    assert plan.name == "PipettePlate"
    assert plan.total_waypoints >= 10

    # ML assertions
    model = res.get("yield_model")
    assert model is not None
    assert model.target == "yield"
    assert model.is_trained is True


def test_quant_trading_desk_showcase():
    doom_file = EXAMPLES_DIR / "quant_trading_desk.doom"
    assert doom_file.exists(), f"Missing showcase file: {doom_file}"
    code = doom_file.read_text(encoding="utf-8")
    res = execute(code)

    # Time series assertions
    future = res.get("future_forecast")
    assert future is not None
    assert len(future.forecasts) == 3
    acf = res.get("price_acf")
    assert len(acf) >= 2

    # Finance assertions
    call_p = res.get("call_price")
    assert call_p > 0.0
    port = res.get("desk_port")
    assert port is not None
    assert port.name == "QuantAlpha"
    assert port.num_assets == 3
    assert port.weights["NVDA"] == 0.45

    # Agent assertions
    team = res.get("desk_team")
    assert team is not None
    assert team.name == "QuantOperations"
    assert len(team.agents) == 2

    # Office assertions
    blotter = res.get("blotter")
    assert blotter is not None
    assert len(blotter.rows) == 4


def test_spatial_game_engine_showcase():
    doom_file = EXAMPLES_DIR / "spatial_game_engine.doom"
    assert doom_file.exists(), f"Missing showcase file: {doom_file}"
    code = doom_file.read_text(encoding="utf-8")
    res = execute(code)

    # Physics assertions
    ke = res.get("projectile_ke")
    assert ke == 1000.0
    v_esc = res.get("earth_escape_v")
    assert v_esc > 11000.0

    # Game assertions
    hero = res.get("hero")
    assert hero.name == "Paladin"
    assert hero.hp == 120
    boss = res.get("boss")
    assert boss.name == "RedDragon"
    init_roll = res.get("initiative_roll")
    assert 7 <= init_roll <= 22
    arena = res.get("arena_grid")
    assert arena is not None

    # Graphics assertions
    canvas = res.get("game_canvas")
    assert canvas is not None
    assert canvas.width == 800
    assert canvas.height == 600

    # Spatial audio assertions
    binaural = res.get("binaural_spell")
    assert len(binaural[0]) > 0
    assert len(binaural[1]) > 0
    doppler = res.get("doppler_spell")
    assert len(doppler) > 0
    reverb = res.get("room_reverb")
    assert len(reverb) > 0
