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
    CORE_COMMAND_VERBS,
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


RESERVED_KEYWORDS = {
    "to": "used to define functions ('to my_function with x:').",
    "say": "used to display output ('say \"hello\"').",
    "show": "used to display output ('show \"hello\"').",
    "ask": "used to prompt for user input ('ask \"Name?\" into name').",
    "read": "used to read files or CSV data ('read file \"f.txt\" into content').",
    "write": "used to write files or CSV data ('write text into file \"f.txt\"').",
    "set": "used to assign variables ('set x to 5').",
    "if": "used for conditional branches ('if x > 5:').",
    "else": "used for alternative conditional branches ('else:').",
    "elif": "used for chained conditionals ('elif x > 2:').",
    "unless": "used for negative conditionals ('unless x > 5:').",
    "repeat": "used for loops ('repeat 5 times:').",
    "while": "used for while loops ('repeat while x > 0:').",
    "until": "used for until loops ('repeat until x is 10:').",
    "for": "used for iteration loops ('for each item in list:').",
    "each": "used in 'for each' iteration loops.",
    "try": "used for error handling ('try: ... if it fails: ...').",
    "attempt": "used for error handling ('attempt: ... if it fails: ...').",
    "match": "used for pattern matching ('match value:').",
    "when": "used for pattern matching branches ('when 1:').",
    "return": "used to return values from functions ('return result').",
    "verify": "used for assertions ('verify condition otherwise \"error\"').",
    "require": "used for preconditions ('require x > 0').",
    "ensure": "used for postconditions ('ensure result > 0').",
    "where": "used for filtering collections ('items where amount > 50').",
    "is": "used for comparisons and assignments ('x is 5').",
    "into": "used to specify destination variables ('read file ... into content').",
    "last": "used in list operations ('last item of list', 'last 3 items of list').",
    "first": "used in list operations ('first item of list', 'first 3 items of list').",
    "item": "used in list item access ('item 1 of list').",
    "items": "used in list slicing ('first 3 items of list').",
    "count": "used for counting items in collections ('count of items').",
    "sum": "used for summing items in collections ('sum of numbers').",
    "average": "used for averaging items in collections ('average of scores').",
    "min": "used to find minimum values ('min of numbers').",
    "max": "used to find maximum values ('max of numbers').",
    "highest": "used to find highest value ('highest score in games').",
    "lowest": "used to find lowest value ('lowest score in games').",
    "sort": "used to sort collections ('sort items').",
    "reverse": "used to reverse collections ('reverse items').",
    "unique": "used to filter unique items ('unique items of list').",
    "length": "used to get collection length ('length of list').",
    "step": "used in loops ('by step 2').",
    "record": "used for database records ('save record ...').",
    "table": "used for database tables ('table \\\"users\\\"').",
    "database": "used for database operations ('database \\\"db.sqlite\\\"').",
    "global": "used to declare global variables in functions ('global counter')."
}


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

    # 4. Keyword-Collision checks (assigning to reserved words)
    kw_assign_m = re.match(r"^(?:set\s+)?([a-z_]+)\s*(?:=|is\b|to\b|\+=|-=|\*=)\s*(.+)$", clean_line, re.IGNORECASE)
    if kw_assign_m:
        kw = kw_assign_m.group(1).lower()
        if kw in RESERVED_KEYWORDS:
            explanation = RESERVED_KEYWORDS[kw]
            val_part = kw_assign_m.group(2).strip()
            return (
                f"'{kw}' is a reserved keyword in DoomScript {explanation} It cannot be used as a variable name.",
                f"set my_{kw} to {val_part}"
            )

    # 5. Incomplete data verbs (trim/uppercase/lowercase/filter missing into or destination)
    if re.match(r"^trim\s+(.+)$", clean_line, re.IGNORECASE) and "into" not in clean_line.lower() and "of" not in clean_line.lower():
        target_expr = re.match(r"^trim\s+(.+)$", clean_line, re.IGNORECASE).group(1).strip()
        return (
            "In DoomScript, data transformations require a destination variable: 'trim <text> into <variable>' or expression form 'say trim of <text>'.",
            f"trim {target_expr} into cleaned"
        )
    if re.match(r"^uppercase\s+(.+)$", clean_line, re.IGNORECASE) and "into" not in clean_line.lower() and "of" not in clean_line.lower():
        target_expr = re.match(r"^uppercase\s+(.+)$", clean_line, re.IGNORECASE).group(1).strip()
        return (
            "In DoomScript, data transformations require a destination variable: 'uppercase <text> into <variable>' or expression form 'say uppercase of <text>'.",
            f"uppercase {target_expr} into upper_text"
        )
    if re.match(r"^lowercase\s+(.+)$", clean_line, re.IGNORECASE) and "into" not in clean_line.lower() and "of" not in clean_line.lower():
        target_expr = re.match(r"^lowercase\s+(.+)$", clean_line, re.IGNORECASE).group(1).strip()
        return (
            "In DoomScript, data transformations require a destination variable: 'lowercase <text> into <variable>' or expression form 'say lowercase of <text>'.",
            f"lowercase {target_expr} into lower_text"
        )
    filt_m = re.match(r"^filter\s+(.+?)\s+where\s+(.+)$", clean_line, re.IGNORECASE)
    if filt_m:
        return (
            "In DoomScript, write filters as '<collection> where <condition> into <target>'.",
            f"{filt_m.group(1).strip()} where {filt_m.group(2).strip()} into filtered_items"
        )

    # 6. Typo / Edit-distance keyword suggestions (e.g. 'sya' -> 'say', 'repeta' -> 'repeat', 'whlie' -> 'while', 'prnt' -> 'say')
    first_token_m = re.match(r"^([A-Za-z_]\w*)", clean_line)
    if first_token_m:
        first_word = first_token_m.group(1).lower()
        candidate_verbs = list(set(CORE_COMMAND_VERBS) | set(VERB_SYNONYMS.keys()) | {"print", "println"})
        if first_word not in candidate_verbs and not re.search(r"^[A-Za-z_]\w*\s*(?:=|is\b|\+=|-=|\*=)", clean_line):
            close_verbs = difflib.get_close_matches(first_word, candidate_verbs, n=1, cutoff=0.6)
            if close_verbs:
                match_verb = close_verbs[0]
                match_verb = VERB_SYNONYMS.get(match_verb, match_verb)
                rest = clean_line[len(first_word):].strip()
                return (
                    f"I didn't recognize the command '{first_word}'. Did you mean '{match_verb}'?",
                    f"{match_verb} {rest}".strip()
                )

    # 7. Comparison vs Assignment in conditions
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


