# tests/research/test_stats.py
import pytest
import math
from doomscript.research.stats import (
    welch_t_test,
    student_t_test,
    mann_whitney_u_test,
    one_way_anova,
    chi_square_independence,
    confidence_interval,
    wilson_score_interval,
    bca_bootstrap,
    adjust_p_values,
    metropolis_hastings,
    TestResult,
    MCMCResult,
)

def test_welch_vs_student_t_test():
    # Unequal variance datasets
    a = [10.1, 9.8, 10.4, 11.0, 9.5, 10.2, 10.0]
    b = [12.5, 13.1, 11.9, 14.0, 12.8, 13.5, 15.0]
    
    welch_res = welch_t_test(a, b)
    assert isinstance(welch_res, TestResult)
    assert welch_res.p_value < 0.001
    assert welch_res.statistic < 0.0
    assert welch_res.effect_size is not None  # Cohen's d / Hedges' g
    assert welch_res.p_value == welch_res["p_value"]

    student_res = student_t_test(a, b)
    assert student_res.p_value < 0.001

def test_mann_whitney_u():
    # Distinct non-overlapping samples
    x = [1, 2, 3, 4]
    y = [5, 6, 7, 8]
    res = mann_whitney_u_test(x, y)
    assert res.statistic == 0.0
    assert res.p_value < 0.05

def test_one_way_anova():
    g1 = [82, 83, 97, 83, 78]
    g2 = [88, 90, 89, 93, 85]
    g3 = [95, 99, 92, 94, 91]
    res = one_way_anova(g1, g2, g3)
    assert res.p_value < 0.05
    assert res.statistic > 3.0
    assert 0.0 < res.effect_size < 1.0  # eta_squared

def test_chi_square_independence():
    # 2x2 table: [[10, 20], [20, 10]]
    table = [[10, 20], [20, 10]]
    res = chi_square_independence(table)
    assert res.p_value < 0.05
    assert res.df == 1

def test_confidence_intervals():
    data = [10.0, 12.0, 11.0, 13.0, 12.0, 11.0]
    low, high = confidence_interval(data, confidence=0.95)
    mean_val = sum(data) / len(data)
    assert low < mean_val < high

    # Wilson score interval for 80 successes out of 100
    w_low, w_high = wilson_score_interval(successes=80, total=100, confidence=0.95)
    assert 0.70 < w_low < 0.80 < w_high < 0.90

def test_bca_bootstrap():
    data = [1.2, 2.3, 1.8, 3.1, 2.7, 3.5, 4.0, 2.9, 3.2]
    low, high = bca_bootstrap(data, stat_func=lambda s: sum(s) / len(s), n_resamples=1000)
    mean_val = sum(data) / len(data)
    assert low <= mean_val <= high

def test_multiple_testing_adjustments():
    raw_p = [0.001, 0.01, 0.03, 0.04, 0.20]
    holm_p = adjust_p_values(raw_p, method="holm")
    assert holm_p[0] <= holm_p[1] <= holm_p[2]
    assert holm_p[0] == pytest.approx(0.005, rel=1e-3)

    bh_p = adjust_p_values(raw_p, method="benjamini_hochberg")
    assert all(p <= 1.0 for p in bh_p)

def test_metropolis_hastings_mcmc():
    # Standard 1D normal target log-density: -0.5 * x^2
    def log_target(x):
        return -0.5 * (x[0] ** 2)

    res = metropolis_hastings(log_target, initial=[3.0], n_samples=3000, burn_in=0.25, n_chains=2)
    assert isinstance(res, MCMCResult)
    assert 0.15 <= res.acceptance_rate <= 0.65
    assert res.r_hat < 1.10
    assert res.ess > 100
