# Postgraduate & PhD Research Specification: English Scientific Computing & Statistical Inference

**Date**: 2026-10-19  
**Status**: APPROVED / SPECIFICATION  
**Scope**: Graduate & Research Computing (Algorithms, Statistical Inference, Autograd & Deep Learning)  
**Target Path**: `src/doomscript/research/` & `src/doomscript/grammar/phrases.py`

---

## 1. Vision & Core Philosophy

DoomScript enables graduate students, researchers, and data scientists to write rigorous, publication-grade computational logic in **idiomatic, readable English**.

Rather than wrapping Python libraries in superficial syntax or slipping into Python muscle memory, DoomScript provides a **Controlled Natural Language (CNL)** for research that is:
1. **Uncompromising on Scientific Reproducibility**: Deterministic single-source PRNG, explicit backends (no silent auto-switching), explicit float64 precision, and tamper-evident run provenance logs.
2. **Mathematically & Statistically Rigorous**: Exact distribution functions (regularized incomplete beta and gamma with direct survival functions), Welch's $t$-test defaults, Mann-Whitney $U$ with exact small-sample distributions and continuity corrections, Gelman-Rubin $\hat{R}$ and ESS diagnostics for MCMC, and deterministic tie-breaking for graphs.
3. **Dual-Form Symmetry from a Single Source of Truth**: All research constructs are defined once in a declarative registry that generates statement forms (`test that ... into res`), expression forms (`res = test that ...`), possessives (`res's p value`), LSP completions, and CLI suggestions without drift.
4. **Scoped to Prevent Keyword Collisions**: Activated strictly via `use research` (or `use research backend "pure"`), keeping the base English grammar lightweight and collision-free.
5. **Zero Mandatory Runtime Dependencies**: Complete pure-Python reference implementations using standard library `math` and `random`, with optional, explicit acceleration via NumPy, SciPy, or PyTorch.

---

## 2. Architecture & Modular Package Design

The research engine lives in `src/doomscript/research/`:

```
src/doomscript/research/
├── __init__.py           # Package facade & lazy submodule loader
├── backend.py            # Backend registry, deterministic PRNG, provenance tracking
├── registry.py           # Single source of truth for research phrases and dual forms
├── distributions.py      # Incomplete gamma/beta, quantile functions, direct survival functions
├── stats.py              # Welch/Student t-test, Mann-Whitney U, ANOVA, Chi-square, BCa bootstrap, MCMC
├── graph.py              # Directed/weighted graph, Dijkstra, Bellman-Ford, Floyd-Warshall, Max Flow
├── algorithms.py         # Dynamic programming (Levenshtein, LCS, Knapsack, Matrix Chain)
├── autograd.py           # Scalar reverse-mode autograd, computational graph, relative grad-check
├── tensor.py             # Multidimensional pure-Python Tensor wrapping autograd scalars
└── optim.py              # SGD with momentum, Adam, RMSprop with explicit state dictionaries
```

---

## 3. Reproducibility & Backend Architecture

### 3.1 Explicit Backend Selection (No Silent Switching)
Auto-switching based on environment packages breaks scientific reproducibility. Therefore, the backend must always be explicit:
* **Default Backend**: `"pure"` (100% pure Python, zero dependencies).
* **Optional Backends**: `"numpy"`, `"torch"`.
* **Activation**:
  ```doomscript
  use research
  # or
  use research backend "numpy"
  ```
* **Capability Matrix & Unsupported Operations**:
  If a backend does not implement a given research verb, it raises `UnsupportedBackendOperationError("Operation '...' is not supported by backend 'numpy'. Use backend 'pure' or specify fallback.")`.

| Feature | `pure` | `numpy` | `torch` |
| :--- | :---: | :---: | :---: |
| Deterministic PRNG | Yes (Internal) | Yes (Seeded from Pure PRNG) | Yes (Seeded from Pure PRNG) |
| Distributions & Stats | Full Pure Implementation | Accelerated Array Ops | Ops via Pure Bridge |
| Graph & DP | Full Pure Implementation | Pure / NetworkX Oracle | Pure / NetworkX Oracle |
| Autograd & Tensors | Scalar / Tensor (Pedagogical) | Array Math | Native `torch.Tensor` (float64) |
| Bitwise Reproducibility | Guaranteed Cross-Platform | Platform-dependent BLAS | CPU deterministic; GPU non-deterministic flag recorded |

### 3.2 Single-Source Deterministic PRNG
* Randomness is generated exclusively by an internal, platform-independent 64-bit PRNG (`research.backend.ResearchRNG`) based on a seedable linear-feedback or xoshiro generator derived from 64-bit seeds.
* Python's standard `random.randint` or `random.choice` are **never** used directly because their implementations vary across Python minor versions.
* Every run instantiates its own isolated `ResearchRNG` context—**no global shared state**.
* When using `"numpy"` or `"torch"` backends, array buffers are filled deterministically by `ResearchRNG` before transfer.

