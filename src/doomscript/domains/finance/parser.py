"""Independent Domain Parser for Quantitative Finance & Time Series domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.finance.spec import (
    FinanceFetchSpec,
    FinanceMavSpec,
    FinanceRsiSpec,
    FinanceReturnsSpec,
    FinanceSharpeSpec,
    FinanceBacktestSpec,
)


class FinanceDomainParser(DomainParser):
    """Independent parser for Quantitative Finance syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # fetch stock [prices for] <symbol> [from <start> to <end>] into <target>
        m_fetch = re.match(
            r"^fetch\s+stock(?:\s+prices\s+for)?\s+(.+?)(?:\s+from\s+(.+?)\s+to\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fetch:
            sym_expr = m_fetch.group(1).strip()
            start_expr = m_fetch.group(2).strip() if m_fetch.group(2) else '"2024-01-01"'
            end_expr = m_fetch.group(3).strip() if m_fetch.group(3) else '"2024-12-31"'
            target = m_fetch.group(4).strip()
            return f"set {target} to fetch_stock_prices({sym_expr}, start_date={start_expr}, end_date={end_expr})"

        # calculate <n> day (moving average|sma|ema) of <series> into <target>
        m_mav = re.match(
            r"^(?:calculate\s+)?(\d+)\s+day\s+(moving\s+average|sma|ema|exponential\s+moving\s+average)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mav:
            window = m_mav.group(1).strip()
            kind_raw = m_mav.group(2).lower()
            kind = "ema" if "e" in kind_raw else "sma"
            series_expr = m_mav.group(3).strip()
            target = m_mav.group(4).strip()
            return f'set {target} to moving_average({series_expr}, window={window}, kind="{kind}")'

        # calculate rsi of <series> [over <n> days] into <target>
        m_rsi = re.match(
            r"^(?:calculate\s+)?rsi\s+of\s+(.+?)(?:\s+over\s+(\d+)\s+days?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rsi:
            series_expr = m_rsi.group(1).strip()
            period = m_rsi.group(2).strip() if m_rsi.group(2) else "14"
            target = m_rsi.group(3).strip()
            return f"set {target} to relative_strength_index({series_expr}, period={period})"

        # calculate daily returns of <series> into <target>
        m_ret = re.match(
            r"^(?:calculate\s+)?daily\s+returns\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ret:
            series_expr = m_ret.group(1).strip()
            target = m_ret.group(2).strip()
            return f"set {target} to calculate_daily_returns({series_expr})"

        # calculate sharpe ratio of <series> [with risk_free_rate <rf>] into <target>
        m_sharpe = re.match(
            r"^(?:calculate\s+)?sharpe\s+ratio\s+of\s+(.+?)(?:\s+with\s+risk_free_rate\s+(\d+(?:\.\d+)?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sharpe:
            series_expr = m_sharpe.group(1).strip()
            rf = m_sharpe.group(2).strip() if m_sharpe.group(2) else "0.04"
            target = m_sharpe.group(3).strip()
            return f"set {target} to calculate_sharpe_ratio({series_expr}, risk_free_rate={rf})"

        # backtest strategy on <prices> [where <cond>] into <target>
        m_bt = re.match(
            r"^backtest\s+strategy\s+on\s+(.+?)(?:\s+where\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bt:
            prices_expr = m_bt.group(1).strip()
            cond = f'"{m_bt.group(2).strip()}"' if m_bt.group(2) else '"crossover"'
            target = m_bt.group(3).strip()
            return f"set {target} to backtest_strategy({prices_expr}, condition={cond})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Finance domain does not currently define declarative blocks")
