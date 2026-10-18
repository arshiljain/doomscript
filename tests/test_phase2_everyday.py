"""
Tests for Phase 2: Everyday Programming in English
Comprehensive test coverage for I/O, list operations, data queries, loops,
functions with defaults/named args, error handling, stdlib helpers, and Python interop.
"""

import textwrap
import pytest
from pathlib import Path
from doomscript.compiler.engine import execute
from doomscript.runtime import Record


def run(source: str):
    env = {}
    execute(textwrap.dedent(source).strip(), custom_globals=env)
    return env


def test_say_multiple_parts_and_interpolation(capsys):
    code = """
    name = "DoomSlayer"
    level = 99
    say "Player:", name, "Level:", level
    greeting = "Welcome {name}, rank {level}!"
    say greeting
    """
    env = run(code)
    out = capsys.readouterr().out
    assert "Player: DoomSlayer Level: 99" in out
    assert "Welcome DoomSlayer, rank 99!" in out
    assert env["greeting"] == "Welcome DoomSlayer, rank 99!"


def test_list_creation_and_manipulation():
    code = """
    numbers = a list of 10, 20, 30
    empty_items = an empty list
    add 40 to numbers
    insert 5 at 1 in numbers
    remove 20 from numbers
    
    second = item 2 of numbers
    first_two = first 2 items of numbers
    last_two = last 2 items of numbers
    is_empty_flag = empty_items is empty
    contains_flag = numbers contains 30
    """
    env = run(code)
    # numbers after: insert 5 at 1 -> [5, 10, 20, 30, 40], remove 20 -> [5, 10, 30, 40]
    assert env["numbers"] == [5, 10, 30, 40]
    assert env["second"] == 10
    assert env["first_two"] == [5, 10]
    assert env["last_two"] == [30, 40]
    assert env["is_empty_flag"] is True
    assert env["contains_flag"] is True


def test_list_transforms_sorted_reversed_unique():
    code = """
    raw = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    s = sorted raw
    r = reversed raw
    u = unique items of raw
    """
    env = run(code)
    assert env["s"] == [1, 1, 2, 3, 4, 5, 5, 6, 9]
    assert env["r"] == [5, 6, 2, 9, 5, 1, 4, 1, 3]
    assert env["u"] == [3, 1, 4, 5, 9, 2, 6]


def test_data_operations_comprehension_and_filter():
    code = """
    people = [
        {name: "Alice", age: 25},
        {name: "Bob", age: 17},
        {name: "Charlie", age: 30}
    ]
    
    names is the name of each person in people
    adults = people where age is over 18 into adults_list
    """
    env = run(code)
    assert env["names"] == ["Alice", "Bob", "Charlie"]
    assert len(env["adults_list"]) == 2
    assert env["adults_list"][0]["name"] == "Alice"
    assert env["adults_list"][1]["name"] == "Charlie"


def test_data_operations_group_and_sort():
    code = """
    orders = [
        {customer: "Alice", amount: 100},
        {customer: "Bob", amount: 200},
        {customer: "Alice", amount: 50}
    ]
    
    group orders by customer into customer_orders
    sort orders by amount descending
    """
    env = run(code)
    assert len(env["customer_orders"]["Alice"]) == 2
    assert len(env["customer_orders"]["Bob"]) == 1
    assert env["orders"][0]["amount"] == 200
    assert env["orders"][1]["amount"] == 100
    assert env["orders"][2]["amount"] == 50


def test_field_aggregates():
    code = """
    orders = [
        {price: 10, count: 2},
        {price: 25, count: 1},
        {price: 40, count: 5}
    ]
    
    tot = total of price in orders
    avg = average of price in orders
    hi = highest price in orders
    lo = lowest price in orders
    """
    env = run(code)
    assert env["tot"] == 75
    assert env["avg"] == 25.0
    assert env["hi"] == 40
    assert env["lo"] == 10


def test_conditions_between_one_of_and_types():
    code = """
    val = 15
    text_val = "doom"
    
    b_true = val is between 10 and 20
    b_false = val is between 20 and 30
    
    options = [5, 10, 15, 20]
    one_of_true = val is one of options
    one_of_false = 99 is one of options
    
    num_check = val is a number
    text_check = text_val is text
    """
    env = run(code)
    assert env["b_true"] is True
    assert env["b_false"] is False
    assert env["one_of_true"] is True
    assert env["one_of_false"] is False
    assert env["num_check"] is True
    assert env["text_check"] is True


