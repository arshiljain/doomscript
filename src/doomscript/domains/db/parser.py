"""Independent Domain Parser for Databases and SQL language constructs."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.db.spec import QuerySpec, WhereClause


class DBDomainParser(DomainParser):
    """Independent parser for Databases and SQL syntax (inspect table, execute sql, query blocks)."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        # inspect table <name> [into <target>]
        m = re.match(
            r"^inspect\s+table\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            tbl_name = m.group(1)
            target = m.group(2) or "table_schema"
            return f'set {target} to inspect_table_schema("{tbl_name}")'

        # schema of <table> [into <target>]
        m2 = re.match(
            r"^schema\s+of\s+(?:table\s+)?([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            tbl_name = m2.group(1)
            target = m2.group(2) or "table_schema"
            return f'set {target} to inspect_table_schema("{tbl_name}")'

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        # execute sql / query db / query sql "<query>" [with <params>] [into <target>]
        m = re.match(
            r'^(?:execute\s+sql|query\s+(?:db|sql))\s+(?:"(.*?)"|\'(.*?)\')(?:\s+with\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$',
            line.strip(),
            re.IGNORECASE,
        )
        if m:
            sql_str = m.group(1) if m.group(1) is not None else m.group(2)
            params = m.group(3)
            target = m.group(4)
            clean_sql = sql_str.replace('"', '\\"')
            call_expr = (
                f'execute_raw_sql("{clean_sql}", params={params})'
                if params
                else f'execute_raw_sql("{clean_sql}")'
            )
            if target:
                return f"set {target} to {call_expr}"
            return call_expr

        # insert into <table> values <expr>
        m2 = re.match(
            r"^insert\s+into\s+([A-Za-z_]\w*)\s+values\s+(.+)$",
            line.strip(),
            re.IGNORECASE,
        )
        if m2:
            tbl = m2.group(1)
            expr = m2.group(2).strip()
            return f'insert_rows("{tbl}", {expr})'

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[QuerySpec, str]:
        # query <table> [into <target>]:
        m = re.match(
            r"^query\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:?$",
            header.strip(),
            re.IGNORECASE,
        )
        if not m:
            raise SyntaxError(f"Invalid query header: {header}")

        tbl_name = m.group(1)
        target = m.group(2) or "query_results"

        spec = QuerySpec(table=tbl_name, target_var=target)

        for l_no, raw_line in body_lines:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            # select <col1>, <col2>, ...
            sel_m = re.match(r"^select\s+(.+)$", line, re.IGNORECASE)
            if sel_m:
                raw_cols = sel_m.group(1).split(",")
                spec.columns = [c.strip().strip("\"'") for c in raw_cols if c.strip()]
                continue

            # where ...
            where_m = re.match(r"^where\s+(.+)$", line, re.IGNORECASE)
            if where_m:
                cond_str = where_m.group(1).strip()
                # Split on ' and '
                conds = re.split(r"\s+and\s+", cond_str, flags=re.IGNORECASE)
                for cond in conds:
                    w = self._parse_single_condition(cond)
                    if w:
                        spec.where.append(w)
                continue

            # order by <col> [descending|ascending]
            ord_m = re.match(
                r"^order\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending|desc|asc))?",
                line,
                re.IGNORECASE,
            )
            if ord_m:
                spec.order_by = ord_m.group(1)
                d_str = (ord_m.group(2) or "").lower()
                spec.order_descending = d_str in ("descending", "desc")
                continue

            # limit <n>
            lim_m = re.match(r"^limit\s+(\d+)$", line, re.IGNORECASE)
            if lim_m:
                spec.limit = int(lim_m.group(1))
                continue

        errors = spec.validate()
        if errors:
            raise SyntaxError(f"Query validation error for '{tbl_name}': {'; '.join(errors)}")

        return spec, target

    def _parse_single_condition(self, cond: str) -> Optional[WhereClause]:
        cond = cond.strip()
        # Patterns:
        # <col> is over / greater than / > <val>
        m_gt = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+over|is\s+greater\s+than|>)\s+(.+)$", cond, re.IGNORECASE)
        if m_gt:
            return WhereClause(column=m_gt.group(1), operator=">", value=self._eval_value(m_gt.group(2)))

        # <col> is under / less than / < <val>
        m_lt = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+under|is\s+less\s+than|<)\s+(.+)$", cond, re.IGNORECASE)
        if m_lt:
            return WhereClause(column=m_lt.group(1), operator="<", value=self._eval_value(m_lt.group(2)))

        # <col> is at least / >= <val>
        m_gte = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+at\s+least|>=)\s+(.+)$", cond, re.IGNORECASE)
        if m_gte:
            return WhereClause(column=m_gte.group(1), operator=">=", value=self._eval_value(m_gte.group(2)))

        # <col> is at most / <= <val>
        m_lte = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+at\s+most|<=)\s+(.+)$", cond, re.IGNORECASE)
        if m_lte:
            return WhereClause(column=m_lte.group(1), operator="<=", value=self._eval_value(m_lte.group(2)))

        # <col> is not / != <val>
        m_ne = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+not|!=)\s+(.+)$", cond, re.IGNORECASE)
        if m_ne:
            return WhereClause(column=m_ne.group(1), operator="!=", value=self._eval_value(m_ne.group(2)))

        # <col> equals / is / == <val>
        m_eq = re.match(r"^([A-Za-z_]\w*)\s+(?:equals|is|==|=)\s+(.+)$", cond, re.IGNORECASE)
        if m_eq:
            return WhereClause(column=m_eq.group(1), operator="=", value=self._eval_value(m_eq.group(2)))

        return None

    def _eval_value(self, val_str: str) -> Any:
        val_str = val_str.strip()
        try:
            return eval(val_str, {}, {})
        except Exception:
            return val_str.strip("\"'")
