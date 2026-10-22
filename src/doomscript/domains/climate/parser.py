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

        m_baro = re.match(r"^calculate\s+barometric\s+pressure\s+at\s+altitude\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_baro:
            return f"set {m_baro.group(2)} to climate_barometric_pressure({m_baro.group(1)})"

        m_co2 = re.match(r"^convert\s+emissions\s+(.+?)\s+of\s+gas\s+(.+?)\s+to\s+co2\s+equivalent\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_co2:
            return f"set {m_co2.group(3)} to climate_co2_equivalent({m_co2.group(1)}, {m_co2.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Climate domain does not define declarative blocks")
