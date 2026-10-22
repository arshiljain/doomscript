import re
from typing import Optional
from doomscript.domains.base import DomainParser

class PharmacologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_rate = re.match(r"^calculate\s+elimination\s+rate\s+halflife\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rate:
            return f"set {m_rate.group(2)} to pharm_elimination_rate({m_rate.group(1)})"

        m_css = re.match(r"^calculate\s+steady\s+state\s+conc\s+dose\s+(.+?)\s+bioavailability\s+(.+?)\s+clearance\s+(.+?)\s+interval\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_css:
            return f"set {m_css.group(5)} to pharm_steady_state_conc({m_css.group(1)}, {m_css.group(2)}, {m_css.group(3)}, {m_css.group(4)})"

        m_vd = re.match(r"^calculate\s+volume\s+distribution\s+dose\s+(.+?)\s+c0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vd:
            return f"set {m_vd.group(3)} to pharm_volume_of_distribution({m_vd.group(1)}, {m_vd.group(2)})"

        m_hill = re.match(r"^calculate\s+hill\s+response\s+conc\s+(.+?)\s+emax\s+(.+?)\s+ec50\s+(.+?)\s+hill\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hill:
            return f"set {m_hill.group(5)} to pharm_hill_equation({m_hill.group(1)}, {m_hill.group(2)}, {m_hill.group(3)}, {m_hill.group(4)})"

        m_mm = re.match(r"^calculate\s+saturable\s+elimination\s+vmax\s+(.+?)\s+km\s+(.+?)\s+conc\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mm:
            return f"set {m_mm.group(4)} to pharm_michaelis_menten_elimination_rate({m_mm.group(1)}, {m_mm.group(2)}, {m_mm.group(3)})"

        m_ld = re.match(r"^calculate\s+loading\s+dose\s+vd\s+(.+?)\s+target\s+(.+?)\s+bio\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ld:
            return f"set {m_ld.group(4)} to pharm_loading_dose({m_ld.group(1)}, {m_ld.group(2)}, {m_ld.group(3)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Pharmacology domain does not define declarative blocks")
