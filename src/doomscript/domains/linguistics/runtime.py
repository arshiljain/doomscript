"""Linguistics Domain Runtime: Levenshtein distance, Soundex, Syllables, Flesch Readability, and TTR."""
import re
from typing import Dict, List, Any

def ling_levenshtein_distance(s1: str, s2: str) -> int:
    """Computes dynamic programming Levenshtein edit distance between two strings."""
    str1 = str(s1)
    str2 = str(s2)
    m, n = len(str1), len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if str1[i - 1] == str2[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[m][n]

def ling_soundex(word: str) -> str:
    """Computes American Soundex phonetic representation (Letter + 3 digits)."""
    cleaned = re.sub(r"[^A-Za-z]", "", str(word)).upper()
    if not cleaned:
        return ""
    code_map = {
        "B": "1", "F": "1", "P": "1", "V": "1",
        "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
        "D": "3", "T": "3",
        "L": "4",
        "M": "5", "N": "5",
        "R": "6"
    }
    first_letter = cleaned[0]
    tail = cleaned[1:]
    encoded = []
    prev_code = code_map.get(first_letter, "")
    for char in tail:
        code = code_map.get(char, "")
        if code:
            if code != prev_code:
                encoded.append(code)
            prev_code = code
        else:
            prev_code = ""
    # Pad or truncate to exactly 3 digits
    digits = "".join(encoded)[:3]
    return (first_letter + digits).ljust(4, "0")

def ling_count_syllables(word: str) -> int:
    """Estimates syllable count using vowel diphthong clustering and silent e deduction."""
    w = str(word).lower().strip()
    if not w:
        return 0
    w = re.sub(r"[^a-z]", "", w)
    if len(w) <= 3:
        return 1
    # Count vowel groups
    vowel_runs = len(re.findall(r"[aeiouy]+", w))
    # Deduct silent trailing e
    if w.endswith("e") and not w.endswith("le") and not w.endswith("ee"):
        vowel_runs -= 1
    return max(1, vowel_runs)

def ling_flesch_reading_ease(text: str) -> float:
    """Computes Flesch Reading Ease score: 206.835 - 1.015*(words/sentences) - 84.6*(syllables/words)."""
    t = str(text).strip()
    if not t:
        return 0.0
    sentences = max(1, len(re.split(r"[.!?]+", t)) - 1)
    words = re.findall(r"\b[A-Za-z]+\b", t)
    total_words = len(words)
    if total_words == 0:
        return 0.0
    total_syllables = sum(ling_count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (total_words / sentences) - 84.6 * (total_syllables / total_words)
    return round(score, 2)

def ling_type_token_ratio(text: str) -> float:
    """Computes Type-Token Ratio (TTR) lexical diversity: unique words / total words."""
    words = [w.lower() for w in re.findall(r"\b[A-Za-z]+\b", str(text))]
    if not words:
        return 0.0
    return round(len(set(words)) / len(words), 4)
