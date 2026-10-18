"""
DoomScript Research Numerical Distributions: Exact Incomplete Functions, Direct Survival, and Inverses.
"""

import math
from typing import Tuple


def log_gamma(x: float) -> float:
    """Natural logarithm of the Gamma function via math.lgamma."""
    return math.lgamma(x)


def beta_ln(a: float, b: float) -> float:
    """Natural logarithm of the Beta function B(a, b)."""
    return math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)


def _gamma_series(s: float, x: float, max_iter: int = 200, eps: float = 1e-15) -> float:
    """Evaluates regularized lower incomplete gamma P(s, x) via Taylor series."""
    if x <= 0.0:
        return 0.0
    term = 1.0 / s
    total = term
    for k in range(1, max_iter):
        term *= x / (s + k)
        total += term
        if abs(term) < abs(total) * eps:
            break
    log_factor = -x + s * math.log(x) - math.lgamma(s)
    return math.exp(log_factor) * total


def _gamma_cont_frac(s: float, x: float, max_iter: int = 200, eps: float = 1e-15) -> float:
    """Evaluates regularized upper incomplete gamma Q(s, x) via Legendre continued fraction (Lentz's method)."""
    tiny = 1e-30
    b0 = x + 1.0 - s
    c0 = 1.0 / tiny
    d0 = 1.0 / b0
    h = d0

    for m in range(1, max_iter):
        an = -m * (m - s)
        bn = b0 + 2.0 * m
        d0 = bn + an * d0
        if abs(d0) < tiny:
            d0 = tiny
        c0 = bn + an / c0
        if abs(c0) < tiny:
            c0 = tiny
        d0 = 1.0 / d0
        delta = c0 * d0
        h *= delta
        if abs(delta - 1.0) < eps:
            break

    log_factor = -x + s * math.log(x) - math.lgamma(s)
    return math.exp(log_factor) * h


def gammainc(s: float, x: float) -> float:
    """Regularized lower incomplete gamma function P(s, x)."""
    if x <= 0.0 or s <= 0.0:
        return 0.0
    if x < s + 1.0:
        return _gamma_series(s, x)
    else:
        return 1.0 - _gamma_cont_frac(s, x)


def gammaincc(s: float, x: float) -> float:
    """Regularized upper incomplete gamma survival function Q(s, x) = 1 - P(s, x)."""
    if s <= 0.0:
        return 0.0
    if x <= 0.0:
        return 1.0
    if x < s + 1.0:
        return 1.0 - _gamma_series(s, x)
    else:
        return _gamma_cont_frac(s, x)


def _betainc_cont_frac(a: float, b: float, x: float, max_iter: int = 200, eps: float = 1e-15) -> float:
    """Evaluates incomplete beta continued fraction via modified Lentz's method."""
    tiny = 1e-30
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d

    for m in range(1, max_iter):
        m2 = 2 * m
        # Even step
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c

        # Odd step
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        del_val = d * c
        h *= del_val
        if abs(del_val - 1.0) < eps:
            break

    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    if a <= 0.0 or b <= 0.0:
        raise ValueError("Beta parameters a and b must be positive.")

    # Symmetry transformation to ensure fast convergence
    if x > (a + 1.0) / (a + b + 2.0):
        return 1.0 - betainc(b, a, 1.0 - x)

    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) +
                  a * math.log(x) + b * math.log(1.0 - x))
    return bt * _betainc_cont_frac(a, b, x) / a


def betaincc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta survival function 1 - I_x(a, b) computed directly via symmetry."""
    if x <= 0.0:
        return 1.0
    if x >= 1.0:
        return 0.0
    # Direct survival via symmetry: 1 - I_x(a, b) = I_{1-x}(b, a)
    return betainc(b, a, 1.0 - x)


# ---------------------------------------------------------------------------
# Standard Statistical Distributions (CDF and Survival Functions)
# ---------------------------------------------------------------------------

def normal_cdf(z: float) -> float:
    """Standard Normal CDF."""
    return 0.5 * math.erfc(-z / math.sqrt(2.0))


def normal_sf(z: float) -> float:
    """Standard Normal survival function S(z) = 1 - CDF(z)."""
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def t_cdf(t: float, df: float) -> float:
    """Student's t cumulative distribution function."""
    if df <= 0.0:
        raise ValueError("Degrees of freedom df must be positive.")
    x = df / (df + t * t)
    if t >= 0.0:
        return 1.0 - 0.5 * betainc(df / 2.0, 0.5, x)
    else:
        return 0.5 * betainc(df / 2.0, 0.5, x)


