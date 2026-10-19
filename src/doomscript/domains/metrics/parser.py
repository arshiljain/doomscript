"""Metrics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class MetricsDomainParser(DomainParser):
    """Parses spoken-English metrics, counters, histograms, and Prometheus statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create counter <name> into <target>
        m_cnt = re.match(
            r"^create\s+counter\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cnt:
            name, target = m_cnt.group(1).strip(), m_cnt.group(2).strip()
            if not (name.startswith('"') or name.startswith("'") or name.isidentifier()):
                name = f'"{name}"'
            return f"set {target} to metrics_counter({name})"

        # create gauge <name> into <target>
        m_g = re.match(
            r"^create\s+gauge\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_g:
            name, target = m_g.group(1).strip(), m_g.group(2).strip()
            if not (name.startswith('"') or name.startswith("'") or name.isidentifier()):
                name = f'"{name}"'
            return f"set {target} to metrics_gauge({name})"

        # export openmetrics [metrics] into <target>
        m_exp = re.match(
            r"^export\s+(?:openmetrics|domain\s+metrics)(?:\s+metrics)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_exp:
            target = m_exp.group(1).strip()
            return f"set {target} to metrics_export_openmetrics()"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Metrics domain does not define declarative blocks")
