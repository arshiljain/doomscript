"""
DoomScript Source Code Formatter (doom fmt)
Formats DoomScript code to canonical, readable English style:
- Consistent 4-space indentation
- Canonical verbs and comparisons
- Strips filler words (please, kindly, just)
- Preserves comments and string literals
"""

import re
from typing import List
from doomscript.grammar.phrases import (
    mask_strings,
    unmask_strings,
    split_comment,
    LEADING_FILLERS,
    VERB_SYNONYMS,
    COMPARISON_SYNONYMS,
)


def format_code(source: str) -> str:
    """Formats DoomScript code into canonical style."""
    lines = source.splitlines()
    formatted_lines: List[str] = []

    for raw_line in lines:
        if not raw_line.strip():
            formatted_lines.append("")
            continue

        indent_len = len(raw_line) - len(raw_line.lstrip(" "))
        # Normalize indentation to nearest 4 spaces
        level = round(indent_len / 4) if indent_len > 0 else 0
        indent = "    " * level

        code, comment = split_comment(raw_line.strip())
        if not code:
            formatted_lines.append(indent + comment)
            continue

        masked, strings = mask_strings(code)

        # 1. Strip leading polite fillers
        for filler in LEADING_FILLERS:
            pat = re.compile(rf"^{filler}\s+", re.IGNORECASE)
            if pat.match(masked):
                masked = pat.sub("", masked)
                break

        # 2. Canonicalize verbs
        for syn, canonical in VERB_SYNONYMS.items():
            pat = re.compile(rf"^{syn}\b", re.IGNORECASE)
            if pat.match(masked):
                masked = pat.sub(canonical, masked)
                break

        # 3. Canonicalize comparisons
        for syn, canonical in COMPARISON_SYNONYMS:
            pat = re.compile(rf"\b{re.escape(syn)}\b", re.IGNORECASE)
            masked = pat.sub(canonical, masked)

        # 4. Spacing around operators and colons
        masked = re.sub(r"\s*:\s*$", ":", masked)
        masked = re.sub(r"\s*,\s*", ", ", masked)

        result_code = unmask_strings(masked, strings)
        if comment:
            formatted_lines.append(f"{indent}{result_code}  {comment}")
        else:
            formatted_lines.append(f"{indent}{result_code}")

    # Remove trailing blank lines
    while formatted_lines and not formatted_lines[-1].strip():
        formatted_lines.pop()

    return "\n".join(formatted_lines) + "\n"