def t_sf(t: float, df: float) -> float:
    """Student's t survival function S(t) = P(T >= t) computed directly to avoid cancellation."""
    if df <= 0.0:
        raise ValueError("Degrees of freedom df must be positive.")
    x = df / (df + t * t)
    if t >= 0.0:
        return 0.5 * betainc(df / 2.0, 0.5, x)
    else:
        return 1.0 - 0.5 * betainc(df / 2.0, 0.5, x)


def f_cdf(f: float, dfn: float, dfd: float) -> float:
    """Snedecor's F cumulative distribution function."""
    if f <= 0.0:
        return 0.0
    x = (dfn * f) / (dfn * f + dfd)
    return betainc(dfn / 2.0, dfd / 2.0, x)


def f_sf(f: float, dfn: float, dfd: float) -> float:
    """Snedecor's F survival function S(f) = P(F >= f) computed directly via beta survival."""
    if f <= 0.0:
        return 1.0
    x = (dfn * f) / (dfn * f + dfd)
    return betaincc(dfn / 2.0, dfd / 2.0, x)


def chi2_cdf(x: float, df: float) -> float:
    """Chi-square cumulative distribution function."""
    if x <= 0.0:
        return 0.0
    return gammainc(df / 2.0, x / 2.0)


def chi2_sf(x: float, df: float) -> float:
    """Chi-square survival function S(x) = P(X >= x) computed directly via upper incomplete gamma."""
    if x <= 0.0:
        return 1.0
    return gammaincc(df / 2.0, x / 2.0)


# ---------------------------------------------------------------------------
# Quantile Functions (Inverse CDFs)
# ---------------------------------------------------------------------------

def inv_normal_cdf(p: float) -> float:
    """Inverse normal CDF (probit) using Acklam's algorithm."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("Probability p must be in (0, 1).")

    # Coefficients in rational approximations
    a = (-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00)
    b = (-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00)

    p_low = 0.02425
    p_high = 1.0 - p_low

    if p < p_low:
        q = math.sqrt(-2.0 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
    elif p <= p_high:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
                ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)


def inv_t_cdf(p: float, df: float, tol: float = 1e-10, max_iter: int = 100) -> float:
    """Inverse Student's t CDF via Newton-Raphson with bisection safeguard."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("Probability p must be in (0, 1).")
    if p == 0.5:
        return 0.0

    # Initial guess via Cornish-Fisher expansion from normal quantile
    z = inv_normal_cdf(p)
    t = z + (z ** 3 + z) / (4.0 * df) + (5.0 * z ** 5 + 16.0 * z ** 3 + 3.0 * z) / (96.0 * df * df)

    # Bracket search
    low, high = -1e6, 1e6
    if t < 0:
        high = 0.0
    else:
        low = 0.0

    # Newton-Raphson with PDF derivative
    pdf_factor = math.exp(math.lgamma((df + 1.0) / 2.0) - math.lgamma(df / 2.0)) / math.sqrt(df * math.pi)
    for _ in range(max_iter):
        f_val = t_cdf(t, df) - p
        if abs(f_val) < tol:
            return t
        if f_val < 0:
            low = max(low, t)
        else:
            high = min(high, t)

        pdf = pdf_factor * ((1.0 + (t * t) / df) ** (-(df + 1.0) / 2.0))
        if pdf > 1e-15:
            step = f_val / pdf
            t_next = t - step
            if low <= t_next <= high:
                t = t_next
            else:
                t = 0.5 * (low + high)
        else:
            t = 0.5 * (low + high)

    return t


def inv_chi2_cdf(p: float, df: float, tol: float = 1e-10, max_iter: int = 100) -> float:
    """Inverse Chi-Square CDF via Wilson-Hilferty transformation and Newton-Raphson."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("Probability p must be in (0, 1).")
    if df <= 0.0:
        raise ValueError("df must be positive.")

    # Wilson-Hilferty approximation as initial guess
    z = inv_normal_cdf(p)
    t = 2.0 / (9.0 * df)
    term = 1.0 - t + z * math.sqrt(t)
    x = max(1e-6, df * (term ** 3))

    low, high = 0.0, 1e6
    log_gamma_half_df = math.lgamma(df / 2.0)
    for _ in range(max_iter):
        f_val = chi2_cdf(x, df) - p
        if abs(f_val) < tol:
            return x
        if f_val < 0:
            low = max(low, x)
        else:
            high = min(high, x)

        log_pdf = (df / 2.0 - 1.0) * math.log(x) - x / 2.0 - (df / 2.0) * math.log(2.0) - log_gamma_half_df
        pdf = math.exp(log_pdf) if log_pdf > -700 else 0.0

        if pdf > 1e-15:
            step = f_val / pdf
            x_next = x - step
            if low <= x_next <= high:
                x = x_next
            else:
                x = 0.5 * (low + high)
        else:
            x = 0.5 * (low + high)

    return x
