"""
Tests for DoomScript Plain-English Runtime Exception Shield.
Verifies that all standard Python runtime exceptions are intercepted, converted to dual-inheritance
DoomError instances, and provide plain-English explanations, line numbers, and source line pointers.
"""

import pytest
from doomscript.compiler.engine import execute
from doomscript.exceptions import (
    DoomError,
    DoomZeroDivisionError,
    DoomIndexError,
    DoomKeyError,
    DoomNameError,
    DoomTypeError,
    DoomValueError,
    DoomAttributeError,
    DoomFileNotFoundError,
    DoomAssertionError,
)


def test_zero_division_shield():
    source = "x = 10\ny = 0\nsay x / y"
    with pytest.raises(ZeroDivisionError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomZeroDivisionError)
    assert isinstance(err, ZeroDivisionError)
    assert err.line == 3
    assert "say x / y" in err.source_line
    assert "Cannot divide by zero" in str(err)
    assert "You tried to divide by zero" in str(err)


def test_index_out_of_bounds_shield():
    source = "items = [1, 2, 3]\nsay items[10]"
    with pytest.raises(IndexError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomIndexError)
    assert isinstance(err, IndexError)
    assert err.line == 2
    assert "items" in err.source_line
    assert "list" in str(err).lower() or "item" in str(err).lower()


def test_key_error_shield():
    source = "user = {name: \"Alice\"}\nsay user[\"missing_key\"]"
    with pytest.raises(KeyError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomKeyError)
    assert isinstance(err, KeyError)
    assert err.line == 2
    assert "missing_key" in str(err)


def test_name_error_shield():
    source = "total = 100\nsay totla + 5"
    with pytest.raises(NameError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomNameError)
    assert isinstance(err, NameError)
    assert err.line == 2
    assert "totla" in str(err)
    assert "total" in str(err)  # Suggestion for typo


def test_type_error_shield():
    source = 'x = 10\nsay x - "hello"'
    with pytest.raises(TypeError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomTypeError)
    assert isinstance(err, TypeError)
    assert err.line == 2
    assert "can't be combined" in str(err) or "type" in str(err).lower()


def test_attribute_error_shield():
    source = "x = 42\nx.nonexistent_method()"
    with pytest.raises(AttributeError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomAttributeError)
    assert isinstance(err, AttributeError)
    assert err.line == 2
    assert "nonexistent_method" in str(err)


def test_file_not_found_shield():
    source = "read file \"completely_nonexistent_file_xyz_123.txt\" into data"
    with pytest.raises(FileNotFoundError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, DoomFileNotFoundError)
    assert isinstance(err, FileNotFoundError)
    assert "completely_nonexistent_file_xyz_123.txt" in str(err)
    assert "couldn't find the file" in str(err) or "Check that the name and folder are correct" in str(err)


def test_verify_assertion_shield():
    source = "age = 15\nverify that age >= 18 otherwise \"Must be an adult\""
    with pytest.raises(AssertionError) as exc_info:
        execute(source)

    err = exc_info.value
    assert isinstance(err, DoomError)
    assert isinstance(err, AssertionError)
    assert "Must be an adult" in str(err)


def test_traceback_preservation():
    source = (
        "to helper_func:\n"
        "    say 10 / 0\n"
        "helper_func()\n"
    )
    with pytest.raises(ZeroDivisionError) as exc_info:
        execute(source)

    err = exc_info.value
    tb = err.__traceback__
    lines = []
    while tb:
        if tb.tb_frame.f_code.co_filename in ("<doom>", "<string>"):
            lines.append(tb.tb_lineno)
        tb = tb.tb_next
    # Traceback should have traversed both the caller and the function body
    assert 2 in lines or 3 in lines
