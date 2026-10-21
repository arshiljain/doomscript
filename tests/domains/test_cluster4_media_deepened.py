"""Comprehensive test suite verifying natural spoken English phrasings
for all 8 domains in Cluster 4: Media, Audio & Simulation
(audio, spatial_audio, signals, image, graphics, game, sim, time_series)
"""

import pytest
from doomscript.compiler.engine import execute


def test_audio_natural_phrases():
    code = """
use audio

create blank audio of 2 seconds into a
duration of audio a into dur
say dur >= 2.0

calculate fft of [1.0, 0.0, -1.0, 0.0] into f_res
say len(f_res) == 4
"""
    res = execute(code)
    assert res.get("dur") >= 2.0
    assert len(res.get("f_res")) == 4


def test_spatial_audio_natural_phrases():
    code = """
use spatial_audio

spatialize audio [0.5, 0.5] at azimuth 45.0 elevation 0.0 into binaural
say len(binaural[0]) > 0

simulate doppler effect on [0.1, 0.2, 0.3] with velocity 10.0 into dop
say len(dop) > 0

apply reverb to [0.1, 0.2] with rt60 0.5 into rev
say len(rev) > 0
"""
    res = execute(code)
    assert len(res.get("binaural")[0]) > 0
    assert len(res.get("dop")) > 0
    assert len(res.get("rev")) > 0


def test_signals_natural_phrases():
    code = """
use signals

decompose signal [1.0, 2.0, 3.0, 4.0] using haar wavelet into dwt
say dwt is not None

find peaks in signal [0.1, 0.9, 0.2, 0.8, 0.1] into pks
say len(pks) >= 1
"""
    res = execute(code)
    assert res.get("dwt") is not None
    assert len(res.get("pks")) >= 1


def test_image_natural_phrases():
    code = """
use image

create blank image of 100 by 100 into img
resize image img to width 50 and height 50 into rimg
dimensions of image rimg into dims
say dims[0] == 50
say dims[1] == 50
"""
    res = execute(code)
    dims = res.get("dims")
    assert dims[0] == 50
    assert dims[1] == 50


def test_graphics_natural_phrases():
    code = """
use graphics

create canvas width 800 height 600 into c
draw circle on c at 100, 100 radius 25 with color (255, 0, 0)
draw line on c from 10, 10 to 50, 50 with color (0, 255, 0)
say c is not None
say c.width == 800
say c.height == 600
"""
    res = execute(code)
    c = res.get("c")
    assert c is not None
    assert c.width == 800
    assert c.height == 600


def test_game_natural_phrases():
    code = """
use game

roll dice "2d6+3" into roll_val
say roll_val >= 5

create combatant "Warrior" with hp 100 attack 15 defense 5 into hero
say hero.name == "Warrior"
say hero.hp == 100

create tilemap with width 10 and height 10 into grid
say grid is not None
"""
    res = execute(code)
    assert res.get("roll_val") >= 5
    hero = res.get("hero")
    assert hero.name == "Warrior"
    assert hero.hp == 100
    assert res.get("grid") is not None


def test_sim_natural_phrases():
    code = """
use sim

simulate queue system with arrival 2.0 service 3.0 servers 1 into q_res
say q_res is not None

simulate random walk with 20 steps into walk
say len(walk) >= 20

sample normal with mean 0.0 and std 1.0 count 5 into samples
say len(samples) == 5
"""
    res = execute(code)
    assert res.get("q_res") is not None
    assert len(res.get("walk")) >= 20
    assert len(res.get("samples")) == 5


def test_time_series_natural_phrases():
    code = """
use time_series

forecast time series [10.0, 12.0, 14.0, 16.0, 18.0] with period 2 with steps 2 into preds
say len(preds.forecasts) == 2

calculate acf for [1.0, 2.0, 3.0, 4.0, 5.0] with lags 2 into acf_res
say len(acf_res) >= 2
"""
    res = execute(code)
    assert len(res.get("preds")["forecasts"]) == 2
    assert len(res.get("acf_res")) >= 2
