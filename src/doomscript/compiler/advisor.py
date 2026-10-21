"""
DidYouMeanAdvisor for DoomScript.
Provides actionable syntax suggestions when users write near-miss natural English statements.
"""

from __future__ import annotations
import re
from typing import Dict, List, Optional, Set, Tuple


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


class DidYouMeanAdvisor:
    """Matches failed or unparsed source lines against registered domain phrase templates."""

    @classmethod
    def _extract_words(cls, text: str) -> List[str]:
        cleaned = re.sub(r"[^a-zA-Z0-9_\s]", " ", text)
        return [w.lower() for w in cleaned.split() if len(w) > 1]

    @classmethod
    def find_suggestion(cls, line: str, active_domains: Optional[List[str]] = None) -> Optional[str]:
        """Calculates token overlap and returns the best matching signature if score >= threshold."""
        s = line.strip()
        if not s or s.startswith("#"):
            return None

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

            # Jaccard overlap on content words
            intersection = len(line_word_set.intersection(sig_word_set))
            union = len(line_word_set.union(sig_word_set))
            score = intersection / union if union > 0 else 0.0

            # Bonus for matching leading keywords
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
