"""Native Python AST Exporter for Image & Vision domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.image.spec import (
    ImageOpenSpec,
    ImageCreateSpec,
    ImageResizeSpec,
    ImageCropSpec,
    ImageRotateSpec,
    ImageFilterSpec,
    ImageSaveSpec,
)


class ImageASTExporter(DomainASTExporter):
    """Translates Image Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"PIL.Image"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, ImageOpenSpec):
            call_node = ast.Call(
                func=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="PIL", ctx=ast.Load()),
                        attr="Image",
                        ctx=ast.Load(),
                    ),
                    attr="open",
                    ctx=ast.Load(),
                ),
                args=[ast.Constant(value=ir.path_expr)],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, ImageCreateSpec):
            call_node = ast.Call(
                func=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="PIL", ctx=ast.Load()),
                        attr="Image",
                        ctx=ast.Load(),
                    ),
                    attr="new",
                    ctx=ast.Load(),
                ),
                args=[
                    ast.Constant(value="RGB"),
                    ast.Tuple(
                        elts=[ast.Constant(value=ir.width), ast.Constant(value=ir.height)],
                        ctx=ast.Load(),
                    ),
                ],
                keywords=[ast.keyword(arg="color", value=ast.Constant(value=ir.color))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, ImageResizeSpec):
            call_node = ast.Call(
                func=ast.Name(id="resize_image", ctx=ast.Load()),
                args=[ast.Name(id=ir.image_var, ctx=ast.Load())],
                keywords=[
                    ast.keyword(
                        arg="width",
                        value=ast.Constant(value=ir.width) if ir.width is not None else ast.Constant(value=None),
                    ),
                    ast.keyword(
                        arg="height",
                        value=ast.Constant(value=ir.height) if ir.height is not None else ast.Constant(value=None),
                    ),
                    ast.keyword(
                        arg="percent",
                        value=ast.Constant(value=ir.percent) if ir.percent is not None else ast.Constant(value=None),
                    ),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, ImageCropSpec):
            call_node = ast.Call(
                func=ast.Name(id="crop_image", ctx=ast.Load()),
                args=[
                    ast.Name(id=ir.image_var, ctx=ast.Load()),
                    ast.Constant(value=ir.x1),
                    ast.Constant(value=ir.y1),
                    ast.Constant(value=ir.x2),
                    ast.Constant(value=ir.y2),
                ],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, ImageSaveSpec):
            call_node = ast.Call(
                func=ast.Name(id="save_image", ctx=ast.Load()),
                args=[
                    ast.Name(id=ir.image_var, ctx=ast.Load()),
                    ast.Constant(value=ir.path_expr),
                ],
                keywords=[
                    ast.keyword(
                        arg="quality",
                        value=ast.Constant(value=ir.quality) if ir.quality is not None else ast.Constant(value=None),
                    )
                ],
            )
            stmts.append(ast.Expr(value=call_node))

        return imports, stmts
