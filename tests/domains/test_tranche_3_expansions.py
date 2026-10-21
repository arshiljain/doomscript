"""Unit tests for Tranche 3 Domain Expansions (dsa, bio, symbolic)."""

import math
import pytest
from doomscript.domains.dsa.runtime import (
    DisjointSparseTable,
    SegmentTree2D,
    WaveletMatrix,
    dsa_disjoint_sparse_table,
    dsa_segment_tree_2d,
)
from doomscript.domains.bio.runtime import (
    ProfileHiddenMarkovModel,
    CodonOptimizationSolver,
    bio_profile_hmm_fit,
    bio_codon_optimize,
)
from doomscript.domains.symbolic.runtime import (
    ChebyshevPolynomialApproximation,
    ContinuedFractionExpander,
    symbolic_chebyshev_t,
    symbolic_chebyshev_nodes,
    symbolic_continued_fraction,
)


def test_dsa_disjoint_sparse_table():
    """Verify O(1) range minimum query on random integer array."""
    arr = [7, 2, 8, 4, 1, 9, 3, 5, 6, 0, 11, 2]
    dst = dsa_disjoint_sparse_table(arr, op="min")

    assert dst.query(0, 4) == 1
    assert dst.query(1, 3) == 2
    assert dst.query(0, len(arr) - 1) == 0
    assert dst.query(5, 7) == 3


def test_dsa_segment_tree_2d():
    """Verify 2D subgrid range minimum queries."""
    matrix = [
        [10.0, 20.0, 30.0],
        [40.0,  5.0, 60.0],
        [70.0, 80.0, 90.0]
    ]
    st2d = dsa_segment_tree_2d(matrix, op="min")

    assert st2d.query(0, 0, 2, 2) == 5.0
    assert st2d.query(0, 0, 0, 2) == 10.0
    assert st2d.query(1, 1, 2, 2) == 5.0
    assert st2d.query(2, 0, 2, 2) == 70.0


def test_dsa_wavelet_matrix():
    """Verify Wavelet Matrix rank query."""
    arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]
    wm = WaveletMatrix(arr)

    # Count occurrences of 5 in prefix up to index 9
    assert wm.rank(5, 9) == 2
    assert wm.rank(5, len(arr)) == 3
    assert wm.rank(1, len(arr)) == 2


def test_bio_profile_hmm_and_codon_optimizer():
    """Verify Profile HMM and Codon usage optimization."""
    alignments = [
        "ATGCATGC",
        "ATGCATGC",
        "ATGAATGC",
        "ATGCATGC"
    ]
    hmm_res = bio_profile_hmm_fit(alignments, length=8)
    assert hmm_res.length == 8
    assert hmm_res.sample_score < 0.0  # Log-likelihood

    # Codon optimization
    prot = "MKTIIALSYIFCLVFA"
    opt_res = bio_codon_optimize(prot)
    assert opt_res.protein_length == len(prot)
    assert len(opt_res.optimized_dna) == len(prot) * 3
    assert 0.3 < opt_res.gc_content < 0.7


def test_symbolic_chebyshev_and_continued_fractions():
    """Verify Chebyshev polynomial recurrence and continued fraction convergents."""
    # T0(x)=1, T1(x)=x, T2(x)=2x^2-1, T3(x)=4x^3-3x
    x = 0.5
    assert symbolic_chebyshev_t(0, x) == 1.0
    assert symbolic_chebyshev_t(1, x) == 0.5
    assert symbolic_chebyshev_t(2, x) == pytest.approx(2 * 0.25 - 1.0)
    assert symbolic_chebyshev_t(3, x) == pytest.approx(4 * 0.125 - 3 * 0.5)

    # Chebyshev nodes
    nodes = symbolic_chebyshev_nodes(5, a=-1.0, b=1.0)
    assert len(nodes) == 5
    assert -1.0 < nodes[0] < nodes[-1] < 1.0

    # Continued fraction for pi
    cf = symbolic_continued_fraction(math.pi, max_terms=5)
    assert cf.terms[0] == 3
    assert cf.terms[1] == 7
    # 355/113 is famous convergent for pi
    conv_strs = [f"{p}/{q}" for p, q in cf.convergents]
    assert "22/7" in conv_strs or "355/113" in conv_strs
