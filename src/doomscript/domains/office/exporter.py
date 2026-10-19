"""Native Python AST Exporter for Office Automation domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.office.spec import (
    OfficeSpreadsheetSpec,
    OfficeAddRowSpec,
    OfficeSaveSpreadsheetSpec,
    OfficeDocumentSpec,
    OfficeAddHeadingSpec,
    OfficeAddParagraphSpec,
    OfficeSaveDocumentSpec,
)


class OfficeASTExporter(DomainASTExporter):
    """Translates Office Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"zipfile"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, OfficeSpreadsheetSpec):
            call_node = ast.Call(
                func=ast.Name(id="create_spreadsheet", ctx=ast.Load()),
                args=[],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, OfficeSaveSpreadsheetSpec):
            call_node = ast.Call(
                func=ast.Name(id="save_spreadsheet", ctx=ast.Load()),
                args=[ast.Name(id=ir.sheet_var, ctx=ast.Load()), ast.Constant(value=ir.path_expr)],
                keywords=[],
            )
            stmts.append(ast.Expr(value=call_node))

        elif isinstance(ir, OfficeDocumentSpec):
            call_node = ast.Call(
                func=ast.Name(id="create_word_document", ctx=ast.Load()),
                args=[],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, OfficeSaveDocumentSpec):
            call_node = ast.Call(
                func=ast.Name(id="save_word_document", ctx=ast.Load()),
                args=[ast.Name(id=ir.doc_var, ctx=ast.Load()), ast.Constant(value=ir.path_expr)],
                keywords=[],
            )
            stmts.append(ast.Expr(value=call_node))

        return imports, stmts
