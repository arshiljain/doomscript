import re
from typing import Optional
from doomscript.domains.base import DomainParser

class NuclearDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_decay = re.match(r"^calculate\s+radioactive\s+decay\s+initial\s+(.+?)\s+halflife\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_decay:
            return f"set {m_decay.group(4)} to nuclear_radioactive_decay({m_decay.group(1)}, {m_decay.group(2)}, {m_decay.group(3)})"

        m_lam = re.match(r"^calculate\s+decay\s+constant\s+halflife\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lam:
            return f"set {m_lam.group(2)} to nuclear_decay_constant({m_lam.group(1)})"

        m_q = re.match(r"^calculate\s+nuclear\s+q\s+value\s+mass_in\s+(.+?)\s+mass_out\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_q:
            return f"set {m_q.group(3)} to nuclear_reaction_q_value({m_q.group(1)}, {m_q.group(2)})"

        m_shield = re.match(r"^calculate\s+radiation\s+shielding\s+initial\s+(.+?)\s+attenuation\s+(.+?)\s+thickness\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_shield:
            return f"set {m_shield.group(4)} to nuclear_radiation_shielding({m_shield.group(1)}, {m_shield.group(2)}, {m_shield.group(3)})"

        m_four = re.match(r"^calculate\s+four\s+factor\s+eta\s+(.+?)\s+epsilon\s+(.+?)\s+p\s+(.+?)\s+f\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_four:
            return f"set {m_four.group(5)} to nuclear_four_factor_formula({m_four.group(1)}, {m_four.group(2)}, {m_four.group(3)}, {m_four.group(4)})"

        m_hvl = re.match(r"^calculate\s+half\s+value\s+layer\s+attenuation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hvl:
            return f"set {m_hvl.group(2)} to nuclear_half_value_layer({m_hvl.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Nuclear domain does not define declarative blocks")
