"""
DoomScript Research Statistical Inference Engine:
Hypothesis Testing, Confidence Intervals, BCa Bootstrap, and Diagnostic MCMC.
"""

import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from .backend import get_active_session
from .distributions import (
    t_cdf,
    t_sf,
    f_sf,
    chi2_sf,
    normal_sf,
    inv_normal_cdf,
    inv_t_cdf,
)


class TestResult(dict):
    """Encapsulates hypothesis test results with attribute and dictionary access."""
    __test__ = False

    def __init__(
        self,
        statistic: float,
        p_value: float,
        test_name: str,
        df: Optional[float] = None,
        effect_size: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__()
        self["statistic"] = float(statistic)
        self["p_value"] = float(p_value)
        self["test_name"] = str(test_name)
        self["df"] = df
        self["effect_size"] = effect_size
        self["details"] = details or {}

    @property
    def statistic(self) -> float:
        return self["statistic"]

    @property
    def p_value(self) -> float:
        return self["p_value"]

    @property
    def test_name(self) -> str:
        return self["test_name"]

    @property
    def df(self) -> Optional[float]:
        return self["df"]

    @property
    def effect_size(self) -> Optional[float]:
        return self["effect_size"]

    @property
    def details(self) -> Dict[str, Any]:
        return self["details"]

    def __repr__(self) -> str:
        s = f"TestResult({self.test_name}: statistic={self.statistic:.4f}, p_value={self.p_value:.4e}"
        if self.df is not None:
            s += f", df={self.df:.2f}"
        if self.effect_size is not None:
            s += f", effect_size={self.effect_size:.4f}"
        s += ")"
        return s


class MCMCResult:
    """Encapsulates Markov Chain Monte Carlo posterior samples and convergence diagnostics."""

    def __init__(
        self,
        samples: List[List[float]],
        acceptance_rate: float,
        r_hat: float,
        ess: float,
        chains: List[List[List[float]]],
    ):
        self.samples = samples
        self.acceptance_rate = acceptance_rate
        self.r_hat = r_hat
        self.ess = ess
        self.chains = chains

    def __repr__(self) -> str:
        return (
            f"MCMCResult({len(self.samples)} samples, "
            f"acceptance_rate={self.acceptance_rate:.2%}, "
            f"R_hat={self.r_hat:.3f}, ESS={self.ess:.1f})"
        )


def _mean(data: list) -> float:
    return sum(data) / len(data)


def _var(data: list, ddof: int = 1) -> float:
    n = len(data)
    if n <= ddof:
        return 0.0
    m = _mean(data)
    return sum((x - m) ** 2 for x in data) / (n - ddof)


def _std(data: list, ddof: int = 1) -> float:
    return math.sqrt(_var(data, ddof=ddof))


# ---------------------------------------------------------------------------
# Hypothesis Testing
# ---------------------------------------------------------------------------

def welch_t_test(a: list, b: list, alternative: str = "two-sided") -> TestResult:
    """Welch's t-test for unequal variances (Default two-sample t-test)."""
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        raise ValueError("Each sample must contain at least 2 observations.")

    m1, m2 = _mean(a), _mean(b)
    v1, v2 = _var(a, ddof=1), _var(b, ddof=1)
    se1, se2 = v1 / n1, v2 / n2
    se = math.sqrt(se1 + se2)

    if se < 1e-15:
        t_stat = 0.0
        df = float(n1 + n2 - 2)
    else:
        t_stat = (m1 - m2) / se
        df = ((se1 + se2) ** 2) / ((se1 ** 2) / (n1 - 1) + (se2 ** 2) / (n2 - 1))

    # P-value calculation using direct survival
    alt = alternative.lower().strip()
    if alt in ("two-sided", "two_sided"):
        p_val = 2.0 * t_sf(abs(t_stat), df)
    elif alt == "greater":
        p_val = t_sf(t_stat, df)
    elif alt == "less":
        p_val = t_cdf(t_stat, df)
    else:
        raise ValueError(f"Unknown alternative: {alternative}. Must be 'two-sided', 'greater', or 'less'.")

    p_val = min(1.0, max(0.0, p_val))

    # Effect size: Cohen's d and Hedges' g
    pooled_sd = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / max(1, n1 + n2 - 2))
    cohen_d = (m1 - m2) / pooled_sd if pooled_sd > 1e-15 else 0.0
    j_factor = 1.0 - 3.0 / (4.0 * (n1 + n2) - 9.0) if (n1 + n2) > 2 else 1.0
    hedges_g = cohen_d * j_factor

    return TestResult(
        statistic=t_stat,
        p_value=p_val,
        test_name="Welch's t-test",
        df=df,
        effect_size=hedges_g,
        details={"m1": m1, "m2": m2, "cohen_d": cohen_d, "hedges_g": hedges_g},
    )


