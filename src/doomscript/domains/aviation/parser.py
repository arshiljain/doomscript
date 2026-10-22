import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AviationDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_pa = re.match(r"^calculate\s+pressure\s+altitude\s+altimeter\s+(.+?)\s+elevation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pa:
            return f"set {m_pa.group(3)} to aviation_pressure_altitude({m_pa.group(1)}, {m_pa.group(2)})"

        m_da = re.match(r"^calculate\s+density\s+altitude\s+pressure_alt\s+(.+?)\s+oat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_da:
            return f"set {m_da.group(3)} to aviation_density_altitude({m_da.group(1)}, {m_da.group(2)})"

        m_wind = re.match(r"^calculate\s+wind\s+components\s+wind_speed\s+(.+?)\s+wind_dir\s+(.+?)\s+runway\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wind:
            return f"set {m_wind.group(4)} to aviation_wind_components({m_wind.group(1)}, {m_wind.group(2)}, {m_wind.group(3)})"

        m_turn = re.match(r"^calculate\s+turn\s+radius\s+tas\s+(.+?)\s+bank\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_turn:
            return f"set {m_turn.group(3)} to aviation_turn_radius({m_turn.group(1)}, {m_turn.group(2)})"

        m_stall = re.match(r"^calculate\s+banked\s+stall\s+speed\s+vs0\s+(.+?)\s+bank\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stall:
            return f"set {m_stall.group(3)} to aviation_banked_stall_speed({m_stall.group(1)}, {m_stall.group(2)})"

        m_climb = re.match(r"^calculate\s+climb\s+gradient\s+roc\s+(.+?)\s+tas\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_climb:
            return f"set {m_climb.group(3)} to aviation_climb_gradient({m_climb.group(1)}, {m_climb.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Aviation domain does not define declarative blocks")
