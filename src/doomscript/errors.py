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
    'sort items',
    'sort items descending',
    'reverse items',
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


def find_closest_phrasings(broken_line: str, n: int = 3, cutoff: float = 0.5) -> List[str]:
    """Finds closest valid sentence phrasings using difflib against template library."""
    clean = broken_line.strip()
    if not clean:
        return []
    clean_stripped = clean.rstrip(":.")
    matches = difflib.get_close_matches(clean_stripped, CANONICAL_TEMPLATES, n=n, cutoff=cutoff)
    if not matches:
        clean_lower = clean_stripped.lower()
        scored = []
        for tmpl in CANONICAL_TEMPLATES:
            ratio = difflib.SequenceMatcher(None, clean_lower, tmpl.lower()).ratio()
            if ratio >= cutoff:
                scored.append((ratio, tmpl))
        scored.sort(key=lambda x: x[0], reverse=True)
        matches = [s[1] for s in scored[:n]]
    return matches


def translate_lark_error(err: Exception, source_line: str) -> Tuple[str, Optional[str]]:
    """
    Translates raw Lark exceptions into friendly, plain-English explanations
    and actionable suggestions for beginners.
    """
    clean_line = source_line.strip()

    # 1. Unclosed quotes check
    dquotes = len(re.findall(r'(?<!\\)"', clean_line))
    squotes = len(re.findall(r"(?<!\\)'", clean_line))
    if dquotes % 2 != 0:
        return (
            "It looks like an unclosed double quote (\"). Every opening quote needs a matching closing quote.",
            f'{clean_line}"'
        )
    if squotes % 2 != 0:
        return (
            "It looks like an unclosed single quote ('). Every opening quote needs a matching closing quote.",
            f"{clean_line}'"
        )

    # 2. Unclosed brackets / parentheses
    if clean_line.count("(") > clean_line.count(")"):
        return (
            "Unclosed parenthesis '('. Make sure every '(' has a matching closing ')'.",
            f"{clean_line})"
        )
    if clean_line.count("[") > clean_line.count("]"):
        return (
            "Unclosed bracket '['. Make sure every list bracket '[' has a matching closing ']'.",
            f"{clean_line}]"
        )
    if clean_line.count("{") > clean_line.count("}"):
        return (
            "Unclosed record brace '{'. Make sure every '{' has a matching closing '}'.",
            f"{clean_line}}}"
        )

    # 3. Python-isms
    if re.match(r"^def\s+([A-Za-z_]\w*)\s*\(", clean_line):
        fn_match = re.match(r"^def\s+([A-Za-z_]\w*)\s*\((.*?)\):?", clean_line)
        if fn_match:
            fn_name = fn_match.group(1)
            params = fn_match.group(2).strip()
            param_part = f" with {params}" if params else ""
            return (
                "In DoomScript, functions start with 'to', not 'def'.",
                f"to {fn_name}{param_part}:"
            )
        return (
            "In DoomScript, functions start with 'to', not 'def'.",
            "to my_function with param1, param2:"
        )

    if re.match(r"^print\s*\(", clean_line) or re.match(r"^print\s+", clean_line):
        inner = re.sub(r"^print\s*\(?\s*(.*?)\s*\)?$", r"\1", clean_line)
        return (
            "In DoomScript, use 'say' instead of 'print' to display output.",
            f"say {inner}"
        )

    if re.match(r"^import\s+([A-Za-z_]\w*)", clean_line):
        mod_name = re.match(r"^import\s+([A-Za-z_]\w*)", clean_line).group(1)
        return (
            f"To import a Python module in DoomScript, use 'use python module {mod_name}'.",
            f"use python module {mod_name}"
        )

    if re.search(r"\bfor\s+\w+\s+in\s+range\s*\(", clean_line):
        return (
            "In DoomScript, write loops in plain English: 'repeat 5 times:' or 'repeat with i from 1 to 5:'.",
            "repeat with i from 1 to 5:"
        )

    # 4. Comparison vs Assignment in conditions
    if re.match(r"^(?:if|unless|while)\s+.+[^=!<>]=[^=]", clean_line):
        return (
            "Single '=' is for setting a variable. To test if two things are equal in a condition, use 'is' or '=='.",
            clean_line.replace("=", "is", 1)
        )

    # 5. Missing 'into' destination in common data commands
    if re.match(r"^read\s+csv\s+(?:file\s+)?(.+?)$", clean_line, re.IGNORECASE) and "into" not in clean_line.lower():
        return (
            "A CSV read command needs a destination variable after 'into'.",
            f'{clean_line} into rows'
        )

    if re.match(r"^read\s+file\s+(.+?)$", clean_line, re.IGNORECASE) and "into" not in clean_line.lower():
        return (
            "A file read command needs a destination variable after 'into'.",
            f'{clean_line} into content'
        )

    if re.match(r"^write\s+csv\s+(.+?)$", clean_line, re.IGNORECASE) and "file" not in clean_line.lower():
        return (
            "A CSV write command needs an output file specified with 'into file'.",
            f'{clean_line} into file "report.csv"'
        )

    if re.match(r"^ask\s+(.+?)$", clean_line, re.IGNORECASE) and "into" not in clean_line.lower():
        return (
            "An input prompt needs a destination variable after 'into'.",
            f'{clean_line} into answer'
        )

    # 6. Abrupt statement endings (missing value after preposition/operator)
    if re.search(r"\b(?:set\s+\w+\s+to|increase\s+\w+\s+by|decrease\s+\w+\s+by|add\s+.+\s+to)\s*$", clean_line, re.IGNORECASE):
        return (
            "The statement is incomplete. You need to provide a value or variable at the end.",
            None
        )

    # 7. Token-specific fallback
    if isinstance(err, UnexpectedToken):
        tok = err.token
        tok_val = getattr(tok, "value", str(tok))

        if tok_val in ("\n", "_NEWLINE", "\\n"):
            return (
                "The statement appears incomplete or ended unexpectedly. Check if a line is missing a value or block body.",
                None
            )
        if tok_val in ("$END", "<END-OF-FILE>"):
            return (
                "The program ended unexpectedly. Check for unclosed blocks, quotes, or incomplete statements.",
                None
            )
        if tok_val in ("_INDENT", "_DEDENT"):
            return (
                "Inconsistent indentation. Check the spaces at the start of this line (DoomScript uses 4 spaces per indent level).",
                None
            )
        if tok_val == "=":
            return (
                "Unexpected '=' here. In DoomScript, you can write 'set x to ...' or 'x is ...'.",
                "set x to 10"
            )
        if tok_val == ":":
            return (
                "Colons ':' are optional in DoomScript blocks, but here it appeared unexpectedly. Make sure your block header starts with 'if', 'repeat', 'for each', 'to', etc.",
                None
            )

        return (
            f"I didn't understand '{tok_val}' here. It wasn't expected in this position.",
            None
        )

    elif isinstance(err, UnexpectedCharacters):
        char = source_line[err.column - 1 : err.column] if hasattr(err, "column") and 0 < err.column <= len(source_line) else "character"
        return (
            f"Unexpected character '{char}'. DoomScript statements should read like plain English without special punctuation.",
            None
        )

    elif isinstance(err, VisitError):
        orig = getattr(err, "orig_exc", err)
        return (f"Failed while compiling statement: {orig}", None)

    elif isinstance(err, DoomError):
        return (err.message, err.suggestion)

    return (str(err), None)


