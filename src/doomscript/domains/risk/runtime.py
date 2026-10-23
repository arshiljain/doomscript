"""Risk Domain Runtime: VaR, Expected Shortfall, Altman Z-Score, Merton structural default, and financial risk metrics."""
import math
import random
from typing import List, Dict, Any, Tuple, Optional
from doomscript.domains.base import DomainRuntime

# ============================================================================
# 1. PRESERVED CORE RISK RATIOS & DRAWDOWN
# ============================================================================

def risk_value_at_risk_historical(returns: List[float], confidence: float = 0.95) -> float:
    """Calculates Historical Value at Risk (VaR) from a series of percentage returns."""
    if not returns:
        return 0.0
    s_ret = sorted(returns)
    idx = int(math.floor((1.0 - confidence) * len(s_ret)))
    cutoff = s_ret[max(0, min(idx, len(s_ret) - 1))]
    return round(-cutoff if cutoff < 0 else 0.0, 4)

def risk_conditional_var(returns: List[float], confidence: float = 0.95) -> float:
    """Calculates Conditional Value at Risk (CVaR / Expected Shortfall)."""
    if not returns:
        return 0.0
    s_ret = sorted(returns)
    idx = int(math.floor((1.0 - confidence) * len(s_ret)))
    tail = s_ret[:max(1, idx + 1)]
    avg_loss = sum(tail) / len(tail)
    return round(-avg_loss if avg_loss < 0 else 0.0, 4)

def risk_max_drawdown(prices: List[float]) -> Dict[str, float]:
    """Calculates maximum peak-to-trough drawdown from price time series."""
    if not prices or len(prices) < 2:
        return {"max_drawdown": 0.0, "peak": 0.0, "trough": 0.0}
    max_dd = 0.0
    peak = prices[0]
    trough = prices[0]
    best_peak = peak
    best_trough = trough
    for p in prices:
        if p > peak:
            peak = p
            trough = p
        elif p < trough:
            trough = p
            dd = (peak - trough) / peak if peak > 0 else 0.0
            if dd > max_dd:
                max_dd = dd
                best_peak = peak
                best_trough = trough
    return {"max_drawdown": round(max_dd, 4), "peak": best_peak, "trough": best_trough}

def risk_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
    """Calculates annualized Sharpe Ratio."""
    n = len(returns)
    if n < 2:
        return 0.0
    mean_r = sum(returns) / n
    var = sum((r - mean_r) ** 2 for r in returns) / (n - 1)
    std_r = math.sqrt(var)
    if std_r == 0:
        return 0.0
    return round((mean_r - risk_free_rate) / std_r, 4)

def risk_sortino_ratio(returns: List[float], target_return: float = 0.0) -> float:
    """Calculates Sortino Ratio penalizing only downside volatility."""
    n = len(returns)
    if n < 2:
        return 0.0
    mean_r = sum(returns) / n
    downside_var = sum((min(0.0, r - target_return) ** 2) for r in returns) / (n - 1)
    downside_dev = math.sqrt(downside_var)
    if downside_dev == 0.0:
        return 0.0
    return round((mean_r - target_return) / downside_dev, 4)

def risk_calmar_ratio(annualized_return: float, max_drawdown: float) -> float:
    """Calculates Calmar Ratio: Annualized Return / Max Drawdown."""
    if max_drawdown <= 0.0:
        return 0.0
    return round(float(annualized_return) / float(max_drawdown), 4)

def risk_portfolio_volatility(weights: List[float], covariance_matrix: List[List[float]]) -> float:
    """Calculates portfolio variance/volatility from asset weights and covariance matrix."""
    n = len(weights)
    if n == 0 or len(covariance_matrix) != n:
        return 0.0
    var = 0.0
    for i in range(n):
        for j in range(n):
            var += weights[i] * weights[j] * covariance_matrix[i][j]
    return round(math.sqrt(max(0.0, var)), 4)

# ============================================================================
# 2. ADVANCED MODELS (ALTMAN Z, MERTON DEFAULT, CORNISH-FISHER)
# ============================================================================

