"""Runtime execution engine for Quantitative Finance & Time Series domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import math
import random
from datetime import datetime, timedelta
from doomscript.runtime import Record
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.finance.spec import (
    FinanceFetchSpec,
    FinanceMavSpec,
    FinanceRsiSpec,
    FinanceReturnsSpec,
    FinanceSharpeSpec,
    FinanceBacktestSpec,
)


def _extract_values(series_or_records: Any) -> List[float]:
    """Extracts raw numeric values from a list of floats, ints, or Records/dicts with 'close' key."""
    if not isinstance(series_or_records, list):
        try:
            return [float(series_or_records)]
        except Exception:
            return []

    values: List[float] = []
    for item in series_or_records:
        if isinstance(item, (int, float)):
            values.append(float(item))
        elif isinstance(item, dict):
            # Look for close, price, or first float value
            val = item.get("close", item.get("price", item.get("val", None)))
            if val is not None and isinstance(val, (int, float)):
                values.append(float(val))
            else:
                for v in item.values():
                    if isinstance(v, (int, float)):
                        values.append(float(v))
                        break
    return values


def fetch_stock_prices(
    symbol: str,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
) -> List[Record]:
    """Generates or fetches realistic deterministic daily price series for a stock symbol."""
    sym = symbol.upper().strip('"\'')
    # Use deterministic seed based on symbol name
    seed_base = sum(ord(c) for c in sym)
    base_price = 100.0 + (seed_base % 150)

    try:
        cur_dt = datetime.strptime(start_date.strip('"\''), "%Y-%m-%d")
        end_dt = datetime.strptime(end_date.strip('"\''), "%Y-%m-%d")
    except Exception:
        cur_dt = datetime(2024, 1, 1)
        end_dt = datetime(2024, 12, 31)

    records: List[Record] = []
    price = base_price
    day_idx = 0

    while cur_dt <= end_dt:
        if cur_dt.weekday() < 5:  # Weekday
            # Deterministic pseudo-random variation
            phase = (day_idx * 0.1) + (seed_base * 0.05)
            ret = math.sin(phase) * 0.015 + math.cos(phase * 0.5) * 0.008
            price = max(5.0, price * (1.0 + ret))
            high = price * 1.01
            low = price * 0.99
            op = (high + low) / 2.0
            vol = 1000000 + int((math.sin(phase) + 1.0) * 500000)

            records.append(
                Record(
                    date=cur_dt.strftime("%Y-%m-%d"),
                    symbol=sym,
                    open=round(op, 2),
                    high=round(high, 2),
                    low=round(low, 2),
                    close=round(price, 2),
                    volume=vol,
                )
            )
            day_idx += 1
        cur_dt += timedelta(days=1)

    return records


def moving_average(
    series: Any,
    window: int = 20,
    kind: str = "sma",
) -> List[float]:
    """Computes Simple Moving Average (SMA) or Exponential Moving Average (EMA)."""
    vals = _extract_values(series)
    if not vals:
        return []

    w = max(1, int(window))
    if kind.lower() in ("ema", "exponential"):
        alpha = 2.0 / (w + 1.0)
        ema_vals = []
        cur_ema = vals[0]
        for v in vals:
            cur_ema = alpha * v + (1.0 - alpha) * cur_ema
            ema_vals.append(round(cur_ema, 4))
        return ema_vals

    # Simple Moving Average
    sma_vals = []
    running_sum = 0.0
    for i, v in enumerate(vals):
        running_sum += v
        if i >= w:
            running_sum -= vals[i - w]
            sma_vals.append(round(running_sum / w, 4))
        else:
            sma_vals.append(round(running_sum / (i + 1), 4))
    return sma_vals


def relative_strength_index(series: Any, period: int = 14) -> List[float]:
    """Computes standard Wilder Relative Strength Index (RSI) bounded [0, 100]."""
    vals = _extract_values(series)
    if len(vals) < 2:
        return [50.0] * len(vals)

    p = max(1, int(period))
    deltas = [vals[i] - vals[i - 1] for i in range(1, len(vals))]
    gains = [max(0.0, d) for d in deltas]
    losses = [max(0.0, -d) for d in deltas]

    rsi_res: List[float] = [50.0]  # Initial placeholder for day 0
    avg_gain = sum(gains[:p]) / float(p) if len(gains) >= p else 0.0
    avg_loss = sum(losses[:p]) / float(p) if len(losses) >= p else 0.0

    for i in range(len(deltas)):
        if i >= p:
            avg_gain = (avg_gain * (p - 1) + gains[i]) / float(p)
            avg_loss = (avg_loss * (p - 1) + losses[i]) / float(p)

        if avg_loss == 0.0:
            rsi_val = 100.0 if avg_gain > 0 else 50.0
        else:
            rs = avg_gain / avg_loss
            rsi_val = 100.0 - (100.0 / (1.0 + rs))

        rsi_res.append(round(rsi_val, 2))

    return rsi_res


def calculate_daily_returns(series: Any) -> List[float]:
    """Computes daily percentage returns: (P_t - P_{t-1}) / P_{t-1}."""
    vals = _extract_values(series)
    if len(vals) < 2:
        return [0.0] * len(vals)

    rets = [0.0]
    for i in range(1, len(vals)):
        prev = vals[i - 1]
        cur = vals[i]
        r = (cur - prev) / prev if prev != 0 else 0.0
        rets.append(round(r, 6))
    return rets


def calculate_sharpe_ratio(
    returns_or_series: Any,
    risk_free_rate: float = 0.04,
) -> float:
    """Computes annualized Sharpe Ratio assuming 252 trading days per year."""
    vals = _extract_values(returns_or_series)
    if not vals:
        return 0.0

    # If inputs look like prices (> 1.0), convert to daily returns first
    if any(abs(v) > 1.0 for v in vals):
        rets = calculate_daily_returns(vals)[1:]
    else:
        rets = vals

    if len(rets) < 2:
        return 0.0

    mean_ret = sum(rets) / len(rets)
    daily_rf = risk_free_rate / 252.0
    excess_rets = [r - daily_rf for r in rets]
    mean_excess = sum(excess_rets) / len(excess_rets)

    variance = sum((r - mean_ret) ** 2 for r in rets) / (len(rets) - 1)
    std_dev = math.sqrt(variance) if variance > 0 else 0.0001

    daily_sharpe = mean_excess / std_dev
    annualized_sharpe = daily_sharpe * math.sqrt(252)
    return round(annualized_sharpe, 4)


def backtest_strategy(
    prices: Any,
    condition: str = "crossover",
    buy_condition: Optional[str] = None,
    sell_condition: Optional[str] = None,
) -> Record:
    """Backtests a simple trading strategy on a price series."""
    vals = _extract_values(prices)
    if len(vals) < 10:
        return Record(total_return=0.0, trades=0, win_rate=0.0, max_drawdown=0.0)

    sma_fast = moving_average(vals, window=10)
    sma_slow = moving_average(vals, window=30)

    in_position = False
    buy_price = 0.0
    trades = 0
    wins = 0
    cash = 10000.0
    portfolio_values = []

    for i in range(len(vals)):
        price = vals[i]
        fast = sma_fast[i]
        slow = sma_slow[i]

        # Buy condition
        if not in_position and fast > slow:
            in_position = True
            buy_price = price
            trades += 1

        # Sell condition
        elif in_position and fast < slow:
            in_position = False
            gain = (price - buy_price) / buy_price
            if gain > 0:
                wins += 1
            cash *= (1.0 + gain)

        cur_val = cash * (price / buy_price if in_position else 1.0)
        portfolio_values.append(cur_val)

    tot_return = round(((portfolio_values[-1] - 10000.0) / 10000.0) * 100.0, 2)
    win_rate = round((wins / float(trades)) * 100.0, 2) if trades > 0 else 0.0

    # Max Drawdown
    peak = portfolio_values[0]
    max_dd = 0.0
    for v in portfolio_values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd

    return Record(
        total_return_pct=tot_return,
        trades=trades,
        win_rate_pct=win_rate,
        max_drawdown_pct=round(max_dd * 100.0, 2),
    )


class FinanceRuntime(DomainRuntime):
    """Runtime execution engine for Quantitative Finance specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Finance spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, FinanceFetchSpec):
            return fetch_stock_prices(ir.symbol, start_date=ir.start_date, end_date=ir.end_date)
        elif isinstance(ir, FinanceMavSpec):
            series = scope.get(ir.series_var)
            return moving_average(series, window=ir.window, kind=ir.kind)
        elif isinstance(ir, FinanceRsiSpec):
            series = scope.get(ir.series_var)
            return relative_strength_index(series, period=ir.period)
        elif isinstance(ir, FinanceReturnsSpec):
            series = scope.get(ir.series_var)
            return calculate_daily_returns(series)
        elif isinstance(ir, FinanceSharpeSpec):
            returns = scope.get(ir.returns_var)
            return calculate_sharpe_ratio(returns, risk_free_rate=ir.risk_free_rate)
        elif isinstance(ir, FinanceBacktestSpec):
            prices = scope.get(ir.prices_var)
            return backtest_strategy(prices, condition=ir.condition)

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_finance_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Finance spec not found: {spec_id}")
    return FinanceRuntime().execute_ir(spec, {})


