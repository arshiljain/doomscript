"""
Optimizers for research models (Adam, SGD with Momentum).
"""

from __future__ import annotations
import math
from typing import List, Sequence
from doomscript.research.autograd import Scalar


class Optimizer:
    """Base class for optimizers."""

    def __init__(self, params: Sequence[Scalar], lr: float):
        self.params: List[Scalar] = list(params)
        self.lr: float = float(lr)

    def zero_grad(self) -> None:
        """Resets the gradients of all parameters to zero."""
        for p in self.params:
            p.grad = 0.0

    def step(self) -> None:
        raise NotImplementedError


class SGDMomentum(Optimizer):
    """
    Stochastic Gradient Descent optimizer with momentum.
    """

    def __init__(self, params: Sequence[Scalar], lr: float = 0.01, momentum: float = 0.9):
        super().__init__(params, lr)
        self.momentum: float = float(momentum)
        self.velocities: List[float] = [0.0] * len(self.params)

    def step(self) -> None:
        for i, p in enumerate(self.params):
            v = self.momentum * self.velocities[i] + p.grad
            self.velocities[i] = v
            p.data -= self.lr * v


class Adam(Optimizer):
    """
    Adaptive Moment Estimation (Adam) optimizer with bias correction.
    """

    def __init__(
        self,
        params: Sequence[Scalar],
        lr: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        eps: float = 1e-8,
    ):
        super().__init__(params, lr)
        self.beta1: float = float(beta1)
        self.beta2: float = float(beta2)
        self.eps: float = float(eps)
        self.t: int = 0
        self.m: List[float] = [0.0] * len(self.params)
        self.v: List[float] = [0.0] * len(self.params)

    def step(self) -> None:
        self.t += 1
        b1, b2, eps, lr = self.beta1, self.beta2, self.eps, self.lr

        for i, p in enumerate(self.params):
            g = p.grad
            self.m[i] = b1 * self.m[i] + (1.0 - b1) * g
            self.v[i] = b2 * self.v[i] + (1.0 - b2) * (g ** 2)

            m_hat = self.m[i] / (1.0 - (b1 ** self.t))
            v_hat = self.v[i] / (1.0 - (b2 ** self.t))

            p.data -= (lr * m_hat) / (math.sqrt(v_hat) + eps)
