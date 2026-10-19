"""Tests for High-Level Algorithmic English DSA Extension in DoomScript."""

import pytest
from doomscript.compiler.engine import execute


def test_dsa_grid_and_dp_tables():
    source = """use dsa

create grid with 3 rows and 4 columns filled with 0 into dp
create 2d grid of 7 with 2 rows and 3 columns into matrix
create dp table with 4 rows and 5 columns into memo

set dp[0][0] to 42
set memo[3][4] to 99
"""
    env = execute(source)
    assert len(env["dp"]) == 3
    assert len(env["dp"][0]) == 4
    assert env["dp"][0][0] == 42
    assert env["dp"][1][1] == 0  # No shallow-copy reference duplication across rows!

    assert env["matrix"] == [[7, 7, 7], [7, 7, 7]]
    assert len(env["memo"]) == 4
    assert len(env["memo"][0]) == 5
    assert env["memo"][3][4] == 99


def test_dsa_connected_components_islands():
    """LeetCode 200: Number of Islands in spoken English."""
    source = """use dsa

grid = [
    ["1", "1", "0", "0"],
    ["1", "1", "0", "0"],
    ["0", "0", "1", "0"],
    ["0", "0", "0", "1"]
]

find 4-way connected components in grid where cell is "1" into islands
count 4-way connected components in grid where cell is "1" into island_count
"""
    env = execute(source)
    assert env["island_count"] == 3
    assert len(env["islands"]) == 3


def test_dsa_native_heaps_and_queues():
    """Universal min and max heaps without numeric negation hacks."""
    source = """use dsa

create max heap into max_pq
push 15 into max_pq
push 42 into max_pq
push 8 into max_pq
push 99 into max_pq

peek max from max_pq into top_val
pop max from max_pq into first_out
pop max from max_pq into second_out

create min heap into min_pq
push 50 into min_pq
push 5 into min_pq
push 25 into min_pq

pop min from min_pq into min_first

create deque into q
push 10 into q
push 20 into q
push left 5 into q

pop left from q into q_head
pop right from q into q_tail
"""
    env = execute(source)
    assert env["top_val"] == 99
    assert env["first_out"] == 99
    assert env["second_out"] == 42
    assert env["min_first"] == 5

    assert env["q_head"] == 5
    assert env["q_tail"] == 20


def test_dsa_graphs_cycle_and_topological_sort():
    """LeetCode 207 (Course Schedule) and topological ordering."""
    source = """use dsa

# Cycle detection: A -> B -> C -> A
prereqs_cycle = [[0, 1], [1, 2], [2, 0]]
build directed graph from prereqs_cycle into g_deadlock
check if g_deadlock has cycle into deadlock_found

# DAG: 0 -> 1 -> 2 -> 3
prereqs_dag = [[0, 1], [1, 2], [2, 3]]
build directed graph from prereqs_dag into g_courses
check if g_courses has cycle into dag_cycle
topological sort of g_courses into course_order

# Dijkstra Shortest Path
edges_weighted = [["A", "B", 1], ["B", "C", 2], ["A", "C", 5]]
build directed graph from edges_weighted into net
shortest path in net from "A" to "C" into fast_path
"""
    env = execute(source)
    assert env["deadlock_found"] is True
    assert env["dag_cycle"] is False
    assert env["course_order"] == [0, 1, 2, 3]
    assert env["fast_path"] == ["A", "B", "C"]


def test_dsa_memoization():
    """Automatic transparent function memoization."""
    source = """use dsa

to fib with n:
    if n is at most 1:
        return n
    return fib(n - 1) + fib(n - 2)

memoize function fib

ans_30 = fib(30)
"""
    env = execute(source)
    assert env["ans_30"] == 832040


def test_dsa_interval_algorithms():
    """LeetCode 56 (Merge Intervals) and LeetCode 986 (Interval Intersections)."""
    source = """use dsa

raw_intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]
merge overlapping intervals in raw_intervals into merged_intervals

a_intervals = [[0, 2], [5, 10]]
b_intervals = [[1, 5], [8, 12]]
intersect intervals a_intervals and b_intervals into overlaps
"""
    env = execute(source)
    assert env["merged_intervals"] == [[1, 6], [8, 10], [15, 18]]
    assert env["overlaps"] == [[1, 2], [5, 5], [8, 10]]


def test_dsa_sliding_window_max_and_frequencies():
    """LeetCode 239 (Sliding Window Maximum) and frequency counts."""
    source = """use dsa

stream = [1, 3, -1, -3, 5, 3, 6, 7]
sliding window maximum of stream with size 3 into window_maxes

chars = "abracadabra"
frequency map of chars into char_freqs
"""
    env = execute(source)
    assert env["window_maxes"] == [3, 3, 5, 5, 6, 7]
    assert env["char_freqs"]["a"] == 5
    assert env["char_freqs"]["b"] == 2
    assert env["char_freqs"]["r"] == 2