def risk_altman_z_score(working_capital: float, total_assets: float, retained_earnings: float, ebit: float, market_cap: float, total_liabilities: float, sales: float) -> Dict[str, Any]:
    """Computes Altman Z-Score for public manufacturing firms to predict insolvency."""
    if total_assets <= 0 or total_liabilities <= 0:
        return {"z_score": 0.0, "zone": "Distress"}
    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = sales / total_assets
    z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 0.999 * x5
    zone = "Safe" if z >= 2.99 else ("Grey" if z >= 1.81 else "Distress")
    return {
        "z_score": round(z, 3),
        "zone": zone,
        "x1_liquidity": round(x1, 3),
        "x2_profitability": round(x2, 3),
        "x3_operating_eff": round(x3, 3),
        "x4_solvency": round(x4, 3),
        "x5_asset_turnover": round(x5, 3)
    }

def risk_var_cornish_fisher(mean: float, std: float, skewness: float, kurtosis: float, confidence: float = 0.95) -> float:
    """Calculates modified VaR using Cornish-Fisher expansion for non-normal distributions."""
    # Base standard normal quantile z
    z_map = {0.90: 1.2816, 0.95: 1.6449, 0.99: 2.3263}
    z = z_map.get(confidence, 1.6449)
    # Excess kurtosis
    excess_kurt = kurtosis - 3.0
    # Cornish-Fisher adjusted quantile
    z_cf = z + (z**2 - 1.0) * (skewness / 6.0) + (z**3 - 3.0 * z) * (excess_kurt / 24.0) - (2.0 * z**3 - 5.0 * z) * (skewness**2 / 36.0)
    var = -(mean - z_cf * std)
    return round(max(0.0, var), 4)

def risk_merton_distance_to_default(asset_value: float, debt_face_value: float, asset_volatility: float, risk_free_rate: float = 0.05, time_years: float = 1.0) -> Dict[str, Any]:
    """Merton structural credit model calculating distance to default (DD) and default probability."""
    if asset_value <= 0 or debt_face_value <= 0 or asset_volatility <= 0:
        return {"distance_to_default": 0.0, "default_probability": 1.0}
    t = max(0.01, float(time_years))
    num = math.log(asset_value / debt_face_value) + (risk_free_rate - 0.5 * (asset_volatility ** 2)) * t
    den = asset_volatility * math.sqrt(t)
    dd = num / den
    # Approximation of standard normal CDF: Phi(-dd)
    pd = 0.5 * math.erfc(dd / math.sqrt(2.0))
    return {
        "distance_to_default": round(dd, 4),
        "default_probability": round(pd, 6),
        "implied_credit_rating": "AAA" if dd > 4.0 else ("A" if dd > 2.5 else ("BBB" if dd > 1.5 else "Junk"))
    }

# ============================================================================
# 3. DOMAIN RUNTIME
# ============================================================================

class RiskRuntime(DomainRuntime):
    """Unified runtime bridge for the Risk computational domain."""
    def execute_ir(self, ir: Any, env: Dict[str, Any]) -> Any:
        return None

    def historical_var(self, returns: List[float], conf: float = 0.95) -> float:
        return risk_value_at_risk_historical(returns, conf)
    def cvar(self, returns: List[float], conf: float = 0.95) -> float:
        return risk_conditional_var(returns, conf)
    def max_drawdown(self, prices: List[float]) -> Dict[str, float]:
        return risk_max_drawdown(prices)
    def sharpe(self, returns: List[float], rf: float = 0.0) -> float:
        return risk_sharpe_ratio(returns, rf)
    def sortino(self, returns: List[float], target: float = 0.0) -> float:
        return risk_sortino_ratio(returns, target)
    def calmar(self, ann_ret: float, mdd: float) -> float:
        return risk_calmar_ratio(ann_ret, mdd)
    def portfolio_vol(self, weights: List[float], cov: List[List[float]]) -> float:
        return risk_portfolio_volatility(weights, cov)
    def altman_z(self, wc: float, ta: float, re: float, ebit: float, mc: float, tl: float, sales: float) -> Dict[str, Any]:
        return risk_altman_z_score(wc, ta, re, ebit, mc, tl, sales)
    def cornish_fisher(self, mean: float, std: float, skew: float, kurt: float, conf: float = 0.95) -> float:
        return risk_var_cornish_fisher(mean, std, skew, kurt, conf)
    def merton_default(self, v: float, d: float, sigma: float, rf: float = 0.05, t: float = 1.0) -> Dict[str, Any]:
        return risk_merton_distance_to_default(v, d, sigma, rf, t)
