"""
DidYouMeanAdvisor for DoomScript.
Provides actionable syntax suggestions when users write near-miss natural English statements
or encounter token-level typos in keywords, built-ins, and variables.
"""

from __future__ import annotations
import difflib
import re
from typing import Dict, List, Optional, Set, Tuple
from doomscript.grammar.phrases import (
    mask_strings,
    unmask_strings,
    CORE_COMMAND_VERBS,
    VERB_SYNONYMS,
)


# Canonical signatures catalog for common domains
DOMAIN_SIGNATURES: Dict[str, List[str]] = {
    "finance": [
        "price (call|put) option with spot <spot> strike <strike> expiry <expiry> rate <rate> vol <vol> into <target>",
        "calculate option greeks with spot <spot> strike <strike> expiry <expiry> rate <rate> vol <vol> into <target>",
        "price american (call|put) option with spot <spot> strike <strike> expiry <expiry> rate <rate> vol <vol> steps <n> into <target>",
    ],
    "ml": [
        "train knn classifier with features <X> and labels <y> and neighbors <k> into <target>",
        "predict classes for <data> with model <model> into <target>",
        "calculate f1 score between <y_true> and <y_pred> into <target>",
        "calculate roc auc score between <y_true> and <y_pred> into <target>",
    ],
    "sim": [
        "simulate markov chain with transitions <matrix> and steps <n> from state <start> into <target>",
        "simulate monte carlo with paths <n> and steps <s> into <target>",
    ],
    "geo": [
        "calculate haversine distance from <p1> to <p2> into <target>",
        "calculate convex hull of <coords> into <target>",
    ],
    "viz": [
        "chart <scatter|line|bar> of <data> with x <col> and y <col> titled <title> into <target>",
        "save chart <plot> to <filepath>",
    ],
    "audio": [
        "generate (sine|square|sawtooth) wave with frequency <f> and duration <d> into <target>",
        "apply (lowpass|highpass) filter to <signal> with cutoff <fc> into <target>",
        "compress dynamic range <samples> with threshold <th_db> and ratio <r> into <target>",
    ],
    "db": [
        "connect to database <db_path> into <db_var>",
        "find all <table_name> in <db_var> where <condition> into <target>",
        "execute sql <query> on <db_var> into <target>",
    ],
    "cloud": [
        "connect to bucket <bucket_name> into <bucket_var>",
        "write text <payload> to object <path> in <bucket_var>",
        "generate presigned put url for <path> in <bucket_var> with expiry <seconds> into <target>",
    ],
    "compression": [
        "compress lzma text <text> into <target>",
        "decompress lzma record <record> into <target>",
    ],
    "signals": [
        "compute fft of <signal> into <target>",
        "compute ifft of <spectrum> into <target>",
    ],
    "chem": [
        "balance reaction <equation> into <target>",
        "calculate formula weight of <formula> into <target>",
    ],
}

CORE_KEYWORDS: Set[str] = {
    "say", "show", "set", "to", "let", "put", "into", "from", "with", "by",
    "if", "else", "elif", "unless", "repeat", "times", "time", "while", "until",
    "for", "each", "in", "where", "try", "attempt", "fails", "always", "match",
    "when", "return", "verify", "otherwise", "require", "ensure", "stop", "skip",
    "call", "class", "define", "ask", "choice", "number", "boolean", "read",
    "write", "append", "copy", "delete", "file", "create", "directory", "list",
    "files", "split", "join", "replace", "uppercase", "lowercase", "trim",
    "round", "clamp", "fetch", "json", "download", "roll", "pick", "random",
    "shuffle", "length", "count", "sum", "average", "highest", "lowest",
    "maximum", "minimum", "first", "last", "reversed", "reverse", "sorted",
    "sort", "unique", "true", "false", "none", "nothing", "not", "and", "or",
    "is", "starts", "ends", "between", "contains", "empty", "sqrt", "absolute",
    "value", "today", "now", "constructor", "init", "initialize", "setup",
    "start", "base", "super", "my", "its", "make", "squares", "words", "lines", "item", "items", "keep", "only", "take", "drop", "every", "any", "has", "have", "had", "joined", "equals", "equal", "over", "under", "above", "below", "greater", "less", "than", "at", "least", "most", "qualifying"
}

BUILTIN_FUNCS: Set[str] = {
    "len", "print", "range", "range_inclusive", "abs", "min", "max", "sum",
    "int", "float", "str", "bool", "list", "dict", "set", "tuple", "open",
    "input", "all", "any", "sorted", "reversed", "round"
}

