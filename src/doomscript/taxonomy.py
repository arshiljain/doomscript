"""
DoomScript Universal Interoperability Value Taxonomy & Conversion Protocols.

Standardizes runtime value representations across domains:
- Scalar & Collection
- Record & RecordList
- Table (with typed columns, row_count, schema, markdown/html export)
- Plot, Graph, Model, Audio, Image, Agent, Connection, Document, Spreadsheet, Bucket
"""

from __future__ import annotations
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Union
import html as html_lib

class ValueKind(Enum):
    SCALAR = "scalar"
    COLLECTION = "collection"
    RECORD = "record"
    RECORD_LIST = "record_list"
    TABLE = "table"
    PLOT = "plot"
    GRAPH = "graph"
    MODEL = "model"
    AUDIO = "audio"
    IMAGE = "image"
    AGENT = "agent"
    CONNECTION = "connection"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    BUCKET = "bucket"
    UNKNOWN = "unknown"


def _infer_type(val: Any) -> str:
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, float):
        return "float"
    if isinstance(val, str):
        return "str"
    if isinstance(val, (list, tuple, set)):
        return "list"
    if isinstance(val, dict):
        return "dict"
    return type(val).__name__


class RecordList(list):
    """
    A list of Record objects with convenient tabular and conversion helpers.
    """
    def to_table(self) -> "Table":
        return to_table(self)

    def where(self, predicate: Callable[[Any], bool]) -> "RecordList":
        from doomscript.runtime import Record
        return RecordList([r for r in self if predicate(r)])


class Table:
    """
    Columnar and row-oriented tabular data structure with explicit schema,
    column names, row counts, and rich conversion protocols.
    """
    def __init__(
        self,
        columns: Sequence[str],
        rows: Sequence[Sequence[Any]],
        schema: Optional[Dict[str, str]] = None,
        name: str = "table",
    ):
        self.name = name
        self.columns = list(columns)
        self.rows = [list(r) for r in rows]
        if schema is None:
            self.schema = self._infer_schema()
        else:
            self.schema = dict(schema)

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return len(self.columns)

    def _infer_schema(self) -> Dict[str, str]:
        schema: Dict[str, str] = {}
        if not self.rows:
            return {col: "unknown" for col in self.columns}
        for col_idx, col_name in enumerate(self.columns):
            inferred = "unknown"
            for row in self.rows:
                if col_idx < len(row) and row[col_idx] is not None:
                    inferred = _infer_type(row[col_idx])
                    break
            schema[col_name] = inferred
        return schema

    @classmethod
    def from_records(cls, records: Sequence[Any], name: str = "table") -> "Table":
        if not records:
            return cls(columns=[], rows=[], schema={}, name=name)
        # Determine all unique keys in order
        col_order: List[str] = []
        for r in records:
            keys = r.keys() if hasattr(r, "keys") else (r.get_fields() if hasattr(r, "get_fields") else [])
            for k in keys:
                if k not in col_order:
                    col_order.append(str(k))
        
        rows: List[List[Any]] = []
        for r in records:
            row = []
            for col in col_order:
                if isinstance(r, dict) or hasattr(r, "__getitem__"):
                    try:
                        row.append(r[col])
                    except (KeyError, IndexError):
                        row.append(getattr(r, col, None))
                else:
                    row.append(getattr(r, col, None))
            rows.append(row)
        return cls(columns=col_order, rows=rows, name=name)

    @classmethod
    def from_columns(cls, data: Dict[str, Sequence[Any]], name: str = "table") -> "Table":
        columns = list(data.keys())
        if not columns:
            return cls(columns=[], rows=[], schema={}, name=name)
        num_rows = len(next(iter(data.values())))
        rows = []
        for i in range(num_rows):
            rows.append([data[col][i] if i < len(data[col]) else None for col in columns])
        return cls(columns=columns, rows=rows, name=name)

    def to_records(self) -> RecordList:
        from doomscript.runtime import Record
        result = RecordList()
        for row in self.rows:
            rec_dict = {}
            for col_idx, col_name in enumerate(self.columns):
                rec_dict[col_name] = row[col_idx] if col_idx < len(row) else None
            result.append(Record(rec_dict))
        return result

    def to_dict(self) -> Dict[str, List[Any]]:
        col_dict: Dict[str, List[Any]] = {col: [] for col in self.columns}
        for row in self.rows:
            for col_idx, col_name in enumerate(self.columns):
                val = row[col_idx] if col_idx < len(row) else None
                col_dict[col_name].append(val)
        return col_dict

    def to_markdown(self) -> str:
        if not self.columns:
            return "*(Empty table)*"
        header = "| " + " | ".join(self.columns) + " |"
        sep = "| " + " | ".join(["---"] * len(self.columns)) + " |"
        body_lines = []
        for row in self.rows:
            row_str = "| " + " | ".join(str(v) if v is not None else "" for v in row) + " |"
            body_lines.append(row_str)
        return "\n".join([header, sep] + body_lines)

    def to_html(self) -> str:
        out = ["<table>", "  <thead>", "    <tr>"]
        for col in self.columns:
            out.append(f"      <th>{html_lib.escape(str(col))}</th>")
        out.extend(["    </tr>", "  </thead>", "  <tbody>"])
        for row in self.rows:
            out.append("    <tr>")
            for val in row:
                s = "" if val is None else str(val)
                out.append(f"      <td>{html_lib.escape(s)}</td>")
            out.append("    </tr>")
        out.extend(["  </tbody>", "</table>"])
        return "\n".join(out)

    def __repr__(self) -> str:
        return f"<Table '{self.name}' ({self.row_count} rows, {self.column_count} columns: {', '.join(self.columns)})>"


