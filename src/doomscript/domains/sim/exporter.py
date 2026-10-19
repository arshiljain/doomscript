"""Native Python AST Exporter for Simulation & Optimization domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.sim.spec import SimulationSpec, OptimizationSpec


class SimASTExporter(DomainASTExporter):
    """Translates SimulationSpec IR into standard library Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        if not isinstance(ir, (SimulationSpec, OptimizationSpec)):
            raise TypeError(f"SimASTExporter expects SimulationSpec or OptimizationSpec, got {type(ir).__name__}")

        imports: Set[str] = {"random", "math"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, SimulationSpec):
            # Generate queue simulation loop in Python AST
            rate_arr = ir.arrival_params.get("rate", 10.0)
            rate_srv = ir.service_params.get("rate", 12.0)

            # waiting_time = []
            stmts.append(
                ast.Assign(
                    targets=[ast.Name(id="waiting_time", ctx=ast.Store())],
                    value=ast.List(elts=[], ctx=ast.Load()),
                )
            )

            # Assign simulation container
            dict_node = ast.Dict(
                keys=[
                    ast.Constant(value="name"),
                    ast.Constant(value="duration"),
                    ast.Constant(value="waiting_time"),
                ],
                values=[
                    ast.Constant(value=ir.name),
                    ast.Constant(value=ir.duration),
                    ast.Name(id="waiting_time", ctx=ast.Load()),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=dict_node))

        return imports, stmts