# --- Batch 4 Spoken English Finance Verbs ---

def finance_bollinger_bands(prices: Any, period: Any = 20, num_std: Any = 2) -> Dict[str, List[float]]:
    """Calculate Bollinger Bands (middle, upper, lower)."""
    vals = _extract_values(prices)
    p = int(period)
    k = float(num_std)
    if len(vals) < p:
        return {"middle": [], "upper": [], "lower": []}
    middle = []
    upper = []
    lower = []
    for i in range(len(vals) - p + 1):
        window = vals[i : i + p]
        m = sum(window) / p
        variance = sum((x - m) ** 2 for x in window) / p
        std = math.sqrt(variance)
        middle.append(round(m, 4))
        upper.append(round(m + k * std, 4))
        lower.append(round(m - k * std, 4))
    return {"middle": middle, "upper": upper, "lower": lower}


def finance_rsi(prices: Any, period: Any = 14) -> List[float]:
    """Calculate Relative Strength Index (RSI)."""
    return relative_strength_index(prices, period=int(period))


def finance_macd(prices: Any, fast: Any = 12, slow: Any = 26, signal: Any = 9) -> Dict[str, List[float]]:
    """Moving Average Convergence Divergence (MACD, signal, and histogram)."""
    vals = _extract_values(prices)
    f, s, sig = int(fast), int(slow), int(signal)
    if len(vals) < s:
        return {"macd": [], "signal": [], "histogram": []}
    ema_fast = moving_average(vals, window=f, kind="ema")
    ema_slow = moving_average(vals, window=s, kind="ema")
    macd_line = [round(a - b, 4) for a, b in zip(ema_fast, ema_slow)]
    sig_line = moving_average(macd_line, window=sig, kind="ema")
    hist = [round(m - s_val, 4) for m, s_val in zip(macd_line, sig_line)]
    return {"macd": macd_line, "signal": sig_line, "histogram": hist}


