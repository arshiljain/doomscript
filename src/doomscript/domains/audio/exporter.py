"""Native Python AST Exporter for Audio & Sound domain."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR
from doomscript.domains.audio.spec import (
    AudioLoadSpec,
    AudioCreateSpec,
    AudioTrimSpec,
    AudioFadeSpec,
    AudioVolumeSpec,
    AudioCombineSpec,
    AudioSaveSpec,
)


class AudioASTExporter(DomainASTExporter):
    """Translates Audio Domain IR into Python AST statements."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        imports: Set[str] = {"wave"}
        stmts: List[ast.stmt] = []

        if isinstance(ir, AudioLoadSpec):
            call_node = ast.Call(
                func=ast.Name(id="load_audio", ctx=ast.Load()),
                args=[ast.Constant(value=ir.path_expr)],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, AudioCreateSpec):
            call_node = ast.Call(
                func=ast.Name(id="create_blank_audio", ctx=ast.Load()),
                args=[ast.Constant(value=ir.duration)],
                keywords=[ast.keyword(arg="sample_rate", value=ast.Constant(value=ir.sample_rate))],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, AudioTrimSpec):
            call_node = ast.Call(
                func=ast.Name(id="trim_audio", ctx=ast.Load()),
                args=[
                    ast.Name(id=ir.audio_var, ctx=ast.Load()),
                    ast.Constant(value=ir.start_sec),
                    ast.Constant(value=ir.end_sec),
                ],
                keywords=[],
            )
            stmts.append(ast.Assign(targets=[ast.Name(id=var_name, ctx=ast.Store())], value=call_node))

        elif isinstance(ir, AudioSaveSpec):
            call_node = ast.Call(
                func=ast.Name(id="save_audio", ctx=ast.Load()),
                args=[ast.Name(id=ir.audio_var, ctx=ast.Load()), ast.Constant(value=ir.path_expr)],
                keywords=[],
            )
            stmts.append(ast.Expr(value=call_node))

        return imports, stmts
