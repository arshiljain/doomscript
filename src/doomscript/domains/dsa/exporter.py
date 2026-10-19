"""Native Python AST Exporter for Testing & Algorithm Analysis (DSA)."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.dsa.spec import BenchmarkSpec


class DsaASTExporter(DomainASTExporter):
    """Translates BenchmarkSpec IR into standard library Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        if not isinstance(ir, BenchmarkSpec):
            raise TypeError(f"DsaASTExporter expects BenchmarkSpec, got {type(ir).__name__}")

        imports: Set[str] = {"time", "tracemalloc"}
        stmts: List[ast.stmt] = []

        # var_name = {"fn": fn_name, "sizes": [...], "repeat": repeat}
        dict_node = ast.Dict(
            keys=[
                ast.Constant(value="fn_name"),
                ast.Constant(value="input_sizes"),
                ast.Constant(value="repeat"),
            ],
            values=[
                ast.Constant(value=ir.fn_name),
                ast.List(elts=[ast.Constant(value=s) for s in ir.input_sizes], ctx=ast.Load()),
                ast.Constant(value=ir.repeat),
            ],
        )
        stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=dict_node))

        return imports, stmts
