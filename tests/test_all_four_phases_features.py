import pytest
from doomscript.compiler.engine import execute


def test_pipe_chaining():
    code = """
set words to ["alpha", "beta", "gamma", "delta"]
words |> take 2 |> join with " / " into short_label
set result to short_label
"""
    globals_dict = execute(code)
    assert globals_dict["result"] == "alpha / beta"


def test_pipe_chaining_numeric():
    code = """
set nums to [10, 20, 30, 40, 50]
set result to nums |> drop 1 |> take 3 |> sorted descending
"""
    globals_dict = execute(code)
    assert globals_dict["result"] == [40, 30, 20]


def test_article_tolerance():
    code = """
set the total to 500
the subtotal is 250
add 50 to the total
set items to [1, 2, 3]
set c to the count of the items
set final_total to the total
"""
    globals_dict = execute(code)
    assert globals_dict["final_total"] == 550
    assert globals_dict["subtotal"] == 250
    assert globals_dict["c"] == 3


def test_currency_and_scale_literals():
    code = """
set price to $1,250.50
set cap to 2.5 million
set users to 500k
set rate to 15%
set discount to 10% of price
"""
    globals_dict = execute(code)
    assert globals_dict["price"] == 1250.50
    assert globals_dict["cap"] == 2500000.0
    assert globals_dict["users"] == 500000
    assert abs(globals_dict["rate"] - 0.15) < 1e-6
    assert abs(globals_dict["discount"] - 125.05) < 1e-4


def test_postfix_conditionals():
    code = """
set flag1 to false
set flag2 to true
set out1 to "unchanged"
set out2 to "unchanged"

set out1 to "triggered" unless flag1
set out2 to "triggered" only if flag2
"""
    globals_dict = execute(code)
    assert globals_dict["out1"] == "triggered"
    assert globals_dict["out2"] == "triggered"


def test_multi_subject_predicates():
    code = """
set a to 10
set b to 20
set c to 30
set x to 5
set y to 8

set all_pos to false
set none_z to false

if all of [a, b, c] are positive:
    set all_pos to true

if none of [x, y] are zero:
    set none_z to true
"""
    globals_dict = execute(code)
    assert globals_dict["all_pos"] is True
    assert globals_dict["none_z"] is True


def test_multi_field_sorting():
    code = """
set employees to [
    {"dept": "Eng", "tenure": 3, "name": "Alice"},
    {"dept": "Support", "tenure": 5, "name": "Bob"},
    {"dept": "Eng", "tenure": 8, "name": "Charlie"},
    {"dept": "Support", "tenure": 2, "name": "David"}
]
sort employees by dept ascending and tenure descending into ranked
"""
    globals_dict = execute(code)
    ranked = globals_dict["ranked"]
    assert ranked[0]["name"] == "Charlie"  # Eng, tenure 8
    assert ranked[1]["name"] == "Alice"    # Eng, tenure 3
    assert ranked[2]["name"] == "Bob"      # Support, tenure 5
    assert ranked[3]["name"] == "David"    # Support, tenure 2


def test_multi_field_grouping():
    code = """
set records to [
    {"region": "North", "quarter": "Q1", "revenue": 100},
    {"region": "North", "quarter": "Q1", "revenue": 150},
    {"region": "South", "quarter": "Q1", "revenue": 200}
]
group records by region and quarter calculating total revenue into summary
"""
    globals_dict = execute(code)
    summary = globals_dict["summary"]
    assert len(summary) == 2
    north = [r for r in summary if r["region"] == "North"][0]
    assert north["total_revenue"] == 250


def test_natural_field_access_with_of():
    code = """
a User has name, status
create a User with name "Alice", status "active" into u
set n to name of u
set s to status of u
"""
    globals_dict = execute(code)
    assert globals_dict["n"] == "Alice"
    assert globals_dict["s"] == "active"


def test_preposition_flexibility():
    code = """
set words to ["apple", "banana", "cherry", "date"]
take 2 from words into first_two
drop 2 from words into last_two
join first_two by " + " into joined
split "one,two,three" with "," into parts
"""
    globals_dict = execute(code)
    assert globals_dict["first_two"] == ["apple", "banana"]
    assert globals_dict["last_two"] == ["cherry", "date"]
    assert globals_dict["joined"] == "apple + banana"
    assert globals_dict["parts"] == ["one", "two", "three"]


def test_background_task_execution():
    code = """
to compute_val with x:
    give back x * 2

run in background compute_val(21) into job
wait for job into ans
"""
    globals_dict = execute(code)
    assert globals_dict["ans"] == 42