def translate_runtime_error(err: Exception) -> str:
    """Translates Python runtime exceptions into beginner-friendly explanations."""
    err_str = str(err)
    if isinstance(err, NameError):
        m = re.search(r"name '([^']+)' is not defined", err_str)
        if m:
            var_name = m.group(1)
            if var_name.startswith("_var_"):
                var_name = var_name[5:]
            return f"I don't know what '{var_name}' is. Did you set it earlier?"
        return "I don't know what that variable is. Did you set it earlier?"
    elif isinstance(err, ZeroDivisionError):
        return "Cannot divide by zero. Make sure the number you're dividing by is not 0."
    elif isinstance(err, IndexError):
        return "List item out of reach. The list doesn't have that many items."
    elif isinstance(err, KeyError):
        m = re.search(r"'([^']+)'", err_str)
        if m:
            return f"Record does not contain the key '{m.group(1)}'. Check the field name."
        return "Record key not found."
    elif isinstance(err, TypeError):
        if "unsupported operand type" in err_str or "can only concatenate" in err_str:
            return f"Cannot perform this operation on different types ({err_str}). Make sure both sides are numbers or both are text."
        return f"Type mismatch: {err_str}."
    elif isinstance(err, AttributeError):
        return f"This value doesn't have that property or action: {err_str}."
    elif isinstance(err, FileNotFoundError):
        return f"File not found: {err_str}. Check that the path is correct."
    elif isinstance(err, PermissionError):
        return f"Permission denied: {err_str}."
    elif isinstance(err, ValueError):
        return f"Invalid value: {err_str}."
    elif isinstance(err, AssertionError):
        return f"Check failed: {err_str}"
    return f"{type(err).__name__}: {err_str}"


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
        closest = find_closest_phrasings(source_line, n=1, cutoff=0.6)
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
