import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ActuarialDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate gompertz mortality age <age> base <b> factor <c> into <target>
        m_gomp = re.match(r"^calculate\s+gompertz\s+mortality\s+age\s+(.+?)\s+base\s+(.+?)\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gomp:
            return f"set {m_gomp.group(4)} to actuarial_gompertz_mortality_rate({m_gomp.group(1)}, {m_gomp.group(2)}, {m_gomp.group(3)})"

        # calculate makeham mortality age <age> accident <a> base <b> factor <c> into <target>
        m_mak = re.match(r"^calculate\s+makeham\s+mortality\s+age\s+(.+?)\s+accident\s+(.+?)\s+base\s+(.+?)\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mak:
            return f"set {m_mak.group(5)} to actuarial_makeham_mortality_rate({m_mak.group(1)}, {m_mak.group(2)}, {m_mak.group(3)}, {m_mak.group(4)})"

        # calculate annuity present value payment <p> rate <r> years <n> into <target>
        m_ann = re.match(r"^calculate\s+annuity\s+present\s+value\s+payment\s+(.+?)\s+rate\s+(.+?)\s+years\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ann:
            return f"set {m_ann.group(4)} to actuarial_annuity_present_value({m_ann.group(1)}, {m_ann.group(2)}, {m_ann.group(3)})"

        # calculate term insurance premium benefit <b> mortality <q> rate <r> term <n> into <target>
        m_term = re.match(r"^calculate\s+term\s+insurance\s+premium\s+benefit\s+(.+?)\s+mortality\s+(.+?)\s+rate\s+(.+?)\s+term\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_term:
            return f"set {m_term.group(5)} to actuarial_term_insurance_premium({m_term.group(1)}, {m_term.group(2)}, {m_term.group(3)}, {m_term.group(4)})"

        # calculate loss reserve claims <c> severity <s> rate <r> into <target>
        m_res = re.match(r"^calculate\s+loss\s+reserve\s+claims\s+(.+?)\s+severity\s+(.+?)\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_res:
            return f"set {m_res.group(4)} to actuarial_loss_reserve({m_res.group(1)}, {m_res.group(2)}, {m_res.group(3)})"

        # calculate chain ladder losses <l> ratio <f> into <target>
        m_cl = re.match(r"^calculate\s+chain\s+ladder\s+losses\s+(.+?)\s+ratio\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cl:
            return f"set {m_cl.group(3)} to actuarial_chain_ladder_projection({m_cl.group(1)}, {m_cl.group(2)})"

        # calculate life expectancy age <age> into <target>
        m_le = re.match(r"^calculate\s+life\s+expectancy\s+age\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_le:
            return f"set {m_le.group(2)} to actuarial_curtate_life_expectancy({m_le.group(1)})"

        # calculate cramer lundberg ruin surplus <u> premium <c> frequency <lam> mean_claim <mu> into <target>
        m_ruin = re.match(r"^calculate\s+cramer\s+lundberg\s+ruin\s+surplus\s+(.+?)\s+premium\s+(.+?)\s+frequency\s+(.+?)\s+mean_claim\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ruin:
            return f"set {m_ruin.group(5)} to actuarial_cramer_lundberg_ruin({m_ruin.group(1)}, {m_ruin.group(2)}, {m_ruin.group(3)}, {m_ruin.group(4)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Actuarial domain does not define declarative blocks")
