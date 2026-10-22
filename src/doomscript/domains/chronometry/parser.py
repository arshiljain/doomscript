import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ChronometryDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_jdn = re.match(r"^calculate\s+julian\s+day\s+year\s+(.+?)\s+month\s+(.+?)\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jdn:
            return f"set {m_jdn.group(4)} to chrono_julian_day_number({m_jdn.group(1)}, {m_jdn.group(2)}, {m_jdn.group(3)})"

        m_gmst = re.match(r"^calculate\s+gmst\s+jdn\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gmst:
            return f"set {m_gmst.group(2)} to chrono_greenwich_mean_sidereal_time({m_gmst.group(1)})"

        m_eot = re.match(r"^calculate\s+equation\s+of\s+time\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eot:
            return f"set {m_eot.group(2)} to chrono_equation_of_time({m_eot.group(1)})"

        m_dil = re.match(r"^calculate\s+time\s+dilation\s+proper\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dil:
            return f"set {m_dil.group(3)} to chrono_relativistic_time_dilation({m_dil.group(1)}, {m_dil.group(2)})"

        m_grav = re.match(r"^calculate\s+gravitational\s+dilation\s+proper\s+(.+?)\s+mass\s+(.+?)\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_grav:
            return f"set {m_grav.group(4)} to chrono_gravitational_time_dilation({m_grav.group(1)}, {m_grav.group(2)}, {m_grav.group(3)})"

        m_sol = re.match(r"^calculate\s+solar\s+declination\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sol:
            return f"set {m_sol.group(2)} to chrono_solar_declination({m_sol.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Chronometry domain does not define declarative blocks")
