"""
Tests for Phase 2: Indexing, Slicing, Tuples, and Essential Operators (CS1 core)
"""

import pytest
from doomscript.compiler.engine import execute


def test_subscript_read_0_based(capsys):
    code = """
xs = [10, 20, 30]
say xs[0]
say xs[1]
say xs[-1]
d = {"k": "v"}
say d["k"]
m = [[1, 2], [3, 4]]
say m[1][0]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["10", "20", "30", "v", "3"]


def test_subscript_write(capsys):
    code = """
xs = [1, 2, 3]
xs[0] = 99
say xs[0]
d = {"a": 1}
d["a"] = 100
d["b"] = 200
say d["a"], d["b"]
grid = [[0, 0], [0, 0]]
grid[1][1] = 77
say grid[1][1]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["99", "100 200", "77"]


def test_subscript_aug_assign(capsys):
    code = """
freq = {"cat": 2}
freq["cat"] += 1
say freq["cat"]
xs = [10, 20]
xs[1] += 5
say xs[1]
grid = [[1, 2], [3, 4]]
grid[0][1] += 10
say grid[0][1]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["3", "25", "12"]


def test_slicing(capsys):
    code = """
xs = [0, 1, 2, 3, 4, 5]
say xs[1:4]
say xs[:3]
say xs[3:]
say xs[::2]
say xs[1:5:2]
say xs[:-1]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[1, 2, 3]",
        "[0, 1, 2]",
        "[3, 4, 5]",
        "[0, 2, 4]",
        "[1, 3]",
        "[0, 1, 2, 3, 4]"
    ]


def test_english_set_item_coexistence(capsys):
    code = """
xs = [10, 20, 30]
set item 2 of xs to 99
say xs[1]
xs[2] = 77
say item 3 of xs
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["99", "77"]


def test_tuple_unpack_and_swap(capsys):
    code = """
a = 1
b = 2
a, b = b, a
say a, b

t = (10, 20)
say t[0], t[1]
x, y = t
say x, y

empty_t = ()
say len(empty_t)
single_t = (5,)
say single_t[0]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "2 1",
        "10 20",
        "10 20",
        "0",
        "5"
    ]


def test_for_enumerate_tuple_target(capsys):
    code = """
fruits = ["apple", "banana"]
for i, f in enumerate(fruits):
    say i, f
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["0 apple", "1 banana"]


def test_set_literals_and_operators(capsys):
    code = """
s1 = {1, 2, 3}
s2 = {3, 4, 5}
say sorted(list(s1 | s2))
say sorted(list(s1 & s2))
say sorted(list(s1 - s2))
say sorted(list(s1 ^ s2))
empty_dict = {}
say len(empty_dict)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[1, 2, 3, 4, 5]",
        "[3]",
        "[1, 2]",
        "[1, 2, 4, 5]",
        "0"
    ]


def test_symbol_operators(capsys):
    code = """
say 7 // 2
say 7 % 2
say 2 ** 3
say 7 mod 2
say 2 to the power of 3
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "3",
        "1",
        "8",
        "1",
        "8"
    ]


def test_pop_statement_and_expression(capsys):
    code = """
st = [10, 20, 30]
val = pop st
say val
say pop st
pop from st
say len(st)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "30",
        "20",
        "0"
    ]


def test_cs1_algorithm_bubble_sort(capsys):
    code = """
arr = [64, 34, 25, 12, 22, 11, 90]
n = len(arr)
for i in range(n):
    for j in range(0, n - i - 1):
        if arr[j] > arr[j + 1]:
            arr[j], arr[j + 1] = arr[j + 1], arr[j]
say arr
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[11, 12, 22, 25, 34, 64, 90]"


def test_cs1_algorithm_word_frequency(capsys):
    code = """
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
freq = {}
for w in words:
    if w not in freq:
        freq[w] = 0
    freq[w] += 1
say freq["apple"], freq["banana"], freq["cherry"]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "3 2 1"


def test_cs1_algorithm_binary_search(capsys):
    code = """
to binary_search with arr, target:
    lo = 0
    hi = len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

items = [10, 20, 30, 40, 50]
say binary_search(items, 30)
say binary_search(items, 99)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == ["2", "-1"]


def test_cs1_algorithm_matrix_multiply(capsys):
    code = """
A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
C = [[0, 0], [0, 0]]

for i in range(2):
    for j in range(2):
        total = 0
        for k in range(2):
            total += A[i][k] * B[k][j]
        C[i][j] = total

say C
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[[19, 22], [43, 50]]"
