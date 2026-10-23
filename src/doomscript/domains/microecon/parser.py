"""Microeconomics Domain Parser: Translates natural economic expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class MicroeconDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_ped = re.match(r"^calculate\s+price\s+elasticity\s+for\s+q1\s+(.+?)\s+q2\s+(.+?)\s+p1\s+(.+?)\s+p2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ped:
            return f"set {m_ped.group(5)} to microecon_price_elasticity({m_ped.group(1)}, {m_ped.group(2)}, {m_ped.group(3)}, {m_ped.group(4)})"

        m_surp = re.match(r"^calculate\s+surplus\s+for\s+p_max\s+(.+?)\s+p_min\s+(.+?)\s+price\s+(.+?)\s+quantity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_surp:
            return f"set {m_surp.group(5)} to microecon_surplus({m_surp.group(1)}, {m_surp.group(2)}, {m_surp.group(3)}, {m_surp.group(4)})"

        m_dwl = re.match(r"^calculate\s+deadweight\s+loss\s+for\s+tax\s+(.+?)\s+quantity\s+reduction\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dwl:
            return f"set {m_dwl.group(3)} to microecon_deadweight_loss({m_dwl.group(1)}, {m_dwl.group(2)})"

        m_gini = re.match(r"^calculate\s+gini\s+coefficient\s+for\s+incomes\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gini:
            return f"set {m_gini.group(2)} to microecon_gini({m_gini.group(1)})"

        m_cournot = re.match(r"^calculate\s+cournot\s+duopoly\s+demand\s+intercept\s+(.+?)\s+slope\s+(.+?)\s+marginal\s+cost\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cournot:
            return f"set {m_cournot.group(4)} to microecon_cournot_duopoly({m_cournot.group(1)}, {m_cournot.group(2)}, {m_cournot.group(3)})"

        m_hhi = re.match(r"^calculate\s+hhi\s+for\s+shares\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hhi:
            return f"set {m_hhi.group(2)} to microecon_hhi_concentration({m_hhi.group(1)})"

        # Deepened syntax
        m_cobb = re.match(r"^calculate\s+cobb\s+douglas\s+optimal\s+income\s+(.+?)\s+px\s+(.+?)\s+py\s+(.+?)\s+alpha\s+(.+?)\s+beta\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cobb:
            return f"set {m_cobb.group(6)} to microecon_cobb_douglas_optimal({m_cobb.group(1)}, {m_cobb.group(2)}, {m_cobb.group(3)}, {m_cobb.group(4)}, {m_cobb.group(5)})"

        m_bert = re.match(r"^calculate\s+bertrand\s+duopoly\s+demand\s+intercept\s+(.+?)\s+slope\s+(.+?)\s+mc1\s+(.+?)\s+mc2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bert:
            return f"set {m_bert.group(5)} to microecon_bertrand_duopoly({m_bert.group(1)}, {m_bert.group(2)}, {m_bert.group(3)}, {m_bert.group(4)})"

        m_mono = re.match(r"^calculate\s+monopoly\s+optimum\s+demand\s+intercept\s+(.+?)\s+slope\s+(.+?)\s+marginal\s+cost\s+(.+?)(?:\s+fixed\s+cost\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mono:
            fc = m_mono.group(4) if m_mono.group(4) else "0.0"
            return f"set {m_mono.group(5)} to microecon_monopoly_optimum({m_mono.group(1)}, {m_mono.group(2)}, {m_mono.group(3)}, {fc})"

        m_xped = re.match(r"^calculate\s+cross\s+elasticity\s+q1\s+(.+?)\s+q2\s+(.+?)\s+p1\s+(.+?)\s+p2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_xped:
            return f"set {m_xped.group(5)} to microecon_cross_price_elasticity({m_xped.group(1)}, {m_xped.group(2)}, {m_xped.group(3)}, {m_xped.group(4)})"

        m_nash = re.match(r"^find\s+nash\s+equilibrium\s+row\s+(.+?)\s+col\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_nash:
            return f"set {m_nash.group(3)} to microecon_nash_equilibrium_2x2({m_nash.group(1)}, {m_nash.group(2)})"

        m_ied = re.match(r"^calculate\s+income\s+elasticity\s+q1\s+(.+?)\s+q2\s+(.+?)\s+inc1\s+(.+?)\s+inc2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ied:
            return f"set {m_ied.group(5)} to microecon_income_elasticity({m_ied.group(1)}, {m_ied.group(2)}, {m_ied.group(3)}, {m_ied.group(4)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Microecon domain does not define declarative blocks")