def student_t_test(a: list, b: list, alternative: str = "two-sided") -> TestResult:
    """Student's two-sample t-test assuming equal variances."""
    n1, n2 = len(a), len(b)
    if n1 < 2 or n2 < 2:
        raise ValueError("Each sample must contain at least 2 observations.")

    m1, m2 = _mean(a), _mean(b)
    v1, v2 = _var(a, ddof=1), _var(b, ddof=1)
    df = float(n1 + n2 - 2)
    pooled_var = ((n1 - 1) * v1 + (n2 - 1) * v2) / df
    se = math.sqrt(pooled_var * (1.0 / n1 + 1.0 / n2))

    t_stat = (m1 - m2) / se if se > 1e-15 else 0.0

    alt = alternative.lower().strip()
    if alt in ("two-sided", "two_sided"):
        p_val = 2.0 * t_sf(abs(t_stat), df)
    elif alt == "greater":
        p_val = t_sf(t_stat, df)
    elif alt == "less":
        p_val = t_cdf(t_stat, df)
    else:
        raise ValueError(f"Unknown alternative: {alternative}")

    p_val = min(1.0, max(0.0, p_val))
    pooled_sd = math.sqrt(pooled_var)
    cohen_d = (m1 - m2) / pooled_sd if pooled_sd > 1e-15 else 0.0

    return TestResult(
        statistic=t_stat,
        p_value=p_val,
        test_name="Student's t-test",
        df=df,
        effect_size=cohen_d,
        details={"m1": m1, "m2": m2, "cohen_d": cohen_d},
    )


def mann_whitney_u_test(a: list, b: list, alternative: str = "two-sided") -> TestResult:
    """
    Mann-Whitney U non-parametric rank-sum test.
    Uses exact distribution for small samples (max(n1, n2) <= 20 and no ties)
    and asymptotic normal approximation with continuity and tie corrections otherwise.
    """
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        raise ValueError("Samples cannot be empty.")

    # Combine and rank
    combined = [(x, 0) for x in a] + [(y, 1) for y in b]
    combined.sort(key=lambda item: item[0])

    ranks = [0.0] * len(combined)
    i = 0
    ties = {}
    while i < len(combined):
        j = i
        while j < len(combined) and combined[j][0] == combined[i][0]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        tie_count = j - i
        if tie_count > 1:
            ties[combined[i][0]] = tie_count
        for k in range(i, j):
            ranks[k] = avg_rank
        i = j

    rank_sum_1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = rank_sum_1 - (n1 * (n1 + 1)) / 2.0
    u2 = n1 * n2 - u1
    u_stat = min(u1, u2)

    # Check exact vs asymptotic
    if max(n1, n2) <= 20 and len(ties) == 0:
        # Dynamic programming for exact distribution of U
        # p(u, n1, n2): number of subsets of size n1 having rank sum = u + n1(n1+1)/2
        max_u = int(n1 * n2)
        dp = [0] * (max_u + 1)
        dp[0] = 1
        for elem in range(1, n1 + n2 + 1):
            for u in range(max_u, elem - 1, -1):
                dp[u] += dp[u - elem]
        total_subsets = math.comb(n1 + n2, n1)
        target_u = int(math.floor(u_stat))
        # Cumulative sum of probabilities up to target_u
        p_lower = sum(dp[u] for u in range(0, target_u + 1)) / total_subsets
        p_val = min(1.0, 2.0 * p_lower)
    else:
        # Asymptotic normal approximation with tie correction
        mean_u = (n1 * n2) / 2.0
        tie_correction = sum((t ** 3 - t) for t in ties.values())
        n_total = n1 + n2
        var_u = (n1 * n2 / 12.0) * ((n_total + 1) - tie_correction / (n_total * (n_total - 1)))
        sd_u = math.sqrt(max(1e-15, var_u))

        # Continuity correction of 0.5 towards mean
        diff = u_stat - mean_u
        if diff < 0:
            diff += 0.5
        elif diff > 0:
            diff -= 0.5
        z = diff / sd_u
        p_val = 2.0 * normal_sf(abs(z))

    return TestResult(
        statistic=u_stat,
        p_value=min(1.0, max(0.0, p_val)),
        test_name="Mann-Whitney U test",
        df=None,
        effect_size=1.0 - (2.0 * u_stat) / (n1 * n2),  # Rank-biserial correlation
        details={"u1": u1, "u2": u2},
    )