DOMAIN_VOCABULARY: Set[str] = {
    "price", "option", "spot", "strike", "expiry", "rate", "vol", "call", "put",
    "greeks", "american", "steps", "train", "knn", "classifier", "features", "labels",
    "neighbors", "model", "predict", "classes", "f1", "roc", "auc", "score",
    "simulate", "markov", "chain", "transitions", "matrix", "monte", "carlo", "paths",
    "haversine", "distance", "convex", "hull", "coords", "chart", "scatter", "line",
    "bar", "titled", "save", "plot", "wave", "frequency", "duration", "filter", "lowpass",
    "highpass", "cutoff", "compress", "dynamic", "threshold", "ratio", "connect", "database",
    "bucket", "lzma", "fft", "ifft", "reaction", "formula", "weight"
}


def extract_known_variables(source: str) -> Set[str]:
    """Extracts variable names and identifiers defined across prior source lines."""
    if not source:
        return set()
    vars_found: Set[str] = set()
    patterns = [
        re.compile(r"^\s*set\s+([A-Za-z_]\w*)\s+to\b", re.IGNORECASE),
        re.compile(r"^\s*([A-Za-z_]\w*)\s*=(?!=)"),
        re.compile(r"^\s*([A-Za-z_]\w*)\s*(?:\+=|-=|\*=|/=|//=)"),
        re.compile(r"^\s*increase\s+([A-Za-z_]\w*)\s+by\b", re.IGNORECASE),
        re.compile(r"^\s*decrease\s+([A-Za-z_]\w*)\s+by\b", re.IGNORECASE),
        re.compile(r"\binto\s+([A-Za-z_]\w*)\s*$", re.IGNORECASE),
        re.compile(r"\bfor\s+(?:each\s+)?([A-Za-z_]\w*)\s+in\b", re.IGNORECASE),
        re.compile(r"^\s*to\s+[A-Za-z_]\w*\s+with\s+([^:]+):", re.IGNORECASE),
        re.compile(r"^\s*class\s+([A-Za-z_]\w*)", re.IGNORECASE),
        re.compile(r"^\s*define\s+(?:a|an)\s+([A-Za-z_]\w*)", re.IGNORECASE),
    ]
    for line in source.splitlines():
        line_clean = line.split("#")[0].strip()
        if not line_clean:
            continue
        for pat in patterns:
            for match in pat.finditer(line_clean):
                val = match.group(1).strip()
                for part in val.split(","):
                    p = part.strip().split("=")[0].strip()
                    if p and re.match(r"^[A-Za-z_]\w*$", p) and p.lower() not in ("it", "that", "self"):
                        vars_found.add(p)
    return vars_found


