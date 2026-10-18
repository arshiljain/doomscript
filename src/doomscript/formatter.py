"""
DoomScript Source Code Formatter (doom fmt)
Formats DoomScript code to canonical, readable English style:
- Structure-aware 4-space indentation with strict validation
- Canonical assignment (score = 100), verbs (say, return), and comparisons
- Strips filler words (please, kindly, just)
- Preserves comments, string literals, and program semantics
- Reports malformed indentation via DoomIndentationError
"""

import re
from typing import List, Tuple
from doomscript.exceptions import DoomIndentationError
from doomscript.grammar.phrases import (
    mask_strings,
    unmask_strings,
    split_comment,
    LEADING_FILLERS,
    VERB_SYNONYMS,
    COMPARISON_SYNONYMS,
)

# Block header keywords that introduce an indented block
BLOCK_HEADER_RE = re.compile(
    r"^(?:"
    r"if\b|"
    r"unless\b|"
    r"elif\b|"
    r"else\b|"
    r"otherwise\b|"
    r"try\b|"
    r"attempt\b|"
    r"if\s+(?:it|that)\s+fails\b|"
    r"always\b|"
    r"repeat\b|"
    r"while\b|"
    r"until\b|"
    r"as\s+long\s+as\b|"
    r"for\s+(?:each\s+)?[A-Za-z_]\w*\s+in\b|"
    r"(?:to|how\s+to|define|function)\s+[A-Za-z_]\w*|"
    r"match\b|"
    r"when\b|"
    r"test\b|"
    r"on\s+(?:get|post|put|delete|patch)\b|"
    r"route\b"
    r")",
    re.IGNORECASE,
)

# Comparison phrases sorted by descending length to prevent prefix shadowing
SORTED_COMPARISONS = sorted(COMPARISON_SYNONYMS, key=lambda item: len(item[0]), reverse=True)

# Assignment alias normalization patterns (applied at statement level)
ASSIGNMENT_ALIAS_PATTERNS: List[Tuple[re.Pattern, str]] = [
    (re.compile(r"^\s*set\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+to\s+(.+)$", re.IGNORECASE), r"\1 = \2"),
    (re.compile(r"^\s*let\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+be\s+(.+)$", re.IGNORECASE), r"\1 = \2"),
    (re.compile(r"^\s*put\s+(.+?)\s+into\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)$", re.IGNORECASE), r"\2 = \1"),
    (re.compile(r"^\s*assign\s+(.+?)\s+to\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)$", re.IGNORECASE), r"\2 = \1"),
    (re.compile(r"^\s*store\s+(.+?)\s+(?:in|into)\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)$", re.IGNORECASE), r"\2 = \1"),
    (re.compile(r"^\s*save\s+(.+?)\s+as\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)$", re.IGNORECASE), r"\2 = \1"),
    (re.compile(r"^\s*initialize\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+(?:to|with)\s+(.+)$", re.IGNORECASE), r"\1 = \2"),
    (re.compile(r"^\s*reset\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+to\s+(.+)$", re.IGNORECASE), r"\1 = \2"),
    (re.compile(r"^\s*make\s+([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+be\s+(.+)$", re.IGNORECASE), r"\1 = \2"),
]

# Legacy assignment deprecation pattern: 'score is 100' -> 'score = 100'
# Must not match comparison predicates such as 'x is positive', 'x is empty', 'x is greater than 5'
LEGACY_IS_ASSIGN_RE = re.compile(
    r"^(?!result\b)(?!the\s+result\b)([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s+is\s+"
    r"(?!even\b|odd\b|positive\b|negative\b|zero\b|blank\b|empty\b|"
    r"a\s+(?:number|string|text|boolean|bool|list|record|dictionary|dict|multiple\s+of)\b|"
    r"an\s+(?:empty\b|integer\b)|not\b|between\b|"
    r"one\s+of\b|inside\b|in\b|divisible\b|greater\b|less\b|equal\b|more\b|smaller\b|above\b|"
    r"below\b|at\s+least\b|at\s+most\b|no\s+more\b|no\s+less\b)(.+)$",
    re.IGNORECASE,
)


