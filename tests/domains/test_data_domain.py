"""Unit and integration tests for the Data Engineering domain pack (use data)."""

import os
import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.data.spec import PipelineSpec, ValidationRule, DedupeStep, DeriveStep, GroupByStep, SortStep
from doomscript.domains.data.runtime import DataPipelineRuntime


def test_pipeline_spec_validation():
    spec = PipelineSpec(name="test_pipe", source="orders", target="clean_orders")
    spec.validations.append(ValidationRule(rule_type="not_null", column="order_id"))
    spec.steps.append(DedupeStep(by_columns=["order_id"]))
    spec.steps.append(DeriveStep(target_col="total", expression="price * qty"))
    
    errors = spec.validate()
    assert len(errors) == 0


def test_data_pipeline_execution_in_doomscript():
    source = """use data

raw_sales = [
    {"order_id": 1, "region": "North", "amount": 100, "discount": 0.1},
    {"order_id": 2, "region": "South", "amount": 200, "discount": 0.0},
    {"order_id": 1, "region": "North", "amount": 100, "discount": 0.1},
    {"order_id": 3, "region": "North", "amount": 150, "discount": 0.2}
]

pipeline "process_sales" from raw_sales into region_summary:
    validate:
        require "region" is text
        require "amount" is positive number
        forbid nulls in "order_id"

    remove duplicate rows by "order_id"
    derive "net_amount" as amount * (1.0 - discount)

    group by region:
        calculate total_revenue as sum of net_amount
        calculate order_count as count

    sort by total_revenue descending
"""
    env = execute(source)
    assert "region_summary" in env
    summary = env["region_summary"]
    assert len(summary) == 2
    # Verify North and South aggregated correctly
    by_region = {r["region"]: r for r in summary}
    assert "North" in by_region
    assert "South" in by_region
    assert by_region["North"]["order_count"] == 2
    assert by_region["South"]["order_count"] == 1
    assert by_region["North"]["total_revenue"] == (100 * 0.9) + (150 * 0.8)


def test_level1_and_level2_operations():
    source = """use data

users = [
    {"id": 1, "name": "Alice", "city": "NYC"},
    {"id": 2, "name": "Bob", "city": None},
    {"id": 3, "name": "Charlie", "city": "LA"}
]

clean users by removing nulls in "city" into clean_users
inspect dataset clean_users into user_profile
"""
    env = execute(source)
    assert len(env["clean_users"]) == 2
    assert env["user_profile"]["row_count"] == 2
    assert "city" in env["user_profile"]["columns"]


def test_data_pipeline_ast_export():
    source = """use data

orders = [{"id": 1, "amt": 50}]
pipeline "p" from orders into res:
    remove duplicate rows by "id"
    derive "amt_tax" as amt * 1.1
"""
    py_code = export_to_python(source)
    assert "pandas" in py_code or "drop_duplicates" in py_code or "for row in" in py_code
    assert "res" in py_code
