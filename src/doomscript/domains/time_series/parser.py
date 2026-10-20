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

        # calculate sakoe chiba dtw between <a> and <b> [with window <w>] into <target>
        m_dtw = re.match(
            r"^calculate\s+sakoe\s+chiba\s+dtw\s+between\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+window\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dtw:
            a, b = m_dtw.group(1).strip(), m_dtw.group(2).strip()
            w = m_dtw.group(3) if m_dtw.group(3) else "5"
            target = m_dtw.group(4).strip()
            return f"set {target} to timeseries_dtw_sakoe_chiba({a}, {b}, band_window={w})"

        # calculate spectral periodogram of <series> [with rate <fs>] [with window <win>] [with peaks <k>] into <target>
        m_spec = re.match(
            r"^calculate\s+spectral\s+periodogram\s+of\s+(.+?)(?:\s+with\s+rate\s+(.+?))?(?:\s+with\s+window\s+(.+?))?(?:\s+with\s+peaks\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_spec:
            series = m_spec.group(1).strip()
            rate = m_spec.group(2).strip() if m_spec.group(2) else "1.0"
            win = m_spec.group(3).strip() if m_spec.group(3) else '"hann"'
            if not (win.startswith('"') or win.startswith("'")):
                win = f'"{win}"'
            peaks = m_spec.group(4) if m_spec.group(4) else "3"
            target = m_spec.group(5).strip()
            return f"set {target} to timeseries_spectral_periodogram({series}, sampling_rate={rate}, window_type={win}, top_k_peaks={peaks})"

        # fit var model on <data> [lags <p>] [forecast <h>] into <target>
        m_var = re.match(
            r"^fit\s+var\s+model\s+on\s+(.+?)(?:\s+lags\s+(\d+))?(?:\s+forecast\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_var:
            data_arg, lags_arg, h_arg, target = (
                m_var.group(1).strip(),
                m_var.group(2),
                m_var.group(3),
                m_var.group(4).strip(),
            )
            p_val = lags_arg.strip() if lags_arg else "1"
            h_val = h_arg.strip() if h_arg else "3"
            return f"set {target} to timeseries_fit_var_model({data_arg}, lags={p_val}, forecast_steps={h_val})"

        # apply kalman filter to <measurements> [process_q <q>] [measurement_r <r>] into <target>
        m_kf = re.match(
            r"^apply\s+kalman\s+filter\s+to\s+(.+?)(?:\s+process_q\s+(.+?))?(?:\s+measurement_r\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kf:
            data_arg, q_arg, r_arg, target = (
                m_kf.group(1).strip(),
                m_kf.group(2),
                m_kf.group(3),
                m_kf.group(4).strip(),
            )
            q_val = q_arg.strip() if q_arg else "1e-4"
            r_val = r_arg.strip() if r_arg else "1e-2"
            return f"set {target} to timeseries_kalman_filter_smooth({data_arg}, process_variance_q={q_val}, measurement_variance_r={r_val})"

        # fit sarima on <data> [order <p> <d> <q>] [seasonal <P> <D> <Q> <s>] [forecast <h>] into <target>
        m_sarima = re.match(
            r"^fit\s+sarima\s+on\s+(.+?)(?:\s+order\s+(\d+)\s+(\d+)\s+(\d+))?(?:\s+seasonal\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+))?(?:\s+forecast\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sarima:
            data_arg = m_sarima.group(1).strip()
            p = m_sarima.group(2) if m_sarima.group(2) else "1"
            d = m_sarima.group(3) if m_sarima.group(3) else "1"
            q = m_sarima.group(4) if m_sarima.group(4) else "0"
            P = m_sarima.group(5) if m_sarima.group(5) else "0"
            D = m_sarima.group(6) if m_sarima.group(6) else "0"
            Q = m_sarima.group(7) if m_sarima.group(7) else "0"
            s_val = m_sarima.group(8) if m_sarima.group(8) else "4"
            h = m_sarima.group(9) if m_sarima.group(9) else "4"
            target = m_sarima.group(10).strip()
            return f"set {target} to timeseries_sarima_forecast({data_arg}, p={p}, d={d}, q={q}, P={P}, D={D}, Q={Q}, s={s_val}, forecast_steps={h})"

        # decompose emd series <data> [max imfs <m>] into <target>
        m_emd = re.match(
            r"^decompose\s+emd\s+series\s+(.+?)(?:\s+max\s+imfs\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_emd:
            data_arg = m_emd.group(1).strip()
            m_val = m_emd.group(2) if m_emd.group(2) else "3"
            target = m_emd.group(3).strip()
            return f"set {target} to timeseries_emd_decompose({data_arg}, max_imfs={m_val})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Time series domain does not define declarative blocks")
