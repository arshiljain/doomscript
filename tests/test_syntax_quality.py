"""
Unit and Regression Tests for DoomScript Syntax Quality Milestone
Covers:
- P0: Formatter structure-aware indentation, validation, and DoomIndentationError
- P1: Canonical assignment (=), reserved comparison (is), AST equivalence
- P2: Formatter canonicalization of aliases, verbs, comparisons, and spacing
- P3: Idempotency, behavior preservation, and source location accuracy
"""

import ast
import pytest
from doomscript.compiler.engine import compile_to_ast, execute
from doomscript.formatter import format_code
from doomscript.exceptions import DoomIndentationError, DoomSyntaxError


# ---------------------------------------------------------------------------
# P1: CANONICAL SYNTAX & UNAMBIGUOUS SEMANTICS
# ---------------------------------------------------------------------------

def test_canonical_assignment_vs_comparison():
    """Verify '=' is canonical assignment and 'is' is strictly comparison in expressions."""
    # Assignment
    env = execute("""
score = 100
is_century = score is 100
is_zero = score is 0
""")
    assert env["score"] == 100
    assert env["is_century"] is True
    assert env["is_zero"] is False


def test_ast_equivalence_for_assignment_aliases():
    """Verify that canonical '=', alias 'set ... to', 'let ... be', and legacy '... is ...' produce equivalent ASTs."""
    ast_canonical = compile_to_ast("score = 100")
    ast_set = compile_to_ast("set score to 100")
    ast_let = compile_to_ast("let score be 100")
    ast_legacy = compile_to_ast("score is 100")

    dump_canonical = ast.dump(ast_canonical, include_attributes=False)
    dump_set = ast.dump(ast_set, include_attributes=False)
    dump_let = ast.dump(ast_let, include_attributes=False)
    dump_legacy = ast.dump(ast_legacy, include_attributes=False)

    assert dump_canonical == dump_set
    assert dump_canonical == dump_let
    assert dump_canonical == dump_legacy


def test_is_in_branching_and_predicates():
    """Verify 'is' behaves unambiguously as equality comparison in conditional statements."""
    code = """
val = 42
branch = "none"

if val is 42:
    branch = "matched_42"
else:
    branch = "wrong"
"""
    env = execute(code)
    assert env["branch"] == "matched_42"


def test_legacy_assignment_statements_in_chained_lines():
    """Verify legacy assignment in chained 'and then' statements still functions correctly during 1.x deprecation."""
    code = "a is 10 and then b is 20 and then sum_val = a + b"
    env = execute(code)
    assert env["a"] == 10
    assert env["b"] == 20
    assert env["sum_val"] == 30


# ---------------------------------------------------------------------------
# P0 & P2: FORMATTER INDENTATION & STRUCTURE-AWARE FORMATTING
# ---------------------------------------------------------------------------

def test_formatter_two_space_indentation():
    """Verify 2-space indented blocks are cleanly normalized to canonical 4-space blocks."""
    src = """if x > 0:
  say "positive"
  y = x * 2
"""
    formatted = format_code(src)
    expected = """if x > 0:
    say "positive"
    y = x * 2
"""
    assert formatted == expected


def test_formatter_mixed_indentation_across_blocks():
    """Verify mixed 2-space and 4-space indentation across different blocks normalizes to 4 spaces."""
    src = """to first_func:
  say 1

to second_func:
    say 2
"""
    formatted = format_code(src)
    expected = """to first_func:
    say 1

to second_func:
    say 2
"""
    assert formatted == expected


def test_formatter_deeply_nested_blocks():
    """Verify deeply nested blocks (3+ levels) format with consistent 4, 8, 12 space hierarchy."""
    src = """repeat 2 times:
  for each x in [1, 2]:
    if x > 0:
      say x
"""
    formatted = format_code(src)
    expected = """repeat 2 times:
    for each x in [1, 2]:
        if x > 0:
            say x
"""
    assert formatted == expected


def test_formatter_comments_inside_and_outside_blocks():
    """Verify comments inside blocks align with block indentation, while top-level comments stay unindented."""
    src = """# Top-level comment
if active:
    # Check status
    say "active"
# Trailing comment
"""
    formatted = format_code(src)
    assert "# Top-level comment" in formatted
    assert "    # Check status" in formatted
    assert "# Trailing comment" in formatted


def test_formatter_inline_comments():
    """Verify inline comments are preserved cleanly after statement formatting."""
    src = "set score to 100  # initial score"
    formatted = format_code(src)
    assert formatted == "score = 100  # initial score\n"


def test_formatter_string_literal_preservation():
    """Verify strings with colons, keywords, and quote marks are never corrupted."""
    src = 'say "Special: please set x to 10 # not a comment"'
    formatted = format_code(src)
    assert formatted == 'say "Special: please set x to 10 # not a comment"\n'


# ---------------------------------------------------------------------------
# P0: STRICT INDENTATION VALIDATION & DOOMINDENTATIONERROR
# ---------------------------------------------------------------------------

