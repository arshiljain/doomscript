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

