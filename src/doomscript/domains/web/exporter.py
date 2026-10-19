"""Native Python AST Exporter for Web Scraping & Document Extraction domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.web.spec import (
    WebPageSpec,
    WebExtractLinksSpec,
    WebExtractTableSpec,
    WebExtractTextSpec,
    WebDownloadMediaSpec,
)


class WebASTExporter(DomainASTExporter):
    """Translates Web Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"urllib.request", "bs4"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, WebPageSpec):
            call_node = ast.Call(
                func=ast.Name(id="open_webpage", ctx=ast.Load()),
                args=[ast.Constant(value=ir.url_expr)],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, WebExtractLinksSpec):
            call_node = ast.Call(
                func=ast.Name(id="extract_web_links", ctx=ast.Load()),
                args=[ast.Name(id=ir.page_var, ctx=ast.Load())],
                keywords=[
                    ast.keyword(
                        arg="filter_class",
                        value=ast.Constant(value=ir.filter_class) if ir.filter_class else ast.Constant(value=None),
                    )
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, WebExtractTableSpec):
            call_node = ast.Call(
                func=ast.Name(id="extract_web_table", ctx=ast.Load()),
                args=[ast.Name(id=ir.page_var, ctx=ast.Load())],
                keywords=[
                    ast.keyword(
                        arg="header_contains",
                        value=ast.Constant(value=ir.header_contains) if ir.header_contains else ast.Constant(value=None),
                    ),
                    ast.keyword(arg="index", value=ast.Constant(value=ir.index)),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, WebExtractTextSpec):
            call_node = ast.Call(
                func=ast.Name(id="webpage_text", ctx=ast.Load()),
                args=[ast.Name(id=ir.page_var, ctx=ast.Load())],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, WebDownloadMediaSpec):
            call_node = ast.Call(
                func=ast.Name(id="download_web_media", ctx=ast.Load()),
                args=[ast.Name(id=ir.page_var, ctx=ast.Load())],
                keywords=[
                    ast.keyword(arg="pattern", value=ast.Constant(value=ir.pattern)),
                    ast.keyword(arg="folder", value=ast.Constant(value=ir.folder_expr)),
                ],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
