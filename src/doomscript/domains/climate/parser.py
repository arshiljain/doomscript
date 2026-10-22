import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ClimateDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_dp = re.match(r"^calculate\s+dew\s+point\s+for\s+temperature\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dp:
            return f"set {m_dp.group(3)} to climate_dew_point({m_dp.group(1)}, {m_dp.group(2)})"

        m_hi = re.match(r"^calculate\s+heat\s+index\s+for\s+temperature\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hi:
            return f"set {m_hi.group(3)} to climate_heat_index({m_hi.group(1)}, {m_hi.group(2)})"

        m_wc = re.match(r"^calculate\s+wind\s+chill\s+for\s+temperature\s+(.+?)\s+wind\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wc:
            return f"set {m_wc.group(3)} to climate_wind_chill({m_wc.group(1)}, {m_wc.group(2)})"

        m_vpd = re.match(r"^calculate\s+vpd\s+for\s+temperature\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vpd:
            return f"set {m_vpd.group(3)} to climate_vapor_pressure_deficit({m_vpd.group(1)}, {m_vpd.group(2)})"

        m_press = re.match(r"^calculate\s+barometric\s+pressure\s+at\s+altitude\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_press:
            return f"set {m_press.group(2)} to climate_barometric_altitude({m_press.group(1)})"

        m_co2 = re.match(r"^convert\s+emissions\s+(.+?)\s+of\s+gas\s+(.+?)\s+to\s+co2\s+equivalent\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_co2:
            return f"set {m_co2.group(3)} to climate_co2_equivalent({m_co2.group(1)}, {m_co2.group(2)})"

        m_rad = re.match(r"^calculate\s+radiative\s+forcing\s+for\s+co2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rad:
            return f"set {m_rad.group(2)} to climate_radiative_forcing({m_rad.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Climate domain does not define declarative blocks")