def to_table(obj: Any) -> Table:
    """Convert any tabular-like object (RecordList, list of dicts/Records, column dict) to a Table."""
    if isinstance(obj, Table):
        return obj
    if isinstance(obj, dict):
        # Could be dict of columns
        if all(isinstance(v, (list, tuple)) for v in obj.values()):
            return Table.from_columns(obj)
        # Single record
        return Table.from_records([obj])
    if isinstance(obj, (list, tuple)):
        if not obj:
            return Table(columns=[], rows=[])
        if all(isinstance(item, dict) or hasattr(item, "keys") for item in obj):
            return Table.from_records(obj)
        if all(isinstance(item, (list, tuple)) for item in obj):
            # 2D matrix
            cols = [f"col_{i}" for i in range(len(obj[0]))]
            return Table(columns=cols, rows=obj)
    raise TypeError(f"Cannot convert object of type {type(obj).__name__} to Table")


def to_records(obj: Any) -> RecordList:
    """Convert a Table or collection of dicts/records into a RecordList."""
    from doomscript.runtime import Record
    if isinstance(obj, Table):
        return obj.to_records()
    if isinstance(obj, RecordList):
        return obj
    if isinstance(obj, (list, tuple)):
        res = RecordList()
        for item in obj:
            if isinstance(item, Record):
                res.append(item)
            elif isinstance(item, dict):
                res.append(Record(item))
            else:
                res.append(Record(value=item))
        return res
    if isinstance(obj, dict):
        return RecordList([Record(obj)])
    raise TypeError(f"Cannot convert object of type {type(obj).__name__} to RecordList")


def classify_value(val: Any) -> ValueKind:
    """Classify any runtime object into its ValueKind taxonomy category."""
    if val is None or isinstance(val, (int, float, str, bool)):
        return ValueKind.SCALAR
    if isinstance(val, Table):
        return ValueKind.TABLE
    from doomscript.runtime import Record
    if isinstance(val, Record):
        return ValueKind.RECORD
    if isinstance(val, dict):
        return ValueKind.RECORD
    if isinstance(val, (list, tuple, set)):
        if not val:
            return ValueKind.COLLECTION
        if all(isinstance(x, (Record, dict)) for x in val):
            return ValueKind.RECORD_LIST
        return ValueKind.COLLECTION

    # Duck-typing checks for domain objects
    cls_name = type(val).__name__.lower()
    if "plot" in cls_name or "figure" in cls_name or hasattr(val, "to_spec"):
        return ValueKind.PLOT
    if "graph" in cls_name or (hasattr(val, "nodes") and hasattr(val, "edges")):
        return ValueKind.GRAPH
    if "model" in cls_name or hasattr(val, "predict") or hasattr(val, "train"):
        return ValueKind.MODEL
    if "audio" in cls_name or hasattr(val, "sample_rate") or hasattr(val, "play"):
        return ValueKind.AUDIO
    if "image" in cls_name or (hasattr(val, "save") and hasattr(val, "size")):
        return ValueKind.IMAGE
    if "agent" in cls_name or hasattr(val, "run_step") or hasattr(val, "ask"):
        return ValueKind.AGENT
    if "connection" in cls_name or hasattr(val, "execute") or hasattr(val, "cursor"):
        return ValueKind.CONNECTION
    if "document" in cls_name or hasattr(val, "pages"):
        return ValueKind.DOCUMENT
    if "spreadsheet" in cls_name or hasattr(val, "sheets"):
        return ValueKind.SPREADSHEET
    if "bucket" in cls_name or hasattr(val, "upload_file"):
        return ValueKind.BUCKET

    return ValueKind.UNKNOWN