def test_if_elif_else_and_unless():
    code = """
    score = 85
    grade = ""
    
    if score is at least 90
        grade = "A"
    otherwise if score is at least 80
        grade = "B"
    otherwise
        grade = "C"
        
    flag = false
    status = "INIT"
    unless flag
        status = "FLAG_IS_FALSE"
        
    action = "STANDBY"
    action = "RUN" unless flag
    """
    env = run(code)
    assert env["grade"] == "B"
    assert env["status"] == "FLAG_IS_FALSE"
    assert env["action"] == "RUN"


def test_loops_range_and_where_and_controls():
    code = """
    total = 0
    repeat with i from 1 to 5
        total = total + i
        
    odd_total = 0
    repeat with j from 1 to 9 by 2
        odd_total = odd_total + j
        
    filtered_items = []
    items = [5, 12, 8, 20, 3]
    for each num in items where num is over 10
        add num to filtered_items
        
    stopped_at = 0
    repeat with k from 1 to 10
        if k equals 4
            stop
        stopped_at = k
        
    skipped_count = 0
    repeat with m from 1 to 5
        if m equals 3
            skip
        skipped_count = skipped_count + 1
    """
    env = run(code)
    assert env["total"] == 15  # 1+2+3+4+5
    assert env["odd_total"] == 25  # 1+3+5+7+9
    assert env["filtered_items"] == [12, 20]
    assert env["stopped_at"] == 3
    assert env["skipped_count"] == 4


def test_functions_defaults_and_expressions():
    code = """
    to greet person with greeting "Hello"
        return "{greeting}, {person}!"
        
    to tax on price
        return price * 0.1
        
    msg1 = greet("Alice")
    msg2 = greet("Bob", greeting="Greetings")
    
    subtotal = 100
    tax_amount is the result of tax on subtotal
    """
    env = run(code)
    assert env["msg1"] == "Hello, Alice!"
    assert env["msg2"] == "Greetings, Bob!"
    assert env["tax_amount"] == 10.0


def test_try_if_fails_always():
    code = """
    caught = false
    always_ran = false
    
    try
        x = 10 / 0
    if that fails as problem
        caught = true
    always
        always_ran = true
    """
    env = run(code)
    assert env["caught"] is True
    assert env["always_ran"] is True


def test_csv_and_json_helpers(tmp_path):
    csv_file = str(tmp_path / "test.csv").replace("\\", "/")
    code = f"""
    rows = [
        {{name: "Alice", score: "95"}},
        {{name: "Bob", score: "88"}}
    ]
    write csv rows into file "{csv_file}"
    append csv {{name: "Charlie", score: "72"}} to file "{csv_file}"
    
    read csv file "{csv_file}" into loaded_rows
    
    raw_json = '{{"server": "DoomNode", "port": 8080}}'
    parse json raw_json into config
    convert config to json into exported_json
    """
    env = run(code)
    assert len(env["loaded_rows"]) == 3
    assert env["loaded_rows"][0]["name"] == "Alice"
    assert env["loaded_rows"][2]["name"] == "Charlie"
    assert env["config"]["server"] == "DoomNode"
    assert "DoomNode" in env["exported_json"]


def test_system_and_math_helpers():
    code = """
    round 3.14159 to 2 places into pi
    abs_val = absolute value of -42
    sq_val = square root of 25
    t = today
    n = now
    get environment variable "OS" into os_val
    run command "python --version" into py_ver
    """
    env = run(code)
    assert env["pi"] == 3.14
    assert env["abs_val"] == 42
    assert env["sq_val"] == 5.0
    assert len(env["t"]) == 10  # YYYY-MM-DD
    assert len(env["n"]) >= 19  # YYYY-MM-DD HH:MM:SS
    assert "Python" in env["py_ver"]


def test_python_interop():
    code = """
    use python module math
    from python module math use ceil, floor
    
    c = ceil(4.2)
    f = floor(4.8)
    pi_const = math.pi
    """
    env = run(code)
    assert env["c"] == 5
    assert env["f"] == 4
    assert env["pi_const"] > 3.14
