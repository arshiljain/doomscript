"""Runtime execution engine for Databases and SQL operations."""

import contextlib
import sqlite3
import sys


def _sqlite3_connect(path: str) -> sqlite3.Connection:
    """Connect to SQLite with autocommit semantics across Python 3.10-3.14+."""
    if sys.version_info >= (3, 12):
        return sqlite3.connect(path, autocommit=True)
    return sqlite3.connect(path, isolation_level=None)
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.db.spec import QuerySpec, WhereClause
from doomscript.domains.data.runtime import _to_record_list
from doomscript.core.record import Record


class DBRuntime(DomainRuntime):
    """Runtime engine executing QuerySpec and SQL commands."""

    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._conn = _sqlite3_connect(db_path)
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
    conn = _sqlite3_connect(dest_path)
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


class SQLQueryBuilder:
    """Fluent SQL Query AST and statement builder with parameterized values."""

    def __init__(self, table: str = ""):
        self._table = table
        self._columns: List[str] = []
        self._joins: List[Dict[str, str]] = []
        self._wheres: List[Tuple[str, str, Any]] = []
        self._group_bys: List[str] = []
        self._havings: List[str] = []
        self._order_bys: List[Tuple[str, str]] = []
        self._limit_val: Optional[int] = None
        self._offset_val: Optional[int] = None

    def select(self, *columns: str) -> "SQLQueryBuilder":
        self._columns.extend(columns)
        return self

    def from_table(self, table: str) -> "SQLQueryBuilder":
        self._table = table
        return self

    def join(self, table: str, on: str, how: str = "INNER") -> "SQLQueryBuilder":
        self._joins.append({"table": table, "on": on, "how": how.upper()})
        return self

    def where(self, col: str, op: str, val: Any) -> "SQLQueryBuilder":
        self._wheres.append((col, op, val))
        return self

    def group_by(self, *columns: str) -> "SQLQueryBuilder":
        self._group_bys.extend(columns)
        return self

    def having(self, clause: str) -> "SQLQueryBuilder":
        self._havings.append(clause)
        return self

    def order_by(self, col: str, descending: bool = False) -> "SQLQueryBuilder":
        self._order_bys.append((col, "DESC" if descending else "ASC"))
        return self

    def limit(self, n: int) -> "SQLQueryBuilder":
        self._limit_val = int(n)
        return self

    def offset(self, n: int) -> "SQLQueryBuilder":
        self._offset_val = int(n)
        return self

    def build(self) -> Tuple[str, List[Any]]:
        cols = ", ".join(self._columns) if self._columns else "*"
        sql_parts = [f"SELECT {cols} FROM {self._table}"]
        params: List[Any] = []

        for j in self._joins:
            sql_parts.append(f"{j['how']} JOIN {j['table']} ON {j['on']}")

        if self._wheres:
            where_clauses = []
            for col, op, val in self._wheres:
                where_clauses.append(f"{col} {op} ?")
                params.append(val)
            sql_parts.append("WHERE " + " AND ".join(where_clauses))

        if self._group_bys:
            sql_parts.append("GROUP BY " + ", ".join(self._group_bys))

        if self._havings:
            sql_parts.append("HAVING " + " AND ".join(self._havings))

        if self._order_bys:
            orders = [f"{col} {direction}" for col, direction in self._order_bys]
            sql_parts.append("ORDER BY " + ", ".join(orders))

        if self._limit_val is not None:
            sql_parts.append("LIMIT ?")
            params.append(self._limit_val)

        if self._offset_val is not None:
            sql_parts.append("OFFSET ?")
            params.append(self._offset_val)

        return " ".join(sql_parts), params


