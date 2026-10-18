"""
Tests for compile-time caching, line mapping, error diagnostics,
core language extensions (sort/reverse/augmented assignments), and security hardening.
"""

import sys
import time
import ast
import pytest
from doomscript.compiler.engine import compile_to_ast, execute, get_parser
from doomscript.errors import find_closest_phrasings, translate_lark_error, translate_runtime_error, format_syntax_error
from doomscript.contracts import analyze_contracts
from doomscript import runtime, runtime_extended
from lark.exceptions import UnexpectedToken
from lark.lexer import Token


def test_parser_caching_perf():
    """Verify get_parser() is cached with lru_cache."""
    p1 = get_parser()  # Initial build
    t0 = time.perf_counter()
    for _ in range(50):
        p2 = get_parser()
    duration = time.perf_counter() - t0
    assert p1 is p2
    assert duration < 0.01  # 50 cached calls take under 10ms


def test_line_mapping_preserves_runtime_lineno():
    """Line numbers must survive normalization and point to correct source lines."""
    source = "say 10\nsay 20\nsay unknown_variable\n"
    py_ast = compile_to_ast(source)
    stmt_lines = [stmt.lineno for stmt in py_ast.body]
    assert stmt_lines == [1, 2, 3]

    try:
        execute(source)
    except NameError as e:
        tb = e.__traceback__
        matched_lineno = None
        while tb:
            if tb.tb_frame.f_code.co_filename == "<doom>":
                matched_lineno = tb.tb_lineno
            tb = tb.tb_next
        assert matched_lineno == 3


def test_runtime_error_translation():
    """Verify runtime errors are translated into beginner-friendly explanations."""
    err1 = NameError("name 'score' is not defined")
    assert translate_runtime_error(err1) == "I don't know what 'score' is. Did you set it earlier?"

    err1_internal = NameError("name '_var_count' is not defined")
    assert translate_runtime_error(err1_internal) == "I don't know what 'count' is. Did you set it earlier?"

    err2 = ZeroDivisionError("division by zero")
    assert "Cannot divide by zero" in translate_runtime_error(err2)

    err3 = IndexError("list index out of range")
    assert "List item out of reach" in translate_runtime_error(err3)

    err4 = KeyError("missing_field")
    assert "missing_field" in translate_runtime_error(err4)


def test_syntax_error_token_translation():
    """Verify \\n and EOF tokens are explained nicely and suggestions are gated."""
    tok = Token("_NEWLINE", "\n")
    err = UnexpectedToken(tok, expected=["_NEWLINE"])
    explanation, suggestion = translate_lark_error(err, "sort items")
    assert "incomplete or ended unexpectedly" in explanation
    assert "\\n" not in explanation

    # Irrelevant phrases should not suggest 'score is 100'
    close = find_closest_phrasings("zyxwvutsrqponm", n=1, cutoff=0.6)
    assert close == []


def test_list_sort_and_reverse():
    """Verify sort items, sort items ascending/descending, and reverse items."""
    env = execute("""
set items to [5, 2, 8, 1, 9]
sort items
say items
""")
    assert env["items"] == [1, 2, 5, 8, 9]

    env_desc = execute("""
set items to [5, 2, 8, 1, 9]
sort items descending
say items
""")
    assert env_desc["items"] == [9, 8, 5, 2, 1]

    env_rev = execute("""
set items to [1, 2, 3]
reverse items
say items
""")
    assert env_rev["items"] == [3, 2, 1]


def test_augmented_assignments_and_while_loop():
    """Verify +=, -=, *=, /=, %= and while loops."""
    env = execute("""
set x to 10
x += 5
x -= 3
x *= 2
x /= 4
x %= 5
""")
    assert env["x"] == 1.0 or env["x"] == 1

    loop_env = execute("""
set count to 5
set total to 0
while count > 0:
    total += count
    count -= 1
""")
    assert loop_env["total"] == 15
    assert loop_env["_var_count"] == 0 or loop_env.get("count") == 0


def test_contracts_eval_eliminated():
    """Verify contracts checker verifies static contracts without using eval."""
    source = """
verify that 5 > 10 otherwise "Math broken"
"""
    violations = analyze_contracts(source)
    assert len(violations) == 1
    assert "statically False" in violations[0].message


def test_subprocess_security_defaults():
    """Verify run_command defaults to shell=False with argument parsing."""
    import inspect
    sig = inspect.signature(runtime.run_command)
    assert sig.parameters["shell"].default is False

    sig_piped = inspect.signature(runtime_extended.run_command_piped)
    assert sig_piped.parameters["shell"].default is False

    # Execute a safe command
    output = runtime.run_command([sys.executable, "-c", "print('hello_safe')"])
    assert output == "hello_safe"


def test_friendly_syntax_error_diagnostics():
    """Verify common beginner syntax errors produce plain-English guidance and actionable suggestions."""
    # 1. Unclosed quote
    err_msg = format_syntax_error('say "Hello, world', Exception(), file_path="script.doom")
    assert "unclosed double quote" in err_msg.lower()
    assert 'say "Hello, world"' in err_msg

    # 2. Unclosed bracket
    err_bracket = format_syntax_error('items = [1, 2, 3', Exception(), file_path="script.doom")
    assert "unclosed bracket" in err_bracket.lower()

    # 3. Python-style 'def'
    err_def = format_syntax_error('def calculate(x, y):', Exception(), file_path="script.doom")
    assert "functions start with 'to'" in err_def.lower()
    assert "to calculate with x, y:" in err_def

    # 4. Python-style 'print'
    err_print = format_syntax_error('print("test")', Exception(), file_path="script.doom")
    assert "use 'say' instead of 'print'" in err_print.lower()

    # 5. Missing 'into' in read csv
    err_csv = format_syntax_error('read csv file "sales.csv"', Exception(), file_path="script.doom")
    assert "destination variable after 'into'" in err_csv.lower()

    # 6. Single '=' in if condition
    err_eq = format_syntax_error('if score = 100:', Exception(), file_path="script.doom")
    assert "single '=' is for setting a variable" in err_eq.lower()


def test_five_step_spreadsheet_to_report_task(tmp_path):
    """
    Core Mission Benchmark:
    Turn a messy spreadsheet into a clean report in plain English.
    """
    raw_csv = tmp_path / "sales_raw.csv"
    raw_csv.write_text("""customer,status,amount,region
Alice,paid,120,North
Bob,pending,45,West
Charlie,paid,350,North
Dana,refunded,90,South
Evan,paid,210,East
Fiona,paid,30,South
George,paid,540,North
""", encoding="utf-8")

    clean_csv = tmp_path / "clean_audit.csv"

    doom_code = f"""
# 1. Read messy transactions
read csv file "{str(raw_csv).replace('\\\\', '/')}" into orders

# 2. Filter valid paid transactions over $50
orders where status is "paid" into valid_orders
valid_orders where amount is over 50 into high_value

# 3. Sort by amount descending
sort high_value by amount descending

# 4. Save clean audit report
write csv high_value into file "{str(clean_csv).replace('\\\\', '/')}"

# 5. Summary metrics
set total_cleaned to count of high_value
set top_order to first item of high_value
"""
    env = execute(doom_code)

    assert env["total_cleaned"] == 4
    assert env["top_order"]["customer"] == "George"
    assert env["top_order"]["amount"] == 540 or env["top_order"]["amount"] == "540"

    # Verify written CSV
    clean_lines = clean_csv.read_text(encoding="utf-8").strip().splitlines()
    assert len(clean_lines) == 5  # header + 4 rows
    assert "George" in clean_lines[1]  # Highest first

