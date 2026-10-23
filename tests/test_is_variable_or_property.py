import pytest
import warnings
from doomscript.compiler.engine import execute


def test_is_variable_comparison_when_in_scope():
    code = """
target = "active"
current_status = "active"
other_status = "inactive"

if current_status is target:
    matched = True
else:
    matched = False

if other_status is target:
    other_matched = True
else:
    other_matched = False
"""
    env = execute(code)
    assert env["matched"] is True
    assert env["other_matched"] is False


def test_is_not_variable_comparison_when_in_scope():
    code = """
target = "guest"
role = "admin"

if role is not target:
    not_guest = True
else:
    not_guest = False

if role isn't target:
    isnt_guest = True
else:
    isnt_guest = False
"""
    env = execute(code)
    assert env["not_guest"] is True
    assert env["isnt_guest"] is True


def test_is_property_check_when_not_in_scope():
    code = """
user1 = {"active": True, "name": "Alice"}
user2 = {"active": False, "name": "Bob"}

if user1 is active:
    u1_active = True
else:
    u1_active = False

if user2 is active:
    u2_active = True
else:
    u2_active = False

if user2 is not active:
    u2_inactive = True
else:
    u2_inactive = False
"""
    env = execute(code)
    assert env["u1_active"] is True
    assert env["u2_active"] is False
    assert env["u2_inactive"] is True


def test_ambiguity_warning_when_both_in_scope_and_property():
    code = """
target = "admin"
user = {"target": "admin", "name": "Alice"}

if user is target:
    matched = True
else:
    matched = False
"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        env = execute(code)
        assert env["matched"] is False # user (dict) != "admin" (str)
        # Verify ambiguity warning was emitted
        ambig_warnings = [item for item in w if "Ambiguous 'is'" in str(item.message)]
        assert len(ambig_warnings) > 0
        assert "'target' is both a variable in scope and a property" in str(ambig_warnings[0].message)


def test_no_warning_when_in_scope_and_not_a_property():
    code = """
expected = 42
actual = 42

if actual is expected:
    matched = True
else:
    matched = False
"""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        env = execute(code)
        assert env["matched"] is True
        ambig_warnings = [item for item in w if "Ambiguous" in str(item.message)]
        assert len(ambig_warnings) == 0


def test_function_parameter_scope_isolation():
    code = """
to check_match with val, candidate:
    if val is candidate:
        return True
    return False

res1 = check_match("hello", "hello")
res2 = check_match("hello", "world")

# Outside function, candidate is NOT in scope, so 'is candidate' is a property check
obj = {"candidate": True}
if obj is candidate:
    obj_has_prop = True
else:
    obj_has_prop = False
"""
    env = execute(code)
    assert env["res1"] is True
    assert env["res2"] is False
    assert env["obj_has_prop"] is True


def test_use_python_module_binds_in_scope():
    code = """
use python module math
m = math
if m is math:
    math_matched = True
else:
    math_matched = False
"""
    env = execute(code)
    assert env["math_matched"] is True
    assert env["math"] is not None
