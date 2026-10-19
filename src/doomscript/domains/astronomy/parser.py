"""Astronomy Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class AstronomyDomainParser(DomainParser):
    """Parses spoken-English astronomy, Keplerian orbits, and celestial coordinate statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate julian date for year <y> month <m> day <d> into <target>
        m_jd = re.match(
            r"^calculate\s+julian\s+date\s+for\s+year\s+(.+?)\s+month\s+(.+?)\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_jd:
            y, m, d, target = m_jd.group(1).strip(), m_jd.group(2).strip(), m_jd.group(3).strip(), m_jd.group(4).strip()
            return f"set {target} to astronomy_julian_date({y}, {m}, {d})"

        # calculate hohmann transfer from radius <r1> to <r2> into <target>
        m_hoh = re.match(
            r"^calculate\s+hohmann\s+transfer\s+from\s+radius\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hoh:
            r1, r2, target = m_hoh.group(1).strip(), m_hoh.group(2).strip(), m_hoh.group(3).strip()
            return f"set {target} to astronomy_hohmann_transfer({r1}, {r2})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Astronomy domain does not define declarative blocks")
