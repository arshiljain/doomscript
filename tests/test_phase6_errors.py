"""
Phase 6 Tests: Friendly Error Experience
Tests plain-English error translations, line number tracking through normalization,
keyword and variable typo suggestions, and top 10 Python runtime exception translations.
"""

import pytest
from lark.exceptions import UnexpectedToken
from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.errors import (
    format_syntax_error,
    translate_runtime_error,
    translate_lark_error,
)
from doomscript.exceptions import DoomSyntaxError


def test_line_number_tracking_syntax_error():
    """Syntax error on line 5 of raw source with statement expansion points to line 5."""
    source = (
        "# Line 1: Header\n"
        "# Line 2: Comment\n"
        "x = 10 and then y = 20\n"
        "# Line 4: Comment\n"
        "sya \"broken line\"\n"
    )
    with pytest.raises(Exception) as exc_info:
        compile_to_ast(source)
    
    formatted = format_syntax_error(source, exc_info.value)
    # Must report line 5 in the error output, pointing to 'sya "broken line"'
    assert "   5 | sya \"broken line\"" in formatted or "5 | sya \"broken line\"" in formatted
    assert "Did you mean:" in formatted
    assert 'say "broken line"' in formatted


def test_line_number_tracking_runtime_error():
    """Runtime error on line 5 points to line 5 in AST / traceback."""
    source = (
        "# Line 1: Header\n"
        "x = 10 and then y = 20\n"
        "# Line 3: Comment\n"
        "# Line 4: Comment\n"
        "say undefined_variable_abc\n"
    )
    with pytest.raises(NameError) as exc_info:
        execute(source)
    
    tb = exc_info.value.__traceback__
    lineno = None
    while tb:
        if tb.tb_frame.f_code.co_filename in ("<doom>", "<string>"):
            lineno = tb.tb_lineno
        tb = tb.tb_next
    assert lineno == 5


def test_typo_keyword_sya():
    """Misspelling 'say' as 'sya' suggests 'say'."""
    source = 'sya "hello world"'
    with pytest.raises(Exception) as exc_info:
        compile_to_ast(source)
    
    formatted = format_syntax_error(source, exc_info.value)
    assert "Did you mean:" in formatted
    assert 'say "hello world"' in formatted


def test_typo_string_content_never_mutated():
    """String contents inside failing lines are preserved completely without corruption."""
    source = 'sya "world scroe lenght test"'
    with pytest.raises(Exception) as exc_info:
        compile_to_ast(source)

    formatted = format_syntax_error(source, exc_info.value)
    assert "Did you mean:" in formatted
    assert 'say "world scroe lenght test"' in formatted


def test_typo_keyword_prnt():
    """Typing 'prnt' suggests 'say'."""
    source = 'prnt "hello world"'
    with pytest.raises(Exception) as exc_info:
        compile_to_ast(source)
    
    formatted = format_syntax_error(source, exc_info.value)
    assert "Did you mean:" in formatted
    assert 'say "hello world"' in formatted


def test_typo_keyword_repeta():
    """Typing 'repeta' suggests 'repeat'."""
    source = "repeta 5 times:\n    say 1"
    with pytest.raises(Exception) as exc_info:
        compile_to_ast(source)
    
    formatted = format_syntax_error(source, exc_info.value)
    assert "Did you mean:" in formatted
    assert "repeat" in formatted


def test_typo_variable_suggestion():
    """Misspelled variable in scope suggests the closest match."""
    source = (
        "user_name = \"Alice\"\n"
        "say usre_name\n"
    )
    with pytest.raises(NameError) as exc_info:
        execute(source)
    
    msg = translate_runtime_error(exc_info.value)
    assert "I don't know what 'usre_name' is." in msg
    assert "Did you mean 'user_name'?" in msg


def test_name_error_without_suggestion():
    """Unknown variable with no similar match prompts defining it earlier."""
    err = NameError("name 'xyz_nonexistent_var' is not defined")
    msg = translate_runtime_error(err)
    assert "I don't know what 'xyz_nonexistent_var' is." in msg
    assert "Did you set it earlier?" in msg or "Did you define it earlier?" in msg


def test_type_error_unsupported_operand():
    """Combining incompatible types explains the type mismatch clearly."""
    try:
        _ = 10 + "hello"
    except TypeError as err:
        msg = translate_runtime_error(err)
        assert "You tried to" in msg
        assert "These types can't be combined this way." in msg


def test_index_error():
    """IndexError reports out of bounds clearly."""
    try:
        items = [1, 2, 3]
        _ = items[10]
    except IndexError as err:
        msg = translate_runtime_error(err)
        assert "You asked for item 10, but this list only has 3 items." in msg or "out of reach" in msg or "beyond" in msg


def test_key_error():
    """KeyError reports missing dictionary key."""
    try:
        user = {"name": "Alice"}
        _ = user["age"]
    except KeyError as err:
        msg = translate_runtime_error(err)
        assert "key called 'age'" in msg or "key 'age'" in msg


def test_zero_division_error():
    """ZeroDivisionError reports division by zero."""
    try:
        _ = 10 / 0
    except ZeroDivisionError as err:
        msg = translate_runtime_error(err)
        assert "You tried to divide by zero." in msg


def test_file_not_found_error():
    """FileNotFoundError reports missing file and path."""
    err = FileNotFoundError(2, "No such file or directory", "missing_data.csv")
    msg = translate_runtime_error(err)
    assert "I couldn't find the file 'missing_data.csv'." in msg
    assert "Check that the name and folder are correct." in msg


def test_attribute_error():
    """AttributeError reports property does not exist on type."""
    try:
        x = 10
        x.append(5)
    except AttributeError as err:
        msg = translate_runtime_error(err)
        assert "doesn't have a 'append' property" in msg or "has no property" in msg


def test_value_error_unpacking():
    """Unpacking value mismatch explains expected vs received."""
    try:
        a, b, c = [1, 2]
    except ValueError as err:
        msg = translate_runtime_error(err)
        assert "Tried to unpack 3 values, but got 2." in msg


def test_recursion_error():
    """RecursionError explains too many self-calls and base cases."""
    err = RecursionError("maximum recursion depth exceeded in comparison")
    msg = translate_runtime_error(err)
    assert "This function called itself too many times." in msg
    assert "Did you forget a base case?" in msg


def test_permission_error():
    """PermissionError explains lack of access permission."""
    err = PermissionError(13, "Permission denied", "protected_log.txt")
    msg = translate_runtime_error(err)
    assert "I don't have permission to access 'protected_log.txt'." in msg
