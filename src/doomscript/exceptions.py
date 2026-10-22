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


class DoomZeroDivisionError(DoomError, ZeroDivisionError):
    """Raised when division or modulo by zero is attempted."""
    pass


class DoomKeyError(DoomError, KeyError):
    """Raised when a dictionary or collection key is not found."""
    pass


class DoomNameError(DoomError, NameError):
    """Raised when a variable or function name is undefined."""
    pass


class DoomFileNotFoundError(DoomError, FileNotFoundError):
    """Raised when a file or directory does not exist."""
    pass


class DoomPermissionError(DoomError, PermissionError):
    """Raised when permission is denied for a system or file operation."""
    pass


class DoomRuntimeError(DoomError, RuntimeError):
    """Raised when a general runtime failure occurs."""
    pass


class DoomTimeoutError(DoomError, TimeoutError):
    """Raised when an operation or polling guard exceeds its timeout deadline."""
    pass


class DoomRecursionError(DoomError, RecursionError):
    """Raised when maximum recursion depth is exceeded."""
    pass


class DoomLookupError(DoomError, LookupError):
    """Raised when a lookup operation fails."""
    pass


class DoomImportError(DoomError, ImportError):
    """Raised when an imported module or symbol cannot be found."""
    pass


class DoomOverflowError(DoomError, OverflowError):
    """Raised when a numeric calculation exceeds limits."""
    pass


EXCEPTION_CLASS_MAP = [
    (FileNotFoundError, DoomFileNotFoundError),
    (PermissionError, DoomPermissionError),
    (ZeroDivisionError, DoomZeroDivisionError),
    (IndexError, DoomIndexError),
    (KeyError, DoomKeyError),
    (NameError, DoomNameError),
    (TypeError, DoomTypeError),
    (ValueError, DoomValueError),
    (AttributeError, DoomAttributeError),
    (AssertionError, DoomAssertionError),
    (RecursionError, DoomRecursionError),
    (ImportError, DoomImportError),
    (OverflowError, DoomOverflowError),
    (LookupError, DoomLookupError),
    (TimeoutError, DoomTimeoutError),
    (RuntimeError, DoomRuntimeError),
]


def wrap_runtime_exception(
    exc: Exception,
    line: Optional[int] = None,
    column: Optional[int] = None,
    source_line: Optional[str] = None,
    file_path: Optional[str] = None,
) -> DoomError:
    """Wraps a Python runtime exception in a dual-inheritance DoomError preserving traceback and types."""
    if isinstance(exc, DoomError):
        return exc

    from doomscript.errors import translate_runtime_error
    msg = translate_runtime_error(exc)

    doom_cls = None
    for py_type, cls in EXCEPTION_CLASS_MAP:
        if isinstance(exc, py_type):
            doom_cls = cls
            break

    if doom_cls is None:
        exc_type = type(exc)
        doom_cls = type(f"Doom{exc_type.__name__}", (DoomError, exc_type), {})

    new_err = doom_cls(
        msg,
        line=line,
        column=column,
        source_line=source_line,
        file_path=file_path,
    )
    for attr in ("name", "filename", "errno", "strerror"):
        val = getattr(exc, attr, None)
        if val is not None:
            try:
                setattr(new_err, attr, val)
            except Exception:
                pass
    return new_err


