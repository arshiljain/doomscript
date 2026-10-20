"""Time Series Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class TimeSeriesDomainParser(DomainParser):
    """Parses spoken-English time series decomposition, ACF, and forecasting statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # decompose time series <series> with period <period> into <target>
        m_dec = re.match(
            r"^decompose\s+time\s+series\s+(.+?)\s+with\s+period\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dec:
            series, period, target = m_dec.group(1).strip(), m_dec.group(2).strip(), m_dec.group(3).strip()
            return f"set {target} to time_series_decompose({series}, period={period})"

        # calculate acf of <series> with lags <lags> into <target>
        m_acf = re.match(
            r"^calculate\s+acf\s+of\s+(.+?)\s+with\s+lags\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_acf:
            series, lags, target = m_acf.group(1).strip(), m_acf.group(2).strip(), m_acf.group(3).strip()
            return f"set {target} to time_series_acf({series}, nlags={lags})"

        # calculate pacf of <series> with lags <lags> into <target>
        m_pacf = re.match(
            r"^calculate\s+pacf\s+of\s+(.+?)\s+with\s+lags\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pacf:
            series, lags, target = m_pacf.group(1).strip(), m_pacf.group(2).strip(), m_pacf.group(3).strip()
            return f"set {target} to time_series_pacf({series}, nlags={lags})"

        # forecast holt winters on <series> [with period <m>] [with steps <steps>] into <target>
        m_hw = re.match(
            r"^forecast\s+holt\s+winters\s+on\s+(.+?)(?:\s+with\s+period\s+(\d+))?(?:\s+with\s+steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hw:
            series = m_hw.group(1).strip()
            period = m_hw.group(2) if m_hw.group(2) else "4"
            steps = m_hw.group(3) if m_hw.group(3) else "4"
            target = m_hw.group(4).strip()
            return f"set {target} to timeseries_holt_winters({series}, season_period={period}, forecast_steps={steps})"

        # forecast ar model on <series> [with order <p>] [with steps <steps>] into <target>
        m_ar = re.match(
            r"^forecast\s+ar\s+model\s+on\s+(.+?)(?:\s+with\s+order\s+(\d+))?(?:\s+with\s+steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ar:
            series = m_ar.group(1).strip()
            order = m_ar.group(2) if m_ar.group(2) else "2"
            steps = m_ar.group(3) if m_ar.group(3) else "3"
            target = m_ar.group(4).strip()
            return f"set {target} to timeseries_ar_forecast({series}, order_p={order}, forecast_steps={steps})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Time series domain does not define declarative blocks")
