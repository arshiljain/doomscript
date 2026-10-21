"""Tests for Cluster 4 (Media, Audio & Simulation) natural English phrases:
audio, spatial_audio, signals, image, graphics, game, sim, time_series
"""

from doomscript.compiler.engine import execute


def test_cluster4_audio_and_image(capsys):
    code = """
use audio
sig = [0.0, 1.0, 0.0, -1.0]
compute fft of sig into f_res
say count of f_res == 4

use image
create blank image of 100 by 100 into img
resize image img to width 50 and height 50 into resized_img
say resized_img is not None
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"


def test_cluster4_game_sim_time_series(capsys):
    code = """
use game
create combatant "Warrior" with hp 100 attack 15 defense 5 into hero
say hero.name == "Warrior"

use sim
simulate queue system with arrival 2.0 service 3.0 servers 1 into q_res
say q_res.avg_wait_time >= 0

use time_series
series = [10.0, 12.0, 14.0, 16.0, 18.0, 20.0, 22.0, 24.0]
forecast time series series with period 2 into preds
say count of preds > 0
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "True"
