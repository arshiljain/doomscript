"""
Pure-Python reverse-mode scalar autograd and numerical gradient checking.
"""

from __future__ import annotations
import math
from typing import Callable, Iterable, List, Optional, Set, Tuple, Union


class Scalar:
    """
    Reverse-mode scalar autograd variable supporting automatic differentiation.
    All data is stored in float64 precision.
    """

    def __init__(
        self,
        data: float,
        _children: Tuple[Scalar, ...] = (),
        _op: str = "",
    ):
        self.data: float = float(data)
        self.grad: float = 0.0
        self._backward: Callable[[], None] = lambda: None
        self._prev: Set[Scalar] = set(_children)
        self._op: str = _op

    @property
    def value(self) -> float:
        return self.data

    def __add__(self, other: Union[Scalar, float, int]) -> Scalar:
        other = other if isinstance(other, Scalar) else Scalar(other)
        out = Scalar(self.data + other.data, (self, other), "+")

        def _backward() -> None:
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __radd__(self, other: Union[Scalar, float, int]) -> Scalar:
        return self + other

    def __neg__(self) -> Scalar:
        return self * -1.0

    def __sub__(self, other: Union[Scalar, float, int]) -> Scalar:
        return self + (-other)

    def __rsub__(self, other: Union[Scalar, float, int]) -> Scalar:
        return Scalar(other) + (-self)

    def __mul__(self, other: Union[Scalar, float, int]) -> Scalar:
        other = other if isinstance(other, Scalar) else Scalar(other)
        out = Scalar(self.data * other.data, (self, other), "*")

        def _backward() -> None:
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    def __rmul__(self, other: Union[Scalar, float, int]) -> Scalar:
        return self * other

    def __truediv__(self, other: Union[Scalar, float, int]) -> Scalar:
        other = other if isinstance(other, Scalar) else Scalar(other)
        return self * (other ** -1.0)

    def __rtruediv__(self, other: Union[Scalar, float, int]) -> Scalar:
        return Scalar(other) / self

    def __pow__(self, other: Union[Scalar, float, int]) -> Scalar:
        is_scalar = isinstance(other, Scalar)
        exp_val = other.data if is_scalar else float(other)
        out = Scalar(self.data ** exp_val, (self, other) if is_scalar else (self,), f"**{exp_val}")

        def _backward() -> None:
            self.grad += (exp_val * (self.data ** (exp_val - 1.0))) * out.grad
            if is_scalar and self.data > 0.0:
                other.grad += (out.data * math.log(self.data)) * out.grad

        out._backward = _backward
        return out

    def relu(self) -> Scalar:
        val = max(0.0, self.data)
        out = Scalar(val, (self,), "relu")

        def _backward() -> None:
            self.grad += (1.0 if self.data > 0.0 else 0.0) * out.grad

        out._backward = _backward
        return out

    def exp(self) -> Scalar:
        val = math.exp(self.data)
        out = Scalar(val, (self,), "exp")

        def _backward() -> None:
            self.grad += val * out.grad

        out._backward = _backward
        return out

    def log(self) -> Scalar:
        val = math.log(self.data)
        out = Scalar(val, (self,), "log")

        def _backward() -> None:
            self.grad += (1.0 / self.data) * out.grad

        out._backward = _backward
        return out

    def tanh(self) -> Scalar:
        val = math.tanh(self.data)
        out = Scalar(val, (self,), "tanh")

        def _backward() -> None:
            self.grad += (1.0 - val ** 2) * out.grad

        out._backward = _backward
        return out

    def sigmoid(self) -> Scalar:
        val = 1.0 / (1.0 + math.exp(-self.data))
        out = Scalar(val, (self,), "sigmoid")

        def _backward() -> None:
            self.grad += (val * (1.0 - val)) * out.grad

        out._backward = _backward
        return out

    def backward(self) -> None:
        """Propagate gradients backward through the DAG starting at this node."""
        topo: List[Scalar] = []
        visited: Set[Scalar] = set()

        def build_topo(v: Scalar) -> None:
            if v not in visited:
                visited.add(v)
                for child in v._prev:
                    build_topo(child)
                topo.append(v)

        build_topo(self)

        self.grad = 1.0
        for node in reversed(topo):
            node._backward()

    def __repr__(self) -> str:
        return f"Scalar(data={self.data:.6f}, grad={self.grad:.6f})"


def check_grad(
    func: Callable[[List[Scalar]], Scalar],
    x_values: List[float],
    eps: float = 1e-6,
    rtol: float = 1e-4,
    atol: float = 1e-5,
) -> bool:
    """
    Verifies autograd gradients against central-difference numerical gradients using relative error.
    """
    # 1. Analytical gradients via autograd
    scalars = [Scalar(x) for x in x_values]
    out = func(scalars)
    out.backward()
    ana_grads = [s.grad for s in scalars]

    # 2. Central difference numerical gradients
    for i in range(len(x_values)):
        x_plus = list(x_values)
        x_plus[i] += eps
        x_minus = list(x_values)
        x_minus[i] -= eps

        out_plus = func([Scalar(x) for x in x_plus]).data
        out_minus = func([Scalar(x) for x in x_minus]).data
        num_grad = (out_plus - out_minus) / (2.0 * eps)

        diff = abs(ana_grads[i] - num_grad)
        scale = max(abs(ana_grads[i]), abs(num_grad), 1e-8)
        rel_err = diff / scale

        if diff > atol and rel_err > rtol:
            return False

    return True