class DidYouMeanAdvisor:
    """Matches failed or unparsed source lines against registered domain phrase templates and token typos."""

    @classmethod
    def _extract_words(cls, text: str) -> List[str]:
        cleaned = re.sub(r"[^a-zA-Z0-9_\s]", " ", text)
        return [w.lower() for w in cleaned.split() if len(w) > 1]

    @classmethod
    def find_token_suggestion(
        cls,
        line: str,
        known_variables: Optional[Set[str]] = None,
        failing_token: Optional[str] = None,
        col: Optional[int] = None,
    ) -> Optional[str]:
        """
        Token-level correction for syntax errors.
        Compares failing token and surrounding tokens against keywords, built-ins,
        and known variables using difflib with ~0.75 cutoff.
        Preserves string contents untouched by masking before inspection.
        Returns the full reconstructed line.
        """
        masked_line, strings = mask_strings(line)
        clean = masked_line.strip()
        if not clean or clean.startswith("#"):
            return None

        # Build vocabulary
        vocab_set = set(CORE_KEYWORDS) | set(BUILTIN_FUNCS) | set(DOMAIN_VOCABULARY)
        if known_variables:
            vocab_set |= set(known_variables)

        vocab_map = {w.lower(): w for w in vocab_set}
        vocab_list = list(vocab_map.keys())

        # Extract words and their spans from masked_line, strictly ignoring placeholder strings
        word_spans = [
            (m.group(0), m.start(), m.end())
            for m in re.finditer(r"\b[A-Za-z_]\w*\b", masked_line)
            if not m.group(0).startswith("__STR_LITERAL_")
        ]
        if not word_spans:
            return None

        target_indices: List[int] = []
        if col is not None:
            # 1-based col: find token closest to or covering col
            for idx, (w, start, end) in enumerate(word_spans):
                if start <= (col - 1) <= end or (idx > 0 and word_spans[idx - 1][1] <= (col - 1) <= end):
                    target_indices.append(idx)
                    if idx > 0:
                        target_indices.append(idx - 1)
                    break

        if failing_token:
            ft_clean = failing_token.strip("'\"")
            for idx, (w, start, end) in enumerate(word_spans):
                if w.lower() == ft_clean.lower() and idx not in target_indices:
                    target_indices.append(idx)
                    if idx > 0 and (idx - 1) not in target_indices:
                        target_indices.append(idx - 1)

        ordered_indices: List[int] = []
        for idx in target_indices:
            if idx not in ordered_indices and 0 <= idx < len(word_spans):
                ordered_indices.append(idx)
        for idx in range(len(word_spans)):
            if idx not in ordered_indices:
                ordered_indices.append(idx)

        candidate_verbs = list(set(CORE_COMMAND_VERBS) | set(VERB_SYNONYMS.keys()) | {"print", "println"})

        # Check candidate tokens
        corrections: List[Tuple[int, int, str]] = []
        seen_words = set()
        for idx in ordered_indices:
            word, start, end = word_spans[idx]
            word_lower = word.lower()

            if word_lower.startswith("__str_literal_"):
                continue

            # First token special check: command verb typos
            if idx == 0:
                if word_lower in {"sya", "sy"}:
                    corrections.append((start, end, "Say" if word.istitle() else "say"))
                    seen_words.add(word_lower)
                    continue
                if word_lower in {"prnt", "prntln", "print", "println"}:
                    corrections.append((start, end, "Say" if word.istitle() else "say"))
                    seen_words.add(word_lower)
                    continue
                if word_lower not in vocab_map and word_lower not in seen_words:
                    close_verbs = difflib.get_close_matches(word_lower, candidate_verbs, n=1, cutoff=0.6)
                    if close_verbs:
                        v_match = close_verbs[0]
                        canon_v = VERB_SYNONYMS.get(v_match, v_match)
                        if word.istitle():
                            canon_v = canon_v.capitalize()
                        corrections.append((start, end, canon_v))
                        seen_words.add(word_lower)
                        continue

            if word_lower in vocab_map or word_lower in seen_words:
                continue
            seen_words.add(word_lower)

            matches = difflib.get_close_matches(word_lower, vocab_list, n=1, cutoff=0.74)
            if matches:
                matched_cand = matches[0]
                replacement = vocab_map[matched_cand]
                if word.istitle() and not replacement.startswith("_"):
                    replacement = replacement.capitalize()
                corrections.append((start, end, replacement))

        if corrections:
            corrections.sort(key=lambda c: c[0], reverse=True)
            res = masked_line
            for start, end, rep in corrections:
                res = res[:start] + rep + res[end:]
            return unmask_strings(res, strings)

        return None

    @classmethod
    def _is_valid_syntax(cls, line: str) -> bool:
        try:
            from doomscript.grammar.phrases import normalize
            from doomscript.compiler.engine import get_parser
            norm = normalize(line.strip())
            if not norm.endswith("\n"):
                norm += "\n"
            get_parser().parse(norm)
            return True
        except Exception:
            return False

    @classmethod
    def find_suggestion(
        cls,
        line: str,
        active_domains: Optional[List[str]] = None,
        source: Optional[str] = None,
        failing_token: Optional[str] = None,
        col: Optional[int] = None,
    ) -> Optional[str]:
        """Calculates token overlap and returns the best matching signature or token-corrected line."""
        s = line.strip()
        if not s or s.startswith("#"):
            return None

        # 1. First check token-level typo correction
        known_vars = extract_known_variables(source) if source else None
        token_sug = cls.find_token_suggestion(
            line,
            known_variables=known_vars,
            failing_token=failing_token,
            col=col,
        )
        if token_sug:
            if cls._is_valid_syntax(token_sug):
                return token_sug

        # 2. Domain signature matching
        line_words = cls._extract_words(s)
        if not line_words:
            return None
        line_word_set = set(line_words)

        candidates: List[str] = []
        domains_to_check = active_domains if active_domains else list(DOMAIN_SIGNATURES.keys())
        for dom in domains_to_check:
            dom_low = dom.lower()
            if dom_low in DOMAIN_SIGNATURES:
                candidates.extend(DOMAIN_SIGNATURES[dom_low])

        best_score = 0.0
        best_sig: Optional[str] = None

        for sig in candidates:
            sig_words = cls._extract_words(sig)
            if not sig_words:
                continue
            sig_word_set = set(sig_words)

            intersection = len(line_word_set.intersection(sig_word_set))
            union = len(line_word_set.union(sig_word_set))
            score = intersection / union if union > 0 else 0.0

            if len(line_words) >= 2 and len(sig_words) >= 2:
                if line_words[0] == sig_words[0] and line_words[1] == sig_words[1]:
                    score += 0.35
            elif len(line_words) >= 1 and len(sig_words) >= 1:
                if line_words[0] == sig_words[0]:
                    score += 0.20

            if score > best_score:
                best_score = score
                best_sig = sig

        if best_score >= 0.35 and best_sig is not None:
            return best_sig

        return None
