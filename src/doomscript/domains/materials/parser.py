import re
from typing import Optional
from doomscript.domains.base import DomainParser

class MaterialsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_ss = re.match(r"^calculate\s+engineering\s+stress\s+and\s+strain\s+for\s+force\s+(.+?)\s+area\s+(.+?)\s+delta\s+(.+?)\s+initial\s+length\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ss:
            return f"set {m_ss.group(5)} to materials_stress_strain({m_ss.group(1)}, {m_ss.group(2)}, {m_ss.group(3)}, {m_ss.group(4)})"

        m_mohr = re.match(r"^calculate\s+mohrs\s+circle\s+principal\s+stresses\s+for\s+sigma\s+x\s+(.+?)\s+sigma\s+y\s+(.+?)\s+tau\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mohr:
            return f"set {m_mohr.group(4)} to materials_mohrs_circle({m_mohr.group(1)}, {m_mohr.group(2)}, {m_mohr.group(3)})"

        m_th = re.match(r"^calculate\s+thermal\s+expansion\s+for\s+length\s+(.+?)\s+coeff\s+(.+?)\s+delta\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_th:
            return f"set {m_th.group(4)} to materials_thermal_expansion({m_th.group(1)}, {m_th.group(2)}, {m_th.group(3)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Materials domain does not define declarative blocks")