def finance_sharpe_ratio(returns: Any, risk_free: Any = 0.0) -> float:
    """Calculate annualized Sharpe ratio with risk-free rate."""
    return calculate_sharpe_ratio(returns, risk_free_rate=float(risk_free))


def finance_maximum_drawdown(prices: Any) -> float:
    """Maximum peak-to-trough drawdown ratio."""
    vals = _extract_values(prices)
    if not vals:
        return 0.0
    peak = vals[0]
    max_dd = 0.0
    for v in vals:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
    return round(max_dd, 4)


def finance_value_at_risk(returns: Any, confidence: Any = 95) -> float:
    """Historical Value at Risk (VaR) at specified confidence percentage."""
    vals = _extract_values(returns)
    if not vals:
        return 0.0
    sorted_rets = sorted(vals)
    conf = float(confidence)
    cutoff_idx = max(0, min(len(sorted_rets) - 1, int(len(sorted_rets) * (1.0 - conf / 100.0))))
    loss = -sorted_rets[cutoff_idx]
    return round(float(loss), 4)


def finance_cagr(prices: Any) -> float:
    """Compound Annual Growth Rate across given periods."""
    vals = _extract_values(prices)
    if len(vals) < 2 or vals[0] <= 0:
        return 0.0
    periods = len(vals) - 1
    cagr = (vals[-1] / vals[0]) ** (1.0 / periods) - 1.0
    return round(float(cagr), 4)


# 350-Expansion Quantitative Finance Operations

def _norm_cdf(x: float) -> float:
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0


def fin_vwap(prices: Any, volumes: Any) -> float:
    """Volume Weighted Average Price."""
    ps = _extract_values(prices)
    vs = _extract_values(volumes)
    if not ps or not vs or len(ps) != len(vs):
        return 0.0
    tot_vol = sum(vs)
    if tot_vol == 0:
        return 0.0
    return round(sum(p * v for p, v in zip(ps, vs)) / tot_vol, 4)


def fin_stochastic_oscillator(highs: Any, lows: Any, closes: Any, k_period: Any = 14, d_period: Any = 3) -> Dict[str, List[float]]:
    """Stochastic Oscillator (%K and %D)."""
    hs = _extract_values(highs)
    ls = _extract_values(lows)
    cs = _extract_values(closes)
    k_p, d_p = int(k_period), int(d_period)
    n = min(len(hs), len(ls), len(cs))
    if n < k_p:
        return {"percent_k": [], "percent_d": []}
    k_vals = []
    for i in range(k_p - 1, n):
        window_high = max(hs[i - k_p + 1:i + 1])
        window_low = min(ls[i - k_p + 1:i + 1])
        denom = window_high - window_low
        val = 100.0 * (cs[i] - window_low) / denom if denom > 0 else 50.0
        k_vals.append(round(val, 4))
    d_vals = []
    for i in range(len(k_vals)):
        if i + 1 >= d_p:
            d_vals.append(round(sum(k_vals[i - d_p + 1:i + 1]) / d_p, 4))
        else:
            d_vals.append(round(sum(k_vals[:i + 1]) / (i + 1), 4))
    return {"percent_k": k_vals, "percent_d": d_vals}


