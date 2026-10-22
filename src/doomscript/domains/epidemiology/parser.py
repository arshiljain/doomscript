import re
from typing import Optional
from doomscript.domains.base import DomainParser

class EpidemiologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_r0 = re.match(r"^calculate\s+reproduction\s+number\s+r0\s+for\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_r0:
            return f"set {m_r0.group(3)} to epi_r0({m_r0.group(1)}, {m_r0.group(2)})"

        m_hit = re.match(r"^calculate\s+herd\s+immunity\s+threshold\s+for\s+r0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hit:
            return f"set {m_hit.group(2)} to epi_herd_immunity_threshold({m_hit.group(1)})"

        m_sir = re.match(r"^step\s+sir\s+model\s+s\s+(.+?)\s+i\s+(.+?)\s+r\s+(.+?)\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sir:
            return f"set {m_sir.group(6)} to epi_sir_step({m_sir.group(1)}, {m_sir.group(2)}, {m_sir.group(3)}, {m_sir.group(4)}, {m_sir.group(5)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Epidemiology domain does not define declarative blocks")
