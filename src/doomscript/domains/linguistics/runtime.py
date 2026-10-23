"""Linguistics Domain Runtime: Phonetics, edit distances, readability metrics, syntactic CYK parsing, and HMM POS tagging."""
import math
import re
from typing import List, Dict, Any, Tuple, Optional, Set
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED CORE METRICS
# ============================================================================

def ling_levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein edit distance (insertions, deletions, substitutions)."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i-1] == s2[j-1] else 1
            dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1, dp[i-1][j-1] + cost)
    return dp[m][n]

def ling_jaro_winkler(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """Calculates Jaro-Winkler string similarity (0.0 to 1.0)."""
    if s1 == s2:
        return 1.0
    len1, len2 = len(s1), len(s2)
    if len1 == 0 or len2 == 0:
        return 0.0
    match_distance = max(len1, len2) // 2 - 1
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0
    transpositions = 0
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break
    if matches == 0:
        return 0.0
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    transpositions //= 2
    jaro = (matches / len1 + matches / len2 + (matches - transpositions) / matches) / 3.0
    prefix = 0
    for i in range(min(4, len1, len2)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
    return round(jaro + prefix * prefix_scale * (1.0 - jaro), 4)

def ling_soundex(word: str) -> str:
    """Computes American Soundex code for a word."""
    if not word:
        return "0000"
    w = word.upper()
    first_char = w[0]
    mapping = {
        'B': '1', 'F': '1', 'P': '1', 'V': '1',
        'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
        'D': '3', 'T': '3',
        'L': '4',
        'M': '5', 'N': '5',
        'R': '6'
    }
    encoded = [first_char]
    prev = mapping.get(first_char, '0')
    for char in w[1:]:
        digit = mapping.get(char, '0')
        if digit != '0' and digit != prev:
            encoded.append(digit)
        prev = digit
    code = "".join(encoded).replace('0', '')
    return (code + "0000")[:4]

def ling_count_syllables(word: str) -> int:
    """Heuristic English syllable counter using vowel groups and silent-e suppression."""
    w = word.lower().strip()
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    w = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', w)
    w = re.sub(r'^y', '', w)
    matches = re.findall(r'[aeiouy]{1,2}', w)
    return max(1, len(matches))

def ling_flesch_reading_ease(text: str) -> float:
    """Calculates Flesch Reading Ease score."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b[A-Za-z]+\b', text)
    if not sentences or not words:
        return 100.0
    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(ling_count_syllables(w) for w in words)
    asl = total_words / total_sentences
    asw = total_syllables / total_words
    ease = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(ease, 2)

def ling_gunning_fog(text: str) -> float:
    """Calculates Gunning Fog readability index."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b[A-Za-z]+\b', text)
    if not sentences or not words:
        return 0.0
    complex_words = [w for w in words if ling_count_syllables(w) >= 3]
    asl = len(words) / len(sentences)
    pct_complex = (len(complex_words) / len(words)) * 100.0
    fog = 0.4 * (asl + pct_complex)
    return round(fog, 2)

def ling_type_token_ratio(text: str) -> float:
    """Calculates lexical diversity (Type-Token Ratio TTR)."""
    words = re.findall(r'\b[A-Za-z]+\b', text.lower())
    if not words:
        return 0.0
    unique_types = len(set(words))
    return round(unique_types / len(words), 4)

# ============================================================================
# 2. ADVANCED PHONETICS & EDIT DISTANCES
# ============================================================================

def ling_damerau_levenshtein(s1: str, s2: str) -> int:
    """Computes Damerau-Levenshtein distance with insertions, deletions, substitutions, and transpositions."""
    d: Dict[Tuple[int, int], int] = {}
    len1, len2 = len(s1), len(s2)
    for i in range(-1, len1 + 1):
        d[(i, -1)] = i + 1
    for j in range(-1, len2 + 1):
        d[(-1, j)] = j + 1
    for i in range(len1):
        for j in range(len2):
            cost = 0 if s1[i] == s2[j] else 1
            d[(i, j)] = min(
                d[(i - 1, j)] + 1,        # deletion
                d[(i, j - 1)] + 1,        # insertion
                d[(i - 1, j - 1)] + cost  # substitution
            )
            if i > 0 and j > 0 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[(i - 2, j - 2)] + 1) # transposition
    return d[(len1 - 1, len2 - 1)]

def ling_metaphone(word: str) -> str:
    """Implements simplified Metaphone phonetic encoding for English words."""
    w = word.upper().strip()
    if not w:
        return ""
    # Transform initial silent letters
    if w.startswith(("KN", "GN", "PN", "AE", "WR")):
        w = w[1:]
    elif w.startswith("X"):
        w = "S" + w[1:]
    elif w.startswith("WH"):
        w = "W" + w[2:]
    res = []
    i = 0
    while i < len(w):
        ch = w[i]
        if ch in "AEIOU":
            if i == 0:
                res.append(ch)
        elif ch == "B":
            if not (i == len(w) - 1 and i > 0 and w[i-1] == "M"):
                res.append("B")
        elif ch == "C":
            if i < len(w) - 1 and w[i+1] in "EIY":
                res.append("S")
            elif i < len(w) - 1 and w[i+1] == "H":
                res.append("X")
                i += 1
            else:
                res.append("K")
        elif ch == "D":
            if i < len(w) - 2 and w[i+1:i+3] in ("GE", "GY", "GI"):
                res.append("J")
                i += 2
            else:
                res.append("T")
        elif ch == "F":
            res.append("F")
        elif ch == "G":
            if i < len(w) - 1 and w[i+1] == "H":
                i += 1
            elif i < len(w) - 1 and w[i+1] in "EIY":
                res.append("J")
            else:
                res.append("K")
        elif ch == "H":
            if i < len(w) - 1 and w[i+1] in "AEIOU" and (i == 0 or w[i-1] not in "CGPST"):
                res.append("H")
        elif ch in "JLM":
            res.append(ch)
        elif ch == "N":
            res.append("N")
        elif ch == "P":
            if i < len(w) - 1 and w[i+1] == "H":
                res.append("F")
                i += 1
            else:
                res.append("P")
        elif ch == "Q":
            res.append("K")
        elif ch == "R":
            res.append("R")
        elif ch == "S":
            if i < len(w) - 1 and w[i+1] == "H":
                res.append("X")
                i += 1
            else:
                res.append("S")
        elif ch == "T":
            if i < len(w) - 1 and w[i+1] == "H":
                res.append("0") # theta sound
                i += 1
            elif i < len(w) - 2 and w[i+1:i+3] in ("IA", "IO"):
                res.append("X")
                i += 2
            else:
                res.append("T")
        elif ch == "V":
            res.append("F")
        elif ch in "WY":
            if i < len(w) - 1 and w[i+1] in "AEIOU":
                res.append(ch)
        elif ch == "X":
            res.append("KS")
        elif ch == "Z":
            res.append("S")
        i += 1
    return "".join(res)

# ============================================================================
# 3. STEMMING (PORTER STEMMER RULES)
# ============================================================================

def ling_porter_stem(word: str) -> str:
    """Applies core Porter Stemming algorithm rules."""
    w = word.lower().strip()
    if len(w) <= 2:
        return w
    # Step 1a
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies"):
        w = w[:-2]
    elif not w.endswith("ss") and w.endswith("s"):
        w = w[:-1]
    # Step 1b
    if w.endswith("eed"):
        if len(w) > 4:
            w = w[:-1]
    elif w.endswith("ed") and any(c in "aeiou" for c in w[:-2]):
        w = w[:-2]
        if w.endswith("at") or w.endswith("bl") or w.endswith("iz"):
            w += "e"
    elif w.endswith("ing") and any(c in "aeiou" for c in w[:-3]):
        w = w[:-3]
        if w.endswith("at") or w.endswith("bl") or w.endswith("iz"):
            w += "e"
    # Step 1c
    if w.endswith("y") and len(w) > 2 and w[-2] not in "aeiou":
        w = w[:-1] + "i"
    # Step 2
    step2_suffixes = {
        "ational": "ate", "tional": "tion", "enci": "ence", "anci": "ance",
        "izer": "ize", "abli": "able", "alli": "al", "entli": "ent",
        "eli": "e", "ousli": "ous", "ization": "ize", "ation": "ate"
    }
    for suff, repl in step2_suffixes.items():
        if w.endswith(suff) and len(w) - len(suff) > 2:
            w = w[:-len(suff)] + repl
            break
    return w

# ============================================================================
# 4. PARSING & TAGGING (CYK & VITERBI HMM)
# ============================================================================

def ling_cyk_parse(words: List[str], grammar: Dict[str, List[Tuple[str, ...]]]) -> bool:
    """CYK parsing algorithm checking Context-Free Grammar membership in CNF."""
    n = len(words)
    if n == 0:
        return False
    table: Dict[Tuple[int, int], Set[str]] = {}
    for i in range(n):
        for j in range(n):
            table[(i, j)] = set()
    for i, w in enumerate(words):
        for lhs, rhs_list in grammar.items():
            for rhs in rhs_list:
                if len(rhs) == 1 and rhs[0] == w:
                    table[(0, i)].add(lhs)
    for l in range(2, n + 1):
        for s in range(n - l + 1):
            for p in range(1, l):
                left_cell = table[(p - 1, s)]
                right_cell = table[(l - p - 1, s + p)]
                for lhs, rhs_list in grammar.items():
                    for rhs in rhs_list:
                        if len(rhs) == 2 and rhs[0] in left_cell and rhs[1] in right_cell:
                            table[(l - 1, s)].add(lhs)
    return "S" in table[(n - 1, 0)]

def ling_viterbi_pos(words: List[str], states: List[str], start_p: Dict[str, float], trans_p: Dict[str, Dict[str, float]], emit_p: Dict[str, Dict[str, float]]) -> List[str]:
    """Viterbi decoding algorithm for HMM Part-of-Speech tagging."""
    if not words:
        return []
    V: List[Dict[str, float]] = [{}]
    path: Dict[str, List[str]] = {}
    for st in states:
        V[0][st] = start_p.get(st, 1e-6) * emit_p.get(st, {}).get(words[0], 1e-6)
        path[st] = [st]
    for t in range(1, len(words)):
        V.append({})
        new_path: Dict[str, List[str]] = {}
        for st in states:
            (prob, prev_st) = max(
                (V[t-1][p0] * trans_p.get(p0, {}).get(st, 1e-6) * emit_p.get(st, {}).get(words[t], 1e-6), p0)
                for p0 in states
            )
            V[t][st] = prob
            new_path[st] = path[prev_st] + [st]
        path = new_path
    (opt_prob, opt_st) = max((V[-1][st], st) for st in states)
    return path[opt_st]

# ============================================================================
# 5. READABILITY & SPEECH ERROR RATES
# ============================================================================

def ling_flesch_kincaid_grade(text: str) -> float:
    """Calculates Flesch-Kincaid Grade Level."""
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    words = re.findall(r'\b[A-Za-z]+\b', text)
    if not sentences or not words:
        return 0.0
    asl = len(words) / len(sentences)
    asw = sum(ling_count_syllables(w) for w in words) / len(words)
    grade = (0.39 * asl) + (11.8 * asw) - 15.59
    return round(grade, 2)

def ling_word_error_rate(reference: str, hypothesis: str) -> Dict[str, Any]:
    """Calculates Word Error Rate (WER) using Levenshtein distance on words."""
    r = reference.split()
    h = hypothesis.split()
    d = ling_levenshtein_distance(r, h)
    wer = d / len(r) if r else 0.0
    return {"wer": round(wer, 4), "substitutions_inserts_deletions": d, "ref_words": len(r), "hyp_words": len(h)}

# ============================================================================
# 6. DOMAIN RUNTIME
# ============================================================================

class LinguisticsRuntime(DomainRuntime):
    """Unified runtime bridge for the Linguistics computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def edit_distance(self, s1: str, s2: str) -> int:
        return ling_levenshtein_distance(s1, s2)
    def damerau(self, s1: str, s2: str) -> int:
        return ling_damerau_levenshtein(s1, s2)
    def jaro_winkler(self, s1: str, s2: str) -> float:
        return ling_jaro_winkler(s1, s2)
    def soundex(self, word: str) -> str:
        return ling_soundex(word)
    def metaphone(self, word: str) -> str:
        return ling_metaphone(word)
    def stem(self, word: str) -> str:
        return ling_porter_stem(word)
    def syllables(self, word: str) -> int:
        return ling_count_syllables(word)
    def flesch(self, text: str) -> float:
        return ling_flesch_reading_ease(text)
    def fk_grade(self, text: str) -> float:
        return ling_flesch_kincaid_grade(text)
    def fog(self, text: str) -> float:
        return ling_gunning_fog(text)
    def ttr(self, text: str) -> float:
        return ling_type_token_ratio(text)
    def cyk(self, words: List[str], grammar: Dict[str, List[Tuple[str, ...]]]) -> bool:
        return ling_cyk_parse(words, grammar)
    def pos_tag(self, words: List[str], states: List[str], start_p: Dict[str, float], trans_p: Dict[str, Dict[str, float]], emit_p: Dict[str, Dict[str, float]]) -> List[str]:
        return ling_viterbi_pos(words, states, start_p, trans_p, emit_p)
    def wer(self, ref: str, hyp: str) -> Dict[str, Any]:
        return ling_word_error_rate(ref, hyp)
