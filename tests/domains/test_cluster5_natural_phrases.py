"""Tests for Cluster 5 (Industry, Workflows & Applications) natural English phrases:
finance, agent, chain, db, geo, office, telecom, metrics, web
"""

from doomscript.compiler.engine import execute


def test_cluster5_agent_and_geo(capsys):
    code = """
use agent
run debate on topic "AI Alignment" rounds 1 into debate_res
say debate_res.consensus is not None

use geo
poly = [{"lat": 0.0, "lon": 0.0}, {"lat": 10.0, "lon": 0.0}, {"lat": 10.0, "lon": 10.0}, {"lat": 0.0, "lon": 10.0}]
pt = {"lat": 5.0, "lon": 5.0}
check if point pt is inside polygon poly into inside
say inside == True
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"


def test_cluster5_telecom_metrics_web(capsys):
    code = """
use telecom
msg = [1, 2, 3, 4]
encode with reed solomon message msg parity 2 into rs_encoded
say count of rs_encoded == 6

use metrics
vals = [10.0, 20.0, 30.0, 40.0, 50.0]
calculate 50th percentile of vals into p50
say p50 == 30.0

use web
html_text = "<html><head><title>DoomScript</title></head><body><h1>Heading</h1></body></html>"
extract metadata from html html_text into meta
say meta.title == "DoomScript"
"""
    execute(code)
    out = capsys.readouterr().out.strip().splitlines()
    assert out[0] == "True"
    assert out[1] == "True"
    assert out[2] == "True"