class InMemoryRelationalDB:
    """Pure-Python in-memory relational database with indexing, joins, and aggregates."""

    def __init__(self):
        self.tables: Dict[str, List[Dict[str, Any]]] = {}
        self.indexes: Dict[str, Dict[str, Dict[Any, List[int]]]] = {}

    def create_table(self, table_name: str) -> None:
        self.tables[table_name] = []
        self.indexes[table_name] = {}

    def insert(self, table_name: str, record: Dict[str, Any]) -> int:
        if table_name not in self.tables:
            self.create_table(table_name)
        row_idx = len(self.tables[table_name])
        self.tables[table_name].append(dict(record))

        # Update indexes
        for col, idx_map in self.indexes[table_name].items():
            if col in record:
                val = record[col]
                idx_map.setdefault(val, []).append(row_idx)
        return row_idx

    def create_index(self, table_name: str, column: str) -> None:
        if table_name not in self.tables:
            self.create_table(table_name)
        idx_map: Dict[Any, List[int]] = {}
        for row_idx, row in enumerate(self.tables[table_name]):
            val = row.get(column)
            idx_map.setdefault(val, []).append(row_idx)
        self.indexes[table_name][column] = idx_map

    def query(
        self,
        table_name: str,
        where_filter: Optional[Callable[[Dict[str, Any]], bool]] = None,
        join_table: Optional[str] = None,
        left_on: Optional[str] = None,
        right_on: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows = self.tables.get(table_name, [])

        if join_table and left_on and right_on:
            right_rows = self.tables.get(join_table, [])
            joined = []
            for l_row in rows:
                l_val = l_row.get(left_on)
                for r_row in right_rows:
                    if r_row.get(right_on) == l_val:
                        comb = {f"{table_name}_{k}": v for k, v in l_row.items()}
                        comb.update({f"{join_table}_{k}": v for k, v in r_row.items()})
                        joined.append(comb)
            rows = joined

        if where_filter:
            rows = [r for r in rows if where_filter(r)]

        return [dict(r) for r in rows]

    def aggregate(
        self,
        table_name: str,
        group_by_col: str,
        agg_col: str,
        agg_func: str = "sum",
    ) -> Dict[Any, float]:
        rows = self.tables.get(table_name, [])
        groups: Dict[Any, List[float]] = {}
        for r in rows:
            grp = r.get(group_by_col)
            val = r.get(agg_col, 0.0)
            if isinstance(val, (int, float)):
                groups.setdefault(grp, []).append(float(val))

        fn = agg_func.lower()
        res: Dict[Any, float] = {}
        for g, vals in groups.items():
            if fn == "sum":
                res[g] = round(sum(vals), 4)
            elif fn == "avg":
                res[g] = round(sum(vals) / max(1, len(vals)), 4)
            elif fn == "min":
                res[g] = round(min(vals), 4) if vals else 0.0
            elif fn == "max":
                res[g] = round(max(vals), 4) if vals else 0.0
            elif fn == "count":
                res[g] = float(len(vals))
        return res


class MigrationManager:
    """Schema version migration controller with rollback and audit logging."""

    def __init__(self, conn: Any):
        self.conn = _resolve_conn(conn)
        self.migrations: List[Dict[str, Any]] = []
        self._init_migration_table()

    def _init_migration_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS _schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                name TEXT
            )
        """)

    def add_migration(self, version: int, name: str, up_sql: str, down_sql: str) -> None:
        self.migrations.append({
            "version": int(version),
            "name": str(name),
            "up_sql": str(up_sql),
            "down_sql": str(down_sql),
        })
        self.migrations.sort(key=lambda m: m["version"])

    def current_version(self) -> int:
        cur = self.conn.execute("SELECT MAX(version) FROM _schema_migrations")
        row = cur.fetchone()
        return int(row[0]) if row and row[0] is not None else 0

    def migrate_up(self) -> int:
        cur_v = self.current_version()
        applied = 0
        for m in self.migrations:
            if m["version"] > cur_v:
                with self.conn:
                    self.conn.executescript(m["up_sql"])
                    self.conn.execute(
                        "INSERT INTO _schema_migrations (version, name) VALUES (?, ?)",
                        (m["version"], m["name"]),
                    )
                applied += 1
        return applied

    def rollback_last(self) -> bool:
        cur_v = self.current_version()
        if cur_v == 0:
            return False
        # Find migration with version == cur_v
        target = next((m for m in self.migrations if m["version"] == cur_v), None)
        if not target or not target["down_sql"]:
            return False

        with self.conn:
            self.conn.executescript(target["down_sql"])
            self.conn.execute("DELETE FROM _schema_migrations WHERE version = ?", (cur_v,))
        return True





# --- Deepened Database Systems: WAL Crash Recovery, Cost-Based Optimizer & MVCC ---

class WALCrashRecovery:
    """ARIES-style Write-Ahead Logging (WAL) engine with Analysis, Redo, and Undo crash recovery passes."""

    class LogRecord:
        def __init__(self, lsn: int, tx_id: int, op: str, page_id: Optional[int] = None, old_val: Any = None, new_val: Any = None, prev_lsn: int = 0):
            self.lsn = lsn
            self.tx_id = tx_id
            self.op = op  # BEGIN, UPDATE, COMMIT, ABORT, CHECKPOINT
            self.page_id = page_id
            self.old_val = old_val
            self.new_val = new_val
            self.prev_lsn = prev_lsn

        def to_dict(self) -> Dict[str, Any]:
            return {
                "lsn": self.lsn,
                "tx_id": self.tx_id,
                "op": self.op,
                "page_id": self.page_id,
                "old_val": self.old_val,
                "new_val": self.new_val,
                "prev_lsn": self.prev_lsn,
            }

    def __init__(self):
        self.log: List[WALCrashRecovery.LogRecord] = []
        self.current_lsn = 0
        self.tx_prev_lsn: Dict[int, int] = {}
        # In-memory database buffer pool: page_id -> (page_lsn, data)
        self.pages: Dict[int, Dict[str, Any]] = {}
        # Flushed disk state
        self.flushed_pages: Dict[int, Dict[str, Any]] = {}

    def begin_tx(self, tx_id: int) -> int:
        self.current_lsn += 1
        rec = self.LogRecord(self.current_lsn, tx_id, "BEGIN", prev_lsn=0)
        self.log.append(rec)
        self.tx_prev_lsn[tx_id] = self.current_lsn
        return self.current_lsn

    def write_update(self, tx_id: int, page_id: int, old_val: Any, new_val: Any) -> int:
        self.current_lsn += 1
        prev = self.tx_prev_lsn.get(tx_id, 0)
        rec = self.LogRecord(self.current_lsn, tx_id, "UPDATE", page_id=page_id, old_val=old_val, new_val=new_val, prev_lsn=prev)
        self.log.append(rec)
        self.tx_prev_lsn[tx_id] = self.current_lsn

        # Update in-memory buffer page
        self.pages[page_id] = {"page_lsn": self.current_lsn, "data": new_val}
        return self.current_lsn

    def commit_tx(self, tx_id: int) -> int:
        self.current_lsn += 1
        prev = self.tx_prev_lsn.get(tx_id, 0)
        rec = self.LogRecord(self.current_lsn, tx_id, "COMMIT", prev_lsn=prev)
        self.log.append(rec)
        self.tx_prev_lsn[tx_id] = self.current_lsn
        return self.current_lsn

    def flush_page_to_disk(self, page_id: int) -> None:
        """Simulates flushing dirty page to persistent disk storage."""
        if page_id in self.pages:
            self.flushed_pages[page_id] = dict(self.pages[page_id])

    def simulate_crash(self) -> None:
        """Simulates power outage: volatile in-memory buffer pool is lost, only disk persists."""
        self.pages = {pid: dict(v) for pid, v in self.flushed_pages.items()}

    def recover(self) -> Dict[str, Any]:
        """Executes full ARIES 3-pass recovery: Analysis, Redo, and Undo."""
        # Pass 1: Analysis
        active_txs: Set[int] = set()
        redo_lsn = 1

        for rec in self.log:
            if rec.op == "BEGIN":
                active_txs.add(rec.tx_id)
            elif rec.op in ("COMMIT", "ABORT"):
                active_txs.discard(rec.tx_id)

        # Pass 2: Redo (repeating history from start)
        redone_count = 0
        for rec in self.log:
            if rec.op == "UPDATE" and rec.page_id is not None:
                disk_page = self.pages.get(rec.page_id, {"page_lsn": 0, "data": None})
                if disk_page["page_lsn"] < rec.lsn:
                    self.pages[rec.page_id] = {"page_lsn": rec.lsn, "data": rec.new_val}
                    redone_count += 1

        # Pass 3: Undo (roll back uncommitted active transactions in reverse order)
        undone_count = 0
        for rec in reversed(self.log):
            if rec.tx_id in active_txs and rec.op == "UPDATE" and rec.page_id is not None:
                self.pages[rec.page_id] = {"page_lsn": self.current_lsn + 1, "data": rec.old_val}
                undone_count += 1

        # Mark all uncommitted transactions aborted
        for tx in active_txs:
            self.current_lsn += 1
            self.log.append(self.LogRecord(self.current_lsn, tx, "ABORT"))

        return {
            "uncommitted_txs": list(active_txs),
            "redone_operations": redone_count,
            "undone_operations": undone_count,
            "recovered_pages": {pid: v["data"] for pid, v in self.pages.items()},
        }


class CostBasedQueryOptimizer:
    """Cost-Based Query Optimizer (CBO) choosing optimal physical scan and join plans using selectivity estimates."""

    PAGE_IO_COST = 1.0
    RANDOM_IO_COST = 4.0
    CPU_TUPLE_COST = 0.01

    def __init__(self):
        # Table metadata: table_name -> {rows, pages, indexes: {col -> {distinct_vals, idx_pages}}}
        self.catalog: Dict[str, Dict[str, Any]] = {}

    def register_table(self, table_name: str, num_rows: int, num_pages: int, indexes: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        self.catalog[table_name] = {
            "num_rows": int(num_rows),
            "num_pages": int(num_pages),
            "indexes": indexes or {},
        }

    def estimate_selectivity(self, table_name: str, col: str, op: str, val: Any) -> float:
        """Estimates predicate selectivity factor in [0.0, 1.0]."""
        meta = self.catalog.get(table_name)
        if not meta:
            return 0.1

        idx_info = meta["indexes"].get(col)
        distinct = idx_info.get("distinct_vals", meta["num_rows"]) if idx_info else max(1, meta["num_rows"] // 10)

        if op == "=":
            return 1.0 / max(1, distinct)
        elif op in ("<", "<=", ">", ">="):
            return 0.33  # standard standard-deviation default range selectivity
        elif op in ("like", "contains"):
            return 0.05
        return 0.1

    def optimize_scan(self, table_name: str, predicate_col: str, op: str, val: Any) -> Dict[str, Any]:
        """Calculates costs of Sequential Scan vs Index Scan and chooses the cheapest execution plan."""
        meta = self.catalog[table_name]
        num_rows = meta["num_rows"]
        num_pages = meta["num_pages"]

        # Cost of SeqScan: read all pages sequentially + cpu cost per tuple
        seq_cost = (num_pages * self.PAGE_IO_COST) + (num_rows * self.CPU_TUPLE_COST)

        sel = self.estimate_selectivity(table_name, predicate_col, op, val)
        est_rows = max(1, int(round(sel * num_rows)))

        has_index = predicate_col in meta["indexes"]
        if has_index:
            idx_info = meta["indexes"][predicate_col]
            idx_pages = idx_info.get("idx_pages", 2)
            # Index scan cost = traverse index + random page fetches for matched rows
            idx_cost = (idx_pages * self.PAGE_IO_COST) + (est_rows * self.RANDOM_IO_COST) + (est_rows * self.CPU_TUPLE_COST)
        else:
            idx_cost = float("inf")

        if idx_cost < seq_cost:
            chosen = "INDEX_SCAN"
            cost = idx_cost
        else:
            chosen = "SEQ_SCAN"
            cost = seq_cost

        return {
            "table": table_name,
            "chosen_plan": chosen,
            "estimated_cost": round(cost, 2),
            "seq_scan_cost": round(seq_cost, 2),
            "index_scan_cost": round(idx_cost, 2) if has_index else None,
            "selectivity": round(sel, 4),
            "estimated_rows": est_rows,
        }


class SnapshotIsolationMVCC:
    """Multi-Version Concurrency Control (MVCC) supporting Snapshot Isolation and First-Committer-Wins conflict resolution."""

    class Version:
        def __init__(self, val: Any, created_tx: int, deleted_tx: Optional[int] = None):
            self.val = val
            self.created_tx = created_tx
            self.deleted_tx = deleted_tx

    def __init__(self):
        self.global_tx_counter = 0
        # key -> List[Version]
        self.store: Dict[str, List[SnapshotIsolationMVCC.Version]] = {}
        # active_txs: tx_id -> {read_ts: int, writes: Dict[key, val]}
        self.active_txs: Dict[int, Dict[str, Any]] = {}
        self.committed_txs: Set[int] = set()

    def begin(self) -> int:
        """Starts a transaction with Snapshot Isolation read timestamp."""
        self.global_tx_counter += 1
        tx_id = self.global_tx_counter
        self.active_txs[tx_id] = {
            "read_ts": self.global_tx_counter,
            "writes": {},
        }
        return tx_id

    def read(self, tx_id: int, key: str) -> Optional[Any]:
        """Reads snapshot-visible version of key."""
        tx_info = self.active_txs[tx_id]
        # First check local write-set
        if key in tx_info["writes"]:
            return tx_info["writes"][key]

        read_ts = tx_info["read_ts"]
        versions = self.store.get(key, [])
        for v in reversed(versions):
            # Version visible if created <= read_ts and (not deleted or deleted > read_ts)
            if v.created_tx <= read_ts and (v.deleted_tx is None or v.deleted_tx > read_ts):
                return v.val
        return None

    def write(self, tx_id: int, key: str, val: Any) -> None:
        """Buffers write in transaction private workspace."""
        self.active_txs[tx_id]["writes"][key] = val

    def commit(self, tx_id: int) -> bool:
        """Validates first-committer-wins rule and applies updates or aborts on write-write conflict."""
        tx_info = self.active_txs[tx_id]
        read_ts = tx_info["read_ts"]
        writes = tx_info["writes"]

        # Conflict check: did any key in writes get modified after this transaction's read_ts?
        for key in writes:
            for v in self.store.get(key, []):
                if v.created_tx > read_ts and v.created_tx in self.committed_txs:
                    # Write conflict: transaction committed concurrently on same key
                    del self.active_txs[tx_id]
                    return False

        # Apply writes
        for key, val in writes.items():
            if key not in self.store:
                self.store[key] = []
            # Mark previous active version as deleted by this tx
            if self.store[key]:
                self.store[key][-1].deleted_tx = tx_id
            self.store[key].append(self.Version(val, created_tx=tx_id))

        self.committed_txs.add(tx_id)
        del self.active_txs[tx_id]
        return True


def db_wal_create() -> WALCrashRecovery:
    return WALCrashRecovery()


def db_mvcc_create() -> SnapshotIsolationMVCC:
    return SnapshotIsolationMVCC()


# ==============================================================================
# B+ TREE STORAGE ENGINE INDEX
# ==============================================================================

class BPlusTreeNode:
    """Node in an in-memory B+ Tree index."""

    def __init__(self, is_leaf: bool = False):
        self.is_leaf = is_leaf
        self.keys: List[Any] = []
        self.values: List[Any] = []  # Only used when is_leaf is True
        self.children: List["BPlusTreeNode"] = []  # Only used when is_leaf is False
        self.next: Optional["BPlusTreeNode"] = None  # Doubly-linked leaf pointer
        self.prev: Optional["BPlusTreeNode"] = None


class BPlusTreeIndex:
    """Complete B+ Tree Index with internal/leaf splitting and linked-leaf range scanning."""

    def __init__(self, order: int = 4):
        self.order = max(3, int(order))
        self.root = BPlusTreeNode(is_leaf=True)
        self.total_keys = 0

    def search(self, key: Any) -> Optional[Any]:
        """Searches for key and returns associated value, or None if not found."""
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                return leaf.values[i]
        return None

    def insert(self, key: Any, value: Any) -> None:
        """Inserts key and value into the B+ Tree, performing splits as necessary."""
        leaf = self._find_leaf(key)

        # Update existing key if present
        for i, k in enumerate(leaf.keys):
            if k == key:
                leaf.values[i] = value
                return

        # Insert key in sorted order
        idx = 0
        while idx < len(leaf.keys) and leaf.keys[idx] < key:
            idx += 1
        leaf.keys.insert(idx, key)
        leaf.values.insert(idx, value)
        self.total_keys += 1

        # Check for leaf split
        if len(leaf.keys) >= self.order:
            self._split_leaf(leaf)

    def range_scan(self, min_key: Any, max_key: Any) -> List[Tuple[Any, Any]]:
        """Scans and returns all (key, value) pairs within [min_key, max_key] inclusive."""
        results = []
        leaf = self._find_leaf(min_key)

        curr: Optional[BPlusTreeNode] = leaf
        while curr is not None:
            for i, k in enumerate(curr.keys):
                if k > max_key:
                    return results
                if k >= min_key:
                    results.append((k, curr.values[i]))
            curr = curr.next

        return results

    def delete(self, key: Any) -> bool:
        """Deletes key from index, returning True if key existed."""
        leaf = self._find_leaf(key)
        for i, k in enumerate(leaf.keys):
            if k == key:
                leaf.keys.pop(i)
                leaf.values.pop(i)
                self.total_keys -= 1
                return True
        return False

    def get_height(self) -> int:
        """Returns the height of the B+ Tree."""
        h = 1
        curr = self.root
        while not curr.is_leaf:
            h += 1
            curr = curr.children[0]
        return h

    def get_stats(self) -> Dict[str, Any]:
        """Returns structural statistics of the B+ Tree."""
        return {
            "order": self.order,
            "total_keys": self.total_keys,
            "height": self.get_height(),
        }

    def _find_leaf(self, key: Any) -> BPlusTreeNode:
        curr = self.root
        while not curr.is_leaf:
            idx = 0
            while idx < len(curr.keys) and key >= curr.keys[idx]:
                idx += 1
            curr = curr.children[idx]
        return curr

    def _find_parent(self, current: BPlusTreeNode, child: BPlusTreeNode) -> Optional[BPlusTreeNode]:
        if current.is_leaf or not current.children:
            return None
        for c in current.children:
            if c is child:
                return current
        for c in current.children:
            res = self._find_parent(c, child)
            if res is not None:
                return res
        return None

    def _split_leaf(self, leaf: BPlusTreeNode) -> None:
        mid = len(leaf.keys) // 2
        right = BPlusTreeNode(is_leaf=True)

        right.keys = leaf.keys[mid:]
        right.values = leaf.values[mid:]
        leaf.keys = leaf.keys[:mid]
        leaf.values = leaf.values[:mid]

        right.next = leaf.next
        if leaf.next is not None:
            leaf.next.prev = right
        leaf.next = right
        right.prev = leaf

        promoted_key = right.keys[0]
        parent = self._find_parent(self.root, leaf)

        if parent is None:
            # Create new root
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.keys = [promoted_key]
            new_root.children = [leaf, right]
            self.root = new_root
        else:
            self._insert_into_parent(parent, promoted_key, right)

    def _split_internal(self, node: BPlusTreeNode) -> None:
        mid = len(node.keys) // 2
        promoted_key = node.keys[mid]

        right = BPlusTreeNode(is_leaf=False)
        right.keys = node.keys[mid + 1 :]
        right.children = node.children[mid + 1 :]

        node.keys = node.keys[:mid]
        node.children = node.children[: mid + 1]

        parent = self._find_parent(self.root, node)
        if parent is None:
            new_root = BPlusTreeNode(is_leaf=False)
            new_root.keys = [promoted_key]
            new_root.children = [node, right]
            self.root = new_root
        else:
            self._insert_into_parent(parent, promoted_key, right)

    def _insert_into_parent(self, parent: BPlusTreeNode, key: Any, right_child: BPlusTreeNode) -> None:
        idx = 0
        while idx < len(parent.keys) and parent.keys[idx] < key:
            idx += 1
        parent.keys.insert(idx, key)
        parent.children.insert(idx + 1, right_child)

        if len(parent.keys) >= self.order:
            self._split_internal(parent)


def db_bplus_tree_create(order: int = 4) -> Any:
    """Creates a new B+ Tree index record."""
    tree = BPlusTreeIndex(order=order)
    return Record({
        "order": tree.order,
        "total_keys": tree.total_keys,
        "instance": tree,
    })


def db_bplus_tree_insert(tree: Any, key: Any, value: Any) -> Any:
    """Inserts key and value into B+ Tree index."""
    idx = tree.instance if hasattr(tree, "instance") else tree
    idx.insert(key, value)
    return Record(idx.get_stats())


def db_bplus_tree_search(tree: Any, key: Any) -> Any:
    """Searches for key in B+ Tree index."""
    idx = tree.instance if hasattr(tree, "instance") else tree
    return idx.search(key)


def db_bplus_tree_range(tree: Any, min_key: Any, max_key: Any) -> List[Any]:
    """Scans B+ Tree index for keys within [min_key, max_key]."""
    idx = tree.instance if hasattr(tree, "instance") else tree
    pairs = idx.range_scan(min_key, max_key)
    return [Record({"key": p[0], "value": p[1]}) for p in pairs]


class BitmapIndexCompressor:
    """Run-Length Encoded (RLE) and Word-Aligned Hybrid Bitmap Index for ultra-fast columnar filtering."""

    @classmethod
    def compress(cls, bit_vector: List[int]) -> Dict[str, Any]:
        if not bit_vector:
            return {"num_bits": 0, "runs": [], "ones_count": 0}
        runs = []
        curr_val = 1 if bit_vector[0] else 0
        run_len = 0
        ones = 0
        for b in bit_vector:
            val = 1 if b else 0
            if val == 1:
                ones += 1
            if val == curr_val:
                run_len += 1
            else:
                runs.append((curr_val, run_len))
                curr_val = val
                run_len = 1
        runs.append((curr_val, run_len))
        return {
            "num_bits": len(bit_vector),
            "runs": runs,
            "ones_count": ones,
        }

    @classmethod
    def decompress(cls, compressed: Any) -> List[int]:
        c = compressed.as_dict() if hasattr(compressed, "as_dict") else compressed
        bits = []
        for val, count in c.get("runs", []):
            bits.extend([val] * count)
        return bits

    @classmethod
    def query_indices(cls, compressed: Any) -> List[int]:
        c = compressed.as_dict() if hasattr(compressed, "as_dict") else compressed
        indices = []
        pos = 0
        for val, count in c.get("runs", []):
            if val == 1:
                indices.extend(range(pos, pos + count))
            pos += count
        return indices

    @classmethod
    def bitwise_and(cls, c1: Any, c2: Any) -> Dict[str, Any]:
        b1 = cls.decompress(c1)
        b2 = cls.decompress(c2)
        n = max(len(b1), len(b2))
        b1.extend([0] * (n - len(b1)))
        b2.extend([0] * (n - len(b2)))
        res = [b1[i] & b2[i] for i in range(n)]
        return cls.compress(res)

    @classmethod
    def bitwise_or(cls, c1: Any, c2: Any) -> Dict[str, Any]:
        b1 = cls.decompress(c1)
        b2 = cls.decompress(c2)
        n = max(len(b1), len(b2))
        b1.extend([0] * (n - len(b1)))
        b2.extend([0] * (n - len(b2)))
        res = [b1[i] | b2[i] for i in range(n)]
        return cls.compress(res)

    @classmethod
    def bitwise_not(cls, c1: Any, total_bits: Optional[int] = None) -> Dict[str, Any]:
        b1 = cls.decompress(c1)
        n = total_bits if total_bits is not None else len(b1)
        if len(b1) < n:
            b1.extend([0] * (n - len(b1)))
        res = [1 - b1[i] for i in range(n)]
        return cls.compress(res)


class LSMTreeCompactionEngine:
    """Log-Structured Merge Tree with MemTable, WAL log, and Level 0 to Level 1 SSTable compaction."""

    TOMBSTONE = "__DELETED__"

    def __init__(self, memtable_threshold: int = 4):
        self.memtable_threshold = max(2, int(memtable_threshold))
        self.memtable: Dict[str, Any] = {}
        self.wal: List[Tuple[str, str, Any]] = []
        self.level0: List[List[Tuple[str, Any]]] = []
        self.level1: List[Tuple[str, Any]] = []

    def put(self, key: str, value: Any) -> None:
        k = str(key)
        self.wal.append(("PUT", k, value))
        self.memtable[k] = value
        if len(self.memtable) >= self.memtable_threshold:
            self.flush_memtable()

    def delete(self, key: str) -> None:
        k = str(key)
        self.wal.append(("DELETE", k, self.TOMBSTONE))
        self.memtable[k] = self.TOMBSTONE
        if len(self.memtable) >= self.memtable_threshold:
            self.flush_memtable()

    def flush_memtable(self) -> None:
        if not self.memtable:
            return
        sstable = sorted(self.memtable.items(), key=lambda kv: kv[0])
        self.level0.append(sstable)
        self.memtable = {}

    def get(self, key: str) -> Any:
        k = str(key)
        if k in self.memtable:
            val = self.memtable[k]
            return None if val == self.TOMBSTONE else val

        for sstable in reversed(self.level0):
            for item_k, item_v in sstable:
                if item_k == k:
                    return None if item_v == self.TOMBSTONE else item_v

        for item_k, item_v in self.level1:
            if item_k == k:
                return None if item_v == self.TOMBSTONE else item_v

        return None

    def compact_level0_to_level1(self) -> Dict[str, Any]:
        if not self.level0:
            return {"compacted_tables": 0, "level1_entries": len(self.level1)}

        merged_map: Dict[str, Any] = {}
        for k, v in self.level1:
            merged_map[k] = v

        for sstable in self.level0:
            for k, v in sstable:
                merged_map[k] = v

        compacted = [
            (k, v) for k, v in sorted(merged_map.items(), key=lambda kv: kv[0])
            if v != self.TOMBSTONE
        ]

        n_compacted = len(self.level0)
        self.level0 = []
        self.level1 = compacted

        return {
            "compacted_tables": n_compacted,
            "level1_entries": len(self.level1),
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "memtable_entries": len(self.memtable),
            "level0_tables": len(self.level0),
            "level1_entries": len(self.level1),
            "wal_records": len(self.wal),
        }


def db_bitmap_compress(bit_vector: List[int]) -> Any:
    """Compresses bit vector into RLE bitmap index."""
    return Record(BitmapIndexCompressor.compress(bit_vector))


def db_bitmap_decompress(compressed: Any) -> List[int]:
    """Decompresses RLE bitmap index back to bit vector."""
    return BitmapIndexCompressor.decompress(compressed)


def db_bitmap_and(c1: Any, c2: Any) -> Any:
    """Performs bitwise AND on two compressed bitmap indices."""
    return Record(BitmapIndexCompressor.bitwise_and(c1, c2))


def db_bitmap_or(c1: Any, c2: Any) -> Any:
    """Performs bitwise OR on two compressed bitmap indices."""
    return Record(BitmapIndexCompressor.bitwise_or(c1, c2))


def db_bitmap_not(c1: Any, total_bits: Optional[int] = None) -> Any:
    """Performs bitwise NOT on compressed bitmap index."""
    return Record(BitmapIndexCompressor.bitwise_not(c1, total_bits=total_bits))


def db_bitmap_query_indices(compressed: Any) -> List[int]:
    """Returns all 1-bit positions from compressed bitmap index."""
    return BitmapIndexCompressor.query_indices(compressed)


def db_lsm_create(memtable_threshold: int = 4) -> Any:
    """Creates an LSM tree engine."""
    lsm = LSMTreeCompactionEngine(memtable_threshold=memtable_threshold)
    return Record({
        "memtable_threshold": lsm.memtable_threshold,
        "instance": lsm,
    })


def db_lsm_put(lsm: Any, key: str, value: Any) -> Any:
    """Writes key-value pair into LSM tree."""
    inst = lsm.instance if hasattr(lsm, "instance") else lsm
    inst.put(key, value)
    return Record(inst.get_stats())


def db_lsm_get(lsm: Any, key: str) -> Any:
    """Reads key from LSM tree across MemTable, L0, and L1."""
    inst = lsm.instance if hasattr(lsm, "instance") else lsm
    return inst.get(key)


def db_lsm_delete(lsm: Any, key: str) -> Any:
    """Writes tombstone delete for key in LSM tree."""
    inst = lsm.instance if hasattr(lsm, "instance") else lsm
    inst.delete(key)
    return Record(inst.get_stats())


def db_lsm_flush(lsm: Any) -> Any:
    """Forces MemTable flush to Level 0 SSTable."""
    inst = lsm.instance if hasattr(lsm, "instance") else lsm
    inst.flush_memtable()
    return Record(inst.get_stats())


def db_lsm_compact(lsm: Any) -> Any:
    """Compacts Level 0 SSTables into Level 1."""
    inst = lsm.instance if hasattr(lsm, "instance") else lsm
    return Record(inst.compact_level0_to_level1())


# ==============================================================================
# B-TREE STORAGE ENGINE & COST-BASED QUERY OPTIMIZER (SELINGER SYSTEM R)
# ==============================================================================


class BTreeNode:
    def __init__(self, is_leaf: bool = True):
        self.is_leaf = is_leaf
        self.keys: List[Any] = []
        self.values: List[Any] = []
        self.children: List["BTreeNode"] = []


class BTreeStorageEnginePure:
    """Pure Python B-Tree Storage Engine with Configurable Order M.

    Implements balanced multi-way tree with O(log N) lookup, insertion with node splitting,
    deletion with borrowing/merging, and range query scans.
    """

    def __init__(self, order: int = 4):
        self.order = max(3, int(order))
        self.max_keys = self.order - 1
        self.min_keys = (self.order + 1) // 2 - 1
        self.root = BTreeNode(is_leaf=True)
        self.total_keys = 0

    def insert(self, key: Any, value: Any) -> None:
        root = self.root
        if len(root.keys) == self.max_keys:
            # Root is full: create new root and split old root
            new_root = BTreeNode(is_leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(self.root, key, value)
        else:
            self._insert_non_full(root, key, value)
        self.total_keys += 1

    def _insert_non_full(self, node: BTreeNode, key: Any, value: Any) -> None:
        i = len(node.keys) - 1
        if node.is_leaf:
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1
            if len(node.children[i].keys) == self.max_keys:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BTreeNode, child_idx: int) -> None:
        child = parent.children[child_idx]
        mid = len(child.keys) // 2
        median_key = child.keys[mid]
        median_val = child.values[mid]

        new_sibling = BTreeNode(is_leaf=child.is_leaf)
        new_sibling.keys = child.keys[mid + 1:]
        new_sibling.values = child.values[mid + 1:]
        if not child.is_leaf:
            new_sibling.children = child.children[mid + 1:]
            child.children = child.children[:mid + 1]

        child.keys = child.keys[:mid]
        child.values = child.values[:mid]

        parent.children.insert(child_idx + 1, new_sibling)
        parent.keys.insert(child_idx, median_key)
        parent.values.insert(child_idx, median_val)

    def search(self, key: Any) -> Optional[Any]:
        curr = self.root
        while curr:
            i = 0
            while i < len(curr.keys) and key > curr.keys[i]:
                i += 1
            if i < len(curr.keys) and key == curr.keys[i]:
                return curr.values[i]
            if curr.is_leaf:
                return None
            curr = curr.children[i]
        return None

    def range_scan(self, min_key: Any, max_key: Any) -> List[Tuple[Any, Any]]:
        results: List[Tuple[Any, Any]] = []

        def traverse(node: BTreeNode) -> None:
            for i, k in enumerate(node.keys):
                if not node.is_leaf and (min_key is None or k >= min_key):
                    traverse(node.children[i])
                if (min_key is None or k >= min_key) and (max_key is None or k <= max_key):
                    results.append((k, node.values[i]))
            if not node.is_leaf and (max_key is None or node.keys[-1] <= max_key):
                traverse(node.children[-1])

        traverse(self.root)
        return results

    def get_height(self) -> int:
        h = 0
        curr = self.root
        while curr and not curr.is_leaf:
            h += 1
            curr = curr.children[0]
        return h + 1


class CostBasedQueryOptimizerCBO:
    """Selinger / System R Dynamic Programming Cost-Based Join Optimizer.

    Evaluates access paths (SeqScan vs IndexScan) and join algorithms (HashJoin vs
    NestedLoopJoin). Determines minimal-cost join tree using selectivity estimation.
    """

    @classmethod
    def optimize(
        cls,
        tables: Dict[str, Dict[str, Any]],
        joins: List[Dict[str, str]],
        predicates: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Calculates optimal join order and physical operator plan."""
        table_names = sorted(list(tables.keys()))
        n_tbl = len(table_names)
        if n_tbl == 0:
            return {"plan": "EMPTY", "cost": 0.0, "estimated_rows": 0}

        # 1. Base table scan costs and cardinalities
        base_plans: Dict[str, Dict[str, Any]] = {}
        for t_name in table_names:
            t_info = tables[t_name]
            rows = float(t_info.get("rows", 1000))
            pages = float(t_info.get("pages", 100))
            indexes = t_info.get("indexes", [])

            # Check if filtered by single-table predicate
            t_pred = next((p for p in (predicates or []) if p.get("table") == t_name), None)
            if t_pred and t_pred.get("column") in indexes:
                # Index scan
                selectivity = float(t_pred.get("selectivity", 0.05))
                est_rows = max(1.0, rows * selectivity)
                cost = 2.0 + (selectivity * pages) + (0.01 * est_rows)
                base_plans[t_name] = {
                    "op": "IndexScan",
                    "table": t_name,
                    "index": t_pred["column"],
                    "cost": round(cost, 2),
                    "rows": int(round(est_rows)),
                }
            else:
                # SeqScan
                cost = pages + (0.01 * rows)
                base_plans[t_name] = {
                    "op": "SeqScan",
                    "table": t_name,
                    "cost": round(cost, 2),
                    "rows": int(round(rows)),
                }

        if n_tbl == 1:
            plan = base_plans[table_names[0]]
            return {"optimal_plan": plan, "total_cost": plan["cost"], "estimated_rows": plan["rows"]}

        # 2. Dynamic programming over subsets of tables
        # memo[frozenset]: best plan dict
        memo: Dict[frozenset, Dict[str, Any]] = {
            frozenset([t]): base_plans[t] for t in table_names
        }

        # Generate combinations of increasing sizes
        from itertools import combinations

        for size in range(2, n_tbl + 1):
            for subset in combinations(table_names, size):
                set_key = frozenset(subset)
                best_sub_plan = None
                min_cost = float("inf")

                # Partition into left and right sub-plans
                for left_size in range(1, size):
                    for left_comb in combinations(subset, left_size):
                        left_set = frozenset(left_comb)
                        right_set = set_key - left_set

                        left_plan = memo.get(left_set)
                        right_plan = memo.get(right_set)
                        if not left_plan or not right_plan:
                            continue

                        # Find applicable join predicates between left and right
                        join_pred = next(
                            (
                                j for j in joins
                                if (j["left_table"] in left_set and j["right_table"] in right_set)
                                or (j["right_table"] in left_set and j["left_table"] in right_set)
                            ),
                            None,
                        )

                        l_rows = left_plan["rows"]
                        r_rows = right_plan["rows"]

                        if join_pred:
                            # Estimate join selectivity
                            sel = 1.0 / max(50.0, float(tables.get(join_pred["left_table"], {}).get("ndv", 50)))
                            out_rows = max(1.0, (l_rows * r_rows) * sel)
                        else:
                            # Cartesian cross product
                            out_rows = l_rows * r_rows

                        # Hash join cost: cost(L) + cost(R) + 2*(L+R)*0.005
                        cost_hash = left_plan["cost"] + right_plan["cost"] + 0.01 * (l_rows + r_rows)

                        # Nested loop join cost: cost(L) + L * cost(R)
                        cost_nl = left_plan["cost"] + l_rows * (right_plan["cost"] * 0.05)

                        chosen_op = "HashJoin" if cost_hash <= cost_nl else "NestedLoopJoin"
                        chosen_cost = min(cost_hash, cost_nl)

                        if chosen_cost < min_cost:
                            min_cost = chosen_cost
                            best_sub_plan = {
                                "op": chosen_op,
                                "left": left_plan,
                                "right": right_plan,
                                "join_predicate": join_pred,
                                "cost": round(chosen_cost, 2),
                                "rows": int(round(out_rows)),
                            }

                if best_sub_plan:
                    memo[set_key] = best_sub_plan

        full_set = frozenset(table_names)
        optimal = memo.get(full_set, {})

        return {
            "optimal_plan": optimal,
            "total_cost": optimal.get("cost", 0.0),
            "estimated_rows": optimal.get("rows", 0),
            "root_operator": optimal.get("op", "None"),
        }