### 3.3 Strict `float64` Policy
* All statistical tests, distributions, and tensor computations operate strictly in IEEE 754 double precision (`float64`).
* Conversions to PyTorch tensors must always specify `dtype=torch.float64` to prevent silent truncation to `float32`.

### 3.4 Reproducibility Provenance Log
Every program running under `use research` automatically records a provenance log separated into deterministic and volatile metadata:
```python
{
    "deterministic": {
        "backend": "pure",
        "seed": 42,
        "doomscript_version": "1.1.0",
        "python_version": "3.14.7",
        "blas_threads": 1,
        "input_checksums": {
            "sample_a": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        }
    },
    "volatile": {
        "timestamp_utc": "2026-10-19T03:30:00Z",
        "hostname": "research-node-01",
        "execution_seconds": 0.428
    }
}
```
Two runs with identical `deterministic` blocks are guaranteed to yield identical results.

---

## 4. Statistical Inference Engine Specifications

### 4.1 Numerical Distributions (`distributions.py`)
* **Incomplete Gamma Function $P(s, x)$**:
  * For $x < s + 1$: Computed via regularized Taylor series expansion:
    $$P(s, x) = \frac{e^{-x} x^s}{\Gamma(s)} \sum_{k=0}^{\infty} \frac{x^k}{s (s+1) \cdots (s+k)}$$
  * For $x \ge s + 1$: Computed via Legendre's continued fraction:
    $$Q(s, x) = 1 - P(s, x) = \frac{e^{-x} x^s}{\Gamma(s)} \frac{1}{x + \frac{1 - s}{1 + \frac{1}{x + \frac{2 - s}{1 + \dots}}}}$$
* **Incomplete Beta Function $I_x(a, b)$**:
  * Evaluated via Lentz's continued fraction method.
  * Uses the symmetry relation $I_x(a, b) = 1 - I_{1-x}(b, a)$ whenever $x > (a + 1) / (a + b + 2)$ to ensure rapid, unconditional convergence.
* **Direct Survival Functions**:
  * All $p$-values evaluate survival functions $S(x) = 1 - CDF(x)$ directly via upper incomplete functions rather than computing $1.0 - CDF(x)$, preventing catastrophic precision loss when $p < 10^{-15}$.
* **Quantile / Inverse CDF Functions**:
  * Inverse normal using Acklam's algorithm.
  * Inverse Student-$t$, Snedecor-$F$, and Chi-Square using Newton-Raphson iteration with bisection safeguard.

### 4.2 Hypothesis Testing & Defaults (`stats.py`)
1. **Two-Sample $t$-Test**:
   * **Default**: Welch's $t$-test (unequal variance, Welch-Satterthwaite degrees of freedom).
   * **Alternative**: Student's $t$-test (pooled variance) via `using student t test`.
   * **Hypothesis Phrasings**:
     * `test that means of sample_a and sample_b are equal using welch t test into result`
     * Alternatives: `with alternative "two-sided"`, `with alternative "greater"`, `with alternative "less"`.
2. **Mann-Whitney $U$ Test**:
   * Evaluates rank sums for non-parametric comparison.
   * **Exact Distribution**: Used when $\max(n_1, n_2) \le 20$ and there are no ties.
   * **Asymptotic Normal Approximation**: Used when $\max(n_1, n_2) > 20$ or ties exist, with full tie adjustment:
     $$\sigma_U = \sqrt{\frac{n_1 n_2}{12} \left( (n_1 + n_2 + 1) - \frac{\sum (t_i^3 - t_i)}{(n_1 + n_2)(n_1 + n_2 - 1)} \right)}$$
     and continuity correction $\pm 0.5$.
3. **One-Way ANOVA**:
   * Computes between-group variance ($SSB, df_b$) and within-group variance ($SSW, df_w$), reporting $F$-statistic, $p$-value, and effect size $\eta^2$.
4. **Chi-Square Test of Independence**:
   * Evaluates $R \times C$ contingency tables with expected frequencies $E_{ij} = (R_i C_j) / N$.
   * Applies Yates' continuity correction automatically for $2 \times 2$ tables.
5. **Effect Sizes**:
   * Cohen's $d$ and Hedges' $g$ (bias-corrected for small samples):
     $$g = d \times \left(1 - \frac{3}{4(n_1 + n_2) - 9}\right)$$
6. **Multiple Testing Corrections**:
   * `adjust p values in p_list using holm into adjusted` (Holm-Bonferroni step-down).
   * `adjust p values in p_list using benjamini hochberg into adjusted` (FDR).
7. **Confidence Intervals**:
   * Student-$t$ confidence interval for means.
   * Wilson score interval for binomial proportions.
