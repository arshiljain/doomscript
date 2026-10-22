import pytest
from pathlib import Path
from doomscript.compiler.engine import execute
from doomscript.tester import extract_test_blocks, run_doom_tests
from doomscript.core.record import Record
from doomscript.exceptions import DoomScriptSyntaxError


def test_item1_quicksort_recursive_scope():
    code = """
to quicksort with arr:
    if arr's length <= 1:
        return arr
    set pivot to arr[0]
    set left to []
    set right to []
    for each x in arr[1:]:
        if x < pivot:
            add x to left
        else:
            add x to right
    return quicksort(left) + [pivot] + quicksort(right)

set numbers to [45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 62, 32]
set sorted_numbers to quicksort(numbers)
"""
    env = execute(code)
    expected = sorted([45, 12, 85, 32, 89, 39, 69, 44, 42, 1, 62, 32])
    assert env["sorted_numbers"] == expected

    # Also test nested function appending to outer list
    nested_code = """
to outer:
    set acc to []
    to inner with x:
        add x to acc
    call inner(10)
    call inner(20)
    return acc

set res to outer()
"""
    env2 = execute(nested_code)
    assert env2["res"] == [10, 20]


def test_item2_tester_file_visibility(tmp_path):
    doom_test_file = tmp_path / "sample_visible_test.doom"
    doom_test_file.write_text(
        """to double_val with n:
    return n * 2

a Config has timeout

test "can call file helper":
    set res to double_val(21)
    expect res to be 42

test "can use file record":
    create a Config with timeout 30 into cfg
    expect cfg's timeout to be 30
""",
        encoding="utf-8",
    )

    preamble, blocks = extract_test_blocks(doom_test_file.read_text(encoding="utf-8"))
    assert "to double_val" in preamble
    assert "a Config has timeout" in preamble
    assert len(blocks) == 2

    passed = run_doom_tests(doom_test_file)
    assert passed is True


def test_item3_group_by_natural_aggregations():
    pipeline_code = """
use data

sales_data = [
    {"region": "North", "amount": 100},
    {"region": "North", "amount": 200},
    {"region": "South", "amount": 300},
    {"region": "South", "amount": 500}
]

pipeline "summary_pipe" from sales_data into summary:
    group by region:
        calculate avg_amt as average of amount
        calculate max_amt as maximum of amount
        calculate min_amt as minimum of amount
        calculate total_amt as sum of amount
        calculate cnt as count
"""
    env = execute(pipeline_code)
    assert "summary" in env
    by_region = {r.region: r for r in env["summary"]}
    assert by_region["North"].avg_amt == 150.0
    assert by_region["North"].max_amt == 200
    assert by_region["North"].min_amt == 100
    assert by_region["North"].total_amt == 300
    assert by_region["North"].cnt == 2

    assert by_region["South"].avg_amt == 400.0
    assert by_region["South"].max_amt == 500
    assert by_region["South"].min_amt == 300
    assert by_region["South"].total_amt == 800
    assert by_region["South"].cnt == 2


def test_item3_group_by_unknown_aggregation_fails():
    bad_code = """
use data
raw = [{"k": 1, "v": 10}]
pipeline "bad" from raw into res:
    group by k:
        calculate x as foobar of v
"""
    with pytest.raises((DoomScriptSyntaxError, ValueError)):
        execute(bad_code)


def test_item4_sorted_and_reversed_rewrites():
    code = """
set nums to [3, 1, 4, 1, 5]
set rev_nums to nums reversed
set s_nums to [5, 2, 8]
reverse s_nums
"""
    env = execute(code)
    assert env["rev_nums"] == [5, 1, 4, 1, 3]
    assert env["s_nums"] == [8, 2, 5]


def test_item5_contract_require_ensure_otherwise():
    code = """
set x to 10
require that x > 5 otherwise "x must be greater than 5"
ensure that x is 10 otherwise "x must remain 10"
require x is positive otherwise "x must be positive"
"""
    env = execute(code)
    assert env["x"] == 10

    fail_code = """
set y to 2
require that y > 10 otherwise "y too small"
"""
    with pytest.raises(AssertionError, match="y too small"):
        execute(fail_code)


def test_item6_string_interpolation_expressions():
    code = """
set c to 21
to double with n:
    return n * 2

a User has name, age
create a User with name "Alice", age 30 into u

set msg1 to "Result is {c * 2}"
set msg2 to "Calling {double(c)}"
set msg3 to "User {u's name} is {u's age} years old"
"""
    env = execute(code)
    assert env["msg1"] == "Result is 42"
    assert env["msg2"] == "Calling 42"
    assert env["msg3"] == "User Alice is 30 years old"


def test_item7_reverse_string_palindrome():
    code = """
set word to "racecar"
set rev_word to reversed of word
set is_palindrome to (word is rev_word)

set hello to "hello"
set rev_hello to reversed of hello
"""
    env = execute(code)
    assert isinstance(env["rev_word"], str)
    assert env["rev_word"] == "racecar"
    assert env["is_palindrome"] is True
    assert env["rev_hello"] == "olleh"


def test_item8_mod_and_indexed_is_in():
    code = """
set a to 10
set b to 7
set n to 5
set mod_res to (a + b) mod n

set s to "cat"
set found_c to (s[0] is in "aeiou")
set found_a to (s[1] is in "aeiou")
set not_in to (s[0] is not in "aeiou")
"""
    env = execute(code)
    assert env["mod_res"] == 2
    assert env["found_c"] is False
    assert env["found_a"] is True
    assert env["not_in"] is True


def test_item9_indexing_harmony():
    code = """
set items to ["first", "second", "third"]
set item_0 to item 0 of items
set item_1 to item 1 of items
set direct_0 to items[0]

insert "zero" at 0 in items
insert "one" at 1 in items
"""
    env = execute(code)
    assert env["item_0"] == "first"
    assert env["item_1"] == "first"
    assert env["direct_0"] == "first"
    assert env["items"][0] == "one" or env["items"][0] == "zero"


def test_item10_data_pipeline_record_attribute_access():
    code = """
use data

sales = [
    {"region": "North", "amount": 100},
    {"region": "South", "amount": 200}
]

pipeline "p" from sales into res:
    sort by amount descending

set first_region to res[0].region
set first_amount to res[0].amount
"""
    env = execute(code)
    assert env["first_region"] == "South"
    assert env["first_amount"] == 200
    assert isinstance(env["res"][0], Record)


def test_item11_dict_keys_values_entries_and_loop():
    code = """
set user_scores to {"Alice": 95, "Bob": 88}
set my_keys to keys of user_scores
set my_vals to values of user_scores
set my_pairs to entries of user_scores

set collected to []
for each k, v in user_scores:
    add "{k}={v}" to collected
"""
    env = execute(code)
    assert "Alice" in env["my_keys"] and "Bob" in env["my_keys"]
    assert 95 in env["my_vals"] and 88 in env["my_vals"]
    assert isinstance(env["my_pairs"], list)
    assert ("Alice", 95) in env["my_pairs"] or ["Alice", 95] in env["my_pairs"]
    assert "Alice=95" in env["collected"]
    assert "Bob=88" in env["collected"]


def test_item12_reserved_words_as_variables():
    code = """
set first to 10
set last to 20
set log to "test_log"
log = 50

set total to first + last + log
"""
    env = execute(code)
    assert env["first"] == 10
    assert env["last"] == 20
    assert env["log"] == 50
    assert env["total"] == 80
