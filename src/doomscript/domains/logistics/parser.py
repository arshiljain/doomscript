import re
from typing import Optional
from doomscript.domains.base import DomainParser

class LogisticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_eoq = re.match(r"^calculate\s+economic\s+order\s+quantity\s+for\s+demand\s+(.+?)\s+order\s+cost\s+(.+?)\s+holding\s+cost\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eoq:
            return f"set {m_eoq.group(4)} to logistics_eoq({m_eoq.group(1)}, {m_eoq.group(2)}, {m_eoq.group(3)})"

        m_rop = re.match(r"^calculate\s+reorder\s+point\s+for\s+lead\s+time\s+(.+?)\s+daily\s+demand\s+(.+?)(?:\s+safety\s+stock\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rop:
            ss = m_rop.group(3) or "0.0"
            return f"set {m_rop.group(4)} to logistics_reorder_point({m_rop.group(1)}, {m_rop.group(2)}, {ss})"

        m_ss = re.match(r"^calculate\s+safety\s+stock\s+for\s+z\s+(.+?)\s+std\s+demand\s+(.+?)\s+lead\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ss:
            return f"set {m_ss.group(4)} to logistics_safety_stock({m_ss.group(1)}, {m_ss.group(2)}, {m_ss.group(3)})"

        m_tsp = re.match(r"^solve\s+tsp\s+nearest\s+neighbor\s+for\s+matrix\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tsp:
            return f"set {m_tsp.group(2)} to logistics_tsp_nearest_neighbor({m_tsp.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Logistics domain does not define declarative blocks")
