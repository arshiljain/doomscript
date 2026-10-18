"""
DoomScript Error Translation & Suggestion Engine
Provides plain-English explanations, caret-positioned error displays,
difflib-powered closest valid sentence suggestions, and optional theatrical mode.
Never shows raw Lark errors to the user.
"""

import difflib
import re
from typing import List, Optional, Tuple
from lark.exceptions import UnexpectedToken, UnexpectedCharacters, VisitError
from doomscript.exceptions import DoomError, DoomSyntaxError, DoomScopeError
from doomscript.grammar.phrases import (
    VERB_SYNONYMS,
    COMPARISON_SYNONYMS,
    ASSIGNMENT_PATTERNS,
)

# Canonical DoomScript sentence patterns for difflib matching
CANONICAL_TEMPLATES = [
    # I/O & Basic
    'say "Hello, world!"',
    'say "Player:", name, "Level:", level',
    'ask "What is your name?" into name',
    'ask number "Enter your age:" into age',
    'ask boolean "Do you want to continue?" into confirmed',
    # Assignment
    'set score to 100',
    'score is 100',
    'let score be 100',
    'put 100 into score',
    'increase count by 1',
    'decrease health by 10',
    'call it total_score',
    # Lists
    'numbers = a list of 10, 20, 30',
    'empty_items = an empty list',
    'add item to list',
    'remove item from list',
    'insert item at 1 in list',
    'second = item 2 of list',
    'first_three = first 3 items of list',
    'last_three = last 3 items of list',
    'sorted_items = sorted items',
    'reversed_items = reversed items',
    'unique = unique items of items',
    'list contains item',
    'list is empty',
    'list is not empty',
    # Conditions
    'if count is greater than 10',
    'otherwise if count is at least 5',
    'otherwise',
    'unless flag',
    'score is between 80 and 100',
    'role is one of ["admin", "editor"]',
    'value is a number',
    'name is text',
    'name starts with "Dr."',
    'filename ends with ".csv"',
    # Loops
    'repeat 5 times:',
    'repeat with i from 1 to 10:',
    'repeat with i from 1 to 10 by 2:',
    'for each person in people:',
    'for each item in items where item is over 10:',
    'while health is over 0:',
    'until game_over:',
    'stop',
    'skip',
    # Functions
    'to greet person with greeting "Hello":',
    'to tax on price:',
    'return total',
    'give back total',
    'tax_amount is the result of tax on subtotal',
    # Data Operations
    'names is the name of each person in people',
    'people where age is over 18 into adults',
    'group orders by customer into customer_orders',
    'sort orders by amount descending',
    'total of price in orders',
    'average of price in orders',
    'highest price in orders',
    'lowest price in orders',
    # Error Handling
    'try:',
    'if that fails as problem:',
    'always:',
    'verify that count is over 0 otherwise "Count must be positive"',
    # File & CSV & JSON
    'read file "data.txt" into content',
    'write "hello" into file "log.txt"',
    'append "hello" to file "log.txt"',
    'read csv file "data.csv" into rows',
    'write csv rows into file "out.csv"',
    'append csv row to file "out.csv"',
    'parse json raw_text into obj',
    'convert obj to json into json_text',
    'list files in "folder" into files',
    # System & Interop
    'today',
    'now',
    'round 3.14159 to 2 places into pi',
    'absolute value of x',
    'square root of 25',
    'get environment variable "PATH" into p',
    'run command "python --version" into ver',
    'use python module math',
    'from python module math use ceil, floor',
    'use "helpers.doom"',
]


def find_closest_phrasings(broken_line: str, n: int = 3) -> List[str]:
    """Finds closest valid sentence phrasings using difflib against template library."""
    clean = broken_line.strip()
    if not clean:
        return []
    # Strip trailing colons or dots for better match
    clean_stripped = clean.rstrip(":.")
    matches = difflib.get_close_matches(clean_stripped, CANONICAL_TEMPLATES, n=n, cutoff=0.3)
    if not matches:
        # Fallback to word-overlap heuristic
        words = set(clean_stripped.lower().split())
        scored = []
        for tmpl in CANONICAL_TEMPLATES:
            tmpl_words = set(tmpl.lower().split())
            overlap = len(words & tmpl_words)
            if overlap > 0:
                scored.append((overlap, tmpl))
        scored.sort(key=lambda x: x[0], reverse=True)
        matches = [s[1] for s in scored[:n]]
    return matches


