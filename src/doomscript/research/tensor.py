"""
Pure-Python Tensor implementation backed by Scalar autograd variables.
"""

from __future__ import annotations
from typing import Any, List, Sequence, Tuple, Union
from doomscript.research.autograd import Scalar


class Tensor:
    """
    Multidimensional Tensor backed by Scalar autograd nodes.
    Supports matrix multiplication, elementwise arithmetic, and sum reductions with automatic gradients.
    """

    def __init__(self, data: Any):
        if isinstance(data, (int, float, Scalar)):
            self._data = data if isinstance(data, Scalar) else Scalar(data)
            self._shape = ()
        elif isinstance(data, list):
            if len(data) == 0:
                self._data = []
                self._shape = (0,)
            elif isinstance(data[0], list):
                # 2D matrix
                rows = len(data)
                cols = len(data[0])
                matrix = []
                for r in range(rows):
                    row = []
                    for c in range(cols):
                        val = data[r][c]
                        row.append(val if isinstance(val, Scalar) else Scalar(val))
                    matrix.append(row)
                self._data = matrix
                self._shape = (rows, cols)
            else:
                # 1D vector
                vec = [x if isinstance(x, Scalar) else Scalar(x) for x in data]
                self._data = vec
                self._shape = (len(data),)
        else:
            raise TypeError(f"Unsupported data type for Tensor: {type(data)}")

    @property
    def shape(self) -> Tuple[int, ...]:
        return self._shape

    @property
    def data(self) -> Any:
        return self._data

    def __getitem__(self, idx: Any) -> Any:
        if isinstance(idx, tuple):
            if len(idx) == 2 and len(self._shape) == 2:
                r, c = idx
                return self._data[r][c]
            raise IndexError("Index dimensionality mismatch.")
        return self._data[idx]

    def sum(self) -> Scalar:
        """Sums all elements in the tensor into a single Scalar."""
        if len(self._shape) == 0:
            return self._data
        if len(self._shape) == 1:
            total = Scalar(0.0)
            for x in self._data:
                total = total + x
            return total
        if len(self._shape) == 2:
            total = Scalar(0.0)
            for row in self._data:
                for x in row:
                    total = total + x
            return total
        raise NotImplementedError("sum() currently supports up to 2D tensors.")

    def transpose(self) -> Tensor:
        """Transposes a 2D matrix tensor."""
        if len(self._shape) != 2:
            raise ValueError(f"transpose() requires 2D tensor, got shape {self._shape}")
        rows, cols = self._shape
        transposed = [[self._data[r][c] for r in range(rows)] for c in range(cols)]
        return Tensor(transposed)

    def matmul(self, other: Tensor) -> Tensor:
        """Performs 2D matrix multiplication."""
        if len(self._shape) != 2 or len(other.shape) != 2:
            raise ValueError(f"matmul requires 2D tensors, got {self._shape} and {other.shape}")
        m, k1 = self._shape
        k2, n = other.shape
        if k1 != k2:
            raise ValueError(f"Incompatible shapes for matmul: {self._shape} and {other.shape}")

        res = []
        for i in range(m):
            row = []
            for j in range(n):
                dot = Scalar(0.0)
                for k in range(k1):
                    dot = dot + (self._data[i][k] * other[k, j])
                row.append(dot)
            res.append(row)
        return Tensor(res)

    def __matmul__(self, other: Tensor) -> Tensor:
        return self.matmul(other)

    def __repr__(self) -> str:
        return f"Tensor(shape={self._shape})"
