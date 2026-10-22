import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ThermodynamicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_carnot = re.match(r"^calculate\s+carnot\s+efficiency\s+hot\s+(.+?)\s+cold\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_carnot:
            return f"set {m_carnot.group(3)} to thermo_carnot_efficiency({m_carnot.group(1)}, {m_carnot.group(2)})"

        m_entropy = re.match(r"^calculate\s+entropy\s+change\s+mass\s+(.+?)\s+specific\s+heat\s+(.+?)\s+t1\s+(.+?)\s+t2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_entropy:
            return f"set {m_entropy.group(5)} to thermo_entropy_change({m_entropy.group(1)}, {m_entropy.group(2)}, {m_entropy.group(3)}, {m_entropy.group(4)})"

        m_poly = re.match(r"^step\s+polytropic\s+p1\s+(.+?)\s+v1\s+(.+?)\s+v2\s+(.+?)\s+index\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_poly:
            return f"set {m_poly.group(5)} to thermo_polytropic_process({m_poly.group(1)}, {m_poly.group(2)}, {m_poly.group(3)}, {m_poly.group(4)})"

        m_cc = re.match(r"^calculate\s+vapor\s+pressure\s+p1\s+(.+?)\s+t1\s+(.+?)\s+t2\s+(.+?)\s+delta\s+h\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cc:
            return f"set {m_cc.group(5)} to thermo_clausius_clapeyron({m_cc.group(1)}, {m_cc.group(2)}, {m_cc.group(3)}, {m_cc.group(4)})"

        m_rank = re.match(r"^calculate\s+rankine\s+cycle\s+boiler\s+(.+?)\s+turbine\s+(.+?)\s+condenser\s+(.+?)\s+pump\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rank:
            return f"set {m_rank.group(5)} to thermo_rankine_cycle_efficiency({m_rank.group(1)}, {m_rank.group(2)}, {m_rank.group(3)}, {m_rank.group(4)})"

        m_jt = re.match(r"^calculate\s+joule\s+thomson\s+drop\s+pressure\s+(.+?)\s+coefficient\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jt:
            return f"set {m_jt.group(3)} to thermo_joule_thomson_expansion({m_jt.group(1)}, {m_jt.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Thermodynamics domain does not define declarative blocks")
