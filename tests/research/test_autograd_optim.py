"""
Tests for DoomScript Research autograd, tensor operations, numerical gradient checking, and optimizers.
"""

import pytest
import math
from doomscript.research.autograd import Scalar, check_grad
from doomscript.research.tensor import Tensor
from doomscript.research.optim import Adam, SGDMomentum


def test_autograd_basic_operations():
    x = Scalar(2.0)
    y = Scalar(-3.0)
    z = (x * y + Scalar(5.0)) ** 2
    z.backward()
    # dz/dx = 2 * (x * y + 5) * y = 2 * (-6 + 5) * (-3) = 6.0
    assert x.grad == pytest.approx(6.0, rel=1e-6)
    assert y.grad == pytest.approx(-4.0, rel=1e-6)


def test_autograd_activations():
    x = Scalar(0.5)
    # Sigmoid
    s = x.sigmoid()
    s.backward()
    expected_s_grad = (1.0 / (1.0 + math.exp(-0.5))) * (1.0 - 1.0 / (1.0 + math.exp(-0.5)))
    assert x.grad == pytest.approx(expected_s_grad, rel=1e-5)

    # Reset grad
    x.grad = 0.0
    # Tanh
    t = x.tanh()
    t.backward()
    expected_t_grad = 1.0 - math.tanh(0.5) ** 2
    assert x.grad == pytest.approx(expected_t_grad, rel=1e-5)

    # ReLU
    a = Scalar(-2.5)
    r = a.relu()
    r.backward()
    assert r.data == 0.0
    assert a.grad == 0.0

    b = Scalar(3.0)
    r2 = b.relu()
    r2.backward()
    assert r2.data == 3.0
    assert b.grad == 1.0


def test_relative_gradient_check():
    def f(v):
        # v is a list of Scalars
        return (v[0] ** 3) + (v[1] * v[0]).exp()

    assert check_grad(f, [1.5, 0.5]) is True


def test_tensor_operations_and_autograd():
    # 2x2 matrix
    A = Tensor([[1.0, 2.0], [3.0, 4.0]])
    B = Tensor([[5.0, 6.0], [7.0, 8.0]])

    assert A.shape == (2, 2)
    C = A.matmul(B)
    assert C.shape == (2, 2)
    # C[0, 0] = 1*5 + 2*7 = 19
    # C[0, 1] = 1*6 + 2*8 = 22
    # C[1, 0] = 3*5 + 4*7 = 43
    # C[1, 1] = 3*6 + 4*8 = 50
    assert C[0, 0].data == pytest.approx(19.0)
    assert C[0, 1].data == pytest.approx(22.0)
    assert C[1, 0].data == pytest.approx(43.0)
    assert C[1, 1].data == pytest.approx(50.0)

    # Backprop through tensor sum
    s = C.sum()
    s.backward()
    # A[0,0] contributes to C[0,0] (times B[0,0]=5) and C[0,1] (times B[0,1]=6)
    # So dA[0,0] = 5 + 6 = 11
    assert A[0, 0].grad == pytest.approx(11.0)


def test_sgd_momentum_step():
    w = Scalar(5.0)
    opt = SGDMomentum([w], lr=0.1, momentum=0.9)
    # Minimize f(w) = w^2
    for _ in range(5):
        opt.zero_grad()
        loss = w * w
        loss.backward()
        opt.step()
    assert w.data < 2.0


def test_adam_optimizer_step():
    w = Scalar(5.0)
    opt = Adam([w], lr=0.1)
    loss = (w - Scalar(1.0)) ** 2
    loss.backward()
    opt.step()
    assert w.data < 5.0

    # Multi-step minimization to near target 1.0
    for _ in range(100):
        opt.zero_grad()
        loss = (w - Scalar(1.0)) ** 2
        loss.backward()
        opt.step()
    assert abs(w.data - 1.0) < 0.05
