"""Native Python AST Exporter for Optimization & Operations Research domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.opt.spec import LinearProgramSpec, SolveLPSpec


class OptASTExporter(DomainASTExporter):
    """Translates LinearProgramSpec IR into standard Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = set()
        stmts: List[ast.stmt] = []

        if isinstance(ir, LinearProgramSpec):
            dict_node = ast.Dict(
                keys=[
                    ast.Constant(value="name"),
                    ast.Constant(value="sense"),
                    ast.Constant(value="objective"),
                    ast.Constant(value="constraints"),
                ],
                values=[
                    ast.Constant(value=ir.name),
                    ast.Constant(value=ir.sense),
                    ast.Constant(value=ir.objective),
                    ast.List(
                        elts=[ast.Constant(value=c) for c in ir.constraints],
                        ctx=ast.Load(),
                    ),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=dict_node))

        elif isinstance(ir, SolveLPSpec):
            call_node = ast.Call(
                func=ast.Name(id="solve_linear_program", ctx=ast.Load()),
                args=[ast.Name(id=ir.lp_name, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
