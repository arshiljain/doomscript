"""Comprehensive tests for the 13 Additional Algorithmic Powers in DoomScript DSA Extension."""

import pytest
from doomscript.compiler.engine import execute


def test_dsa_trie():
    """1. Trie (Prefix Tree) Engine: LC 208."""
    source = """use dsa

create trie into t
insert word "apple" into trie t
insert word "app" into trie t

check if trie t contains word "apple" into has_apple
check if trie t contains word "appl" into has_appl
check if trie t starts with prefix "app" into starts_app
check if trie t starts with prefix "bat" into starts_bat

all words in trie t starting with "app" into app_words
"""
    env = execute(source)
    assert env["has_apple"] is True
    assert env["has_appl"] is False
    assert env["starts_app"] is True
    assert env["starts_bat"] is False
    assert sorted(env["app_words"]) == ["app", "apple"]


def test_dsa_disjoint_set():
    """2. Disjoint Set Union (DSU / Union-Find): LC 547."""
    source = """use dsa

create disjoint set with size 5 into dsu
union 0 and 1 in disjoint set dsu
union 1 and 2 in disjoint set dsu

check if 0 and 2 are connected in disjoint set dsu into conn_0_2
check if 0 and 3 are connected in disjoint set dsu into conn_0_3
count of disjoint sets in dsu into num_sets
"""
    env = execute(source)
    assert env["conn_0_2"] is True
    assert env["conn_0_3"] is False
    assert env["num_sets"] == 3


def test_dsa_binary_tree():
    """3. Binary Tree Construction, Traversal, and Inversion: LC 102, LC 226."""
    source = """use dsa

build binary tree from [3, 9, 20, null, null, 15, 7] into tree
level order traversal of tree tree into levels
inorder traversal of tree tree into in_order
maximum depth of tree tree into depth

invert binary tree tree
level order traversal of tree tree into inverted_levels
"""
    env = execute(source)
    assert env["levels"] == [[3], [9, 20], [15, 7]]
    assert env["in_order"] == [9, 3, 15, 20, 7]
    assert env["depth"] == 3
    assert env["inverted_levels"] == [[3], [20, 9], [7, 15]]


def test_dsa_binary_search_and_bounds():
    """4. Binary Search, Lower Bound, Upper Bound: LC 704, LC 34."""
    source = """use dsa

nums = [1, 3, 5, 7, 9, 11]
binary search target 7 in nums into idx
lower bound of 6 in nums into lb
upper bound of 7 in nums into ub
"""
    env = execute(source)
    assert env["idx"] == 3
    assert env["lb"] == 3
    assert env["ub"] == 4


def test_dsa_monotonic_stack():
    """5. Monotonic Stack Engine: LC 496, LC 739."""
    source = """use dsa

arr = [2, 1, 5, 3]
next greater elements in arr into nge
next smaller elements in arr into nse
"""
    env = execute(source)
    assert env["nge"] == [5, 5, -1, -1]
    assert env["nse"] == [1, -1, 3, -1]


def test_dsa_combinatorics():
    """6. Combinatorics & Power Set: LC 46, LC 77, LC 78."""
    source = """use dsa

items = [1, 2, 3]
all permutations of items into perms
all combinations of items with size 2 into combs
power set of items into pset
"""
    env = execute(source)
    assert len(env["perms"]) == 6
    assert len(env["combs"]) == 3
    assert len(env["pset"]) == 8


def test_dsa_linked_list():
    """7. Linked List Engine: LC 206, LC 141."""
    source = """use dsa

build linked list from [1, 2, 3, 4] into head
reverse linked list head into rev
convert linked list rev to list into rev_list
check if linked list rev has cycle into has_cycle
"""
    env = execute(source)
    assert env["rev_list"] == [4, 3, 2, 1]
    assert env["has_cycle"] is False


def test_dsa_kadane_max_subarray():
    """8. Kadane's Maximum Subarray: LC 53."""
    source = """use dsa

nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
maximum subarray sum of nums into max_sum
maximum subarray in nums into best_slice
"""
    env = execute(source)
    assert env["max_sum"] == 6
    assert env["best_slice"] == [4, -1, 2, 1]


def test_dsa_prefix_sums_and_2d():
    """9. Prefix Sums & 2D Range Queries: LC 303, LC 304."""
    source = """use dsa

nums = [1, 2, 3, 4, 5]
prefix sums of nums into pref
range sum in pref from 1 to 3 into r_sum

matrix = [
    [1, 2],
    [3, 4]
]
create 2d prefix sums of matrix into pref2d
query 2d range sum in pref2d from 0, 0 to 1, 1 into total_2d
"""
    env = execute(source)
    assert env["r_sum"] == 9  # 2 + 3 + 4 = 9
    assert env["total_2d"] == 10  # 1 + 2 + 3 + 4 = 10


def test_dsa_two_pointer_pairs_and_triplets():
    """10. Two-Pointer Pairs (LC 167) and 3Sum Triplets (LC 15)."""
    source = """use dsa

sorted_nums = [2, 7, 11, 15]
find pair with sum 9 in sorted_nums into pair

nums = [-1, 0, 1, 2, -1, -4]
find all triplets with sum 0 in nums into triplets
"""
    env = execute(source)
    assert env["pair"] == [2, 7]
    assert env["triplets"] == [[-1, -1, 2], [-1, 0, 1]]


def test_dsa_minimum_spanning_tree():
    """11. Minimum Spanning Tree (Kruskal's Algorithm): LC 1584."""
    source = """use dsa

edges = [["A", "B", 1], ["B", "C", 4], ["A", "C", 2]]
build undirected graph from edges into g
minimum spanning tree of g into mst
minimum spanning tree weight of g into mst_cost
"""
    env = execute(source)
    assert env["mst_cost"] == 3.0
    assert len(env["mst"]) == 2


def test_dsa_knapsack_and_coin_change():
    """12. 0-1 Knapsack & Coin Change DP: LC 322, LC 518."""
    source = """use dsa

weights = [1, 3, 4, 5]
vals = [1, 4, 5, 7]
solve 0-1 knapsack with weights weights, values vals, capacity 7 into max_val

coins = [1, 2, 5]
minimum coins to make 11 in coins into min_coins
count ways to make 5 in coins into ways
"""
    env = execute(source)
    assert env["max_val"] == 9
    assert env["min_coins"] == 3  # 5 + 5 + 1
    assert env["ways"] == 4       # [5], [2,2,1], [2,1,1,1], [1,1,1,1,1]


def test_dsa_palindromes_and_kmp():
    """13. String Palindromes & KMP Pattern Matching: LC 28, LC 5."""
    source = """use dsa

text = "ABABDABACDABABCABAB"
find pattern "ABA" in text using kmp into kmp_matches

str_pal = "babad"
longest palindromic substring of str_pal into lps

check if "racecar" is palindrome into is_pal
check if "hello" is palindrome into not_pal
"""
    env = execute(source)
    assert env["kmp_matches"] == [0, 5, 10, 15]
    assert env["lps"] in ("bab", "aba")
    assert env["is_pal"] is True
    assert env["not_pal"] is False
