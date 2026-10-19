"""Unit and integration tests for the Databases and SQL domain pack (use db)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.db.spec import QuerySpec, WhereClause


def test_query_spec_validation_and_parameterized_sql():
    spec = QuerySpec(
        table="employees",
        columns=["name", "salary"],
        where=[
            WhereClause(column="salary", operator=">", value=100000),
            WhereClause(column="dept", operator="=", value="Engineering"),
        ],
        order_by="salary",
        order_descending=True,
        limit=10,
    )
    assert len(spec.validate()) == 0
    sql, params = spec.to_parameterized_sql()
    assert "SELECT name, salary FROM employees" in sql
    assert "WHERE salary > ? AND dept = ?" in sql
    assert "ORDER BY salary DESC" in sql
    assert "LIMIT 10" in sql
    assert params == [100000, "Engineering"]


def test_db_domain_execution_in_doomscript():
    source = """use db

employees = [
    {"name": "Alice", "salary": 120000, "dept": "Engineering"},
    {"name": "Bob", "salary": 80000, "dept": "Design"},
    {"name": "Charlie", "salary": 150000, "dept": "Engineering"},
    {"name": "Dave", "salary": 95000, "dept": "Marketing"}
]

query employees into senior_eng:
    select name, salary
    where salary is over 100000 and dept equals "Engineering"
    order by salary descending

inspect table employees into emp_schema
"""
    env = execute(source)
    assert "senior_eng" in env
    senior_eng = env["senior_eng"]
    assert len(senior_eng) == 2
    assert senior_eng[0]["name"] == "Charlie"
    assert senior_eng[0]["salary"] == 150000
    assert senior_eng[1]["name"] == "Alice"
    assert senior_eng[1]["salary"] == 120000

    assert "emp_schema" in env
    schema = env["emp_schema"]
    assert "name" in schema["column_names"]
    assert "salary" in schema["column_names"]


def test_db_raw_sql_and_insert():
    source = """use db

execute sql "CREATE TABLE logs (msg TEXT)"
insert into logs values [{"msg": "System ready"}, {"msg": "Task completed"}]
query logs into all_logs:
    select *
"""
    env = execute(source)
    assert "all_logs" in env
    assert len(env["all_logs"]) == 2
    assert env["all_logs"][0]["msg"] == "System ready"


def test_db_ast_export():
    source = """use db

query users into res:
    select name, age
    where age is over 18
"""
    py_code = export_to_python(source)
    assert "sqlite3" in py_code
    assert "res" in py_code
