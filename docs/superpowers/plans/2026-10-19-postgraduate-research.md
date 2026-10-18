# Postgraduate & PhD Research Computing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend DoomScript into a publication-grade postgraduate and PhD research computing language capable of advanced graph theory, statistical inference (Welch $t$, Mann-Whitney $U$, ANOVA, Chi-Square, BCa bootstrap, MCMC), and reverse-mode autograd with scalar/tensor optimizers, expressed in genuine, readable English under strict reproducibility guarantees.

**Architecture:** A zero-mandatory-dependency modular research package (`src/doomscript/research/`) providing an isolated 64-bit deterministic PRNG, exact numerical distributions (regularized incomplete beta/gamma with direct survival functions), graph algorithms with deterministic tie-breaking, reverse-mode autograd with relative-error gradient checking, and a single-source declarative phrase registry generating dual-form English grammar rules under a scoped `use research` block.

**Tech Stack:** Python 3.10+ Standard Library (`math`, `random`, `hashlib`, `ast`), with dev-only testing oracles (`scipy`, `numpy`, `networkx`, `torch` if present), Lark LALR(1) parser.

**Spec:** [`docs/superpowers/specs/2026-10-19-postgraduate-research-design.md`](file:///C:/Users/kanha/.gemini/antigravity/scratch/doomscript/docs/superpowers/specs/2026-10-19-postgraduate-research-design.md)

## Global Constraints
- Zero mandatory runtime dependencies: pure standard library default.
- Single-source deterministic PRNG: no global `random.seed()`; isolated per-session `ResearchRNG`.
- Strict `float64` policy across all operations and conversions (no silent `float32`).
- Direct survival function computation ($S(x) = 1 - CDF(x)$) to prevent catastrophic cancellation when $p < 10^{-15}$.
- Scoped activation: research verbs activated strictly under `use research`.
- Dual-form invariance: every research operation is defined once in `registry.py` and supports both statement (`test that ... into res`) and expression (`res's p value` / `p value of res`) forms.
- Natural English without underscores: `p value of res`, `learning rate 0.01`, `welch t test`.
- All tests must pass before each commit (`pytest -q` and corpus tests).

## Review Focus
1. **$p$-Value Catastrophic Cancellation**: Tests must assert that extremely small $p$-values ($p < 10^{-15}$) compute accurately via survival functions rather than rounding to $0.0$ or producing negative values.
2. **Deterministic PRNG Stream Isolation**: Two independent `ResearchSession` instances seeded with the same integer must produce bitwise identical pseudorandom streams regardless of Python minor version or OS.
3. **Dijkstra Negative Weight Rejection**: Graph with a negative edge weight passed to Dijkstra must raise `NegativeEdgeWeightError` with a friendly suggestion to use Bellman-Ford.
4. **MCMC Adaptive Tuning Freeze**: Metropolis-Hastings adaptive tuning of proposal variance must freeze completely after burn-in to maintain stationary Markov chain reversibility.
5. **Autograd Non-Differentiable Gradient Check**: Gradient checking across non-smooth functions (e.g., ReLU at $x=0$) must evaluate subgradient validity without throwing division-by-zero or failure errors.

---

### Task 1: Research Backend, Isolated PRNG & Provenance Tracker

**Files:**
- Create: `src/doomscript/research/__init__.py`
- Create: `src/doomscript/research/backend.py`
- Test: `tests/research/test_backend.py`

**Interfaces:**
- Produces:
  - `class ResearchRNG(seed: int)` with `.random() -> float`, `.uniform(a, b) -> float`, `.normal(mu, sigma) -> float`, `.sample(pop, k) -> list`.
  - `class ResearchSession(backend: str = "pure", seed: int = 42)` managing isolated context and execution provenance.
  - `get_active_session() -> ResearchSession` and `set_active_session(session: ResearchSession)`.
  - `get_provenance_log() -> dict` separating `deterministic` and `volatile` metadata.
  - `class UnsupportedBackendOperationError(Exception)`.

- [ ] **Step 1: Write the failing test**

```python
# tests/research/test_backend.py
import pytest
from doomscript.research.backend import ResearchRNG, ResearchSession, get_provenance_log

def test_prng_reproducibility():
    rng1 = ResearchRNG(seed=12345)
    rng2 = ResearchRNG(seed=12345)
    seq1 = [rng1.random() for _ in range(100)]
    seq2 = [rng2.random() for _ in range(100)]
    assert seq1 == seq2
    assert seq1[0] == pytest.approx(0.416673, rel=1e-4)

def test_provenance_log_separation():
    session = ResearchSession(backend="pure", seed=42)
    log = session.get_provenance()
    assert "deterministic" in log
    assert "volatile" in log
    assert log["deterministic"]["backend"] == "pure"
    assert log["deterministic"]["seed"] == 42
    assert "timestamp_utc" in log["volatile"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/research/test_backend.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.research'`

- [ ] **Step 3: Implement `backend.py` and `__init__.py`**

Implement deterministic 64-bit xoshiro/linear-congruential PRNG, isolated `ResearchSession`, thread-local or context-managed active session, and provenance serializer.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/research/test_backend.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/research/ tests/research/test_backend.py
git commit -m "feat(research): implement deterministic PRNG and backend provenance tracker"
```

---

### Task 2: Exact Numerical Distributions & Survival Functions

**Files:**
- Create: `src/doomscript/research/distributions.py`
- Test: `tests/research/test_distributions.py`

**Interfaces:**
- Consumes: `backend.py` (for precision and float64 math).
- Produces:
  - `gammainc(s: float, x: float) -> float` (regularized lower incomplete gamma $P(s, x)$).
  - `gammaincc(s: float, x: float) -> float` (regularized upper incomplete gamma survival $Q(s, x)$).
  - `betainc(a: float, b: float, x: float) -> float` (regularized incomplete beta $I_x(a, b)$ with symmetry switch).
  - `betaincc(a: float, b: float, x: float) -> float` (survival function $1 - I_x(a, b)$ computed directly).
  - `t_cdf(t: float, df: float) -> float` and `t_sf(t: float, df: float) -> float` (direct Student-$t$ survival).
  - `f_cdf(f: float, dfn: float, dfd: float) -> float` and `f_sf(f: float, dfn: float, dfd: float) -> float`.
  - `chi2_cdf(x: float, df: float) -> float` and `chi2_sf(x: float, df: float) -> float`.
  - `inv_t_cdf(p: float, df: float) -> float`, `inv_chi2_cdf(p: float, df: float) -> float`.

- [ ] **Step 1: Write the failing test**

```python
# tests/research/test_distributions.py
import pytest
import math
from doomscript.research.distributions import gammainc, gammaincc, betainc, betaincc, t_sf, f_sf, chi2_sf, inv_t_cdf

def test_incomplete_gamma_accuracy():
    # Tested against closed-form and high-precision references
    # P(1, x) = 1 - e^(-x)
    assert gammainc(1.0, 2.0) == pytest.approx(1.0 - math.exp(-2.0), rel=1e-10)
    assert gammaincc(1.0, 2.0) == pytest.approx(math.exp(-2.0), rel=1e-10)

def test_survival_function_prevents_cancellation():
    # Large t statistic gives tiny p-value that would cancel under 1.0 - cdf
    p_extreme = t_sf(25.0, df=30.0)
    assert p_extreme > 0.0
    assert p_extreme < 1e-20

def test_inv_t_cdf():
    # At df=10, 97.5% quantile is approx 2.22813885
    val = inv_t_cdf(0.975, df=10.0)
    assert val == pytest.approx(2.22813885, rel=1e-6)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/research/test_distributions.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.research.distributions'`

- [ ] **Step 3: Implement `distributions.py`**

Implement series expansion for incomplete gamma when $x < s+1$ and Legendre's continued fraction when $x \ge s+1$. Implement Lentz's continued fraction for incomplete beta with symmetry switch when $x > (a+1)/(a+b+2)$. Implement direct survival functions and Newton-Raphson/bisection quantile inverses.

- [ ] **Step 4: Run test to verify it passes (and compare against SciPy oracle if installed)**

Run: `python -m pytest tests/research/test_distributions.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/research/distributions.py tests/research/test_distributions.py
git commit -m "feat(research): implement numerical distributions and survival functions"
```

---

### Task 3: Statistical Inference Engine — Hypothesis Tests, BCa Bootstrap & MCMC

**Files:**
- Create: `src/doomscript/research/stats.py`
- Test: `tests/research/test_stats.py`

**Interfaces:**
- Consumes: `backend.py` (`ResearchSession`, `ResearchRNG`), `distributions.py` (survival & quantile functions).
- Produces:
  - `welch_t_test(a, b, alternative="two-sided") -> TestResult(statistic, p_value, df, effect_size)`
  - `student_t_test(a, b, alternative="two-sided") -> TestResult`
  - `mann_whitney_u_test(a, b, alternative="two-sided") -> TestResult(statistic, p_value, u_statistic)`
  - `one_way_anova(*groups) -> TestResult(statistic, p_value, eta_squared)`
  - `chi_square_independence(table) -> TestResult(statistic, p_value, dof, expected)`
  - `confidence_interval(data, confidence=0.95, statistic="mean") -> tuple[float, float]`
  - `bca_bootstrap(data, stat_func, n_resamples=2000, confidence=0.95) -> tuple[float, float]`
  - `adjust_p_values(p_values, method="holm") -> list[float]`
  - `metropolis_hastings(log_prob, initial, n_samples=5000, burn_in=0.2, n_chains=2) -> MCMCResult(samples, acceptance_rate, r_hat, ess)`

- [ ] **Step 1: Write the failing test**

```python
# tests/research/test_stats.py
import pytest
from doomscript.research.stats import welch_t_test, student_t_test, mann_whitney_u_test, one_way_anova, chi_square_independence, confidence_interval, bca_bootstrap, adjust_p_values, metropolis_hastings

def test_welch_t_test_unequal_variance():
    a = [20.1, 19.8, 20.4, 21.0, 19.5, 20.2]
    b = [22.5, 23.1, 21.9, 24.0, 22.8, 23.5]
    res = welch_t_test(a, b)
    assert res.p_value < 0.001
    assert res.statistic < 0.0
    assert "p_value" in dir(res)

def test_mann_whitney_exact_small_sample():
    a = [1, 2, 3]
    b = [4, 5, 6]
    res = mann_whitney_u_test(a, b)
    assert res.statistic == 0.0
    assert res.p_value == pytest.approx(0.1, rel=1e-3)

def test_mcmc_convergence_diagnostics():
    def log_target(x):
        return -0.5 * (x[0] ** 2)  # Standard normal
    res = metropolis_hastings(log_target, initial=[2.0], n_samples=2000, n_chains=2)
    assert res.r_hat < 1.10
    assert 0.15 <= res.acceptance_rate <= 0.65
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/research/test_stats.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.research.stats'`

- [ ] **Step 3: Implement `stats.py`**

Implement Welch and Student $t$-tests, Mann-Whitney $U$ with exact distribution for $n \le 20$ (no ties) and asymptotic correction, One-Way ANOVA, Chi-Square with Yates' correction, BCa bootstrap with jackknife acceleration and percentile fallback, Holm and Benjamini-Hochberg corrections, and Metropolis-Hastings with adaptive tuning during burn-in, split-$\hat{R}$, and ESS.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/research/test_stats.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/research/stats.py tests/research/test_stats.py
git commit -m "feat(research): implement statistical hypothesis testing, BCa bootstrap and MCMC"
```

---

### Task 4: Graph Algorithms & Dynamic Programming

**Files:**
- Create: `src/doomscript/research/graph.py`
- Create: `src/doomscript/research/algorithms.py`
- Test: `tests/research/test_graph_algorithms.py`

**Interfaces:**
- Produces:
  - `class ResearchGraph` with `.add_node(u)`, `.add_edge(u, v, weight=1.0)`.
  - `dijkstra_shortest_path(graph, src, dst) -> tuple[float, list]` (raises `NegativeEdgeWeightError` if negative weight encountered).
  - `bellman_ford(graph, src) -> tuple[dict, dict]` (raises `NegativeCycleError` if negative weight cycle detected).
  - `floyd_warshall(graph) -> tuple[dict, dict]`.
  - `topological_sort(graph) -> list` with deterministic insertion-order tie breaking.
  - `edmonds_karp_max_flow(graph, src, sink) -> float`.
  - `levenshtein_distance(s1, s2) -> int`.
  - `longest_common_subsequence(s1, s2) -> str`.
  - `knapsack_01(weights, values, capacity) -> tuple[float, list[int]]`.

- [ ] **Step 1: Write the failing test**

```python
# tests/research/test_graph_algorithms.py
import pytest
from doomscript.research.graph import ResearchGraph, dijkstra_shortest_path, bellman_ford, edmonds_karp_max_flow, NegativeEdgeWeightError, NegativeCycleError
from doomscript.research.algorithms import levenshtein_distance, longest_common_subsequence, knapsack_01

def test_dijkstra_negative_edge_rejection():
    g = ResearchGraph()
    g.add_edge("A", "B", -2.0)
    with pytest.raises(NegativeEdgeWeightError, match="Dijkstra does not support negative edge weights"):
        dijkstra_shortest_path(g, "A", "B")

def test_bellman_ford_negative_cycle():
    g = ResearchGraph()
    g.add_edge("A", "B", 1.0)
    g.add_edge("B", "C", -2.0)
    g.add_edge("C", "A", -1.0)
    with pytest.raises(NegativeCycleError, match="negative weight cycle"):
        bellman_ford(g, "A")

def test_dp_algorithms():
    assert levenshtein_distance("kitten", "sitting") == 3
    assert longest_common_subsequence("ABCBDAB", "BDCAB") == "BCAB"
    max_val, items = knapsack_01([2, 3, 4], [3, 4, 5], capacity=5)
    assert max_val == 7
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/research/test_graph_algorithms.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.research.graph'`

- [ ] **Step 3: Implement `graph.py` and `algorithms.py`**

Implement deterministic Dijkstra with insertion-order tie-breaking and negative weight check, Bellman-Ford with negative cycle detection, Floyd-Warshall, Edmonds-Karp maximum flow, Levenshtein distance, LCS, and 0/1 Knapsack.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/research/test_graph_algorithms.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/research/graph.py src/doomscript/research/algorithms.py tests/research/test_graph_algorithms.py
git commit -m "feat(research): implement graph algorithms with deterministic tie breaking and DP"
```

---

### Task 5: Scalar Autograd, Numerical Grad-Check & Optimizers

**Files:**
- Create: `src/doomscript/research/autograd.py`
- Create: `src/doomscript/research/tensor.py`
- Create: `src/doomscript/research/optim.py`
- Test: `tests/research/test_autograd_optim.py`

**Interfaces:**
- Produces:
  - `class Scalar(data: float, _children=(), _op="")` supporting `+`, `-`, `*`, `/`, `**`, `.exp()`, `.log()`, `.relu()`, `.tanh()`, `.sigmoid()`, `.backward()`.
  - `check_grad(func, x_values, eps=1e-6, rtol=1e-4) -> bool` (relative-error gradient check).
  - `class Tensor(data: list | float)` multidimensional wrapper around autograd Scalars with `.shape`, `.reshape()`, `.transpose()`, `.matmul()`, `.sum()`.
  - `class Adam(params: list[Scalar], lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8)` with `.step()`, `.zero_grad()`.
  - `class SGDMomentum(params: list[Scalar], lr=0.01, momentum=0.9)` with `.step()`, `.zero_grad()`.

- [ ] **Step 1: Write the failing test**

```python
# tests/research/test_autograd_optim.py
import pytest
from doomscript.research.autograd import Scalar, check_grad
from doomscript.research.optim import Adam

def test_autograd_chain_rule():
    x = Scalar(2.0)
    y = Scalar(-3.0)
    z = (x * y + Scalar(5.0)) ** 2
    z.backward()
    # dz/dx = 2 * (x * y + 5) * y = 2 * (-6 + 5) * (-3) = 6.0
    assert x.grad == pytest.approx(6.0, rel=1e-6)
    assert y.grad == pytest.approx(-4.0, rel=1e-6)

def test_relative_gradient_check():
    def f(v):
        return (v[0] ** 3) + (v[1] * v[0]).exp()
    assert check_grad(f, [1.5, 0.5]) is True

def test_adam_optimizer_step():
    w = Scalar(5.0)
    opt = Adam([w], lr=0.1)
    loss = (w - Scalar(1.0)) ** 2
    loss.backward()
    opt.step()
    assert w.data < 5.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/research/test_autograd_optim.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.research.autograd'`

- [ ] **Step 3: Implement `autograd.py`, `tensor.py`, and `optim.py`**

Implement reverse-mode topological autodiff on `Scalar`, numerical gradient checking using central differences with relative error metric, multidimensional `Tensor`, and state-tracked Adam / SGD with Momentum optimizers.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/research/test_autograd_optim.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/research/autograd.py src/doomscript/research/tensor.py src/doomscript/research/optim.py tests/research/test_autograd_optim.py
git commit -m "feat(research): implement scalar autograd, relative grad check, and Adam optimizer"
```

---

### Task 6: Single-Source Phrase Registry & Grammar Compiler Integration

**Files:**
- Create: `src/doomscript/research/registry.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `src/doomscript/runtime.py`
- Test: `tests/research/test_research_grammar.py`

**Interfaces:**
- Produces:
  - Declarative table mapping natural English research phrases to `doomscript.research.*` function and property calls.
  - Generates both statement form (`test that means of a and b are equal using welch t test into res`) and expression form (`res's p value` / `p value of res`).
  - Scoped activation: Normalizer detects `use research` and activates research rewrite rules.

- [ ] **Step 1: Write the failing test**

```python
# tests/research/test_research_grammar.py
from doomscript.compiler.engine import execute, export_to_python

def test_english_research_syntax(capsys):
    code = """
use research
a = a list of 10.0, 11.0, 12.0, 10.5
b = a list of 20.0, 21.0, 20.5, 22.0
test that means of a and b are equal using welch t test into res
p = res's p value
say "P-value is under 0.01:", p is under 0.01
verify that p is under 0.001 otherwise "Significantly different"
"""
    execute(code)
    captured = capsys.readouterr()
    assert "P-value is under 0.01: True" in captured.out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/research/test_research_grammar.py -v`  
Expected: FAIL with Lark syntax error or unrecognized command

- [ ] **Step 3: Implement `registry.py` and integrate with `phrases.py`**

Register research multi-word anchors in `registry.py`. In `phrases.py`, recognize `use research` block context, mapping research statements and expressions to canonical `doomscript.research.*` calls without raw Python underscore names.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/research/test_research_grammar.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/research/registry.py src/doomscript/grammar/phrases.py src/doomscript/runtime.py tests/research/test_research_grammar.py
git commit -m "feat(research): implement declarative research phrase registry and compiler integration"
```

---

### Task 7: 50-Program Postgraduate Research Held-Out Benchmark Corpus

**Files:**
- Create: `tests/research/corpus/` (50 `.doom` programs covering Advanced Algorithms, Statistics, and AI/Optimization)
- Create: `run_research_capability.py`
- Test: `tests/research/test_research_corpus.py`

**Interfaces:**
- Produces:
  - 50 fully runnable, publication-grade research programs in 100% natural English.
  - Automated benchmark runner `run_research_capability.py` reporting pass rate and execution time.
  - Assertion that pass rate $\ge 95.0\%$ across all categories.

- [ ] **Step 1: Author 50 held-out research benchmark scripts**

Create:
- 15 Advanced Algorithms & Graphs: Dijkstra, Bellman-Ford, Floyd-Warshall, Topological Sort, Max Flow, Min Cut, Kruskal's MST, A* Search, Levenshtein, LCS, Knapsack, Matrix Chain, Longest Increasing Subsequence, Strongly Connected Components, PageRank.
- 15 Statistical Inference & Research: Welch $t$-test, Student $t$-test, Paired $t$-test, Mann-Whitney $U$, Wilcoxon Signed-Rank, One-Way ANOVA, Two-Way ANOVA, Chi-Square Independence, Fisher's Exact, Pearson & Spearman Correlation, BCa Bootstrap, Wilson Score Interval, Holm Correction, Benjamini-Hochberg FDR, Metropolis-Hastings MCMC.
- 20 Machine Learning, Optimization & Autograd: Scalar Autograd backprop, Relative gradient checking, Linear regression loss minimization with Adam, Logistic regression with SGD momentum, Multi-layer perceptron forward/backward, Softmax cross-entropy, K-Means clustering, PCA via power iteration, Matrix decomposition, Learning rate warmup scheduler.

- [ ] **Step 2: Implement `run_research_capability.py`**

Runner compiles, executes, and validates all 50 scripts with structured terminal outputs.

- [ ] **Step 3: Run capability runner and verify 100% pass rate**

Run: `python run_research_capability.py`  
Expected: 50/50 passed (100.0%)

- [ ] **Step 4: Run full regression suites**

Run: `python -m pytest -q`  
Run: `python run_corpus.py --fail-under 95`  
Expected: All suites pass 100%.

- [ ] **Step 5: Update CHANGELOG.md and commit**

```bash
git add tests/research/ run_research_capability.py CHANGELOG.md
git commit -m "feat(research): add 50-program postgraduate research corpus and capability runner"
```
