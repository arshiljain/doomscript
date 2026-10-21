"""Unit tests for Tranche 5 Domain Expansions (finance, time_series, opt)."""

import math
import pytest
from doomscript.domains.finance.runtime import (
    SABRVolatilityModel,
    KellyCriterionMultiAsset,
    finance_sabr_volatility,
    finance_kelly_allocation,
)
from doomscript.domains.time_series.runtime import (
    CointegrationEngleGranger,
    PELTChangepointDetection,
    time_series_cointegration,
    time_series_pelt_changepoints,
)
from doomscript.domains.opt.runtime import (
    DifferentialEvolutionOptimizer,
    opt_differential_evolution,
)


def test_finance_sabr_volatility_model():
    """Verify SABR implied volatility model calculation."""
    f = 100.0
    K = 100.0  # ATM
    T = 1.0
    alpha = 0.2
    beta = 0.5
    rho = -0.3
    nu = 0.4

    vol_atm = finance_sabr_volatility(f, K, T, alpha, beta, rho, nu)
    assert 0.01 < vol_atm < 0.5

    # Out of the money call K = 120
    vol_otm = finance_sabr_volatility(f, 120.0, T, alpha, beta, rho, nu)
    assert 0.01 < vol_otm < 0.5


def test_finance_kelly_multi_asset():
    """Verify multi-asset Kelly criterion optimal leverage fraction."""
    mu = [0.10, 0.08]
    cov = [
        [0.04, 0.01],
        [0.01, 0.03]
    ]
    res = finance_kelly_allocation(mu, cov, rf=0.02, fraction=0.5)
    assert len(res.optimal_weights) == 2
    assert res.optimal_weights[0] > 0.0
    assert res.optimal_weights[1] > 0.0
    assert res.total_leverage > 0.0


def test_time_series_cointegration_test():
    """Verify Engle-Granger cointegration detection on simulated random walk pairs."""
    import random
    rng = random.Random(42)
    n = 60
    # Common stochastic trend
    trend = 0.0
    common = []
    for _ in range(n):
        trend += rng.normalvariate(0, 1)
        common.append(trend)

    # Cointegrated pair: y = 2 * x + noise
    x = [val + rng.normalvariate(0, 0.2) for val in common]
    y = [2.0 * val + rng.normalvariate(0, 0.2) for val in common]

    res = time_series_cointegration(y, x)
    assert res.beta == pytest.approx(2.0, abs=0.2)
    assert res.t_statistic < 0.0


def test_time_series_pelt_changepoints():
    """Verify PELT structural regime shift detection."""
    # Signal with 3 regimes: 0..20 at 5.0, 21..40 at 25.0, 41..60 at 10.0
    data = [5.0] * 20 + [25.0] * 20 + [10.0] * 20
    res = time_series_pelt_changepoints(data, penalty=10.0)

    assert len(res.changepoints) == 2
    assert 18 <= res.changepoints[0] <= 22
    assert 38 <= res.changepoints[1] <= 42


def test_opt_differential_evolution():
    """Verify Differential Evolution global optimizer on Sphere function."""
    # Sphere function f(x, y) = x^2 + y^2, minimum at (0, 0)
    sphere = lambda ind: ind[0] ** 2 + ind[1] ** 2
    bounds = [(-5.0, 5.0), (-5.0, 5.0)]

    res = opt_differential_evolution(sphere, bounds, max_iter=40)
    assert res.best_value < 1e-3
    assert abs(res.best_solution[0]) < 0.05
    assert abs(res.best_solution[1]) < 0.05
