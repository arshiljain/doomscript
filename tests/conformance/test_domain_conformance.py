"""Domain conformance suite testing semantic parity between interpreter and exported Python."""

import pytest
from doomscript.testing.conformance import assert_execution_and_export_parity


def test_core_language_conformance():
    source = """
x = 10
y = 25
total = x + y
ratio = y / x
is_valid = total > 30 and ratio == 2.5
items = [1, 2, 3]
items_doubled = [n * 2 for n in items]
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["x", "y", "total", "ratio", "is_valid", "items", "items_doubled"],
    )


def test_data_pipeline_conformance():
    source = """use data

records = [
    {"dept": "Engineering", "salary": 120000},
    {"dept": "Engineering", "salary": 140000},
    {"dept": "Design", "salary": 95000}
]

pipeline "dept_salaries":
    read records into dept_df
    group dept_df by dept
    calculate total_payroll as sum of salary
    calculate head_count as count
"""
    env_direct, env_export = assert_execution_and_export_parity(
        source,
        expected_vars=["dept_salaries"],
    )
    assert len(env_direct["dept_salaries"]) == 2
    assert len(env_export["dept_salaries"]) == 2


def test_dsa_conformance():
    source = """use dsa

to double_val with n:
    return n * 2

val = double_val(21)
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["val"],
    )


def test_advanced_pipeline_conformance():
    source = """use data

users = [
    {"user_id": 1, "name": "Alice"},
    {"user_id": 2, "name": "Bob"}
]

orders = [
    {"order_id": 101, "user_id": 1, "amount": 150},
    {"order_id": 102, "user_id": 2, "amount": 250}
]

pipeline "user_orders_pipe":
    read users into user_df
    join with orders on user_id
    calculate running_sum of amount over order_id into cum_amount
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["user_orders_pipe"],
    )


def test_nlp_conformance():
    source = """use nlp

doc = "DoomScript domain architecture"
clean text in doc into c
tokenize c into words
extract 2-grams from c into bigrams
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["c", "words", "bigrams"],
    )


def test_geo_conformance():
    source = """use geo

point at 10.0, 20.0 into p1
point at 15.0, 25.0 into p2
distance between p1 and p2 in km into d
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["p1", "p2", "d"],
    )


def test_agent_conformance():
    source = """use agent

create agent Bot with role "Helper" into b
tell agent b "Keep responses brief"
memory of agent b into m
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["m"],
    )


def test_image_conformance():
    source = """use image

create blank image with width 200, height 100, color "white" into img
dimensions of img into dims
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["dims"],
    )


def test_web_conformance():
    source = """use web

parse html "<html><title>Doom</title><body><a href='http://test.com'>Go</a></body></html>" into p
title of p into t
extract all links from p into l
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["t", "l"],
    )


def test_audio_conformance():
    source = """use audio

create blank audio with duration 1.0 into clip
trim clip from 0.2 to 0.8 into part
duration of part into d
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["d"],
    )


def test_finance_conformance():
    source = """use finance

quotes = [100.0, 102.0, 101.0, 105.0, 107.0, 110.0]
calculate 3 day moving average of quotes into sma
calculate daily returns of quotes into rets
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["sma", "rets"],
    )


def test_graph_conformance():
    source = """use graph

create graph into g
connect "A" to "B" with weight 1.0 in g
connect "B" to "C" with weight 2.0 in g
shortest path from "A" to "C" in g into sp
degrees of nodes in g into degs
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["sp", "degs"],
    )


def test_office_conformance():
    source = """use office

create spreadsheet into s
add row ["Item", "Count"] to s
add row ["Apples", 42] to s
num_rows = count of s.rows
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["num_rows"],
    )


def test_cloud_conformance():
    source = """use cloud

connect to bucket "conformance-store" into b
generate signed url for "data.csv" in b into link
"""
    assert_execution_and_export_parity(
        source,
        expected_vars=["link"],
    )