def translate_lark_error(err: Exception, source_line: str) -> Tuple[str, Optional[str]]:
    """
    Translates raw Lark exceptions into friendly, plain-English explanations
    and a helpful suggestion.
    """
    if isinstance(err, UnexpectedToken):
        tok = err.token
        tok_val = getattr(tok, "value", str(tok))
        expected = getattr(err, "expected", []) or []

        # Common intent patterns
        if tok_val == "=":
            return (
                "Unexpected '=' here.",
                "In DoomScript, you can write 'set x to ...' or 'x is ...'."
            )
        if tok_val == ":":
            return (
                "Colons ':' are optional in DoomScript blocks, but here it appeared unexpectedly.",
                "Make sure your block header starts with 'if', 'repeat', 'for each', 'to', etc."
            )
        if tok_val in ("print", "echo", "console.log"):
            return (
                f"The verb '{tok_val}' is not standard in DoomScript.",
                f"Use 'say {source_line.split(tok_val, 1)[-1].strip()}' instead."
            )
        if "to" in source_line and tok_val == "def":
            return (
                "Functions in DoomScript start with 'to', not 'def'.",
                "to function_name with param1, param2:"
            )

        return (
            f"I didn't understand '{tok_val}' here. It wasn't expected in this position.",
            None
        )

    elif isinstance(err, UnexpectedCharacters):
        char = source_line[err.column - 1 : err.column] if hasattr(err, "column") and 0 < err.column <= len(source_line) else "character"
        return (
            f"Unexpected character '{char}'. DoomScript statements should read like plain English.",
            None
        )

    elif isinstance(err, VisitError):
        orig = getattr(err, "orig_exc", err)
        return (f"Failed while compiling statement: {orig}", None)

    elif isinstance(err, DoomError):
        return (err.message, err.suggestion)

    return (str(err), None)


def format_syntax_error(
    source: str,
    err: Exception,
    file_path: str = "<source>",
    theatrical: bool = False,
) -> str:
    """
    Builds a complete, formatted plain-English error message with line numbers,
    caret pointer under the problem, plain explanation, and 'Did you mean: ...?'.
    Never outputs raw Lark error representations.
    """
    line_no = getattr(err, "line", 1)
    col_no = getattr(err, "column", 1)
    lines = source.splitlines()

    source_line = ""
    if 1 <= line_no <= len(lines):
        source_line = lines[line_no - 1]
    elif lines:
        source_line = lines[-1]
        line_no = len(lines)

    explanation, explicit_suggestion = translate_lark_error(err, source_line)

    suggestion = explicit_suggestion
    if not suggestion and source_line.strip():
        closest = find_closest_phrasings(source_line, n=1)
        if closest:
            suggestion = closest[0]

    # Caret positioning
    pointer_col = max(1, col_no)
    prefix = f"{line_no:4d} | "
    caret_pad = " " * (len(prefix) + pointer_col - 1)

    output = []
    if theatrical:
        output.append("[bold red]FOOLISH MORTAL! The ancient monolith rejects your utterance![/bold red]")
        output.append(f"[bold yellow]File:[/bold yellow] {file_path}:{line_no}:{col_no}")
        output.append("")
        output.append(f"{prefix}{source_line}")
        output.append(f"{caret_pad}[bold red]^[/bold red]")
        output.append("")
        output.append(f"[bold red]DoomScript Curse:[/bold red] {explanation}")
        if suggestion:
            output.append(f"[bold green]Bow before the correct incantation:[/bold green] {suggestion}")
    else:
        output.append(f"[bold red]DoomScript Syntax Error[/bold red] at [cyan]{file_path}:{line_no}:{col_no}[/cyan]")
        output.append("")
        output.append(f"{prefix}{source_line}")
        output.append(f"{caret_pad}[bold red]^[/bold red]")
        output.append("")
        output.append(f"[bold white]Problem:[/bold white] {explanation}")
        if suggestion:
            output.append(f"[bold green]Did you mean:[/bold green] [italic]{suggestion}[/italic]")

    return "\n".join(output)
