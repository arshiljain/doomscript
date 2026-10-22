import re
from typing import Optional
from doomscript.domains.base import DomainParser

class MetallurgyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_hp = re.match(r"^calculate\s+hall\s+petch\s+strength\s+friction\s+(.+?)\s+locking\s+(.+?)\s+grain\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hp:
            return f"set {m_hp.group(4)} to metal_hall_petch_yield_strength({m_hp.group(1)}, {m_hp.group(2)}, {m_hp.group(3)})"

        m_hollo = re.match(r"^calculate\s+hollomon\s+true\s+stress\s+k\s+(.+?)\s+strain\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hollo:
            return f"set {m_hollo.group(4)} to metal_hollomon_true_stress({m_hollo.group(1)}, {m_hollo.group(2)}, {m_hollo.group(3)})"

        m_lever = re.match(r"^calculate\s+lever\s+rule\s+overall\s+(.+?)\s+alpha\s+(.+?)\s+beta\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lever:
            return f"set {m_lever.group(4)} to metal_lever_rule({m_lever.group(1)}, {m_lever.group(2)}, {m_lever.group(3)})"

        m_scheil = re.match(r"^calculate\s+scheil\s+composition\s+initial\s+(.+?)\s+partition\s+(.+?)\s+solid\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_scheil:
            return f"set {m_scheil.group(4)} to metal_scheil_solidification({m_scheil.group(1)}, {m_scheil.group(2)}, {m_scheil.group(3)})"

        m_jmak = re.match(r"^calculate\s+jmak\s+recrystallization\s+time\s+(.+?)\s+k\s+(.+?)\s+exponent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jmak:
            return f"set {m_jmak.group(4)} to metal_jmak_recrystallization({m_jmak.group(1)}, {m_jmak.group(2)}, {m_jmak.group(3)})"

        m_diff = re.match(r"^calculate\s+metal\s+diffusion\s+d0\s+(.+?)\s+energy\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_diff:
            return f"set {m_diff.group(4)} to metal_arrhenius_diffusion({m_diff.group(1)}, {m_diff.group(2)}, {m_diff.group(3)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Metallurgy domain does not define declarative blocks")
