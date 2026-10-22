"""AST Exporter for electromagnetics domain."""
import ast
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import DomainASTExporter, DomainIR

class ElectromagneticsASTExporter(DomainASTExporter):
    def to_ast(self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None) -> Tuple[Set[str], List[ast.stmt]]:
        return set(), []
