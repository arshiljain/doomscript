import pytest
from doomscript.compiler.engine import execute


def test_discourse_block_with_target():
    code = """
set raw_deals to [
    {client: "Acme Corp", amount: 45000, closed: true},
    {client: "Global Tech", amount: 120000, closed: true},
    {client: "Omni Industries", amount: 35000, closed: false},
    {client: "Vertex Systems", amount: 85000, closed: true},
    {client: "Nova Retail", amount: 60000, closed: true}
]

take raw_deals into top_deals:
    keep where closed
    sort by amount descending
    take 3

say "Top deals: {count of top_deals}"
"""
    res = execute(code)
    assert len(res["top_deals"]) == 3
    assert res["top_deals"][0]["client"] == "Global Tech"
    assert res["top_deals"][1]["client"] == "Vertex Systems"
    assert res["top_deals"][2]["client"] == "Nova Retail"


def test_discourse_block_in_place():
    code = """
set numbers to [10, 25, 5, 80, 15, 90, 3]

focus on numbers:
    discard where item < 10
    sort ascending
    take 3
"""
    res = execute(code)
    assert res["numbers"] == [10, 15, 25]


def test_inline_discourse_with_commas():
    code = """
set deals to [
    {client: "Acme Corp", amount: 45000, closed: true},
    {client: "Global Tech", amount: 120000, closed: true},
    {client: "Omni Industries", amount: 35000, closed: false},
    {client: "Vertex Systems", amount: 85000, closed: true},
    {client: "Nova Retail", amount: 60000, closed: true}
]

take deals, keep where closed, sort by amount descending, take 3 into top_3
"""
    res = execute(code)
    assert len(res["top_3"]) == 3
    assert res["top_3"][0]["client"] == "Global Tech"
    assert res["top_3"][1]["amount"] == 85000


def test_inline_discourse_with_then():
    code = """
set scores to [55, 92, 88, 40, 76, 95]

take scores then discard where item < 70 then sort descending then take top 3 into honor_roll
"""
    res = execute(code)
    assert res["honor_roll"] == [95, 92, 88]


def test_discourse_drop_and_take_last():
    code = """
set items to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

focus on items:
    drop first 3
    take last 4
"""
    res = execute(code)
    assert res["items"] == [7, 8, 9, 10]