def get_traceback_variables(err: Exception) -> List[str]:
    vars_found = set()
    tb = getattr(err, "__traceback__", None)
    while tb:
        frame = tb.tb_frame
        for k in frame.f_locals:
            if not k.startswith("_") and k not in ("sys", "builtins", "runtime", "execute", "ast"):
                vars_found.add(k)
        for k in frame.f_globals:
            if not k.startswith("_") and k not in ("sys", "builtins", "runtime", "execute", "ast"):
                vars_found.add(k)
        tb = tb.tb_next
    return list(vars_found)


def translate_runtime_error(err: Exception) -> str:
    """Translates Python runtime exceptions into beginner-friendly explanations."""
    if isinstance(err, DoomError) and hasattr(err, "message") and err.message:
        return err.message
    err_str = str(err)
    if isinstance(err, UnboundLocalError):
        m = re.search(r"(?:local variable|cannot access local variable) '([^']+)'", err_str)
        var_name = m.group(1) if m else "this variable"
        if var_name.startswith("_var_"):
            var_name = var_name[5:]
        return f"You tried to modify the global variable '{var_name}' inside a function. In DoomScript, declare 'global {var_name}' at the top of the function to modify it."
    elif isinstance(err, NameError):
        m = re.search(r"name '([^']+)' is not defined", err_str)
        if m:
            var_name = m.group(1)
            if var_name.startswith("_var_"):
                var_name = var_name[5:]
            candidates = [c for c in get_traceback_variables(err) if c != var_name]
            close = difflib.get_close_matches(var_name, candidates, n=1, cutoff=0.55)
            if close:
                return f"I don't know what '{var_name}' is. Did you mean '{close[0]}'?"
            return f"I don't know what '{var_name}' is. Did you set it earlier?"
        return "I don't know what that variable is. Did you set it earlier?"
    elif isinstance(err, ZeroDivisionError):
        return "Cannot divide by zero. You tried to divide by zero. Make sure the number you're dividing by is not 0."
    elif isinstance(err, IndexError):
        if err_str and err_str not in ("list index out of range", "pop from empty list"):
            return err_str
        tb = getattr(err, "__traceback__", None)
        extracted = None
        while tb:
            frame = tb.tb_frame
            line = ""
            if frame.f_code and frame.f_code.co_filename:
                import linecache
                line = linecache.getline(frame.f_code.co_filename, tb.tb_lineno).strip()
            if line:
                m_sub = re.search(r"(\w+)\[(-?\d+)\]", line)
                if m_sub:
                    vname, idx_s = m_sub.group(1), m_sub.group(2)
                    c = frame.f_locals.get(vname) or frame.f_globals.get(vname)
                    if isinstance(c, (list, tuple, str)):
                        extracted = f"You asked for item {idx_s}, but this list only has {len(c)} items."
                        break
                m_it = re.search(r"(?:item_of\((\d+),\s*(\w+)\)|item\s+(\d+)\s+of\s+(\w+))", line)
                if m_it:
                    idx_s = m_it.group(1) or m_it.group(3)
                    vname = m_it.group(2) or m_it.group(4)
                    c = frame.f_locals.get(vname) or frame.f_globals.get(vname)
                    if isinstance(c, (list, tuple, str)):
                        extracted = f"You asked for item {idx_s}, but this list only has {len(c)} items."
                        break
            tb = tb.tb_next
        if extracted:
            return extracted
        return "List item out of reach. The list doesn't have that many items."
    elif isinstance(err, KeyError):
        m = re.search(r"['\"]?([^'\"]+)['\"]?", err_str)
        key = m.group(1) if m else err_str
        return f"This dictionary doesn't have a key called '{key}'."
    elif isinstance(err, TypeError):
        m_op = re.search(r"unsupported operand type\(s\) for ([^:]+):\s*'([^']+)'\s*and\s*'([^']+)'", err_str)
        if m_op:
            op, t1, t2 = m_op.groups()
            op_disp = {"+": "add", "-": "subtract", "*": "multiply", "/": "divide", "//": "floor divide", "%": "mod"}.get(op.strip(), op.strip())
            return f"You tried to {op_disp} a {t1} and a {t2}. These types can't be combined this way."
        m_cat = re.search(r"can only concatenate (\w+) \(not \"(\w+)\"\) to \1", err_str)
        if m_cat:
            t1, t2 = m_cat.groups()
            return f"You tried to combine a {t1} and a {t2}. These types can't be combined this way."
        return f"Type mismatch: {err_str}."
    elif isinstance(err, AttributeError):
        m = re.search(r"'([^']+)' object has no attribute '([^']+)'", err_str)
        if m:
            t_name, a_name = m.groups()
            return f"A '{t_name}' doesn't have a '{a_name}' property."
        return f"This value doesn't have that property or action: {err_str}."
    elif isinstance(err, FileNotFoundError):
        path = getattr(err, "filename", None)
        if not path:
            m = re.search(r"'(.*?)'", err_str)
            path = m.group(1) if m else "specified"
        return f"I couldn't find the file '{path}'. Check that the name and folder are correct."
    elif isinstance(err, PermissionError):
        path = getattr(err, "filename", None)
        if path:
            return f"I don't have permission to access '{path}'."
        m = re.search(r"'(.*?)'", err_str)
        if m:
            return f"I don't have permission to access '{m.group(1)}'."
        return f"Permission error: {err_str}"
    elif isinstance(err, ValueError):
        m = re.search(r"(?:not enough|too many) values to unpack \(expected (\d+)(?:,\s*got\s*(\d+))?\)", err_str)
        if m:
            exp, got = m.groups()
            got_str = got if got is not None else "fewer"
            return f"Tried to unpack {exp} values, but got {got_str}."
        return f"Invalid value: {err_str}."
    elif isinstance(err, RecursionError):
        return "This function called itself too many times. Did you forget a base case?"
    elif isinstance(err, (ImportError, ModuleNotFoundError)):
        m = re.search(r"No module named '([^']+)'", err_str)
        mod = m.group(1) if m else err_str
        return f"Could not find module '{mod}'. Check that it is installed or spelled correctly."
    elif isinstance(err, OverflowError):
        return "Number too large to calculate. The result exceeded numeric limits."
    elif isinstance(err, StopIteration):
        return "Reached the end of items. No more values are available."
    elif isinstance(err, AssertionError):
        return f"Check failed: {err_str}"
    return f"{type(err).__name__}: {err_str}"


