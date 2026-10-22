import re
from typing import Optional
from doomscript.domains.base import DomainParser

class EcologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_sh = re.match(r"^calculate\s+shannon\s+diversity\s+for\s+abundances\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sh:
            return f"set {m_sh.group(2)} to ecology_shannon_diversity({m_sh.group(1)})"

        m_simp = re.match(r"^calculate\s+simpson\s+diversity\s+for\s+abundances\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_simp:
            return f"set {m_simp.group(2)} to ecology_simpson_diversity({m_simp.group(1)})"

        m_lv = re.match(r"^step\s+lotka\s+volterra\s+prey\s+(.+?)\s+pred\s+(.+?)\s+alpha\s+(.+?)\s+beta\s+(.+?)\s+gamma\s+(.+?)\s+delta\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lv:
            return f"set {m_lv.group(7)} to ecology_lotka_volterra_step({m_lv.group(1)}, {m_lv.group(2)}, {m_lv.group(3)}, {m_lv.group(4)}, {m_lv.group(5)}, {m_lv.group(6)})"

        m_log = re.match(r"^calculate\s+logistic\s+growth\s+for\s+n0\s+(.+?)\s+r\s+(.+?)\s+k\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_log:
            return f"set {m_log.group(5)} to ecology_logistic_growth({m_log.group(1)}, {m_log.group(2)}, {m_log.group(3)}, {m_log.group(4)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Ecology domain does not define declarative blocks")