def fin_sortino_ratio(returns: Any, risk_free_rate: Any = 0.02, target_return: Any = 0.0) -> float:
    """Annualized Sortino Ratio focusing on downside risk."""
    rets = _extract_values(returns)
    if not rets:
        return 0.0
    rf = float(risk_free_rate)
    tgt = float(target_return)
    mean_ret = sum(rets) / len(rets)
    downside_sq = [min(0.0, r - tgt) ** 2 for r in rets]
    downside_dev = math.sqrt(sum(downside_sq) / len(rets))
    if downside_dev == 0:
        return 0.0
    return round((mean_ret - rf) / downside_dev, 4)


def fin_beta(asset_returns: Any, market_returns: Any) -> float:
    """Beta sensitivity coefficient against benchmark."""
    a = _extract_values(asset_returns)
    m = _extract_values(market_returns)
    n = min(len(a), len(m))
    if n < 2:
        return 1.0
    a, m = a[:n], m[:n]
    mean_a, mean_m = sum(a) / n, sum(m) / n
    cov = sum((a[i] - mean_a) * (m[i] - mean_m) for i in range(n)) / (n - 1)
    var_m = sum((m[i] - mean_m) ** 2 for i in range(n)) / (n - 1)
    if var_m == 0:
        return 1.0
    return round(cov / var_m, 4)


def fin_treynor_ratio(returns: Any, market_returns: Any, risk_free_rate: Any = 0.02) -> float:
    """Treynor Ratio per unit of systematic risk (Beta)."""
    b = fin_beta(returns, market_returns)
    if abs(b) < 1e-6:
        return 0.0
    rets = _extract_values(returns)
    mean_ret = sum(rets) / len(rets) if rets else 0.0
    return round((mean_ret - float(risk_free_rate)) / b, 4)


def fin_calmar_ratio(returns: Any, max_drawdown_val: Any = None) -> float:
    """Calmar Ratio of compound annual return to maximum drawdown."""
    rets = _extract_values(returns)
    if not rets:
        return 0.0
    cum = 1.0
    peak = 1.0
    max_dd = float(max_drawdown_val) if max_drawdown_val is not None else 0.0
    if max_drawdown_val is None:
        for r in rets:
            cum *= (1.0 + r)
            if cum > peak:
                peak = cum
            dd = (peak - cum) / peak
            if dd > max_dd:
                max_dd = dd
    ann_ret = sum(rets) / len(rets) * 252.0 if len(rets) > 0 else 0.0
    if max_dd <= 0:
        return 0.0
    return round(ann_ret / max_dd, 4)


def fin_alpha(asset_returns: Any, market_returns: Any, risk_free_rate: Any = 0.02) -> float:
    """Jensen's Alpha abnormal return."""
    a = _extract_values(asset_returns)
    m = _extract_values(market_returns)
    rf = float(risk_free_rate)
    b = fin_beta(a, m)
    mean_a = sum(a) / len(a) if a else 0.0
    mean_m = sum(m) / len(m) if m else 0.0
    expected = rf + b * (mean_m - rf)
    return round(mean_a - expected, 4)


def fin_black_scholes_call(spot: Any, strike: Any, t: Any, rate: Any, vol: Any) -> float:
    """Black-Scholes analytical Call Option price."""
    S, K, T, r, v = float(spot), float(strike), float(t), float(rate), float(vol)
    if T <= 0 or v <= 0:
        return max(0.0, S - K)
    d1 = (math.log(S / K) + (r + 0.5 * v * v) * T) / (v * math.sqrt(T))
    d2 = d1 - v * math.sqrt(T)
    call = S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    return round(max(0.0, call), 4)


def fin_black_scholes_put(spot: Any, strike: Any, t: Any, rate: Any, vol: Any) -> float:
    """Black-Scholes analytical Put Option price."""
    S, K, T, r, v = float(spot), float(strike), float(t), float(rate), float(vol)
    if T <= 0 or v <= 0:
        return max(0.0, K - S)
    d1 = (math.log(S / K) + (r + 0.5 * v * v) * T) / (v * math.sqrt(T))
    d2 = d1 - v * math.sqrt(T)
    put = K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)
    return round(max(0.0, put), 4)


def fin_average_true_range(highs: Any, lows: Any, closes: Any, period: Any = 14) -> List[float]:
    """Average True Range (ATR) volatility indicator."""
    hs = _extract_values(highs)
    ls = _extract_values(lows)
    cs = _extract_values(closes)
    p = int(period)
    n = min(len(hs), len(ls), len(cs))
    if n == 0:
        return []
    trs = [hs[0] - ls[0]]
    for i in range(1, n):
        tr = max(hs[i] - ls[i], abs(hs[i] - cs[i - 1]), abs(ls[i] - cs[i - 1]))
        trs.append(tr)
    atr = []
    curr = sum(trs[:min(p, n)]) / min(p, n)
    for i in range(n):
        if i < p:
            atr.append(round(sum(trs[:i + 1]) / (i + 1), 4))
        else:
            curr = (curr * (p - 1) + trs[i]) / p
            atr.append(round(curr, 4))
    return atr


