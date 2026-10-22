import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ActuarialDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_gomp = re.match(r"^calculate\s+gompertz\s+mortality\s+age\s+(.+?)\s+base\s+(.+?)\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gomp:
            return f"set {m_gomp.group(4)} to actuarial_gompertz_mortality_rate({m_gomp.group(1)}, {m_gomp.group(2)}, {m_gomp.group(3)})"

        m_make = re.match(r"^calculate\s+makeham\s+mortality\s+age\s+(.+?)\s+accident\s+(.+?)\s+base\s+(.+?)\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_make:
            return f"set {m_make.group(5)} to actuarial_makeham_mortality_rate({m_make.group(1)}, {m_make.group(2)}, {m_make.group(3)}, {m_make.group(4)})"

        m_ann = re.match(r"^calculate\s+annuity\s+present\s+value\s+payment\s+(.+?)\s+rate\s+(.+?)\s+years\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ann:
            return f"set {m_ann.group(4)} to actuarial_annuity_present_value({m_ann.group(1)}, {m_ann.group(2)}, {m_ann.group(3)})"

        m_term = re.match(r"^calculate\s+term\s+insurance\s+premium\s+benefit\s+(.+?)\s+mortality\s+(.+?)\s+rate\s+(.+?)\s+term\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_term:
            return f"set {m_term.group(5)} to actuarial_term_insurance_premium({m_term.group(1)}, {m_term.group(2)}, {m_term.group(3)}, {m_term.group(4)})"

        m_loss = re.match(r"^calculate\s+loss\s+reserve\s+claims\s+(.+?)\s+severity\s+(.+?)\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_loss:
            return f"set {m_loss.group(4)} to actuarial_loss_reserve({m_loss.group(1)}, {m_loss.group(2)}, {m_loss.group(3)})"

        m_ladder = re.match(r"^calculate\s+chain\s+ladder\s+losses\s+(.+?)\s+ratio\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ladder:
            return f"set {m_ladder.group(3)} to actuarial_chain_ladder_projection({m_ladder.group(1)}, {m_ladder.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Actuarial domain does not define declarative blocks")