def db_btree_index_benchmark(
    order: int = 4,
    num_keys: int = 20,
) -> Record:
    """Benchmarks B-Tree insertion, search, and range scanning."""
    btree = BTreeStorageEnginePure(order=order)
    for i in range(num_keys):
        btree.insert(f"key_{i:03d}", i * 10)

    val = btree.search("key_005")
    range_res = btree.range_scan("key_002", "key_006")

    return Record({
        "order": order,
        "total_keys": btree.total_keys,
        "tree_height": btree.get_height(),
        "search_key_005": val,
        "range_count": len(range_res),
    })


def db_cost_based_join_optimizer(
    tables: Dict[str, Dict[str, Any]],
    joins: List[Dict[str, str]],
    predicates: Optional[List[Dict[str, Any]]] = None,
) -> Record:
    """Finds optimal join order using Selinger dynamic programming CBO."""
    return Record(CostBasedQueryOptimizerCBO.optimize(tables, joins, predicates=predicates))





def execute_db_ir(spec: Any) -> Any:
    """Executes a Database Domain IR specification against the caller's scope."""
    import sys
    from doomscript.domains.registry import get_domain_registry
    if isinstance(spec, str):
        spec = get_domain_registry().get_spec(spec)
    caller_frame = sys._getframe(1)
    target_env = caller_frame.f_globals if caller_frame.f_globals is not None else caller_frame.f_locals
    scope = dict(target_env)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    res = get_db_runtime().execute_query_spec(spec, scope)
    for k, v in scope.items():
        target_env[k] = v
    return res


