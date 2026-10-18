"""
Phase 4 Tests: Comprehensions, Lambdas, Generators, and Math Builtins
Verifies CS and data science coursework capabilities in DoomScript.
"""

import pytest
import math
from doomscript.compiler.engine import execute


def test_list_comprehension_python_style(capsys):
    code = """
squares = [x * x for x in range(5)]
say squares

evens = [x for x in [1, 2, 3, 4, 5, 6] if x % 2 == 0]
say evens
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[0, 1, 4, 9, 16]",
        "[2, 4, 6]"
    ]


def test_list_comprehension_english(capsys):
    code = """
xs = [1, 2, 3, 4, 5]
squares = each x * x for x in range(5)
say squares

positives = each x in [-2, -1, 0, 1, 2] where x > 0
say positives

doubled_evens = each x * 2 for x in xs where x % 2 == 0
say doubled_evens
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[0, 1, 4, 9, 16]",
        "[1, 2]",
        "[4, 8]"
    ]


def test_dict_and_set_comprehensions(capsys):
    code = """
pairs = [("a", 1), ("b", 2), ("c", 3)]
d = {k: v for k, v in pairs}
say d["b"]

sq_dict = {x: x * x for x in range(4)}
say sq_dict[3]

st = {x * 2 for x in [1, 2, 2, 3]}
say sorted(list(st))
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "2",
        "9",
        "[2, 4, 6]"
    ]


def test_lambdas_english_and_python(capsys):
    code = """
inc = a function of x giving x + 1
say inc(10)

add = a function of a, b giving a + b
say add(15, 27)

mult = lambda x, y: x * y
say mult(6, 7)

pairs = [(1, "banana"), (2, "apple"), (3, "cherry")]
pairs.sort(key=a function of p giving p[1])
say [p[1] for p in pairs]
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "11",
        "42",
        "42",
        "['apple', 'banana', 'cherry']"
    ]


def test_generator_yield(capsys):
    code = """
to count_up with n:
    repeat with i from 1 to n:
        yield i

gen = count_up(4)
for each num in gen:
    say num

say list(count_up(3))
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "1",
        "2",
        "3",
        "4",
        "[1, 2, 3]"
    ]


def test_math_and_stats_builtins(capsys):
    code = """
nums = [10, 20, 30, 40, 50]
say mean(nums)
say median(nums)
say round(std_dev(nums), 2)
say round(variance(nums), 2)

say min(nums)
say max(nums)
say sum(nums)

say round(PI, 4)
say round(E, 4)
say INF > 999999
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "30.0",
        "30",
        "15.81",
        "250.0",
        "10",
        "50",
        "150",
        "3.1416",
        "2.7183",
        "True"
    ]


def test_cs_sieve_of_eratosthenes(capsys):
    code = """
to sieve with n:
    primes = []
    candidates = set(range(2, n + 1))
    while len(candidates) > 0:
        p = min(candidates)
        primes.append(p)
        multiples = set(range(p, n + 1, p))
        candidates = candidates - multiples
    return primes

say sieve(30)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]"
    ]


def test_cs_quicksort(capsys):
    code = """
to quicksort with xs:
    if len(xs) <= 1:
        return xs
    pivot = xs[0]
    rest = xs[1:]
    less = [x for x in rest if x <= pivot]
    greater = [x for x in rest if x > pivot]
    return quicksort(less) + [pivot] + quicksort(greater)

say quicksort([38, 27, 43, 3, 9, 82, 10])
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "[3, 9, 10, 27, 38, 43, 82]"
    ]


def test_ds_linear_regression_from_scratch(capsys):
    code = """
xs = [1.0, 2.0, 3.0, 4.0, 5.0]
ys = [2.0, 4.0, 5.0, 4.0, 5.0]

x_mean = mean(xs)
y_mean = mean(ys)

numerator = sum([(xs[i] - x_mean) * (ys[i] - y_mean) for i in range(len(xs))])
denominator = sum([(x - x_mean) ** 2 for x in xs])

slope = numerator / denominator
intercept = y_mean - slope * x_mean

say round(slope, 2)
say round(intercept, 2)

x_test = 6.0
y_pred = slope * x_test + intercept
say round(y_pred, 2)
"""
    execute(code)
    captured = capsys.readouterr()
    assert captured.out.strip().splitlines() == [
        "0.6",
        "2.2",
        "5.8"
    ]
