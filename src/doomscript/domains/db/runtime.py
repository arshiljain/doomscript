"""Runtime execution engine for Databases and SQL operations."""

import contextlib
import sqlite3
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.db.spec import QuerySpec, WhereClause
from doomscript.domains.data.runtime import _to_record_list


class DBRuntime(DomainRuntime):
    """Runtime engine executing QuerySpec and SQL commands."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, autocommit=True)
        self._conn.row_factory = sqlite3.Row

    @contextlib.contextmanager
    def transaction(self):
        """Context-managed atomic transaction block."""
        self._conn.execute("BEGIN TRANSACTION")
        try:
            yield self._conn
            self._conn.execute("COMMIT")
        except Exception:
            self._conn.execute("ROLLBACK")
            raise

    def get_connection(self) -> sqlite3.Connection:
        return self._conn

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not isinstance(ir, QuerySpec):
            raise TypeError(f"DBRuntime expects QuerySpec, got {type(ir).__name__}")
        return self.execute_query_spec(ir, scope)

    def _sync_in_memory_dataset_if_present(self, table_name: str, scope: Dict[str, Any]) -> None:
        """If table_name exists in scope as a list of dicts/records, mirrors it to SQLite table."""
        if table_name in scope and isinstance(scope[table_name], list):
            rows = _to_record_list(scope[table_name])
            if not rows:
                return

            cols = list(rows[0].keys())
            col_defs = []
            for c in cols:
                sample_val = rows[0].get(c)
                if isinstance(sample_val, int):
                    col_defs.append(f'"{c}" INTEGER')
                elif isinstance(sample_val, float):
                    col_defs.append(f'"{c}" REAL')
                else:
                    col_defs.append(f'"{c}" TEXT')

            create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
            self._conn.execute(create_sql)

            # Check if table already has rows; if not, populate
            cur = self._conn.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            if cur.fetchone()[0] == 0:
                placeholders = ", ".join(["?"] * len(cols))
                insert_sql = f'INSERT INTO "{table_name}" ({", ".join(cols)}) VALUES ({placeholders})'
                val_tuples = [tuple(r.get(c) for c in cols) for r in rows]
                self._conn.executemany(insert_sql, val_tuples)

    def execute_query_spec(self, spec: QuerySpec, scope: Dict[str, Any]) -> List[Dict[str, Any]]:
        self._sync_in_memory_dataset_if_present(spec.table, scope)
        sql, params = spec.to_parameterized_sql()
        cursor = self._conn.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        if spec.target_var:
            scope[spec.target_var] = results
        return results

    def inspect_table_schema(self, table_name: str, scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if scope:
            self._sync_in_memory_dataset_if_present(table_name, scope)
        cursor = self._conn.execute(f"PRAGMA table_info('{table_name}')")
        rows = cursor.fetchall()
        columns = [
            {"cid": r[0], "name": r[1], "type": r[2], "notnull": bool(r[3]), "pk": bool(r[5])}
            for r in rows
        ]
        return {
            "table": table_name,
            "columns": columns,
            "column_names": [c["name"] for c in columns],
        }

    def execute_raw_sql(
        self, sql: str, params: Optional[List[Any]] = None, scope: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        cursor = self._conn.execute(sql, params or [])
        try:
            return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

    def insert_rows(
        self, table_name: str, data: Any, scope: Optional[Dict[str, Any]] = None
    ) -> int:
        rows = _to_record_list(data)
        if not rows:
            return 0
        cols = list(rows[0].keys())
        col_defs = []
        for c in cols:
            sample_val = rows[0].get(c)
            if isinstance(sample_val, int):
                col_defs.append(f'"{c}" INTEGER')
            elif isinstance(sample_val, float):
                col_defs.append(f'"{c}" REAL')
            else:
                col_defs.append(f'"{c}" TEXT')

        create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
        self._conn.execute(create_sql)
        placeholders = ", ".join(["?"] * len(cols))
        insert_sql = f'INSERT INTO "{table_name}" ({", ".join(cols)}) VALUES ({placeholders})'
        val_tuples = [tuple(r.get(c) for c in cols) for r in rows]
        self._conn.executemany(insert_sql, val_tuples)
        return len(rows)


# Process-wide DB runtime singleton
_GLOBAL_DB_RUNTIME = DBRuntime()


def get_db_runtime() -> DBRuntime:
    return _GLOBAL_DB_RUNTIME


def execute_parameterized_query(
    spec_or_id: Any, scope: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    if isinstance(spec_or_id, str):
        from doomscript.domains.registry import get_domain_registry
        spec = get_domain_registry().get_spec(spec_or_id)
    else:
        spec = spec_or_id
    return get_db_runtime().execute_query_spec(spec, scope)


def inspect_table_schema(
    table_name: str, scope: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    return get_db_runtime().inspect_table_schema(table_name, scope)


def execute_raw_sql(
    sql: str, params: Optional[List[Any]] = None, scope: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    if scope is None:
        import sys
        caller_frame = sys._getframe(1)
        scope = dict(caller_frame.f_globals)
        scope.update(caller_frame.f_locals)
    return get_db_runtime().execute_raw_sql(sql, params, scope)


def db_transaction():
    """Context manager for DB transactions."""
    return get_db_runtime().transaction()
