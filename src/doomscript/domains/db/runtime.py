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


# --- Batch 11 Spoken English Database Verbs ---

def db_connect(path: Any) -> sqlite3.Connection:
    """Connect to SQLite database and register as active connection."""
    dest_path = str(path).strip("'\"")
    conn = sqlite3.connect(dest_path, autocommit=True)
    conn.row_factory = sqlite3.Row
    get_db_runtime()._conn = conn
    return conn

def _resolve_conn(db: Any = None) -> sqlite3.Connection:
    if isinstance(db, sqlite3.Connection):
        return db
    return get_db_runtime().get_connection()

def db_inspect_schema(target: Any = None, db: Any = None) -> Dict[str, Any]:
    """Inspect schema of database table or entire database."""
    conn = _resolve_conn(target if isinstance(target, sqlite3.Connection) else db)
    if isinstance(target, str):
        t_name = str(target).strip("'\"")
        cur = conn.execute(f'PRAGMA table_info("{t_name}")')
        cols = [dict(row) for row in cur.fetchall()]
        return {t_name: cols}
    else:
        # Inspect all tables in database
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] if isinstance(row, sqlite3.Row) else row[0] for row in cur.fetchall()]
        res = {}
        for t in tables:
            cur_t = conn.execute(f'PRAGMA table_info("{t}")')
            res[t] = [dict(row) for row in cur_t.fetchall()]
        return res


def db_upsert_record(record: Any, table_name: Any, conflict_col: Any, db: Any = None) -> bool:
    """Insert or update record into SQLite table on primary/unique key conflict."""
    t_name = str(table_name).strip("'\"")
    c_col = str(conflict_col).strip("'\"")
    conn = _resolve_conn(db)
    rec = dict(record)
    cols = list(rec.keys())
    if not cols:
        return False

    # Ensure table exists
    col_defs = [f'"{c}" TEXT' for c in cols]
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{t_name}" ({", ".join(col_defs)}, UNIQUE("{c_col}"))')

    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(f'"{c}"' for c in cols)
    update_pairs = ", ".join(f'"{c}" = excluded."{c}"' for c in cols if c != c_col)

    if update_pairs:
        sql = f'INSERT INTO "{t_name}" ({col_names}) VALUES ({placeholders}) ON CONFLICT("{c_col}") DO UPDATE SET {update_pairs}'
    else:
        sql = f'INSERT INTO "{t_name}" ({col_names}) VALUES ({placeholders}) ON CONFLICT("{c_col}") DO NOTHING'

    conn.execute(sql, [str(rec[c]) if rec[c] is not None else None for c in cols])
    return True


def db_optimize(db: Any = None) -> bool:
    """Optimize database storage and query planner indices (VACUUM & ANALYZE)."""
    conn = _resolve_conn(db)
    try:
        conn.execute("ANALYZE")
        conn.execute("VACUUM")
    except Exception:
        pass
    return True


def db_backup(db_or_path: Any, path: Any = None) -> str:
    """Backup active database to specified file destination."""
    if path is None:
        dest_path = str(db_or_path).strip("'\"")
        src_conn = get_db_runtime().get_connection()
    else:
        src_conn = _resolve_conn(db_or_path)
        dest_path = str(path).strip("'\"")
    dest_conn = sqlite3.connect(dest_path)
    src_conn.backup(dest_conn)
    dest_conn.close()
    return dest_path


def db_truncate_table(table_name: Any, db: Any = None) -> bool:
    """Remove all records from table."""
    t_name = str(table_name).strip("'\"")
    conn = _resolve_conn(db)
    conn.execute(f'DELETE FROM "{t_name}"')
    return True


def db_count_rows_where(table_name: Any, condition: Any = "1=1", db: Any = None) -> int:
    """Count records in table matching WHERE condition."""
    t_name = str(table_name).strip("'\"")
    cond_str = str(condition).strip("'\"")
    conn = _resolve_conn(db)
    try:
        cur = conn.execute(f'SELECT COUNT(*) FROM "{t_name}" WHERE {cond_str}')
        res = cur.fetchone()
        return int(res[0]) if res else 0
    except Exception:
        # Fallback if table does not exist yet
        return 0


# --- 350-Expansion 20 Database Operations ---

def db_create_index(conn: Any, table: Any, col: Any, index_name: Any = None) -> str:
    """Create index on table column."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    column = str(col).strip("'\"")
    idx = str(index_name).strip("'\"") if index_name else f"idx_{tbl}_{column}"
    c.execute(f'CREATE INDEX IF NOT EXISTS "{idx}" ON "{tbl}" ("{column}")')
    return idx


def db_drop_index(conn: Any, index_name: Any) -> bool:
    """Drop specified index."""
    c = _resolve_conn(conn)
    idx = str(index_name).strip("'\"")
    c.execute(f'DROP INDEX IF EXISTS "{idx}"')
    return True


def db_add_column(conn: Any, table: Any, col_name: Any, col_type: Any = "TEXT") -> bool:
    """Alter table to append new column."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    col = str(col_name).strip("'\"")
    ctype = str(col_type).strip("'\"").upper()
    c.execute(f'ALTER TABLE "{tbl}" ADD COLUMN "{col}" {ctype}')
    return True


