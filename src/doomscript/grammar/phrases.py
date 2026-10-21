"""
DoomScript Normalization and Phrase Layer
Driven by data tables (synonyms, filler words, flexible assignments, pronouns, possessives).
Adding a synonym here requires NO grammar edits.
"""

import difflib
import re
from typing import Optional, List, Tuple, Dict, Any
from doomscript.exceptions import DoomScopeError, DoomSyntaxError


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
    "increase", "decrease", "increment", "decrement", "bump", "double", "halve", "triple",
    "multiply", "divide",
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
    "round", "clamp", "convert",
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

STRING_REGEX = re.compile(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|(?<!\w)\'(?:[^\'\\]|\\.)*\')')

F_STRING_PREFIX_REGEX = re.compile(r'(?<!\w)[fF](?=["\'])')

def mask_strings(text: str) -> Tuple[str, List[str]]:
    """Replaces string literals with placeholders to preserve their exact content."""
    text = F_STRING_PREFIX_REGEX.sub("", text)
    strings = []
    def repl(m):
        idx = len(strings)
        strings.append(m.group(0))
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
    Maintains a stack of lexical scopes to track the most recently assigned
    variable for resolving the pronouns 'it' and 'that'.
    """
    def __init__(self):
        # Stack of indent levels and their last assigned variable
        # [(indent_level, last_var)]
        self.scopes: List[Dict[str, Any]] = [{"indent": 0, "last_var": None, "diverged": False}]

    def update_indent(self, indent: int):
        # If indent decreased, pop deeper scopes
        while len(self.scopes) > 1 and self.scopes[-1]["indent"] > indent:
            popped = self.scopes.pop()
            # If the current parent had no last_var, inherit if not diverged
            if self.scopes[-1]["last_var"] is None and not popped["diverged"]:
                self.scopes[-1]["last_var"] = popped["last_var"]

        # If indent increased, push new scope inheriting current last_var
        if indent > self.scopes[-1]["indent"]:
            self.scopes.append({"indent": indent, "last_var": self.scopes[-1]["last_var"], "diverged": False})

    def record_assignment(self, var_name: str):
        self.scopes[-1]["last_var"] = var_name

    def mark_diverged(self):
        self.scopes[-1]["diverged"] = True
        self.scopes[-1]["last_var"] = None

    def get_last_var(self) -> Optional[str]:
        return self.scopes[-1]["last_var"]


# Helper regex to detect variable assignment targets
ASSIGN_VAR_PATTERNS = [
    re.compile(r"^\s*set\s+([A-Za-z_]\w*)\s+to\b", re.IGNORECASE),
    re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(?!=\s*)"),
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
# STATEMENT NORMALIZATION PIPELINE
# ---------------------------------------------------------------------------

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

    # Normalize 'attempt' to 'try'
    if re.match(r"^attempt\b", masked, re.IGNORECASE):
        masked = re.sub(r"^attempt\b", "try", masked, flags=re.IGNORECASE)

    # If or unless condition ending in 'then' -> replace with ':'
    if re.match(r"^(?:if|unless)\s+.+\s+then$", masked, re.IGNORECASE):
        masked = re.sub(r"\s+then$", ":", masked, flags=re.IGNORECASE)

    # Pre-normalize and protect assert that / make sure that / check that / assert
    masked = re.sub(r"^\s*(?:make\s+sure\s+that|assert\s+that|assert|check\s+that)\s+(.+?)\s+otherwise\s+(.+)$", r"verify that \1 otherwise \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*(?:make\s+sure\s+that|assert\s+that|assert|check\s+that)\s+(.+)$", r'verify that \1 otherwise "Check failed"', masked, flags=re.IGNORECASE)

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
    masked = re.sub(r"\b(?:my|its)\s+([A-Za-z_]\w*)", r"self.\1", masked, flags=re.IGNORECASE)

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
        r"\b(?:the\s+)?squares\s+(?:of|from)\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\s+to\s+([A-Za-z_]\w*|\d+(?:\.\d+)?)\b",
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

    # Expression sort: sorted <var> -> sorted of <var>
    masked = re.sub(
        r"\bsorted\s+(?!of\b)([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)(?!\s*[\(=])\b",
        r"sorted of \1",
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
        r"^\s*sort\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])?)\s*$",
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
    masked = re.sub(r"\bif\s+(?:(?:it|that)\s+fails|there\s+is\s+an?\s+error)\b", "__IF_FAILS__", masked, flags=re.IGNORECASE)

    pronoun_match = re.search(r"\b(it|that)\b", masked, re.IGNORECASE)
    if pronoun_match:
        last_var = scope.get_last_var()
        if not last_var:
            raise DoomScopeError(
                f"Cannot resolve pronoun '{pronoun_match.group(1)}' on line {line_num}: no preceding variable assigned in scope.",
                line=line_num,
                source_line=stmt,
                suggestion="assign a variable first or use an explicit variable name"
            )
        masked = re.sub(r"\b(it|that)\b", last_var, masked, flags=re.IGNORECASE)

    # Restore protected keywords (also normalizes 'if that fails' to 'if it fails')
    masked = masked.replace("__VERIFY_THAT__", "verify that")
    masked = masked.replace("__IF_FAILS__", "if it fails")

    # 5. Verb Synonyms
    # Handle display vs display colored
    if re.match(r"^display\s+colored\b", masked, re.IGNORECASE):
        pass  # Keep legacy display colored
    elif re.match(r"^display\b", masked, re.IGNORECASE):
        masked = re.sub(r"^display\b", "say", masked, flags=re.IGNORECASE)

    for syn, canonical in VERB_SYNONYMS.items():
        pattern = re.compile(rf"^{syn}\b", re.IGNORECASE)
        if pattern.match(masked):
            masked = pattern.sub(canonical, masked)
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
    masked = re.sub(r"^\s*random\s+number\b", "roll", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*open\s+window\b", "open_window", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*with\s+(.+?)\s+(?:as|into)\s+([A-Za-z_]\w*)\s*:?", r"with \1 into \2:", masked, flags=re.IGNORECASE)
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
    masked = re.sub(r"^\s*(?:sleep|delay|pause)\s+(.+?\s+(?:seconds?|ms|milliseconds))\s*$", r"wait \1", masked, flags=re.IGNORECASE)

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

    # Ergonomic Networking & HTTP (fetch, post, download)
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
    masked = re.sub(r"\b(?:an\s+empty\s+record|a\s+new\s+record|empty\s+record)\b", "Record()", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:a\s+list\s+of|list\s+of)\s+([^;\n]+?)(?=\s+with\b|\s+at\b|\s+into\b|;\s*|\n|$)", r"[\1]", masked, flags=re.IGNORECASE)

    # Function definition with 'on': 'to tax on price' -> 'to tax with price'
    masked = re.sub(r"^\s*to\s+([A-Za-z_]\w*)\s+on\s+([A-Za-z_]\w*)\b", r"to \1 with \2", masked, flags=re.IGNORECASE)

    # Filter statements with assignment or into
    filter_into_m = re.match(r"^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s+where\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if filter_into_m:
        masked = f"{filter_into_m.group(2)} where {filter_into_m.group(3)} into {filter_into_m.group(4)}"
    else:
        filter_assign_m = re.match(r"^\s*([A-Za-z_]\w*)\s*=\s*(.+?)\s+where\s+(.+?)$", masked, re.IGNORECASE)
        if filter_assign_m:
            masked = f"{filter_assign_m.group(2)} where {filter_assign_m.group(3)} into {filter_assign_m.group(1)}"

    # Normalize square root of to sqrt of
    masked = re.sub(r"\bsquare\s+root\s+of\b", "sqrt of", masked, flags=re.IGNORECASE)

    # Result of function calls in expressions
    masked = re.sub(r"\b(?:the\s+)?result\s+of\s+([A-Za-z_]\w*)\s+on\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"\1(\2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?result\s+of\s+([A-Za-z_]\w*)\s+with\s+(.+?)(?=\s+and\s+then|\s+into\b|\s+otherwise\b|\s*$)", r"\1(\2)", masked, flags=re.IGNORECASE)

    # Field aggregates
    masked = re.sub(r"\b(?:total|sum)\s+of\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)", r'agg_field("sum", "\1", \2)', masked, flags=re.IGNORECASE)
    masked = re.sub(r"\baverage\s+of\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)", r'agg_field("avg", "\1", \2)', masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:highest|maximum)\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)", r'agg_field("max", "\1", \2)', masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:lowest|minimum)\s+([A-Za-z_]\w*)\s+in\s+([A-Za-z_]\w*)", r'agg_field("min", "\1", \2)', masked, flags=re.IGNORECASE)

    # List operations
    masked = re.sub(r"^\s*set\s+item\s+(.+?)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+to\s+(.+)$", r"set_item(\1, \2, \3)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bitem\s+(\d+|[A-Za-z_]\w*)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"item_of(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\bfirst\s+(\d+|[A-Za-z_]\w*)\s+items\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"first_n_items(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\blast\s+(\d+|[A-Za-z_]\w*)\s+items\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"last_n_items(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:title|titlecase)\s+of\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)", r"str_title(\1)", masked, flags=re.IGNORECASE)

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
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<![\"'])\badd\b(?![\"'])(?!\s+(?:.+?\s+)?to\b)", "_var_add", masked)
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<!\bto\s)(?<!\bbullet\s)(?<!\ba\s)(?<!\bempty\s)(?<!\bnew\s)(?<![\"'])\blist\b(?![\"'])(?!\s+files\b)(?!\s+of\b)(?!\s*\()", "_var_list", masked)
    masked = re.sub(r"(?<!'s\s)(?<!\.)(?<!\bto\s)(?<!\bfind\s)(?<!\btake\s)(?<!\bdrop\s)\bfirst\b(?!\s+(?:\d+|[A-Za-z_]\w*)\s+items?\s+(?:of|from)\b|\s+item\s+of\b|\s+[A-Z]\w*)(?!\s*\()", "_var_first", masked)
    masked = re.sub(r"\bround\s*\(", "math_round(", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(?<!\.)\bsum\s*\(", "agg_sum(", masked, flags=re.IGNORECASE)

    # Arithmetic in words
    double_m = re.match(r"^\s*double\s+([A-Za-z_]\w*)\s*$", masked, re.IGNORECASE)
    if double_m:
        var = double_m.group(1)
        masked = f"set {var} to {var} * 2"

    masked = re.sub(r"(\d+(?:\.\d+)?)\s*%\s+of\s+([A-Za-z_]\w*|\d+(?:\.\d+)?|\([^)]+\))", r"percent_of(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+to\s+(?:the\s+)?power\s+of\s+(\b\w+|\()", r"math_pow(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+squared\b", r"math_pow(\1, 2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+mod\s+(\b\w+|\()", r"math_mod(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+plus\s+(\b\w+|\()", r"\1 + \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+minus\s+(\b\w+|\()", r"\1 - \2", masked, flags=re.IGNORECASE)
    if not re.match(r"^\s*repeat\b", masked, re.IGNORECASE):
        masked = re.sub(r"(\b\w+|\))\s+times\s+(\b\w+|\()", r"\1 * \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+multiplied\s+by\s+(\b\w+|\()", r"\1 * \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b(?:the\s+)?remainder\s+of\s+(.+?)\s+(?:divided\s+by|mod|/)\s+([^\s;,\n]+)", r"math_mod(\1, \2)", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+|\))\s+divided\s+by\s+(\b\w+|\()", r"\1 / \2", masked, flags=re.IGNORECASE)

    # Arithmetic Mutators in English
    masked = re.sub(r"^\s*increment\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"increase \1 by \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*increment\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"increase \1 by 1", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*decrement\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+by\s+(.+)$", r"decrease \1 by \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"^\s*decrement\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*$", r"decrease \1 by 1", masked, flags=re.IGNORECASE)
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
    masked = re.sub(r"^\s*discard\s+(.+?)\s+from\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?)\s*$", r"remove \1 from \2", masked, flags=re.IGNORECASE)
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
    _SUBJ_PAT = r"(\d+(?:\.\d+)?|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*)?|\([^\)]+\))"
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
    masked = re.sub(r"(\b\w+(?:'s\s+[A-Za-z_]\w*)?|\))\s+is\s+(?:inside|in)\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?|\[[^\]]*\]|\{[^\}]*\})", r"\1 is inside \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"(\b\w+(?:'s\s+[A-Za-z_]\w*)?|\))\s+(?:is\s+)?not\s+(?:inside|in)\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?|\[[^\]]*\]|\{[^\}]*\})", r"\1 is not inside \2", masked, flags=re.IGNORECASE)
    masked = re.sub(r"\b([A-Za-z_]\w*(?:\[[^\]]+\])?|\d+)\s+xor\s+([A-Za-z_]\w*(?:\[[^\]]+\])?|\d+)\b", r"\1 ^ \2", masked, flags=re.IGNORECASE)
    
    # Membership 'in' operator: x in y -> x is inside y (excluding for-loops, comprehensions, and statement keywords)
    if not re.match(r"^\s*(?:set\s+(?:cookie|config)|remember\s+in\s+memory|mask\s+pii|list\s+files|start\s+server|insert\b|replace\b|display\s+colored|fill\b)\b", masked, re.IGNORECASE):
        def _in_repl(m):
            if m.group(2).lower() in ("background", "bytes", "seconds", "minutes", "hours", "milliseconds", "days"):
                return m.group(0)
            if m.group(1).lower() in ("highest", "maximum", "lowest", "minimum", "files", "nulls", "missing", "items", "now"):
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
    masked = re.sub(r"\b(?:the\s+)?remainder\s+of\s+(.+?)\s+(?:divided\s+by|mod|/)\s+([^\s;,\n]+)", r"math_mod(\1, \2)", masked, flags=re.IGNORECASE)

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
        msg_part = req_otherwise_m.group(2).strip()
        masked = f"verify that {cond_part} otherwise {msg_part}"
    else:
        req_m = re.match(r"^require\s+(.+)$", masked, re.IGNORECASE)
        if req_m:
            cond_part = req_m.group(1).strip()
            orig_cond_text = unmask_strings(cond_part, strings)
            safe_cond = orig_cond_text.replace('"', "'")
            msg_literal = f'"Requirement failed: {safe_cond}"'
            msg_idx = len(strings)
            strings.append(msg_literal)
            masked = f"verify that {cond_part} otherwise __STR_LITERAL_{msg_idx}__"

    ens_otherwise_m = re.match(r"^ensure\s+(.+?)\s+otherwise\s+(.+)$", masked, re.IGNORECASE)
    if ens_otherwise_m:
        cond_part = ens_otherwise_m.group(1).strip()
        msg_part = ens_otherwise_m.group(2).strip()
        masked = f"verify that {cond_part} otherwise {msg_part}"
    else:
        ens_m = re.match(r"^ensure\s+(.+)$", masked, re.IGNORECASE)
        if ens_m:
            cond_part = ens_m.group(1).strip()
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

    timeout_m = re.match(r"^timeout\s+(.+?)\s+seconds\s+for\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
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

    orm_save_m = re.match(r"^(?:save\s+new|create\s+(?:a|an\s+)?)\s*([A-Za-z_]\w*)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if orm_save_m:
        ename = orm_save_m.group(1)
        vals_str = orm_save_m.group(2)
        target = orm_save_m.group(3)
        val_pairs = [v.strip() for v in re.split(r",\s*", vals_str)]
        kwargs = []
        for vp in val_pairs:
            m_vp = re.match(r"^([A-Za-z_]\w*)[:\s]+(.+)$", vp)
            if m_vp:
                kwargs.append(f'{m_vp.group(1)}={m_vp.group(2).strip()}')
        if masked.lower().startswith("save new"):
            masked = f'set {target} to orm_save("{ename}", {", ".join(kwargs)})'
        else:
            masked = f'set {target} to make_entity("{ename}", {", ".join(kwargs)})' 

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
    sched_every_m = re.match(r"^schedule\s+every\s+(.+?)\s+seconds?\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if sched_every_m:
        masked = f"schedule_every_seconds({sched_every_m.group(1).strip()}, {sched_every_m.group(2)})"

    sched_run_m = re.match(r"^run\s+scheduler\s+for\s+(.+?)\s+seconds?$", masked, re.IGNORECASE)
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
    pipe_m = re.match(r"^pipe\s+(.+?)\s+into\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if pipe_m:
        masked = f"set {pipe_m.group(3)} to pipe_pipeline({pipe_m.group(1).strip()}, {pipe_m.group(2).strip()})"

    take_m = re.match(r"^take\s+first\s+(\d+)\s+items\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if take_m:
        masked = f"set {take_m.group(3)} to take_first_n({take_m.group(2).strip()}, {take_m.group(1)})"

    drop_m = re.match(r"^drop\s+first\s+(\d+)\s+items\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", masked, re.IGNORECASE)
    if drop_m:
        masked = f"set {drop_m.group(3)} to drop_first_n({drop_m.group(2).strip()}, {drop_m.group(1)})"

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
    match_stack: List[Dict[str, Any]] = []
    plot_stack: List[Dict[str, Any]] = []
    domain_block_stack: List[Dict[str, Any]] = []
    in_research_mode: bool = False

    from doomscript.domains.registry import get_domain_registry
    reg = get_domain_registry()
    reg.reset_active()

    def _close_domain_block(b_info, at_line_idx):
        ir_spec, target_var = b_info["domain"].parser.parse_block(b_info["header"], b_info["lines"], b_info["indent"])
        spec_id = reg.store_spec(ir_spec)
        d_name = b_info["domain"].name
        emit(f"{b_info['parent_indent']}set {target_var} to execute_{d_name}_ir('{spec_id}')", b_info["header_line"])

    for line_idx, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            if domain_block_stack:
                domain_block_stack[-1]["lines"].append((line_idx, raw_line))
                continue
            emit("", line_idx)
            continue

        # Extract leading indentation
        indent_len = len(raw_line) - len(raw_line.lstrip(" "))
        indent = " " * indent_len
        scope.update_indent(indent_len)

        # Pop domain_block_stack if indentation returned to parent level
        while domain_block_stack and indent_len <= domain_block_stack[-1]["indent"]:
            _close_domain_block(domain_block_stack.pop(), line_idx)

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

        # Check pending deferred routes if indentation returned to parent level
        while pending_routes and indent_len <= pending_routes[-1][0]:
            _, r_stmt, r_line = pending_routes.pop()
            emit(r_stmt, r_line)

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

        # Domain Activation: use <domain>, using <domain>, import <domain>, enable <domain>
        use_domain_m = re.match(
            r"^(?:use|using|import|enable)\s+([A-Za-z_]\w*)$",
            code.strip(),
            re.IGNORECASE,
        )
        if use_domain_m:
            domain_name = use_domain_m.group(1).lower()
            try:
                from doomscript.domains.registry import get_domain_registry
                reg = get_domain_registry()
                if reg.has_domain(domain_name):
                    reg.activate(domain_name)
                    dom = reg.get_domain(domain_name)
                    if dom and dom.name == "research":
                        in_research_mode = True
            except Exception:
                pass
            if domain_name == "research":
                in_research_mode = True
            emit(f"{indent}# use {domain_name}", line_idx)
            continue

                # Declarative Entity: a Person has name, age / Person has name, age
        ent_schema_m = re.match(
            r"^(?:(?:a|an)\s+)?([A-Z]\w*)\s+has\s+([A-Za-z_][A-Za-z0-9_,\s]*)$",
            code.strip(),
            re.IGNORECASE,
        )
        if ent_schema_m:
            cname = ent_schema_m.group(1)
            raw_fields = [f.strip() for f in ent_schema_m.group(2).split(",") if f.strip()]
            params = ", ".join(f"{f}=None" for f in raw_fields)
            emit(f"{indent}class {cname}:", line_idx)
            emit(f"{indent}    to init with {params}:", line_idx)
            for f in raw_fields:
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

                if re.match(r"^(?:over|greater\s+than)\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^(?:over|greater\s+than)\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is greater than {val_rest})"
                elif re.match(r"^(?:under|less\s+than)\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^(?:under|less\s+than)\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is less than {val_rest})"
                elif re.match(r"^at\s+least\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^at\s+least\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is at least {val_rest})"
                elif re.match(r"^at\s+most\s+", pat, re.IGNORECASE):
                    val_rest = re.sub(r"^at\s+most\s+", "", pat, flags=re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is at most {val_rest})"
                elif re.match(r"^between\s+(.+?)\s+and\s+(.+)$", pat, re.IGNORECASE):
                    b_m = re.match(r"^between\s+(.+?)\s+and\s+(.+)$", pat, re.IGNORECASE)
                    cond = f"({m_var} is a number) and ({m_var} is between {b_m.group(1)} and {b_m.group(2)})"
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

        # Mask strings for statement splitting
        masked_code, code_strings = mask_strings(code)

        # 1. Statement chaining via 'and then'
        chain_parts = re.split(r"\s+and\s+then\s+", masked_code, flags=re.IGNORECASE)

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
            norm_s = normalize_statement_text(unmasked_s, scope, line_idx)
            if norm_s:
                emit(f"{indent}{norm_s}", line_idx)

    while pending_injections:
        top_indent, assertions, top_line = pending_injections.pop(0)
        body_indent = " " * (top_indent + 4)
        for inj in assertions:
            emit(f"{body_indent}{inj}", top_line)

    while pending_routes:
        _, r_stmt, r_line = pending_routes.pop(0)
        emit(r_stmt, r_line)

    while plot_stack:
        p_info = plot_stack.pop(0)
        if p_info.get("deferred_draw"):
            emit(f"{p_info['parent_indent']}{p_info['var']}.draw('{p_info['deferred_draw']}')", len(lines))

    while domain_block_stack:
        _close_domain_block(domain_block_stack.pop(0), len(lines))

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