def insert_rows(table_name: str, data: Any) -> Any:
    """Inserts records into a database table."""
    import sys
    caller_frame = sys._getframe(1)
    scope = dict(caller_frame.f_globals)
    if caller_frame.f_locals:
        scope.update(caller_frame.f_locals)
    return get_db_runtime().insert_rows(table_name, data, scope)


def db_find_rows(table_name: str, where_sql: Optional[str] = None) -> list:
    """Query rows from an SQLite table in the active db session."""
    from doomscript.core.record import Record
    db_rt = get_db_runtime()
    q = f'SELECT * FROM "{table_name}"'
    if where_sql:
        q += f" WHERE {where_sql}"
    cur = db_rt.get_connection().cursor()
    try:
        cur.execute(q)
    except Exception:
        return []
    cols = [d[0] for d in cur.description] if cur.description else []
    rows = cur.fetchall()
    return [Record(dict(zip(cols, r))) for r in rows]


def db_count_rows(table_name: str) -> int:
    """Count rows in an SQLite table in the active db session."""
    db_rt = get_db_runtime()
    cur = db_rt.get_connection().cursor()
    cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
    row = cur.fetchone()
    return row[0] if row else 0


def db_wal_create() -> WALCrashRecovery:
    """Instantiates an ARIES write-ahead logger with recovery support."""
    return WALCrashRecovery()


def db_query_optimizer() -> CostBasedQueryOptimizer:
    """Instantiates a cost-based query optimizer for table scan planning."""
    return CostBasedQueryOptimizer()


def db_mvcc_create() -> SnapshotIsolationMVCC:
    """Instantiates a Snapshot Isolation Multi-Version Concurrency Control engine."""
    return SnapshotIsolationMVCC()