def fin_keltner_channels(highs: Any, lows: Any, closes: Any, ema_period: Any = 20, atr_period: Any = 10, multiplier: Any = 2.0) -> Dict[str, List[float]]:
    """Keltner Channels (Upper, Middle, Lower)."""
    cs = _extract_values(closes)
    mid = moving_average(cs, window=int(ema_period), kind="ema")
    atr = fin_average_true_range(highs, lows, closes, period=int(atr_period))
    mult = float(multiplier)
    upper, lower = [], []
    for m, a in zip(mid, atr):
        upper.append(round(m + mult * a, 4))
        lower.append(round(m - mult * a, 4))
    return {"middle": mid, "upper": upper, "lower": lower}


def fin_williams_r(highs: Any, lows: Any, closes: Any, period: Any = 14) -> List[float]:
    """Williams %R momentum indicator."""
    hs = _extract_values(highs)
    ls = _extract_values(lows)
    cs = _extract_values(closes)
    p = int(period)
    n = min(len(hs), len(ls), len(cs))
    wr = []
    for i in range(n):
        start = max(0, i - p + 1)
        hh = max(hs[start:i + 1])
        ll = min(ls[start:i + 1])
        denom = hh - ll
        val = ((hh - cs[i]) / denom) * -100.0 if denom > 0 else -50.0
        wr.append(round(val, 4))
    return wr


def fin_money_flow_index(highs: Any, lows: Any, closes: Any, volumes: Any, period: Any = 14) -> List[float]:
    """Money Flow Index (MFI) volume-weighted RSI."""
    hs = _extract_values(highs)
    ls = _extract_values(lows)
    cs = _extract_values(closes)
    vs = _extract_values(volumes)
    p = int(period)
    n = min(len(hs), len(ls), len(cs), len(vs))
    if n < 2:
        return [50.0] * n
    tp = [(hs[i] + ls[i] + cs[i]) / 3.0 for i in range(n)]
    pos_flow, neg_flow = [0.0] * n, [0.0] * n
    for i in range(1, n):
        raw_mf = tp[i] * vs[i]
        if tp[i] > tp[i - 1]:
            pos_flow[i] = raw_mf
        elif tp[i] < tp[i - 1]:
            neg_flow[i] = raw_mf
    mfi = []
    for i in range(n):
        start = max(0, i - p + 1)
        tot_pos = sum(pos_flow[start:i + 1])
        tot_neg = sum(neg_flow[start:i + 1])
        if tot_neg == 0:
            mfi.append(100.0)
        else:
            mr = tot_pos / tot_neg
            mfi.append(round(100.0 - (100.0 / (1.0 + mr)), 4))
    return mfi


def fin_portfolio_rebalance(current_weights: Any, target_weights: Any, total_value: Any) -> Dict[str, float]:
    """Generate trade amounts (currency) required to rebalance portfolio."""
    tot = float(total_value)
    cur = dict(current_weights)
    tgt = dict(target_weights)
    all_assets = set(cur.keys()).union(set(tgt.keys()))
    trades: Dict[str, float] = {}
    for a in all_assets:
        w_cur = float(cur.get(a, 0.0))
        w_tgt = float(tgt.get(a, 0.0))
        diff = (w_tgt - w_cur) * tot
        trades[a] = round(diff, 2)
    return trades


def fin_twap(prices: Any, timestamps: Any = None) -> float:
    """Time-Weighted Average Price across timestamps."""
    ps = _extract_values(prices)
    if not ps:
        return 0.0
    return round(sum(ps) / len(ps), 4)


def fin_donchian_channels(highs: Any, lows: Any, period: Any = 20) -> Dict[str, List[float]]:
    """Donchian Channels (Upper, Lower, Middle)."""
    hs = _extract_values(highs)
    ls = _extract_values(lows)
    p = int(period)
    n = min(len(hs), len(ls))
    upper, lower, mid = [], [], []
    for i in range(n):
        start = max(0, i - p + 1)
        u = max(hs[start:i + 1])
        l = min(ls[start:i + 1])
        upper.append(round(u, 4))
        lower.append(round(l, 4))
        mid.append(round((u + l) / 2.0, 4))
    return {"upper": upper, "lower": lower, "middle": mid}


def fin_information_ratio(asset_returns: Any, benchmark_returns: Any) -> float:
    """Information Ratio: active return over tracking error."""
    a = _extract_values(asset_returns)
    b = _extract_values(benchmark_returns)
    n = min(len(a), len(b))
    if n < 2:
        return 0.0
    diffs = [a[i] - b[i] for i in range(n)]
    mean_diff = sum(diffs) / n
    te = math.sqrt(sum((d - mean_diff) ** 2 for d in diffs) / (n - 1))
    if te == 0:
        return 0.0
    return round(mean_diff / te, 4)


