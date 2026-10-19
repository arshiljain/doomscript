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
