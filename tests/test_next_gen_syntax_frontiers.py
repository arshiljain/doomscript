"""
Tests for DoomScript Next-Generation Syntax Frontiers (1 to 6)
Frontier 1: Disjunctions (either...or, neither...nor, one of)
Frontier 2: Proportional Quantities & Percentage Arithmetic
Frontier 3: Full Expression / Statement Participle Parity
Frontier 4: Range Literals & Slicing Verb Ergonomics
Frontier 5: Single-Line Guard Clauses & Block Inlining
Frontier 6: Safe Null-Coalescing & Default Fallbacks
"""

import pytest
from doomscript.compiler.engine import execute, compile_to_ast
from doomscript.exceptions import DoomSyntaxError


class TestFrontier1Disjunctions:
    def test_either_or_positive(self):
        code = """
set role to "admin"
set granted to false
if role is either "admin" or "editor":
    set granted to true
"""
        env = execute(code)
        assert env["granted"] is True

    def test_either_or_negative(self):
        code = """
set role to "viewer"
set granted to false
if role is either "admin" or "editor":
    set granted to true
"""
        env = execute(code)
        assert env["granted"] is False

    def test_neither_nor(self):
        code = """
set status to "active"
set is_clean to false
if status is neither "banned" nor "suspended":
    set is_clean to true
"""
        env = execute(code)
        assert env["is_clean"] is True

    def test_neither_nor_blocked(self):
        code = """
set status to "banned"
set is_clean to true
if status is neither "banned" nor "suspended":
    set is_clean to true
else:
    set is_clean to false
"""
        env = execute(code)
        assert env["is_clean"] is False

    def test_disjunction_numeric(self):
        code = """
set code_val to 404
set is_err to false
if code_val is either 404 or 500:
    set is_err to true
"""
        env = execute(code)
        assert env["is_err"] is True


class TestFrontier2ProportionalQuantities:
    def test_increase_by_percent(self):
        code = """
set price to 100
increase price by 15%
"""
        env = execute(code)
        assert round(env["price"], 2) == 115.0

    def test_decrease_by_percent(self):
        code = """
set budget to 250
decrease budget by 20%
"""
        env = execute(code)
        assert round(env["budget"], 2) == 200.0

    def test_increase_by_percent_word(self):
        code = """
set salary to 50000
increase salary by 10 percent
"""
        env = execute(code)
        assert round(env["salary"], 2) == 55000.0

    def test_inline_percent_of(self):
        code = """
set subtotal to 80
set tax to 10% of subtotal
set total to subtotal + 10% of subtotal
"""
        env = execute(code)
        assert round(env["tax"], 2) == 8.0
        assert round(env["total"], 2) == 88.0


class TestFrontier3ParticipleExpressionParity:
    def test_joined_with(self):
        code = """
set words to ["alpha", "beta", "gamma"]
set csv_line to words joined with ", "
"""
        env = execute(code)
        assert env["csv_line"] == "alpha, beta, gamma"

    def test_trimmed(self):
        code = """
set raw_input to "   trimmed text   "
set clean_input to raw_input trimmed
"""
        env = execute(code)
        assert env["clean_input"] == "trimmed text"

    def test_uppercase_and_lowercase(self):
        code = """
set loud to "loud whisper" uppercase
set quiet to "QUIET SHOUT" lowercase
"""
        env = execute(code)
        assert env["loud"] == "LOUD WHISPER"
        assert env["quiet"] == "quiet shout"

    def test_reversed(self):
        code = """
set nums to [1, 2, 3, 4]
set back to nums reversed
"""
        env = execute(code)
        assert env["back"] == [4, 3, 2, 1]

    def test_sorted_by_descending(self):
        code = """
set students to [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 95},
    {"name": "Charlie", "score": 70}
]
set leaderboard to []
for each s in students sorted by score descending:
    add s["name"] to leaderboard
"""
        env = execute(code)
        assert env["leaderboard"] == ["Bob", "Alice", "Charlie"]

    def test_sorted_by_ascending(self):
        code = """
set students to [
    {"name": "Alice", "score": 85},
    {"name": "Bob", "score": 95},
    {"name": "Charlie", "score": 70}
]
set order_asc to []
for each s in students sorted by score ascending:
    add s["name"] to order_asc
"""
        env = execute(code)
        assert env["order_asc"] == ["Charlie", "Alice", "Bob"]


class TestFrontier4RangeLiteralsAndSlicing:
    def test_numeric_range_literal(self):
        code = """
set nums to [1 to 5]
"""
        env = execute(code)
        assert env["nums"] == [1, 2, 3, 4, 5]

    def test_char_range_literal(self):
        code = """
set letters to ["a" to "e"]
"""
        env = execute(code)
        assert env["letters"] == ["a", "b", "c", "d", "e"]

    def test_for_each_in_range(self):
        code = """
set collected to []
for each i in 1 to 4:
    add i to collected
"""
        env = execute(code)
        assert env["collected"] == [1, 2, 3, 4]

    def test_take_last(self):
        code = """
set items to [10, 20, 30, 40, 50]
take last 2 items from items into bottom_2
"""
        env = execute(code)
        assert env["bottom_2"] == [40, 50]

    def test_drop_last(self):
        code = """
set items to [10, 20, 30, 40, 50]
drop last 2 items from items into front_3
"""
        env = execute(code)
        assert env["front_3"] == [10, 20, 30]


class TestFrontier5SingleLineGuardsAndBlockInlining:
    def test_single_line_if(self):
        code = """
set balance to 0
set stopped to false
if balance is 0: set stopped to true
"""
        env = execute(code)
        assert env["stopped"] is True

    def test_single_line_for_loop(self):
        code = """
set items to [2, 4, 6]
set total to 0
for each item in items: set total to total + item
"""
        env = execute(code)
        assert env["total"] == 12

    def test_single_line_while_loop(self):
        code = """
set counter to 0
while counter < 5: set counter to counter + 1
"""
        env = execute(code)
        assert env["counter"] == 5


class TestFrontier6SafeNullCoalescingAndQuoteSafety:
    def test_possessive_otherwise(self):
        code = """
set user to {"name": "Alice", "nickname": None}
set display_name to user's nickname otherwise "Guest"
"""
        env = execute(code)
        assert env["display_name"] == "Guest"

    def test_possessive_default(self):
        code = """
set config to {"host": "localhost"}
set port to config's port default 8080
"""
        env = execute(code)
        assert env["port"] == 8080

    def test_dot_access_default(self):
        code = """
set config to {"host": "localhost"}
set port to config.port default 3000
"""
        env = execute(code)
        assert env["port"] == 3000

    def test_standalone_coalesce(self):
        code = """
set empty_val to None
set final_val to empty_val otherwise "Fallback"
"""
        env = execute(code)
        assert env["final_val"] == "Fallback"

    def test_possessive_apostrophe_no_unclosed_quote_error(self):
        bad_code = """
set val to user's nickname ???
"""
        with pytest.raises(DoomSyntaxError) as exc_info:
            compile_to_ast(bad_code)
        err_msg = str(exc_info.value)
        assert "unclosed single quote" not in err_msg.lower()
        assert "???" in err_msg or "punctuation" in err_msg.lower() or "character '?'" in err_msg.lower()