def fin_drawdown_series(cumulative_returns: Any) -> List[float]:
    """Compute underwater drawdown series."""
    vals = _extract_values(cumulative_returns)
    if not vals:
        return []
    peak = vals[0]
    dd_series = []
    for v in vals:
        if v > peak:
            peak = v
        dd = (v - peak) / peak if peak > 0 else 0.0
        dd_series.append(round(dd, 4))
    return dd_series


def fin_implied_volatility_bisection(market_price: Any, spot: Any, strike: Any, t: Any, rate: Any, is_call: bool = True) -> float:
    """Solve for implied volatility via bisection search."""
    target_p = float(market_price)
    S, K, T, r = float(spot), float(strike), float(t), float(rate)
    low_vol, high_vol = 0.001, 5.0
    for _ in range(50):
        mid_vol = (low_vol + high_vol) / 2.0
        price = fin_black_scholes_call(S, K, T, r, mid_vol) if is_call else fin_black_scholes_put(S, K, T, r, mid_vol)
        if abs(price - target_p) < 1e-4:
            return round(mid_vol, 4)
        if price < target_p:
            low_vol = mid_vol
        else:
            high_vol = mid_vol
    return round((low_vol + high_vol) / 2.0, 4)


def fin_var_historical(returns: Any, confidence: Any = 0.95) -> float:
    """Historical Value at Risk."""
    return finance_value_at_risk(returns, confidence=float(confidence) * (100.0 if float(confidence) <= 1.0 else 1.0))


# =========================================================================
# Deepened Quantitative Finance Models & Indicators
# =========================================================================

def _mat_inv(A: List[List[float]]) -> List[List[float]]:
    """Matrix inverse via Gauss-Jordan elimination with partial pivoting."""
    n = len(A)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for i in range(n):
        pivot_r = max(range(i, n), key=lambda r: abs(aug[r][i]))
        if abs(aug[pivot_r][i]) < 1e-12:
            raise ValueError("Singular matrix in inversion")
        aug[i], aug[pivot_r] = aug[pivot_r], aug[i]

        p_val = aug[i][i]
        for c in range(2 * n):
            aug[i][c] /= p_val

        for r in range(n):
            if r != i:
                f = aug[r][i]
                for c in range(2 * n):
                    aug[r][c] -= f * aug[i][c]

    return [[round(aug[r][c + n], 8) for c in range(n)] for r in range(n)]


def _mat_mul(A: List[List[float]], B: List[List[float]]) -> List[List[float]]:
    rows_A, cols_A = len(A), len(A[0])
    rows_B, cols_B = len(B), len(B[0])
    res = [[0.0] * cols_B for _ in range(rows_A)]
    for i in range(rows_A):
        for k in range(cols_A):
            for j in range(cols_B):
                res[i][j] += A[i][k] * B[k][j]
    return res


def _mat_vec_mul(A: List[List[float]], v: List[float]) -> List[float]:
    return [sum(row[c] * v[c] for c in range(len(v))) for row in A]


def fin_black_litterman(
    market_weights: List[float],
    cov_matrix: List[List[float]],
    views_p: List[List[float]],
    views_q: List[float],
    tau: float = 0.05,
    risk_aversion: float = 2.5,
    view_confidences: Optional[List[float]] = None,
) -> Dict[str, Any]:
    """Black-Litterman asset allocation combining market prior with investor views."""
    n = len(market_weights)
    k = len(views_q)
    w_mkt = [float(w) for w in market_weights]
    sigma = [[float(val) for val in row] for row in cov_matrix]
    P = [[float(val) for val in row] for row in views_p]
    Q = [float(q) for q in views_q]

    # Implied equilibrium excess returns Pi = lambda * Sigma * w_mkt
    Pi = [risk_aversion * val for val in _mat_vec_mul(sigma, w_mkt)]

    # tau * Sigma
    tau_sigma = [[tau * val for val in row] for row in sigma]
    tau_sigma_inv = _mat_inv(tau_sigma)

    # View uncertainty Omega = diag(P * (tau * Sigma) * P^T)
    omega = [[0.0] * k for _ in range(k)]
    P_tau_sigma = _mat_mul(P, tau_sigma)
    P_tau_sigma_PT = _mat_mul(P_tau_sigma, [[P[j][i] for j in range(k)] for i in range(n)])

    for i in range(k):
        if view_confidences and i < len(view_confidences) and view_confidences[i] > 0:
            omega[i][i] = 1.0 / float(view_confidences[i])
        else:
            omega[i][i] = max(1e-6, P_tau_sigma_PT[i][i])

    omega_inv = _mat_inv(omega)

    # P^T * Omega^-1 * P
    PT = [[P[j][i] for j in range(k)] for i in range(n)]
    PT_omega_inv = _mat_mul(PT, omega_inv)
    PT_omega_inv_P = _mat_mul(PT_omega_inv, P)

    # Precision matrix M = (tau*Sigma)^-1 + P^T * Omega^-1 * P
    M = [[tau_sigma_inv[i][j] + PT_omega_inv_P[i][j] for j in range(n)] for i in range(n)]
    M_inv = _mat_inv(M)

    # Right hand side: (tau*Sigma)^-1 * Pi + P^T * Omega^-1 * Q
    rhs1 = _mat_vec_mul(tau_sigma_inv, Pi)
    rhs2 = _mat_vec_mul(PT_omega_inv, Q)
    rhs = [rhs1[i] + rhs2[i] for i in range(n)]

    # Posterior returns E[R] = M^-1 * rhs
    post_returns = _mat_vec_mul(M_inv, rhs)

    # Posterior weights w* = (lambda * Sigma)^-1 * E[R]
    sigma_inv = _mat_inv(sigma)
    raw_weights = [(1.0 / risk_aversion) * val for val in _mat_vec_mul(sigma_inv, post_returns)]
    tot_w = sum(raw_weights) or 1.0
    norm_weights = [round(w / tot_w, 4) for w in raw_weights]

    return {
        "implied_equilibrium_returns": [round(r, 4) for r in Pi],
        "posterior_returns": [round(r, 4) for r in post_returns],
        "posterior_weights": norm_weights,
    }


