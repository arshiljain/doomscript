"""Databases and SQL Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.db.spec import QuerySpec, WhereClause
from doomscript.domains.db.parser import DBDomainParser
from doomscript.domains.db.runtime import (
    DBRuntime,
    get_db_runtime,
    execute_parameterized_query,
    inspect_table_schema,
    execute_raw_sql,
    db_transaction,
)
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.db.exporter import DBASTExporter
from doomscript.domains.registry import get_domain_registry


class DBDomain(DomainContract):
    """Databases and SQL domain pack providing queries, schema reflection, and safe SQL execution."""

    name = "db"
    aliases = ["sql", "database"]
    description = "Relational database operations, SQL execution, schema reflection, and parameterized queries"
    parser = DBDomainParser()
    runtime = get_db_runtime()
    exporter = DBASTExporter()
    capabilities = ["query", "sql", "schema", "insert", "transactions"]
    optional_dependencies = ["sqlite3", "sqlalchemy"]

    verbs = [
        VerbSpec(
            name="query_table",
            pattern="query {table:ident} [where {cond:expr}] into {target:ident}",
            arg_schema={"table": "ident", "cond": "expr", "target": "ident"},
            returns="Table",
            description="Select records from database table with optional filter",
        ),
        VerbSpec(
            name="inspect_table",
            pattern="inspect table {table:ident} [into {target:ident}]",
            arg_schema={"table": "ident", "target": "ident"},
            returns="Record",
            description="Inspect schema, columns, and foreign keys of a database table",
        ),
        VerbSpec(
            name="execute_sql",
            pattern="execute sql {query:expr} [into {target:ident}]",
            arg_schema={"query": "expr", "target": "ident"},
            returns="Any",
            description="Execute parameterized raw SQL statement",
        ),
        VerbSpec(
            name="insert_into",
            pattern="insert into {table:ident} values {values:expr}",
            arg_schema={"table": "ident", "values": "expr"},
            returns="None",
            description="Insert new row or records into database table",
        ),
        VerbSpec(
            name="count_rows",
            pattern="count rows in {table:ident} [into {target:ident}]",
            arg_schema={"table": "ident", "target": "ident"},
            returns="int",
            description="Count total rows matching in database table",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        return (
            s.startswith("inspect table ")
            or s.startswith("schema of ")
            or s.startswith("execute sql ")
            or s.startswith("insert into ")
            or s.startswith("query db ")
            or s.startswith("query sql ")
            or s.startswith("find rows in ")
            or s.startswith("find all rows in ")
            or s.startswith("count rows in ")
            or (s.startswith("query ") and (" where " in s or " into " in s))
        )

    def can_handle_block(self, header: str) -> bool:
        s = header.strip().lower()
        return s.startswith("query ") and (" into " in s or s.endswith(":"))


# Register with central registry
DB_DOMAIN = DBDomain()
get_domain_registry().register(DB_DOMAIN)

__all__ = [
    "DBDomain",
    "DB_DOMAIN",
    "QuerySpec",
    "WhereClause",
    "DBDomainParser",
    "DBRuntime",
    "DBASTExporter",
    "get_db_runtime",
    "execute_parameterized_query",
    "inspect_table_schema",
    "execute_raw_sql",
    "db_transaction",
]
