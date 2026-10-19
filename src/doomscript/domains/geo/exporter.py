"""Native Python AST Exporter for Geospatial Analytics domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.geo.spec import (
    GeoPointSpec,
    GeoPolygonSpec,
    GeoDistanceSpec,
    GeoContainmentSpec,
    GeoBoundingBoxSpec,
    GeoSpatialJoinSpec,
)


class GeoASTExporter(DomainASTExporter):
    """Translates Geospatial domain IR to Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"math"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, GeoPointSpec):
            call_node = ast.Call(
                func=ast.Name(id="point", ctx=ast.Load()),
                args=[
                    ast.Constant(value=float(ir.lat_expr)),
                    ast.Constant(value=float(ir.lon_expr)),
                ],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, GeoDistanceSpec):
            call_node = ast.Call(
                func=ast.Name(id="distance_between", ctx=ast.Load()),
                args=[
                    ast.Name(id=ir.p1_expr, ctx=ast.Load()),
                    ast.Name(id=ir.p2_expr, ctx=ast.Load()),
                ],
                keywords=[ast.keyword(arg="unit", value=ast.Constant(value=ir.unit))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
