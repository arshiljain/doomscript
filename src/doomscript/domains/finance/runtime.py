"""Runtime execution engine for Quantitative Finance & Time Series domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import math
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
