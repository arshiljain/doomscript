"""Biomechanics Domain AST Exporter."""
import ast
from typing import Optional, Set, List, Tuple, Any
from doomscript.domains.base import DomainASTExporter, DomainIR

class BiomechanicsASTExporter(DomainASTExporter):
    def to_ast(self, ir: DomainIR, var_name: str, scope: Optional[dict] = None) -> Tuple[Set[str], List[ast.stmt]]:
        return set(), []
