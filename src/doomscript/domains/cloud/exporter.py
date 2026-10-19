"""Native Python AST Exporter for Cloud & Object Storage domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.cloud.spec import (
    CloudConnectSpec,
    CloudUploadSpec,
    CloudDownloadSpec,
    CloudListSpec,
    CloudSignedUrlSpec,
)


class CloudASTExporter(DomainASTExporter):
    """Translates Cloud Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"shutil", "os"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, CloudConnectSpec):
            call_node = ast.Call(
                func=ast.Name(id="connect_to_bucket", ctx=ast.Load()),
                args=[ast.Constant(value=ir.bucket_name)],
                keywords=[ast.keyword(arg="provider", value=ast.Constant(value=ir.provider))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, CloudListSpec):
            call_node = ast.Call(
                func=ast.Name(id="list_cloud_files", ctx=ast.Load()),
                args=[ast.Name(id=ir.bucket_var, ctx=ast.Load())],
                keywords=[ast.keyword(arg="pattern", value=ast.Constant(value=ir.pattern))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, CloudSignedUrlSpec):
            call_node = ast.Call(
                func=ast.Name(id="generate_cloud_signed_url", ctx=ast.Load()),
                args=[ast.Name(id=ir.bucket_var, ctx=ast.Load()), ast.Constant(value=ir.remote_path)],
                keywords=[ast.keyword(arg="expiry", value=ast.Constant(value=ir.expiry_sec))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        return imports, stmts
