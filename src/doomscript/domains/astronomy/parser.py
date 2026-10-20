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
            r"^calculate\s+hohmann\s+transfer\s+(?:from\s+(?:radius\s+)?)?(.+?)\s+to\s+(.+?)(?:\s+around\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hoh:
            r1, r2 = m_hoh.group(1).strip(), m_hoh.group(2).strip()
            mu = m_hoh.group(3).strip() if m_hoh.group(3) else "3.986004418e14"
            target = m_hoh.group(4).strip()
            return f"set {target} to astronomy_calculate_hohmann({r1}, {r2}, {mu})"

        # simulate n body system with bodies <bodies> duration <dur> [with dt <dt>] into <target>
        m_nb = re.match(
            r"^simulate\s+n\s+body\s+system\s+with\s+bodies\s+(.+?)\s+duration\s+(.+?)(?:\s+with\s+dt\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_nb:
            bodies, dur = m_nb.group(1).strip(), m_nb.group(2).strip()
            dt = m_nb.group(3).strip() if m_nb.group(3) else "60.0"
            target = m_nb.group(4).strip()
            return f"set {target} to astronomy_simulate_n_body({bodies}, {dur}, {dt})"

        # calculate bi-elliptic transfer from <r1> to <r2> via <rb> [around <mu>] into <target>
        m_bi = re.match(
            r"^calculate\s+bi-elliptic\s+transfer\s+from\s+(.+?)\s+to\s+(.+?)\s+via\s+(.+?)(?:\s+around\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bi:
            r1, r2, rb = m_bi.group(1).strip(), m_bi.group(2).strip(), m_bi.group(3).strip()
            mu = m_bi.group(4).strip() if m_bi.group(4) else "3.986004418e14"
            target = m_bi.group(5).strip()
            return f"set {target} to astronomy_calculate_bi_elliptic({r1}, {r2}, {rb}, {mu})"

        # precess coordinates ra <ra> dec <dec> to date <jd> into <target>
        m_pr = re.match(
            r"^precess\s+coordinates\s+ra\s+(.+?)\s+dec\s+(.+?)\s+to\s+date\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pr:
            ra, dec, jd, target = m_pr.group(1).strip(), m_pr.group(2).strip(), m_pr.group(3).strip(), m_pr.group(4).strip()
            return f"set {target} to astronomy_precession_j2000_to_date({ra}, {dec}, {jd})"

        # calculate celestial rise and set for ra <ra> dec <dec> at lat <lat> lon <lon> on <jd> into <target>
        m_rs = re.match(
            r"^calculate\s+celestial\s+rise\s+and\s+set\s+for\s+ra\s+(.+?)\s+dec\s+(.+?)\s+at\s+lat\s+(.+?)\s+lon\s+(.+?)\s+on\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rs:
            ra, dec, lat, lon, jd = m_rs.group(1).strip(), m_rs.group(2).strip(), m_rs.group(3).strip(), m_rs.group(4).strip(), m_rs.group(5).strip()
            target = m_rs.group(6).strip()
            return f"set {target} to astronomy_calculate_rise_set({ra}, {dec}, {lat}, {lon}, {jd})"

        # solve lambert transfer from <r1> to <r2> with tof <tof> into <target>
        m_lamb = re.match(
            r"^solve\s+lambert\s+transfer\s+from\s+(.+?)\s+to\s+(.+?)\s+with\s+tof\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lamb:
            r1, r2, tof, target = m_lamb.group(1).strip(), m_lamb.group(2).strip(), m_lamb.group(3).strip(), m_lamb.group(4).strip()
            return f"set {target} to astronomy_lambert_solve({r1}, {r2}, {tof})"

        # calculate lagrange points for mass1 <m1> and mass2 <m2> at distance <dist> into <target>
        m_lag = re.match(
            r"^calculate\s+lagrange\s+points\s+for\s+mass1\s+(.+?)\s+and\s+mass2\s+(.+?)\s+at\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lag:
            m1, m2, dist, target = m_lag.group(1).strip(), m_lag.group(2).strip(), m_lag.group(3).strip(), m_lag.group(4).strip()
            return f"set {target} to astronomy_lagrange_points({m1}, {m2}, {dist})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Astronomy domain does not define declarative blocks")