def fin_var_cvar_monte_carlo(
    current_val: float,
    mu: float,
    sigma: float,
    horizon_days: int = 10,
    simulations: int = 5000,
    confidence: float = 0.95,
    seed: int = 42,
) -> Dict[str, Any]:
    """Monte Carlo Value at Risk and Conditional Value at Risk (Expected Shortfall)."""
    import random
    rng = random.Random(seed)
    dt = float(horizon_days) / 252.0
    cur_v = float(current_val)
    drift = (float(mu) - 0.5 * (float(sigma) ** 2)) * dt
    vol = float(sigma) * math.sqrt(dt)

    losses = []
    # Box-Muller simulation
    for _ in range(max(10, simulations // 2)):
        u1 = max(1e-12, rng.random())
        u2 = rng.random()
        r_box = math.sqrt(-2.0 * math.log(u1))
        z1 = r_box * math.cos(2.0 * math.pi * u2)
        z2 = r_box * math.sin(2.0 * math.pi * u2)

        s_t1 = cur_v * math.exp(drift + vol * z1)
        s_t2 = cur_v * math.exp(drift + vol * z2)
        losses.append(cur_v - s_t1)
        losses.append(cur_v - s_t2)

    losses.sort()
    idx = int(round(float(confidence) * len(losses)))
    idx = min(idx, len(losses) - 1)
    var = max(0.0, losses[idx])
    tail_losses = [l for l in losses[idx:] if l > 0]
    cvar = sum(tail_losses) / len(tail_losses) if tail_losses else var

    return {
        "var": round(var, 2),
        "cvar": round(cvar, 2),
        "mean_loss": round(sum(losses) / len(losses), 2),
        "confidence": float(confidence),
        "horizon_days": int(horizon_days),
        "simulations": len(losses),
    }


def fin_hull_white_trinomial(
    r0: float,
    a: float,
    sigma: float,
    n_steps: int = 10,
    dt: float = 0.25,
) -> Dict[str, Any]:
    """1-Factor Hull-White short rate trinomial tree for zero-coupon bond pricing."""
    n = max(2, int(n_steps))
    delta_t = float(dt)
    r_init = float(r0)
    rev_a = float(a)
    vol = float(sigma)

    delta_r = vol * math.sqrt(3.0 * delta_t)

    # State values at maturity N: V[N][j] = 1.0 for all j in [-N, N]
    # Initialize backward induction
    values = {j: 1.0 for j in range(-n, n + 1)}

    for step in reversed(range(n)):
        next_values = {}
        for j in range(-step, step + 1):
            r_val = r_init + j * delta_r
            # Drift calculation
            drift = -rev_a * j * delta_r * delta_t
            # Branching probabilities
            term1 = (drift ** 2) / (2.0 * (delta_r ** 2))
            term2 = drift / (2.0 * delta_r)
            pu = max(0.0, min(1.0, 1.0 / 6.0 + term1 + term2))
            pm = max(0.0, min(1.0, 2.0 / 3.0 - 2.0 * term1))
            pd = max(0.0, min(1.0, 1.0 / 6.0 + term1 - term2))

            sum_p = pu + pm + pd or 1.0
            pu, pm, pd = pu / sum_p, pm / sum_p, pd / sum_p

            expected_v = (
                pu * values.get(j + 1, 1.0)
                + pm * values.get(j, 1.0)
                + pd * values.get(j - 1, 1.0)
            )
            discount = math.exp(-r_val * delta_t)
            next_values[j] = discount * expected_v
        values = next_values

    bond_price = round(values[0], 6)
    return {
        "lattice_steps": n,
        "dt": delta_t,
        "bond_price": bond_price,
        "yield_to_maturity": round(-math.log(max(1e-6, bond_price)) / (n * delta_t), 4),
        "short_rate": r_init,
    }


def fin_ichimoku_cloud(
    highs: Any,
    lows: Any,
    closes: Any,
    tenkan_period: int = 9,
    kijun_period: int = 26,
    senkou_b_period: int = 52,
    displacement: int = 26,
) -> Dict[str, List[Optional[float]]]:
    """Ichimoku Kinko Hyo indicator (Tenkan, Kijun, Senkou A/B, Chikou)."""
    hs = _extract_values(highs)
    ls = _extract_values(lows)
    cs = _extract_values(closes)
    n = min(len(hs), len(ls), len(cs))
    if n == 0:
        return {"tenkan": [], "kijun": [], "senkou_a": [], "senkou_b": [], "chikou": []}

    tenkan: List[Optional[float]] = []
    kijun: List[Optional[float]] = []
    senkou_a: List[Optional[float]] = [None] * n
    senkou_b: List[Optional[float]] = [None] * n
    chikou: List[Optional[float]] = [None] * n

    for i in range(n):
        # Tenkan-sen (Conversion Line)
        t_start = max(0, i - tenkan_period + 1)
        t_val = round((max(hs[t_start : i + 1]) + min(ls[t_start : i + 1])) / 2.0, 4)
        tenkan.append(t_val)

        # Kijun-sen (Base Line)
        k_start = max(0, i - kijun_period + 1)
        k_val = round((max(hs[k_start : i + 1]) + min(ls[k_start : i + 1])) / 2.0, 4)
        kijun.append(k_val)

        # Senkou Span A (Leading Span A) plotted displacement ahead
        lead_idx = i + displacement
        if lead_idx < n:
            senkou_a[lead_idx] = round((t_val + k_val) / 2.0, 4)

        # Senkou Span B plotted displacement ahead
        sb_start = max(0, i - senkou_b_period + 1)
        sb_val = round((max(hs[sb_start : i + 1]) + min(ls[sb_start : i + 1])) / 2.0, 4)
        if lead_idx < n:
            senkou_b[lead_idx] = sb_val

        # Chikou Span (Lagging Span) plotted displacement behind
        lag_idx = i - displacement
        if lag_idx >= 0:
            chikou[lag_idx] = round(cs[i], 4)

    return {
        "tenkan": tenkan,
        "kijun": kijun,
        "senkou_a": senkou_a,
        "senkou_b": senkou_b,
        "chikou": chikou,
    }


def fin_monte_carlo_var(
    initial_portfolio_value: float,
    expected_annual_return: float,
    annual_volatility: float,
    time_horizon_days: int = 10,
    num_simulations: int = 1000,
    seed: Optional[int] = 42,
) -> Dict[str, float]:
    """Computes Monte Carlo Value at Risk (VaR) and Expected Shortfall (CVaR) using Geometric Brownian Motion.
    Returns 95% and 99% VaR in absolute currency and percentage loss.
    """
    if seed is not None:
        random.seed(seed)

    S0 = float(initial_portfolio_value)
    mu = float(expected_annual_return)
    sigma = float(annual_volatility)
    dt = float(time_horizon_days) / 252.0  # trading year
    drift = (mu - 0.5 * sigma * sigma) * dt
    vol_sqrt_dt = sigma * math.sqrt(dt)

    final_values: List[float] = []
    pnl_losses: List[float] = []

    for _ in range(num_simulations):
        # Box-Muller transform for standard normal random variable
        u1 = max(1e-12, random.random())
        u2 = random.random()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)

        st = S0 * math.exp(drift + vol_sqrt_dt * z)
        final_values.append(st)
        loss = S0 - st  # positive means loss
        pnl_losses.append(loss)

    # Sort losses in ascending order (higher loss at end)
    sorted_losses = sorted(pnl_losses)
    idx_95 = int(num_simulations * 0.95)
    idx_99 = int(num_simulations * 0.99)

    var_95 = max(0.0, sorted_losses[idx_95])
    var_99 = max(0.0, sorted_losses[idx_99])

    # Expected Shortfall (CVaR) = average of losses beyond VaR
    tail_95 = [l for l in sorted_losses[idx_95:]]
    tail_99 = [l for l in sorted_losses[idx_99:]]

    cvar_95 = sum(tail_95) / len(tail_95) if tail_95 else var_95
    cvar_99 = sum(tail_99) / len(tail_99) if tail_99 else var_99

    return {
        "var_95": round(var_95, 2),
        "var_99": round(var_99, 2),
        "var_95_pct": round((var_95 / S0) * 100.0, 3),
        "var_99_pct": round((var_99 / S0) * 100.0, 3),
        "cvar_95": round(cvar_95, 2),
        "cvar_99": round(cvar_99, 2),
        "mean_final_value": round(sum(final_values) / num_simulations, 2),
        "median_final_value": round(sorted(final_values)[num_simulations // 2], 2),
    }

