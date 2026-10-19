"""Signals Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class SignalsDomainParser(DomainParser):
    """Parses spoken-English DSP, wavelet, and signal filtering statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # decompose signal <sig> using haar wavelet into <target>
        m_haar = re.match(
            r"^decompose\s+signal\s+(.+?)\s+using\s+haar\s+wavelet\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_haar:
            sig, target = m_haar.group(1).strip(), m_haar.group(2).strip()
            return f"set {target} to signals_haar_dwt({sig})"

        # apply fir lowpass filter to <sig> with cutoff <cut> and rate <rate> into <target>
        m_fir = re.match(
            r"^apply\s+fir\s+lowpass\s+filter\s+to\s+(.+?)\s+with\s+cutoff\s+(.+?)\s+and\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fir:
            sig, cut, rate, target = m_fir.group(1).strip(), m_fir.group(2).strip(), m_fir.group(3).strip(), m_fir.group(4).strip()
            return f"set {target} to signals_fir_lowpass({sig}, 31, {cut}, {rate})"

        # calculate analytic signal of <sig> using hilbert into <target>
        m_hilb = re.match(
            r"^calculate\s+analytic\s+signal\s+of\s+(.+?)\s+using\s+hilbert\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hilb:
            sig, target = m_hilb.group(1).strip(), m_hilb.group(2).strip()
            return f"set {target} to signals_hilbert({sig})"

        # find peaks in signal <sig> into <target>
        m_peaks = re.match(
            r"^find\s+peaks\s+in\s+signal\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_peaks:
            sig, target = m_peaks.group(1).strip(), m_peaks.group(2).strip()
            return f"set {target} to signals_find_peaks({sig})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Signals domain does not define declarative blocks")
