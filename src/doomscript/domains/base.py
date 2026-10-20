"""Base contracts and interfaces for DoomScript domain extension architecture."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple
import ast
from doomscript.domains.matcher import VerbSpec


class DomainIR(ABC):
    """Abstract base class for all domain specification intermediate representations."""

    @abstractmethod
    def validate(self) -> List[str]:
        """Returns a list of semantic validation errors if any, or empty list if valid."""
        pass


class DomainParser(ABC):
    """Independent domain parser operating on source lines, phrases, or blocks."""

    @abstractmethod
    def parse_inspect(self, line: str, line_no: int) -> Optional[DomainIR]:
        """Parses a Level 1 inspect/explore statement."""
        pass

    @abstractmethod
    def parse_operation(self, line: str, line_no: int) -> Optional[ast.stmt]:
        """Parses a Level 2 single operation statement."""
        pass

    @abstractmethod
    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int
    ) -> Tuple[DomainIR, str]:
        """Parses a Level 3 declarative block into a DomainIR and target variable name."""
        pass


class DomainRuntime(ABC):
    """Execution engine for domain operations and workflows."""

    @abstractmethod
    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        """Executes a domain IR object in the provided execution scope."""
        pass


class DomainASTExporter(ABC):
    """Translates DomainIR into safe, native Python AST statements."""

    @abstractmethod
    def to_ast(
        self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None
    ) -> Tuple[Set[str], List[ast.stmt]]:
        """Translates DomainIR into imported module/symbol names and native Python AST statements."""
        pass


class DomainContract(ABC):
    """Formal contract required for all DoomScript domain packs."""

    name: str
    aliases: List[str]
    parser: DomainParser
    runtime: DomainRuntime
    exporter: DomainASTExporter
    verbs: List[Any] = []
    blocks: List[Any] = []
    capabilities: List[str] = []
    optional_dependencies: Dict[str, str] = {}

    def can_handle_line(self, line: str) -> bool:
        """Determines if this domain can parse or handle a given standalone line."""
        if hasattr(self, "parser") and self.parser:
            try:
                if hasattr(self.parser, "parse_inspect") and self.parser.parse_inspect(line, 0) is not None:
                    return True
                if hasattr(self.parser, "parse_operation") and self.parser.parse_operation(line, 0) is not None:
                    return True
            except Exception:
                pass
        if hasattr(self, "verbs") and self.verbs:
            return any(v.matches(line) for v in self.verbs if hasattr(v, "matches"))
        return False

    def can_handle_block(self, header: str) -> bool:
        """Determines if this domain can parse or handle a given block header."""
        if hasattr(self, "blocks") and self.blocks:
            return any(b.matches(header) for b in self.blocks if hasattr(b, "matches"))
        return False
