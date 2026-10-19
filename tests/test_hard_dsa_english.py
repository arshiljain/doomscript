import pytest
from doomscript.compiler.engine import execute

def test_trapping_rain_water():
    """LeetCode 42 (Hard): Trapping Rain Water.
    Given n non-negative integers representing an elevation map where the width of each bar is 1,
    compute how much water it can trap after raining.
    """
    source = """
to trap_rain_water with heights:
    if (count of heights) is less than 3:
        return 0
    
    set left to 0
    set right to (count of heights) - 1
    set max_left to 0
    set max_right to 0
    set trapped_water to 0

    while left is less than right:
        if heights[left] is less than heights[right]:
            if heights[left] is at least max_left:
                set max_left to heights[left]
            else:
                increase trapped_water by (max_left - heights[left])
            increase left by 1
        else:
            if heights[right] is at least max_right:
                set max_right to heights[right]
            else:
                increase trapped_water by (max_right - heights[right])
            decrease right by 1
            
    return trapped_water

elevation_map1 = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
ans1 = trap_rain_water(elevation_map1)

elevation_map2 = [4, 2, 0, 3, 2, 5]
ans2 = trap_rain_water(elevation_map2)
"""
    env = execute(source)
    assert env["ans1"] == 6
    assert env["ans2"] == 9


def test_edit_distance_levenshtein():
    """LeetCode 72 (Hard): Edit Distance.
    Given two strings word1 and word2, return the minimum number of operations
    required to convert word1 to word2 (insert, delete, replace).
    """
    source = """
to edit_distance with word1, word2:
    set m to length of word1
    set n to length of word2

    # Create 2D DP matrix initialized with zeros
    set dp to []
    repeat with i from 0 to m:
        set row to []
        repeat with j from 0 to n:
            append 0 to row
        append row to dp

    # Base cases: transforming to/from empty string
    repeat with i from 0 to m:
        set dp[i][0] to i
    repeat with j from 0 to n:
        set dp[0][j] to j

    repeat with i from 1 to m:
        repeat with j from 1 to n:
            if word1[i - 1] is equal to word2[j - 1]:
                set dp[i][j] to dp[i - 1][j - 1]
            else:
                set insertion to dp[i][j - 1]
                set deletion to dp[i - 1][j]
                set replacement to dp[i - 1][j - 1]
                set best to minimum of [insertion, deletion, replacement]
                set dp[i][j] to 1 + best

    return dp[m][n]

dist1 = edit_distance("horse", "ros")
dist2 = edit_distance("intention", "execution")
"""
    env = execute(source)
    assert env["dist1"] == 3
    assert env["dist2"] == 5


def test_n_queens_backtracking():
    """LeetCode 51 (Hard): N-Queens.
    Place n queens on an n x n chessboard such that no two queens threaten each other.
    """
    source = """
to solve_n_queens with n:
    set solutions to []

    to is_safe with board, row, col:
        repeat with r from 0 to (row - 1):
            set c to board[r]
            if c is equal to col:
                return false
            set row_diff to row - r
            set col_diff to absolute value of (col - c)
            if row_diff is equal to col_diff:
                return false
        return true

    to place_queen with row, board:
        if row is equal to n:
            append (copy of board) to solutions
            return 0

        repeat with col from 0 to (n - 1):
            if is_safe(board, row, col) is true:
                append col to board
                place_queen(row + 1, board)
                pop board
        return 0

    place_queen(0, [])
    return count of solutions

queens_4 = solve_n_queens(4)
queens_8 = solve_n_queens(8)
"""
    env = execute(source)
    assert env["queens_4"] == 2
    assert env["queens_8"] == 92


def test_median_two_sorted_arrays():
    """LeetCode 4 (Hard): Median of Two Sorted Arrays in O(log(min(m, n)))."""
    source = """
to find_median_sorted_arrays with nums1, nums2:
    if (count of nums1) is greater than (count of nums2):
        return find_median_sorted_arrays(nums2, nums1)

    set m to count of nums1
    set n to count of nums2
    set low to 0
    set high to m

    while low is at most high:
        set partition_x to (low + high) // 2
        set partition_y to ((m + n + 1) // 2) - partition_x

        if partition_x is 0:
            set max_left_x to -999999999
        else:
            set max_left_x to nums1[partition_x - 1]

        if partition_x is m:
            set min_right_x to 999999999
        else:
            set min_right_x to nums1[partition_x]

        if partition_y is 0:
            set max_left_y to -999999999
        else:
            set max_left_y to nums2[partition_y - 1]

        if partition_y is n:
            set min_right_y to 999999999
        else:
            set min_right_y to nums2[partition_y]

        if (max_left_x is at most min_right_y) and (max_left_y is at most min_right_x):
            if ((m + n) % 2) is equal to 0:
                set left_max to maximum of [max_left_x, max_left_y]
                set right_min to minimum of [min_right_x, min_right_y]
                return (left_max + right_min) / 2.0
            else:
                return maximum of [max_left_x, max_left_y]
        elif max_left_x is greater than min_right_y:
            set high to partition_x - 1
        else:
            set low to partition_x + 1

    return 0.0

a1 = [1, 3]
b1 = [2]
med1 = find_median_sorted_arrays(a1, b1)

a2 = [1, 2]
b2 = [3, 4]
med2 = find_median_sorted_arrays(a2, b2)
"""
    env = execute(source)
    assert env["med1"] == 2.0
    assert env["med2"] == 2.5
