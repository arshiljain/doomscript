"""Unit and integration tests for Quantitative Finance & Time Series domain (use finance)."""

import pytest
from doomscript.compiler.engine import execute, export_to_python
from doomscript.domains.finance.runtime import (
    fetch_stock_prices,
    moving_average,
    relative_strength_index,
    calculate_daily_returns,
    calculate_sharpe_ratio,
    backtest_strategy,
)


def test_finance_runtime_direct():
    quotes = fetch_stock_prices("AAPL", start_date="2024-01-01", end_date="2024-03-31")
    assert len(quotes) > 40
    assert "close" in quotes[0]

    # SMA & EMA
    sma = moving_average(quotes, window=5, kind="sma")
    assert len(sma) == len(quotes)
    ema = moving_average(quotes, window=5, kind="ema")
    assert len(ema) == len(quotes)

    # RSI
    rsi = relative_strength_index(quotes, period=14)
    assert len(rsi) == len(quotes)
    assert all(0 <= r <= 100 for r in rsi)

    # Daily returns
    rets = calculate_daily_returns(quotes)
    assert len(rets) == len(quotes)

    # Sharpe ratio
    sharpe = calculate_sharpe_ratio(quotes, risk_free_rate=0.04)
    assert isinstance(sharpe, float)

    # Backtest
    report = backtest_strategy(quotes)
    assert "total_return_pct" in report
    assert "trades" in report


def test_finance_domain_script_execution():
    source = """use finance

fetch stock prices for "MSFT" from "2024-01-01" to "2024-06-30" into quotes
calculate 20 day moving average of quotes into sma20
calculate rsi of quotes over 14 days into rsi14
calculate daily returns of quotes into returns_series
calculate sharpe ratio of quotes into sharpe_val
backtest strategy on quotes into bt_report
"""
    env = execute(source)
    assert len(env["quotes"]) > 100
    assert len(env["sma20"]) == len(env["quotes"])
    assert len(env["rsi14"]) == len(env["quotes"])
    assert len(env["returns_series"]) == len(env["quotes"])
    assert isinstance(env["sharpe_val"], float)
    assert "trades" in env["bt_report"]


def test_finance_domain_python_export():
    source = """use finance

fetch stock prices for "GOOGL" from "2024-01-01" to "2024-03-31" into data
calculate 10 day moving average of data into sma
calculate sharpe ratio of data into ratio
"""
    py_code = export_to_python(source)
    assert "fetch_stock_prices" in py_code
    assert "moving_average" in py_code
    assert "calculate_sharpe_ratio" in py_code