def one_way_anova(*groups: list) -> TestResult:
    """One-way Analysis of Variance (ANOVA)."""
    k = len(groups)
    if k < 2:
        raise ValueError("At least 2 groups required for ANOVA.")

    all_data = []
    group_means = []
    group_sizes = []
    for g in groups:
        if len(g) == 0:
            raise ValueError("Group cannot be empty.")
        all_data.extend(g)
        group_means.append(_mean(g))
        group_sizes.append(len(g))

    total_n = len(all_data)
    grand_mean = _mean(all_data)

    ss_between = sum(n * (m - grand_mean) ** 2 for n, m in zip(group_sizes, group_means))
    ss_within = sum(sum((x - m) ** 2 for x in g) for g, m in zip(groups, group_means))
    df_between = k - 1
    df_within = total_n - k

    if df_within <= 0:
        raise ValueError("Not enough total observations for within-group variance.")

    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    f_stat = ms_between / ms_within if ms_within > 1e-15 else 0.0

    p_val = f_sf(f_stat, df_between, df_within)
    eta_sq = ss_between / (ss_between + ss_within) if (ss_between + ss_within) > 1e-15 else 0.0

    return TestResult(
        statistic=f_stat,
        p_value=p_val,
        test_name="One-way ANOVA",
        df=df_between,
        effect_size=eta_sq,
        details={"df_between": df_between, "df_within": df_within, "eta_squared": eta_sq},
    )


def chi_square_independence(table: List[List[Union[int, float]]]) -> TestResult:
    """Pearson's Chi-Square Test of Independence with Yates' correction for 2x2 tables."""
    rows = len(table)
    if rows < 2:
        raise ValueError("Table must have at least 2 rows.")
    cols = len(table[0])
    if cols < 2:
        raise ValueError("Table must have at least 2 columns.")

    row_sums = [sum(r) for r in table]
    col_sums = [sum(table[r][c] for r in range(rows)) for c in range(cols)]
    total = sum(row_sums)
    df = (rows - 1) * (cols - 1)

    expected = [[(row_sums[r] * col_sums[c]) / total for c in range(cols)] for r in range(rows)]

    chi2 = 0.0
    is_2x2 = (rows == 2 and cols == 2)
    for r in range(rows):
        for c in range(cols):
            obs = table[r][c]
            exp = expected[r][c]
            diff = abs(obs - exp)
            if is_2x2:
                # Yates' continuity correction
                diff = max(0.0, diff - 0.5)
            chi2 += (diff ** 2) / exp if exp > 1e-15 else 0.0

    p_val = chi2_sf(chi2, df)
    return TestResult(
        statistic=chi2,
        p_value=p_val,
        test_name="Chi-square test of independence",
        df=df,
        details={"expected": expected},
    )


chi_square_test = chi_square_independence


# ---------------------------------------------------------------------------
# Confidence Intervals
# ---------------------------------------------------------------------------

def confidence_interval(data: list, confidence: float = 0.95, statistic: str = "mean") -> Tuple[float, float]:
    """Student's t confidence interval for the sample mean."""
    n = len(data)
    if n < 2:
        raise ValueError("At least 2 data points required for confidence interval.")
    m = _mean(data)
    se = _std(data, ddof=1) / math.sqrt(n)
    alpha = 1.0 - confidence
    t_crit = inv_t_cdf(1.0 - alpha / 2.0, df=n - 1)
    margin = t_crit * se
    return (m - margin, m + margin)


