"""Runtime execution engine for Databases and SQL operations."""

import contextlib
import sqlite3
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
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
