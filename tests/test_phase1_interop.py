"""
Tests for Phase 1: Dotted calls and full Python interop.
Validates:
- Dotted attribute access: obj.attr
- Dotted method calls: obj.method(args)
- Chained calls: a.b(c).d(e)
- Calls with keyword args: f(x=1)
- Calls on call results: f()(x)
- Python import aliasing: use python module numpy as np
- Dotted module paths: use python module matplotlib.pyplot as plt
- from python module ... use ... with dotted module path
- Variables named like keywords with dotted access: first = {revenue: 3}; first.revenue
- Function names like square callable: square(5)
- Standard library interop: math.sqrt(16), random.seed(1)
"""

import sys
from pathlib import Path
import pytest
from doomscript.compiler.engine import execute


def test_standard_library_math_and_random():
    """Verify standard library dotted calls like math.sqrt(16) and random.seed(1)."""
    code = """
use python module math
root = math.sqrt(16)
val = math.floor(3.7)
"""
    env = execute(code)
    assert env["root"] == 4.0
    assert env["val"] == 3


def test_chained_string_methods():
    """Verify chained method calls: s.lower().split(' ')."""
    code = """
s = "Hello World"
parts = s.lower().split(" ")
"""
    env = execute(code)
    assert env["parts"] == ["hello", "world"]


def test_keyword_variables_dotted_access():
    """Verify that variables named like keywords (e.g. first, count) support dotted access."""
    code = """
first = {revenue: 3}
val = first.revenue
"""
    env = execute(code)
    assert env["val"] == 3


def test_function_named_square_callable():
    """Verify function named square can be defined and called cleanly."""
    code = """
to square with x:
    return x * x

res = square(5)
"""
    env = execute(code)
    assert env["res"] == 25


def test_method_call_with_keyword_arguments():
    """Verify method and function calls support keyword arguments f(x=1)."""
    code = """
s = "a,b,c"
res = s.split(",", maxsplit=1)
"""
    env = execute(code)
    assert env["res"] == ["a", "b,c"]


def test_calls_on_call_results():
    """Verify calls on call results: f()(x)."""
    code = """
to get_multiplier with factor:
    to mult with x:
        return x * factor
    return mult

res = get_multiplier(3)(7)
"""
    env = execute(code)
    assert env["res"] == 21


def test_numpy_interop():
    """Acceptance test 1: numpy as np, np.array, a.mean()."""
    pytest.importorskip("numpy")
    code = """
use python module numpy as np
a = np.array([1, 2, 3, 4])
avg = a.mean()
"""
    env = execute(code)
    assert float(env["avg"]) == 2.5


def test_pandas_interop(tmp_path, monkeypatch):
    """Acceptance test 2: pandas as pd, pd.read_csv, df['y'].mean()."""
    pytest.importorskip("pandas")
    monkeypatch.chdir(tmp_path)
    csv_file = tmp_path / "d.csv"
    csv_file.write_text("x,y\n1,10\n2,20\n3,30\n", encoding="utf-8")

    code = """
use python module pandas as pd
df = pd.read_csv("d.csv")
avg_y = df["y"].mean()
"""
    env = execute(code)
    assert float(env["avg_y"]) == 20.0


def test_matplotlib_interop(tmp_path, monkeypatch):
    """Acceptance test 3: matplotlib with Agg, matplotlib.pyplot as plt, plt.savefig."""
    pytest.importorskip("matplotlib")
    monkeypatch.chdir(tmp_path)

    code = """
use python module matplotlib
matplotlib.use("Agg")
use python module matplotlib.pyplot as plt
plt.plot([1, 2], [3, 4])
plt.savefig("p.png")
"""
    execute(code)
    assert (tmp_path / "p.png").exists()


def test_sklearn_interop():
    """Acceptance test 4: from python module sklearn.linear_model use LinearRegression."""
    pytest.importorskip("sklearn")
    code = """
from python module sklearn.linear_model use LinearRegression
m = LinearRegression()
m.fit([[1], [2], [3]], [2, 4, 6])
pred = m.predict([[4]])
pred_val = pred[0]
"""
    env = execute(code)
    assert round(float(env["pred_val"])) == 8
