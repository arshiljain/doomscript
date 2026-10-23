"""
DoomScript Normalization and Phrase Layer
Driven by data tables (synonyms, filler words, flexible assignments, pronouns, possessives).
Adding a synonym here requires NO grammar edits.
"""

import difflib
import re
re._MAXCACHE = 16384
from typing import Optional, List, Tuple, Dict, Any, Set
from doomscript.exceptions import DoomScopeError, DoomSyntaxError
from doomscript.core.entity import stem_verb


# ---------------------------------------------------------------------------
# DATA TABLES
# ---------------------------------------------------------------------------

# Filler words that can precede statements or verbs
LEADING_FILLERS = [
    "go ahead and",
    "go ahead",
    "please",
    "kindly",
    "just",
    "simply",
    "then",
    "now",
    "next",
    "finally",
]

# Articles that can precede nouns/identifiers outside strings
IGNORABLE_ARTICLES = [
    "the",
]

# Verb synonyms mapping to canonical DoomScript verbs
VERB_SYNONYMS: Dict[str, str] = {
    "show": "say",
    "print out": "say",
    "print": "say",
    "tell": "say",
    "echo": "say",
    "output": "say",
    "log": "say",
    "give back": "return",
    "hand back": "return",
    "yield back": "return",
    "result is": "return",
    "the result is": "return",
}

# Comparison synonyms mapping to canonical Lark operators
# Longest match first to prevent prefix shadowing
COMPARISON_SYNONYMS: List[Tuple[str, str]] = [
    ("is strictly greater than", "is greater than"),
    ("is greater than or equal to", "is at least"),
    ("is strictly less than", "is less than"),
    ("is less than or equal to", "is at most"),
    ("is no greater than", "is at most"),
    ("is no less than", "is at least"),
    ("is no more than", "is at most"),
    ("is no smaller than", "is at least"),
    ("is at minimum", "is at least"),
    ("is at maximum", "is at most"),
    ("is bigger than", "is greater than"),
    ("is more than", "is greater than"),
    ("is higher than", "is greater than"),
    ("is longer than", "is greater than"),
    ("exceeds", "is greater than"),
    ("is smaller than", "is less than"),
    ("is lower than", "is less than"),
    ("is shorter than", "is less than"),
    ("is above", "is greater than"),
    ("is below", "is less than"),
    ("is over", "is greater than"),
    ("is under", "is less than"),
    ("is identical to", "equals"),
    ("is strictly equal to", "equals"),
    ("is equal to", "equals"),
    ("is the same as", "equals"),
    ("does not equal", "is not"),
    ("is not equal to", "is not"),
    ("is different from", "is not"),
    ("is within", "is between"),
]

# Statement starting keywords for sentence style case-normalization
STATEMENT_START_KEYWORDS = {
    "say", "show", "print", "display", "tell", "echo", "log", "output",
    "set", "let", "make", "put", "assign", "store", "save", "initialize", "reset",
    "suppose", "assume", "remember", "keep", "find", "what", "does", "deposit", "withdraw",
    "increase", "decrease", "increment", "decrement", "bump", "double", "halve", "triple",
    "multiply", "divide", "subtract",
    "if", "unless", "while", "until", "repeat", "for", "loop",
    "try", "attempt", "return", "give", "hand", "yield", "with",
    "to", "def", "how", "define", "function", "require", "ensure", "verify", "assert", "check",
    "match", "when", "otherwise", "else", "elif",
    "write", "read", "append", "delete", "copy", "create",
    "ask", "call", "import", "unpack", "trim", "replace", "split", "join",
    "capitalize", "convert", "sort", "round", "combine", "fetch", "post", "download",
    "break", "continue", "stop", "exit", "quit", "add", "remove", "insert", "push", "discard", "clear", "empty", "reverse",
    "load", "filter", "group", "plot", "step", "compute", "test",
    "sleep", "delay", "pause", "shuffle", "words", "lines", "keys", "values",
    "average", "mean", "median", "total", "sum", "maximum", "minimum", "variance", "standard",
    "scatter", "line", "bar", "histogram", "box",
    "train", "predict", "evaluate", "accuracy", "score",
    "distance", "point", "polygon", "maximize", "minimize", "optimize", "benchmark", "trace", "pop",
    "sentiment", "tokenize", "entities", "tfidf", "sample",
    "explain", "preview", "summary"
}

CORE_COMMAND_VERBS: List[str] = [
    "say", "show", "display",
    "set", "make", "create", "let",
    "if", "unless", "else", "elif",
    "repeat", "while", "until", "for",
    "to", "return", "ask", "read", "write", "append",
    "sort", "reverse", "group", "filter",
    "trim", "uppercase", "lowercase", "capitalize",
    "round", "clamp", "convert", "subtract",
    "try", "attempt", "verify", "require", "ensure",
    "fetch", "download", "post", "send",
    "spawn", "wait", "start", "stop", "pause",
    "match", "when", "unpack"
]

# Patterns for flexible assignments
# Format: (regex_pattern, replacement_template)
ASSIGNMENT_PATTERNS: List[Tuple[re.Pattern, str]] = [
    # put <expr> into <target>  -> set <target> to <expr>
    (re.compile(r"^\s*put\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", re.IGNORECASE), r"set \2 to \1"),
    # assign <expr> to <target> -> set <target> to <expr>
    (re.compile(r"^\s*assign\s+(.+?)\s+to\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", re.IGNORECASE), r"set \2 to \1"),
    # store <expr> in/into <target>  -> set <target> to <expr>
    (re.compile(r"^\s*store\s+(.+?)\s+(?:in|into)\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", re.IGNORECASE), r"set \2 to \1"),
    # save <expr> as <target>   -> set <target> to <expr>
    (re.compile(r"^\s*save\s+(.+?)\s+as\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", re.IGNORECASE), r"set \2 to \1"),
    # initialize <target> to/with <expr> -> set <target> to <expr>
    (re.compile(r"^\s*initialize\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+(?:to|with)\s+(.+)$", re.IGNORECASE), r"set \1 to \2"),
    # reset <target> to <expr>   -> set <target> to <expr>
    (re.compile(r"^\s*reset\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+to\s+(.+)$", re.IGNORECASE), r"set \1 to \2"),
    # let <target> be <expr>     -> set <target> to <expr>
    (re.compile(r"^\s*let\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+be\s+(.+)$", re.IGNORECASE), r"set \1 to \2"),
    # make <target> be <expr>   -> set <target> to <expr>
    (re.compile(r"^\s*make\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+be\s+(.+)$", re.IGNORECASE), r"set \1 to \2"),
    # make <target> <expr>      -> set <target> to <expr> (e.g. make x 5)
    (re.compile(r"^\s*make\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+([^\s].*)$", re.IGNORECASE), r"set \1 to \2"),
]

# Regex patterns for possessives and article counts
# e.g., name's length, name's count -> count of name
# the length of name -> count of name
POSSESSIVE_REWRITES: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"\b([A-Za-z_]\w*)'s\s+(?:length|count|size)\b", re.IGNORECASE), r"count of \1"),
    (re.compile(r"\bthe\s+(?:length|count|size)\s+of\s+([A-Za-z_]\w*)\b", re.IGNORECASE), r"count of \1"),
    (re.compile(r"\b(?:length|size)\s+of\s+([A-Za-z_]\w*)\b", re.IGNORECASE), r"count of \1"),
]


# Patterns for Phase 8 type contracts
TYPE_CONTRACT_MAP: Dict[str, str] = {
    "number": "is a number",
    "int": "is a number",
    "float": "is a number",
    "text": "is text",
    "string": "is text",
    "str": "is text",
    "boolean": "is a boolean",
    "bool": "is a boolean",
    "list": "is a list",
    "record": "is a record",
    "dictionary": "is a record",
    "dict": "is a record",
}


# ---------------------------------------------------------------------------
# STRING & COMMENT MASKING UTILITIES
# ---------------------------------------------------------------------------

STRING_REGEX = re.compile(
    r'(?<![\w"\'\\])([fF]?)(("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|(?<!\w)\'(?:[^\'\\]|\\.)*\'))'
)


def mask_strings(text: str) -> Tuple[str, List[str]]:
    """Replaces string literals with placeholders to preserve their exact content."""
    strings = []
    def repl(m):
        idx = len(strings)
        strings.append(m.group(2))
        return f"__STR_LITERAL_{idx}__"
    masked = STRING_REGEX.sub(repl, text)
    return masked, strings

def unmask_strings(text: str, strings: List[str]) -> str:
    """Restores masked string literals."""
    for idx, s in enumerate(strings):
        text = text.replace(f"__STR_LITERAL_{idx}__", s)
    return text


def split_comment(line: str) -> Tuple[str, str]:
    """Splits a line into code and comment (#...) while respecting string literals."""
    masked, strings = mask_strings(line)
    if "#" in masked:
        idx = masked.index("#")
        code_part = masked[:idx]
        comment_part = masked[idx:]
        return unmask_strings(code_part, strings), unmask_strings(comment_part, strings)
    return unmask_strings(masked, strings), ""


def _split_respecting_delimiters(s: str, delimiter: str = ",") -> List[str]:
    """Splits a string by delimiter while respecting quotes and nested brackets."""
    parts = []
    current = []
    depth = 0
    in_quote = None
    for ch in s:
        if in_quote:
            current.append(ch)
            if ch == in_quote:
                in_quote = None
        elif ch in ('"', "'"):
            in_quote = ch
            current.append(ch)
        elif ch in ("(", "[", "{"):
            depth += 1
            current.append(ch)
        elif ch in (")", "]", "}"):
            depth = max(0, depth - 1)
            current.append(ch)
        elif ch == delimiter and depth == 0:
            parts.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current).strip())
    return [p for p in parts if p]


SYNONYM_REPLACEMENTS = [
    # Math & Metric Verbs (calculate is the canonical verb across 300+ domain signatures)
    (re.compile(r"\bcompute\b", re.IGNORECASE), "calculate"),
    # Creation Verbs
    (re.compile(r"\bconstruct\b", re.IGNORECASE), "create"),
    # Data & Imputation Clauses
    (re.compile(r"\bmissing\s+values?\b", re.IGNORECASE), "missing"),
    (re.compile(r"\bfill\s+nulls\b", re.IGNORECASE), "fill missing"),
    # Sorting Direction
    (re.compile(r"\bdesc\b", re.IGNORECASE), "descending"),
    (re.compile(r"\basc\b", re.IGNORECASE), "ascending"),
    # Inspection Verbs
    (re.compile(r"\bexamine\b", re.IGNORECASE), "inspect"),
    # Agent Article Tolerance
    (re.compile(r"^\s*ask\s+the\s+agent\s+", re.IGNORECASE), "ask agent "),
    (re.compile(r"^\s*tell\s+the\s+agent\s+", re.IGNORECASE), "tell agent "),
]


def canonicalize_synonyms(text: str) -> str:
    """Standardizes synonymous English keywords and verbs outside string literals."""
    masked, strings = mask_strings(text)
    for pat, repl in SYNONYM_REPLACEMENTS:
        masked = pat.sub(repl, masked)
    return unmask_strings(masked, strings)


# ---------------------------------------------------------------------------
# SCOPE & PRONOUN TRACKER
# ---------------------------------------------------------------------------

class ScopeTracker:
    """
    Maintains a stack of lexical scopes to track discourse referents:
    both singular ('it', 'that', 'its') and plural ('them', 'these', 'those', 'their'),
    as well as declared variable names for scope-aware syntax disambiguation.
    """
    def __init__(self):
        # Stack of indent levels and their discourse referents
        self.scopes: List[Dict[str, Any]] = [{
            "indent": 0,
            "last_var": None,
            "last_singular": None,
            "last_plural": None,
            "last_subject": None,
            "last_object": None,
            "diverged": False,
            "in_class": False,
            "is_func": False,
            "vars": set(),
        }]
        self.pending_block_vars: List[str] = []
        self._next_is_func: bool = False
        self.builtin_vars: Set[str] = {
            "PI", "E", "math", "random", "json", "re", "sys", "os",
            "True", "False", "None"
        }

    def update_indent(self, indent: int):
        # If indent decreased, pop deeper scopes
        while len(self.scopes) > 1 and self.scopes[-1]["indent"] > indent:
            popped = self.scopes.pop()
            # If popped scope was not an isolated function, merge declared variables into enclosing scope
            if not popped.get("is_func", False):
                self.scopes[-1]["vars"].update(popped.get("vars", set()))

            if self.scopes[-1]["last_var"] is None and not popped["diverged"]:
                self.scopes[-1]["last_var"] = popped["last_var"]
            if self.scopes[-1]["last_singular"] is None and not popped["diverged"]:
                self.scopes[-1]["last_singular"] = popped["last_singular"]
            if self.scopes[-1]["last_plural"] is None and not popped["diverged"]:
                self.scopes[-1]["last_plural"] = popped["last_plural"]
            if self.scopes[-1].get("last_subject") is None and not popped["diverged"]:
                self.scopes[-1]["last_subject"] = popped.get("last_subject")
            if self.scopes[-1].get("last_object") is None and not popped["diverged"]:
                self.scopes[-1]["last_object"] = popped.get("last_object")

        # If indent increased, push new scope inheriting current discourse referents
        if indent > self.scopes[-1]["indent"]:
            new_vars = set(self.pending_block_vars)
            self.pending_block_vars = []
            is_func = self._next_is_func
            self._next_is_func = False
            self.scopes.append({
                "indent": indent,
                "last_var": self.scopes[-1]["last_var"],
                "last_singular": self.scopes[-1]["last_singular"],
                "last_plural": self.scopes[-1]["last_plural"],
                "last_subject": self.scopes[-1].get("last_subject"),
                "last_object": self.scopes[-1].get("last_object"),
                "diverged": False,
                "in_class": self.scopes[-1]["in_class"],
                "is_func": is_func,
                "vars": new_vars,
            })
        elif indent <= self.scopes[-1]["indent"] and self.pending_block_vars:
            self.pending_block_vars = []
            self._next_is_func = False

    def set_pending_vars(self, var_names: List[str], is_func: bool = False):
        for v in var_names:
            clean = re.split(r"[.\[\(\s]", v.strip())[0]
            if clean and re.match(r"^[A-Za-z_]\w*$", clean):
                self.pending_block_vars.append(clean)
        self._next_is_func = is_func

    def record_var(self, var_name: str):
        clean = re.split(r"[.\[\(\s]", var_name.strip())[0]
        if clean and re.match(r"^[A-Za-z_]\w*$", clean):
            self.scopes[-1]["vars"].add(clean)

    def is_var_in_scope(self, name: str) -> bool:
        if not name or not re.match(r"^[A-Za-z_]\w*$", name):
            return False
        if name in self.builtin_vars:
            return True
        for s in self.scopes:
            if name in s.get("vars", set()):
                return True
        return False

    def record_singular(self, var_name: str):
        self.scopes[-1]["last_singular"] = var_name
        self.scopes[-1]["last_var"] = var_name
        self.record_var(var_name)

    def record_plural(self, var_name: str):
        self.scopes[-1]["last_plural"] = var_name
        self.scopes[-1]["last_var"] = var_name
        self.record_var(var_name)

    def record_assignment(self, var_name: str, is_plural: Optional[bool] = None):
        self.scopes[-1]["last_var"] = var_name
        self.record_var(var_name)
        if is_plural is True:
            self.scopes[-1]["last_plural"] = var_name
        elif is_plural is False:
            self.scopes[-1]["last_singular"] = var_name
        else:
            lower = var_name.lower()
            if lower in ("sender", "actor", "author", "creator", "caller", "source", "user"):
                self.scopes[-1]["last_subject"] = var_name
            elif lower in ("recipient", "target", "receiver", "callee", "dest", "destination"):
                self.scopes[-1]["last_object"] = var_name

            if lower.endswith(("s", "list", "array", "collection", "batch", "data", "records", "items", "results", "table")) and not lower.endswith(("is", "ss", "us")):
                self.scopes[-1]["last_plural"] = var_name
            else:
                self.scopes[-1]["last_singular"] = var_name

    def mark_diverged(self):
        self.scopes[-1]["diverged"] = True
        self.scopes[-1]["last_var"] = None
        self.scopes[-1]["last_singular"] = None
        self.scopes[-1]["last_plural"] = None

    def get_last_var(self) -> Optional[str]:
        return self.scopes[-1]["last_var"]

    def get_last_singular(self) -> Optional[str]:
        return self.scopes[-1]["last_singular"]

    def get_last_plural(self) -> Optional[str]:
        return self.scopes[-1]["last_plural"]

    def get_last_subject(self) -> Optional[str]:
        return self.scopes[-1].get("last_subject") or self.scopes[-1].get("last_singular") or self.scopes[-1].get("last_var")

    def get_last_object(self) -> Optional[str]:
        return self.scopes[-1].get("last_object") or self.scopes[-1].get("last_singular") or self.scopes[-1].get("last_var")

    @property
    def in_class(self) -> bool:
        return self.scopes[-1].get("in_class", False)

    @in_class.setter
    def in_class(self, val: bool):
        self.scopes[-1]["in_class"] = val


# Helper regex to detect variable assignment targets
ASSIGN_VAR_PATTERNS = [
    re.compile(r"^\s*set\s+([A-Za-z_]\w*)\s+to\b", re.IGNORECASE),
    re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(?!=\s*)"),
    re.compile(r"^\s*let\s+([A-Za-z_]\w*)\s*=\s*", re.IGNORECASE),
    re.compile(r"^\s*let\s+([A-Za-z_]\w*)\s+be\b", re.IGNORECASE),
    re.compile(r"^\s*increase\s+([A-Za-z_]\w*)\s+by\b", re.IGNORECASE),
    re.compile(r"^\s*decrease\s+([A-Za-z_]\w*)\s+by\b", re.IGNORECASE),
    re.compile(r"\binto\s+([A-Za-z_]\w*)\s*$", re.IGNORECASE),
    re.compile(r"^\s*for\s+each\s+([A-Za-z_]\w*)\s+in\b", re.IGNORECASE),
]

def extract_assigned_var(code: str) -> Optional[str]:
    for pat in ASSIGN_VAR_PATTERNS:
        m = pat.search(code)
        if m:
            target = m.group(1)
            if target.lower() not in ("it", "that"):
                return target
    return None


# ---------------------------------------------------------------------------
# UNITS OF MEASUREMENT DATA & NORMALIZATION
# ---------------------------------------------------------------------------

COMPOUND_UNITS = [
    "degrees fahrenheit", "degree fahrenheit",
    "degrees celsius", "degree celsius",
    "miles per hour", "mile per hour",
    "kilometers per hour", "kilometer per hour",
    "meters per second", "meter per second",
    "feet per second", "foot per second",
    "nautical miles", "nautical mile",
    "fluid ounces", "fluid ounce",
    "pounds sterling", "pound sterling",
    "kilowatt hours", "kilowatt hour",
]

SINGLE_UNITS = [
    "kilometers", "kilometer", "km",
    "millimeters", "millimeter", "mm",
    "centimeters", "centimeter", "cm",
    "nanometers", "nanometer", "nm",
    "micrometers", "micrometer", "microns", "micron", "um",
    "meters", "meter",
    "inches", "inch",
    "feet", "foot", "ft",
    "yards", "yard", "yd",
    "miles", "mile", "mi",
    "milliseconds", "millisecond", "ms",
    "microseconds", "microsecond", "us",
    "nanoseconds", "nanosecond", "ns",
    "seconds", "second", "sec",
    "minutes", "minute", "min",
    "hours", "hour", "hr",
    "days", "day",
    "weeks", "week",
    "kilograms", "kilogram", "kg",
    "milligrams", "milligram", "mg",
    "micrograms", "microgram", "ug",
    "grams", "gram",
    "ounces", "ounce", "oz",
    "pounds", "pound", "lbs", "lb",
    "tonnes", "tonne",
    "tons", "ton",
    "petabytes", "petabyte", "pb",
    "terabytes", "terabyte", "tb",
    "gigabytes", "gigabyte", "gb",
    "megabytes", "megabyte", "mb",
    "kilobytes", "kilobyte", "kb",
    "bytes", "byte",
    "bits", "bit",
    "celsius", "fahrenheit", "kelvin",
    "milliliters", "milliliter", "ml",
    "liters", "liter",
    "gallons", "gallon", "gal",
    "quarts", "quart", "qt",
    "pints", "pint", "pt",
    "cups", "cup",
    "fl oz",
    "dollars", "dollar", "usd",
    "cents", "cent",
    "euros", "euro", "eur",
    "yen", "jpy", "gbp",
    "kilojoules", "kilojoule", "kj",
    "joules", "joule",
    "kilocalories", "kilocalorie", "kcal",
    "calories", "calorie", "cal",
    "kilowatts", "kilowatt", "kw",
    "watts", "watt",
    "horsepower", "hp", "kwh",
    "knots", "knot",
]

ALL_UNITS = sorted(COMPOUND_UNITS + SINGLE_UNITS, key=lambda u: len(u), reverse=True)
ALL_UNITS_PAT = "|".join(re.escape(u) for u in ALL_UNITS)


def normalize_units_sub(text: str) -> str:
    """Normalizes numbers with units, currency symbols, and conversions inside expressions."""
    # Currency symbol prefixes: $100 -> make_quantity(100, "dollars"), $1,250.50
    text = re.sub(r"\$([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)\b", lambda m: f'make_quantity({m.group(1).replace(",", "")}, "dollars")', text)
    text = re.sub(r"€([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)\b", lambda m: f'make_quantity({m.group(1).replace(",", "")}, "euros")', text)
    text = re.sub(r"£([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)\b", lambda m: f'make_quantity({m.group(1).replace(",", "")}, "pounds sterling")', text)

    # Protect relative time: \d+ days from now, \d+ hours ago
    rel_saved = []
    def save_rel(m):
        rel_saved.append(m.group(0))
        return f"__REL_TIME_{len(rel_saved)-1}__"

    text = re.sub(
        r"\b\d+(?:\.\d+)?\s+(?:days?|hours?|minutes?|seconds?|weeks?|months?|years?)\s+(?:from\s+now|ago)\b",
        save_rel,
        text,
        flags=re.IGNORECASE,
    )

    # Number followed by unit: 60 miles per hour, 2.5 hours, 10 km
    text = re.sub(
        rf"\b([0-9]+(?:\.[0-9]+)?)\s+({ALL_UNITS_PAT})\b",
        lambda m: f'make_quantity({m.group(1)}, "{m.group(2).strip().lower()}")',
        text,
        flags=re.IGNORECASE,
    )

    # Contextual 'in <unit>' conversions
    # 1. After say / print / display / show / tell: 'say distance in miles'
    text = re.sub(
        rf"\b(say|show|print|display|tell)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+in\s+({ALL_UNITS_PAT})\b",
        lambda m: f'{m.group(1)} convert_unit({m.group(2)}, "{m.group(3).strip().lower()}")',
        text,
        flags=re.IGNORECASE,
    )

    # 2. After assignment (to, =): 'set dist_mi to distance in miles', 'dist_mi = distance in miles'
    text = re.sub(
        rf"(\bto\s+|=\s*)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+in\s+({ALL_UNITS_PAT})\b",
        lambda m: f'{m.group(1)}convert_unit({m.group(2)}, "{m.group(3).strip().lower()}")',
        text,
        flags=re.IGNORECASE,
    )

    # 3. Inside parentheses: '(distance in miles)'
    text = re.sub(
        rf"(\(\s*)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+in\s+({ALL_UNITS_PAT})\b",
        lambda m: f'{m.group(1)}convert_unit({m.group(2)}, "{m.group(3).strip().lower()}")',
        text,
        flags=re.IGNORECASE,
    )

    # 4. In condition before comparison operator: 'if distance in miles > 5:'
    text = re.sub(
        rf"\b(if|where|while)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+in\s+({ALL_UNITS_PAT})\s*(==|!=|<=|>=|<|>|equals\b|is\b)",
        lambda m: f'{m.group(1)} convert_unit({m.group(2)}, "{m.group(3).strip().lower()}") {m.group(4)}',
        text,
        flags=re.IGNORECASE,
    )

    # 5. Quantity literal in unit: '72 degrees fahrenheit in celsius' -> make_quantity(...) in celsius
    text = re.sub(
        rf"(make_quantity\([^)]+\))\s+in\s+({ALL_UNITS_PAT})\b",
        lambda m: f'convert_unit({m.group(1)}, "{m.group(2).strip().lower()}")',
        text,
        flags=re.IGNORECASE,
    )

    # Restore relative time
    for idx, orig in enumerate(rel_saved):
        text = text.replace(f"__REL_TIME_{idx}__", orig)

    return text


def normalize_units(text: str) -> str:
    """Normalizes units of measurement statements and expressions."""
    # 1. Statement: convert <expr> to <unit> into <target>
    m_conv_into = re.match(
        rf"^\s*convert\s+(.+?)\s+to\s+({ALL_UNITS_PAT})\s+into\s+([A-Za-z_]\w*)\s*$",
        text,
        re.IGNORECASE,
    )
    if m_conv_into:
        expr = m_conv_into.group(1).strip()
        unit = m_conv_into.group(2).strip().lower()
        target = m_conv_into.group(3).strip()
        expr_norm = normalize_units_sub(expr)
        return f'set {target} to convert_unit({expr_norm}, "{unit}")'

    # 2. Expression: convert <expr> to <unit>
    text = re.sub(
        rf"\bconvert\s+(.+?)\s+to\s+({ALL_UNITS_PAT})\b",
        lambda m: f'convert_unit({normalize_units_sub(m.group(1).strip())}, "{m.group(2).strip().lower()}")',
        text,
        flags=re.IGNORECASE,
    )

    return normalize_units_sub(text)


# ---------------------------------------------------------------------------
# STATEMENT NORMALIZATION PIPELINE
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# PHASE A-D DESUGARING HELPERS
# ---------------------------------------------------------------------------

RESERVED_OF_PROPS: Set[str] = {
    "first", "last", "count", "length", "size", "sum", "total", "average", "avg", "mean",
    "median", "variance", "stdev", "std_dev", "min", "max", "minimum", "maximum", "highest", "lowest",
    "keys", "values", "items", "item", "element", "member", "all", "any",
    "none", "each", "both", "either", "neither", "one", "many",
    "type", "percent", "square_root", "sqrt", "square", "root",
    "absolute", "abs", "reverse", "reversed", "unique", "take", "drop",
    "head", "tail", "uppercase", "lowercase", "trim", "strip", "pairs",
    "list", "dictionary", "set", "tuple", "number", "text", "boolean",
    "sort", "sorted", "chart", "plot", "histogram", "summary", "copy",
    "round", "rounded", "function", "preview", "entries", "words", "lines",
    "characters", "chars", "token", "tokens", "deviation", "standard",
    "union", "intersection", "difference", "scatter", "adler32", "crc32",
    "sha256", "md5", "line", "bar", "pie", "area", "box", "heatmap", "lenght",
    "out", "case", "title", "result", "results", "remainder", "product", "half",
    "quarter", "third", "double", "triple", "most", "majority", "minority", "few", "several"
}


