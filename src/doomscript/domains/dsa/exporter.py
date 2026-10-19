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

        imports: Set[str] = {"time", "tracemalloc", "math"}
        stmts: List[ast.stmt] = []

        call_node = ast.Call(
            func=ast.Name(id="run_dsa_benchmark", ctx=ast.Load()),
            args=[
                ast.Constant(value=ir.fn_name),
            ],
            keywords=[
                ast.keyword(
                    arg="input_sizes",
                    value=ast.List(elts=[ast.Constant(value=s) for s in ir.input_sizes], ctx=ast.Load()),
                ),
                ast.keyword(arg="repeat", value=ast.Constant(value=ir.repeat)),
                ast.keyword(arg="generator", value=ast.Constant(value=ir.generator)),
                ast.keyword(arg="measure_memory", value=ast.Constant(value=ir.measure_memory)),
            ],
        )
        stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
