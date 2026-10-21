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
    db_connect,
    db_inspect_schema,
    db_upsert_record,
    db_optimize,
    db_backup,
    db_truncate_table,
    db_count_rows_where,
    db_create_index,
    db_drop_index,
    db_add_column,
    db_drop_column_sqlite,
    db_vacuum,
    db_analyze,
    db_list_tables,
    db_list_views,
    db_list_indices,
    db_table_exists,
    db_bulk_insert,
    db_export_table_to_csv,
    db_import_csv_to_table,
    db_get_foreign_keys,
    db_check_foreign_key_integrity,
    db_export_ddl,
    db_table_column_types,
    db_database_size_bytes,
    db_count_distinct_values,
    db_clone_table_schema,
    SQLQueryBuilder,
    InMemoryRelationalDB,
    MigrationManager,
    WALCrashRecovery,
    CostBasedQueryOptimizer,
    SnapshotIsolationMVCC,
    BPlusTreeIndex,
    db_bplus_tree_create,
    db_bplus_tree_insert,
    db_bplus_tree_search,
    db_bplus_tree_range,
    BitmapIndexCompressor,
    LSMTreeCompactionEngine,
    db_bitmap_compress,
    db_bitmap_decompress,
    db_bitmap_and,
    db_bitmap_or,
    db_bitmap_not,
    db_bitmap_query_indices,
    db_lsm_create,
    db_lsm_put,
    db_lsm_get,
    db_lsm_delete,
    db_lsm_flush,
    db_lsm_compact,
    BTreeStorageEnginePure,
    CostBasedQueryOptimizerCBO,
    db_btree_index_benchmark,
    db_cost_based_join_optimizer,
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
        if self.parser.parse_inspect(line, 0) is not None or self.parser.parse_operation(line, 0) is not None:
            return True
        s = line.strip().lower()
        return (
            s.startswith("inspect table ")
            or s.startswith("schema of ")
            or s.startswith("execute sql ")
            or s.startswith("insert into ")
            or s.startswith("query db ")
            or s.startswith("query sql ")
            or s.startswith("find rows in ")
            or (s.startswith("find all ") and " in " in s)
            or s.startswith("find all rows in ")
            or s.startswith("count rows in ")
            or (s.startswith("query ") and (" where " in s or " into " in s))
            or s.startswith("upsert record ")
            or s.startswith("optimize database")
            or s.startswith("backup database")
            or s.startswith("truncate table ")
            or s.startswith("inspect schema of ")
            or s.startswith("create wal ")
            or s.startswith("create mvcc ")
            or super().can_handle_line(line)
            or s.startswith("inspect database schema ")
            or s.startswith("connect to sqlite ")
            or s.startswith("connect to database ")
            or s.startswith("create index ")
            or s.startswith("drop index ")
            or s.startswith("add column ")
            or s.startswith("drop column ")
            or s.startswith("vacuum database")
            or s.startswith("analyze database")
            or s.startswith("list tables")
            or s.startswith("list views")
            or s.startswith("list indices")
            or s.startswith("table ")
            or s.startswith("check if table ")
            or s.startswith("bulk insert ")
            or s.startswith("export table ")
            or s.startswith("import csv ")
            or s.startswith("get foreign keys ")
            or s.startswith("check foreign key ")
            or s.startswith("export ddl ")
            or s.startswith("column types ")
            or s.startswith("database size ")
            or s.startswith("get database size ")
            or s.startswith("count distinct ")
            or s.startswith("clone schema ")
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
    "db_connect",
    "db_inspect_schema",
    "db_upsert_record",
    "db_optimize",
    "db_backup",
    "db_truncate_table",
    "db_count_rows_where",
    "db_create_index",
    "db_drop_index",
    "db_add_column",
    "db_drop_column_sqlite",
    "db_vacuum",
    "db_analyze",
    "db_list_tables",
    "db_list_views",
    "db_list_indices",
    "db_table_exists",
    "db_bulk_insert",
    "db_export_table_to_csv",
    "db_import_csv_to_table",
    "db_get_foreign_keys",
    "db_check_foreign_key_integrity",
    "db_export_ddl",
    "db_table_column_types",
    "db_database_size_bytes",
    "db_count_distinct_values",
    "db_clone_table_schema",
    "SQLQueryBuilder",
    "InMemoryRelationalDB",
    "MigrationManager",
    "WALCrashRecovery",
    "CostBasedQueryOptimizer",
    "SnapshotIsolationMVCC",
    "BPlusTreeIndex",
    "db_bplus_tree_create",
    "db_bplus_tree_insert",
    "db_bplus_tree_search",
    "db_bplus_tree_range",
    "BitmapIndexCompressor",
    "LSMTreeCompactionEngine",
    "db_bitmap_compress",
    "db_bitmap_decompress",
    "db_bitmap_and",
    "db_bitmap_or",
    "db_bitmap_not",
    "db_bitmap_query_indices",
    "db_lsm_create",
    "db_lsm_put",
    "db_lsm_get",
    "db_lsm_delete",
    "db_lsm_flush",
    "db_lsm_compact",
    "BTreeStorageEnginePure",
    "CostBasedQueryOptimizerCBO",
    "db_btree_index_benchmark",
    "db_cost_based_join_optimizer",
]
