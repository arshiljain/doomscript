import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CombustionDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_phi = re.match(r"^calculate\s+equivalence\s+ratio\s+fuel\s+(.+?)\s+air\s+(.+?)\s+stoich\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_phi:
            return f"set {m_phi.group(4)} to combust_equivalence_ratio({m_phi.group(1)}, {m_phi.group(2)}, {m_phi.group(3)})"

        m_arr = re.match(r"^calculate\s+arrhenius\s+rate\s+preexp\s+(.+?)\s+ea\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_arr:
            return f"set {m_arr.group(4)} to combust_arrhenius_rate({m_arr.group(1)}, {m_arr.group(2)}, {m_arr.group(3)})"

        m_hrr = re.match(r"^calculate\s+heat\s+release\s+rate\s+flow\s+(.+?)\s+lhv\s+(.+?)\s+eff\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hrr:
            return f"set {m_hrr.group(4)} to combust_heat_release_rate({m_hrr.group(1)}, {m_hrr.group(2)}, {m_hrr.group(3)})"

        m_flame = re.match(r"^calculate\s+adiabatic\s+flame\s+temp\s+t0\s+(.+?)\s+lhv\s+(.+?)\s+cp\s+(.+?)\s+afr\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_flame:
            return f"set {m_flame.group(5)} to combust_adiabatic_flame_temp({m_flame.group(1)}, {m_flame.group(2)}, {m_flame.group(3)}, {m_flame.group(4)})"

        m_le = re.match(r"^calculate\s+mixture\s+flammability\s+fractions\s+(.+?)\s+limits\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_le:
            return f"set {m_le.group(3)} to combust_le_chatelier_flammability_limit({m_le.group(1)}, {m_le.group(2)})"

        m_nox = re.match(r"^calculate\s+thermal\s+nox\s+temp\s+(.+?)\s+oxygen\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_nox:
            return f"set {m_nox.group(3)} to combust_zeldovich_nox_scaling({m_nox.group(1)}, {m_nox.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Combustion domain does not define declarative blocks")