def test_formatter_raises_unexpected_indent():
    """Verify DoomIndentationError is raised when an unexpected indent appears without a block header."""
    src = """say "hello"
    say "world"
"""
    with pytest.raises(DoomIndentationError) as exc_info:
        format_code(src)
    err = exc_info.value
    assert err.line == 2
    assert "Unexpected indent" in str(err)
    assert "remove unexpected leading indentation" in str(err)


def test_formatter_raises_expected_block():
    """Verify DoomIndentationError is raised when a block header is not followed by an indented block."""
    src = """if x > 0:
say "done"
"""
    with pytest.raises(DoomIndentationError) as exc_info:
        format_code(src)
    err = exc_info.value
    assert err.line == 2
    assert "Expected an indented block after 'if x > 0:'" in str(err)
    assert "indent this line by 4 spaces" in str(err)


def test_formatter_raises_unaligned_dedent():
    """Verify DoomIndentationError is raised when a dedent does not match any outer nesting level."""
    src = """if a:
    if b:
        say "deep"
      say "unaligned"
"""
    with pytest.raises(DoomIndentationError) as exc_info:
        format_code(src)
    err = exc_info.value
    assert err.line == 4
    assert "Unindent does not match any outer indentation level" in str(err)


def test_formatter_raises_expected_block_at_eof():
    """Verify DoomIndentationError is raised when a block header appears at EOF without a body."""
    src = "if x > 0:"
    with pytest.raises(DoomIndentationError) as exc_info:
        format_code(src)
    err = exc_info.value
    assert "Expected an indented block" in str(err)


# ---------------------------------------------------------------------------
# P2: CANONICAL NORMALIZATION OF ALIASES
# ---------------------------------------------------------------------------

def test_formatter_canonicalizes_assignment_aliases():
    """Verify all supported assignment aliases normalize to '<target> = <expr>'."""
    src = """please set a to 10
let b be 20
put 30 into c
assign 40 to d
store 50 in e
save 60 as f
initialize g with 70
reset h to 80
make i be 90
legacy_val is 100
"""
    formatted = format_code(src)
    expected = """a = 10
b = 20
c = 30
d = 40
e = 50
f = 60
g = 70
h = 80
i = 90
legacy_val = 100
"""
    assert formatted == expected


def test_formatter_canonicalizes_verbs_and_comparisons():
    """Verify print/show verbs become 'say' and comparison synonyms normalize."""
    src = """print "Hello"
show "World"
if x is bigger than 5:
    say "x is big"
if y is equal to 10:
    say "y is 10"
if z is at minimum 20:
    say "z is high"
"""
    formatted = format_code(src)
    expected = """say "Hello"
say "World"
if x is greater than 5:
    say "x is big"
if y equals 10:
    say "y is 10"
if z is at least 20:
    say "z is high"
"""
    assert formatted == expected


def test_formatter_chained_and_then_statements():
    """Verify 'and then' statement chains are canonicalized within the line."""
    src = 'please print "Starting" and then set count to 1 and then print count'
    formatted = format_code(src)
    assert formatted == 'say "Starting" and then count = 1 and then say count\n'


# ---------------------------------------------------------------------------
# P3: IDEMPOTENCY & BEHAVIOR PRESERVATION
# ---------------------------------------------------------------------------

def test_formatter_idempotency_suite():
    """Verify format_code is strictly idempotent: format_code(format_code(s)) == format_code(s)."""
    samples = [
        "",
        'say "Single line"',
        "score = 100\nbonus = 20\ntotal = score + bonus\nsay total",
        """to compute_total with subtotal, tax_rate:
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total

orders = [100, 250, 400]
repeat with idx from 1 to 3:
    order_val = item idx of orders
    final_val = compute_total(order_val, 0.08)
    if final_val is greater than 200:
        say "High value order:", final_val
""",
        """# File with comments and strings
user = "Alice"
greeting = "Hello, {user}!"  # greeting message
say greeting
"""
    ]

    for src in samples:
        pass1 = format_code(src)
        pass2 = format_code(pass1)
        assert pass1 == pass2, f"Idempotency failure on:\n{src}\nPass1:\n{pass1}\nPass2:\n{pass2}"


def test_behavior_preservation_across_formatting():
    """Verify program runtime execution produces identical environment before and after formatting."""
    unformatted = """please set score to 50
kindly increase score by 25
let multiplier be 2
total is score * multiplier
if total is bigger than 100:
  set status to "gold"
else:
  set status to "silver"
"""
    env_unformatted = execute(unformatted)
    formatted = format_code(unformatted)
    env_formatted = execute(formatted)

    assert env_unformatted["score"] == env_formatted["score"] == 75
    assert env_unformatted["multiplier"] == env_formatted["multiplier"] == 2
    assert env_unformatted["total"] == env_formatted["total"] == 150
    assert env_unformatted["status"] == env_formatted["status"] == "gold"