def db_drop_column_sqlite(conn: Any, table: Any, col_name: Any) -> bool:
    """Safely drop column from table."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    col = str(col_name).strip("'\"")
    c.execute(f'ALTER TABLE "{tbl}" DROP COLUMN "{col}"')
    return True


def db_vacuum(conn: Any = None) -> bool:
    """Reclaim unused space and defragment database."""
    c = _resolve_conn(conn)
    c.execute("VACUUM")
    return True


def db_analyze(conn: Any = None) -> bool:
    """Collect optimizer statistics on tables and indices."""
    c = _resolve_conn(conn)
    c.execute("ANALYZE")
    return True


def db_list_tables(conn: Any = None) -> List[str]:
    """List all user tables in database."""
    c = _resolve_conn(conn)
    cur = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def db_list_views(conn: Any = None) -> List[str]:
    """List all views in database."""
    c = _resolve_conn(conn)
    cur = c.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def db_list_indices(conn: Any, table: Any = None) -> List[str]:
    """List index names attached to database or specific table."""
    c = _resolve_conn(conn)
    if table:
        tbl = str(table).strip("'\"")
        cur = c.execute(f'PRAGMA index_list("{tbl}")')
        return [r[1] for r in cur.fetchall()]
    cur = c.execute("SELECT name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


def db_table_exists(conn: Any, table: Any) -> bool:
    """Check if table exists in database."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    cur = c.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
    return cur.fetchone() is not None


def db_bulk_insert(conn: Any, table: Any, records: Any, chunk_size: Any = 1000) -> int:
    """Chunked parameterized bulk insert."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    recs = [dict(r) for r in records]
    if not recs:
        return 0
    cols = list(recs[0].keys())
    col_names = ", ".join(f'"{col}"' for col in cols)
    placeholders = ", ".join(["?"] * len(cols))
    sql = f'INSERT INTO "{tbl}" ({col_names}) VALUES ({placeholders})'
    batch_size = max(1, int(chunk_size))
    total = 0
    for i in range(0, len(recs), batch_size):
        chunk = recs[i:i + batch_size]
        vals = [[r.get(col) for col in cols] for r in chunk]
        c.executemany(sql, vals)
        total += len(chunk)
    return total


def db_export_table_to_csv(conn: Any, table: Any, csv_path: Any) -> str:
    """Stream table rows directly to CSV file."""
    import csv
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    path = str(csv_path).strip("'\"")
    cur = c.execute(f'SELECT * FROM "{tbl}"')
    cols = [d[0] for d in cur.description] if cur.description else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if cols:
            writer.writerow(cols)
        writer.writerows(cur.fetchall())
    return path


def db_import_csv_to_table(conn: Any, csv_path: Any, table: Any) -> int:
    """Import CSV file directly into SQLite table."""
    import csv
    c = _resolve_conn(conn)
    path = str(csv_path).strip("'\"")
    tbl = str(table).strip("'\"")
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return 0
        col_defs = ", ".join(f'"{h}" TEXT' for h in headers)
        c.execute(f'CREATE TABLE IF NOT EXISTS "{tbl}" ({col_defs})')
        placeholders = ", ".join(["?"] * len(headers))
        sql = f'INSERT INTO "{tbl}" ({", ".join(f"{h}" for h in headers)}) VALUES ({placeholders})'
        rows = list(reader)
        c.executemany(sql, rows)
        return len(rows)


def db_get_foreign_keys(conn: Any, table: Any) -> List[Dict[str, Any]]:
    """PRAGMA foreign key list inspector."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    cur = c.execute(f'PRAGMA foreign_key_list("{tbl}")')
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def db_check_foreign_key_integrity(conn: Any = None) -> List[Dict[str, Any]]:
    """Verify referential integrity constraints."""
    c = _resolve_conn(conn)
    cur = c.execute("PRAGMA foreign_key_check")
    cols = [d[0] for d in cur.description] if cur.description else ["table", "rowid", "parent", "fkid"]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def db_export_ddl(conn: Any, table: Any) -> str:
    """Export SQL CREATE TABLE DDL statement."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    cur = c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tbl,))
    row = cur.fetchone()
    return str(row[0]) if row and row[0] else ""


def db_table_column_types(conn: Any, table: Any) -> Dict[str, str]:
    """Column name to declared type mapping."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    cur = c.execute(f'PRAGMA table_info("{tbl}")')
    return {r[1]: r[2] for r in cur.fetchall()}


def db_database_size_bytes(conn: Any = None) -> int:
    """Total on-disk/allocated size of SQLite database in bytes."""
    c = _resolve_conn(conn)
    cur_pages = c.execute("PRAGMA page_count").fetchone()
    cur_size = c.execute("PRAGMA page_size").fetchone()
    pages = cur_pages[0] if cur_pages else 0
    size = cur_size[0] if cur_size else 4096
    return int(pages * size)


def db_count_distinct_values(conn: Any, table: Any, col: Any) -> int:
    """Count unique values in column."""
    c = _resolve_conn(conn)
    tbl = str(table).strip("'\"")
    column = str(col).strip("'\"")
    cur = c.execute(f'SELECT COUNT(DISTINCT "{column}") FROM "{tbl}"')
    res = cur.fetchone()
    return int(res[0]) if res else 0


def db_clone_table_schema(conn: Any, src_table: Any, new_table: Any) -> bool:
    """Clone structure of existing table without rows."""
    c = _resolve_conn(conn)
    src = str(src_table).strip("'\"")
    dst = str(new_table).strip("'\"")
    ddl = db_export_ddl(c, src)
    if not ddl:
        return False
    # Replace table name in DDL
    new_ddl = ddl.replace(f'"{src}"', f'"{dst}"', 1)
    if new_ddl == ddl:
        new_ddl = ddl.replace(f" {src} ", f' "{dst}" ', 1).replace(f" {src}(", f' "{dst}"(', 1)
    c.execute(new_ddl)
    return True


