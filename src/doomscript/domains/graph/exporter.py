"""Native Python AST Exporter for Graph Analytics domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.graph.spec import (
    GraphCreateSpec,
    GraphAddNodeSpec,
    GraphAddEdgeSpec,
    GraphShortestPathSpec,
    GraphPageRankSpec,
    GraphDegreesSpec,
    GraphCommunitiesSpec,
)


class GraphASTExporter(DomainASTExporter):
    """Translates Graph Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"heapq"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, GraphCreateSpec):
            call_node = ast.Call(
                func=ast.Name(id="create_graph", ctx=ast.Load()),
                args=[],
                keywords=[ast.keyword(arg="directed", value=ast.Constant(value=ir.directed))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, GraphShortestPathSpec):
            call_node = ast.Call(
                func=ast.Name(id="graph_shortest_path", ctx=ast.Load()),
                args=[
                    ast.Name(id=ir.graph_var, ctx=ast.Load()),
                    ast.Constant(value=ir.start_node),
                    ast.Constant(value=ir.end_node),
                ],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, GraphPageRankSpec):
            call_node = ast.Call(
                func=ast.Name(id="graph_pagerank", ctx=ast.Load()),
                args=[ast.Name(id=ir.graph_var, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, GraphDegreesSpec):
            call_node = ast.Call(
                func=ast.Name(id="graph_degrees", ctx=ast.Load()),
                args=[ast.Name(id=ir.graph_var, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, GraphCommunitiesSpec):
            call_node = ast.Call(
                func=ast.Name(id="graph_communities", ctx=ast.Load()),
                args=[ast.Name(id=ir.graph_var, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
