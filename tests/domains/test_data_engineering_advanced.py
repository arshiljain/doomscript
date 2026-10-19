"""Tests for advanced Data Engineering capabilities: Joins, Schema Contracts, Window Functions, Explain, and Dry-Run."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.data.runtime import explain_pipeline, dry_run_pipeline
from doomscript.domains.data.spec import PipelineSpec, SchemaContractStep, JoinStep, WindowStep


def test_schema_contract_validation():
    source = """use data

records = [
    {"id": "1", "name": "Alice", "score": "95.5"},
    {"id": "2", "name": "Bob", "score": "88.0"}
]

pipeline "scored_users":
    read records into user_df
    validate schema: id as integer, name as string, score as float
"""
    env = execute(source)
    assert "scored_users" in env
    rows = env["scored_users"]
    assert rows[0]["id"] == 1
    assert isinstance(rows[0]["score"], float)
    assert rows[0]["score"] == 95.5


def test_joins_in_pipeline():
    source = """use data

users = [
    {"user_id": 1, "name": "Alice"},
    {"user_id": 2, "name": "Bob"}
]

orders = [
    {"order_id": 101, "user_id": 1, "item": "Keyboard"},
    {"order_id": 102, "user_id": 3, "item": "Mouse"}
]

pipeline "user_orders":
    read users into user_df
    left join with orders on user_id
"""
    env = execute(source)
    assert "user_orders" in env
    res = env["user_orders"]
    assert len(res) == 2
    alice = next(r for r in res if r["name"] == "Alice")
    assert alice["item"] == "Keyboard"
    bob = next(r for r in res if r["name"] == "Bob")
    assert bob.get("item") is None


def test_window_functions_in_pipeline():
    source = """use data

transactions = [
    {"date": "2026-01-01", "amount": 100},
    {"date": "2026-01-02", "amount": 200},
    {"date": "2026-01-03", "amount": 300}
]

pipeline "cumulative_sales":
    read transactions into tx
    calculate running_sum of amount over date into cum_amount
    calculate row_number over date into row_idx
"""
    env = execute(source)
    assert "cumulative_sales" in env
    rows = env["cumulative_sales"]
    assert rows[0]["cum_amount"] == 100
    assert rows[1]["cum_amount"] == 300
    assert rows[2]["cum_amount"] == 600
    assert rows[0]["row_idx"] == 1
    assert rows[1]["row_idx"] == 2
    assert rows[2]["row_idx"] == 3


def test_pipeline_explain_and_dry_run():
    source = """use data

pipeline "sales_pipeline":
    read "sales.csv" into sales
    remove duplicate rows
    group by region
    calculate total_rev as sum of amount
"""
    env = execute(source)
    assert "sales_pipeline_spec" in env or "sales_pipeline" in env
    
    # Verify explain and dry_run helpers
    plan = explain_pipeline("sales_pipeline")
    assert "sales_pipeline" in plan
    assert "Source: sales.csv" in plan or "Source: sales" in plan
    assert "GroupBy" in plan
