import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ErgonomicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_niosh = re.match(r"^calculate\s+niosh\s+lifting\s+limit\s+load\s+(.+?)\s+horiz\s+(.+?)\s+vert\s+(.+?)\s+dist\s+(.+?)\s+angle\s+(.+?)\s+freq\s+(.+?)\s+coupling\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_niosh:
            return f"set {m_niosh.group(8)} to ergo_niosh_rwl({m_niosh.group(1)}, {m_niosh.group(2)}, {m_niosh.group(3)}, {m_niosh.group(4)}, {m_niosh.group(5)}, {m_niosh.group(6)}, {m_niosh.group(7)})"

        m_rula = re.match(r"^calculate\s+rula\s+score\s+upper\s+(.+?)\s+lower\s+(.+?)\s+wrist\s+(.+?)\s+neck\s+(.+?)\s+trunk\s+(.+?)\s+load\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rula:
            return f"set {m_rula.group(7)} to ergo_rula_score({m_rula.group(1)}, {m_rula.group(2)}, {m_rula.group(3)}, {m_rula.group(4)}, {m_rula.group(5)}, {m_rula.group(6)})"

        m_met = re.match(r"^calculate\s+metabolic\s+expenditure\s+weight\s+(.+?)\s+met\s+(.+?)\s+minutes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_met:
            return f"set {m_met.group(4)} to ergo_metabolic_expenditure({m_met.group(1)}, {m_met.group(2)}, {m_met.group(3)})"

        m_reba = re.match(r"^calculate\s+reba\s+score\s+trunk\s+(.+?)\s+neck\s+(.+?)\s+legs\s+(.+?)\s+uarm\s+(.+?)\s+larm\s+(.+?)\s+wrist\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_reba:
            return f"set {m_reba.group(7)} to ergo_reba_score({m_reba.group(1)}, {m_reba.group(2)}, {m_reba.group(3)}, {m_reba.group(4)}, {m_reba.group(5)}, {m_reba.group(6)})"

        m_si = re.match(r"^calculate\s+strain\s+index\s+intensity\s+(.+?)\s+duration\s+(.+?)\s+efforts\s+(.+?)\s+posture\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_si:
            return f"set {m_si.group(5)} to ergo_strain_index({m_si.group(1)}, {m_si.group(2)}, {m_si.group(3)}, {m_si.group(4)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Ergonomics domain does not define declarative blocks")