def format_syntax_error(
    source: str,
    err: Exception,
    file_path: str = "<source>",
    theatrical: bool = False,
    line_map: Optional[dict] = None,
) -> str:
    """
    Builds a complete, formatted plain-English error message with line numbers,
    caret pointer under the problem, plain explanation, and 'Did you mean: ...?'.
    Never outputs raw Lark error representations.
    """
    from doomscript.exceptions import DoomScriptSyntaxError

    if isinstance(err, DoomScriptSyntaxError):
        line_no = getattr(err, "line", 1) or 1
        col_no = getattr(err, "column", 1) or 1
        lines = source.splitlines()
        source_line = ""
        if 1 <= line_no <= len(lines):
            source_line = lines[line_no - 1]
        elif lines:
            source_line = lines[-1]
            line_no = len(lines)
        orig_err = getattr(err, "__cause__", None) or err
        explanation, explicit_suggestion = translate_lark_error(orig_err, source_line)
        suggestion = getattr(err, "suggestion", None) or explicit_suggestion
        if not suggestion and source_line.strip():
            from doomscript.compiler.advisor import DidYouMeanAdvisor, extract_known_variables
            failing_tok = None
            if hasattr(orig_err, "token"):
                failing_tok = getattr(orig_err.token, "value", str(orig_err.token))
            suggestion = DidYouMeanAdvisor.find_token_suggestion(
                source_line,
                known_variables=extract_known_variables(source),
                failing_token=failing_tok,
                col=col_no,
            )
    elif isinstance(err, DoomError):
        line_no = getattr(err, "line", 1) or 1
        col_no = getattr(err, "column", 1) or 1
        lines = source.splitlines()
        source_line = getattr(err, "source_line", None) or ""
        if not source_line and lines:
            if 1 <= line_no <= len(lines):
                source_line = lines[line_no - 1]
            else:
                source_line = lines[-1]
                line_no = len(lines)
        explanation = getattr(err, "message", str(err))
        suggestion = getattr(err, "suggestion", None)
    else:
        raw_line_no = getattr(err, "line", 1) or 1
        col_no = getattr(err, "column", 1) or 1

        if line_map is None:
            try:
                from doomscript.grammar.phrases import normalize_with_map
                _, line_map = normalize_with_map(source)
            except Exception:
                line_map = {}

        line_no = (line_map.get(raw_line_no, raw_line_no) if line_map else raw_line_no) or 1
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
            from doomscript.compiler.advisor import DidYouMeanAdvisor, extract_known_variables
            failing_tok = None
            if hasattr(err, "token"):
                failing_tok = getattr(err.token, "value", str(err.token))
            suggestion = DidYouMeanAdvisor.find_token_suggestion(
                source_line,
                known_variables=extract_known_variables(source),
                failing_token=failing_tok,
                col=col_no,
            )
            if not suggestion:
                closest = find_closest_phrasings(source_line, n=1, cutoff=0.7)
                if closest:
                    suggestion = closest[0]

    # Caret positioning: clamp to length of source_line + 1
    pointer_col = max(1, min(col_no, len(source_line) + 1 if source_line else 1))
    prefix = f"{line_no:4d} | "
    caret_pad = " " * (len(prefix) + pointer_col - 1)

    output = []
    if theatrical:
        output.append("[bold red]FOOLISH MORTAL! The ancient monolith rejects your utterance![/bold red]")
        output.append(f"[bold yellow]File:[/bold yellow] {file_path}:{line_no}:{pointer_col}")
        output.append("")
        output.append(f"{prefix}{source_line}")
        output.append(f"{caret_pad}[bold red]^[/bold red]")
        output.append("")
        output.append(f"[bold red]DoomScript Curse:[/bold red] {explanation}")
        if suggestion:
            output.append(f"[bold green]Bow before the correct incantation:[/bold green] {suggestion}")
    else:
        is_syntax_err = isinstance(err, (DoomSyntaxError, UnexpectedToken, UnexpectedCharacters, VisitError))
        if isinstance(err, DoomError) and not is_syntax_err:
            err_category = "Runtime Error"
        elif is_syntax_err:
            err_category = "Syntax Error"
        elif isinstance(err, (IndexError, NameError, ZeroDivisionError, TypeError, KeyError, ValueError, AttributeError, RuntimeError, FileNotFoundError, PermissionError)):
            err_category = "Runtime Error"
        else:
            err_category = "Syntax Error"
        output.append(f"[bold red]DoomScript {err_category}[/bold red] at [cyan]{file_path}:{line_no}:{pointer_col}[/cyan]")
        output.append("")
        output.append(f"{prefix}{source_line}")
        output.append(f"{caret_pad}[bold red]^[/bold red]")
        output.append("")
        output.append(f"[bold white]Problem:[/bold white] {explanation}")
        if suggestion:
            output.append(f"[bold green]Did you mean:[/bold green] [italic]{suggestion}[/italic]")

    return "\n".join(output)