8. **BCa (Bias-Corrected and Accelerated) Bootstrap**:
   * Default: 2,000 resamples.
   * Jackknife estimation of acceleration parameter $a$.
   * Fallback: If variance of jackknife resamples is zero or $N < 8$, falls back gracefully to percentile bootstrap and issues a warning.
9. **MCMC (Metropolis-Hastings)**:
   * Mandatory burn-in (default 20%).
   * Adaptive proposal standard deviation tuned **only during burn-in** (targeting acceptance rate $0.234$ for multi-dimensional, $0.44$ for 1D). Adaptation is strictly frozen after burn-in to preserve stationary Markov chain properties.
   * Diagnostics: Split-$\hat{R}$ (Gelman-Rubin convergence diagnostic; warns if $\hat{R} > 1.05$) and Effective Sample Size (ESS) via autocorrelation time. Rejects non-finite log-densities ($-\infty$).

---

## 5. Graph Theory & Combinatorial Algorithms

### 5.1 Deterministic Graph Specifications (`graph.py`)
* **Tie-Breaking Rule**: When priority values or distances are identical, nodes resolve strictly by **insertion order** (creation sequence), guaranteeing identical traversal orders across platforms.
* **Negative Edge Weights**:
  * Dijkstra checks all edge weights and raises `NegativeEdgeWeightError("Dijkstra does not support negative edge weights (found weight w). Use Bellman-Ford instead.")`.
* **Negative Cycles**:
  * Bellman-Ford performs $V-1$ relaxation passes; on pass $V$, any relaxation raises `NegativeCycleError("Graph contains a negative weight cycle reachable from source.")`.
* **Parallel Edges & Self-Loops**:
  * Multigraph edges preserve distinct identifiers; simple graph methods default to the minimum weight parallel edge.

### 5.2 Dynamic Programming Primitives (`algorithms.py`)
* `edit distance between seq1 and seq2` (Levenshtein distance with insertions, deletions, substitutions).
* `longest common subsequence of seq1 and seq2`.
* `knapsack with weights w and values v for capacity c`.
* `matrix chain order for dimensions dims`.

---

## 6. Autograd & Deep Learning Specifications

### 6.1 Pure-Python Scalar Reverse-Mode Autograd (`autograd.py`)
* Scalar graph structure (`Scalar(data, creator, op)`).
* Forward operations build a Directed Acyclic Graph (DAG) with topological sorting on `.backward()`.
* Supported operations: addition, subtraction, multiplication, division, power, exp, log, relu, tanh, sigmoid.
* **Numerical Gradient Check (`check_grad`)**:
  * Validates analytical gradients against two-point central difference $\frac{f(x + \epsilon) - f(x - \epsilon)}{2\epsilon}$ with $\epsilon = 10^{-6}$.
  * Evaluates relative error:
    $$\frac{|\nabla_{ana} - \nabla_{num}|}{\max(|\nabla_{ana}|, |\nabla_{num}|, 10^{-7})} \le 10^{-4}$$
  * Smoothly handles non-differentiable points (e.g. ReLU at $0$) by checking subgradient membership.

### 6.2 Pure-Python Multidimensional Tensor (`tensor.py`)
* Pedagogical N-dimensional tensor wrapping autograd scalars.
* Shape manipulation: `reshape`, `transpose`, broadcasting across matching dimensions.
* Matrix multiplication (`matmul`), 2D dot products, batch operations.
* Documented performance boundary: Explicit warning if tensor elements exceed $10^5$ on pure backend.

### 6.3 Optimizers (`optim.py`)
* Explicit state dictionaries tracking step counts, first moments ($m_t$), and second moments ($v_t$):
  * **SGD with Momentum**: Velocity accumulation $v_{t+1} = \beta v_t + \nabla L$.
  * **Adam**: Bias-corrected first and second moments:
    $$m_t = \beta_1 m_{t-1} + (1-\beta_1) g_t, \quad v_t = \beta_2 v_{t-1} + (1-\beta_2) g_t^2$$
    $$\hat{m}_t = \frac{m_t}{1 - \beta_1^t}, \quad \hat{v}_t = \frac{v_t}{1 - \beta_2^t}, \quad \theta_t = \theta_{t-1} - \frac{\alpha}{\sqrt{\hat{v}_t} + \epsilon} \hat{m}_t$$

---

## 7. Single Source of Truth Phrase Registry (`registry.py`)

All English research phrases are registered in a single declarative table. One entry automatically generates:
1. Lark grammar rules (both statement and expression forms).
2. AST code generation mapping.
3. Natural English aliases and possessives (`res's p value` $\leftrightarrow$ `p value of res`).
4. Interactive `doom suggest` entries and LSP autocompletions.
5. Documentation and corpus test stubs.

