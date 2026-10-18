"""
Dynamic programming and fundamental research algorithms.
"""

from typing import List, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes Levenshtein edit distance between strings s1 and s2 (insertions, deletions, substitutions).
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        c1 = s1[i - 1]
        for j in range(1, n + 1):
            c2 = s2[j - 1]
            if c1 == c2:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1],  # substitution
                )

    return dp[m][n]


def longest_common_subsequence(s1: str, s2: str) -> str:
    """
    Computes the Longest Common Subsequence between s1 and s2 and returns the reconstructed string.
    """
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # Reconstruct LCS deterministically
    chars = []
    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            chars.append(s1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    chars.reverse()
    return "".join(chars)


def knapsack_01(
    weights: List[int],
    values: List[float],
    capacity: int,
) -> Tuple[float, List[int]]:
    """
    Solves the 0/1 Knapsack problem using dynamic programming.
    Returns (maximum_value, selected_item_indices).
    """
    n = len(weights)
    if len(values) != n:
        raise ValueError("Weights and values must have the same length.")
    if capacity < 0:
        raise ValueError("Capacity must be non-negative.")

    cap = int(capacity)
    dp = [[0.0] * (cap + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w = int(weights[i - 1])
        v = float(values[i - 1])
        for c in range(cap + 1):
            if w <= c:
                dp[i][c] = max(dp[i - 1][c], dp[i - 1][c - w] + v)
            else:
                dp[i][c] = dp[i - 1][c]

    # Reconstruct selected items
    selected = []
    c = cap
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            selected.append(i - 1)
            c -= int(weights[i - 1])

    selected.reverse()
    return (dp[n][cap], selected)
