"""
DoomScript Exception Hierarchy
Provides structured, user-friendly exception types with file, line, and suggestion support.
"""

from typing import Optional


class DoomError(Exception):
    """Base exception for all DoomScript compiler and runtime errors."""

    def __init__(
        self,
        message: str,
        line: Optional[int] = None,
        column: Optional[int] = None,
        source_line: Optional[str] = None,
        suggestion: Optional[str] = None,
        file_path: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line
        self.suggestion = suggestion
        self.file_path = file_path

    def __str__(self) -> str:
        loc = ""
        if self.file_path or self.line:
            fp = self.file_path or "<source>"
            ln = f":{self.line}" if self.line is not None else ""
            col = f":{self.column}" if self.column is not None else ""
            loc = f" at {fp}{ln}{col}"
        msg = f"{self.message}{loc}"
        if self.source_line:
            prefix = "    "
            msg += f"\n{prefix}{self.source_line}"
            if self.column:
                pointer = " " * (self.column - 1) + "^"
                msg += f"\n{prefix}{pointer}"
        if self.suggestion:
            msg += f"\nDid you mean:\n    {self.suggestion}"
        return msg


class DoomSyntaxError(DoomError):
    """Raised when source code cannot be parsed or normalized."""
    pass


# Alias for readability and spec conformance
DoomScriptSyntaxError = DoomSyntaxError


class DoomIndentationError(DoomSyntaxError):
    """Raised when source code contains malformed indentation."""
    pass


class DoomScopeError(DoomError):
    """Raised when variable or pronoun scope resolution fails."""
    pass


class DoomAmbiguityError(DoomError):
    """Raised when a sentence has ambiguous meaning."""
    pass


class DoomCompilationError(DoomError):
    """Raised when compilation or AST export transformation fails."""
    pass


class DoomCompilerWarning(UserWarning):
    """Warning emitted during compilation or AST export transformations."""
    pass


class DoomAssertionError(DoomError, AssertionError):
    """Raised when a verification/assertion check fails."""
    pass


class DoomIndexError(DoomError, IndexError):
    """Raised when an indexing operation is out of bounds."""
    pass


class DoomTypeError(DoomError, TypeError):
    """Raised when an operation is performed on incompatible types."""
    pass


class DoomValueError(DoomError, ValueError):
    """Raised when an operation receives an invalid argument value."""
    pass


class DoomAttributeError(DoomError, AttributeError):
    """Raised when accessing a missing object attribute or record field."""
    pass

