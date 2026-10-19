"""Native Python AST Exporter for Databases and SQL domain queries."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.db.spec import QuerySpec


class DBASTExporter(DomainASTExporter):
    """Translates QuerySpec IR into standard library sqlite3 Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        if not isinstance(ir, QuerySpec):
            raise TypeError(f"DBASTExporter expects QuerySpec, got {type(ir).__name__}")

        imports: Set[str] = {"sqlite3"}
        stmts: List[ast.stmt] = []

        sql, params = ir.to_parameterized_sql()

        # Build parameterized execute call
        param_elts = []
        for p in params:
            if isinstance(p, (int, float, str, bool)):
                param_elts.append(ast.Constant(value=p))
            else:
                param_elts.append(ast.Constant(value=str(p)))

        params_tuple = ast.Tuple(elts=param_elts, ctx=ast.Load())

        # cursor = conn.execute(sql, params)
        cur_name = f"{var_name}_cur"
        exec_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id="_conn", ctx=ast.Load()), attr="execute", ctx=ast.Load()),
            args=[ast.Constant(value=sql), params_tuple],
            keywords=[],
        )
        stmts.append(ast.Assign(targets=[ast.Name(id=cur_name, ctx=ast.Store())], value=exec_call))

        # var_name = [dict(r) for r in cur.fetchall()]
        fetch_call = ast.Call(
            func=ast.Attribute(value=ast.Name(id=cur_name, ctx=ast.Load()), attr="fetchall", ctx=ast.Load()),
            args=[],
            keywords=[],
        )
        comp = ast.ListComp(
            elt=ast.Call(
                func=ast.Name(id="dict", ctx=ast.Load()),
                args=[ast.Name(id="r", ctx=ast.Load())],
                keywords=[],
            ),
            generators=[
                ast.comprehension(
                    target=ast.Name(id="r", ctx=ast.Store()),
                    iter=fetch_call,
                    ifs=[],
                    is_async=0,
                )
            ],
        )
        stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=comp))

        return imports, stmts
