import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ChronometryDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate julian day year <y> month <m> day <d> into <target>
        m_jdn = re.match(r"^calculate\s+julian\s+day\s+year\s+(.+?)\s+month\s+(.+?)\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jdn:
            return f"set {m_jdn.group(4)} to chrono_julian_day_number({m_jdn.group(1)}, {m_jdn.group(2)}, {m_jdn.group(3)})"

        # calculate gmst jdn <jdn> into <target>
        m_gmst = re.match(r"^calculate\s+gmst\s+jdn\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gmst:
            return f"set {m_gmst.group(2)} to chrono_greenwich_mean_sidereal_time({m_gmst.group(1)})"

        # calculate equation of time day <d> into <target>
        m_eot = re.match(r"^calculate\s+equation\s+of\s+time\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eot:
            return f"set {m_eot.group(2)} to chrono_equation_of_time({m_eot.group(1)})"

        # calculate time dilation proper <t0> velocity <v> into <target>
        m_td = re.match(r"^calculate\s+time\s+dilation\s+proper\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_td:
            return f"set {m_td.group(3)} to chrono_relativistic_time_dilation({m_td.group(1)}, {m_td.group(2)})"

        # calculate gravitational dilation proper <t0> mass <m> radius <r> into <target>
        m_gd = re.match(r"^calculate\s+gravitational\s+dilation\s+proper\s+(.+?)\s+mass\s+(.+?)\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gd:
            return f"set {m_gd.group(4)} to chrono_gravitational_time_dilation({m_gd.group(1)}, {m_gd.group(2)}, {m_gd.group(3)})"

        # calculate solar declination day <d> into <target>
        m_sd = re.match(r"^calculate\s+solar\s+declination\s+day\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sd:
            return f"set {m_sd.group(2)} to chrono_solar_declination({m_sd.group(1)})"

        # calculate gps drift altitude <alt> velocity <v> into <target>
        m_gps = re.match(r"^calculate\s+gps\s+drift\s+altitude\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gps:
            return f"set {m_gps.group(3)} to chrono_gps_relativistic_drift({m_gps.group(1)}, {m_gps.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Chronometry domain does not define declarative blocks")