def format_single_statement(masked: str) -> str:
    """Formats an individual atomic statement (with string literals already masked)."""
    text = masked.strip()
    if not text:
        return ""

    # 1. Strip leading polite fillers
    for filler in LEADING_FILLERS:
        pat = re.compile(rf"^{filler}\s+", re.IGNORECASE)
        if pat.match(text):
            text = pat.sub("", text)
            break

    # 2. Canonicalize verbs
    if re.match(r"^display\s+colored\b", text, re.IGNORECASE):
        pass  # Preserve display colored
    elif re.match(r"^display\b", text, re.IGNORECASE):
        text = re.sub(r"^display\b", "say", text, flags=re.IGNORECASE)
    else:
        for syn, canonical in VERB_SYNONYMS.items():
            pat = re.compile(rf"^{syn}\b", re.IGNORECASE)
            if pat.match(text):
                text = pat.sub(canonical, text)
                break

    # 3. Canonicalize assignment aliases to 'target = expr'
    for pat, repl in ASSIGNMENT_ALIAS_PATTERNS:
        if pat.match(text):
            text = pat.sub(repl, text)
            break

    # 4. Canonicalize legacy assignment alias 'target is expr' -> 'target = expr'
    legacy_m = LEGACY_IS_ASSIGN_RE.match(text)
    if legacy_m:
        text = f"{legacy_m.group(1)} = {legacy_m.group(2)}"

    # 5. Canonicalize comparisons
    for syn, canonical in SORTED_COMPARISONS:
        pat = re.compile(rf"\b{re.escape(syn)}\b", re.IGNORECASE)
        text = pat.sub(canonical, text)

    # 6. Spacing around assignment operator
    text = re.sub(r"^([A-Za-z_]\w*(?:'s\s+[A-Za-z_]\w*)?)\s*=\s*(?!=\s*)(.+)$", r"\1 = \2", text)

    # 7. Strip sentence-ending period on simple statements (e.g. 'say "hello".' -> 'say "hello"')
    # Protect decimal numbers (e.g. 3.14) and ellipsis (...)
    if not text.endswith(":") and not BLOCK_HEADER_RE.match(text):
        text = re.sub(r"(?<!\d)\.\s*$", "", text)

    # 8. Canonical comma spacing
    text = re.sub(r"\s*,\s*", ", ", text)

    return text.strip()


def format_statement(code: str) -> str:
    """Formats a statement or statement chain (handling strings and 'and then')."""
    masked, strings = mask_strings(code)

    if re.search(r"\s+and\s+then\s+", masked, re.IGNORECASE):
        parts = re.split(r"\s+and\s+then\s+", masked, flags=re.IGNORECASE)
        formatted_parts = [format_single_statement(p) for p in parts if p.strip()]
        masked = " and then ".join(formatted_parts)
    else:
        masked = format_single_statement(masked)

    # Format block colon spacing
    masked = re.sub(r"\s*:\s*$", ":", masked)

    return unmask_strings(masked, strings)


