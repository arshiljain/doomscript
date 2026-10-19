"""Databases and SQL Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainIR


@dataclass
class WhereClause:
    column: str
    operator: str  # "=", "!=", ">", "<", ">=", "<=", "LIKE", "IN"
    value: Any


@dataclass
class QuerySpec(DomainIR):
    """Specification for a structured relational query."""

    table: str
    columns: List[str] = field(default_factory=lambda: ["*"])
    where: List[WhereClause] = field(default_factory=list)
    order_by: Optional[str] = None
    order_descending: bool = False
    limit: Optional[int] = None
    target_var: str = "query_results"

    def validate(self) -> List[str]:
        errors = []
        if not self.table:
            errors.append("Query table name cannot be empty")
        if not self.columns:
            errors.append("Query requires at least one selected column or '*'")
        if self.limit is not None and self.limit < 0:
            errors.append(f"Limit must be non-negative, got {self.limit}")
        return errors

    def to_parameterized_sql(self) -> Tuple[str, List[Any]]:
        """Safely compiles the query spec into parameterized SQL and parameter values."""
        cols_sql = ", ".join(self.columns) if self.columns else "*"
        sql_parts = [f"SELECT {cols_sql} FROM {self.table}"]
        params: List[Any] = []

        if self.where:
            where_strs = []
            for w in self.where:
                where_strs.append(f"{w.column} {w.operator} ?")
                params.append(w.value)
            sql_parts.append("WHERE " + " AND ".join(where_strs))

        if self.order_by:
            direction = "DESC" if self.order_descending else "ASC"
            sql_parts.append(f"ORDER BY {self.order_by} {direction}")

        if self.limit is not None:
            sql_parts.append(f"LIMIT {int(self.limit)}")

        return " ".join(sql_parts), params
