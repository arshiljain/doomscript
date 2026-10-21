"""Comprehensive test suite verifying natural spoken English phrasings
and declarative blocks for all 9 domains in Cluster 5: Industry, Web & Operations
(finance, agent, chain, db, geo, office, telecom, metrics, web)
"""

import pytest
from doomscript.compiler.engine import execute


def test_finance_natural_phrases_and_blocks():
    code = """
use finance

calculate black-scholes price for call option on asset 100.0 strike 100.0 expiry 1.0 rate 0.05 volatility 0.2 into c_price
say c_price > 0.0

portfolio "Growth" into tech_port:
    asset "AAPL" with weight 0.4
    asset "MSFT" with weight 0.6

say tech_port.num_assets == 2
"""
    res = execute(code)
    assert res.get("c_price") > 0.0
    port = res.get("tech_port")
    assert port.num_assets == 2
    assert port.name == "Growth"
    assert port.weights["AAPL"] == 0.4
    assert port.weights["MSFT"] == 0.6


def test_agent_natural_blocks():
    code = """
use agent

define agent Alice with role "Researcher":
    instructions: "Find facts"

define agent Bob with role "Writer":
    instructions: "Draft report"

team "ContentSquad" into squad:
    member Alice
    member Bob

say squad.name == "ContentSquad"
"""
    res = execute(code)
    squad = res.get("squad")
    assert squad.name == "ContentSquad"
    assert len(squad.agents) == 2


def test_chain_natural_phrases():
    code = """
use chain

create merkle tree from ["tx1", "tx2", "tx3", "tx4"] into tree
get merkle root of tree into root
say root is not None
"""
    res = execute(code)
    assert res.get("tree") is not None
    assert res.get("root") is not None


def test_db_natural_phrases():
    code = """
use db

execute sql "SELECT 42 as num" into res
create wal logger into wal
say res is not None
say wal is not None
"""
    res = execute(code)
    assert res.get("res") is not None
    assert res.get("wal") is not None


def test_geo_natural_phrases():
    code = """
use geo

point at lat 37.7749 and lon -122.4194 into sf
point at lat 34.0522 and lon -118.2437 into la
distance between sf and la in km into d
say d > 500.0
"""
    res = execute(code)
    assert res.get("d") > 500.0


def test_office_natural_phrases():
    code = """
use office

create spreadsheet into sheet
add row ["Item", "Cost"] to spreadsheet sheet
add row ["Apple", 1.5] to spreadsheet sheet
say sheet is not None
"""
    res = execute(code)
    sheet = res.get("sheet")
    assert sheet is not None
    assert len(sheet.rows) == 2


def test_telecom_natural_phrases():
    code = """
use telecom

encode bits [1, 0, 1, 1] with hamming74 into enc
decode bits enc with hamming74 into dec
say dec[0] == [1, 0, 1, 1]
"""
    res = execute(code)
    assert res.get("dec")[0] == [1, 0, 1, 1]


def test_metrics_natural_phrases():
    code = """
use metrics

create counter "requests_total" into cnt
create gauge "active_connections" into g
say cnt is not None
say g is not None
"""
    res = execute(code)
    assert res.get("cnt") is not None
    assert res.get("g") is not None


def test_web_natural_phrases():
    code = """
use web

extract metadata from html "<html><head><title>DoomScript Web</title></head><body><p>Hello</p></body></html>" into meta
say meta.title == "DoomScript Web"
"""
    res = execute(code)
    meta = res.get("meta")
    assert meta.title == "DoomScript Web"