### 7.1 Natural English Syntax Rules
* **No Raw Identifiers with Underscores**: Research phrases use spaces: `p value of res`, `learning rate 0.01`, `welch t test`.
* **Dual Form Invariance**: Every research query exists symmetrically as both a statement and an expression:
  * *Statement*: `test that means of a and b are equal using welch t test into res`
  * *Expression*: `res = test that means of a and b are equal using welch t test`
  * *Property Statement*: `p value of res into p`
  * *Property Expression*: `p = p value of res` or `p = res's p value`

### 7.2 Core Research Verbal Forms

| Concept | Canonical Statement Form | Canonical Expression Form |
| :--- | :--- | :--- |
| **$t$-Test** | `test that means of A and B are equal using welch t test into res` | `test that means of A and B are equal using welch t test` |
| **Mann-Whitney** | `test that distributions of A and B are equal using mann whitney into res` | `test that distributions of A and B are equal using mann whitney` |
| **ANOVA** | `test that means of groups are equal using one way anova into res` | `one way anova of groups` |
| **Chi-Square** | `test independence of table using chi square into res` | `chi square test of table` |
| **CI** | `confidence interval of data at 95 percent into ci` | `confidence interval of data at 95 percent` |
| **Bootstrap** | `bootstrap sample data with 2000 resamples into dist` | `bootstrap sample of data with 2000 resamples` |
| **MCMC** | `sample posterior of log_post with 5000 iterations into chain` | `sample posterior of log_post with 5000 iterations` |
| **Dijkstra** | `find shortest path from u to v in g using dijkstra into path` | `shortest path from u to v in g using dijkstra` |
| **Max Flow** | `find maximum flow from s to t in g into flow` | `maximum flow from s to t in g` |
| **Edit Dist** | `edit distance between s1 and s2 into d` | `edit distance between s1 and s2` |
| **LCS** | `longest common subsequence of s1 and s2 into lcs` | `longest common subsequence of s1 and s2` |
| **Autograd** | `gradient of loss with respect to w into grad` | `gradient of loss with respect to w` |

---

## 8. Verification & Acceptance Criteria

### 8.1 Numerical Oracle Tolerances
Tested against SciPy, NumPy, and PyTorch (if present in development environment) and verified against closed-form analytical solutions:

| Function | Comparison Metric | Tolerance (`rtol` / `atol`) |
| :--- | :--- | :--- |
| Incomplete Gamma $P(s, x)$ | SciPy `gammainc` | `rtol=1e-10`, `atol=1e-12` |
| Incomplete Beta $I_x(a, b)$ | SciPy `betainc` | `rtol=1e-10`, `atol=1e-12` |
| Welch $t$-test statistic & $p$ | SciPy `ttest_ind(..., equal_var=False)` | `rtol=1e-6`, `atol=1e-9` |
| Mann-Whitney $U$ statistic & $p$ | SciPy `mannwhitneyu` | `rtol=1e-6`, `atol=1e-9` |
| ANOVA $F$-statistic & $p$ | SciPy `f_oneway` | `rtol=1e-6`, `atol=1e-9` |
| Chi-Square independence | SciPy `chi2_contingency` | `rtol=1e-6`, `atol=1e-9` |
| Dijkstra & Bellman-Ford | NetworkX shortest paths | Exact path match |
| Autograd gradients | Analytical Central Difference | Relative error $\le 10^{-4}$ |

### 8.2 Research Phrase Held-Out Corpus
A dedicated benchmark suite of 50 postgraduate research programs (`tests/research/corpus/`) spanning all domains, completely held out from training examples, must compile, execute, and assert with a 100% pass rate.

---

## 9. Implementation Milestones

1. **Milestone 1**: `src/doomscript/research/backend.py` (Isolated `ResearchRNG`, explicit backend registry, provenance log).
2. **Milestone 2**: `src/doomscript/research/distributions.py` (Incomplete gamma/beta, quantile functions, direct survival functions, SciPy oracle tests).
3. **Milestone 3**: `src/doomscript/research/stats.py` (Welch/Student $t$-test, Mann-Whitney $U$, ANOVA, Chi-square, BCa bootstrap, MCMC with $\hat{R}$ and ESS).
4. **Milestone 4**: `src/doomscript/research/graph.py` & `algorithms.py` (Dijkstra, Bellman-Ford, Floyd-Warshall, Max Flow, DP primitives).
5. **Milestone 5**: `src/doomscript/research/autograd.py`, `tensor.py`, `optim.py` (Scalar autograd, numerical grad-check, tensor ops, Adam/SGD).
6. **Milestone 6**: `src/doomscript/research/registry.py` & Grammar integration (Dual-form research phrases under `use research`, compiler AST emission).
7. **Milestone 7**: 50 Postgraduate research benchmark programs & CI verification.
