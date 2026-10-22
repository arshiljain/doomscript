"""Risk Management Domain Runtime: Value-at-Risk, CVaR, Drawdown, and Risk-Adjusted Ratios."""
import math
from typing import List, Dict, Any

def risk_value_at_risk_historical(returns: List[float], confidence: float = 0.95) -> float:
    """Historical Value at Risk (VaR). Returns the loss threshold at given confidence level (e.g. 0.95)."""
    if not returns:
        return 0.0
    sorted_ret = sorted([float(r) for r in returns])
    # VaR is the negative of the quantile loss
    idx = int((1.0 - float(confidence)) * len(sorted_ret))
    idx = max(0, min(len(sorted_ret) - 1, idx))
    val = sorted_ret[idx]
    # Return as positive loss magnitude if negative, or negative if positive
    return round(-val if val < 0 else 0.0, 4)

def risk_conditional_var(returns: List[float], confidence: float = 0.95) -> float:
    """Conditional Value at Risk (CVaR) / Expected Shortfall: average loss beyond VaR."""
    if not returns:
        return 0.0
    sorted_ret = sorted([float(r) for r in returns])
    idx = int((1.0 - float(confidence)) * len(sorted_ret))
    idx = max(1, min(len(sorted_ret), idx))
    tail_losses = sorted_ret[:idx]
    if not tail_losses:
        return 0.0
    mean_tail = sum(tail_losses) / len(tail_losses)
    return round(-mean_tail if mean_tail < 0 else 0.0, 4)

def risk_max_drawdown(prices: List[float]) -> Dict[str, float]:
    """Computes Maximum Peak-to-Trough Drawdown in an asset or portfolio price series."""
    if not prices or len(prices) < 2:
        return {"max_drawdown": 0.0, "peak": 0.0, "trough": 0.0}
    peak = float(prices[0])
    max_dd = 0.0
    trough_at_max = peak
    peak_at_max = peak
    for p_raw in prices:
        p = float(p_raw)
        if p > peak:
            peak = p
        dd = (peak - p) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
            peak_at_max = peak
            trough_at_max = p
    return {"max_drawdown": round(max_dd, 4), "peak": round(peak_at_max, 2), "trough": round(trough_at_max, 2)}

def risk_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
    """Computes annualized/period Sharpe Ratio: (mean(returns) - Rf) / std(returns)."""
    if not returns or len(returns) < 2:
        return 0.0
    rf = float(risk_free_rate)
    mean_r = sum(returns) / len(returns)
    variance = sum((r - mean_r) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = math.sqrt(variance)
    if std_dev == 0.0:
        return 0.0
    return round((mean_r - rf) / std_dev, 4)

def risk_sortino_ratio(returns: List[float], target_return: float = 0.0) -> float:
    """Computes Sortino Ratio: (mean(returns) - target) / downside_deviation."""
    if not returns or len(returns) < 2:
        return 0.0
    target = float(target_return)
    mean_r = sum(returns) / len(returns)
    downside_diffs = [min(0.0, float(r) - target) ** 2 for r in returns]
    downside_var = sum(downside_diffs) / len(returns)
    downside_std = math.sqrt(downside_var)
    if downside_std == 0.0:
        return 0.0
    return round((mean_r - target) / downside_std, 4)
