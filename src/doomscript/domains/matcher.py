"""Declarative Spoken-English Phrase Engine for DoomScript Domains."""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import re
import difflib


@dataclass
class VerbSpec:
    """Specification of a single spoken-English domain operation verb."""

    pattern: str
    emit: str = ""
    name: str = ""
    arg_schema: Dict[str, str] = field(default_factory=dict)
    defaults: Dict[str, Any] = field(default_factory=dict)
    returns: str = "Any"
    doc: str = ""
    description: str = ""
    _compiled_regex: Optional[re.Pattern] = field(default=None, repr=False)
    _slots: List[Tuple[str, str]] = field(default_factory=list, repr=False)
    _alt_groups: List[str] = field(default_factory=list, repr=False)

    def __post_init__(self):
        if not self.description and self.doc:
            self.description = self.doc
        if not self.doc and self.description:
            self.doc = self.description
        if not self.name and self.pattern:
            self.name = self.pattern.split()[0].replace("[", "").replace("]", "")
        self._compile()

    def _compile(self) -> None:
        """Compiles human-readable pattern template into an efficient regex."""
        raw = re.sub(r"\s+", " ", self.pattern.strip())
        self._slots = []
        self._alt_groups = []

        tokens: List[str] = []
        pos = 0
        n = len(raw)
        need_space = False

        while pos < n:
            c = raw[pos]

            if c == " ":
                if tokens and not tokens[-1].endswith(r"\s+)?"):
                    need_space = True
                pos += 1
                continue

            # Optional block [ ... ]
            if c == "[":
                close = raw.find("]", pos)
                if close == -1:
                    close = n
                inner = raw[pos + 1 : close].strip()
                pos = close + 1
                sub = self._compile_subpattern(inner)
                if not tokens:  # at very start of pattern
                    tokens.append(f"(?:{sub}\\s+)?")
                    need_space = False
                else:
                    tokens.append(f"(?:\\s+{sub})?")
                    need_space = True
                continue

            # If space is needed before this required element
            if need_space:
                tokens.append(r"\s+")
                need_space = False

            # Alternatives (a|b|c)
            if c == "(":
                close = raw.find(")", pos)
                if close == -1:
                    close = n
                inner = raw[pos + 1 : close].strip()
                pos = close + 1
                alt_name = f"alt_{len(self._alt_groups) + 1}"
                self._alt_groups.append(inner)
                tokens.append(f"(?P<{alt_name}>{inner})")
                continue

            # Slot {name:type}
            if c == "{":
                close = raw.find("}", pos)
                if close == -1:
                    close = n
                slot_def = raw[pos + 1 : close].strip()
                pos = close + 1
                if ":" in slot_def:
                    s_name, s_type = slot_def.split(":", 1)
                    s_name, s_type = s_name.strip(), s_type.strip()
                else:
                    s_name, s_type = slot_def, "expr"

                self._slots.append((s_name, s_type))
                if s_type == "ident":
                    tokens.append(f"(?P<slot_{s_name}>[A-Za-z_]\\w*)")
                elif s_type == "int":
                    tokens.append(f"(?P<slot_{s_name}>\\d+)")
                elif s_type == "float":
                    tokens.append(f"(?P<slot_{s_name}>-?\\d+(?:\\.\\d+)?)")
                elif s_type == "str":
                    tokens.append(f'(?P<slot_{s_name}>"(?:\\\\.|[^"\\\\])*"|\'(?:\\\\.|[^\'\\\\])*\')')
                else:
                    tokens.append(f"(?P<slot_{s_name}>.+?)")
                continue

            # Word / token
            wm = re.match(r"^[A-Za-z0-9_]+", raw[pos:])
            if wm:
                w = wm.group(0)
                pos += len(w)
                tokens.append(re.escape(w))
            else:
                tokens.append(re.escape(c))
                pos += 1

        regex_str = "^" + "".join(tokens) + "$"
        self._compiled_regex = re.compile(regex_str, re.IGNORECASE)

    def _compile_subpattern(self, inner: str) -> str:
        """Recursively compiles subpatterns inside brackets."""
        sub_tokens: List[str] = []
        pos = 0
        n = len(inner)
        while pos < n:
            if inner[pos].isspace():
                sub_tokens.append(r"\s+")
                while pos < n and inner[pos].isspace():
                    pos += 1
                continue
            if inner[pos] == "{":
                close = inner.find("}", pos)
                if close == -1:
                    close = n
                slot_def = inner[pos + 1 : close].strip()
                pos = close + 1
                if ":" in slot_def:
                    s_name, s_type = slot_def.split(":", 1)
                    s_name, s_type = s_name.strip(), s_type.strip()
                else:
                    s_name, s_type = slot_def, "expr"

                self._slots.append((s_name, s_type))
                if s_type == "ident":
                    sub_tokens.append(f"(?P<slot_{s_name}>[A-Za-z_]\\w*)")
                elif s_type == "int":
                    sub_tokens.append(f"(?P<slot_{s_name}>\\d+)")
                elif s_type == "float":
                    sub_tokens.append(f"(?P<slot_{s_name}>-?\\d+(?:\\.\\d+)?)")
                elif s_type == "str":
                    sub_tokens.append(f'(?P<slot_{s_name}>"(?:\\\\.|[^"\\\\])*"|\'(?:\\\\.|[^\'\\\\])*\')')
                else:
                    sub_tokens.append(f"(?P<slot_{s_name}>.+?)")
                continue

            if inner[pos] == "(":
                close = inner.find(")", pos)
                if close == -1:
                    close = n
                alt_inner = inner[pos + 1 : close].strip()
                pos = close + 1
                alt_name = f"alt_{len(self._alt_groups) + 1}"
                self._alt_groups.append(alt_inner)
                sub_tokens.append(f"(?P<{alt_name}>{alt_inner})")
                continue

            wm = re.match(r"^[A-Za-z0-9_]+", inner[pos:])
            if wm:
                w = wm.group(0)
                pos += len(w)
                sub_tokens.append(re.escape(w))
            else:
                sub_tokens.append(re.escape(inner[pos]))
                pos += 1

        return "".join(sub_tokens)

    def matches(self, line: str) -> bool:
        """Fast check whether this line matches the pattern."""
        if not self._compiled_regex:
            return False
        return self._compiled_regex.match(line.strip()) is not None


