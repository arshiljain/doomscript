"""
Unit tests for DoomScript Advanced Evolution:
- Phase 9: Pattern Matching & Destructuring
- Phase 10: Plain-English Native Test Runner
- Phase 11: Declarative CLI App Builder
- Phase 12: Background Concurrency & Timers
- Phase 13: Declarative Web Server & Route Handlers
"""

import pytest
from typer.testing import CliRunner
from doomscript.cli import app
from doomscript.compiler.engine import execute
from doomscript.runtime import _ROUTES


runner = CliRunner()


def test_destructuring_list_and_record():
    code = """
set my_list to [10, 20, 30]
unpack a, b, c from my_list

set my_user to {"username": "DoomGuy", "score": 9000}
unpack username, score from my_user

set nums to [1, 2, 3, 4]
first item into head, remaining items into tail from nums
"""
    ns = execute(code)
    assert ns["a"] == 10
    assert ns["b"] == 20
    assert ns["c"] == 30
    assert ns["username"] == "DoomGuy"
    assert ns["score"] == 9000
    assert ns["head"] == 1
    assert ns["tail"] == [2, 3, 4]


def test_pattern_matching():
    code = """
to categorize with role:
    match role:
        when "admin":
            return "Full Access"
        when "guest" or "anon":
            return "Read Only"
        when a number where it is greater than 100:
            return "VIP Number"
        when a list:
            return "Group"
        when over 50:
            return "High Value"
        otherwise:
            return "Standard"

set r1 to categorize("admin")
set r2 to categorize("guest")
set r3 to categorize("anon")
set r4 to categorize(150)
set r5 to categorize([1, 2])
set r6 to categorize(75)
set r7 to categorize("unknown")
"""
    ns = execute(code)
    assert ns["r1"] == "Full Access"
    assert ns["r2"] == "Read Only"
    assert ns["r3"] == "Read Only"
    assert ns["r4"] == "VIP Number"
    assert ns["r5"] == "Group"
    assert ns["r6"] == "High Value"
    assert ns["r7"] == "Standard"


def test_testing_expectations():
    code = """
test "sample expectations":
    set val to 50
    expect val to equal 50
    expect val to be a number
    expect val to be greater than 20
    expect val to be at least 50
    expect val to be less than 100

    set greeting to "Hello World"
    expect greeting to be text
    expect greeting to contain "World"

    set is_valid to true
    expect is_valid to be a boolean

    set items to [1, 2, 3]
    expect items to be a list
    expect items to contain 2

    set rec to {"a": 1}
    expect rec to be a record
"""
    ns = execute(code)
    assert ns["val"] == 50
    assert ns["greeting"] == "Hello World"


def test_doom_test_runner_cli(tmp_path):
    test_file = tmp_path / "test_example.doom"
    test_file.write_text("""
test "addition works":
    set a to 10
    set b to 20
    expect a + b to equal 30

test "string formatting":
    set name to "Doom"
    expect "Hello " + name to equal "Hello Doom"
""", encoding="utf-8")

    res = runner.invoke(app, ["test", str(test_file)])
    assert res.exit_code == 0
    assert "addition works" in res.output
    assert "string formatting" in res.output
    assert "All 2 test(s) passed" in res.output


def test_declarative_cli_builder():
    code = """
program description "Process analytics files"
option input_file with default "data.csv" and description "Path to CSV"
option max_rows as number with default 100 and description "Max rows to read"
flag dry_run with description "Simulate run without writing"
parse arguments into opts
"""
    # Execute with specific arguments by pre-setting sys.argv or invoking helper
    from doomscript import runtime
    runtime._CURRENT_CLI.options.clear()
    
    # Run the configuration code
    execute(code)
    # Parse mock arguments
    mock_args = ["--input-file", "sales.csv", "-m", "250", "--dry-run"]
    parsed = runtime.cli_parse_arguments(mock_args)
    assert parsed.input_file == "sales.csv"
    assert parsed.max_rows == 250.0
    assert parsed.dry_run is True


def test_background_concurrency_and_timers():
    code = """
to compute_square with n:
    return n * n

run in background compute_square(9) into task1
run in background compute_square(10) into task2

wait for task1 into res1
wait for task2 into res2

run in background compute_square(3) into t_a
run in background compute_square(4) into t_b
wait for all [t_a, t_b] into res_all

timeout 2 seconds for compute_square(7) into res_timed
"""
    ns = execute(code)
    assert ns["res1"] == 81
    assert ns["res2"] == 100
    assert ns["res_all"] == [9, 16]
    assert ns["res_timed"] == 49


def test_declarative_web_server_routes():
    code = """
on get "/api/v1/status":
    reply with json {"status": "ok", "service": "doomscript"}

on get "/welcome":
    reply with "<h1>Welcome</h1>"
"""
    execute(code)
    assert ("GET", "/api/v1/status") in _ROUTES
    assert ("GET", "/welcome") in _ROUTES

    handler_status = _ROUTES[("GET", "/api/v1/status")]
    res_status = handler_status()
    assert res_status == {"status": "ok", "service": "doomscript"}

    handler_welcome = _ROUTES[("GET", "/welcome")]
    res_welcome = handler_welcome()
    assert res_welcome == "<h1>Welcome</h1>"
