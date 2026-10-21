"""Unit tests for Tranche 2 Domain Expansions (metrics, research, graphics, quantum)."""

import math
import pytest
from doomscript.domains.metrics.runtime import (
    TDigestQuantileEstimator,
    HyperLogLogPlusPlus,
    CountMinSketch,
    metrics_tdigest_estimate,
    metrics_hyperloglog_count,
    metrics_count_min_frequencies,
)
from doomscript.domains.research.runtime import (
    PrincipalComponentAnalysis,
    LinearDiscriminantAnalysis,
    ConfidenceIntervalBootstrap,
    ANOVAOneWay,
    research_pca_fit_transform,
    research_lda_fit_transform,
    research_bootstrap_ci,
    research_anova_oneway,
)
from doomscript.domains.graphics.runtime import (
    PerlinNoiseGenerator,
    BezierSplineEvaluator,
    graphics_perlin_noise_2d,
    graphics_fbm_noise_2d,
    graphics_bezier_evaluate,
)
from doomscript.domains.quantum.runtime import (
    StabilizerTableauSimulator,
    Steane7QubitCode,
    quantum_stabilizer_simulate,
    quantum_steane_diagnose,
)


def test_metrics_tdigest_quantiles():
    """Verify T-Digest quantile tracking on sequential data."""
    values = [float(i) for i in range(1001)]  # 0 to 1000
    res = metrics_tdigest_estimate(values, [0.5, 0.9, 0.99])

    assert res["p50"] == pytest.approx(500.0, abs=15.0)
    assert res["p90"] == pytest.approx(900.0, abs=25.0)
    assert res["p99"] == pytest.approx(990.0, abs=15.0)


def test_metrics_hyperloglog_and_cms():
    """Verify HyperLogLog++ cardinality and Count-Min Sketch frequency."""
    items = [f"user_{i}" for i in range(5000)]
    est_card = metrics_hyperloglog_count(items)
    # HLL relative error within 5%
    assert 4750 <= est_card <= 5250

    # CMS test
    stream = ["apple"] * 50 + ["banana"] * 30 + ["cherry"] * 10
    freqs = metrics_count_min_frequencies(stream, ["apple", "banana", "cherry", "orange"])
    assert freqs["apple"] >= 50
    assert freqs["banana"] >= 30
    assert freqs["cherry"] >= 10
    assert freqs["orange"] == 0


def test_research_pca_and_lda():
    """Verify PCA variance explanation and LDA projection."""
    # Data with primary variance along x-axis
    data = [
        [10.0, 1.0], [20.0, 1.2], [30.0, 0.9], [40.0, 1.1], [50.0, 1.0]
    ]
    pca_res = research_pca_fit_transform(data, n_components=2)
    assert pca_res.explained_variance_ratio[0] > 0.95

    # LDA separation
    X = [[1.0, 1.0], [1.2, 0.9], [10.0, 10.0], [10.2, 9.8]]
    y = [0, 0, 1, 1]
    lda_res = research_lda_fit_transform(X, y)
    assert len(lda_res.transformed) == 4
    # Class 0 projections should be separated from class 1
    assert lda_res.transformed[0][0] != lda_res.transformed[2][0]


def test_research_bootstrap_and_anova():
    """Verify bootstrap confidence interval and one-way ANOVA F-statistic."""
    sample = [10.0, 11.0, 9.5, 10.5, 10.2, 9.8]
    ci_res = research_bootstrap_ci(sample, n_bootstraps=500, alpha=0.05)
    assert ci_res.ci_lower < ci_res.point_estimate < ci_res.ci_upper

    group1 = [1.0, 2.0, 3.0]
    group2 = [10.0, 11.0, 12.0]
    group3 = [20.0, 21.0, 22.0]
    anova_res = research_anova_oneway(group1, group2, group3)
    assert anova_res.f_statistic > 50.0  # Strongly different groups


def test_graphics_perlin_and_bezier():
    """Verify Perlin noise range and cubic Bezier curve evaluation."""
    n1 = graphics_perlin_noise_2d(1.5, 2.5)
    assert -1.5 <= n1 <= 1.5

    fbm = graphics_fbm_noise_2d(3.0, 4.0, octaves=4)
    assert -1.5 <= fbm <= 1.5

    # Bezier curve from (0, 0) to (10, 10)
    p0 = (0.0, 0.0)
    p1 = (0.0, 5.0)
    p2 = (5.0, 10.0)
    p3 = (10.0, 10.0)
    start_pt = graphics_bezier_evaluate(p0, p1, p2, p3, 0.0)
    mid_pt = graphics_bezier_evaluate(p0, p1, p2, p3, 0.5)
    end_pt = graphics_bezier_evaluate(p0, p1, p2, p3, 1.0)

    assert start_pt == (0.0, 0.0)
    assert end_pt == (10.0, 10.0)
    assert 0.0 < mid_pt[0] < 10.0
    assert 0.0 < mid_pt[1] < 10.0


def test_quantum_stabilizer_and_steane():
    """Verify Clifford stabilizer Bell state and Steane 7-qubit syndrome diagnosis."""
    # Create Bell state |Phi+> = (H on 0, CNOT 0->1)
    res = quantum_stabilizer_simulate(2, [("H", [0]), ("CNOT", [0, 1])])
    stabilizers = res["stabilizers"]
    assert "+XX" in stabilizers
    assert "+ZZ" in stabilizers

    # Steane code syndrome diagnosis for bit flip on qubit 3 (index 2)
    # H row 3 has bit 1 at col 0, 2, 4, 6
    bit_err = [0, 0, 1, 0, 0, 0, 0]  # bit flip at qubit index 2 (qubit 3)
    phase_err = [0, 0, 0, 0, 0, 0, 0]
    diag = quantum_steane_diagnose(bit_err, phase_err)
    assert diag.bit_flip_error_qubit == 2
    assert diag.phase_flip_error_qubit is None