def desugar_pipe(code: str) -> str:
    """Desugars pipeline chaining |> into nested calls or assignments."""
    if "|>" not in code:
        return code
    into_m = re.search(r"\binto\s+([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    set_m = re.match(r"^\s*set\s+([A-Za-z_]\w*)\s+to\s+(.+)$", code, re.IGNORECASE)
    target = None
    if set_m:
        target = set_m.group(1).strip()
        pipe_part = set_m.group(2).strip()
    elif into_m:
        target = into_m.group(1).strip()
        pipe_part = code[:into_m.start()].strip()
    else:
        pipe_part = code.strip()

    segments = [s.strip() for s in pipe_part.split("|>")]
    curr = segments[0]
    for seg in segments[1:]:
        m_take = re.match(r"^take\s+(\d+|[A-Za-z_]\w*)(?:\s+(?:items|from))?$", seg, re.IGNORECASE)
        m_drop = re.match(r"^drop\s+(\d+|[A-Za-z_]\w*)(?:\s+(?:items|from))?$", seg, re.IGNORECASE)
        m_sort_by = re.match(r"^(?:sort|sorted)\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|desc|ascending|asc))?$", seg, re.IGNORECASE)
        m_sort = re.match(r"^(?:sort|sorted)(?:\s+(descending|desc|ascending|asc))?$", seg, re.IGNORECASE)
        m_join = re.match(r"^join(?:\s+(?:with|by))?\s+(.+)$", seg, re.IGNORECASE)
        m_uniq = re.match(r"^unique(?:\s+items)?$", seg, re.IGNORECASE)
        m_upper = re.match(r"^(?:uppercase|upper)$", seg, re.IGNORECASE)
        m_lower = re.match(r"^(?:lowercase|lower)$", seg, re.IGNORECASE)
        m_trim = re.match(r"^trim$", seg, re.IGNORECASE)
        m_count = re.match(r"^(?:count|length)$", seg, re.IGNORECASE)
        m_rev = re.match(r"^(?:reverse|reversed)$", seg, re.IGNORECASE)
        m_flat = re.match(r"^flatten$", seg, re.IGNORECASE)

        if m_take:
            curr = f"ds_take({curr}, {m_take.group(1)})"
        elif m_drop:
            curr = f"ds_drop({curr}, {m_drop.group(1)})"
        elif m_sort_by:
            rev = "True" if m_sort_by.group(2) and m_sort_by.group(2).lower() in ("desc", "descending") else "False"
            curr = f"ds_sorted_by({curr}, '{m_sort_by.group(1)}', reverse={rev})"
        elif m_sort:
            rev = "True" if m_sort.group(1) and m_sort.group(1).lower() in ("desc", "descending") else "False"
            curr = f"sorted({curr}, reverse={rev})"
        elif m_join:
            curr = f"ds_join({curr}, {m_join.group(1)})"
        elif m_uniq:
            curr = f"list(dict.fromkeys({curr}))"
        elif m_upper:
            curr = f"ds_uppercase({curr})"
        elif m_lower:
            curr = f"ds_lowercase({curr})"
        elif m_trim:
            curr = f"ds_trim({curr})"
        elif m_count:
            curr = f"len({curr})"
        elif m_rev:
            curr = f"ds_reversed({curr})"
        elif m_flat:
            curr = f"ds_flatten({curr})"
        else:
            curr = f"{seg}({curr})"

    if target:
        return f"set {target} to {curr}"
    return curr


def desugar_articles(masked: str) -> str:
    """Tolerates optional English articles the, a, an before identifiers and clauses."""
    masked = re.sub(r"^\s*set\s+the\s+([A-Za-z_]\w*)\s+to\b", r"set \1 to", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*the\s+(?!result\b|answer\b|goal\s+is\s+to\b)([A-Za-z_]\w*)\s+(?:is|=)\s+(?!even\b|odd\b|positive\b|negative\b|zero\b|empty\b|not\b)(.+)$", r"set \1 to \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bto\s+the\s+([A-Za-z_]\w*)\b", r"to \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bfrom\s+the\s+([A-Za-z_]\w*)\b", r"from \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bby\s+the\s+([A-Za-z_]\w*)\b", r"by \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bin\s+the\s+(?!worst\s+case\b)([A-Za-z_]\w*)\b", r"in \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bof\s+the\s+([A-Za-z_]\w*)\b", r"of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*the\s+(count|length|first|last|sum|average|mean|median|min|max|highest|lowest)\s+of\b", r"\1 of", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:say|print)\s+the\s+([A-Za-z_]\w*)\b", r"say \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(if|unless|while|until)\s+the\s+([A-Za-z_]\w*)\b", r"\1 \2", masked, flags=re.IGNORECASE)
    return masked


def desugar_currency_and_scale(text: str) -> str:
    """Normalizes magnitude suffixes (k, million, billion), and percentage literals (preserving currency symbols for units system)."""
    text = re.sub(r"\b(\d+(?:\.\d+)?)\s*(?:million|mil)\b", lambda m: str(float(m.group(1)) * 1_000_000), text, flags=re.IGNORECASE)
    text = re.sub(r"\b(\d+(?:\.\d+)?)\s*billion\b", lambda m: str(float(m.group(1)) * 1_000_000_000), text, flags=re.IGNORECASE)
    text = re.sub(r"(?<![A-Za-z_])(\d+(?:\.\d+)?)k\b", lambda m: str(int(float(m.group(1)) * 1_000)), text, flags=re.IGNORECASE)
    text = re.sub(r"(?<![A-Za-z0-9_.])(\d+(?:\.\d+)?)%(?!\s+(?:of\b|off\b|on\b|markup\b|tax\b))", r"(\1 / 100.0)", text)
    return text


def desugar_prepositions(text: str) -> str:
    """Normalizes preposition flexibility across take/drop/join/split."""
    text = re.sub(r"\btake\s+(\d+|[A-Za-z_]\w*)(?:\s+items)?\s+of\s+([A-Za-z_]\w*)\b", r"take \1 items from \2", text, flags=re.IGNORECASE)
    text = re.sub(r"\bdrop\s+(\d+|[A-Za-z_]\w*)(?:\s+items)?\s+of\s+([A-Za-z_]\w*)\b", r"drop \1 items from \2", text, flags=re.IGNORECASE)
    text = re.sub(r"\bjoin\s+([A-Za-z_]\w*)\s+by\s+(.+?)(?=\s+into\b|\s*$)", r"join \1 with \2", text, flags=re.IGNORECASE)
    text = re.sub(r"\bsplit\s+(.+?)\s+with\s+(.+?)(?=\s+into\b|\s*$)", r"split \1 by \2", text, flags=re.IGNORECASE)
    return text


def desugar_multi_sort(code: str) -> str:
    """Desugars multi-field sorting into ds_sorted_by_multi."""
    m = re.match(r"^\s*sort\s+([A-Za-z_]\w*)\s+by\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    if not m:
        return code
    coll = m.group(1)
    spec_str = m.group(2)
    target = m.group(3)
    if ' and ' not in spec_str and ',' not in spec_str:
        return code
    parts = [p.strip() for p in re.split(r",|\band\b", spec_str) if p.strip()]
    specs = []
    for p in parts:
        words = p.split()
        field = words[0]
        desc = "False"
        if len(words) > 1 and words[1].lower() in ("desc", "descending", "down"):
            desc = "True"
        specs.append(f'("{field}", {desc})')
    specs_lit = "[" + ", ".join(specs) + "]"
    return f"set {target} to ds_sorted_by_multi({coll}, {specs_lit})"


def desugar_multi_group(code: str) -> str:
    """Desugars multi-key grouping with aggregation into ds_group_by_multi."""
    m = re.match(
        r"^\s*group\s+([A-Za-z_]\w*)\s+by\s+(.+?)\s+calculating\s+(sum|total|avg|average|mean|max|highest|min|lowest|count)\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)\s*$",
        code,
        re.IGNORECASE
    )
    if not m:
        return code
    coll = m.group(1)
    keys_str = m.group(2)
    agg_op = m.group(3).lower()
    agg_field = m.group(4)
    target = m.group(5)
    keys = [k.strip() for k in re.split(r",|\band\b", keys_str) if k.strip()]
    keys_lit = "[" + ", ".join(f'"{k}"' for k in keys) + "]"
    return f'set {target} to ds_group_by_multi({coll}, {keys_lit}, "{agg_op}", "{agg_field}")'


def desugar_background(code: str) -> str:
    """Desugars background execution and task synchronization."""
    m1 = re.match(r"^\s*run\s+in\s+background\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    if m1:
        action = m1.group(1).strip()
        task = m1.group(2).strip()
        return f"set {task} to ds_run_background(lambda: {action})"
    m2 = re.match(r"^\s*wait\s+for\s+all\s+tasks\s+in\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    if m2:
        return f"set {m2.group(2).strip()} to ds_wait_tasks({m2.group(1).strip()})"
    m3 = re.match(r"^\s*wait\s+for\s+all\s+tasks\s+in\s+([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    if m3:
        return f"ds_wait_tasks({m3.group(1).strip()})"
    m4 = re.match(r"^\s*wait\s+for\s+(?:task\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    if m4:
        return f"set {m4.group(2).strip()} to wait_for_thread({m4.group(1).strip()})"
    m5 = re.match(r"^\s*wait\s+for\s+(?:task\s+)?([A-Za-z_]\w*)\s*$", code, re.IGNORECASE)
    if m5 and m5.group(1).lower() not in ("all", "until"):
        return f"wait_for_thread({m5.group(1).strip()})"
    return code


def desugar_field_access(text: str) -> str:
    """Desugars natural field access <prop> of <target> into <target>.<prop>."""
    def repl(m):
        prop = m.group(1)
        target = m.group(2)
        if prop.lower() in RESERVED_OF_PROPS or target.lower() in ('length', 'size', 'type', 'buffer', 'string', 'number', 'text', 'each', 'every', 'all', 'any', 'none'):
            return m.group(0)
        start = m.start()
        prefix = text[:start].rstrip()
        if not prefix and re.search(r"\binto\s+[A-Za-z_]\w*\s*$", text[start:]):
            return m.group(0)
        if re.search(r"\b(?:sum|total|average|avg|mean|median|variance|stdev|highest|lowest|max|min|count|size|length|chart|plot)\s+of$", prefix, re.I):
            return m.group(0)
        if re.search(r"\bsquare$", prefix, re.I):
            return m.group(0)
        return f"{target}.{prop}"
    pat = r"(?<!\bfirst\s)(?<!\blast\s)(?<!\bitem\s)(?<!\bitems\s)\b([A-Za-z_]\w*)\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|\[[^\]]+\])*)\b"
    return re.sub(pat, repl, text, flags=re.IGNORECASE)


def desugar_multi_subject_predicates(masked: str) -> str:
    """Desugars multi-subject agreement (all of, any of, none of) for collections and list literals."""
    target_pat = r"(\[[^\]]+\]|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])*)"
    masked = re.sub(rf"\ball\s+of\s+{target_pat}\s+(?:is|are)\s+positive\b", r"ds_all_positive(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\ball\s+of\s+{target_pat}\s+(?:is|are)\s+negative\b", r"ds_all_negative(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\ball\s+of\s+{target_pat}\s+(?:is|are)\s+even\b", r"ds_all_even(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\ball\s+of\s+{target_pat}\s+(?:is|are)\s+odd\b", r"ds_all_odd(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\ball\s+of\s+{target_pat}\s+(?:is|are)\s+zero\b", r"ds_all_zero(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bany\s+of\s+{target_pat}\s+(?:is|are)\s+positive\b", r"ds_any_positive(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bany\s+of\s+{target_pat}\s+(?:is|are)\s+negative\b", r"ds_any_negative(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bany\s+of\s+{target_pat}\s+(?:is|are)\s+even\b", r"ds_any_even(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bany\s+of\s+{target_pat}\s+(?:is|are)\s+odd\b", r"ds_any_odd(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bany\s+of\s+{target_pat}\s+(?:is|are)\s+zero\b", r"ds_any_zero(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bnone\s+of\s+{target_pat}\s+(?:is|are)\s+positive\b", r"ds_none_positive(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bnone\s+of\s+{target_pat}\s+(?:is|are)\s+negative\b", r"ds_none_negative(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bnone\s+of\s+{target_pat}\s+(?:is|are)\s+zero\b", r"ds_none_zero(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bnone\s+of\s+{target_pat}\s+(?:is|are)\s+even\b", r"all(_x % 2 != 0 for _x in \1)", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\bnone\s+of\s+{target_pat}\s+(?:is|are)\s+odd\b", r"all(_x % 2 == 0 for _x in \1)", masked, flags=re.IGNORECASE)
    return masked

def normalize_statement_text(stmt: str, scope: ScopeTracker, line_num: int) -> str:
    """Normalizes a single statement (without comments or leading indent)."""
    text = stmt.strip()
    if not text:
        return ""

    # Mask strings
    masked, strings = mask_strings(text)

    # 1. Strip leading filler words (please, kindly, just, simply, then)
    for filler in LEADING_FILLERS:
        pattern = re.compile(rf"^{re.escape(filler)}\s+(?![=,])", re.IGNORECASE)
        if pattern.match(masked):
            masked = pattern.sub("", masked)
            break

    # Sentence-style keyword case normalization (e.g. Say, Set, Let, Make, If, Repeat, For, While, Attempt, Try)
    first_word_m = re.match(r"^([A-Za-z_]\w*)(\s+.*|$)", masked)
    if first_word_m:
        w1 = first_word_m.group(1)
        w1_lower = w1.lower()
        if w1_lower in STATEMENT_START_KEYWORDS and w1 != w1_lower:
            masked = w1_lower + first_word_m.group(2)

    # Early desugaring: Pipe operator, articles, currency/scale, prepositions, background, multi-sort, multi-group, field access
    masked = desugar_pipe(masked)
    masked = desugar_articles(masked)
    masked = desugar_currency_and_scale(masked)
    masked = desugar_prepositions(masked)
    masked = desugar_background(masked)
    masked = desugar_multi_sort(masked)
    masked = desugar_multi_group(masked)
    masked = re.sub(r"\bsquare\s+root\s+of\b", "sqrt of", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bsquare\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?|\d+(?:\.\d+)?|\([^)]+\))", r"((\1) ** 2)", masked, flags=re.IGNORECASE)
    masked = desugar_field_access(masked)

    # Units of measurement normalization (numbers with units, conversions, currency)
    # Paradigm 36: Relative Time Offsets (before and after units normalization)
    def _repl_time_ago(m):
        unit = m.group(2).lower().rstrip('s') + 's'
        return f"ds_time_ago({unit}={m.group(1)})"

    def _repl_time_from_now(m):
        unit = m.group(2).lower().rstrip('s') + 's'
        return f"ds_time_from_now({unit}={m.group(1)})"

    masked = re.sub(r"\b(\d+)\s+(days?|hours?|minutes?|seconds?)\s+ago\b", _repl_time_ago, masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bin\s+(\d+)\s+(days?|hours?|minutes?|seconds?)\b", _repl_time_from_now, masked, flags=re.IGNORECASE)

    masked = normalize_units(masked)

    masked = re.sub(r'\bin\s+make_quantity\s*\(\s*(\d+)\s*,\s*["\'](\w+)["\']\s*\)', _repl_time_from_now, masked, flags=re.IGNORECASE)

    # Compositional: Ternary assignment: set <var> to <val1> if <cond> otherwise <val2>
    ternary_assign_m = re.match(
        r"^\s*set\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+to\s+(.+?)\s+if\s+(.+?)\s+(?:otherwise|else)\s+(.+)$",
        masked,
        re.IGNORECASE,
    )
    if ternary_assign_m:
        t_var = ternary_assign_m.group(1).strip()
        t_then = ternary_assign_m.group(2).strip()
        t_cond = ternary_assign_m.group(3).strip()
        t_else = ternary_assign_m.group(4).strip()
        masked = f"set {t_var} to ds_ternary({t_cond}, {t_then}, {t_else})"

    # Compositional: Prefix ternary assignment: set <var> to if <cond> then <val1> otherwise <val2>
    ternary_prefix_m = re.match(
        r"^\s*set\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+to\s+if\s+(.+?)\s+then\s+(.+?)\s+(?:otherwise|else)\s+(.+)$",
        masked,
        re.IGNORECASE,
    )
    if ternary_prefix_m:
        t_var = ternary_prefix_m.group(1).strip()
        t_cond = ternary_prefix_m.group(2).strip()
        t_then = ternary_prefix_m.group(3).strip()
        t_else = ternary_prefix_m.group(4).strip()
        masked = f"set {t_var} to ds_ternary({t_cond}, {t_then}, {t_else})"

    # Compositional: set <var> to <coll> whose <field> <cmp> <val>
    whose_expr_m = re.match(
        r"^\s*set\s+([A-Za-z_]\w*)\s+to\s+([A-Za-z_]\w*)\s+whose\s+([A-Za-z_]\w*)\s+(is|equals|==|!=|>|<|>=|<=)\s+(.+)$",
        masked,
        re.IGNORECASE,
    )
    if whose_expr_m:
        t_var = whose_expr_m.group(1).strip()
        coll = whose_expr_m.group(2).strip()
        attr = whose_expr_m.group(3).strip()
        cmp_op = whose_expr_m.group(4).strip()
        val = whose_expr_m.group(5).strip()
        norm_cmp = "==" if cmp_op.lower() in ("is", "equals") else cmp_op
        masked = f"set {t_var} to [item for item in {coll} if ds_attr(item, '{attr}') {norm_cmp} {val}]"

    # Compositional: Inline expression sort: sort <list> descending/ascending
    if not re.match(r"^\s*sort\s+(?:the\s+)?([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+(?:descending|ascending)\s*$", masked, re.IGNORECASE):
        masked = re.sub(r"\bsort\s+(\[[^\]]+\]|[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+descending\b", r"sorted_list(\1, reverse=True)", masked, flags=re.IGNORECASE)
        masked = re.sub(r"\bsort\s+(\[[^\]]+\]|[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+ascending\b", r"sorted_list(\1, reverse=False)", masked, flags=re.IGNORECASE)

    # Phase 5: Data Science Verbs over pandas
    masked = re.sub(
        r"^\s*load\s+table\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"\2 = load_table(\1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*save\s+table\s+(.+?)\s+(?:into|to)\s+(.+?)\s*$",
        r"save_table(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*filter\s+([A-Za-z_]\w*)\s+where\s+([A-Za-z_]\w*)\s*(==|!=|>=|<=|>|<|is\s+greater\s+than|is\s+at\s+least|is\s+less\s+than|is\s+at\s+most|is\s+not|equals|is)\s*(.+?)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"\5 = filter_table(\1, '\2', '\3', \4)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*sort\s+([A-Za-z_]\w*)\s+by\s+([A-Za-z_]\w*)\s+(?:descending|in\s+descending\s+order)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"\3 = sort_table(\1, '\2', ascending=False)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*sort\s+([A-Za-z_]\w*)\s+by\s+([A-Za-z_]\w*)\s*(?:ascending|in\s+ascending\s+order)?\s+into\s+([A-Za-z_]\w*)\s*$",
        r"\3 = sort_table(\1, '\2', ascending=True)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*group\s+([A-Za-z_]\w*)\s+by\s+([A-Za-z_]\w*)\s+and\s+(?:average|mean)\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"\4 = group_and_agg_table(\1, '\2', '\3', 'mean')",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*group\s+([A-Za-z_]\w*)\s+by\s+([A-Za-z_]\w*)\s+and\s+sum\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"\4 = group_and_agg_table(\1, '\2', '\3', 'sum')",
        masked,
        flags=re.IGNORECASE
    )

    # Filter statements starting with 'filter': filter <coll> where <cond> into <target>
    masked = re.sub(r"^\s*filter\s+(.+?\s+where\s+.+?\s+into\s+[A-Za-z_]\w*)$", r"\1", masked, flags=re.IGNORECASE)

    # Compositional: Inline expression filter: filter <list> where <var> is ...
    filter_expr_m = re.search(r"\bfilter\s+(\[[^\]]+\]|[A-Za-z_]\w*)\s+where\s+([A-Za-z_]\w*)\s+(is\s+[A-Za-z_]\w*|==.+?|!=.+?|>.*|<.*|>=.*|<=.*)", masked, re.IGNORECASE)
    if filter_expr_m:
        f_coll, f_var, f_pred = filter_expr_m.group(1), filter_expr_m.group(2), filter_expr_m.group(3)
        masked = masked.replace(filter_expr_m.group(0), f"[{f_var} for {f_var} in {f_coll} if {f_var} {f_pred}]")


    # Normalize 'attempt' to 'try'
    if re.match(r"^attempt\b", masked, re.IGNORECASE):
        masked = re.sub(r"^attempt\b", "try", masked, flags=re.IGNORECASE)

    # If or unless condition ending in 'then' -> replace with ':'
    if re.match(r"^(?:if|unless)\s+.+\s+then$", masked, re.IGNORECASE):
        masked = re.sub(r"\s+then$", ":", masked, flags=re.IGNORECASE)

    # Pre-normalize and protect assert that / make sure [that] / check that / assert
    masked = re.sub(r"^\s*(?:make\s+sure(?:\s+that)?|assert(?:\s+that)?|check\s+that)\s+(.+?)\s+otherwise\s+(.+)$", r"verify that \1 otherwise \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:make\s+sure(?:\s+that)?|assert(?:\s+that)?|check\s+that)\s+(.+)$", r'verify that \1 otherwise "Check failed"', masked, flags=re.IGNORECASE)

    # Pillar A: Conversational hypotheses and intentional definitions
    masked = re.sub(
        r"^\s*(?:suppose|assume|let's\s+say)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+(?:is|=)\s+(.+)$",
        r"set \1 to \2",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:remember|store)\s+(.+?)\s+as\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \2 to \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:how\s+to|in\s+order\s+to|the\s+goal\s+is\s+to)\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?))?:?$",
        lambda m: f"to {m.group(1)} with {m.group(2)}:" if m.group(2) else f"to {m.group(1)}:",
        masked,
        flags=re.IGNORECASE
    )

    # Pillar B: Stream-of-thought control flow and natural guards
    masked = re.sub(r"^\s*try\s+to:?$", r"try:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*as\s+long\s+as\s+(.+?):?$", r"while \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*for\s+(?:each\s+and\s+every|every)\s+([A-Za-z_]\w*)\s+in\s+([^:\n]+?):?$", r"for each \1 in \2:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*in\s+case\s+(?:of\s+)?(.+?):?$", r"if \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*in\s+(?:the\s+)?worst\s+case:?$", r"else:", masked, flags=re.IGNORECASE)

    # For loop with index: 'for each item and its index in items:'
    masked = re.sub(
        r"^\s*for\s+(?:each\s+)?([A-Za-z_]\w*)\s+and\s+(?:its|their|his|her)\s+index\s+in\s+(.+?):?$",
        r"for each index, \1 in ds_enumerate(\2):",
        masked,
        flags=re.IGNORECASE
    )

    # Quantifiers & multi-subject predicates
    masked = desugar_multi_subject_predicates(masked)

    _reserved_query_words = {
        'and', 'or', 'not', 'is', 'in', 'true', 'false', 'none', 'item', 'x',
        'at', 'least', 'most', 'greater', 'less', 'than', 'between', 'outside',
        'empty', 'even', 'odd', 'positive', 'negative', 'zero',
        'over', 'under', 'above', 'below', 'equal', 'equals', 'strictly', 'more',
        'identical', 'same', 'different', 'from', 'within', "isn't", 'inside'
    }

    def _normalize_query_cond(c: str) -> str:
        replacements = [
            (r"\bis\s+greater\s+than\s+or\s+equal\s+to\b", ">="),
            (r"\bis\s+less\s+than\s+or\s+equal\s+to\b", "<="),
            (r"\bis\s+strictly\s+greater\s+than\b", ">"),
            (r"\bis\s+strictly\s+less\s+than\b", "<"),
            (r"\bis\s+at\s+least\b", ">="),
            (r"\bis\s+at\s+most\b", "<="),
            (r"\bis\s+greater\s+than\b", ">"),
            (r"\bis\s+less\s+than\b", "<"),
            (r"\bis\s+more\s+than\b", ">"),
            (r"\bis\s+over\b", ">"),
            (r"\bis\s+under\b", "<"),
            (r"\bis\s+above\b", ">"),
            (r"\bis\s+below\b", "<"),
            (r"\bis\s+equal\s+to\b", "=="),
            (r"\bequal\s+to\b", "=="),
            (r"\bis\s+identical\s+to\b", "=="),
            (r"\bis\s+the\s+same\s+as\b", "=="),
            (r"\bequals\b", "=="),
            (r"\bequal\b", "=="),
            (r"\bdoes\s+not\s+equal\b", "!="),
            (r"\bis\s+not\s+equal\s+to\b", "!="),
            (r"\bis\s+not\b", "!="),
            (r"\bisn't\b", "!="),
            (r"\bis\s+even\b", "% 2 == 0"),
            (r"\bis\s+odd\b", "% 2 != 0"),
            (r"\bis\s+positive\b", "> 0"),
            (r"\bis\s+negative\b", "< 0"),
            (r"\bis\s+zero\b", "== 0"),
            (r"\bis\b", "=="),
        ]
        for pat, rep in replacements:
            c = re.sub(pat, rep, c, flags=re.IGNORECASE)
        return c

    def _bind_contextual_attrs(cond: str, var_name: str) -> str:
        cond = _normalize_query_cond(cond)
        if re.search(r"\b(x|item)\b", cond):
            return cond
        def _repl(m):
            w = m.group(1)
            if w.lower() in _reserved_query_words or w.startswith("__STR_"):
                return m.group(0)
            return f"ds_attr({var_name}, '{w}')"
        return re.sub(r"(?<![\w\.])([A-Za-z_]\w*)(?!\s*\()", _repl, cond)

    # Phase 4, Task 4.2: Relational Set Reshaping Syntax (pair, partition, flatten)
    pair_dict_m = re.match(r"^\s*pair\s+(.+?)\s+with\s+(.+?)\s+into\s+dictionary\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if pair_dict_m:
        e1 = pair_dict_m.group(1).strip()
        e2 = pair_dict_m.group(2).strip()
        tgt = pair_dict_m.group(3).strip()
        masked = f"set {tgt} to ds_pair({e1}, {e2}, as_dict=True)"

    pair_m = re.match(r"^\s*pair\s+(?!with\b)(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if pair_m:
        e1 = pair_m.group(1).strip()
        e2 = pair_m.group(2).strip()
        tgt = pair_m.group(3).strip()
        masked = f"set {tgt} to ds_pair({e1}, {e2})"

    part_m = re.match(r"^\s*partition\s+(.+?)\s+into\s+([A-Za-z_]\w*)(?:\s*,\s*|\s+and\s+|\s*,\s*and\s+)([A-Za-z_]\w*)\s+where\s+(.+?)$", masked, re.IGNORECASE)
    if part_m:
        coll = part_m.group(1).strip()
        t1 = part_m.group(2).strip()
        t2 = part_m.group(3).strip()
        cond = part_m.group(4).strip()
        var_name = "x" if re.search(r"\bx\b", cond) else "item"
        bound_cond = _bind_contextual_attrs(cond, var_name)
        masked = f"{t1}, {t2} = ds_partition({coll}, lambda {var_name}: {bound_cond})"

    flatten_m = re.match(r"^\s*flatten\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if flatten_m:
        coll = flatten_m.group(1).strip()
        tgt = flatten_m.group(2).strip()
        masked = f"set {tgt} to ds_flatten({coll})"

    # Phase 4, Task 4.3: Conversational Analytics Inquiries
    if masked.rstrip().endswith("?"):
        masked = masked.rstrip()[:-1].rstrip()

    how_many_m = re.match(
        r"^\s*how\s+many(?:\s+(?:items|elements|records|objects|rows))?\s+(?:in|of)\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
        masked,
        re.IGNORECASE
    )
    if how_many_m:
        coll = how_many_m.group(1).strip()
        tgt = how_many_m.group(2)
        if tgt:
            masked = f"set {tgt} to count of {coll}"
        else:
            masked = f"say count of {coll}"

    what_into_m = re.match(
        r"^\s*(?:what\s+is|what's)\s+(?:the\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE
    )
    if what_into_m:
        expr = what_into_m.group(1).strip()
        tgt = what_into_m.group(2).strip()
        masked = f"set {tgt} to {expr}"

    # Phase 3, Task 3.2: Adverbial Statement Qualifiers (retrying, timeout, caching)
    retry_m = re.match(
        r"^\s*(?:call\s+)?(.+?)\s+retrying\s+(\d+)\s+times(?:\s+with\s+(.+?)\s+backoff)?(?:\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?))?\s*$",
        masked,
        re.IGNORECASE
    )
    if retry_m:
        fn_expr = retry_m.group(1).strip()
        times_v = retry_m.group(2).strip()
        backoff_v = retry_m.group(3).strip() if retry_m.group(3) else "0.1"
        target_v = retry_m.group(4).strip() if retry_m.group(4) else None
        call_expr = f"{fn_expr}()" if not ("(" in fn_expr and fn_expr.endswith(")")) else fn_expr
        retry_call = f"ds_retry(lambda: {call_expr}, max_attempts={times_v}, backoff={backoff_v})"
        if target_v:
            masked = f"set {target_v} to {retry_call}"
        else:
            masked = retry_call

    # Paradigm 33: Synchronous Polling Guards
    wait_until_m = re.match(
        r"^\s*wait\s+until\s+(.+?)\s+with\s+timeout\s+of\s+(.+?)$",
        masked,
        re.IGNORECASE
    )
    if wait_until_m:
        masked = f"ds_wait_until(lambda: {wait_until_m.group(1).strip()}, timeout={wait_until_m.group(2).strip()})"
    elif re.match(r"^\s*wait\s+until\s+(.+?)\s*$", masked, re.IGNORECASE):
        wait_m = re.match(r"^\s*wait\s+until\s+(.+?)\s*$", masked, re.IGNORECASE)
        masked = f"ds_wait_until(lambda: {wait_m.group(1).strip()})"

    timeout_m = None
    if not masked.strip().startswith("ds_wait_until("):
        timeout_m = re.match(
            r"^\s*(?:call\s+)?(?!wait\s+until\b)(.+?)\s+with\s+timeout\s+of\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?))?\s*$",
            masked,
            re.IGNORECASE
        )
    if timeout_m:
        fn_expr = timeout_m.group(1).strip()
        secs_v = timeout_m.group(2).strip()
        target_v = timeout_m.group(3).strip() if timeout_m.group(3) else None
        call_expr = f"{fn_expr}()" if not ("(" in fn_expr and fn_expr.endswith(")")) else fn_expr
        timeout_call = f"ds_with_timeout(lambda: {call_expr}, seconds={secs_v})"
        if target_v:
            masked = f"set {target_v} to {timeout_call}"
        else:
            masked = timeout_call

    cache_m = re.match(
        r"^\s*(?:call\s+)?(.+?)\s+caching\s+for\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?))?\s*$",
        masked,
        re.IGNORECASE
    )
    if cache_m:
        fn_expr = cache_m.group(1).strip()
        dur_expr = cache_m.group(2).strip()
        target_v = cache_m.group(3).strip() if cache_m.group(3) else None
        call_expr = f"{fn_expr}()" if not ("(" in fn_expr and fn_expr.endswith(")")) else fn_expr
        cache_call = f"ds_cached_call('{fn_expr}', lambda: {call_expr}, ttl_seconds={dur_expr})"
        if target_v:
            masked = f"set {target_v} to {cache_call}"
        else:
            masked = cache_call

    # Phase 2, Task 2.4: Natural Superlatives
    superlative_m = re.match(
        r"^\s*find\s+(?:the\s+)?(largest|biggest|highest|maximum|cheapest|smallest|lowest|minimum|oldest|newest)\s+(?:[A-Za-z_]\w*\s+)?in\s+(.+?)(?:\s+by\s+([A-Za-z_]\w*))?\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        masked,
        re.IGNORECASE
    )
    if superlative_m:
        kind = superlative_m.group(1).lower()
        coll = superlative_m.group(2).strip()
        key_attr = f"'{superlative_m.group(3).strip()}'" if superlative_m.group(3) else "None"
        target = superlative_m.group(4).strip()
        order_arg = "'max'" if kind in ("largest", "biggest", "highest", "maximum", "oldest", "newest") else "'min'"
        masked = f"set {target} to ds_find_superlative({coll}, order={order_arg}, key={key_attr})"

    # Phase 2, Task 2.3: Relative Clauses in Loops ('whose')
    whose_loop_m = re.match(
        r"^\s*for\s+(?:each\s+)?([A-Za-z_]\w*)(?:\s+in\s+([A-Za-z_]\w*))?\s+whose\s+([A-Za-z_]\w*)\s+(is|==|equals|is at least|is at most|is greater than|is less than|is over|is under|>=|<=|<|>)\s+(.+?):?$",
        masked,
        re.IGNORECASE
    )
    if whose_loop_m:
        item_var = whose_loop_m.group(1).strip()
        coll_var = whose_loop_m.group(2).strip() if whose_loop_m.group(2) else (scope.get_last_plural() or f"{item_var}s")
        attr_name = whose_loop_m.group(3).strip()
        cmp_op = whose_loop_m.group(4).strip()
        val_expr = whose_loop_m.group(5).strip()
        if cmp_op.lower() in ("is", "equals"):
            cmp_op = "=="
        masked = f"for each {item_var} in {coll_var} where ds_attr({item_var}, '{attr_name}') {cmp_op} {val_expr}:"

    # Phase 1, Task 1.4: Universal, Existential & Negative Set Quantifiers
    def _parse_quant_predicate(var_name: str, mode: str, pred_str: str) -> str:
        p = pred_str.strip()
        if mode == "has":
            m_cmp = re.match(r"^([A-Za-z_]\w*)\s+(?:equal\s+to|equals|is|==)\s+(.+)$", p, re.IGNORECASE)
            if m_cmp:
                return f"ds_attr({var_name}, '{m_cmp.group(1)}') == {m_cmp.group(2).strip()}"
            m_implied = re.match(r"^([A-Za-z_]\w*)\s+([\"'].*[\"']|-?\d+(?:\.\d+)?|__STR_LITERAL_\d+__|True|False)$", p, re.IGNORECASE)
            if m_implied:
                return f"ds_attr({var_name}, '{m_implied.group(1)}') == {m_implied.group(2).strip()}"
            m_gt = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+)?(?:over|greater\s+than|>)\s+(.+)$", p, re.IGNORECASE)
            if m_gt:
                return f"ds_attr({var_name}, '{m_gt.group(1)}') > {m_gt.group(2).strip()}"
            m_lt = re.match(r"^([A-Za-z_]\w*)\s+(?:is\s+)?(?:under|less\s+than|<)\s+(.+)$", p, re.IGNORECASE)
            if m_lt:
                return f"ds_attr({var_name}, '{m_lt.group(1)}') < {m_lt.group(2).strip()}"
            return f"ds_quant_match({var_name}, '{p}')"
        else: # is
            low = p.lower()
            if low == "even":
                return f"({var_name} % 2 == 0)"
            if low == "odd":
                return f"({var_name} % 2 != 0)"
            if low == "positive":
                return f"({var_name} > 0)"
            if low == "negative":
                return f"({var_name} < 0)"
            if low == "zero":
                return f"({var_name} == 0)"
            if low == "empty":
                return f"(len({var_name}) == 0)"
            if low in ("not empty", "non-empty"):
                return f"(len({var_name}) > 0)"
            if low in ("true", "false", "none"):
                return f"({var_name} is {p})"
            if (p.startswith(("'", '"')) and p.endswith(("'", '"'))) or re.match(r"^-?\d+(?:\.\d+)?$", p):
                return f"({var_name} == {p})"
            m_comp = re.match(r"^(?:over|greater\s+than|>)\s+(.+)$", p, re.IGNORECASE)
            if m_comp:
                return f"({var_name} > {m_comp.group(1).strip()})"
            m_comp_lt = re.match(r"^(?:under|less\s+than|<)\s+(.+)$", p, re.IGNORECASE)
            if m_comp_lt:
                return f"({var_name} < {m_comp_lt.group(1).strip()})"
            if re.match(r"^[A-Za-z_]\w*$", p):
                return f"ds_quant_match({var_name}, '{p}')"
            return f"({var_name} == {p})"

    all_are_m = re.match(r"^\s*if\s+all\s+(?:of\s+)?(?:items\s+in\s+)?(.+?)\s+(?:are|have)\s+(.+?):?$", masked, re.IGNORECASE)
    if all_are_m:
        coll = all_are_m.group(1).strip()
        pred = all_are_m.group(2).strip()
        mode = "has" if re.search(r"\bhave\b", all_are_m.group(0), re.IGNORECASE) else "is"
        pred_code = _parse_quant_predicate("x", mode, pred)
        masked = f"if ds_every({coll}, lambda x: {pred_code}):"

    every_in_m = re.match(r"^\s*if\s+every\s+([A-Za-z_]\w*)\s+in\s+(.+?)\s+(is|has)\s+(.+?):?$", masked, re.IGNORECASE)
    if every_in_m:
        var = every_in_m.group(1).strip()
        coll = every_in_m.group(2).strip()
        mode = every_in_m.group(3).lower()
        pred = every_in_m.group(4).strip()
        pred_code = _parse_quant_predicate(var, mode, pred)
        masked = f"if ds_every({coll}, lambda {var}: {pred_code}):"

    any_in_m = re.match(r"^\s*if\s+any\s+([A-Za-z_]\w*)\s+in\s+(.+?)\s+(is|has)\s+(.+?):?$", masked, re.IGNORECASE)
    if any_in_m:
        var = any_in_m.group(1).strip()
        coll = any_in_m.group(2).strip()
        mode = any_in_m.group(3).lower()
        pred = any_in_m.group(4).strip()
        pred_code = _parse_quant_predicate(var, mode, pred)
        masked = f"if ds_any({coll}, lambda {var}: {pred_code}):"

    any_of_m = re.match(r"^\s*if\s+any\s+of\s+(.+?)\s+(is|has)\s+(.+?):?$", masked, re.IGNORECASE)
    if any_of_m:
        coll = any_of_m.group(1).strip()
        mode = any_of_m.group(2).lower()
        pred = any_of_m.group(3).strip()
        pred_code = _parse_quant_predicate("x", mode, pred)
        masked = f"if ds_any({coll}, lambda x: {pred_code}):"

    no_in_m = re.match(r"^\s*if\s+no\s+([A-Za-z_]\w*)\s+in\s+(.+?)\s+(is|has)\s+(.+?):?$", masked, re.IGNORECASE)
    if no_in_m:
        var = no_in_m.group(1).strip()
        coll = no_in_m.group(2).strip()
        mode = no_in_m.group(3).lower()
        pred = no_in_m.group(4).strip()
        pred_code = _parse_quant_predicate(var, mode, pred)
        masked = f"if ds_none({coll}, lambda {var}: {pred_code}):"

    none_of_m = re.match(r"^\s*if\s+none\s+of\s+(.+?)\s+(?:are|is|have|has)\s+(.+?):?$", masked, re.IGNORECASE)
    if none_of_m:
        coll = none_of_m.group(1).strip()
        pred = none_of_m.group(2).strip()
        pred_code = _parse_quant_predicate("x", "is", pred)
        masked = f"if ds_none({coll}, lambda x: {pred_code}):"

    # Pillar C: Thought Queries & Intuitive Filtering

    def _rewrite_keep_only(m):
        coll = m.group(1).strip()
        cond = m.group(2).strip()
        target = m.group(3).strip() if m.group(3) else coll
        var_name = "x" if re.search(r"\bx\b", cond) else "item"
        bound_cond = _bind_contextual_attrs(cond, var_name)
        return f"set {target} to [{var_name} for {var_name} in {coll} if {bound_cond}]"

    masked = re.sub(
        r"^\s*keep\s+only\s+(?:items\s+in\s+)?(.+?)\s+where\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?))?$",
        _rewrite_keep_only,
        masked,
        flags=re.IGNORECASE
    )

    def _rewrite_discard(m):
        coll = m.group(1).strip()
        cond = m.group(2).strip()
        target = m.group(3).strip() if m.group(3) else coll
        var_name = "x" if re.search(r"\bx\b", cond) else "item"
        bound_cond = _bind_contextual_attrs(cond, var_name)
        return f"set {target} to [{var_name} for {var_name} in {coll} if not ({bound_cond})]"

    masked = re.sub(
        r"^\s*discard\s+from\s+(.+?)\s+where\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?))?$",
        _rewrite_discard,
        masked,
        flags=re.IGNORECASE
    )

    def _rewrite_find_first(m):
        coll = m.group(1).strip()
        cond = m.group(2).strip()
        target = m.group(3).strip()
        var_name = "x" if re.search(r"\bx\b", cond) else "item"
        bound_cond = _bind_contextual_attrs(cond, var_name)
        return f"set {target} to ds_find_first({coll}, lambda {var_name}: {bound_cond})"

    masked = re.sub(
        r"^\s*find\s+first\s+in\s+(.+?)\s+where\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        _rewrite_find_first,
        masked,
        flags=re.IGNORECASE
    )

    masked = re.sub(
        r"^\s*check\s+if\s+(.+?)\s+contains\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \3 to (\2 in \1)",
        masked,
        flags=re.IGNORECASE
    )

    masked = re.sub(
        r"^\s*check\s+whether\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \2 to (\1)",
        masked,
        flags=re.IGNORECASE
    )

    # Phase 5: Thought-to-Code Dimensions (Aggregations, Percentages, Bulk Actions, Iterations, Properties)

    # 1. Declarative Aggregations & Query Filters
    def _rewrite_thought_agg(m):
        op = m.group(1).lower()
        field = m.group(2).strip()
        coll = m.group(3).strip()
        cond = m.group(4).strip() if m.group(4) else None
        if cond:
            var_name = "x" if re.search(r"\bx\b", cond) else "item"
            if coll.endswith("s") and len(coll) > 2:
                singular = coll[:-1]
                cond = re.sub(rf"\b{singular}\.(?=[A-Za-z_])", f"{var_name}.", cond)
            bound = _bind_contextual_attrs(cond, var_name)
            return f"ds_query_agg('{op}', '{field}', {coll}, lambda {var_name}: {bound})"
        return f"ds_query_agg('{op}', '{field}', {coll})"

    masked = re.sub(
        r"\b(sum|total|average|mean|highest|maximum|lowest|minimum)\s+(?:of\s+)?([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)*)(?:\s+where\s+([^,:\n\(\)]+?))?(?=[,:\n\)]|$)",
        _rewrite_thought_agg,
        masked,
        flags=re.IGNORECASE
    )

    def _rewrite_thought_count(m):
        coll = m.group(1).strip()
        cond = m.group(2).strip()
        var_name = "x" if re.search(r"\bx\b", cond) else "item"
        if coll.endswith("s") and len(coll) > 2:
            singular = coll[:-1]
            cond = re.sub(rf"\b{singular}\.(?=[A-Za-z_])", f"{var_name}.", cond)
        bound = _bind_contextual_attrs(cond, var_name)
        return f"ds_query_agg('count', None, {coll}, lambda {var_name}: {bound})"

    masked = re.sub(
        r"\b(?:count\s+of|number\s+of|how\s+many)\s+(?:items\s+in\s+)?([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)*)\s+where\s+([^,:\n\(\)]+?)(?=[,:\n\)]|$)",
        _rewrite_thought_count,
        masked,
        flags=re.IGNORECASE
    )

    # 2. Natural Proportions & Percentages
    _EXPR_TERM = r"(\([^\)]+\)|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)*|\d+(?:\.\d+)?)"
    masked = re.sub(
        rf"\b{_EXPR_TERM}\s+as\s+(?:a\s+)?percent(?:age)?\s+of\s+{_EXPR_TERM}(?=[,:\s\n\)]|$)",
        r"(((\1) / (\2)) * 100.0)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b([A-Za-z_]\w*|\d+(?:\.\d+)?)\s*%\s+off\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\([^\)]+\))?|\d+(?:\.\d+)?)\b",
        r"((\2) * (1.0 - ((\1) / 100.0)))",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b([A-Za-z_]\w*|\d+(?:\.\d+)?)\s*%\s+(?:markup\s+on|tax\s+on|on)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\([^\)]+\))?|\d+(?:\.\d+)?)\b",
        r"((\2) * (1.0 + ((\1) / 100.0)))",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b([A-Za-z_]\w*|\d+(?:\.\d+)?)\s*%\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\([^\)]+\))?|\d+(?:\.\d+)?)\b",
        r"(((\1) / 100.0) * (\2))",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bhalf\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\([^\)]+\))?|\d+(?:\.\d+)?)\b",
        r"((\1) / 2.0)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bquarter\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\([^\)]+\))?|\d+(?:\.\d+)?)\b",
        r"((\1) / 4.0)",
        masked,
        flags=re.IGNORECASE
    )

    # 3. Bulk Actions & Collective Verbs
    masked = re.sub(
        r"^\s*add\s+all\s+(?:of\s+)?(.+?)\s+(?:to|into)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \2 to ds_extend(\2, \1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*remove\s+all\s+(?:of\s+)?(.+?)\s+from\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \2 to ds_remove_all(\2, \1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:clear|empty)\s+(?!screen\b)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \1 to ds_clear(\1)",
        masked,
        flags=re.IGNORECASE
    )

    # 4. Parallel, Paired & Indexed Iteration
    masked = re.sub(
        r"^\s*for\s+each\s+([A-Za-z_]\w*)\s+with\s+0-based\s+index\s+in\s+(.+?):$",
        r"for each index, \1 in ds_enumerate(\2, 0):",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*for\s+each\s+([A-Za-z_]\w*)\s+(?:with|and\s+its)\s+index\s+in\s+(.+?):$",
        r"for each index, \1 in ds_enumerate(\2):",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bpairs\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)*)\s+(?:and|,)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)*)\b",
        r"ds_pairs(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )

        # 5. Boolean Property Ergonomics vs Variable Equality Disambiguation
    _RESERVED_ADJ = {'none', 'true', 'false', 'even', 'odd', 'positive', 'negative', 'empty', 'zero', 'a', 'an', 'one', 'between', 'outside', 'inside', 'in', 'greater', 'less', 'at', 'over', 'under', 'equal', 'not', 'more', 'above', 'below', 'text', 'number', 'boolean', 'list', 'record', 'dict', 'dictionary', 'tuple', 'set', 'string', 'int', 'float', 'bool', 'defined', 'valid', 'present', 'null', 'nan'}
    if re.match(r"^\s*(?:if|unless|while|repeat\s+while|repeat\s+until|verify(?:\s+that)?|ensure|require|assert|check(?:\s+that)?)\b", masked, re.IGNORECASE) or re.search(r"\([^\)]*?\bis\b[^\)]*?\)", masked, re.IGNORECASE):
        def _repl_is_prop(m):
            subj = m.group(1).strip()
            adj = m.group(2).strip()
            if adj.startswith("__STR_LITERAL_") or adj.lower() in _RESERVED_ADJ:
                return m.group(0)
            if scope.is_var_in_scope(adj):
                return f"ds_is_compare({subj}, {adj}, '{adj}')"
            return f"ds_is_property({subj}, '{adj}')"

        def _repl_is_not_prop(m):
            subj = m.group(1).strip()
            adj = m.group(2).strip()
            if adj.startswith("__STR_LITERAL_") or adj.lower() in _RESERVED_ADJ:
                return m.group(0)
            if scope.is_var_in_scope(adj):
                return f"ds_is_not_compare({subj}, {adj}, '{adj}')"
            return f"not (ds_is_property({subj}, '{adj}'))"

        masked = re.sub(
            r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+(?:is\s+not|isn't)\s+([A-Za-z_]\w+)(?=\s*(?:\)|and\b|or\b|then\b|otherwise\b)|:|\n|$)",
            _repl_is_not_prop,
            masked,
            flags=re.IGNORECASE
        )
        masked = re.sub(
            r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+is\s+([A-Za-z_]\w+)(?=\s*(?:\)|and\b|or\b|then\b|otherwise\b)|:|\n|$)",
            _repl_is_prop,
            masked,
            flags=re.IGNORECASE
        )

    # Pillar D: Interrogative Inquiries & Collaborative Outputs
    masked = re.sub(r"^\s*(?:what\s+is|what's)\s+(?:the\s+)?(.+?)\??$", r"say \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:tell|show)\s+(?:me|us)\s+(.+)$", r"say \1", masked, flags=re.IGNORECASE)

    # Spoken Action Invocations (Statement & Expression Parity):
    # tell <target> to <action> [with <args>]
    def _repl_tell(m):
        tgt = m.group(1).replace("'s ", ".").strip()
        act = m.group(2).strip()
        a_str = m.group(3)
        if a_str:
            a_stripped = re.sub(r"^\s*with\s+", "", a_str.strip(), flags=re.IGNORECASE)
            a_clean = ", ".join(a.strip() for a in a_stripped.split(",") if a.strip())
            return f"{tgt}.{act}({a_clean})"
        return f"{tgt}.{act}()"

    masked = re.sub(
        r"\btell\s+(?!(?:me|us)\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+to\s+([a-z_]\w*)(?:\s+(?:with\s+)?([^,\n\)#:;]+))?",
        _repl_tell,
        masked,
        flags=re.IGNORECASE
    )

    # 2. deposit <amount> into/to <target>
    deposit_m = re.match(
        r"^\s*deposit\s+(.+?)\s+(?:into|to)\s+(.+)$",
        masked,
        re.IGNORECASE,
    )
    if deposit_m:
        val = deposit_m.group(1).strip()
        target = deposit_m.group(2).replace("'s ", ".").strip()
        masked = f"{target}.deposit({val})"

    # 3. withdraw <amount> from <target>
    withdraw_m = re.match(
        r"^\s*withdraw\s+(.+?)\s+from\s+(.+)$",
        masked,
        re.IGNORECASE,
    )
    if withdraw_m:
        val = withdraw_m.group(1).strip()
        target = withdraw_m.group(2).replace("'s ", ".").strip()
        masked = f"{target}.withdraw({val})"

    masked = re.sub(
        r"^\s*how\s+many\s+(?:items\s+in|of)\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \2 to count of \1",
        masked,
        flags=re.IGNORECASE
    )

    masked = re.sub(
        r"^\s*does\s+(.+?)\s+contain\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)$",
        r"set \3 to (\2 is inside \1)",
        masked,
        flags=re.IGNORECASE
    )

    # Phase 3: Classes and Instance Attributes
    masked = re.sub(
        r"^\s*define\s+(?:a|an)\s+([A-Za-z_]\w*)\s+(?:that\s+is\s+(?:a|an)\s+|that\s+extends\s+|inherits\s+from\s+|from\s+)([A-Za-z_]\w*)\s*:",
        r"class \1(\2):",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*define\s+(?:a|an)\s+([A-Za-z_]\w*)\s*:",
        r"class \1:",
        masked,
        flags=re.IGNORECASE
    )
    if scope.in_class:
        masked = re.sub(r"\b(?:my|its)\s+([A-Za-z_]\w*)", r"self.\1", masked, flags=re.IGNORECASE)
    else:
        masked = re.sub(r"\bmy\s+([A-Za-z_]\w*)", r"self.\1", masked, flags=re.IGNORECASE)
        last_sing = scope.get_last_singular() or scope.get_last_var()
        if last_sing:
            masked = re.sub(r"\bits\s+([A-Za-z_]\w*)", rf"{last_sing}.\1", masked, flags=re.IGNORECASE)
        subj = scope.get_last_subject()
        obj = scope.get_last_object()
        last_pl = scope.get_last_plural() or scope.get_last_var()
        if subj:
            masked = re.sub(r"\bher\s+([A-Za-z_]\w*)", rf"{subj}.\1", masked, flags=re.IGNORECASE)
        if obj:
            masked = re.sub(r"\bhis\s+([A-Za-z_]\w*)", rf"{obj}.\1", masked, flags=re.IGNORECASE)
        if last_pl:
            masked = re.sub(r"\btheir\s+(?!count\b)([A-Za-z_]\w*)", rf"{last_pl}.\1", masked, flags=re.IGNORECASE)

    # Phase 4: Lambdas and Comprehensions in English
    # English List Comprehensions and Ranges
    masked = re.sub(
        r"^\s*make\s+a\s+list\s+of\s+squares\s+(?:from|of)\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \3 to [x * x for x in range_inclusive(\1, \2)]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*make\s+a\s+list\s+of\s+(.+?)\s+for\s+each\s+([A-Za-z_]\w*)\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+(?:where|if)\s+(.+?))?\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        lambda m: f"set {m.group(6)} to [{m.group(1)} for {m.group(2)} in range_inclusive({m.group(3)}, {m.group(4)}) if {m.group(5)}]" if m.group(5) else f"set {m.group(6)} to [{m.group(1)} for {m.group(2)} in range_inclusive({m.group(3)}, {m.group(4)})]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*make\s+a\s+list\s+of\s+(.+?)\s+for\s+each\s+([A-Za-z_]\w*)\s+in\s+([^:\n]+?)(?:\s+(?:where|if)\s+(.+?))?\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        lambda m: f"set {m.group(5)} to [{m.group(1)} for {m.group(2)} in {m.group(3)} if {m.group(4)}]" if m.group(4) else f"set {m.group(5)} to [{m.group(1)} for {m.group(2)} in {m.group(3)}]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:make|create)\s+a\s+list\s+(?:of\s+numbers\s+)?from\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \3 to [x for x in range_inclusive(\1, \2)]",
        masked,
        flags=re.IGNORECASE
    )

    # Standalone statement form of make/create a list
    standalone_sq_m = re.match(
        r"^\s*(?:make|create)\s+a\s+list\s+of\s+squares\s+(?:from|of)\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s+to\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s*$",
        masked,
        re.IGNORECASE
    )
    if standalone_sq_m:
        start_v = standalone_sq_m.group(1)
        stop_v = standalone_sq_m.group(2)
        tmp_v = f"__it_{line_num}"
        masked = f"set {tmp_v} to [x * x for x in range_inclusive({start_v}, {stop_v})]"
        scope.record_assignment(tmp_v)

    standalone_rng_m = re.match(
        r"^\s*(?:make|create)\s+a\s+list\s+(?:of\s+([A-Za-z_]\w*)\s+)?from\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s+to\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s*$",
        masked,
        re.IGNORECASE
    )
    if standalone_rng_m:
        noun = standalone_rng_m.group(1)
        start_v = standalone_rng_m.group(2)
        stop_v = standalone_rng_m.group(3)
        tmp_v = noun if noun else f"__it_{line_num}"
        masked = f"set {tmp_v} to [x for x in range_inclusive({start_v}, {stop_v})]"
        scope.record_assignment(tmp_v)

    masked = re.sub(
        r"\bmake\s+a\s+list\s+of\s+squares\s+(?:from|of)\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s+to\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\b",
        r"[x * x for x in range_inclusive(\1, \2)]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bmake\s+a\s+list\s+of\s+(.+?)\s+for\s+each\s+([A-Za-z_]\w*)\s+from\s+([A-Za-z_]\w*|\d+)\s+to\s+([A-Za-z_]\w*|\d+)(?:\s+(?:where|if)\s+([^,\)\n]+?))?(?=\s+into\b|[,\)\n]|#|$)",
        lambda m: f"[{m.group(1)} for {m.group(2)} in range_inclusive({m.group(3)}, {m.group(4)}) if {m.group(5)}]" if m.group(5) else f"[{m.group(1)} for {m.group(2)} in range_inclusive({m.group(3)}, {m.group(4)})]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bmake\s+a\s+list\s+of\s+(.+?)\s+for\s+each\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)(?:\s+(?:where|if)\s+([^,\)\n]+?))?(?=\s+into\b|[,\)\n]|#|$)",
        lambda m: f"[{m.group(1)} for {m.group(2)} in {m.group(3)} if {m.group(4)}]" if m.group(4) else f"[{m.group(1)} for {m.group(2)} in {m.group(3)}]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b(?:make|create)\s+a\s+list\s+(?:of\s+numbers\s+)?from\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s+to\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\b",
        r"[x for x in range_inclusive(\1, \2)]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b(?:(?:a\s+)?list\s+of\s+|the\s+)?squares\s+(?:of|from)\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s+to\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\b",
        r"[x * x for x in range_inclusive(\1, \2)]",
        masked,
        flags=re.IGNORECASE
    )

    # Desugar change/modify/update to set
    masked = re.sub(
        r"^\s*(?:change|modify|update)\s+(.+?)\s+to\s+(.+)$",
        r"set \1 to \2",
        masked,
        flags=re.IGNORECASE
    )

    # In-place string mutators (trim, capitalize, uppercase, lowercase)
    masked = re.sub(
        r"^\s*trim\s+((?!__STR_)[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \1 to trim of \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*capitalize\s+((?!__STR_)[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \1 to capitalize of \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:convert\s+((?!__STR_)[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+to\s+uppercase|uppercase\s+((?!__STR_)[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?))\s*$",
        lambda m: f"set {m.group(1) or m.group(2)} to uppercase of {m.group(1) or m.group(2)}",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:convert\s+((?!__STR_)[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+to\s+lowercase|lowercase\s+((?!__STR_)[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?))\s*$",
        lambda m: f"set {m.group(1) or m.group(2)} to lowercase of {m.group(1) or m.group(2)}",
        masked,
        flags=re.IGNORECASE
    )

    # Preposition flexibility (add X into/in Y -> add X to Y, first item in X -> first item of X)
    masked = re.sub(
        r"^\s*add\s+(.+?)\s+(?:into|in)\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"add \1 to \2",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b(first|last)\s+item\s+in\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)",
        r"\1 item of \2",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bsplit\s+(.+?)\s+(?:with|on)\s+(\S+)",
        r"split \1 by \2",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bjoin\s+(.+?)\s+by\s+(\S+)",
        r"join \1 with \2",
        masked,
        flags=re.IGNORECASE
    )

    # Conversational list assignment: numbers is a list of 1, 2, 3
    masked = re.sub(
        r"^\s*([A-Za-z_]\w*)\s+is\s+(a\s+list\s+of\b.+)$",
        r"set \1 to \2",
        masked,
        flags=re.IGNORECASE
    )

    # Trailing type cast in input: ask "..." into age as number
    masked = re.sub(
        r"^\s*ask\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s+as\s+(number|text|string|boolean|bool)\s*$",
        lambda m: f"ask {'boolean' if m.group(3).lower() in ('boolean', 'bool') else m.group(3).lower()} {m.group(1)} into {m.group(2)}" if m.group(3).lower() not in ('text', 'string') else f"ask {m.group(1)} into {m.group(2)}",
        masked,
        flags=re.IGNORECASE
    )

    # Expression sort: sorted <var> -> sorted of <var>
    masked = re.sub(
        r"\bsorted\s+(?!of\b)(?!by\b)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)(?!\s+(?:by|of)\b)(?!\s*[\(=])\b",
        r"sorted of \1",
        masked,
        flags=re.IGNORECASE
    )

    # Expression reverse: reversed <var> -> reversed of <var>
    masked = re.sub(
        r"\breversed\s+(?!of\b)(?!in\b)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)(?!\s*[\(=])\b",
        r"reversed of \1",
        masked,
        flags=re.IGNORECASE
    )

    # Desugar data operations to canonical expression assignments
    masked = re.sub(
        r"^\s*split\s+(.+?)\s+by\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \3 to split \1 by \2",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*split\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \2 to split \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*join\s+(.+?)\s+(?:with|by)\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \3 to join \1 with \2",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*replace\s+(.+?)\s+with\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \4 to replace \1 with \2 in \3",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*trim\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \2 to trim \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*capitalize\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \2 to capitalize \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:convert\s+(.+?)\s+to\s+uppercase|uppercase\s+(.+?))\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        lambda m: f"set {m.group(3)} to uppercase {m.group(1) or m.group(2)}",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:convert\s+(.+?)\s+to\s+lowercase|lowercase\s+(.+?))\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        lambda m: f"set {m.group(3)} to lowercase {m.group(1) or m.group(2)}",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*sort\s+(?!.*\bby\b)(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \2 to sorted of \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:unique\s+items\s+of|unique\s+of|unique)\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \2 to unique items of \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*(?:reverse|reversed)\s+(?:of\s+|in\s+)?(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \2 to reversed of \1",
        masked,
        flags=re.IGNORECASE
    )
    # In-place reverse: reverse <var>
    masked = re.sub(
        r"^\s*(?:reverse|reversed)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \1 to ds_reversed(\1)",
        masked,
        flags=re.IGNORECASE
    )

    # Standalone data operations (implicit target __it_{line_num})
    replace_inplace_m = re.match(
        r"^\s*replace\s+(.+?)\s+with\s+(.+?)\s+in\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        masked,
        re.IGNORECASE,
    )
    if replace_inplace_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        old_v = replace_inplace_m.group(1).strip()
        new_v = replace_inplace_m.group(2).strip()
        tgt = replace_inplace_m.group(3).strip()
        masked = f"set {tgt} to replace {old_v} with {new_v} in {tgt}"
        scope.record_assignment(tgt)

    join_standalone_m = re.match(
        r"^\s*join\s+(.+?)\s+(?:with|by)\s+(.+?)\s*$",
        masked,
        re.IGNORECASE,
    )
    if join_standalone_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        coll = join_standalone_m.group(1).strip()
        delim = join_standalone_m.group(2).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to join {coll} with {delim}"
        scope.record_assignment(tmp_var)

    how_many_m = re.match(
        r"^\s*how\s+many\s+items\s+in\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        masked,
        re.IGNORECASE,
    )
    if how_many_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        coll = how_many_m.group(1).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to count of {coll}"
        scope.record_assignment(tmp_var)

    trim_standalone_m = re.match(r"^\s*trim\s+(.+?)\s*$", masked, re.IGNORECASE)
    if trim_standalone_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        val = trim_standalone_m.group(1).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to trim {val}"
        scope.record_assignment(tmp_var)

    upper_standalone_m = re.match(r"^\s*(?:convert\s+(.+?)\s+to\s+uppercase|uppercase\s+(.+?))\s*$", masked, re.IGNORECASE)
    if upper_standalone_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        val = (upper_standalone_m.group(1) or upper_standalone_m.group(2)).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to uppercase {val}"
        scope.record_assignment(tmp_var)

    lower_standalone_m = re.match(r"^\s*(?:convert\s+(.+?)\s+to\s+lowercase|lowercase\s+(.+?))\s*$", masked, re.IGNORECASE)
    if lower_standalone_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        val = (lower_standalone_m.group(1) or lower_standalone_m.group(2)).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to lowercase {val}"
        scope.record_assignment(tmp_var)

    make_squares_standalone_m = re.match(
        r"^\s*(?:make|create)\s+a\s+list\s+of\s+squares\s+(?:from|of)\s+(.+?)\s+to\s+(.+?)\s*$",
        masked,
        re.IGNORECASE,
    )
    if make_squares_standalone_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        start = make_squares_standalone_m.group(1).strip()
        stop = make_squares_standalone_m.group(2).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to [x * x for x in range_inclusive({start}, {stop})]"
        scope.record_assignment(tmp_var)

    make_range_standalone_m = re.match(
        r"^\s*(?:make|create)\s+a\s+list\s+(?:of\s+numbers\s+)?from\s+(.+?)\s+to\s+(.+?)\s*$",
        masked,
        re.IGNORECASE,
    )
    if make_range_standalone_m and not re.search(r"\binto\b", masked, re.IGNORECASE):
        start = make_range_standalone_m.group(1).strip()
        stop = make_range_standalone_m.group(2).strip()
        tmp_var = f"__it_{line_num}"
        masked = f"set {tmp_var} to [x for x in range_inclusive({start}, {stop})]"
        scope.record_assignment(tmp_var)

    masked = re.sub(
        r"\ba\s+function\s+of\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s+giving\s+(.+?)(?=[,\n]|\)$|$)",
        r"(lambda \1: \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"(?<!for\s)\beach\s+([A-Za-z_]\w*)\s+in\s+([^:\n]+?)\s+(?:where|if)\s+(.+?)(?=\s*(?:#|\n|$))",
        r"[\1 for \1 in \2 if \3]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"(?<!for\s)\beach\s+(.+?)\s+for\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s+in\s+([^:\n]+?)\s+(?:where|if)\s+(.+?)(?=\s*(?:#|\n|$))",
        r"[\1 for \2 in \3 if \4]",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"(?<!for\s)\beach\s+(.+?)\s+for\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)\s+in\s+([^:\n]+?)(?=\s*(?:#|\n|$))",
        r"[\1 for \2 in \3]",
        masked,
        flags=re.IGNORECASE
    )


    masked = re.sub(
        r"\bplot\s+([A-Za-z_]\w*)\s+against\s+([A-Za-z_]\w*)\s+from\s+([A-Za-z_]\w*)\b",
        r"plot_table(\3, '\2', '\1')",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bplot\s+(?:line\s+)?([A-Za-z_]\w*)\s+with\s+x=(.+?),\s*y=(.+?)(?=[,\)\]\}:;\n]|$)",
        r"plot_table(\1, \2, \3)",
        masked,
        flags=re.IGNORECASE
    )

    # 2. Flexible Assignment Patterns
    for pat, repl in ASSIGNMENT_PATTERNS:
        if pat.match(masked):
            masked = pat.sub(repl, masked)
            break

    # Legacy assignment statement deprecation rewrite: 'target is expr' -> 'target = expr'
    # Supported during DoomScript 1.x deprecation window; canonical syntax is 'target = expr'.
    legacy_is_assign = re.match(
        r"^(?!result\b)(?!the\s+result\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+is\s+"
        r"(?!even\b|odd\b|positive\b|negative\b|zero\b|blank\b|empty\b|"
        r"a\s+(?:number|string|text|boolean|bool|list(?!\s+of\b)|record|dictionary|dict|multiple\s+of)\b|"
        r"an\s+(?:empty\b|integer\b)|not\b|between\b|"
        r"one\s+of\b|inside\b|in\b|divisible\b|greater\b|less\b|equal\b|more\b|smaller\b|above\b|"
        r"below\b|at\s+least\b|at\s+most\b|no\s+more\b|no\s+less\b)(.+)$",
        masked,
        re.IGNORECASE,
    )
    if legacy_is_assign:
        t_var = legacy_is_assign.group(1).strip()
        v_expr = legacy_is_assign.group(2).strip()
        masked = f"{t_var} = {v_expr}"

    # 3. Special handling for 'call it <target>'
    call_it_match = re.match(r"^call\s+(?:it|that)\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if call_it_match:
        target = call_it_match.group(1)
        last_var = scope.get_last_var()
        if not last_var:
            raise DoomScopeError(
                f"Cannot resolve 'call it {target}' on line {line_num}: no preceding variable assigned in scope.",
                line=line_num,
                source_line=stmt
            )
        masked = f"set {target} to {last_var}"
        scope.record_assignment(target)
        return unmask_strings(masked, strings)

    # 4. Pronoun Resolution ('it' / 'that')
    # Temporarily protect grammar keywords that contain 'that' or 'it'
    masked = re.sub(r"\bverify\s+that\b", "__VERIFY_THAT__", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\brequire\s+that\b", "__REQUIRE_THAT__", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bensure\s+that\b", "__ENSURE_THAT__", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bif\s+(?:(?:it|that)\s+fails|there\s+is\s+an?\s+error|(?:it|anything)\s+goes\s+wrong)\b", "__IF_FAILS__", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bif\s+it\s+(?:turns\s+out|happens)\s+that\b", "__IF_TURNS_OUT__", masked, flags=re.IGNORECASE)

    # Plural pronoun resolution: 'their count', 'them', 'these', 'those'
    if re.search(r"\btheir\s+count\b", masked, re.IGNORECASE):
        last_pl = scope.get_last_plural() or scope.get_last_var()
        if last_pl:
            masked = re.sub(r"\btheir\s+count\b", f"count of {last_pl}", masked, flags=re.IGNORECASE)

    # In them / from them / to them / with them
    if re.search(r"\b(in|from|to|with|for|each)\s+(them|these|those)\b", masked, re.IGNORECASE):
        last_pl = scope.get_last_plural() or scope.get_last_var()
        if last_pl:
            masked = re.sub(r"\b(in|from|to|with|for|each)\s+(?:them|these|those)\b", rf"\1 {last_pl}", masked, flags=re.IGNORECASE)

    if re.search(r"\b(to|from|with|for)\s+her\b", masked, re.IGNORECASE):
        subj = scope.get_last_subject()
        if subj:
            masked = re.sub(r"\b(to|from|with|for)\s+her\b", rf"\1 {subj}", masked, flags=re.IGNORECASE)
    if re.search(r"\b(to|from|with|for)\s+him\b", masked, re.IGNORECASE):
        obj = scope.get_last_object()
        if obj:
            masked = re.sub(r"\b(to|from|with|for)\s+him\b", rf"\1 {obj}", masked, flags=re.IGNORECASE)

    pronoun_match = re.search(r"\b(it|that)\b", masked, re.IGNORECASE)
    if pronoun_match:
        last_var = scope.get_last_singular() or scope.get_last_var()
        if not last_var:
            raise DoomScopeError(
                f"Cannot resolve pronoun '{pronoun_match.group(1)}' on line {line_num}: no preceding variable assigned in scope.",
                line=line_num,
                source_line=stmt,
                suggestion="assign a variable first or use an explicit variable name"
            )
        masked = re.sub(r"\b(it|that)\b", last_var, masked, flags=re.IGNORECASE)

    # Plural pronoun resolution ('them', 'these', 'those')
    plural_pronoun_match = re.search(r"\b(them|these|those)\b", masked, re.IGNORECASE)
    if plural_pronoun_match:
        last_pl = scope.get_last_plural() or scope.get_last_var()
        if last_pl:
            masked = re.sub(r"\b(them|these|those)\b", last_pl, masked, flags=re.IGNORECASE)

    # Restore protected keywords (also normalizes 'if that fails' to 'if it fails')
    masked = masked.replace("__VERIFY_THAT__", "verify that")
    masked = masked.replace("__REQUIRE_THAT__", "verify that")
    masked = masked.replace("__ENSURE_THAT__", "verify that")
    masked = masked.replace("__IF_FAILS__", "if it fails")
    masked = masked.replace("__IF_TURNS_OUT__", "if")

    # 5. Verb Synonyms
    # Handle display vs display colored
    if re.match(r"^display\s+colored\b", masked, re.IGNORECASE):
        pass  # Keep legacy display colored
    elif re.match(r"^display\b", masked, re.IGNORECASE):
        masked = re.sub(r"^display\b", "say", masked, flags=re.IGNORECASE)

    if not re.match(r"^\s*[A-Za-z_]\w*\s*(?:=|\+=|-=|\*=)", masked):
        for syn, canonical in VERB_SYNONYMS.items():
            pattern = re.compile(rf"^{syn}\s+(?![=+\-*/%<>&|^]|\b(?:is|=|to|in)\b)", re.IGNORECASE)
            if pattern.match(masked):
                masked = pattern.sub(f"{canonical} ", masked, count=1)
                break

    # 6. Possessives and Article Rewrites
    for pat, repl in POSSESSIVE_REWRITES:
        masked = pat.sub(repl, masked)

    # 7. Comparison Synonyms
    for syn, canonical in COMPARISON_SYNONYMS:
        # Replace whole phrase
        pattern = re.compile(rf"\b{re.escape(syn)}\b", re.IGNORECASE)
        if pattern.search(masked):
            masked = pattern.sub(canonical, masked)

    # 8. Ignorable Articles before identifiers
    # E.g. "say the total" -> "say total"
    # "add 5 to the list" -> "add 5 to list"
    for art in IGNORABLE_ARTICLES:
        # 'the' followed by an identifier or word
        masked = re.sub(rf"\b{art}\s+([A-Za-z_]\w*)", r"\1", masked, flags=re.IGNORECASE)

    # 9. Phase 2 Everyday Programming Rewrites
    masked = re.sub(r"^\s*(?:otherwise\s+if|else\s+if)\b", "elif", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*otherwise\b", "else", masked, flags=re.IGNORECASE)
    # Paradigm 36: Relative Time Offsets
    masked = re.sub(r"\b(\d+)\s+days?\s+ago\b", r"ds_time_ago(days=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(\d+)\s+hours?\s+ago\b", r"ds_time_ago(hours=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(\d+)\s+minutes?\s+ago\b", r"ds_time_ago(minutes=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(\d+)\s+seconds?\s+ago\b", r"ds_time_ago(seconds=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bin\s+(\d+)\s+days?\b", r"ds_time_from_now(days=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bin\s+(\d+)\s+hours?\b", r"ds_time_from_now(hours=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bin\s+(\d+)\s+minutes?\b", r"ds_time_from_now(minutes=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bin\s+(\d+)\s+seconds?\b", r"ds_time_from_now(seconds=\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*random\s+number\b", "roll", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*open\s+window\b", "open_window", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*with\s+(.+?)\s+(?:as|into)\s+([A-Za-z_]\w*)\s*:?", r"with \1 into \2:", masked, flags=re.IGNORECASE)
        # Conversational AI & Assistant:
    masked = re.sub(r"^\s*ask\s+the\s+agent\s+", "ask agent ", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*tell\s+the\s+agent\s+", "tell agent ", masked, flags=re.IGNORECASE)

    ask_ast_m = re.match(
        r"^\s*ask\s+(?:the\s+)?assistant\s+(.+?)(?:\s+for\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if ask_ast_m:
        p_str = ask_ast_m.group(1).strip()
        ctx_str = ask_ast_m.group(2)
        tgt_var = ask_ast_m.group(3).strip()
        if ctx_str:
            masked = f"{tgt_var} = ask_assistant({p_str}, context={ctx_str.strip()})"
        else:
            masked = f"{tgt_var} = ask_assistant({p_str})"

    ask_mod_m = re.match(
        r"^\s*ask\s+(?:the\s+)?model\s+(.+?)(?:\s+for\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if ask_mod_m:
        p_str = ask_mod_m.group(1).strip()
        ctx_str = ask_mod_m.group(2)
        tgt_var = ask_mod_m.group(3).strip()
        if ctx_str:
            masked = f"{tgt_var} = ask_model({p_str}, context={ctx_str.strip()})"
        else:
            masked = f"{tgt_var} = ask_model({p_str})"

    # Trailing input type cast: ask "..." into target as number/boolean/text
    ask_as_m = re.match(
        r"^\s*ask\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s+as\s+(number|boolean|bool|text|string)\s*$",
        masked,
        re.IGNORECASE,
    )
    if ask_as_m:
        prompt = ask_as_m.group(1).strip()
        t_var = ask_as_m.group(2).strip()
        as_type = ask_as_m.group(3).lower()
        if as_type == "number":
            masked = f"ask number {prompt} into {t_var}"
        elif as_type in ("boolean", "bool"):
            masked = f"ask boolean {prompt} into {t_var}"
        else:
            masked = f"ask {prompt} into {t_var}"

    masked = re.sub(r"\bask\s+(?:for\s+)?number\b", "ask number", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bask\s+(?:for\s+)?(?:boolean|yes/no|confirmation)\b", "ask boolean", masked, flags=re.IGNORECASE)
    # Ergonomic timing
    masked = re.sub(r"^\s*(?:sleep|delay|pause)\s+(?!for\b)(.+)$", r"wait \1", masked, flags=re.IGNORECASE)

    # Conversational Data File Ingestion:
    load_csv_m = re.match(r"^\s*load\s+csv\s+(?:from\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if load_csv_m:
        masked = f"read csv file {load_csv_m.group(1).strip()} into {load_csv_m.group(2).strip()}"

    load_json_m = re.match(r"^\s*load\s+json\s+(?:from\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if load_json_m:
        masked = f"{load_json_m.group(2).strip()} = load_json_file({load_json_m.group(1).strip()})"

    # Ergonomic File I/O (omitting 'file' keyword)
    read_m = re.match(r"^\s*read\s+(?!file\b|csv\b|records\b)(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if read_m:
        path_expr = read_m.group(1).strip()
        target_var = read_m.group(2).strip()
        unmasked_path = unmask_strings(path_expr, strings).lower()
        if unmasked_path.endswith('.csv"') or unmasked_path.endswith(".csv'"):
            masked = f"read csv file {path_expr} into {target_var}"
        else:
            masked = f"read file {path_expr} into {target_var}"

    write_m = re.match(r"^\s*(?:write|save)\s+(?!csv\b|record\b|model\b|plot\b|table\b|new\b)(.+?)\s+(?:to|into)\s+(?!file\b|screen\b|console\b)(.+)$", masked, re.IGNORECASE)
    if write_m:
        val_expr = write_m.group(1).strip()
        path_expr = write_m.group(2).strip()
        unmasked_path = unmask_strings(path_expr, strings).strip()
        is_quoted = (unmasked_path.startswith('"') and unmasked_path.endswith('"')) or (unmasked_path.startswith("'") and unmasked_path.endswith("'"))
        has_file_ext = "." in unmasked_path and not unmasked_path.endswith(".")
        if is_quoted or has_file_ext:
            unmasked_lower = unmasked_path.lower()
            if unmasked_lower.endswith('.csv"') or unmasked_lower.endswith(".csv'") or unmasked_lower.endswith(".csv"):
                masked = f"write csv {val_expr} into file {path_expr}"
            else:
                masked = f"write {val_expr} into file {path_expr}"

    append_m = re.match(r"^\s*append\s+(?!file\b|csv\b)(.+?)\s+to\s+(?!file\b|the\s+list\b)(.+)$", masked, re.IGNORECASE)
    if append_m:
        val_expr = append_m.group(1).strip()
        path_expr = append_m.group(2).strip()
        unmasked_path = unmask_strings(path_expr, strings).strip()
        is_quoted = (unmasked_path.startswith('"') and unmasked_path.endswith('"')) or (unmasked_path.startswith("'") and unmasked_path.endswith("'"))
        has_file_ext = "." in unmasked_path and not unmasked_path.endswith(".")
        if is_quoted or has_file_ext:
            unmasked_lower = unmasked_path.lower()
            if unmasked_lower.endswith('.csv"') or unmasked_lower.endswith(".csv'") or unmasked_lower.endswith(".csv"):
                masked = f"append csv {val_expr} to file {path_expr}"
            else:
                masked = f"append {val_expr} to file {path_expr}"

    check_m = re.match(r"^\s*check\s+if\s+(?!file\b)(.+?)\s+exists\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if check_m:
        masked = f"check if file {check_m.group(1).strip()} exists into {check_m.group(2).strip()}"

    # Ergonomic Networking & HTTP (fetch, post, download, conversational requests)
    send_get_m = re.match(
        r"^\s*send\s+(?:a\s+)?get\s+request\s+to\s+(.+?)(?:\s+and\s+wait\s+for\s+response)?\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if send_get_m:
        masked = f"{send_get_m.group(2).strip()} = fetch_url({send_get_m.group(1).strip()}, method='GET')"

    send_post_m = re.match(
        r"^\s*send\s+(?:a\s+)?post\s+request\s+to\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if send_post_m:
        masked = f"{send_post_m.group(3).strip()} = fetch_url({send_post_m.group(1).strip()}, method='POST', json_body={send_post_m.group(2).strip()})"

    extract_field_m = re.match(
        r"^\s*extract\s+(?:json\s+)?field\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if extract_field_m:
        masked = f"{extract_field_m.group(3).strip()} = extract_json_field({extract_field_m.group(2).strip()}, {extract_field_m.group(1).strip()})"

    fetch_m = re.match(r"^\s*fetch\s+(?!url\b|json\b|text\b)(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if fetch_m:
        masked = f"{fetch_m.group(2)} = fetch_url({fetch_m.group(1).strip()})"

    fetch_json_m = re.match(r"^\s*fetch\s+json\s+(?!from\b)(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if fetch_json_m:
        masked = f"fetch json from {fetch_json_m.group(1).strip()} into {fetch_json_m.group(2).strip()}"

    fetch_text_m = re.match(r"^\s*fetch\s+text\s+(?!from\b)(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if fetch_text_m:
        masked = f"fetch text from {fetch_text_m.group(1).strip()} into {fetch_text_m.group(2).strip()}"

    dl_m = re.match(r"^\s*download\s+(.+?)\s+(?:to|into)\s+(?!file\b)(.+)$", masked, re.IGNORECASE)
    if dl_m:
        masked = f"download {dl_m.group(1).strip()} to file {dl_m.group(2).strip()}"

    post_m = re.match(r"^\s*post\s+(?!json\b)(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if post_m:
        masked = f"{post_m.group(3).strip()} = fetch_url({post_m.group(2).strip()}, method='POST', json_body={post_m.group(1).strip()})"

    # Ergonomic Statistics & Math Statements
    stat_stmt_m = re.match(
        r"^\s*(?:calculate\s+|compute\s+)?(average|mean|median|total|sum|maximum|highest|minimum|lowest|variance|standard\s+deviation|std_dev|stdev|count|length|summary)\s+(?:of|in)\s+(?!.+?\s+in\s+bytes\b)(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE
    )
    if stat_stmt_m:
        fn_word = stat_stmt_m.group(1).lower().replace(" ", "_")
        val_expr = stat_stmt_m.group(2).strip()
        target_var = stat_stmt_m.group(3).strip()
        if fn_word in ("average", "mean"):
            masked = f"set {target_var} to agg_avg({val_expr})"
        elif fn_word in ("total", "sum"):
            masked = f"set {target_var} to sum of {val_expr}"
        elif fn_word in ("median",):
            masked = f"set {target_var} to math_median({val_expr})"
        elif fn_word in ("variance",):
            masked = f"set {target_var} to variance({val_expr})"
        elif fn_word in ("standard_deviation", "std_dev", "stdev"):
            masked = f"set {target_var} to std_dev({val_expr})"
        elif fn_word in ("maximum", "highest"):
            masked = f"set {target_var} to highest in {val_expr}"
        elif fn_word in ("minimum", "lowest"):
            masked = f"set {target_var} to lowest in {val_expr}"
        elif fn_word in ("count", "length"):
            masked = f"set {target_var} to count of {val_expr}"
        elif fn_word == "summary":
            masked = f"set {target_var} to summary_of({val_expr})"

    masked = re.sub(r"\b(?:reversed|reverse)\s+in\b", "reversed of", masked, flags=re.IGNORECASE)

    # Conversational Finance & Simulation:
    sim_port_m = re.match(
        r"^\s*simulate\s+portfolio\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if sim_port_m:
        raw_with = sim_port_m.group(1).strip()
        target_var = sim_port_m.group(2).strip()
        if "%" in raw_with:
            pct_pairs = re.findall(r"(\d+(?:\.\d+)?)\s*%\s*([A-Za-z_]\w*)", raw_with)
            if pct_pairs:
                dict_body = ", ".join(f'"{sym}": {float(p)/100.0}' for p, sym in pct_pairs)
                masked = f"{target_var} = simulate_portfolio({{{dict_body}}})"
            else:
                masked = f"{target_var} = simulate_portfolio({raw_with})"
        else:
            masked = f"{target_var} = simulate_portfolio({raw_with})"

    calc_ci_m = re.match(
        r"^\s*calculate\s+compound\s+interest\s+on\s+principal\s+(.+?)\s+at\s+rate\s+(.+?)\s+(?:over|for)\s+(.+?)\s+years\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if calc_ci_m:
        p_expr = calc_ci_m.group(1).strip()
        r_expr = calc_ci_m.group(2).strip()
        y_expr = calc_ci_m.group(3).strip()
        target_var = calc_ci_m.group(4).strip()
        if r_expr.endswith("%"):
            r_val = str(float(r_expr[:-1].strip()) / 100.0)
        else:
            r_val = r_expr
        masked = f"{target_var} = calculate_compound_interest({p_expr}, {r_val}, {y_expr})"

    # Conversational Data Summaries:
    summ_col_m = re.match(
        r"^\s*summarize\s+column\s+(.+?)\s+by\s+(.+?)\s+(?:in|from)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if summ_col_m:
        masked = f"{summ_col_m.group(4).strip()} = summarize_data({summ_col_m.group(3).strip()}, {summ_col_m.group(1).strip()}, {summ_col_m.group(2).strip()}, agg_fn='sum')"

    summ_fn_m = re.match(
        r"^\s*summarize\s+(.+?)\s+by\s+(.+?)\s+calculating\s+([A-Za-z_]\w*)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE,
    )
    if summ_fn_m:
        masked = f"{summ_fn_m.group(5).strip()} = summarize_data({summ_fn_m.group(1).strip()}, {summ_fn_m.group(4).strip()}, {summ_fn_m.group(2).strip()}, agg_fn='{summ_fn_m.group(3).strip().lower()}')"

    # Ergonomic String & Collection Operations
    words_m = re.match(r"^\s*words\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if words_m:
        masked = f"set {words_m.group(2)} to words_of({words_m.group(1).strip()})"

    lines_m = re.match(r"^\s*lines\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if lines_m:
        masked = f"set {lines_m.group(2)} to lines_of({lines_m.group(1).strip()})"

    keys_m = re.match(r"^\s*keys\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if keys_m:
        masked = f"set {keys_m.group(2)} to dict_keys({keys_m.group(1).strip()})"

    values_m = re.match(r"^\s*values\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if values_m:
        masked = f"set {values_m.group(2)} to dict_values({values_m.group(1).strip()})"

    shuffle_m = re.match(r"^\s*shuffle\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if shuffle_m:
        masked = f"set {shuffle_m.group(2)} to shuffle_list({shuffle_m.group(1).strip()})"

    masked = re.sub(
        r"^\s*pick\s+random\s+item\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
        r"pick random from \1 into \2",
        masked,
        flags=re.IGNORECASE
    )

    # Ergonomic Visualization Short Forms
    viz_chart_m = re.match(
        r"^\s*(?:chart\s+)?(scatter(?:\s+plot)?|line(?:\s+chart)?|bar(?:\s+chart)?|histogram|box(?:\s+plot)?)\s+of\s+([A-Za-z_]\w*)\s+with\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
        masked,
        re.IGNORECASE
    )
    if viz_chart_m:
        c_type = viz_chart_m.group(1).lower()
        dataset = viz_chart_m.group(2)
        raw_params = viz_chart_m.group(3).strip()
        target = viz_chart_m.group(4) or "plot"
        geom = "point" if "scatter" in c_type else "line" if "line" in c_type else "bar" if "bar" in c_type else "histogram" if "hist" in c_type else "boxplot"
        p_str = re.sub(r"\b(titled|title)\s+", r" and title=", raw_params, flags=re.IGNORECASE)
        parts = re.split(r"\s+and\s+|,\s*", p_str)
        formatted_args = []
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                formatted_args.append(part)
            else:
                kv_m = re.match(r"^([A-Za-z_]\w*)\s+(.+)$", part)
                if kv_m:
                    formatted_args.append(f"{kv_m.group(1)}={kv_m.group(2).strip()}")
                else:
                    formatted_args.append(part)
        with_kwargs = ", ".join(formatted_args)
        masked = f'set {target} to PlotBuilder({dataset}).kind("{geom}", {with_kwargs})'

    masked = re.sub(r"\bread\s+csv\s+(?!file\b)", "read csv file ", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bwrite\s+csv\s+(.+?)\s+to\s+file\b", r"write csv \1 into file", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bwrite\s+csv\s+(.+?)\s+to\s+(?!file\b)", r"write csv \1 into file ", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bjson\s+parse\b", "parse json", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bjson\s+stringify\s+(.+?)\s+into\b", r"convert \1 to json into", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bget\s+environment\s+variable\b", "environment variable", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bround\s+(.+?)\s+to\s+(.+?)\s+places\s+into\b", r"round \1 to \2 decimals into", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bsort\s+(.+?)\s+by\s+([A-Za-z_]\w*)\s+\((?:descending|desc)\)", r"sort \1 by \2 descending", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bsort\s+(.+?)\s+by\s+([A-Za-z_]\w*)\s+desc\b", r"sort \1 by \2 descending", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\binsert\s+(.+?)\s+at\s+(?:index|position)\s+(.+?)\s+in\b", r"insert \1 at \2 in", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bunique\s+items\s+in\b", "unique items of", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:an\s+empty\s+list|a\s+new\s+list)\b", "[]", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:an?\s+empty\s+(?:record|dictionary|dict|map)|a\s+new\s+(?:record|dictionary|dict|map)|empty\s+(?:record|dictionary|dict|map))\b", "Record()", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:a\s+list\s+of|list\s+of)\s+([^;\n]+?)(?=\s+with\b|\s+at\b|\s+into\b|;\s*|\n|$)", r"[\1]", masked, flags=re.IGNORECASE)

    # Function definition with 'on': 'to tax on price' -> 'to tax with price'
    masked = re.sub(r"^\s*to\s+([A-Za-z_]\w*)\s+on\s+([A-Za-z_]\w*)\b", r"to \1 with \2", masked, flags=re.IGNORECASE)

    # Filter statements with assignment, set, or leading 'filter'
    masked = re.sub(r"^\s*filter\s+(.+?\s+where\s+.+)$", r"\1", masked, flags=re.IGNORECASE)
    filter_into_m = re.match(r"^\s*(?:set\s+)?([A-Za-z_]\w*)\s*(?:=|to)\s+(.+?)\s+where\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if filter_into_m:
        masked = f"{filter_into_m.group(2)} where {filter_into_m.group(3)} into {filter_into_m.group(4)}"
    else:
        filter_assign_m = re.match(r"^\s*(?:set\s+)?([A-Za-z_]\w*)\s*(?:=|to)\s+(.+?)\s+where\s+(.+?)$", masked, re.IGNORECASE)
        if filter_assign_m:
            masked = f"{filter_assign_m.group(2)} where {filter_assign_m.group(3)} into {filter_assign_m.group(1)}"

    # Normalize square root of to sqrt of
    masked = re.sub(r"\bsquare\s+root\s+of\b", "sqrt of", masked, flags=re.IGNORECASE)

    # Result of function calls in expressions
    masked = re.sub(r"\b(?:the\s+)?result\s+of\s+([A-Za-z_]\w*)\s+on\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"\1(\2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?result\s+of\s+([A-Za-z_]\w*)\s+with\s+(.+?)(?=\s+and\s+then|\s+into\b|\s+otherwise\b|\s*$)", r"\1(\2)", masked, flags=re.IGNORECASE)

    # Field aggregates
    masked = re.sub(r"\b(?:total|sum)\s+(?:of\s+)?([A-Za-z_]\w*)\s+(?:in|of|from)\s+([A-Za-z_]\w*)", r'agg_field("sum", "\1", \2)', masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:average|mean)\s+(?:of\s+)?([A-Za-z_]\w*)\s+(?:in|of|from)\s+([A-Za-z_]\w*)", r'agg_field("avg", "\1", \2)', masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:highest|maximum|largest)\s+(?:of\s+)?([A-Za-z_]\w*)\s+(?:in|of|from)\s+([A-Za-z_]\w*)", r'agg_field("max", "\1", \2)', masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:lowest|minimum|smallest)\s+(?:of\s+)?([A-Za-z_]\w*)\s+(?:in|of|from)\s+([A-Za-z_]\w*)", r'agg_field("min", "\1", \2)', masked, flags=re.IGNORECASE)

    # List operations (statement forms)
    masked = re.sub(
        r"^\s*first\s+(\d+|[A-Za-z_]\w*)\s+items\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \3 to first_n_items(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*last\s+(\d+|[A-Za-z_]\w*)\s+items\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"set \3 to last_n_items(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(r"^\s*set\s+item\s+(.+?)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+to\s+(.+)$", r"set_item(\1, \2, \3)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bitem\s+(\d+|[A-Za-z_]\w*)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"item_of(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bfirst\s+(\d+|[A-Za-z_]\w*)\s+items\s+of\s+([A-Za-z_]\w*(?:\([^)]*\)|(?:'s\s+[A-Za-z_]\w*)?)|\[[^\]]+\])", r"first_n_items(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\blast\s+(\d+|[A-Za-z_]\w*)\s+items\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"last_n_items(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:title|titlecase)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"str_title(\1)", masked, flags=re.IGNORECASE)

    # Frontier 6: Safe Null-Coalescing & Default Fallbacks (otherwise / default)
    # Note: 'verify that <cond> otherwise <msg>' uses 'otherwise' as syntax separator, not null-coalescing.
    is_contract_stmt = bool(re.search(r"^\s*(?:verify|require|ensure|assert|check)\b", masked, re.IGNORECASE))

    if not is_contract_stmt:
        masked = re.sub(
            r"\b([A-Za-z_]\w*)'s\s+([A-Za-z_]\w*)\s+(?:otherwise|default)\s+([^\s,:\);]+(?:\s+[^\s,:\);]+)*)",
            r'ds_attr(\1, "\2", \3)',
            masked,
            flags=re.IGNORECASE
        )
        masked = re.sub(
            r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\s+(?:otherwise|default)\s+([^\s,:\);]+(?:\s+[^\s,:\);]+)*)",
            r'ds_attr(\1, "\2", \3)',
            masked,
            flags=re.IGNORECASE
        )
        masked = re.sub(
            r"\b([A-Za-z_]\w*)\[([^\]]+)\]\s+(?:otherwise|default)\s+([^\s,:\);]+(?:\s+[^\s,:\);]+)*)",
            r"ds_attr(\1, \2, \3)",
            masked,
            flags=re.IGNORECASE
        )
        def _coal_repl(m):
            w = m.group(1)
            if m.start() == 0 or w.lower() in ("with", "by", "from", "to", "in", "at", "on", "as", "of", "verify", "check", "assert", "require", "ensure", "if", "unless", "when", "otherwise", "else"):
                return m.group(0)
            return f"ds_coalesce({w}, {m.group(2)})"

        masked = re.sub(
            r"\b([A-Za-z_]\w*)\s+(?:otherwise|default)\s+([^\s,:\);]+(?:\s+[^\s,:\);]+)*)",
            _coal_repl,
            masked,
            flags=re.IGNORECASE
        )

    # Frontier 1: Disjunctions (either ... or ... / neither ... nor ...)
    masked = re.sub(
        r"\b([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+is\s+either\s+(.+?)\s+or\s+([^\s,:\);]+)",
        r"(\1 is one of [\2, \3])",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+is\s+neither\s+(.+?)\s+nor\s+([^\s,:\);]+)",
        r"(not (\1 is one of [\2, \3]))",
        masked,
        flags=re.IGNORECASE
    )

    # Frontier 2: Proportional percentage arithmetic mutators (increase/decrease by N%)
    inc_pct_m = re.match(
        r"^\s*increase\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+by\s+(?:(\d+(?:\.\d+)?)\s*(?:%|percent)|\((\d+(?:\.\d+)?)\s*/\s*100(?:\.0)?\))\s*$",
        masked,
        re.IGNORECASE
    )
    if inc_pct_m:
        target_v = inc_pct_m.group(1).strip()
        raw_pct = inc_pct_m.group(2) or inc_pct_m.group(3)
        pct_num = float(raw_pct) / 100.0
        masked = f"set {target_v} to {target_v} * {1.0 + pct_num}"

    dec_pct_m = re.match(
        r"^\s*decrease\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s+by\s+(?:(\d+(?:\.\d+)?)\s*(?:%|percent)|\((\d+(?:\.\d+)?)\s*/\s*100(?:\.0)?\))\s*$",
        masked,
        re.IGNORECASE
    )
    if dec_pct_m:
        target_v = dec_pct_m.group(1).strip()
        raw_pct = dec_pct_m.group(2) or dec_pct_m.group(3)
        pct_num = float(raw_pct) / 100.0
        masked = f"set {target_v} to {target_v} * {1.0 - pct_num}"

    # Frontier 3: Composable participle expressions (support calls, identifiers, indexing, parenthesized exprs)
    masked = re.sub(
        r"((?:[A-Za-z_]\w*(?:\([^)]*\)|\[[^\]]+\]|'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*)+|\([^)]+\)|[A-Za-z_]\w*|__STR_LITERAL_\d+__))\s+joined\s+with\s+(.+?)(?=[,\)\n;]|$)",
        r"ds_join(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"((?:[A-Za-z_]\w*(?:\([^)]*\)|\[[^\]]+\]|'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*)+|\([^)]+\)|[A-Za-z_]\w*|__STR_LITERAL_\d+__))\s+split\s+by\s+(.+?)(?=[,\)\n;]|$)",
        r"str_split(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    def _sort_by_repl(m):
        coll = m.group(1)
        attr = m.group(2)
        desc = True if (m.group(3) and m.group(3).lower() == 'descending') else False
        return f"ds_sorted_by({coll}, '{attr}', reverse={desc})"

    masked = re.sub(
        r"\b([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+sorted\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending))?\b",
        _sort_by_repl,
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bsorted\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending))?\b",
        _sort_by_repl,
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bunique\s+(?!(?:of|items|into|where|to|in)\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\b(?!\s+(?:into|where|to|in|of)\b)",
        r"unique of \1",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"(?<!^)\btake\s+(\d+|[A-Za-z_]\w*)\s+(?:items\s+)?from\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\b",
        r"ds_take(\2, \1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"(?<!^)\bdrop\s+(\d+|[A-Za-z_]\w*)\s+(?:items\s+)?from\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\b",
        r"ds_drop(\2, \1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\b(?!(?:say|show|print|display|return|yield|if|while|until|to|in|into|of|from|as|with|set|let|put|the|a|an)\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+sorted\b(?!\s+(?:by|of)\b)(?!\s*\()",
        r"sorted(\1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(r"\b([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+trimmed\b", r"ds_trim(\1)", masked, flags=re.IGNORECASE)
    
    # Nested and composable casing: uppercase of X / lowercase of X / trim of X
    first_last_of = r"(?:first|last)\s+(?:item\s+)?of\s+[A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?"
    casing_sub_expr = rf"(?:{first_last_of}|__STR_LITERAL_\d+__|[A-Za-z_]\w*(?:\([^)]*\)|\[[^\]]+\]|\.[A-Za-z_]\w*)+|\([^)]+\)|(?!(?:uppercase|lowercase|trim)\b)[A-Za-z_]\w*)"
    casing_pat = rf"\b(?:the\s+)?(uppercase|lowercase|trim)\s+of\s+({casing_sub_expr})(?=\s*(?:[,\)\n;]|#|$))"
    for _ in range(4):
        new_masked = re.sub(casing_pat, lambda m: f"ds_{m.group(1).lower()}({m.group(2)})", masked, flags=re.IGNORECASE)
        if new_masked == masked:
            break
        masked = new_masked

    # Participle case: X uppercase / X lowercase (excluding keywords & verbs)
    masked = re.sub(r"\b(?!(?:to|in|into|of|from|as|with|say|show|print|display|set|let|put|the|a|an|ds_\w+)\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+uppercase\b", r"ds_uppercase(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?!(?:to|in|into|of|from|as|with|say|show|print|display|set|let|put|the|a|an|ds_\w+)\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+lowercase\b", r"ds_lowercase(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?!(?:to|in|into|of|from|as|with|say|show|print|display|set|let|put|the|a|an|ds_\w+)\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+reversed\b", r"ds_reversed(\1)", masked, flags=re.IGNORECASE)

    # Frontier 4: Range Literals and Loops
    masked = re.sub(
        r"^\s*for\s+(?:each\s+)?([A-Za-z_]\w*)\s+in\s+(.+?)\s+to\s+(.+?)\s*:",
        r"for each \1 from \2 to \3:",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\[\s*(\d+|[A-Za-z_]\w*|__STR_\d+__)\s+to\s+(\d+|[A-Za-z_]\w*|__STR_\d+__)\s*\]",
        r"ds_range(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )

    # Membership: collection has item -> collection contains item
    def _repl_has_membership(m):
        subj = m.group(1).strip()
        val = m.group(2).strip()
        if val.lower() in ("many", "one"):
            return m.group(0)
        start = m.start()
        prefix = masked[:start].rstrip()
        if re.search(r"\b(?:a|an)\s+[A-Za-z_]\w*$", prefix, re.I):
            return m.group(0)
        return f"{subj} contains {val}"

    masked = re.sub(
        r"\b([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)\s+has\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?|\d+(?:\.\d+)?|__STR_LITERAL_\d+__)\b",
        _repl_has_membership,
        masked,
        flags=re.IGNORECASE
    )

    # Chained possessives: A's B's C -> get_field(get_field(A, "B"), "C")
    while re.search(r"\b([A-Za-z_]\w*)'s\s+([A-Za-z_]\w*)'s\s+([A-Za-z_]\w*)", masked):
        masked = re.sub(
            r"\b([A-Za-z_]\w*)'s\s+([A-Za-z_]\w*)'s\s+([A-Za-z_]\w*)",
            r'get_field(get_field(\1, "\2"), "\3")',
            masked
        )

    # Disambiguate reserved words used as standalone variable names
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<!\bto\s)(?<![\"'])\bcount\b(?![\"'])(?!\s+of\b)(?!\s+from\b)(?!\s+into\b)(?!\s*\()", "_var_count", masked)
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<!\bto\s)(?<![\"'])\bsum\b(?![\"'])(?!\s+of\b)(?!\s*\()", "_var_sum", masked)
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<![\"'])\badd\b(?![\"'])(?!\s+(?:.+?\s+)?(?:to|into)\b)", "_var_add", masked)
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<!\bto\s)(?<!\bbullet\s)(?<!\ba\s)(?<!\bempty\s)(?<!\bnew\s)(?<![\"'])\blist\b(?![\"'])(?!\s+files\b)(?!\s+of\b)(?!\s*\()", "_var_list", masked)
    # Removed _var_first hack (first is now a first-class ident in grammar)
    # Preposition flexibility: add <item> into <target>
    masked = re.sub(
        r"^\s*add\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
        r"add \1 to \2",
        masked,
        flags=re.IGNORECASE
    )

    # Elliptical branching: if so: / if not:
    if re.match(r"^\s*if\s+so\s*:", masked, re.IGNORECASE):
        last_v = scope.get_last_singular() or scope.get_last_var() or "true"
        masked = f"if {last_v}:"
    masked = re.sub(r"^\s*if\s+not\s*:", "else:", masked, flags=re.IGNORECASE)

    # Imperative & Nominal string case transformations
    m_up_into = re.match(r"^\s*uppercase\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if m_up_into:
        masked = f"set {m_up_into.group(2)} to ds_uppercase({m_up_into.group(1).strip()})"

    m_low_into = re.match(r"^\s*lowercase\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if m_low_into:
        masked = f"set {m_low_into.group(2)} to ds_lowercase({m_low_into.group(1).strip()})"

    if not re.search(r"\binto\b", masked, re.IGNORECASE):
        m_up_bare = re.match(r"^\s*uppercase\s+([^\s].*)$", masked, re.IGNORECASE)
        if m_up_bare:
            masked = f"set that to ds_uppercase({m_up_bare.group(1).strip()})"

        m_low_bare = re.match(r"^\s*lowercase\s+([^\s].*)$", masked, re.IGNORECASE)
        if m_low_bare:
            masked = f"set that to ds_lowercase({m_low_bare.group(1).strip()})"

    masked = re.sub(r"\b(?:the\s+)?uppercase\s+of\s+([^\s,;:\)]+)", r"ds_uppercase(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?lowercase\s+of\s+([^\s,;:\)]+)", r"ds_lowercase(\1)", masked, flags=re.IGNORECASE)

    masked = re.sub(r"\bround\s*\(", "math_round(", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(?<!\.)\bsum\s*\(", "agg_sum(", masked, flags=re.IGNORECASE)

    # Arithmetic in words
    double_m = re.match(r"^\s*double\s+([A-Za-z_]\w*)\s*$", masked, re.IGNORECASE)
    if double_m:
        var = double_m.group(1)
        masked = f"set {var} to {var} * 2"

    masked = re.sub(r"(\d+(?:\.\d+)?)\s*%\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])*|\d+(?:\.\d+)?|\([^)]+\))", r"percent_of(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+to\s+(?:the\s+)?power\s+of\s+(\b\w+|\()", r"math_pow(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+squared\b", r"math_pow(\1, 2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bmod\b", "%", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+plus\s+(\b\w+|\()", r"\1 + \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+minus\s+(\b\w+|\()", r"\1 - \2", masked, flags=re.IGNORECASE)
    if not re.match(r"^\s*repeat\b", masked, re.IGNORECASE):
        masked = re.sub(r"(\b\w+|\))\s+times\s+(\b\w+|\()", r"\1 * \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+multiplied\s+by\s+(\b\w+|\()", r"\1 * \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?remainder\s+of\s+(.+?)\s+(?:divided\s+by|mod|/)\s+([^\s;,\n]+)", r"(\1 % \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+divided\s+by\s+(\b\w+|\()", r"\1 / \2", masked, flags=re.IGNORECASE)

    # Arithmetic Mutators in English
    masked = re.sub(r"^\s*increment\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"increase \1 by \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*increment\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"increase \1 by 1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*decrement\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"decrease \1 by \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*decrement\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"decrease \1 by 1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*subtract\s+(.+?)\s+from\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$", r"decrease \2 by \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*bump\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"increase \1 by \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*bump\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"increase \1 by 1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*multiply\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"set \1 to \1 * \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*divide\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"set \1 to \1 / \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*halve\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"set \1 to \1 / 2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*triple\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"set \1 to \1 * 3", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:clear|empty)\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"set \1 to []", masked, flags=re.IGNORECASE)

    # List Mutators in English
    masked = re.sub(r"^\s*append\s+(.+?)\s+to\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s*$", r"add \1 to \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*push\s+(.+?)\s+(?:to|into)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s*$", r"add \1 to \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:discard|delete)\s+(.+?)\s+from\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s*$", r"remove \1 from \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:pop\s+(?:from\s+)?|remove\s+last\s+(?:item\s+)?from\s+)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s*$", r"pop(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(?<!def\s)(?<!to\s)\bpop\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\b", r"pop(\1)", masked, flags=re.IGNORECASE)

    # Loop Controls & Flow
    masked = re.sub(
        r"^\s*for\s+(?:each\s+)?([A-Za-z_]\w*)\s+in\s+(.+?)\s+count(?:\s+from\s+(\d+))?\s+into\s+([A-Za-z_]\w*):?\s*$",
        lambda m: f"for each {m.group(4)}, {m.group(1)} in enumerate({m.group(2)}, {m.group(3)}):" if m.group(3) else f"for each {m.group(4)}, {m.group(1)} in enumerate({m.group(2)}):",
        masked,
        flags=re.IGNORECASE,
    )
    masked = re.sub(r"^\s*for\s+(?:all|each\s+of\s+the|every)\s+([A-Za-z_]\w*)\s+in\b", r"for each \1 in", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*for\s+each\s+([A-Za-z_]\w*)\s+of\b", r"for each \1 in", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*for\s+(?!each\b)(.+?)\s+in\b", r"for each \1 in", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*loop\s+(?:through|over)\s+(.+?)\s+as\s+([A-Za-z_]\w*):", r"for each \2 in \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*as\s+long\s+as\s+(.+?):", r"while \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*until\s+(.+?):", r"while not (\1):", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*repeat\s+while\s+(.+?):", r"while \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*repeat\s+until\s+(.+?):", r"while not (\1):", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:break\s+out\s+of\s+(?:the\s+)?loop|break\s+loop|exit\s+loop|stop\s+loop|break)\s*$", "stop", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:skip\s+to\s+next|skip\s+(?:this\s+)?iteration|continue\s+loop|next\s+iteration|continue)\s*$", "skip", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\brepeat\s+with\s+([A-Za-z_]\w*)\s+from\s+(.+?)\s+down\s+to\s+(.+?)(?=:|\n|$)", r"repeat with \1 from \2 to \3 by -1", masked, flags=re.IGNORECASE)

    # Phase 3: Class Dunder Methods, Constructors, and Super
    masked = re.sub(r"^\s*(?:to\s+(?:start|init)|constructor)\s+with\s+(.+?):", r"to __init__ with \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:to\s+(?:start|init)|constructor)\s*:", r"to __init__:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*to\s+describe\s*:", r"to __repr__:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*to\s+get\s+length\s*:", r"to __len__:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*to\s+get\s+item\s+with\s+(.+?):", r"to __getitem__ with \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*to\s+set\s+item\s+with\s+(.+?):", r"to __setitem__ with \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:base|super)\s+(?:start|init|initialize|create|setup|constructor)\s+with\s+(.+)$", r"super().__init__(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:base|super)\s+(?:start|init|initialize|create|setup|constructor)\s*$", r"super().__init__()", masked, flags=re.IGNORECASE)

    # Function Definition & Returns
    masked = re.sub(r"^\s*def\s+([A-Za-z_]\w*)\s*\(\s*(.*?)\s*\)\s*:?", lambda m: f"to {m.group(1)} with {m.group(2).strip()}:" if m.group(2).strip() else f"to {m.group(1)}:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:how\s+to|define|function)\s+([A-Za-z_]\w*)\s+with\s+(.+?):", r"to \1 with \2:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:how\s+to|define|function)\s+([A-Za-z_]\w*):", r"to \1:", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:the\s+)?result\s+is\s+(.+)$", r"return \1", masked, flags=re.IGNORECASE)

    # Conditions & Parity
    _SUBJ_PAT = r"(\d+(?:\.\d+)?|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?|\([^\)]+\))"
    masked = re.sub(rf"\b{_SUBJ_PAT}\s+is\s+divisible\s+by\s+([A-Za-z_]\w*|\d+)\b", r"math_mod(\1, \2) is 0", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\b{_SUBJ_PAT}\s+is\s+not\s+divisible\s+by\s+([A-Za-z_]\w*|\d+)\b", r"math_mod(\1, \2) is not 0", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\b{_SUBJ_PAT}\s+is\s+(?:a\s+)?multiple\s+of\s+([A-Za-z_]\w*|\d+)\b", r"math_mod(\1, \2) is 0", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\b{_SUBJ_PAT}\s+is\s+blank\b", r"\1 is empty", masked, flags=re.IGNORECASE)
    masked = re.sub(rf"\b{_SUBJ_PAT}\s+is\s+not\s+blank\b", r"\1 is not empty", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+does\s+not\s+contain\s+(.+?)(?=\s+and\b|\s+or\b|:|\n|$)", r"not (\1 contains \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+does\s+not\s+start\s+with\s+(.+?)(?=\s+and\b|\s+or\b|:|\n|$)", r"not (\1 starts with \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+does\s+not\s+end\s+with\s+(.+?)(?=\s+and\b|\s+or\b|:|\n|$)", r"not (\1 ends with \2)", masked, flags=re.IGNORECASE)
    # Handled natively in Lark grammar via IS_BETWEEN and IS_OUTSIDE
    pass
    masked = re.sub(r"\b([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s+is\s+neither\s+(.+?)\s+nor\s+([^\s;,\n]+)", r"not (\1 is \2 or \1 is \3)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"""(\b\w+(?:\[[^\]]+\]|\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\))\s+is\s+(?:inside|in)\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?|\[[^\]]*\]|\{[^\}]*\}|"[^"]*"|'[^']*')""", r"\1 is inside \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"""(\b\w+(?:\[[^\]]+\]|\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\))\s+(?:is\s+)?(?:not\s+(?:inside|in)|isn't\s+(?:inside|in))\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?|\[[^\]]*\]|\{[^\}]*\}|"[^"]*"|'[^']*')""", r"\1 is not inside \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b([A-Za-z_]\w*(?:\[[^\]]+\])?|\d+)\s+xor\s+([A-Za-z_]\w*(?:\[[^\]]+\])?|\d+)\b", r"\1 ^ \2", masked, flags=re.IGNORECASE)
    
    # Membership 'in' operator: x in y -> x is inside y (excluding for-loops, comprehensions, and statement keywords)
    if not re.match(r"^\s*(?:set\s+(?:cookie|config)|remember\s+in\s+memory|mask\s+pii|list\s+files|start\s+server|insert\b|replace\b|display\s+colored|fill\b)\b", masked, re.IGNORECASE):
        def _in_repl(m):
            if m.group(2).lower() in ("background", "bytes", "seconds", "minutes", "hours", "milliseconds", "days"):
                return m.group(0)
            if m.group(1).lower() in ("highest", "maximum", "lowest", "minimum", "files", "nulls", "missing", "items", "now", "is", "not", "isn't", "inside"):
                return m.group(0)
            if re.search(r"\b(?:is|not|isn't)\s*$", masked[:m.start()], re.IGNORECASE):
                return m.group(0)
            full_prefix = masked[:m.start()] + m.group(1)
            if re.search(r"\bfor\s+(?:each\s+)?([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*)$", full_prefix, re.IGNORECASE):
                return m.group(0)
            if re.search(r"\beach\s+[A-Za-z_]\w*$", full_prefix, re.IGNORECASE):
                return m.group(0)
            prefix = masked[:m.start()]
            if re.search(r"\b(?:insert|replace|fill|files|nulls|missing|background|highest|lowest|maximum|minimum|items)\s+(?:[^\n]*\s+)?$", prefix, re.IGNORECASE):
                return m.group(0)
            if re.search(r"\b(?:sum|average|avg|count|number)\s+of\s+(?:items\s+)?$", prefix, re.IGNORECASE):
                return m.group(0)
            return f"{m.group(1)} is inside {m.group(2)}"

        masked = re.sub(
            r"(\b\w+(?:\[[^\]]+\]|\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\))\s+in\s+([A-Za-z_]\w*(?:\[[^\]]+\]|\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\[|\(|\{)",
            _in_repl,
            masked,
            flags=re.IGNORECASE,
        )
    masked = re.sub(r"(\b\w+(?:'s\s+[A-Za-z_]\w*)?|\))\s+is\s+not\s+one\s+of\s+([\[A-Za-z_].*?)(?=\s+and\b|\s+or\b|:|\n|$)", r"not (\1 is one of \2)", masked, flags=re.IGNORECASE)

    # Fractions and Multiples
    masked = re.sub(r"\bhalf\s+of\s+([A-Za-z_]\w*|\d+)\b", r"(\1 / 2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bquarter\s+of\s+([A-Za-z_]\w*|\d+)\b", r"(\1 / 4)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:double|twice)\s+of\s+([A-Za-z_]\w*|\d+)\b", r"(\1 * 2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\btriple\s+of\s+([A-Za-z_]\w*|\d+)\b", r"(\1 * 3)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?remainder\s+of\s+(.+?)\s+(?:divided\s+by|mod|/)\s+([^\s;,\n]+)", r"(\1 % \2)", masked, flags=re.IGNORECASE)

    # Dict keys, values, and entries in English
    masked = re.sub(r"\b(?:the\s+)?keys\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)", r"ds_keys(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?values\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)", r"ds_values(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?(?:entries|pairs)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)", r"ds_items(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(?<!\bunique\s)\b(?:the\s+)?items\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*|\.[A-Za-z_]\w*|\[[^\]]+\])?)", r"ds_items(\1)", masked, flags=re.IGNORECASE)
    # Loop over key and value
    masked = re.sub(r"\bfor\s+(?:each\s+)?([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+in\b", r"for each \1, \2 in", masked, flags=re.IGNORECASE)

    # Lists, Text, and Aggregates
    masked = re.sub(r"\bhow\s+many\s+items\s+are\s+in\s+([A-Za-z_]\w*)", r"count of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:how\s+many|number\s+of)\s+items\s+in\s+(\[[^\]]*\]|[A-Za-z_]\w*)", r"count of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bthe\s+count\s+of\s+([A-Za-z_]\w*)", r"count of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?(?:length|size)\s+of\s+([A-Za-z_]\w*)", r"count of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?reverse\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*)", r"reversed of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bmean\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w+)", r"average of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?sum\s+of\s+all\s+(\[[^\]]*\]|[A-Za-z_]\w+)", r"sum of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bthe\s+sum\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w+)(?!\s+in\b)", r"sum of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\btotal\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*)(?!\s+in\b)", r"sum of \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bproduct\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w+)", r"math_product(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bmaximum\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*)", r"highest in \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bminimum\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*)", r"lowest in \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bmedian\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*)\b(?!\s+into\b)", r"math_median(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?(?:standard\s+deviation|std_dev|stdev)\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\([^)]+\))\b(?!\s+into\b)", r"std_dev(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?variance\s+of\s+(\[[^\]]*\]|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\([^)]+\))\b(?!\s+into\b)", r"variance(\1)", masked, flags=re.IGNORECASE)

    # Text & Type Transformations
    masked = re.sub(r"\bstrip\s+(?:spaces|whitespace)\s+from\s+(.+?)(?=\s+and\s+then|\s+into\b|\s*$|\))", r"str_trim(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\btrim\s+spaces\s+from\s+(.+?)(?=\s+and\s+then|\s+into\b|\s*$|\))", r"str_trim(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\btitle\s+case\s+of\s+(.+?)(?=\s+and\s+then|\s+into\b|\s*$|\))", r"str_title(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bconvert\s+(?!hex\b|binary\b)(.+?)\s+to\s+text\s+into\s+([A-Za-z_]\w*)", r"set \2 to to_text(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bturn\s+(?!hex\b|binary\b)(.+?)\s+into\s+text\s+into\s+([A-Za-z_]\w*)", r"set \2 to to_text(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bconvert\s+(?!hex\b|binary\b)(.+?)\s+to\s+number\s+into\s+([A-Za-z_]\w*)", r"set \2 to to_number(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bturn\s+(?!hex\b|binary\b)(.+?)\s+into\s+number\s+into\s+([A-Za-z_]\w*)", r"set \2 to to_number(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bto\s+text\s+(?!into\b)([A-Za-z_]\w*)\b", r"to_text(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bto\s+number\s+(?!into\b)([A-Za-z_]\w*)\b", r"to_number(\1)", masked, flags=re.IGNORECASE)

    # Relative Dates
    masked = re.sub(r"\byesterday\b", "date_yesterday()", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\btomorrow\b", "date_tomorrow()", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bcurrent\s+date\b", "date_today()", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bcurrent\s+timestamp\b", "date_now()", masked, flags=re.IGNORECASE)

    # Call statement without 'call' keyword: e.g. greet "Bob"
    call_no_kw_m = re.match(r"^\s*([A-Za-z_]\w*)\s+(__STR_LITERAL_\d+__|[\"'].*?[\"']|\d+|\[.*?\])\s*$", masked)
    if call_no_kw_m:
        func_word = call_no_kw_m.group(1).lower()
        if func_word not in STATEMENT_START_KEYWORDS:
            close_kw = difflib.get_close_matches(func_word, ["say", "print"], n=1, cutoff=0.65)
            if not close_kw:
                masked = f"{call_no_kw_m.group(1)}({call_no_kw_m.group(2)})"

    # Phase 4 Table Joins
    masked = re.sub(
        r"\bcombine\s+(.+?)\s+and\s+(.+?)\s+on\s+(.+?)\s+with\s+style\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\5 = combine_tables(\1, \2, \3, \4)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bcombine\s+(.+?)\s+and\s+(.+?)\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\4 = combine_tables(\1, \2, \3)",
        masked,
        flags=re.IGNORECASE
    )

    # Phase 4 HTML Extraction
    masked = re.sub(
        r"\bextract\s+text\s+from\s+html\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\2 = extract_html_text(\1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bextract\s+links\s+from\s+html\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\2 = extract_html_links(\1)",
        masked,
        flags=re.IGNORECASE
    )

    # Phase 4 HTTP Requests
    masked = re.sub(
        r"\bfetch\s+url\s+(.+?)\s+with\s+headers\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\3 = fetch_url(\1, headers=\2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bfetch\s+url\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\2 = fetch_url(\1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bpost\s+json\s+(.+?)\s+to\s+(.+?)\s+with\s+headers\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\4 = fetch_url(\2, method='POST', headers=\3, json_body=\1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bpost\s+json\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\3 = fetch_url(\2, method='POST', json_body=\1)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bdownload\s+(.+?)\s+to\s+file\s+(.+?)$",
        r"download_file_url(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )

    # Phase 4 Email Sending
    masked = re.sub(
        r"\bsend\s+email\s+to\s+(.+?)\s+with\s+subject\s+(.+?)\s+and\s+body\s+(.+?)\s+into\s+([A-Za-z_]\w*)",
        r"\4 = send_email(\1, \2, \3)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"\bsend\s+email\s+to\s+(.+?)\s+with\s+subject\s+(.+?)\s+and\s+body\s+(.+?)$",
        r"send_email(\1, \2, \3)",
        masked,
        flags=re.IGNORECASE
    )

    # Phase 4 Date & Timezones
    masked = re.sub(r"\bnow\s+in\s+([^\s;,\n]+)", r"date_now_in(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bnext\s+business\s+day\s+from\s+([^\s;,\n]+)", r"next_business_day(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:today\s+)?is\s+weekend\b", r"is_weekend()", masked, flags=re.IGNORECASE)

    # Phase 8 Contracts: require and ensure
    req_otherwise_m = re.match(r"^require\s+(.+?)\s+otherwise\s+(.+)$", masked, re.IGNORECASE)
    if req_otherwise_m:
        cond_part = req_otherwise_m.group(1).strip()
        cond_part = re.sub(r"^that\s+", "", cond_part, flags=re.IGNORECASE).strip()
        msg_part = req_otherwise_m.group(2).strip()
        masked = f"verify that {cond_part} otherwise {msg_part}"
    else:
        req_m = re.match(r"^require\s+(.+)$", masked, re.IGNORECASE)
        if req_m:
            cond_part = req_m.group(1).strip()
            cond_part = re.sub(r"^that\s+", "", cond_part, flags=re.IGNORECASE).strip()
            orig_cond_text = unmask_strings(cond_part, strings)
            safe_cond = orig_cond_text.replace('"', "'")
            msg_literal = f'"Requirement failed: {safe_cond}"'
            msg_idx = len(strings)
            strings.append(msg_literal)
            masked = f"verify that {cond_part} otherwise __STR_LITERAL_{msg_idx}__"

    ens_otherwise_m = re.match(r"^ensure\s+(.+?)\s+otherwise\s+(.+)$", masked, re.IGNORECASE)
    if ens_otherwise_m:
        cond_part = ens_otherwise_m.group(1).strip()
        cond_part = re.sub(r"^that\s+", "", cond_part, flags=re.IGNORECASE).strip()
        msg_part = ens_otherwise_m.group(2).strip()
        masked = f"verify that {cond_part} otherwise {msg_part}"
    else:
        ens_m = re.match(r"^ensure\s+(.+)$", masked, re.IGNORECASE)
        if ens_m:
            cond_part = ens_m.group(1).strip()
            cond_part = re.sub(r"^that\s+", "", cond_part, flags=re.IGNORECASE).strip()
            orig_cond_text = unmask_strings(cond_part, strings)
            safe_cond = orig_cond_text.replace('"', "'")
            msg_literal = f'"Postcondition failed: {safe_cond}"'
            msg_idx = len(strings)
            strings.append(msg_literal)
            masked = f"verify that {cond_part} otherwise __STR_LITERAL_{msg_idx}__"

    # Phase 9: Destructuring
    head_tail_m = re.match(r"^first\s+item\s+into\s+([A-Za-z_]\w*)\s*,\s*remaining\s+items\s+into\s+([A-Za-z_]\w*)\s+from\s+(.+)$", masked, re.IGNORECASE)
    if head_tail_m:
        h_var = head_tail_m.group(1)
        t_var = head_tail_m.group(2)
        c_expr = head_tail_m.group(3).strip()
        masked = f"set {h_var} to head_of({c_expr}) and then set {t_var} to tail_of({c_expr})"

    unpack_m = re.match(r"^unpack\s+(?!binary\b)(.+?)\s+from\s+(.+)$", masked, re.IGNORECASE)
    if unpack_m:
        targets_raw = [t.strip() for t in unpack_m.group(1).split(",")]
        c_expr = unpack_m.group(2).strip()
        quoted_keys = "[" + ", ".join(f'"{t}"' for t in targets_raw) + "]"
        tmp_unp = f"__unp_{line_num}"
        unp_stmts = [f"set {tmp_unp} to unpack_values({quoted_keys}, {c_expr})"]
        for idx, t in enumerate(targets_raw, 1):
            unp_stmts.append(f"set {t} to item {idx} of {tmp_unp}")
        masked = " and then ".join(unp_stmts)

    # Phase 10: Testing Assertions (expect ... to ...)
    exp_eq_m = re.match(r"^expect\s+(.+?)\s+to\s+equal\s+(.+)$", masked, re.IGNORECASE)
    if exp_eq_m:
        e_expr = exp_eq_m.group(1).strip()
        e_exp = exp_eq_m.group(2).strip()
        masked = f'verify that {e_expr} equals {e_exp} otherwise "Expectation failed: equality check"'

    exp_num_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:a\s+)?number$", masked, re.IGNORECASE)
    if exp_num_m:
        e_expr = exp_num_m.group(1).strip()
        masked = f'verify that {e_expr} is a number otherwise "Expectation failed: value is not a number"'

    exp_txt_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:a\s+)?(?:text|string)$", masked, re.IGNORECASE)
    if exp_txt_m:
        e_expr = exp_txt_m.group(1).strip()
        masked = f'verify that {e_expr} is text otherwise "Expectation failed: value is not text"'

    exp_bool_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:a\s+)?(?:boolean|bool)$", masked, re.IGNORECASE)
    if exp_bool_m:
        e_expr = exp_bool_m.group(1).strip()
        masked = f'verify that {e_expr} is a boolean otherwise "Expectation failed: value is not a boolean"'

    exp_list_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:a\s+)?list$", masked, re.IGNORECASE)
    if exp_list_m:
        e_expr = exp_list_m.group(1).strip()
        masked = f'verify that {e_expr} is a list otherwise "Expectation failed: value is not a list"'

    exp_rec_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:a\s+)?(?:record|dictionary|dict)$", masked, re.IGNORECASE)
    if exp_rec_m:
        e_expr = exp_rec_m.group(1).strip()
        masked = f'verify that {e_expr} is a record otherwise "Expectation failed: value is not a record"'

    exp_gt_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:greater\s+than|over)\s+(.+)$", masked, re.IGNORECASE)
    if exp_gt_m:
        e_expr = exp_gt_m.group(1).strip()
        e_val = exp_gt_m.group(2).strip()
        masked = f'verify that {e_expr} is greater than {e_val} otherwise "Expectation failed: value not greater"'

    exp_ge_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:at\s+least|no\s+less\s+than)\s+(.+)$", masked, re.IGNORECASE)
    if exp_ge_m:
        e_expr = exp_ge_m.group(1).strip()
        e_val = exp_ge_m.group(2).strip()
        masked = f'verify that {e_expr} is at least {e_val} otherwise "Expectation failed: value not at least"'

    exp_lt_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:less\s+than|under)\s+(.+)$", masked, re.IGNORECASE)
    if exp_lt_m:
        e_expr = exp_lt_m.group(1).strip()
        e_val = exp_lt_m.group(2).strip()
        masked = f'verify that {e_expr} is less than {e_val} otherwise "Expectation failed: value not less"'

    exp_le_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(?:at\s+most|no\s+more\s+than)\s+(.+)$", masked, re.IGNORECASE)
    if exp_le_m:
        e_expr = exp_le_m.group(1).strip()
        e_val = exp_le_m.group(2).strip()
        masked = f'verify that {e_expr} is at most {e_val} otherwise "Expectation failed: value not at most"'

    exp_be_val_m = re.match(r"^expect\s+(.+?)\s+to\s+be\s+(.+)$", masked, re.IGNORECASE)
    if exp_be_val_m:
        e_expr = exp_be_val_m.group(1).strip()
        e_exp = exp_be_val_m.group(2).strip()
        masked = f'verify that {e_expr} equals {e_exp} otherwise "Expectation failed: equality check"'

    exp_cont_m = re.match(r"^expect\s+(.+?)\s+to\s+contain\s+(.+)$", masked, re.IGNORECASE)
    if exp_cont_m:
        e_expr = exp_cont_m.group(1).strip()
        e_val = exp_cont_m.group(2).strip()
        masked = f'verify that {e_expr} contains {e_val} otherwise "Expectation failed: value does not contain item"'

    # Phase 11: CLI Builder
    cli_desc_m = re.match(r"^program\s+description\s+(.+)$", masked, re.IGNORECASE)
    if cli_desc_m:
        masked = f"cli_set_description({cli_desc_m.group(1).strip()})"

    cli_opt_type_m = re.match(r"^option\s+([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w+)\s+with\s+default\s+(.+?)\s+and\s+description\s+(.+)$", masked, re.IGNORECASE)
    if cli_opt_type_m:
        o_name = cli_opt_type_m.group(1)
        o_type = cli_opt_type_m.group(2).lower()
        o_def = cli_opt_type_m.group(3).strip()
        o_desc = cli_opt_type_m.group(4).strip()
        masked = f'cli_add_option("{o_name}", default={o_def}, opt_type="{o_type}", help_text={o_desc})'
    else:
        cli_opt_m = re.match(r"^option\s+([A-Za-z_]\w*)\s+with\s+default\s+(.+?)\s+and\s+description\s+(.+)$", masked, re.IGNORECASE)
        if cli_opt_m:
            o_name = cli_opt_m.group(1)
            o_def = cli_opt_m.group(2).strip()
            o_desc = cli_opt_m.group(3).strip()
            masked = f'cli_add_option("{o_name}", default={o_def}, help_text={o_desc})'

    cli_flag_m = re.match(r"^flag\s+([A-Za-z_]\w*)\s+with\s+description\s+(.+)$", masked, re.IGNORECASE)
    if cli_flag_m:
        f_name = cli_flag_m.group(1)
        f_desc = cli_flag_m.group(2).strip()
        masked = f'cli_add_flag("{f_name}", help_text={f_desc})'

    cli_parse_m = re.match(r"^parse\s+arguments\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if cli_parse_m:
        t_var = cli_parse_m.group(1)
        masked = f"set {t_var} to cli_parse_arguments()"

    # Phase 12: Concurrency & Timers
    bg_m = re.match(r"^run\s+in\s+background\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if bg_m:
        fn_call = bg_m.group(1).strip()
        t_var = bg_m.group(2)
        fn_call_m = re.match(r"^([A-Za-z_]\w*)\((.*)\)$", fn_call)
        if fn_call_m:
            fn_name = fn_call_m.group(1)
            fn_args = fn_call_m.group(2).strip()
            if fn_args:
                masked = f"set {t_var} to spawn_background_task({fn_name}, {fn_args})"
            else:
                masked = f"set {t_var} to spawn_background_task({fn_name})"
        else:
            masked = f"set {t_var} to spawn_background_task({fn_call})"

    wait_all_m = re.match(r"^wait\s+for\s+all\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if wait_all_m:
        t_list = wait_all_m.group(1).strip()
        t_var = wait_all_m.group(2)
        masked = f"set {t_var} to wait_all_background_tasks({t_list})"
    else:
        wait_one_m = re.match(r"^wait\s+for\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
        if wait_one_m:
            t_task = wait_one_m.group(1)
            t_var = wait_one_m.group(2)
            masked = f"set {t_var} to wait_background_task({t_task})"

    timeout_m = re.match(r"^timeout\s+(.+?)(?:\s+seconds?)?\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if timeout_m:
        sec = timeout_m.group(1).strip()
        fn_call = timeout_m.group(2).strip()
        t_var = timeout_m.group(3)
        fn_call_m = re.match(r"^([A-Za-z_]\w*)\((.*)\)$", fn_call)
        if fn_call_m:
            fn_name = fn_call_m.group(1)
            fn_args = fn_call_m.group(2).strip()
            if fn_args:
                masked = f"set {t_var} to timeout_call({sec}, {fn_name}, {fn_args})"
            else:
                masked = f"set {t_var} to timeout_call({sec}, {fn_name})"
        else:
            masked = f"set {t_var} to timeout_call({sec}, {fn_call})"

    # Phase 13: Web Server High-Level Verbs
    masked = re.sub(r"^reply\s+with\s+json\s+(.+)$", r"return \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^reply\s+with\s+(.+)$", r"return \1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^serve\s+on\s+port\s+(.+?)\s+in\s+background\s+into\s+([A-Za-z_]\w*)$", r"start server on port \1 in background into \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^serve\s+on\s+port\s+(.+)$", r"start server on port \1", masked, flags=re.IGNORECASE)

    # Phase 14: AI / LLM
    ai_json_m = re.match(r"^ask\s+ai\s+(.+?)\s+as\s+json\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if ai_json_m:
        masked = f"set {ai_json_m.group(2)} to ask_ai_json({ai_json_m.group(1).strip()})"
    else:
        ai_model_m = re.match(r"^ask\s+ai\s+(.+?)\s+with\s+model\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
        if ai_model_m:
            masked = f"set {ai_model_m.group(3)} to ask_ai_model({ai_model_m.group(1).strip()}, {ai_model_m.group(2).strip()})"
        else:
            ai_simple_m = re.match(r"^ask\s+ai\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
            if ai_simple_m:
                masked = f"set {ai_simple_m.group(2)} to ask_ai({ai_simple_m.group(1).strip()})"

    # Phase 15: Declarative English Database ORM
    orm_def_m = re.match(r"^define\s+entity\s+([A-Za-z_]\w*)\s+with\s+(.+)$", masked, re.IGNORECASE)
    if orm_def_m:
        ename = orm_def_m.group(1)
        f_str = orm_def_m.group(2)
        field_parts = [f.strip() for f in f_str.split(",")]
        kwargs = []
        for fp in field_parts:
            m_f = re.match(r"^([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w+)$", fp, re.IGNORECASE)
            if m_f:
                kwargs.append(f'{m_f.group(1)}="{m_f.group(2).lower()}"')
        masked = f'orm_define("{ename}", {", ".join(kwargs)})'

    orm_save_m = re.match(r"^(?:save\s+new|create\s+(?:a\s+|an\s+)?)\s*(?!jwt\b)([A-Za-z_]\w*)(?:\s+with\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if orm_save_m:
        ename = orm_save_m.group(1)
        vals_str = orm_save_m.group(2)
        target = orm_save_m.group(3)
        kwargs = []
        if vals_str:
            val_pairs = [v.strip() for v in re.split(r",\s*", vals_str)]
            for vp in val_pairs:
                m_vp = re.match(r"^([A-Za-z_]\w*)[:\s]+(.+)$", vp)
                if m_vp:
                    kwargs.append(f'{m_vp.group(1)}={m_vp.group(2).strip()}')
        kwargs_str = f', {", ".join(kwargs)}' if kwargs else ""
        if masked.lower().startswith("save new"):
            masked = f'set {target} to orm_save("{ename}"{kwargs_str})'
        else:
            masked = f'set {target} to make_entity("{ename}"{kwargs_str})' 

    orm_find_all_m = re.match(r"^find\s+all\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if orm_find_all_m:
        ename = orm_find_all_m.group(1)
        singular = ename[:-1] if ename.endswith("s") else ename
        masked = f'set {orm_find_all_m.group(2)} to orm_find_all("{singular}")'

    orm_find_one_m = re.match(r"^find\s+first\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if orm_find_one_m:
        ename = orm_find_one_m.group(1)
        singular = ename[:-1] if ename.endswith("s") else ename
        masked = f'set {orm_find_one_m.group(2)} to orm_find_first("{singular}")'

    # Phase 17: English Markdown & Rich Document Generator
    doc_create_m = re.match(r"^create\s+(?:markdown\s+)?document\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_create_m:
        masked = f"set {doc_create_m.group(1)} to doc_create()"

    doc_head_lvl_m = re.match(r"^add\s+heading\s+(.+?)\s+at\s+level\s+(\d+)\s+to\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_head_lvl_m:
        masked = f"doc_add_heading({doc_head_lvl_m.group(3)}, {doc_head_lvl_m.group(1).strip()}, {doc_head_lvl_m.group(2)})"
    else:
        doc_head_m = re.match(r"^add\s+heading\s+(.+?)\s+to\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
        if doc_head_m:
            masked = f"doc_add_heading({doc_head_m.group(2)}, {doc_head_m.group(1).strip()}, 1)"

    doc_p_m = re.match(r"^add\s+paragraph\s+(.+?)\s+to\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_p_m:
        masked = f"doc_add_paragraph({doc_p_m.group(2)}, {doc_p_m.group(1).strip()})"

    doc_tbl_m = re.match(r"^add\s+table\s+with\s+headers\s+(.+?)\s+and\s+rows\s+(.+?)\s+to\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_tbl_m:
        masked = f"doc_add_table({doc_tbl_m.group(3)}, {doc_tbl_m.group(1).strip()}, {doc_tbl_m.group(2).strip()})"

    doc_list_m = re.match(r"^add\s+bullet\s+list\s+(.+?)\s+to\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_list_m:
        masked = f"doc_add_list({doc_list_m.group(2)}, {doc_list_m.group(1).strip()})"

    doc_save_m = re.match(r"^save\s+document\s+([A-Za-z_]\w*)\s+to\s+file\s+(.+)$", masked, re.IGNORECASE)
    if doc_save_m:
        masked = f"doc_save({doc_save_m.group(1)}, {doc_save_m.group(2).strip()})"

    doc_rndr_md_m = re.match(r"^render\s+document\s+([A-Za-z_]\w*)\s+as\s+markdown\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_rndr_md_m:
        masked = f"set {doc_rndr_md_m.group(2)} to doc_render_markdown({doc_rndr_md_m.group(1)})"

    doc_rndr_html_m = re.match(r"^render\s+document\s+([A-Za-z_]\w*)\s+as\s+html\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if doc_rndr_html_m:
        masked = f"set {doc_rndr_html_m.group(2)} to doc_render_html({doc_rndr_html_m.group(1)})"

    # Phase 19: English Cron & Event Scheduling
    sched_every_m = re.match(r"^schedule\s+every\s+(.+?)(?:\s+seconds?)?\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if sched_every_m:
        masked = f"schedule_every_seconds({sched_every_m.group(1).strip()}, {sched_every_m.group(2)})"

    sched_run_m = re.match(r"^run\s+scheduler\s+for\s+(.+?)(?:\s+seconds?)?$", masked, re.IGNORECASE)
    if sched_run_m:
        masked = f"run_scheduler_for({sched_run_m.group(1).strip()})"

    # Phase 20: Cryptography & Secrets
    hash_algo_m = re.match(r"^hash\s+text\s+(.+?)\s+with\s+algorithm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if hash_algo_m:
        masked = f"set {hash_algo_m.group(3)} to crypto_hash({hash_algo_m.group(1).strip()}, {hash_algo_m.group(2).strip()})"
    else:
        hash_m = re.match(r"^hash\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
        if hash_m:
            masked = f"set {hash_m.group(2)} to crypto_hash({hash_m.group(1).strip()})"

    token_m = re.match(r"^generate\s+secure\s+token\s+of\s+length\s+(\d+)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if token_m:
        masked = f"set {token_m.group(2)} to crypto_token({token_m.group(1)})"

    b64_enc_m = re.match(r"^encode\s+text\s+(.+?)\s+as\s+base64\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if b64_enc_m:
        masked = f"set {b64_enc_m.group(2)} to crypto_base64_encode({b64_enc_m.group(1).strip()})"

    b64_dec_m = re.match(r"^decode\s+base64\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if b64_dec_m:
        masked = f"set {b64_dec_m.group(2)} to crypto_base64_decode({b64_dec_m.group(1).strip()})"

    enc_m = re.match(r"^encrypt\s+text\s+(.+?)\s+with\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if enc_m:
        masked = f"set {enc_m.group(3)} to crypto_encrypt({enc_m.group(1).strip()}, {enc_m.group(2).strip()})"

    dec_m = re.match(r"^decrypt\s+text\s+(.+?)\s+with\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if dec_m:
        masked = f"set {dec_m.group(3)} to crypto_decrypt({dec_m.group(1).strip()}, {dec_m.group(2).strip()})"

    # Phase 21: Streaming Data & Pipeline Operators
    pipe_into_m = re.match(r"^pipe\s+(.+?)\s+into\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if pipe_into_m:
        p_expr = pipe_into_m.group(1).strip()
        p_funcs_str = pipe_into_m.group(2).strip()
        p_target = pipe_into_m.group(3).strip()
        p_funcs = [f.strip() for f in re.split(r"\s+then\s+", p_funcs_str, flags=re.IGNORECASE)]
        masked = f"set {p_target} to ds_pipe({p_expr}, {', '.join(p_funcs)})"
    else:
        pipe_expr_m = re.search(r"\bpipe\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\s+then\s+[A-Za-z_]\w*)+)", masked, re.IGNORECASE)
        if pipe_expr_m:
            p_expr = pipe_expr_m.group(1).strip()
            p_funcs = [f.strip() for f in re.split(r"\s+then\s+", pipe_expr_m.group(2).strip(), flags=re.IGNORECASE)]
            p_repl = f"ds_pipe({p_expr}, {', '.join(p_funcs)})"
            masked = masked[:pipe_expr_m.start()] + p_repl + masked[pipe_expr_m.end():]

    take_last_m = re.match(r"^\s*take\s+last\s+(.+?)\s+(?:items\s+)?from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if take_last_m:
        masked = f"set {take_last_m.group(3)} to ds_take_last({take_last_m.group(2).strip()}, {take_last_m.group(1).strip()})"

    drop_last_m = re.match(r"^\s*drop\s+last\s+(.+?)\s+(?:items\s+)?from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if drop_last_m:
        masked = f"set {drop_last_m.group(3)} to ds_drop_last({drop_last_m.group(2).strip()}, {drop_last_m.group(1).strip()})"

    take_m = re.match(r"^take\s+(?:first\s+)?(.+?)\s+(?:items\s+)?from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if take_m:
        masked = f"set {take_m.group(3)} to ds_take({take_m.group(2).strip()}, {take_m.group(1).strip()})"

    drop_m = re.match(r"^drop\s+(?:first\s+)?(.+?)\s+(?:items\s+)?from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if drop_m:
        masked = f"set {drop_m.group(3)} to ds_drop({drop_m.group(2).strip()}, {drop_m.group(1).strip()})"

    batch_m = re.match(r"^batch\s+(.+?)\s+by\s+(\d+)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if batch_m:
        masked = f"set {batch_m.group(3)} to batch_items({batch_m.group(1).strip()}, {batch_m.group(2)})"

    # Phase 22: Binary & Hex
    n2h_m = re.match(r"^convert\s+number\s+(.+?)\s+to\s+hex\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if n2h_m:
        masked = f"set {n2h_m.group(2)} to num_to_hex({n2h_m.group(1).strip()})"

    h2n_m = re.match(r"^convert\s+hex\s+(.+?)\s+to\s+number\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if h2n_m:
        masked = f"set {h2n_m.group(2)} to hex_to_num({h2n_m.group(1).strip()})"

    pack_m = re.match(r"^pack\s+numbers\s+(.+?)\s+as\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if pack_m:
        masked = f"set {pack_m.group(3)} to pack_numbers({pack_m.group(1).strip()}, {pack_m.group(2).strip()})"

    unpack_bin_m = re.match(r"^unpack\s+binary\s+(.+?)\s+from\s+(?:buffer\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if unpack_bin_m:
        masked = f"set {unpack_bin_m.group(3)} to unpack_numbers({unpack_bin_m.group(2).strip()}, {unpack_bin_m.group(1).strip()})"

    buf_len_m = re.match(r"^(?:size|length|count)\s+of\s+(?:buffer\s+)?(.+?)\s+in\s+bytes\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if buf_len_m:
        masked = f"set {buf_len_m.group(2)} to bytes_length({buf_len_m.group(1).strip()})"

    # Phase 23: Configuration Manager
    cfg_load_m = re.match(r"^load\s+config\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if cfg_load_m:
        masked = f"set {cfg_load_m.group(2)} to config_load({cfg_load_m.group(1).strip()})"

    cfg_get_def_m = re.match(r"^get\s+config\s+(.+?)\s+with\s+default\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if cfg_get_def_m:
        masked = f"set {cfg_get_def_m.group(4)} to config_get({cfg_get_def_m.group(3).strip()}, {cfg_get_def_m.group(1).strip()}, {cfg_get_def_m.group(2).strip()})"
    else:
        cfg_get_m = re.match(r"^get\s+config\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
        if cfg_get_m:
            masked = f"set {cfg_get_m.group(3)} to config_get({cfg_get_m.group(2).strip()}, {cfg_get_m.group(1).strip()})"

    cfg_set_m = re.match(r"^set\s+config\s+(.+?)\s+to\s+(.+?)\s+in\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if cfg_set_m:
        masked = f"config_set({cfg_set_m.group(3)}, {cfg_set_m.group(1).strip()}, {cfg_set_m.group(2).strip()})"

    cfg_save_m = re.match(r"^save\s+config\s+([A-Za-z_]\w*)\s+to\s+file\s+(.+)$", masked, re.IGNORECASE)
    if cfg_save_m:
        masked = f"config_save({cfg_save_m.group(1)}, {cfg_save_m.group(2).strip()})"

    # Phase 24: Benchmarking
    bench_m = re.match(r"^benchmark\s+(.+?)\s+with\s+(\d+)\s+iterations\s+for\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if bench_m:
        masked = f"set {bench_m.group(4)} to benchmark_block({bench_m.group(1).strip()}, {bench_m.group(2)}, {bench_m.group(3)})"

    # Universal Introspection Framework (explain, summary of, preview of)
    exp_dom_m = re.match(r"^explain\s+domain\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?$", masked, re.IGNORECASE)
    if exp_dom_m:
        d_name = exp_dom_m.group(1).lower()
        tgt = exp_dom_m.group(2)
        if tgt:
            masked = f'set {tgt} to explain_domain("{d_name}")'
        else:
            masked = f'say explain_domain("{d_name}")'

    exp_into_m = re.match(r"^explain\s+(?!domain\b)(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if exp_into_m:
        masked = f"set {exp_into_m.group(2)} to explain({exp_into_m.group(1).strip()})"
    elif re.match(r"^explain\s+(?!domain\b)(.+)$", masked, re.IGNORECASE):
        exp_bare_m = re.match(r"^explain\s+(?!domain\b)(.+)$", masked, re.IGNORECASE)
        masked = f"say explain({exp_bare_m.group(1).strip()})"

    prev_into_m = re.match(r"^preview\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if prev_into_m:
        masked = f"set {prev_into_m.group(2)} to preview_of({prev_into_m.group(1).strip()})"
    elif re.match(r"^preview\s+of\s+(.+)$", masked, re.IGNORECASE):
        prev_bare_m = re.match(r"^preview\s+of\s+(.+)$", masked, re.IGNORECASE)
        masked = f"say preview_of({prev_bare_m.group(1).strip()})"

    summ_into_m = re.match(r"^summary\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if summ_into_m:
        masked = f"set {summ_into_m.group(2)} to summary_of({summ_into_m.group(1).strip()})"
    elif re.match(r"^summary\s+of\s+(.+)$", masked, re.IGNORECASE):
        summ_bare_m = re.match(r"^summary\s+of\s+(.+)$", masked, re.IGNORECASE)
        masked = f"say summary_of({summ_bare_m.group(1).strip()})"

    # =======================================================================
    # PHASES 26 TO 100 PHRASE NORMALIZATIONS
    # =======================================================================

    # Cluster 1 (Phases 26-32: Systems, OS, Processes & Signals)
    p_cmd_shell_into = re.match(r"^(?:run\s+command|execute\s+shell)\s+(.+?)\s+using\s+shell\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if not p_cmd_shell_into:
        p_cmd_shell_into = re.match(r"^(?:run\s+command|execute\s+shell)\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s+using\s+shell$", masked, re.IGNORECASE)
    if p_cmd_shell_into:
        masked = f"{p_cmd_shell_into.group(2)} = run_command({p_cmd_shell_into.group(1).strip()}, shell=True)"

    p_cmd_piped_shell = re.match(r"^(?:run\s+command|execute\s+shell)\s+(.+?)\s+using\s+shell\s+(?:piped\s+into|capturing\s+into)\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if not p_cmd_piped_shell:
        p_cmd_piped_shell = re.match(r"^(?:run\s+command|execute\s+shell)\s+(.+?)\s+(?:piped\s+into|capturing\s+into)\s+([A-Za-z_]\w*)\s+using\s+shell$", masked, re.IGNORECASE)
    if p_cmd_piped_shell:
        masked = f"set {p_cmd_piped_shell.group(2)} to run_command_piped({p_cmd_piped_shell.group(1).strip()}, shell=True)"

    p_cmd_shell_bare = re.match(r"^(?:run\s+command|execute\s+shell)\s+(.+?)\s+using\s+shell$", masked, re.IGNORECASE)
    if p_cmd_shell_bare:
        masked = f"run_command({p_cmd_shell_bare.group(1).strip()}, shell=True)"

    p_cmd_m = re.match(r"^(?:run\s+command|execute\s+shell)\s+(.+?)\s+(?:piped\s+into|capturing\s+into)\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_cmd_m:
        masked = f"set {p_cmd_m.group(2)} to run_command_piped({p_cmd_m.group(1).strip()})"

    p_cmd_bare = re.match(r"^run\s+command\s+(.+?)$", masked, re.IGNORECASE)
    if p_cmd_bare and not re.search(r"\s+into\s+[A-Za-z_]\w*$", masked, re.IGNORECASE):
        masked = f"run_command({p_cmd_bare.group(1).strip()})"

    p_proc_m = re.match(r"^(?:check\s+if\s+)?process\s+(.+?)\s+is\s+running\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_proc_m:
        masked = f"set {p_proc_m.group(2)} to check_process_running({p_proc_m.group(1).strip()})"

    p_path_m = re.match(r"^(?:add\s+(?:path|directory)\s+(.+?)\s+to\s+system\s+path|extend\s+system\s+path\s+with\s+(.+?))$", masked, re.IGNORECASE)
    if p_path_m:
        p_dir = p_path_m.group(1) or p_path_m.group(2)
        masked = f"add_system_path({p_dir.strip()})"

    p_lock_m = re.match(r"^(?:acquire\s+file\s+lock|lock\s+file)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_lock_m:
        masked = f"set {p_lock_m.group(2)} to acquire_file_lock({p_lock_m.group(1).strip()})"

    p_unlock_m = re.match(r"^(?:release\s+file\s+lock|unlock\s+file)\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_unlock_m:
        masked = f"release_file_lock({p_unlock_m.group(1)})"

    p_disk_m = re.match(r"^(?:get\s+system\s+disk\s+space|check\s+disk\s+space)(?:\s+for\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_disk_m:
        path = p_disk_m.group(1) or '"."'
        masked = f"set {p_disk_m.group(2)} to system_disk_space({path})"

    # Cluster 2 (Phases 33-40: Network Protocols & Web)
    p_dns_m = re.match(r"^(?:resolve\s+dns\s+of|lookup\s+dns\s+for)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_dns_m:
        masked = f"set {p_dns_m.group(2)} to resolve_dns({p_dns_m.group(1).strip()})"

    p_ping_m = re.match(r"^(?:ping\s+host|check\s+connection\s+to)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_ping_m:
        masked = f"set {p_ping_m.group(2)} to ping_host({p_ping_m.group(1).strip()})"

    p_jar_m = re.match(r"^(?:create|new)\s+cookie\s+jar\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_jar_m:
        masked = f"set {p_jar_m.group(1)} to cookie_jar_create()"

    p_cset_m = re.match(r"^set\s+cookie\s+(.+?)\s+to\s+(.+?)\s+in\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_cset_m:
        masked = f"cookie_jar_set({p_cset_m.group(3)}, {p_cset_m.group(1).strip()}, {p_cset_m.group(2).strip()})"

    p_cget_def_m = re.match(r"^get\s+cookie\s+(.+?)\s+with\s+default\s+(.+?)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_cget_def_m:
        masked = f"set {p_cget_def_m.group(4)} to cookie_jar_get({p_cget_def_m.group(3)}, {p_cget_def_m.group(1).strip()}, {p_cget_def_m.group(2).strip()})"
    else:
        p_cget_m = re.match(r"^get\s+cookie\s+(.+?)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
        if p_cget_m:
            masked = f"set {p_cget_m.group(3)} to cookie_jar_get({p_cget_m.group(2)}, {p_cget_m.group(1).strip()})"

    # Cluster 3 (Phases 41-48: Data Engineering, Compression & Geolocation)
    p_gzip_m = re.match(r"^(?:compress\s+text\s+(.+?)\s+with\s+gzip|gzip\s+compress\s+(.+?))\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_gzip_m:
        txt = p_gzip_m.group(1) or p_gzip_m.group(2)
        masked = f"set {p_gzip_m.group(3)} to compress_gzip({txt.strip()})"

    p_gunzip_m = re.match(r"^(?:decompress\s+gzip|gzip\s+decompress)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_gunzip_m:
        masked = f"set {p_gunzip_m.group(2)} to decompress_gzip({p_gunzip_m.group(1).strip()})"

    p_bz2_m = re.match(r"^(?:compress\s+text\s+(.+?)\s+with\s+bz2|bz2\s+compress\s+(.+?))\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_bz2_m:
        txt = p_bz2_m.group(1) or p_bz2_m.group(2)
        masked = f"set {p_bz2_m.group(3)} to compress_bz2({txt.strip()})"

    p_bunzip_m = re.match(r"^(?:decompress\s+bz2|bz2\s+decompress)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_bunzip_m:
        masked = f"set {p_bunzip_m.group(2)} to decompress_bz2({p_bunzip_m.group(1).strip()})"

    p_zip_m = re.match(r"^create\s+zip\s+archive\s+(.+?)\s+from\s+files\s+(.+)$", masked, re.IGNORECASE)
    if p_zip_m:
        masked = f"create_zip_archive({p_zip_m.group(1).strip()}, {p_zip_m.group(2).strip()})"

    p_unzip_m = re.match(r"^(?:extract\s+zip\s+archive|unzip)\s+(.+?)\s+(?:into\s+folder|to)\s+(.+)$", masked, re.IGNORECASE)
    if p_unzip_m:
        masked = f"extract_zip_archive({p_unzip_m.group(1).strip()}, {p_unzip_m.group(2).strip()})"

    p_crc_m = re.match(r"^(?:calculate\s+crc32\s+of|crc32\s+checksum\s+of)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_crc_m:
        masked = f"set {p_crc_m.group(2)} to calculate_checksum_crc32({p_crc_m.group(1).strip()})"

    p_adler_m = re.match(r"^(?:calculate\s+adler32\s+of|adler32\s+checksum\s+of)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_adler_m:
        masked = f"set {p_adler_m.group(2)} to calculate_checksum_adler32({p_adler_m.group(1).strip()})"

    p_geo_m = re.match(r"^(?:calculate\s+geo\s+distance\s+between|distance\s+between\s+coordinates)\s+(.+?),\s*(.+?)\s+and\s+(.+?),\s*(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_geo_m:
        masked = f"set {p_geo_m.group(5)} to calculate_geo_distance({p_geo_m.group(1).strip()}, {p_geo_m.group(2).strip()}, {p_geo_m.group(3).strip()}, {p_geo_m.group(4).strip()})"

    # Cluster 4 (Phases 49-56: Mathematics, Linear Algebra, Statistics & Finance)
    p_dot_m = re.match(r"^(?:vector\s+(.+?)\s+dot\s+vector\s+(.+?)|dot\s+product\s+of\s+(.+?)\s+and\s+(.+?))\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_dot_m:
        v1 = p_dot_m.group(1) or p_dot_m.group(3)
        v2 = p_dot_m.group(2) or p_dot_m.group(4)
        masked = f"set {p_dot_m.group(5)} to vector_dot({v1.strip()}, {v2.strip()})"

    p_vmag_m = re.match(r"^(?:vector\s+magnitude\s+of|magnitude\s+of\s+vector|length\s+of\s+vector)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_vmag_m:
        masked = f"set {p_vmag_m.group(2)} to vector_magnitude({p_vmag_m.group(1).strip()})"

    p_matmul_m = re.match(r"^(?:matrix\s+(.+?)\s+multiply\s+matrix\s+(.+?)|multiply\s+matrix\s+(.+?)\s+by\s+(.+?))\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_matmul_m:
        m1 = p_matmul_m.group(1) or p_matmul_m.group(3)
        m2 = p_matmul_m.group(2) or p_matmul_m.group(4)
        masked = f"set {p_matmul_m.group(5)} to matrix_multiply({m1.strip()}, {m2.strip()})"

    p_stdev_m = re.match(r"^(?:standard\s+deviation|stdev)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_stdev_m:
        masked = f"set {p_stdev_m.group(2)} to stats_stdev({p_stdev_m.group(1).strip()})"

    p_var_m = re.match(r"^variance\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_var_m:
        masked = f"set {p_var_m.group(2)} to stats_variance({p_var_m.group(1).strip()})"

    p_med_m = re.match(r"^median\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_med_m:
        masked = f"set {p_med_m.group(2)} to stats_median({p_med_m.group(1).strip()})"

    p_comp_m = re.match(
        r"^compound\s+interest\s+on\s+(.+?)\s+at\s+(.+?)(?:%|\s*percent)?\s+for\s+(.+?)\s+years?(?:\s+compounded\s+(\w+))?\s+into\s+([A-Za-z_]\w*)$",
        masked,
        re.IGNORECASE
    )
    if p_comp_m:
        freq = f'"{p_comp_m.group(4).strip()}"' if p_comp_m.group(4) else "1"
        masked = f"set {p_comp_m.group(5)} to calc_compound_interest({p_comp_m.group(1).strip()}, {p_comp_m.group(2).strip()}, {p_comp_m.group(3).strip()}, {freq})"

    p_loan_m = re.match(r"^loan\s+payment\s+for\s+principal\s+(.+?)\s+rate\s+(.+?)(?:%|\s*percent)?\s+months\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_loan_m:
        masked = f"set {p_loan_m.group(4)} to calc_loan_payment({p_loan_m.group(1).strip()}, {p_loan_m.group(2).strip()}, {p_loan_m.group(3).strip()})"

    # Cluster 5 (Phases 57-64: Reactive EventBus, Priority Queues, Circuit Breaker)
    p_ebus_m = re.match(r"^create\s+event\s+bus\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_ebus_m:
        masked = f"set {p_ebus_m.group(1)} to EventBus()"

    p_pub_m = re.match(r"^publish\s+event\s+(.+?)\s+with\s+data\s+(.+)$", masked, re.IGNORECASE)
    if p_pub_m:
        masked = f"event_publish({p_pub_m.group(1).strip()}, {p_pub_m.group(2).strip()})"

    p_pq_m = re.match(r"^create\s+priority\s+queue\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_pq_m:
        masked = f"set {p_pq_m.group(1)} to priority_queue_create()"

    p_enq_m = re.match(r"^enqueue\s+(?:task|item)\s+(.+?)\s+with\s+priority\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_enq_m:
        masked = f"priority_queue_enqueue({p_enq_m.group(3)}, {p_enq_m.group(1).strip()}, {p_enq_m.group(2).strip()})"

    p_deq_m = re.match(r"^dequeue\s+(?:next\s+)?(?:task|item)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_deq_m:
        masked = f"set {p_deq_m.group(2)} to priority_queue_dequeue({p_deq_m.group(1)})"

    p_cb_m = re.match(r"^create\s+circuit\s+breaker\s+named\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_cb_m:
        masked = f"set {p_cb_m.group(2)} to CircuitBreaker({p_cb_m.group(1).strip()})"

    p_cb_call_m = re.match(r"^call\s+circuit\s+breaker\s+([A-Za-z_]\w*)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_cb_call_m:
        masked = f"set {p_cb_call_m.group(3)} to circuit_breaker_call({p_cb_call_m.group(1)}, {p_cb_call_m.group(2).strip()})"

    # Cluster 6 (Phases 65-72: Modern Web, UI & Components, SVG Canvas)
    p_svg_m = re.match(r"^create\s+svg\s+canvas\s+width\s+(.+?)\s+height\s+(.+?)\s+with\s+elements\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_svg_m:
        masked = f"set {p_svg_m.group(4)} to generate_svg_canvas({p_svg_m.group(1).strip()}, {p_svg_m.group(2).strip()}, {p_svg_m.group(3).strip()})"

    p_svg_c_m = re.match(r"^create\s+svg\s+circle\s+at\s+(.+?),\s*(.+?)\s+radius\s+(.+?)\s+fill\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_svg_c_m:
        masked = f"set {p_svg_c_m.group(5)} to generate_svg_circle({p_svg_c_m.group(1).strip()}, {p_svg_c_m.group(2).strip()}, {p_svg_c_m.group(3).strip()}, {p_svg_c_m.group(4).strip()})"

    p_svg_r_m = re.match(r"^create\s+svg\s+rect\s+at\s+(.+?),\s*(.+?)\s+width\s+(.+?)\s+height\s+(.+?)\s+fill\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_svg_r_m:
        masked = f"set {p_svg_r_m.group(6)} to generate_svg_rect({p_svg_r_m.group(1).strip()}, {p_svg_r_m.group(2).strip()}, {p_svg_r_m.group(3).strip()}, {p_svg_r_m.group(4).strip()}, {p_svg_r_m.group(5).strip()})"

    p_diff_m = re.match(r"^diff\s+records\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_diff_m:
        masked = f"set {p_diff_m.group(3)} to diff_records({p_diff_m.group(1).strip()}, {p_diff_m.group(2).strip()})"

    # Cluster 7 (Phases 73-80: AI Agents, RAG & Cognitive Loops)
    p_idx_m = re.match(r"^create\s+knowledge\s+index\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_idx_m:
        masked = f"set {p_idx_m.group(1)} to knowledge_index_create()"

    p_doc_idx_m = re.match(r"^(?:index|add)\s+document\s+(.+?)\s+(?:with\s+)?text\s+(.+?)\s+(?:into|to)\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_doc_idx_m:
        masked = f"knowledge_index_add({p_doc_idx_m.group(3)}, {p_doc_idx_m.group(1).strip()}, {p_doc_idx_m.group(2).strip()})"

    p_q_idx_m = re.match(r"^search\s+(?:knowledge\s+index\s+)?([A-Za-z_]\w*)\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_q_idx_m:
        masked = f"set {p_q_idx_m.group(3)} to knowledge_index_query({p_q_idx_m.group(1)}, {p_q_idx_m.group(2).strip()})"

    p_cos_m = re.match(r"^cosine\s+similarity\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_cos_m:
        masked = f"set {p_cos_m.group(3)} to cosine_similarity({p_cos_m.group(1).strip()}, {p_cos_m.group(2).strip()})"

    p_mem_m = re.match(r"^create\s+conversation\s+memory\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_mem_m:
        masked = f"set {p_mem_m.group(1)} to memory_create()"

    p_rem_m = re.match(r"^remember\s+in\s+memory\s+([A-Za-z_]\w*)\s+role\s+(.+?)\s+content\s+(.+)$", masked, re.IGNORECASE)
    if p_rem_m:
        masked = f"memory_remember({p_rem_m.group(1)}, {p_rem_m.group(2).strip()}, {p_rem_m.group(3).strip()})"

    p_rec_m = re.match(r"^(?:get\s+recall\s+history|recall\s+all)\s+from\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_rec_m:
        masked = f"set {p_rec_m.group(2)} to memory_recall({p_rec_m.group(1)})"

    # Cluster 8 (Phases 81-88: Security, Identity, Auth & Compliance)
    p_jwt_c_m = re.match(r"^create\s+jwt\s+with\s+payload\s+(.+?)\s+and\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_jwt_c_m:
        masked = f"set {p_jwt_c_m.group(3)} to jwt_create({p_jwt_c_m.group(1).strip()}, {p_jwt_c_m.group(2).strip()})"

    p_jwt_v_m = re.match(r"^verify\s+jwt\s+(.+?)\s+with\s+secret\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_jwt_v_m:
        masked = f"set {p_jwt_v_m.group(3)} to jwt_verify({p_jwt_v_m.group(1).strip()}, {p_jwt_v_m.group(2).strip()})"

    p_pwd_h_m = re.match(r"^secure\s+hash\s+password\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_pwd_h_m:
        masked = f"set {p_pwd_h_m.group(2)} to hash_password_secure({p_pwd_h_m.group(1).strip()})"

    p_pwd_v_m = re.match(r"^verify\s+password\s+(.+?)\s+matches\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_pwd_v_m:
        masked = f"set {p_pwd_v_m.group(3)} to verify_password_secure({p_pwd_v_m.group(1).strip()}, {p_pwd_v_m.group(2).strip()})"

    p_pii_m = re.match(r"^mask\s+pii\s+in\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_pii_m:
        masked = f"set {p_pii_m.group(2)} to mask_pii_text({p_pii_m.group(1).strip()})"

    # Cluster 9 (Phases 89-95: Cloud, Containers & Metrics)
    p_dock_m = re.match(r"^generate\s+dockerfile\s+for\s+entrypoint\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_dock_m:
        masked = f"set {p_dock_m.group(2)} to generate_dockerfile_content({p_dock_m.group(1).strip()})"

    p_met_inc_m = re.match(r"^(?:increment|increase)\s+metric\s+(.+)$", masked, re.IGNORECASE)
    if p_met_inc_m:
        masked = f"metric_increment({p_met_inc_m.group(1).strip()})"

    p_met_set_m = re.match(r"^set\s+metric\s+(.+?)\s+to\s+(.+)$", masked, re.IGNORECASE)
    if p_met_set_m:
        masked = f"metric_set({p_met_set_m.group(1).strip()}, {p_met_set_m.group(2).strip()})"

    p_met_exp_m = re.match(r"^export\s+prometheus\s+metrics\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_met_exp_m:
        masked = f"set {p_met_exp_m.group(1)} to metrics_export_prometheus()"

    # Cluster 10 (Phases 96-100: Metaprogramming, FFI & Self-Hosting)
    p_c_m = re.match(r"^call\s+c\s+library\s+(.+?)\s+function\s+(.+?)\s+with\s+args\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_c_m:
        masked = f"set {p_c_m.group(4)} to call_c_function({p_c_m.group(1).strip()}, {p_c_m.group(2).strip()}, {p_c_m.group(3).strip()})"

    p_mini_m = re.match(r"^minify\s+doomscript\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if p_mini_m:
        masked = f"set {p_mini_m.group(2)} to minify_doomscript_source({p_mini_m.group(1).strip()})"


    # -----------------------------------------------------------------------
    # 100 Thought-to-Code Paradigms (Clusters 1 - 10)
    # -----------------------------------------------------------------------
    # Paradigm 8: Reciprocal Swapping ('swap a and b')
    swap_m = re.match(r"^\s*swap\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s*$", masked, re.IGNORECASE)
    if swap_m:
        masked = f"{swap_m.group(1)}, {swap_m.group(2)} = {swap_m.group(2)}, {swap_m.group(1)}"

    # Paradigm 10, 46, 47: Epistemic & Contractual Assertions
    surely_m = re.match(r"^\s*surely\s+(.+)$", masked, re.IGNORECASE)
    if surely_m:
        masked = f'verify that {surely_m.group(1)} otherwise "Invariant violated: surely {surely_m.group(1)}"'

    pres_m = re.match(r"^\s*presumably\s+(.+)$", masked, re.IGNORECASE)
    if pres_m:
        masked = f'verify that {pres_m.group(1)} otherwise "Presumption failed: presumably {pres_m.group(1)}"'

    req_m = re.match(r"^\s*requires\s+(.+)$", masked, re.IGNORECASE)
    if req_m:
        masked = f'verify that {req_m.group(1)} otherwise "Precondition failed: requires {req_m.group(1)}"'

    ens_m = re.match(r"^\s*ensures\s+(.+)$", masked, re.IGNORECASE)
    if ens_m:
        masked = f'verify that {ens_m.group(1)} otherwise "Postcondition failed: ensures {ens_m.group(1)}"'

    inv_m = re.match(r"^\s*invariant\s+(.+)$", masked, re.IGNORECASE)
    if inv_m:
        masked = f'verify that {inv_m.group(1)} otherwise "Invariant violated: {inv_m.group(1)}"'

    # Paradigm 99: Purpose Docstring Statements
    masked = re.sub(r"^\s*purpose:\s*(.+)$", r"# purpose: \1", masked, flags=re.IGNORECASE)

    # Paradigm 18: Set-Theoretic Algebra
    masked = re.sub(
        r"^\s*union\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"set \3 to ds_union(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*intersection\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"set \3 to ds_intersection(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*difference\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$",
        r"set \3 to ds_difference(\1, \2)",
        masked,
        flags=re.IGNORECASE
    )
    # Inline set operations
    masked = re.sub(r"\bunion\s+of\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\b", r"ds_union(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bintersection\s+of\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\b", r"ds_intersection(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bdifference\s+between\s+([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\b", r"ds_difference(\1, \2)", masked, flags=re.IGNORECASE)

    # Paradigm 20: Semantic Multi-Bucket Grouping
    masked = re.sub(
        r"^\s*(?:group|bucket)\s+(.+?)\s+by\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)\s*$",
        r'set \3 to ds_group_by(\1, "\2")',
        masked,
        flags=re.IGNORECASE
    )

    # Paradigm 66: Boundary Clamping Directives
    clamp_m = re.match(r"^\s*clamp\s+([A-Za-z_]\w*)\s+between\s+(.+?)\s+and\s+(.+?)\s*$", masked, re.IGNORECASE)
    if clamp_m:
        masked = f"set {clamp_m.group(1)} to ds_clamp({clamp_m.group(1)}, {clamp_m.group(2)}, {clamp_m.group(3)})"

    # Paradigm 62: Hierarchical Family Traversal
    masked = re.sub(r"\b(?:all\s+)?children\s+of\s+([A-Za-z_]\w*)\b", r"ds_get_children(\1)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bparent\s+of\s+([A-Za-z_]\w*)\b", r"ds_get_parent(\1)", masked, flags=re.IGNORECASE)

    # Paradigm 53: Approximate Natural Quantifiers
    masked = re.sub(
        r"^\s*if\s+most\s+of\s+(.+?)\s+are\s+([A-Za-z_]\w*)\s*:",
        r'if ds_most(\1, lambda _x: bool(ds_attr(_x, "\2", _x))):',
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*if\s+almost\s+all\s+(?:of\s+)?(.+?)\s+are\s+([A-Za-z_]\w*)\s*:",
        r'if ds_almost_all(\1, lambda _x: bool(ds_attr(_x, "\2", _x))):',
        masked,
        flags=re.IGNORECASE
    )
    masked = re.sub(
        r"^\s*if\s+few\s+(?:of\s+)?(.+?)\s+are\s+([A-Za-z_]\w*)\s*:",
        r'if ds_few(\1, lambda _x: bool(ds_attr(_x, "\2", _x))):',
        masked,
        flags=re.IGNORECASE
    )

    # Paradigm 72: Event-Driven State Transitions
    trans_from_m = re.match(r"^\s*transition\s+([A-Za-z_]\w*)\s+from\s+(.+?)\s+to\s+(.+?)\s*$", masked, re.IGNORECASE)
    if trans_from_m:
        masked = f"ds_transition({trans_from_m.group(1)}, {trans_from_m.group(3)}, {trans_from_m.group(2)})"
    else:
        trans_to_m = re.match(r"^\s*transition\s+([A-Za-z_]\w*)\s+to\s+(.+?)\s*$", masked, re.IGNORECASE)
        if trans_to_m:
            masked = f"ds_transition({trans_to_m.group(1)}, {trans_to_m.group(2)})"

    # Paradigm 33: Synchronous Polling Guards
    wait_until_m = re.match(
        r"^\s*wait\s+until\s+(.+?)\s+with\s+timeout\s+of\s+(\d+(?:\.\d+)?)\s*(?:seconds?)?\s*$",
        masked,
        re.IGNORECASE
    )
    if wait_until_m:
        masked = f"ds_wait_until(lambda: {wait_until_m.group(1).strip()}, timeout={wait_until_m.group(2).strip()})"
    elif re.match(r"^\s*wait\s+until\s+(.+?)\s*$", masked, re.IGNORECASE):
        wait_m = re.match(r"^\s*wait\s+until\s+(.+?)\s*$", masked, re.IGNORECASE)
        masked = f"ds_wait_until(lambda: {wait_m.group(1).strip()})"



    # Paradigm 86: Safe Navigation Chains
    safe_acc_m = re.match(
        r"^\s*safely\s+access\s+(.+?)\s+otherwise\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*$",
        masked,
        re.IGNORECASE
    )
    if safe_acc_m:
        masked = f"set {safe_acc_m.group(3)} to ds_safe_access(lambda: {safe_acc_m.group(1).strip()}, {safe_acc_m.group(2).strip()})"

    say_safe_m = re.match(
        r"^\s*say\s+safely\s+access\s+(.+?)\s+otherwise\s+(.+?)\s*$",
        masked,
        re.IGNORECASE
    )
    if say_safe_m:
        masked = f"say ds_safe_access(lambda: {say_safe_m.group(1).strip()}, {say_safe_m.group(2).strip()})"

    # Restore strings
    normalized = unmask_strings(masked, strings)

    # Check for assignments to update scope tracker
    assigned = extract_assigned_var(normalized)
    if assigned:
        scope.record_assignment(assigned)

    return normalized


# ---------------------------------------------------------------------------
# MAIN NORMALIZATION FUNCTION
# ---------------------------------------------------------------------------

def normalize_with_map(source: str) -> Tuple[str, Dict[int, int]]:
    """
    Preprocesses DoomScript source into canonical DoomScript.
    Returns (normalized_source, line_map) where line_map maps 1-based line numbers
    in normalized_source to 1-based line numbers in the original source.
    """
    lines = source.splitlines()
    output_lines: List[str] = []
    line_map: Dict[int, int] = {}

    def emit(text: str, orig_line: int):
        output_lines.append(text)
        line_map[len(output_lines)] = orig_line

    scope = ScopeTracker()
    pending_injections: List[Tuple[int, List[str], int]] = []
    pending_routes: List[Tuple[int, str, int]] = []
    pending_entity_methods: List[Tuple[int, str, int]] = []
    match_stack: List[Dict[str, Any]] = []
    plot_stack: List[Dict[str, Any]] = []
    domain_block_stack: List[Dict[str, Any]] = []
    scoped_domain_stack: List[Tuple[int, str]] = []
    suppose_stack: List[Tuple[int, str, str]] = []
    discourse_stack: List[Dict[str, Any]] = []
    in_research_mode: bool = False

    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    reg.reset_active()

    def _close_domain_block(b_info, at_line_idx):
        ir_spec, target_var = b_info["domain"].parser.parse_block(b_info["header"], b_info["lines"], b_info["indent"])
        spec_id = reg.store_spec(ir_spec)
        d_name = b_info["domain"].name
        emit(f"{b_info['parent_indent']}set {target_var} to execute_{d_name}_ir('{spec_id}')", b_info["header_line"])

    expanded_lines: List[Tuple[int, str]] = []
    for line_idx, raw_line in enumerate(lines, start=1):
        cur_raw = raw_line
        cur_indent_len = len(cur_raw) - len(cur_raw.lstrip(" "))
        cur_indent = " " * cur_indent_len
        split_any = False
        while True:
            stripped = cur_raw.strip()
            code_no_comment, comment = split_comment(stripped)
            if not code_no_comment:
                break
            masked_inline, inline_strings = mask_strings(code_no_comment)
            # Postfix conditionals: <stmt> unless <cond>  /  <stmt> only if <cond>
            if not masked_inline.endswith(":") and not masked_inline.lower().startswith(("if ", "unless ", "while ", "repeat ", "for ", "class ", "def ", "to ", "return ", "yield ")):
                m_unl = re.match(r"^(.+?)\s+unless\s+([^\s].*)$", masked_inline, re.IGNORECASE)
                if m_unl:
                    stmt_sub = m_unl.group(1).strip()
                    cond_sub = m_unl.group(2).strip()
                    masked_inline = f"unless {cond_sub}: {stmt_sub}"
                    code_no_comment = unmask_strings(masked_inline, inline_strings)
                    masked_inline, inline_strings = mask_strings(code_no_comment)
                else:
                    m_oif = re.match(r"^(.+?)\s+only\s+if\s+([^\s].*)$", masked_inline, re.IGNORECASE)
                    if m_oif:
                        stmt_sub = m_oif.group(1).strip()
                        cond_sub = m_oif.group(2).strip()
                        masked_inline = f"if {cond_sub}: {stmt_sub}"
                        code_no_comment = unmask_strings(masked_inline, inline_strings)
                        masked_inline, inline_strings = mask_strings(code_no_comment)

            inline_m = re.match(
                r"^(if\s+.+?|unless\s+.+?|while\s+.+?|until\s+.+?|repeat\s+.+?\s+times|for\s+(?:each\s+)?[A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*\s+in\s+[^:]+)\s*:\s*([^\s#].+)$",
                masked_inline,
                re.IGNORECASE
            )
            if not inline_m:
                break
            split_any = True
            hdr = unmask_strings(inline_m.group(1).strip() + ":", inline_strings)
            body = unmask_strings(inline_m.group(2).strip(), inline_strings)
            expanded_lines.append((line_idx, f"{cur_indent}{hdr}"))
            cur_indent += "    "
            cur_raw = f"{cur_indent}{body}"
            if comment and not re.search(r"#(?!.*['\"])", cur_raw):
                cur_raw += f" {comment}"
        if split_any:
            expanded_lines.append((line_idx, cur_raw))
        else:
            expanded_lines.append((line_idx, raw_line))

    for line_idx, raw_line in expanded_lines:
        if not raw_line.strip():
            if domain_block_stack:
                domain_block_stack[-1]["lines"].append((line_idx, raw_line))
                continue
            emit("", line_idx)
            continue

        # Extract leading indentation
        indent_len = len(raw_line) - len(raw_line.lstrip(" "))
        indent = " " * indent_len
        if indent_len == 0:
            scope.in_class = False
        scope.update_indent(indent_len)
        stripped = raw_line.strip()
        if (stripped.startswith(("class ", "define a ", "define an ")) or (stripped.startswith(("a ", "an ")) and "begins with" in stripped)) and stripped.endswith(":"):
            scope.in_class = True

        # Pop domain_block_stack if indentation returned to parent level
        while domain_block_stack and indent_len <= domain_block_stack[-1]["indent"]:
            _close_domain_block(domain_block_stack.pop(), line_idx)

        # Pop scoped_domain_stack if indentation returned to parent level
        while scoped_domain_stack and indent_len <= scoped_domain_stack[-1][0]:
            _, d_to_pop = scoped_domain_stack.pop()
            reg.deactivate(d_to_pop)

        # Pop suppose_stack if indentation returned to parent level
        while suppose_stack and indent_len <= suppose_stack[-1][0]:
            _, s_var, p_ind = suppose_stack.pop()
            emit(f"{p_ind}set {s_var} to _suppose_saved_{s_var}", line_idx)

        # If inside active domain block, buffer line and continue
        if domain_block_stack:
            domain_block_stack[-1]["lines"].append((line_idx, raw_line))
            continue

        # Pop plot_stack if indentation returned to parent level
        while plot_stack and indent_len <= plot_stack[-1]["indent"]:
            p_info = plot_stack.pop()
            if p_info.get("deferred_draw"):
                emit(f"{p_info['parent_indent']}{p_info['var']}.draw('{p_info['deferred_draw']}')", line_idx)

        # Pop match_stack if indentation returned to parent level
        while match_stack and indent_len <= match_stack[-1]["match_indent"]:
            match_stack.pop()

        # Pop discourse_stack if indentation returned to parent level
        while discourse_stack and indent_len <= discourse_stack[-1]["indent"]:
            discourse_stack.pop()

        # Check pending deferred routes if indentation returned to parent level
        while pending_routes and indent_len <= pending_routes[-1][0]:
            _, r_stmt, r_line = pending_routes.pop()
            emit(r_stmt, r_line)

        # Check pending entity methods if indentation returned to parent level
        while pending_entity_methods and indent_len <= pending_entity_methods[-1][0]:
            _, em_stmt, em_line = pending_entity_methods.pop()
            emit(em_stmt, em_line)

        # Check pending injections from a function header
        if pending_injections and raw_line.strip():
            top_indent, assertions, top_line = pending_injections[-1]
            if indent_len > top_indent:
                for inj in assertions:
                    emit(f"{indent}{inj}", top_line)
                pending_injections.pop()

        # Split comment
        code, comment = split_comment(raw_line.strip())
        if not code:
            # Comment-only line
            emit(raw_line, line_idx)
            continue

        code = canonicalize_synonyms(code)

        # Phase 22: Discourse-Flow Architecture (Topic-Comment Intent Pipelining)
        if discourse_stack and indent_len > discourse_stack[-1]["indent"]:
            curr = discourse_stack[-1]["target"]
            p_ind = discourse_stack[-1]["parent_indent"]
            scope.record_assignment(curr)

            m_keep = re.match(r"^(?:keep\s+only\s+|keep\s+)(?:items\s+)?where\s+(.+)$", code.strip(), re.IGNORECASE)
            if m_keep:
                cond = m_keep.group(1).strip()
                var_name = "x" if re.search(r"\bx\b", cond) else "item"
                cond_expr = f"ds_attr({var_name}, '{cond}')" if re.match(r"^[A-Za-z_]\w*$", cond) else cond
                norm_step = normalize_statement_text(f"set {curr} to [{var_name} for {var_name} in {curr} if {cond_expr}]", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            m_disc = re.match(r"^(?:discard|exclude|filter\s+out)(?:\s+items)?\s+where\s+(.+)$", code.strip(), re.IGNORECASE)
            if m_disc:
                cond = m_disc.group(1).strip()
                var_name = "x" if re.search(r"\bx\b", cond) else "item"
                cond_expr = f"ds_attr({var_name}, '{cond}')" if re.match(r"^[A-Za-z_]\w*$", cond) else cond
                norm_step = normalize_statement_text(f"set {curr} to [{var_name} for {var_name} in {curr} if not ({cond_expr})]", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            m_sort_plain = re.match(r"^sort(?:\s+(descending|ascending))?$", code.strip(), re.IGNORECASE)
            if m_sort_plain:
                order = m_sort_plain.group(1).strip() if m_sort_plain.group(1) else "ascending"
                rev = "True" if order.lower() == "descending" else "False"
                norm_step = normalize_statement_text(f"set {curr} to sorted({curr}, reverse={rev})", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            m_sort = re.match(r"^sort\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending))?$", code.strip(), re.IGNORECASE)
            if m_sort:
                field = m_sort.group(1).strip()
                order = m_sort.group(2).strip() if m_sort.group(2) else "ascending"
                if field.lower() in ("item", "val", "value", "it", "self"):
                    rev = "True" if order.lower() == "descending" else "False"
                    norm_step = normalize_statement_text(f"set {curr} to sorted({curr}, reverse={rev})", scope, line_idx)
                else:
                    norm_step = normalize_statement_text(f"sort {curr} by {field} {order} into {curr}", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            m_take = re.match(r"^(?:take\s+)?(?:first\s+|top\s+)?(\d+|[A-Za-z_]\w*)(?:\s+items)?$", code.strip(), re.IGNORECASE)
            if m_take and (code.strip().lower().startswith(("take ", "first ", "top ")) or code.strip().isdigit()):
                n = m_take.group(1).strip()
                norm_step = normalize_statement_text(f"set {curr} to ds_take({curr}, {n})", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            m_take_last = re.match(r"^(?:take\s+)?last\s+(\d+|[A-Za-z_]\w*)(?:\s+items)?$", code.strip(), re.IGNORECASE)
            if m_take_last:
                n = m_take_last.group(1).strip()
                norm_step = normalize_statement_text(f"set {curr} to ds_take_last({curr}, {n})", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            m_drop = re.match(r"^drop\s+(?:first\s+)?(\d+|[A-Za-z_]\w*)(?:\s+items)?$", code.strip(), re.IGNORECASE)
            if m_drop:
                n = m_drop.group(1).strip()
                norm_step = normalize_statement_text(f"set {curr} to ds_drop({curr}, {n})", scope, line_idx)
                emit(f"{p_ind}{norm_step}", line_idx)
                continue

            if re.match(r"^for\s+each\s*:?$", code.strip(), re.IGNORECASE):
                emit(f"{p_ind}for each item in {curr}:", line_idx)
                continue

            rel_indent_len = indent_len - discourse_stack[-1]["indent"]
            adjusted_indent = p_ind + (" " * (rel_indent_len - 4)) if rel_indent_len >= 4 else p_ind
            norm_stmt = normalize_statement_text(code, scope, line_idx)
            emit(f"{adjusted_indent}{norm_stmt}", line_idx)
            continue

        take_block_m = re.match(r"^(?:take|focus\s+on)\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?\s*:$", code.strip(), re.IGNORECASE)
        if take_block_m:
            source_expr = take_block_m.group(1).strip()
            target_var = take_block_m.group(2).strip() if take_block_m.group(2) else (source_expr if re.match(r"^[A-Za-z_]\w*$", source_expr) else "_topic")
            if target_var != source_expr:
                norm_init = normalize_statement_text(f"set {target_var} to {source_expr}", scope, line_idx)
                emit(f"{indent}{norm_init}", line_idx)
            discourse_stack.append({
                "indent": indent_len,
                "target": target_var,
                "parent_indent": indent
            })
            scope.record_assignment(target_var)
            continue

        inline_discourse_m = re.match(
            r"^(?:take|focus\s+on)\s+(.+?)(?:\s+then\s+|,\s*then\s+|,\s*|\s+)(keep\b|discard\b|filter\s+out\b|sort\s+by\b|take\s+first\b|take\s+top\b|take\s+last\b|drop\b)(.+)$",
            code.strip(),
            re.IGNORECASE
        )
        if inline_discourse_m and not code.strip().endswith(":"):
            source_expr = inline_discourse_m.group(1).strip()
            first_verb = inline_discourse_m.group(2).strip()
            rest = inline_discourse_m.group(3).strip()
            full_chain = first_verb + " " + rest

            into_m = re.search(r"\s+into\s+([A-Za-z_]\w*)\s*$", full_chain, re.IGNORECASE)
            if into_m:
                target_var = into_m.group(1).strip()
                chain_body = full_chain[:into_m.start()].strip()
            else:
                target_var = source_expr if re.match(r"^[A-Za-z_]\w*$", source_expr) else "_result"
                chain_body = full_chain

            steps = re.split(
                r"(?:\s+then\s+|,\s*then\s+|,\s*(?=(?:keep|discard|filter|sort|take|drop)\b))",
                chain_body,
                flags=re.IGNORECASE
            )

            norm_init = normalize_statement_text(f"set {target_var} to {source_expr}", scope, line_idx)
            emit(f"{indent}{norm_init}", line_idx)
            scope.record_assignment(target_var)

            for step in steps:
                step = step.strip()
                if not step:
                    continue
                m_k = re.match(r"^(?:keep\s+only\s+|keep\s+)(?:items\s+)?where\s+(.+)$", step, re.IGNORECASE)
                if m_k:
                    cond = m_k.group(1).strip()
                    var_name = "x" if re.search(r"\bx\b", cond) else "item"
                    cond_expr = f"ds_attr({var_name}, '{cond}')" if re.match(r"^[A-Za-z_]\w*$", cond) else cond
                    norm_s = normalize_statement_text(f"set {target_var} to [{var_name} for {var_name} in {target_var} if {cond_expr}]", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue

                m_d = re.match(r"^(?:discard|exclude|filter\s+out)(?:\s+items)?\s+where\s+(.+)$", step, re.IGNORECASE)
                if m_d:
                    cond = m_d.group(1).strip()
                    var_name = "x" if re.search(r"\bx\b", cond) else "item"
                    cond_expr = f"ds_attr({var_name}, '{cond}')" if re.match(r"^[A-Za-z_]\w*$", cond) else cond
                    norm_s = normalize_statement_text(f"set {target_var} to [{var_name} for {var_name} in {target_var} if not ({cond_expr})]", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue

                m_s_plain = re.match(r"^sort(?:\s+(descending|ascending))?$", step, re.IGNORECASE)
                if m_s_plain:
                    order = m_s_plain.group(1).strip() if m_s_plain.group(1) else "ascending"
                    rev = "True" if order.lower() == "descending" else "False"
                    norm_s = normalize_statement_text(f"set {target_var} to sorted({target_var}, reverse={rev})", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue

                m_s = re.match(r"^sort\s+by\s+([A-Za-z_]\w*)(?:\s+(descending|ascending))?$", step, re.IGNORECASE)
                if m_s:
                    field = m_s.group(1).strip()
                    order = m_s.group(2).strip() if m_s.group(2) else "ascending"
                    if field.lower() in ("item", "val", "value", "it", "self"):
                        rev = "True" if order.lower() == "descending" else "False"
                        norm_s = normalize_statement_text(f"set {target_var} to sorted({target_var}, reverse={rev})", scope, line_idx)
                    else:
                        norm_s = normalize_statement_text(f"sort {target_var} by {field} {order} into {target_var}", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue

                m_t = re.match(r"^(?:take\s+)?(?:first\s+|top\s+)?(\d+|[A-Za-z_]\w*)(?:\s+items)?$", step, re.IGNORECASE)
                if m_t and (step.lower().startswith(("take ", "first ", "top ")) or step.isdigit()):
                    n = m_t.group(1).strip()
                    norm_s = normalize_statement_text(f"set {target_var} to ds_take({target_var}, {n})", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue

                m_tl = re.match(r"^(?:take\s+)?last\s+(\d+|[A-Za-z_]\w*)(?:\s+items)?$", step, re.IGNORECASE)
                if m_tl:
                    n = m_tl.group(1).strip()
                    norm_s = normalize_statement_text(f"set {target_var} to ds_take_last({target_var}, {n})", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue

                m_dr = re.match(r"^drop\s+(?:first\s+)?(\d+|[A-Za-z_]\w*)(?:\s+items)?$", step, re.IGNORECASE)
                if m_dr:
                    n = m_dr.group(1).strip()
                    norm_s = normalize_statement_text(f"set {target_var} to ds_drop({target_var}, {n})", scope, line_idx)
                    emit(f"{indent}{norm_s}", line_idx)
                    continue
            continue

        # Milestone 5 & 6: Pre-split compositional blocks
        # Transfer: transfer <amt> from <src> to <dst>
        transfer_m = re.match(r"^transfer\s+(.+?)\s+from\s+([A-Za-z_]\w*)\s+to\s+([A-Za-z_]\w*)$", code.strip(), re.IGNORECASE)
        if transfer_m:
            amt, src, dst = transfer_m.group(1).strip(), transfer_m.group(2).strip(), transfer_m.group(3).strip()
            code = f"decrease {src} by {amt} and then increase {dst} by {amt}"

        # Safely do: <action> otherwise <fallback>
        safely_m = re.match(r"^safely\s+(?:do\s*)?:\s*(.+?)\s+otherwise\s+(.+)$", code.strip(), re.IGNORECASE)
        if safely_m:
            main_act = safely_m.group(1).strip()
            fallback = safely_m.group(2).strip()
            emit(f"{indent}try:", line_idx)
            norm_main = normalize_statement_text(main_act, scope, line_idx)
            emit(f"{indent}    {norm_main}", line_idx)
            emit(f"{indent}if it fails:", line_idx)
            into_m = re.search(r"\binto\s+([A-Za-z_]\w*)", main_act, re.IGNORECASE)
            is_stmt = re.match(r"^(?:say|show|print|display|set|let|put|write|read|raise|return|pause|stop)\b", fallback, re.IGNORECASE)
            if into_m and not is_stmt:
                target_var = into_m.group(1).strip()
                emit(f"{indent}    set {target_var} to {fallback}", line_idx)
            else:
                norm_fallback = normalize_statement_text(fallback, scope, line_idx)
                emit(f"{indent}    {norm_fallback}", line_idx)
            continue

        # Retry N times: <action>
        retry_m = re.match(r"^retry\s+(\d+)\s+times?\s*:\s*(.+)$", code.strip(), re.IGNORECASE)
        if retry_m:
            times = retry_m.group(1).strip()
            act = retry_m.group(2).strip()
            norm_act = normalize_statement_text(act, scope, line_idx)
            emit(f"{indent}for each _retry_iter from 1 to {times}:", line_idx)
            emit(f"{indent}    try:", line_idx)
            emit(f"{indent}        {norm_act}", line_idx)
            emit(f"{indent}        stop", line_idx)
            emit(f"{indent}    if it fails:", line_idx)
            emit(f"{indent}        skip", line_idx)
            continue

        # In N seconds: <action>
        temporal_m = re.match(r"^in\s+(\d+(?:\.\d+)?)\s+(seconds?|secs?|minutes?|mins?|hours?)\s*:\s*(.+)$", code.strip(), re.IGNORECASE)
        if temporal_m:
            delay = temporal_m.group(1).strip()
            unit = temporal_m.group(2).strip()
            act = temporal_m.group(3).strip()
            emit(f"{indent}wait {delay} {unit}", line_idx)
            norm_act = normalize_statement_text(act, scope, line_idx)
            emit(f"{indent}{norm_act}", line_idx)
            continue

                # Python module interop: use python module X [as Y], from python module X use Y
        py_mod_m = re.match(
            r"^\b(?:use|import)\s+python\s+module\s+([A-Za-z_][\w\.]*)(?:\s+as\s+([A-Za-z_]\w*))?$",
            code.strip(),
            re.IGNORECASE,
        )
        if py_mod_m:
            mod_path = py_mod_m.group(1).strip()
            as_alias = py_mod_m.group(2).strip() if py_mod_m.group(2) else None
            bound_name = as_alias if as_alias else mod_path.split(".")[0]
            scope.record_var(bound_name)
            alias_part = f" as {as_alias}" if as_alias else ""
            emit(f"{indent}use python module {mod_path}{alias_part}", line_idx)
            continue

        from_py_mod_m = re.match(
            r"^from\s+python\s+module\s+([A-Za-z_][\w\.]*)\s+(?:use|import)\s+(.+)$",
            code.strip(),
            re.IGNORECASE,
        )
        if from_py_mod_m:
            mod_path = from_py_mod_m.group(1).strip()
            raw_imports = from_py_mod_m.group(2).strip()
            for item in raw_imports.split(","):
                item = item.strip()
                if not item:
                    continue
                as_match = re.search(r"\bas\s+([A-Za-z_]\w*)$", item, re.IGNORECASE)
                if as_match:
                    scope.record_var(as_match.group(1).strip())
                else:
                    first_w = item.split()[0].strip()
                    if re.match(r"^[A-Za-z_]\w*$", first_w):
                        scope.record_var(first_w)
            emit(f"{indent}from python module {mod_path} use {raw_imports}", line_idx)
            continue

        # Track function definitions and loop headers for scope variables
        m_func_hdr = re.match(r"^\s*to\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?))?:", code, re.IGNORECASE)
        if m_func_hdr:
            scope.record_var(m_func_hdr.group(1))
            f_params = []
            if m_func_hdr.group(2):
                for p in m_func_hdr.group(2).split(","):
                    p_clean = p.strip().split("=")[0].strip()
                    if re.match(r"^[A-Za-z_]\w*$", p_clean):
                        f_params.append(p_clean)
            scope.set_pending_vars(f_params, is_func=True)

        m_for_hdr = re.match(r"^\s*for\s+each\s+(.+?)\s+in\b", code, re.IGNORECASE)
        if m_for_hdr:
            l_vars = []
            for v in m_for_hdr.group(1).split(","):
                v_clean = v.strip()
                if re.match(r"^[A-Za-z_]\w*$", v_clean):
                    l_vars.append(v_clean)
            if "with index" in code.lower() or "with 0-based index" in code.lower():
                l_vars.append("index")
            scope.set_pending_vars(l_vars, is_func=False)

        m_from_hdr = re.match(r"^\s*for\s+(?:each\s+)?([A-Za-z_]\w*)\s+from\b", code, re.IGNORECASE)
        if m_from_hdr:
            scope.set_pending_vars([m_from_hdr.group(1).strip()], is_func=False)

        # Domain Activation: use <domain>, using <domain>, import <domain>, enable <domain> (supports comma and 'and' lists)
        use_domain_m = re.match(
            r"^(?:use|using|import|enable|domain|domains)\s+(.+)$",
            code.strip(),
            re.IGNORECASE,
        )
        if use_domain_m:
            raw_domains = use_domain_m.group(1).strip()
            domain_tokens = re.split(r"\s*,\s*|\s+and\s+", raw_domains)
            activated_any = False
            for d_tok in domain_tokens:
                d_name = d_tok.strip().lower()
                if not d_name:
                    continue
                try:
                    from doomscript.domains.registry import get_domain_registry
                    reg = get_domain_registry()
                    if reg.has_domain(d_name):
                        reg.activate(d_name)
                        activated_any = True
                        dom = reg.get_domain(d_name)
                        if dom and dom.name == "research":
                            in_research_mode = True
                except Exception:
                    pass
                if d_name == "research":
                    in_research_mode = True
            emit(f"{indent}# use {raw_domains}", line_idx)
            continue

        # Declarative Entity with initial lifecycle:
        # a BankAccount begins with balance = 100, status = "active", transactions = []
        begins_with_m = re.match(
            r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+begins\s+with\s+(.+?)(:)?$",
            code.strip(),
            re.IGNORECASE,
        )
        if begins_with_m:
            cname = begins_with_m.group(1)
            defaults_str = begins_with_m.group(2)
            has_colon = bool(begins_with_m.group(3))

            raw_parts = _split_respecting_delimiters(defaults_str, ",")
            field_pairs = []
            for part in raw_parts:
                if "=" in part:
                    f, def_expr = part.split("=", 1)
                    field_pairs.append((f.strip(), def_expr.strip()))
                else:
                    field_pairs.append((part.strip(), "None"))

            params = ", ".join(f"{f}=None" for f, _ in field_pairs)
            emit(f"{indent}class {cname}(DoomEntity):", line_idx)
            emit(f"{indent}    to init with {params}:", line_idx)
            for f, def_expr in field_pairs:
                emit(f"{indent}        if {f} is not None:", line_idx)
                emit(f"{indent}            self.{f} = {f}", line_idx)
                emit(f"{indent}        else:", line_idx)
                emit(f"{indent}            self.{f} = {def_expr}", line_idx)
            continue

        # Declarative Relationship: a User has many Orders
        has_many_m = re.match(
            r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+has\s+many\s+([A-Za-z_]\w*)$",
            code.strip(),
            re.IGNORECASE,
        )
        if has_many_m:
            owner_cls = has_many_m.group(1)
            target = has_many_m.group(2)
            col_name = target.lower()
            if not col_name.endswith("s"):
                col_name = col_name + "s"
            target_cls = target[:-1] if target.endswith("s") and not target.endswith("ss") else target
            target_cls = target_cls[0].upper() + target_cls[1:]
            inv_name = owner_cls.lower()
            emit(f'{indent}ds_register_relation_has_many("{owner_cls}", "{col_name}", "{target_cls}", "{inv_name}")', line_idx)
            continue

        # Declarative Relationship: an Order belongs to a User
        belongs_to_m = re.match(
            r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+belongs\s+to\s+(?:(?:a|an)\s+)?([A-Z]\w*)$",
            code.strip(),
            re.IGNORECASE,
        )
        if belongs_to_m:
            child_cls = belongs_to_m.group(1)
            parent_cls = belongs_to_m.group(2)
            inv_name = parent_cls.lower()
            col_name = child_cls.lower()
            if not col_name.endswith("s"):
                col_name = col_name + "s"
            emit(f'{indent}ds_register_relation_belongs_to("{child_cls}", "{inv_name}", "{parent_cls}", "{col_name}")', line_idx)
            continue

        # Declarative Relationship: a User has one Profile
        has_one_m = re.match(
            r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+has\s+one\s+([A-Za-z_]\w*)$",
            code.strip(),
            re.IGNORECASE,
        )
        if has_one_m:
            owner_cls = has_one_m.group(1)
            target = has_one_m.group(2)
            prop_name = target.lower()
            target_cls = target[0].upper() + target[1:]
            inv_name = owner_cls.lower()
            emit(f'{indent}ds_register_relation_has_one("{owner_cls}", "{prop_name}", "{target_cls}", "{inv_name}")', line_idx)
            continue

        # Declarative Entity: a Person has name, age / Person has name, age = 0, status = "active"
        ent_schema_m = re.match(
            r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+has\s+(?!many\b|one\b)(.+)$",
            code.strip(),
            re.IGNORECASE,
        )
        if ent_schema_m:
            cname = ent_schema_m.group(1)
            raw_field_str = ent_schema_m.group(2)
            raw_parts = [p.strip() for p in raw_field_str.split(",") if p.strip()]
            field_pairs = []
            for p in raw_parts:
                if "=" in p:
                    f_name, def_val = p.split("=", 1)
                    field_pairs.append((f_name.strip(), def_val.strip()))
                elif re.search(r"\(default\s+(.+)\)", p, re.IGNORECASE):
                    m_def = re.search(r"^([A-Za-z_]\w*)\s*\(default\s+(.+)\)", p, re.IGNORECASE)
                    field_pairs.append((m_def.group(1).strip(), m_def.group(2).strip()))
                else:
                    field_pairs.append((p.strip(), "None"))

            params = ", ".join(f"{f}={d}" for f, d in field_pairs)
            emit(f"{indent}class {cname}(DoomEntity):", line_idx)
            emit(f"{indent}    to init with {params}:", line_idx)
            for f, _ in field_pairs:
                emit(f"{indent}        self.{f} = {f}", line_idx)
            continue

        if re.match(r"^target\s+leetcode$", code.strip(), re.IGNORECASE):
            emit(f"{indent}# target leetcode", line_idx)
            continue

        # Database transaction: transaction [db]:
        trans_m = re.match(r"^transaction(?:\s+db)?:$", code.strip(), re.IGNORECASE)
        if trans_m:
            emit(f"{indent}with db_transaction():", line_idx)
            continue

        # Scoped domain block: in <domain>: or within <domain>:
        scoped_dom_m = re.match(r"^(?:in|within)\s+([A-Za-z_]\w*)\s*:$", code.strip(), re.IGNORECASE)
        if scoped_dom_m:
            dom_name = scoped_dom_m.group(1).lower()
            if reg.has_domain(dom_name):
                reg.activate(dom_name)
                scoped_domain_stack.append((indent_len, dom_name))
                emit(f"{indent}if true:  # in {dom_name}", line_idx)
                continue

        # Paradigm 44: Scoped Assumptions ('suppose <var> is <val>:')
        suppose_m = re.match(r"^suppose\s+([A-Za-z_]\w*)\s+is\s+(.+?):$", code.strip(), re.IGNORECASE)
        if suppose_m:
            s_var = suppose_m.group(1)
            s_val = suppose_m.group(2)
            emit(f"{indent}_suppose_saved_{s_var} = {s_var}", line_idx)
            emit(f"{indent}set {s_var} to {s_val}", line_idx)
            emit(f"{indent}if true:", line_idx)
            suppose_stack.append((indent_len, s_var, indent))
            continue

        # Paradigm 31: Periodic Interval Timers ('every 5 seconds:')
        every_m = re.match(r"^every\s+(\d+(?:\.\d+)?)\s+(seconds?|minutes?|hours?|ms|milliseconds?)\s*:$", code.strip(), re.IGNORECASE)
        if every_m:
            n_val = every_m.group(1)
            u_val = every_m.group(2)
            emit(f"{indent}for _pulse in ds_interval({n_val}, '{u_val}'):", line_idx)
            continue

        # Paradigm 71: Declarative State Machine Specification
        can_be_m = re.match(r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+can\s+be\s+(.+)$", code.strip(), re.IGNORECASE)
        if can_be_m:
            ent_name = can_be_m.group(1)
            raw_states = can_be_m.group(2).strip()
            parts = [p.strip().strip("'\"") for p in re.split(r",\s*(?:or\s+)?|\s+or\s+", raw_states) if p.strip()]
            cleaned_states = [f'\"{p}\"' for p in parts]
            emit(f'{indent}ds_register_states("{ent_name}", [{", ".join(cleaned_states)}])', line_idx)
            continue

        # Paradigm 89: Safe Resource Decontamination
        safe_open_m = re.match(r"^safely\s+open\s+file\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s+ensuring\s+it\s+closes\s*:$", code.strip(), re.IGNORECASE)
        if safe_open_m:
            f_path = safe_open_m.group(1).strip()
            f_var = safe_open_m.group(2).strip()
            emit(f"{indent}with open({f_path}) as {f_var}:", line_idx)
            continue

        # Check domain block header (e.g. pipeline "name" from src into target:)
        if code.rstrip().endswith(":"):
            matched_domain_block = reg.find_domain_for_block(code)
            if matched_domain_block:
                domain_block_stack.append({
                    "domain": matched_domain_block,
                    "header": code,
                    "indent": indent_len,
                    "parent_indent": indent,
                    "header_line": line_idx,
                    "lines": [],
                })
                continue

        # Check domain single-line statement (Level 1 / Level 2 inspect, clean, join, etc.)
        # Skip if line is a compound chained sentence so it splits into sub-statements first
        masked_check, _ = mask_strings(code)
        is_chained = bool(re.search(r",\s*(?:and\s+then|then)\s+|\s+and\s+then\s+|;\s*", masked_check, re.IGNORECASE))
        if not is_chained:
            parsed_domain_code = reg.try_parse_domain_line(code, line_idx)
            if parsed_domain_code is not None:
                norm_domain_code = normalize_statement_text(parsed_domain_code, scope, line_idx)
                emit(f"{indent}{norm_domain_code}", line_idx)
                continue

        # If in research mode, apply declarative research phrase normalization first
        if in_research_mode:
            from doomscript.research.registry import apply_research_normalization
            norm_res = apply_research_normalization(code)
            if norm_res is not None:
                code = norm_res

        # Visualization: Inside plot/chart block
        if plot_stack and indent_len > plot_stack[-1]["indent"]:
            cur_plot = plot_stack[-1]
            p_var = cur_plot["var"]

            # Labels sub-block start
            if re.match(r"^labels\s*:?$", code, re.IGNORECASE):
                cur_plot["in_labels"] = True
                cur_plot["labels_indent"] = indent_len
                emit(f"{indent}if true:  # labels", line_idx)
                continue

            # Check if dedented out of labels sub-block
            if cur_plot.get("in_labels"):
                if cur_plot.get("labels_indent") is not None and indent_len <= cur_plot["labels_indent"]:
                    cur_plot["in_labels"] = False
                    cur_plot["labels_indent"] = None

            if cur_plot.get("in_labels"):
                lab_m = re.match(r"^([A-Za-z_]\w*)\s*:\s*(.+)$", code)
                if lab_m:
                    l_key = lab_m.group(1).lower()
                    l_val = lab_m.group(2).strip()
                    emit(f"{indent}{p_var}.labels({l_key}={l_val})", line_idx)
                    continue

            # map <col> to <aes>
            map_m = re.match(r"^map\s+(.+?)\s+to\s+([A-Za-z_]\w*)$", code, re.IGNORECASE)
            if map_m:
                col = map_m.group(1).strip().strip('"\'')
                aes = map_m.group(2).strip().lower()
                emit(f'{indent}{p_var}.map("{aes}", "{col}")', line_idx)
                continue

            # draw <geom> [with <params>]
            draw_m = re.match(r"^draw\s+(.+)$", code, re.IGNORECASE)
            if draw_m:
                d_rest = draw_m.group(1).strip()
                if "smooth" in d_rest.lower():
                    emit(f"{indent}{p_var}.draw('smooth')", line_idx)
                elif " with " in d_rest:
                    g_part, p_part = d_rest.split(" with ", 1)
                    emit(f"{indent}{p_var}.draw('{g_part.strip()}', {p_part.strip()})", line_idx)
                else:
                    emit(f"{indent}{p_var}.draw('{d_rest}')", line_idx)
                continue

            # annotate <text> at x=<x>, y=<y> [with ...]
            ann_m = re.match(
                r"^annotate\s+(.+?)\s+at\s+x=(.+?),\s*y=(.+?)(?:\s+with\s+(.+))?$",
                code,
                re.IGNORECASE,
            )
            if ann_m:
                text_val = ann_m.group(1).strip()
                x_val = ann_m.group(2).strip()
                y_val = ann_m.group(3).strip()
                params = ann_m.group(4)
                if params:
                    emit(
                        f"{indent}{p_var}.annotate({text_val}, x={x_val}, y={y_val}, {params.strip()})",
                        line_idx,
                    )
                else:
                    emit(
                        f"{indent}{p_var}.annotate({text_val}, x={x_val}, y={y_val})",
                        line_idx,
                    )
                continue

            # facet by <col>
            facet_m = re.match(r"^facet\s+by\s+(.+)$", code, re.IGNORECASE)
            if facet_m:
                col = facet_m.group(1).strip().strip('"\'')
                emit(f'{indent}{p_var}.facet("{col}")', line_idx)
                continue

            # facet grid by row=<r>, col=<c>
            facet_grid_m = re.match(r"^facet\s+grid\s+by\s+row=(.+?),\s*col=(.+)$", code, re.IGNORECASE)
            if facet_grid_m:
                r_val = facet_grid_m.group(1).strip().strip('"\'')
                c_val = facet_grid_m.group(2).strip().strip('"\'')
                emit(f'{indent}{p_var}.facet(row="{r_val}", col="{c_val}", type="grid")', line_idx)
                continue

            # scale color/fill as palette <pal>
            scale_pal_m = re.match(r"^scale\s+(color|fill)\s+as\s+palette\s+(.+)$", code, re.IGNORECASE)
            if scale_pal_m:
                target = scale_pal_m.group(1).lower()
                pal = scale_pal_m.group(2).strip()
                emit(f"{indent}{p_var}.scale('{target}', 'palette', palette={pal})", line_idx)
                continue

            # scale x/y as log/reverse
            scale_axis_m = re.match(r"^scale\s+([xy])\s+as\s+(log|reverse)$", code, re.IGNORECASE)
            if scale_axis_m:
                ax = scale_axis_m.group(1).lower()
                st = scale_axis_m.group(2).lower()
                emit(f"{indent}{p_var}.scale('{ax}', '{st}')", line_idx)
                continue

            # theme: <name>
            theme_m = re.match(r"^theme\s*:\s*(.+)$", code, re.IGNORECASE)
            if theme_m:
                th_name = theme_m.group(1).strip().strip('"\'')
                emit(f'{indent}{p_var}.theme("{th_name}")', line_idx)
                continue

            # title: <text>
            title_m = re.match(r"^title\s*:\s*(.+)$", code, re.IGNORECASE)
            if title_m:
                t_val = title_m.group(1).strip()
                emit(f"{indent}{p_var}.title({t_val})", line_idx)
                continue

            # Level 2 property mappings: x: col, y: col, color: col, etc.
            prop_m = re.match(r"^([A-Za-z_]\w*)\s*:\s*(.+)$", code)
            if prop_m:
                prop = prop_m.group(1).lower()
                val = prop_m.group(2).strip().strip('"\'')
                emit(f'{indent}{p_var}.map("{prop}", "{val}")', line_idx)
                continue

        # Visualization: Top-level verbs and block headers
        # 1. Level 1: explore <dataset> [to understand <focus>] [into <target>]
        exp_m = re.match(
            r"^explore\s+([A-Za-z_]\w*)(?:\s+to\s+understand\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            code,
            re.IGNORECASE,
        )
        if exp_m:
            dataset = exp_m.group(1)
            focus_str = exp_m.group(2)
            target = exp_m.group(3) or "explore_report"
            if focus_str:
                emit(f'{indent}set {target} to explore_dataset({dataset}, focus="{focus_str.strip()}")', line_idx)
            else:
                emit(f'{indent}set {target} to explore_dataset({dataset})', line_idx)
            continue

        # 2. show <var>
        show_m = re.match(r"^show\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)\s*$", code, re.IGNORECASE)
        if show_m:
            var_target = show_m.group(1)
            emit(f"{indent}show_plot({var_target})", line_idx)
            continue

        # 3. save <target> to/into <path> [with ...]
        save_stmt_m = re.match(
            r"^save\s+(?:chart\s+)?([A-Za-z_]\w*)\s+(?:to|into)\s+([\"'][^\"']+[\"'])(?:\s+with\s+(.+))?$",
            code,
            re.IGNORECASE,
        )
        if save_stmt_m:
            target_var = save_stmt_m.group(1)
            path_str = save_stmt_m.group(2)
            with_args = save_stmt_m.group(3)
            unquoted_path = path_str.strip('"\'').lower()
            plot_exts = (".png", ".svg", ".html", ".pdf", ".jpeg", ".jpg")
            if with_args or any(unquoted_path.endswith(ext) for ext in plot_exts):
                if with_args:
                    emit(f"{indent}save_plot({target_var}, {path_str}, {with_args})", line_idx)
                else:
                    emit(f"{indent}save_plot({target_var}, {path_str})", line_idx)
            elif unquoted_path.endswith(".csv") or unquoted_path.endswith(".tsv"):
                emit(f"{indent}write csv {target_var} into file {path_str}", line_idx)
            else:
                emit(f"{indent}write {target_var} into file {path_str}", line_idx)
            continue

        # Conversational single-line chart: plot <data> as [a] <geom> chart [titled <title>] [into <target>]
        plot_chart_m = re.match(
            r"^plot\s+([A-Za-z_]\w*)\s+as\s+(?:a\s+)?([A-Za-z_]\w+)\s+chart(?:\s+titled\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$",
            code,
            re.IGNORECASE,
        )
        if plot_chart_m:
            dataset = plot_chart_m.group(1)
            geom = plot_chart_m.group(2).lower()
            title_part = plot_chart_m.group(3)
            target = plot_chart_m.group(4) or "plot"
            if title_part:
                emit(f'{indent}set {target} to PlotBuilder({dataset}, title={title_part.strip()}).draw("{geom}")', line_idx)
            else:
                emit(f'{indent}set {target} to PlotBuilder({dataset}).draw("{geom}")', line_idx)
            continue

        # 4. Level 2 single-line: plot <data> as <geom> with <params> [into <target>]
        plot_single_m = re.match(
            r"^plot\s+([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w+)\s+with\s+(.+?)(?:\s+into\s+([A-Za-z_]\w*))?$",
            code,
            re.IGNORECASE,
        )
        if plot_single_m:
            dataset = plot_single_m.group(1)
            geom = plot_single_m.group(2)
            with_params = plot_single_m.group(3)
            target = plot_single_m.group(4) or "plot"
            emit(f'{indent}set {target} to PlotBuilder({dataset}).kind("{geom}", {with_params})', line_idx)
            continue

        # 5. Level 2 block header: plot <data> as <geom> [into <target>]:
        plot_block_m = re.match(
            r"^plot\s+([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w+)(?:\s+into\s+([A-Za-z_]\w*))?:$",
            code,
            re.IGNORECASE,
        )
        if plot_block_m:
            dataset = plot_block_m.group(1)
            geom = plot_block_m.group(2)
            target = plot_block_m.group(3) or "plot"
            emit(f"{indent}set {target} to PlotBuilder({dataset})", line_idx)
            emit(f"{indent}if true:  # plot block", line_idx)
            plot_stack.append({
                "indent": indent_len,
                "parent_indent": indent,
                "var": target,
                "deferred_draw": geom,
                "in_labels": False,
                "labels_indent": None,
            })
            continue

        # 6. Level 3 chart header: chart <title> from <data> [into <target>]:
        chart_block_m = re.match(
            r"^chart\s+(.+?)\s+from\s+([A-Za-z_]\w*)(?:\s+into\s+([A-Za-z_]\w*))?:$",
            code,
            re.IGNORECASE,
        )
        if chart_block_m:
            title_expr = chart_block_m.group(1)
            dataset = chart_block_m.group(2)
            target = chart_block_m.group(3) or "plot"
            emit(f"{indent}set {target} to PlotBuilder({dataset}, title={title_expr})", line_idx)
            emit(f"{indent}if true:  # chart block", line_idx)
            plot_stack.append({
                "indent": indent_len,
                "parent_indent": indent,
                "var": target,
                "deferred_draw": None,
                "in_labels": False,
                "labels_indent": None,
            })
            continue


        # Phase 10: 'test "name":'
        test_m = re.match(r"^test\s+(.+?):?$", code, re.IGNORECASE)
        if test_m:
            test_name = test_m.group(1).strip()
            emit(f"{indent}if true:  # Test: {test_name}", line_idx)
            continue

        # Phase 9: 'match <expr>:'
        match_m = re.match(r"^match\s+(.+?):?$", code, re.IGNORECASE)
        if match_m:
            target_expr = match_m.group(1).strip()
            match_var = f"__match_val_{len(match_stack)}_{line_idx}"
            emit(f"{indent}set {match_var} to {target_expr}", line_idx)
            match_stack.append({"match_indent": indent_len, "when_indent": None, "var": match_var, "is_first": True})
            continue

        # Phase 9: inside match block
        if match_stack and indent_len > match_stack[-1]["match_indent"]:
            cur_match = match_stack[-1]
            when_m = re.match(r"^when\s+(.+?):?$", code, re.IGNORECASE)
            if when_m:
                if cur_match["when_indent"] is None:
                    cur_match["when_indent"] = indent_len
                pat = when_m.group(1).strip()
                m_var = cur_match["var"]

                if re.match(r"^(?:is\s+)?(?:over|greater\s+than|>)\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^(?:is\s+)?(?:over|greater\s+than|>)\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is greater than {val_rest})"
                elif re.match(r"^(?:is\s+)?(?:under|less\s+than|<)\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^(?:is\s+)?(?:under|less\s+than|<)\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is less than {val_rest})"
                elif re.match(r"^(?:is\s+)?(?:at\s+least|>=)\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^(?:is\s+)?(?:at\s+least|>=)\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is at least {val_rest})"
                elif re.match(r"^(?:is\s+)?(?:at\s+most|<=)\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^(?:is\s+)?(?:at\s+most|<=)\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is at most {val_rest})"
                elif re.match(r"^(?:is\s+)?between\s+(.+?)\s+and\s+(.+)$", pat, re.IGNORECASE):
                    b_m = re.match(r"^(?:is\s+)?between\s+(.+?)\s+and\s+(.+)$", pat, re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is between {b_m.group(1)} and {b_m.group(2)})"
                elif re.match(r"^(?:is\s+)?outside\s+(.+?)\s+and\s+(.+)$", pat, re.IGNORECASE):
                    b_m = re.match(r"^(?:is\s+)?outside\s+(.+?)\s+and\s+(.+)$", pat, re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is outside {b_m.group(1)} and {b_m.group(2)})"
                elif re.match(r"^(?:is\s+)?even$", pat, re.IGNORECASE):
                    cond = f"{m_var} is even"
                elif re.match(r"^(?:is\s+)?odd$", pat, re.IGNORECASE):
                    cond = f"{m_var} is odd"
                elif re.match(r"^(?:is\s+)?positive$", pat, re.IGNORECASE):
                    cond = f"{m_var} is positive"
                elif re.match(r"^(?:is\s+)?negative$", pat, re.IGNORECASE):
                    cond = f"{m_var} is negative"
                elif re.match(r"^(?:is\s+)?zero$", pat, re.IGNORECASE):
                    cond = f"{m_var} is zero"
                elif re.match(r"^(?:is\s+)?empty$", pat, re.IGNORECASE):
                    cond = f"{m_var} is empty"
                elif re.match(r"^(?:is\s+)?(?:one\s+of|inside|in)\s+(.+)$", pat, re.IGNORECASE):
                    in_m = re.match(r"^(?:is\s+)?(?:one\s+of|inside|in)\s+(.+)$", pat, re.IGNORECASE)
                    cond = f"{m_var} is one of {in_m.group(1)}"
                elif pat.lower() in ("a number", "number"):
                    cond = f"{m_var} is a number"
                elif pat.lower() in ("text", "a string", "string"):
                    cond = f"{m_var} is text"
                elif pat.lower() in ("a boolean", "boolean", "bool", "a bool"):
                    cond = f"{m_var} is a boolean"
                elif pat.lower() in ("a list", "list"):
                    cond = f"{m_var} is a list"
                elif pat.lower() in ("a record", "record", "a dictionary", "dict"):
                    cond = f"{m_var} is a record"
                elif re.match(r"^(?:a\s+)?number\s+where\s+it\s+(.+)$", pat, re.IGNORECASE):
                    w_cond = re.match(r"^(?:a\s+)?number\s+where\s+it\s+(.+)$", pat, re.IGNORECASE).group(1)
                    cond = f"({m_var} is a number) and ({m_var} {w_cond})"
                elif " or " in pat:
                    choices = [c.strip() for c in pat.split(" or ")]
                    cond = f"{m_var} is one of [{', '.join(choices)}]"
                else:
                    cond = f"{m_var} equals {pat}"

                branch_keyword = "if" if cur_match["is_first"] else "elif"
                cur_match["is_first"] = False
                emit(f"{' ' * cur_match['match_indent']}{branch_keyword} {cond}:", line_idx)
                continue

            otherwise_m = re.match(r"^(?:otherwise|else):?$", code, re.IGNORECASE)
            if otherwise_m:
                emit(f"{' ' * cur_match['match_indent']}else:", line_idx)
                continue

            # Body lines inside a when branch: unindent by shift
            if cur_match["when_indent"] is not None:
                shift = cur_match["when_indent"] - cur_match["match_indent"]
                new_indent_len = max(indent_len - shift, cur_match["match_indent"] + 4)
                indent = " " * new_indent_len

        # Declarative action on entity: action <name> on [a|an] <Entity> [with <args>]:
        action_on_m = re.match(
            r"^action\s+([A-Za-z_]\w*)\s+on\s+(?:(?:a|an)\s+)?([A-Za-z_]\w*)(?:\s+with\s+(.+?))?\s*:$",
            code,
            re.IGNORECASE,
        )
        if action_on_m:
            act_name = action_on_m.group(1)
            cname = action_on_m.group(2)
            args = (action_on_m.group(3) or "").strip()
            primary_verb = stem_verb(act_name)
            fn_name = f"__{cname}_{primary_verb}_{line_idx}"
            param_str = f"self, {args}" if args else "self"
            emit(f"{indent}to {fn_name} with {param_str}:", line_idx)
            pending_entity_methods.append((indent_len, f"{indent}set {cname}.{primary_verb} to {fn_name}", line_idx))
            if act_name != primary_verb:
                pending_entity_methods.append((indent_len, f"{indent}set {cname}.{act_name} to {fn_name}", line_idx))
            continue

        # Phase 12b: Event-Driven State Transitions ('when ...')
        if not (match_stack and indent_len > match_stack[-1]["match_indent"]):
            # 1. Standalone story rule at top level: when [a|an] <Entity> <action> [with <args>]:
            if indent_len == 0:
                when_standalone_m = re.match(
                    r"^when\s+(?:(?:a|an)\s+)?([A-Za-z_]\w*)\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?)|\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*))?\s*:$",
                    code,
                    re.IGNORECASE,
                )
                if when_standalone_m:
                    cname = when_standalone_m.group(1)
                    raw_action = when_standalone_m.group(2)
                    args = (when_standalone_m.group(3) or when_standalone_m.group(4) or "").strip()
                    primary_verb = stem_verb(raw_action)
                    fn_name = f"__{cname}_{primary_verb}_{line_idx}"
                    param_str = f"self, {args}" if args else "self"
                    emit(f"{indent}to {fn_name} with {param_str}:", line_idx)
                    pending_entity_methods.append((indent_len, f"{indent}set {cname}.{primary_verb} to {fn_name}", line_idx))
                    if raw_action != primary_verb:
                        pending_entity_methods.append((indent_len, f"{indent}set {cname}.{raw_action} to {fn_name}", line_idx))
                    continue

            # 2. Embedded entity method handler inside entity/class block: when <action> [with <args>]:
            else:
                when_embedded_m = re.match(
                    r"^when\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?)|\s+([A-Za-z_]\w*(?:\s*,\s*[A-Za-z_]\w*)*))?\s*:$",
                    code,
                    re.IGNORECASE,
                )
                if when_embedded_m:
                    raw_action = when_embedded_m.group(1)
                    args = (when_embedded_m.group(2) or when_embedded_m.group(3) or "").strip()
                    primary_verb = stem_verb(raw_action)
                    if args:
                        emit(f"{indent}to {primary_verb} with {args}:", line_idx)
                    else:
                        emit(f"{indent}to {primary_verb}:", line_idx)
                    continue

        # Phase 13: 'on get|post|put|delete <path>:'
        route_m = re.match(r"^on\s+(get|post|put|delete)\s+(.+?):?$", code, re.IGNORECASE)
        if route_m:
            method = route_m.group(1).upper()
            path_expr = route_m.group(2).strip()
            slug = re.sub(r"\W+", "_", path_expr.strip('\"\'')).strip("_") or "root"
            fn_name = f"__route_{method.lower()}_{slug}_{line_idx}"
            emit(f"{indent}to {fn_name}:", line_idx)
            pending_routes.append((indent_len, f"{indent}route {method} {path_expr} to {fn_name}", line_idx))
            continue

        # Check for function definition with typed parameters: 'to ... with ...'
        func_m = re.match(r"^to\s+(.+?)\s+with\s+(.+?)(:?)$", code, re.IGNORECASE)
        if func_m and re.search(r"\bas\b", func_m.group(2), re.IGNORECASE):
            func_prefix = func_m.group(1).strip()
            param_str = func_m.group(2).strip()
            colon = func_m.group(3) or ":"

            p_masked, p_strings = mask_strings(param_str)
            raw_params = [p.strip() for p in p_masked.split(",")]
            cleaned_params = []
            assertions = []

            for p in raw_params:
                param_m = re.match(r"^([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w+)(.*)$", p, re.IGNORECASE)
                if param_m:
                    p_name = param_m.group(1)
                    p_type = param_m.group(2).lower()
                    p_rest = param_m.group(3).strip()

                    type_cond = TYPE_CONTRACT_MAP.get(p_type)
                    if type_cond:
                        assertions.append(f'verify that {p_name} {type_cond} otherwise "Argument \'{p_name}\' must be {p_type}"')

                    if p_rest:
                        cleaned_params.append(f"{p_name} {p_rest}".strip())
                    else:
                        cleaned_params.append(p_name)
                else:
                    cleaned_params.append(p)

            if assertions:
                cleaned_param_str = unmask_strings(", ".join(cleaned_params), p_strings)
                new_header = f"to {func_prefix} with {cleaned_param_str}{colon}"
                emit(f"{indent}{new_header}", line_idx)
                pending_injections.append((indent_len, assertions, line_idx))
                continue

    # Phase 9: Destructuring (split via 'and then')
        head_tail_m = re.match(r"^first\s+item\s+into\s+([A-Za-z_]\w*)\s*,\s*remaining\s+items\s+into\s+([A-Za-z_]\w*)\s+from\s+(.+)$", code, re.IGNORECASE)
        if head_tail_m:
            h_var = head_tail_m.group(1)
            t_var = head_tail_m.group(2)
            c_expr = head_tail_m.group(3).strip()
            code = f"set {h_var} to head_of({c_expr}) and then set {t_var} to tail_of({c_expr})"

        unpack_m = re.match(r"^unpack\s+(?!binary\b)(.+?)\s+from\s+(.+)$", code, re.IGNORECASE)
        if unpack_m:
            targets_raw = [t.strip() for t in unpack_m.group(1).split(",")]
            c_expr = unpack_m.group(2).strip()
            quoted_keys = "[" + ", ".join(f'"{t}"' for t in targets_raw) + "]"
            tmp_unp = f"__unp_{line_idx}"
            unp_stmts = [f"set {tmp_unp} to unpack_values({quoted_keys}, {c_expr})"]
            for idx, t in enumerate(targets_raw, 1):
                unp_stmts.append(f"set {t} to item {idx} of {tmp_unp}")
            code = " and then ".join(unp_stmts)

        # Check for typed variable assignments: 'set x as number to 5' / 'x as number = 5'
        var_typed_m = re.match(r"^(?:set\s+)?([A-Za-z_]\w*)\s+as\s+([A-Za-z_]\w+)\s+(?:to|=)\s+(.+)$", code, re.IGNORECASE)
        if var_typed_m and var_typed_m.group(2).lower() in TYPE_CONTRACT_MAP:
            v_name = var_typed_m.group(1)
            v_type = var_typed_m.group(2).lower()
            v_expr = var_typed_m.group(3).strip()
            type_cond = TYPE_CONTRACT_MAP[v_type]
            code = f'set {v_name} to {v_expr} and then verify that {v_name} {type_cond} otherwise "Variable \'{v_name}\' must be {v_type}"'

        # Single-line 'if ... then ...' split: e.g. 'if x is 5 then say "five"'
        if_then_m = re.match(r"^if\s+(.+?)\s+then\s+([^\s].*)$", code, re.IGNORECASE)
        if if_then_m:
            cond = if_then_m.group(1).strip()
            then_stmt = if_then_m.group(2).strip()
            norm_cond = normalize_statement_text(f"if {cond}", scope, line_idx)
            norm_then = normalize_statement_text(then_stmt, scope, line_idx)
            if not norm_cond.endswith(":"):
                norm_cond += ":"
            emit(f"{indent}{norm_cond}", line_idx)
            emit(f"{indent}    {norm_then}", line_idx)
            continue

        # Single-line 'unless ... then ...' split: e.g. 'unless x is 5 then say "not five"'
        unless_then_m = re.match(r"^unless\s+(.+?)\s+then\s+([^\s].*)$", code, re.IGNORECASE)
        if unless_then_m:
            cond = unless_then_m.group(1).strip()
            then_stmt = unless_then_m.group(2).strip()
            norm_cond = normalize_statement_text(f"if not ({cond})", scope, line_idx)
            norm_then = normalize_statement_text(then_stmt, scope, line_idx)
            if not norm_cond.endswith(":"):
                norm_cond += ":"
            emit(f"{indent}{norm_cond}", line_idx)
            emit(f"{indent}    {norm_then}", line_idx)
            continue

        # Compound sentence chaining into block statement: e.g. 'do something, then if cond:'
        compound_chain_m = re.match(r"^(.+?)(?:,\s*and\s+then|,\s*then|\s+and\s+then)\s+((?:if|unless|for|while|repeat)\s+.+?:)$", code, re.IGNORECASE)
        if compound_chain_m:
            first_stmt = compound_chain_m.group(1).strip()
            second_hdr = compound_chain_m.group(2).strip()
            first_masked, first_strings = mask_strings(first_stmt)
            pre_chain_parts = re.split(r"\s*(?:,\s*and\s+then|,\s*then|\s+and\s+then|;)\s+", first_masked, flags=re.IGNORECASE)
            for part in pre_chain_parts:
                for dp in re.split(r"\.\s+", part):
                    cleaned = dp.strip()
                    if cleaned.endswith("."):
                        cleaned = cleaned[:-1].rstrip()
                    if not cleaned:
                        continue
                    unmasked_part = unmask_strings(cleaned, first_strings)
                    dom_parsed = reg.try_parse_domain_line(unmasked_part, line_idx)
                    target_part = dom_parsed if dom_parsed is not None else unmasked_part
                    norm_part = normalize_statement_text(target_part, scope, line_idx)
                    if norm_part:
                        assigned = extract_assigned_var(norm_part)
                        if assigned:
                            scope.record_assignment(assigned)
                        emit(f"{indent}{norm_part}", line_idx)
            norm_second = normalize_statement_text(second_hdr, scope, line_idx)
            emit(f"{indent}{norm_second}", line_idx)
            continue

        # Mask strings for statement splitting
        masked_code, code_strings = mask_strings(code)

        # Multi-clause natural sentence chaining desugaring
        s_trimmed = masked_code.strip()
        s_lower = s_trimmed.lower()
        if not s_trimmed.endswith(":") and not s_lower.startswith(("if ", "unless ", "while ", "repeat ", "for each ", "to ", "target ")):
            # Rule 1: '... into <var> and <verb> ...'
            masked_code = re.sub(
                r"\b(into\s+[A-Za-z_]\w*)\s+and\s+((?:[A-Za-z_]\w*)\b)",
                lambda m: f"{m.group(1)} and then {m.group(2)}" if m.group(2).lower() in STATEMENT_START_KEYWORDS else m.group(0),
                masked_code,
                flags=re.IGNORECASE,
            )
            # Rule 2: '... then <verb> ...' (where not preceded by 'and ')
            masked_code = re.sub(
                r"(?<!\band\s)\bthen\s+([A-Za-z_]\w*)",
                lambda m: f"and then {m.group(1)}" if m.group(1).lower() in STATEMENT_START_KEYWORDS else m.group(0),
                masked_code,
                flags=re.IGNORECASE,
            )
        if not re.search(r"^\s*group\s+.+?\s+by\s+.+?\s+and\s+(?:average|mean|sum)\b", masked_code, re.IGNORECASE):
            # Rule 3: '... and <imperative_verb> ...' (all statement verbs)
            masked_code = re.sub(
                r"(?<!\band\sthen)(?<!\bgo\sahead)\s+and\s+([A-Za-z_]\w*)",
                lambda m: f" and then {m.group(1)}" if m.group(1).lower() in STATEMENT_START_KEYWORDS and m.group(1).lower() not in ("then", "of", "in", "to", "as", "with", "by", "from") else m.group(0),
                masked_code,
                flags=re.IGNORECASE,
            )
            # Rule 4: '<assign> and <assign>' (e.g. x = 10 and y = 20)
            masked_code = re.sub(
                r"\s+and\s+([A-Za-z_]\w*\s*=(?!=))",
                r" and then \1",
                masked_code,
                flags=re.IGNORECASE,
            )

        # 1. Statement chaining via 'and then', 'then', and semicolons
        chain_parts = re.split(r"\s*(?:,\s*and\s+then|,\s*then|\s+and\s+then|;)\s+", masked_code, flags=re.IGNORECASE)

        sub_statements: List[str] = []
        for part in chain_parts:
            # 2. Period sentence ending: split on period followed by space
            # e.g., 'set x to 5. say x.'
            dot_parts = re.split(r"\.\s+", part)
            for dp in dot_parts:
                cleaned = dp.strip()
                # Strip trailing period at end of statement
                if cleaned.endswith("."):
                    cleaned = cleaned[:-1].rstrip()
                if cleaned:
                    sub_statements.append(cleaned)

        # Process each statement
        for s in sub_statements:
            unmasked_s = unmask_strings(s, code_strings)
            dom_parsed = reg.try_parse_domain_line(unmasked_s, line_idx)
            target_s = dom_parsed if dom_parsed is not None else unmasked_s
            norm_s = normalize_statement_text(target_s, scope, line_idx)
            if norm_s:
                assigned = extract_assigned_var(norm_s)
                if assigned:
                    scope.record_assignment(assigned)
                emit(f"{indent}{norm_s}", line_idx)

    while pending_injections:
        top_indent, assertions, top_line = pending_injections.pop(0)
        body_indent = " " * (top_indent + 4)
        for inj in assertions:
            emit(f"{body_indent}{inj}", top_line)

    while pending_routes:
        _, r_stmt, r_line = pending_routes.pop(0)
        emit(r_stmt, r_line)

    while pending_entity_methods:
        _, em_stmt, em_line = pending_entity_methods.pop(0)
        emit(em_stmt, em_line)

    while plot_stack:
        p_info = plot_stack.pop(0)
        if p_info.get("deferred_draw"):
            emit(f"{p_info['parent_indent']}{p_info['var']}.draw('{p_info['deferred_draw']}')", len(lines))

    while domain_block_stack:
        _close_domain_block(domain_block_stack.pop(0), len(lines))

    while scoped_domain_stack:
        _, d_to_pop = scoped_domain_stack.pop(0)
        reg.deactivate(d_to_pop)

    while suppose_stack:
        _, s_var, p_ind = suppose_stack.pop(0)
        emit(f"{p_ind}set {s_var} to _suppose_saved_{s_var}", len(lines))

    res_str = "\n".join(output_lines) + ("\n" if source.endswith("\n") else "")
    return res_str, line_map

def normalize(source: str) -> str:
    return normalize_with_map(source)[0]


def explain_normalization(source: str) -> List[Tuple[str, str]]:
    """Returns pairs of (original, normalized) lines for inspection."""
    orig_lines = source.splitlines()
    norm_source = normalize(source)
    norm_lines = norm_source.splitlines()
    return list(zip(orig_lines, norm_lines))