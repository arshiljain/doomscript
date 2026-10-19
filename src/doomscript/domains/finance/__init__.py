"""Quantitative Finance & Time Series Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.finance.spec import (
    FinanceFetchSpec,
    FinanceMavSpec,
    FinanceRsiSpec,
    FinanceReturnsSpec,
    FinanceSharpeSpec,
    FinanceBacktestSpec,
)
from doomscript.domains.finance.parser import FinanceDomainParser
from doomscript.domains.finance.runtime import (
    FinanceRuntime,
    fetch_stock_prices,
    moving_average,
    relative_strength_index,
    calculate_daily_returns,
    calculate_sharpe_ratio,
    backtest_strategy,
    execute_finance_ir,
)
from doomscript.domains.finance.exporter import FinanceASTExporter
from doomscript.domains.registry import get_domain_registry


class FinanceDomain(DomainContract):
    """Quantitative Finance & Time Series domain pack."""

    name = "finance"
    aliases = ["quant", "trading", "timeseries"]
    parser = FinanceDomainParser()
    runtime = FinanceRuntime()
    exporter = FinanceASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("fetch stock ")
            or s.startswith("fetch stock prices ")
            or s.startswith("calculate daily returns ")
            or s.startswith("daily returns of ")
            or s.startswith("calculate sharpe ratio ")
            or s.startswith("sharpe ratio of ")
            or s.startswith("calculate rsi ")
            or s.startswith("rsi of ")
            or s.startswith("backtest strategy on ")
        ):
            return True

        if ("day moving average" in s or "day sma" in s or "day ema" in s) and " into " in s:
            return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
FINANCE_DOMAIN = FinanceDomain()
get_domain_registry().register(FINANCE_DOMAIN)

__all__ = [
    "FinanceDomain",
    "FINANCE_DOMAIN",
    "FinanceFetchSpec",
    "FinanceMavSpec",
    "FinanceRsiSpec",
    "FinanceReturnsSpec",
    "FinanceSharpeSpec",
    "FinanceBacktestSpec",
    "FinanceDomainParser",
    "FinanceRuntime",
    "FinanceASTExporter",
    "fetch_stock_prices",
    "moving_average",
    "relative_strength_index",
    "calculate_daily_returns",
    "calculate_sharpe_ratio",
    "backtest_strategy",
    "execute_finance_ir",
]