@dataclass
class PhraseMatchResult:
    """Result of successfully matching a line against a VerbSpec."""

    verb: VerbSpec
    args: Dict[str, Any]
    emitted: str


class EnglishPhraseMatcher:
    """Matches freeform English sentences against declared VerbSpec rules."""

    def __init__(self, verbs: Optional[List[VerbSpec]] = None):
        self.verbs: List[VerbSpec] = verbs or []

    def add_verb(self, verb: VerbSpec) -> None:
        self.verbs.append(verb)

    def match(self, line: str) -> Optional[PhraseMatchResult]:
        s = line.strip()
        for v in self.verbs:
            if not v._compiled_regex:
                continue
            m = v._compiled_regex.match(s)
            if not m:
                continue

            gd = m.groupdict()
            args: Dict[str, Any] = {}

            for s_name, _ in v._slots:
                val = gd.get(f"slot_{s_name}")
                args[s_name] = val.strip() if val is not None else None

            for i in range(1, len(v._alt_groups) + 1):
                val = gd.get(f"alt_{i}")
                args[f"_group{i}"] = val.strip() if val is not None else None

            # Format the emit template
            emitted = self._render_emit(v.emit, args)
            return PhraseMatchResult(verb=v, args=args, emitted=emitted)

        return None

    def _render_emit(self, template: str, args: Dict[str, Any]) -> str:
        """Renders the emit template with slot values and default fallbacks."""
        def repl(match):
            key_expr = match.group(1).strip()
            if "|" in key_expr:
                key, default = key_expr.split("|", 1)
                key, default = key.strip(), default.strip()
            else:
                key, default = key_expr, ""

            val = args.get(key)
            if val is not None and val != "":
                return str(val)
            return default

        return re.sub(r"\{([^}]+)\}", repl, template)


def suggest_near_miss_verb(line: str, verbs: List[VerbSpec]) -> Optional[str]:
    """Generates an advisory 'Did you mean?' suggestion for near-miss English lines."""
    line_clean = line.strip().lower()
    line_words = set(re.findall(r"\w+", line_clean))
    if not line_words:
        return None

    best_score = 0.0
    best_pattern = None

    for v in verbs:
        pat_clean = re.sub(r"\{[^}]+\}", "", v.pattern)
        pat_clean = re.sub(r"[\[\]\(\)\|]", " ", pat_clean).lower()
        pat_words = set(re.findall(r"\w+", pat_clean))
        if not pat_words:
            continue

        overlap = len(line_words & pat_words) / float(len(pat_words))
        seq_ratio = difflib.SequenceMatcher(None, line_clean, pat_clean).ratio()
        score = (overlap * 0.6) + (seq_ratio * 0.4)

        if score > best_score and score >= 0.4:
            best_score = score
            best_pattern = v.pattern

    if best_pattern:
        # Format a clean readable suggestion
        readable = re.sub(r"\[([^\]]+)\]", r"\1", best_pattern)
        readable = re.sub(r"\{([A-Za-z_]\w*)(?::\w+)?\}", r"<\1>", readable)
        return f"Did you mean: {readable}?"

    return None
