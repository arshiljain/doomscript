import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AerospaceDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_ld = re.match(r"^calculate\s+lift\s+and\s+drag\s+for\s+density\s+(.+?)\s+velocity\s+(.+?)\s+area\s+(.+?)\s+cl\s+(.+?)\s+cd\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ld:
            return f"set {m_ld.group(6)} to aero_lift_drag({m_ld.group(1)}, {m_ld.group(2)}, {m_ld.group(3)}, {m_ld.group(4)}, {m_ld.group(5)})"

        m_mach = re.match(r"^calculate\s+mach\s+number\s+for\s+velocity\s+(.+?)(?:\s+at\s+temp\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mach:
            t = m_mach.group(2) or "288.15"
            return f"set {m_mach.group(3)} to aero_mach_number({m_mach.group(1)}, {t})"

        m_br = re.match(r"^calculate\s+breguet\s+range\s+for\s+ld\s+(.+?)\s+velocity\s+(.+?)\s+sfc\s+(.+?)\s+w0\s+(.+?)\s+w1\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_br:
            return f"set {m_br.group(6)} to aero_breguet_range({m_br.group(1)}, {m_br.group(2)}, {m_br.group(3)}, {m_br.group(4)}, {m_br.group(5)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Aerospace domain does not define declarative blocks")
