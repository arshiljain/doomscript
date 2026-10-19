"""Math3D Domain AST Exporter for DoomScript."""

import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR


class Math3DASTExporter(DomainASTExporter):
    """Exports math3d domain calls to clean Python AST."""

    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        return set(), []