def format_code(source: str) -> str:
    """
    Formats DoomScript code into canonical style.
    Replaces arbitrary or 2-space indentation with canonical structure-aware 4-space blocks.
    Strictly validates indentation hierarchy and reports malformed indentation via DoomIndentationError.
    Idempotent: format_code(format_code(src)) == format_code(src).
    """
    if not source.strip():
        return ""

    lines = source.splitlines()
    formatted_lines: List[str] = []

    indent_stack: List[int] = [0]
    expecting_block = False
    header_line_num = 0
    header_line_str = ""
    paren_depth = 0

    for line_num, raw_line in enumerate(lines, start=1):
        if not raw_line.strip():
            formatted_lines.append("")
            continue

        raw_indent = len(raw_line) - len(raw_line.lstrip(" "))
        raw_code, comment = split_comment(raw_line.strip())

        # Comment-only line
        if not raw_code:
            if raw_indent == 0:
                formatted_lines.append(comment)
            elif expecting_block:
                # Indented comment immediately following a block header
                indent_str = "    " * len(indent_stack)
                formatted_lines.append(f"{indent_str}{comment}")
            else:
                # Indented comment inside an active block
                cur_level = len(indent_stack) - 1
                for idx in range(len(indent_stack) - 1, -1, -1):
                    if raw_indent >= indent_stack[idx]:
                        cur_level = idx
                        break
                indent_str = "    " * cur_level
                formatted_lines.append(f"{indent_str}{comment}")
            continue

        # Non-comment line containing executable code
        if paren_depth > 0:
            # Inside multi-line bracketed expression; maintain block indent + 4
            cur_level = len(indent_stack)
            indent_str = "    " * cur_level
            masked_temp, _ = mask_strings(raw_code)
            paren_depth += (
                masked_temp.count("(") + masked_temp.count("[") + masked_temp.count("{")
                - masked_temp.count(")") - masked_temp.count("]") - masked_temp.count("}")
            )
            formatted_code = format_statement(raw_code)
            if comment:
                formatted_lines.append(f"{indent_str}{formatted_code}  {comment}")
            else:
                formatted_lines.append(f"{indent_str}{formatted_code}")
            continue

        if expecting_block:
            if raw_indent <= indent_stack[-1]:
                expected_indent = 4 * len(indent_stack)
                raise DoomIndentationError(
                    f"Expected an indented block after '{header_line_str}' on line {header_line_num}",
                    line=line_num,
                    column=raw_indent + 1,
                    source_line=raw_line,
                    suggestion=f"indent this line by {expected_indent} spaces",
                )
            indent_stack.append(raw_indent)
            expecting_block = False
            cur_level = len(indent_stack) - 1
        else:
            if raw_indent == indent_stack[-1]:
                cur_level = len(indent_stack) - 1
            elif raw_indent > indent_stack[-1]:
                raise DoomIndentationError(
                    f"Unexpected indent on line {line_num}",
                    line=line_num,
                    column=raw_indent + 1,
                    source_line=raw_line,
                    suggestion="remove unexpected leading indentation",
                )
            else:
                if raw_indent not in indent_stack:
                    valid_levels = ", ".join(str(x) for x in indent_stack)
                    raise DoomIndentationError(
                        f"Unindent does not match any outer indentation level on line {line_num}",
                        line=line_num,
                        column=raw_indent + 1,
                        source_line=raw_line,
                        suggestion=f"align with an outer indentation level ({valid_levels})",
                    )
                while indent_stack and indent_stack[-1] > raw_indent:
                    indent_stack.pop()
                cur_level = len(indent_stack) - 1

        formatted_code = format_statement(raw_code)

        # Check if line initiates a block
        masked_chk, _ = mask_strings(formatted_code)
        is_header = BLOCK_HEADER_RE.match(masked_chk) is not None or masked_chk.endswith(":")
        if is_header:
            if not masked_chk.endswith(":"):
                formatted_code += ":"
            expecting_block = True
            header_line_num = line_num
            header_line_str = raw_line.strip()
        else:
            expecting_block = False

        # Update bracket depth
        masked_paren, _ = mask_strings(raw_code)
        paren_depth += (
            masked_paren.count("(") + masked_paren.count("[") + masked_paren.count("{")
            - masked_paren.count(")") - masked_paren.count("]") - masked_paren.count("}")
        )

        indent_str = "    " * cur_level
        if comment:
            formatted_lines.append(f"{indent_str}{formatted_code}  {comment}")
        else:
            formatted_lines.append(f"{indent_str}{formatted_code}")

    if expecting_block:
        raise DoomIndentationError(
            f"Expected an indented block after '{header_line_str}' on line {header_line_num}",
            line=header_line_num,
            source_line=header_line_str,
            suggestion="add an indented block of statements",
        )

    while formatted_lines and not formatted_lines[-1].strip():
        formatted_lines.pop()

    if not formatted_lines:
        return ""

    return "\n".join(formatted_lines) + "\n"
