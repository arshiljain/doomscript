"""
Tests for DoomScript Deep Syntax Expansion.
Covers:
- Task 1: Runtime primitives (ds_median, ds_stdev, ds_variance, ds_enumerate, ds_take, ds_drop)
- Task 2: Math, powers, percentages, roots, statistical aggregates
- Task 3: Pattern matching (match ... when ... otherwise)
- Task 4: Slicing, take/drop, and spoken pipelines
- Task 5: Looping with index, down-to ranges, and English quantifiers
"""

import math
import pytest
from doomscript.compiler.engine import execute


# ---------------------------------------------------------------------------
# Task 1: Runtime Helpers Tests
# ---------------------------------------------------------------------------

def test_runtime_helpers_import():
    from doomscript.runtime import (
        ds_median,
        ds_stdev,
        ds_variance,
        ds_enumerate,
        ds_take,
        ds_drop,
    )

    data = [10, 20, 30, 40, 50]
    assert ds_median(data) == 30
    assert math.isclose(ds_stdev([1, 2, 3, 4, 5]), 1.5811388300841898)
    assert math.isclose(ds_variance([1, 2, 3, 4, 5]), 2.5)

    # 1-based indexing default for ds_enumerate
    enumerated = list(ds_enumerate(["alpha", "beta", "gamma"]))
    assert enumerated == [(1, "alpha"), (2, "beta"), (3, "gamma")]

    # ds_take and ds_drop
    assert ds_take([1, 2, 3, 4, 5], 3) == [1, 2, 3]
    assert ds_take([1, 2], 5) == [1, 2]
    assert ds_drop([1, 2, 3, 4, 5], 2) == [3, 4, 5]
    assert ds_drop([1, 2], 5) == []
