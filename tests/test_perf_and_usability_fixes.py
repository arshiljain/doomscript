"""
Tests for compiler performance optimization, indexing error handling,
global variable scope in functions, keyword collisions, and usability fixes.
"""

import re
import time
import pytest
from doomscript.compiler.engine import compile_to_ast, execute, get_parser
from doomscript.exceptions import DoomIndexError, DoomNameError, DoomSyntaxError
from doomscript.errors import format_syntax_error, find_closest_phrasings, translate_runtime_error


def test_lark_and_regex_cache_speed():
    """Verify Lark cache=True and expanded re._MAXCACHE provide blazing compilation speed."""
    assert re._MAXCACHE >= 8192

    # Warm parse
    compile_to_ast("say 10\nset x to 5\n")

    # Second parse must be sub-50ms
    t0 = time.perf_counter()
    compile_to_ast("say 20\nset y to 10\n")
    duration = time.perf_counter() - t0
    assert duration < 0.05, f"Expected < 50ms, took {duration*1000:.2f}ms"


def test_item_of_indexing_errors_not_silent_none():
    """Verify item 10 of nums raises clear DoomIndexError instead of returning None silently."""
    # Out of bounds index
    with pytest.raises(DoomIndexError) as exc_info:
        execute("""
nums = [1, 2, 3]
say item 10 of nums
""")
    assert "You asked for item 10" in str(exc_info.value)
    assert "only has 3 items" in str(exc_info.value)

    # 1-based indexing note on 0 index
    with pytest.raises(DoomIndexError) as exc_info_zero:
        execute("""
nums = [1, 2, 3]
say item 0 of nums
""")
    assert "1-based" in str(exc_info_zero.value)


def test_global_variable_modification_in_functions():
    """Verify global, modify global, and global variable allow modifying outer scope."""
    env = execute("""
counter = 0
to inc:
    global counter
    counter = counter + 1

to inc_by_ten:
    modify global counter
    set counter to counter + 10

inc()
inc()
inc_by_ten()
""")
    assert env["counter"] == 12


def test_unbound_local_helpful_error_not_did_you_set_it_earlier():
    """Verify modifying a global without declaration explains global keyword instead of misleading name error."""
    with pytest.raises(DoomNameError) as exc_info:
        execute("""
counter = 0
to inc:
    counter = counter + 1
inc()
""")
    msg = str(exc_info.value)
    assert "global variable 'counter'" in msg
    assert "declare 'global counter'" in msg
    assert "Did you set it earlier?" not in msg


def test_keyword_collision_last_assignment():
    """Verify 'last = 9' produces keyword collision explanation instead of generic error."""
    with pytest.raises(DoomSyntaxError) as exc_info:
        compile_to_ast("last = 9")
    msg = str(exc_info.value)
    assert "'last' is a reserved keyword" in msg
    assert "set my_last to 9" in msg or "Did you mean:" in msg


def test_runtime_error_label_in_format():
    """Verify runtime errors are labelled DoomScript Runtime Error, not Syntax Error."""
    try:
        execute("""
nums = [10, 20]
say item 5 of nums
""")
    except Exception as e:
        formatted = format_syntax_error("nums = [10, 20]\nsay item 5 of nums", e)
        assert "DoomScript Runtime Error" in formatted
        assert "DoomScript Syntax Error" not in formatted

    # Real syntax error
    try:
        compile_to_ast('say "unclosed')
    except Exception as e:
        formatted = format_syntax_error('say "unclosed', e)
        assert "DoomScript Syntax Error" in formatted
        assert "DoomScript Runtime Error" not in formatted


def test_doom_suggest_no_deprecated_score_is_100():
    """Verify doom suggest recommends canonical 'set score to 100' and not deprecated 'score is 100'."""
    suggestions = find_closest_phrasings("score 100")
    assert "set score to 100" in suggestions
    assert "score is 100" not in suggestions


def test_relationships_declared_before_entities():
    """Verify entity relationships can be declared in any order, including before classes."""
    env = execute("""
a User has many Orders
an Order belongs to a User

a User begins with name = ""
an Order begins with item = "", price = 0

create a User with name "Alice" into u1
create an Order with item "Book", price 25 into o1
add o1 to u1.orders
""")
    assert len(env["u1"].orders) == 1
    assert env["o1"].user.name == "Alice"


def test_entity_module_annotations_no_tuple_name_error():
    """Verify doomscript.core.entity imports Tuple and module annotations evaluate without NameError."""
    import doomscript.core.entity as entity_mod
    ann = getattr(entity_mod, "__annotations__", {})
    assert "_PENDING_RELATIONS" in ann