def wilson_score_interval(successes: int, total: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Wilson score confidence interval for binomial proportions."""
    if total <= 0:
        raise ValueError("Total must be positive.")
    p = successes / total
    alpha = 1.0 - confidence
    z = inv_normal_cdf(1.0 - alpha / 2.0)
    denominator = 1.0 + (z ** 2) / total
    center = (p + (z ** 2) / (2.0 * total)) / denominator
    margin = (z / denominator) * math.sqrt((p * (1.0 - p)) / total + (z ** 2) / (4.0 * total * total))
    return (max(0.0, center - margin), min(1.0, center + margin))


# ---------------------------------------------------------------------------
# BCa Bootstrap
# ---------------------------------------------------------------------------

def bca_bootstrap(
    data: list,
    stat_func: Callable[[list], float],
    n_resamples: int = 2000,
    confidence: float = 0.95,
) -> Tuple[float, float]:
    """
    Bias-Corrected and Accelerated (BCa) bootstrap confidence interval.
    Falls back gracefully to percentile bootstrap if data is small or acceleration is undefined.
    """
    n = len(data)
    if n < 3:
        raise ValueError("At least 3 observations required for bootstrap.")

    rng = get_active_session().rng
    theta_hat = stat_func(data)

    # 1. Resample
    boot_stats = []
    for _ in range(n_resamples):
        sample = [data[int(rng.random() * n)] for _ in range(n)]
        boot_stats.append(stat_func(sample))
    boot_stats.sort()

    # 2. Bias correction factor z0
    num_less = sum(1 for b in boot_stats if b < theta_hat)
    prop_less = max(1e-6, min(1.0 - 1e-6, num_less / n_resamples))
    z0 = inv_normal_cdf(prop_less)

    # 3. Acceleration factor a via jackknife
    jack_stats = []
    for i in range(n):
        jack_sample = data[:i] + data[i + 1:]
        jack_stats.append(stat_func(jack_sample))
    jack_mean = _mean(jack_stats)
    u = [jack_mean - j for j in jack_stats]
    sum_u2 = sum(x ** 2 for x in u)
    sum_u3 = sum(x ** 3 for x in u)

    if sum_u2 < 1e-15:
        # Fallback to percentile bootstrap
        alpha = 1.0 - confidence
        low_idx = int((alpha / 2.0) * n_resamples)
        high_idx = int((1.0 - alpha / 2.0) * n_resamples)
        return (boot_stats[low_idx], boot_stats[min(n_resamples - 1, high_idx)])

    a = sum_u3 / (6.0 * (sum_u2 ** 1.5))

    # 4. Adjusted percentiles
    alpha = 1.0 - confidence
    z_alpha1 = inv_normal_cdf(alpha / 2.0)
    z_alpha2 = inv_normal_cdf(1.0 - alpha / 2.0)

    def _adj_alpha(z_crit: float) -> float:
        num = z0 + z_crit
        denom = 1.0 - a * num
        if denom <= 0:
            return 0.5
        w = z0 + num / denom
        return normal_sf(-w)

    alpha1 = max(0.001, min(0.999, _adj_alpha(z_alpha1)))
    alpha2 = max(0.001, min(0.999, _adj_alpha(z_alpha2)))

    idx1 = int(alpha1 * n_resamples)
    idx2 = int(alpha2 * n_resamples)
    return (boot_stats[min(n_resamples - 1, max(0, idx1))], boot_stats[min(n_resamples - 1, max(0, idx2))])


# ---------------------------------------------------------------------------
# Multiple Testing Corrections
# ---------------------------------------------------------------------------

def adjust_p_values(p_values: list, method: str = "holm") -> list:
    """Adjusts p-values for multiple comparisons using 'holm' or 'benjamini_hochberg'."""
    m = len(p_values)
    if m <= 1:
        return list(p_values)

    indexed = sorted(enumerate(p_values), key=lambda item: item[1])
    adjusted = [0.0] * m

    method = method.lower().strip()
    if method in ("holm", "holm_bonferroni"):
        max_so_far = 0.0
        for rank, (orig_idx, p) in enumerate(indexed):
            mult = m - rank
            val = min(1.0, p * mult)
            max_so_far = max(max_so_far, val)
            adjusted[orig_idx] = max_so_far
    elif method in ("benjamini_hochberg", "bh", "fdr"):
        min_so_far = 1.0
        for rank in range(m - 1, -1, -1):
            orig_idx, p = indexed[rank]
            q = (m / (rank + 1)) * p
            min_so_far = min(min_so_far, q)
            adjusted[orig_idx] = min(1.0, min_so_far)
    else:
        raise ValueError(f"Unknown multiple testing adjustment method: {method}")

    return adjusted


# ---------------------------------------------------------------------------
# Diagnostic MCMC (Metropolis-Hastings)
# ---------------------------------------------------------------------------

def metropolis_hastings(
    log_prob_func: Callable[[list], float],
    initial: list,
    n_samples: int = 5000,
    burn_in: float = 0.2,
    n_chains: int = 2,
) -> MCMCResult:
    """
    Metropolis-Hastings MCMC sampler with burn-in adaptation and convergence diagnostics (Split-Rhat and ESS).
    """
    rng = get_active_session().rng
    dim = len(initial)
    burn_samples = int(n_samples * burn_in)
    keep_samples = n_samples - burn_samples

    all_chains: List[List[List[float]]] = []
    accepted_counts = [0] * n_chains

    for chain_idx in range(n_chains):
        chain: List[List[float]] = []
        cur_state = [x + rng.normal(0.0, 0.5) for x in initial]
        cur_log_prob = log_prob_func(cur_state)
        if math.isnan(cur_log_prob) or math.isinf(cur_log_prob):
            cur_state = list(initial)
            cur_log_prob = log_prob_func(cur_state)

        burn_accepted = 0
        proposal_sigma = 1.0

        for step in range(n_samples):
            # Propose state
            prop_state = [cur_state[d] + rng.normal(0.0, proposal_sigma) for d in range(dim)]
            prop_log_prob = log_prob_func(prop_state)

            if not math.isnan(prop_log_prob) and not math.isinf(prop_log_prob):
                log_alpha = prop_log_prob - cur_log_prob
                if log_alpha >= 0.0 or math.log(max(1e-15, rng.random())) < log_alpha:
                    cur_state = prop_state
                    cur_log_prob = prop_log_prob
                    if step >= burn_samples:
                        accepted_counts[chain_idx] += 1
                    else:
                        burn_accepted += 1

            # Adaptive proposal tuning during burn-in ONLY
            if step < burn_samples and step > 0 and step % 50 == 0:
                acc_rate = burn_accepted / step
                if acc_rate < 0.20:
                    proposal_sigma *= 0.8
                elif acc_rate > 0.50:
                    proposal_sigma *= 1.2

            if step >= burn_samples:
                chain.append(list(cur_state))

        all_chains.append(chain)

    total_kept = keep_samples * n_chains
    overall_acceptance = sum(accepted_counts) / max(1, total_kept)

    # Flatten samples
    flat_samples: List[List[float]] = []
    for chain in all_chains:
        flat_samples.extend(chain)

    # Gelman-Rubin Split-Rhat diagnostic across chains
    # Between-chain variance B, within-chain variance W
    chain_means = [[_mean([chain[i][d] for i in range(keep_samples)]) for d in range(dim)] for chain in all_chains]
    chain_vars = [[_var([chain[i][d] for i in range(keep_samples)], ddof=1) for d in range(dim)] for chain in all_chains]

    r_hat_max = 1.0
    ess_min = float(total_kept)

    for d in range(dim):
        means_d = [chain_means[c][d] for c in range(n_chains)]
        vars_d = [chain_vars[c][d] for c in range(n_chains)]
        mean_grand = _mean(means_d)
        w_d = _mean(vars_d)
        b_d = keep_samples * _var(means_d, ddof=1) if n_chains > 1 else 0.0
        var_plus = ((keep_samples - 1) / keep_samples) * w_d + (1.0 / keep_samples) * b_d
        r_hat = math.sqrt(var_plus / w_d) if w_d > 1e-15 else 1.0
        r_hat_max = max(r_hat_max, r_hat)

        # Autocorrelation lag 1 for ESS
        flat_d = [s[d] for s in flat_samples]
        m_d = _mean(flat_d)
        c0 = sum((x - m_d) ** 2 for x in flat_d)
        c1 = sum((flat_d[t] - m_d) * (flat_d[t + 1] - m_d) for t in range(len(flat_d) - 1))
        rho1 = c1 / c0 if c0 > 1e-15 else 0.0
        ess_d = total_kept * (1.0 - rho1) / (1.0 + rho1) if (1.0 + rho1) > 1e-15 else total_kept
        ess_min = min(ess_min, max(1.0, ess_d))

    return MCMCResult(
        samples=flat_samples,
        acceptance_rate=overall_acceptance,
        r_hat=r_hat_max,
        ess=ess_min,
        chains=all_chains,
    )
