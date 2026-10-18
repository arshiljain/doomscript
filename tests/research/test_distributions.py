# tests/research/test_distributions.py
import math
import pytest
from doomscript.research.distributions import (
    gammainc,
    gammaincc,
    betainc,
    betaincc,
    t_cdf,
    t_sf,
    f_cdf,
    f_sf,
    chi2_cdf,
    chi2_sf,
    inv_t_cdf,
    inv_chi2_cdf,
    normal_cdf,
    normal_sf,
)

def test_incomplete_gamma_values():
    # P(1, 2) = 1 - e^-2 = 0.8646647167633873
    expected_lower = 1.0 - math.exp(-2.0)
    expected_upper = math.exp(-2.0)
    assert gammainc(1.0, 2.0) == pytest.approx(expected_lower, rel=1e-10)
    assert gammaincc(1.0, 2.0) == pytest.approx(expected_upper, rel=1e-10)
    assert gammainc(1.0, 2.0) + gammaincc(1.0, 2.0) == pytest.approx(1.0, abs=1e-12)

def test_incomplete_beta_values():
    # I_0.5(1, 1) = 0.5
    assert betainc(1.0, 1.0, 0.5) == pytest.approx(0.5, rel=1e-10)
    assert betaincc(1.0, 1.0, 0.5) == pytest.approx(0.5, rel=1e-10)
    # I_0.2(2, 3) = 10 * integral from 0 to 0.2 of t*(1-t)^2 dt = 0.1808
    assert betainc(2.0, 3.0, 0.2) == pytest.approx(0.1808, rel=1e-8)
    assert betaincc(2.0, 3.0, 0.2) == pytest.approx(1.0 - 0.1808, rel=1e-8)

def test_student_t_and_survival():
    # At t=0, cdf is exactly 0.5
    assert t_cdf(0.0, df=10.0) == pytest.approx(0.5, rel=1e-10)
    assert t_sf(0.0, df=10.0) == pytest.approx(0.5, rel=1e-10)
    
    # Extreme survival avoids catastrophic cancellation
    extreme_p = t_sf(25.0, df=30.0)
    assert extreme_p > 0.0
    assert extreme_p < 1e-15

def test_f_distribution_and_chi2():
    # F(1, 10) at f=4.9646 approx 0.05 p-value (survival)
    p_f = f_sf(4.9646, dfn=1.0, dfd=10.0)
    assert p_f == pytest.approx(0.05, rel=1e-2)

    # Chi-square with df=2: P(x) = 1 - e^(-x/2), S(x) = e^(-x/2)
    # At x=5.991, survival is approx 0.05
    p_chi2 = chi2_sf(5.991, df=2.0)
    assert p_chi2 == pytest.approx(0.05, rel=1e-2)

def test_inverse_cdf_quantiles():
    # 97.5% quantile for t with df=10 is approx 2.2281
    q = inv_t_cdf(0.975, df=10.0)
    assert q == pytest.approx(2.228139, rel=1e-4)

    # Chi-square inverse CDF with df=2 at 0.95 is approx 5.991
    q_chi2 = inv_chi2_cdf(0.95, df=2.0)
    assert q_chi2 == pytest.approx(5.99146, rel=1e-4)
