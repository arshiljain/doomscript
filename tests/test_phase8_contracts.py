"""
Unit tests for DoomScript Phase 8: English Type Contracts & Gradual Safety.
Verifies type comparison operators, require/ensure contracts, typed function parameters,
typed variable assignments, and static analysis with --strict mode.
"""

import pytest
from typer.testing import CliRunner
from doomscript.cli import app
from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.contracts import analyze_contracts, ContractViolation


runner = CliRunner()


def test_type_comparisons():
    code = """
set a to 42
set b to "Doom"
set c to true
set d to [1, 2, 3]
set e to {"name": "Slayer"}

verify that a is a number otherwise "a is number"
verify that a is not text otherwise "a not text"
verify that b is text otherwise "b is text"
verify that b is not a number otherwise "b not number"
verify that c is a boolean otherwise "c is boolean"
verify that c is not a list otherwise "c not list"
verify that d is a list otherwise "d is list"
verify that d is not a record otherwise "d not record"
verify that e is a record otherwise "e is record"
verify that e is not a boolean otherwise "e not bool"
"""
    tree = compile_to_ast(code)
    ns = execute(tree)
    assert ns["a"] == 42
    assert ns["b"] == "Doom"


def test_require_and_ensure():
    code = """
to safe_divide with a, b:
    require b is not 0 otherwise "Denominator cannot be zero"
    set res to a / b
    ensure res is a number
    return res

set ok to safe_divide(10, 2)
"""
    tree = compile_to_ast(code)
    ns = execute(tree)
    assert ns["ok"] == 5.0

    fail_code = """
to safe_divide with a, b:
    require b is not 0 otherwise "Denominator cannot be zero"
    return a / b

set bad to safe_divide(10, 0)
"""
    with pytest.raises(AssertionError) as excinfo:
        execute(compile_to_ast(fail_code))
    assert "Denominator cannot be zero" in str(excinfo.value)


def test_require_default_message():
    code = """
set val to -5
require val is greater than 0
"""
    with pytest.raises(AssertionError) as excinfo:
        execute(compile_to_ast(code))
    assert "Requirement failed" in str(excinfo.value)


def test_ensure_default_message():
    code = """
set val to -10
ensure val is at least 0
"""
    with pytest.raises(AssertionError) as excinfo:
        execute(compile_to_ast(code))
    assert "Postcondition failed" in str(excinfo.value)


def test_typed_function_parameters():
    code = """
to compute_discount with price as number, rate as number:
    return price * rate

to greet_user with name as text, is_admin as boolean:
    if is_admin:
        return "Admin: " + name
    else:
        return "User: " + name

set disc to compute_discount(100, 0.2)
set greeting to greet_user("Alice", true)
"""
    tree = compile_to_ast(code)
    ns = execute(tree)
    assert ns["disc"] == 20.0
    assert ns["greeting"] == "Admin: Alice"

    fail_code = """
to compute_discount with price as number, rate as number:
    return price * rate

set bad to compute_discount("invalid", 0.2)
"""
    with pytest.raises(AssertionError) as excinfo:
        execute(compile_to_ast(fail_code))
    assert "Argument 'price' must be number" in str(excinfo.value)


def test_typed_variable_assignment():
    code = """
set score as number to 95
set title as text to "Champion"
"""
    tree = compile_to_ast(code)
    ns = execute(tree)
    assert ns["score"] == 95
    assert ns["title"] == "Champion"

    fail_code = """
set score as number to "not a number"
"""
    with pytest.raises(AssertionError) as excinfo:
        execute(compile_to_ast(fail_code))
    assert "Variable 'score' must be number" in str(excinfo.value)


def test_static_contract_analyzer_clean():
    clean_code = """
to add_bonus with salary as number, bonus as number:
    require salary is greater than 0
    return salary + bonus

set total to add_bonus(50000, 5000)
"""
    violations = analyze_contracts(clean_code)
    assert len(violations) == 0


def test_static_contract_analyzer_mismatch():
    mismatch_code = """
to add_bonus with salary as number, bonus as number:
    return salary + bonus

set total to add_bonus("invalid_salary", 5000)
"""
    violations = analyze_contracts(mismatch_code)
    assert len(violations) >= 1
    assert any("salary" in v.message and "number" in v.message for v in violations)


def test_cli_check_strict(tmp_path):
    ok_file = tmp_path / "ok.doom"
    ok_file.write_text("""
to double with x as number:
    return x * 2

set res to double(10)
""", encoding="utf-8")

    res = runner.invoke(app, ["check", str(ok_file), "--strict"])
    assert res.exit_code == 0
    assert "Strict Type & Contract Checks Passed" in res.output

    bad_file = tmp_path / "bad.doom"
    bad_file.write_text("""
to double with x as number:
    return x * 2

set res to double("hello")
""", encoding="utf-8")

    res_bad = runner.invoke(app, ["check", str(bad_file), "--strict"])
    assert res_bad.exit_code == 1
    assert "Strict Error" in res_bad.output
