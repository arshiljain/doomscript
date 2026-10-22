import re
from typing import Optional
from doomscript.domains.base import DomainParser

class MicroeconDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_ped = re.match(r"^calculate\s+price\s+elasticity\s+for\s+q1\s+(.+?)\s+q2\s+(.+?)\s+p1\s+(.+?)\s+p2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ped:
            return f"set {m_ped.group(5)} to micro_price_elasticity({m_ped.group(1)}, {m_ped.group(2)}, {m_ped.group(3)}, {m_ped.group(4)})"

        m_sur = re.match(r"^calculate\s+surplus\s+for\s+p_max\s+(.+?)\s+p_min\s+(.+?)\s+price\s+(.+?)\s+quantity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sur:
            return f"set {m_sur.group(5)} to micro_surplus({m_sur.group(1)}, {m_sur.group(2)}, {m_sur.group(3)}, {m_sur.group(4)})"

        m_dwl = re.match(r"^calculate\s+deadweight\s+loss\s+for\s+tax\s+(.+?)\s+quantity\s+reduction\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dwl:
            return f"set {m_dwl.group(3)} to micro_deadweight_loss({m_dwl.group(1)}, {m_dwl.group(2)})"

        m_gini = re.match(r"^calculate\s+gini\s+coefficient\s+for\s+incomes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gini:
            return f"set {m_gini.group(2)} to micro_gini_coefficient({m_gini.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Microecon domain does not define declarative blocks")
