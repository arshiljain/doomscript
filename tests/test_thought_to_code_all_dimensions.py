import pytest
from doomscript.compiler.engine import execute


def test_dimension_1_declarative_aggregations():
    code = """
set deals to [
    {client: "Acme", amount: 45000, closed: true},
    {client: "Global", amount: 120000, closed: true},
    {client: "Omni", amount: 35000, closed: false}
]

set total_all to sum of amount in deals
set total_closed to sum of amount in deals where closed
set closed_count to count of deals where closed
set max_deal to highest of amount in deals
set min_deal to lowest of amount in deals
"""
    result = execute(code)
    assert result["total_all"] == 200000
    assert result["total_closed"] == 165000
    assert result["closed_count"] == 2
    assert result["max_deal"] == 120000
    assert result["min_deal"] == 35000


def test_dimension_2_natural_proportions_and_percentages():
    code = """
set original_price to 200.0
set discounted to 25% off original_price
set tax to 8% of original_price
set half_val to half of original_price
set quarter_val to quarter of original_price
set with_tip to 15% on original_price
set ratio to 25 as percent of 100
"""
    result = execute(code)
    assert result["discounted"] == 150.0
    assert result["tax"] == 16.0
    assert result["half_val"] == 100.0
    assert result["quarter_val"] == 50.0
    assert result["with_tip"] == pytest.approx(230.0)
    assert result["ratio"] == pytest.approx(25.0)


def test_dimension_3_bulk_actions_and_collective_verbs():
    code = """
set inventory to ["Torch", "Rusty Dagger"]
set loot to ["Potion", "Gold Key"]

add all of loot to inventory
set count_after_add to count of inventory

set unwanted to ["Rusty Dagger", "Potion"]
remove all of unwanted from inventory
set count_after_remove to count of inventory

clear inventory
set count_after_clear to count of inventory
"""
    result = execute(code)
    assert result["count_after_add"] == 4
    assert result["count_after_remove"] == 2
    assert result["count_after_clear"] == 0
    assert result["inventory"] == []


def test_dimension_4_parallel_paired_and_indexed_iteration():
    code = """
set names to ["Alice", "Bob"]
set scores to [95, 88]

set paired_out to []
for each name, score in pairs of names and scores:
    add name + ":" + score to paired_out

set indexed_out to []
for each item with index in names:
    add index + "." + item to indexed_out

set zero_indexed_out to []
for each item with 0-based index in names:
    add index + "." + item to zero_indexed_out
"""
    result = execute(code)
    assert result["paired_out"] == ["Alice:95", "Bob:88"]
    assert result["indexed_out"] == ["1.Alice", "2.Bob"]
    assert result["zero_indexed_out"] == ["0.Alice", "1.Bob"]


def test_dimension_5_inline_formatting_modifiers():
    code = """
set salary to 8500.5
set rate to 82.34
set items to ["Apple", "Banana", "Cherry"]

set str_usd to "{salary as USD}"
set str_pct to "{rate as percentage}"
set str_list to "{items joined with ', '}"
set str_cnt to "{count of items}"
"""
    result = execute(code)
    assert result["str_usd"] == "$8,500.50"
    assert result["str_pct"] == "82.3%"
    assert result["str_list"] == "Apple, Banana, Cherry"
    assert result["str_cnt"] == "3"


def test_dimension_6_boolean_property_ergonomics():
    code = """
set deal1 to {title: "Enterprise", closed: true}
set deal2 to {title: "Startup", closed: false}

set is_d1_closed to false
if deal1 is closed:
    set is_d1_closed to true

set is_d2_not_closed to false
if deal2 is not closed:
    set is_d2_not_closed to true

set d2_unless_closed to false
unless deal2 is closed:
    set d2_unless_closed to true
"""
    result = execute(code)
    assert result["is_d1_closed"] is True
    assert result["is_d2_not_closed"] is True
    assert result["d2_unless_closed"] is True
