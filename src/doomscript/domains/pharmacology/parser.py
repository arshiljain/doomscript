import re
from typing import Optional
from doomscript.domains.base import DomainParser

class PharmacologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate elimination rate halflife <t> into <target>
        m_ke = re.match(r"^calculate\s+elimination\s+rate\s+halflife\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ke:
            return f"set {m_ke.group(2)} to pharm_elimination_rate({m_ke.group(1)})"

        # calculate steady state conc dose <d> bioavailability <f> clearance <cl> interval <tau> into <target>
        m_css = re.match(r"^calculate\s+steady\s+state\s+conc\s+dose\s+(.+?)\s+bioavailability\s+(.+?)\s+clearance\s+(.+?)\s+interval\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_css:
            return f"set {m_css.group(5)} to pharm_steady_state_conc({m_css.group(1)}, {m_css.group(2)}, {m_css.group(3)}, {m_css.group(4)})"

        # calculate volume distribution dose <d> c0 <c0> into <target>
        m_vd = re.match(r"^calculate\s+volume\s+distribution\s+dose\s+(.+?)\s+c0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vd:
            return f"set {m_vd.group(3)} to pharm_volume_of_distribution({m_vd.group(1)}, {m_vd.group(2)})"

        # calculate hill response conc <c> emax <emax> ec50 <ec50> hill <n> into <target>
        m_hill = re.match(r"^calculate\s+hill\s+response\s+conc\s+(.+?)\s+emax\s+(.+?)\s+ec50\s+(.+?)\s+hill\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hill:
            return f"set {m_hill.group(5)} to pharm_hill_equation({m_hill.group(1)}, {m_hill.group(2)}, {m_hill.group(3)}, {m_hill.group(4)})"

        # calculate saturable elimination vmax <vmax> km <km> conc <c> into <target>
        m_sat = re.match(r"^calculate\s+saturable\s+elimination\s+vmax\s+(.+?)\s+km\s+(.+?)\s+conc\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sat:
            return f"set {m_sat.group(4)} to pharm_michaelis_menten_elimination_rate({m_sat.group(1)}, {m_sat.group(2)}, {m_sat.group(3)})"

        # calculate loading dose vd <vd> target <target_c> bio <f> into <target>
        m_ld = re.match(r"^calculate\s+loading\s+dose\s+vd\s+(.+?)\s+target\s+(.+?)\s+bio\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ld:
            return f"set {m_ld.group(4)} to pharm_loading_dose({m_ld.group(1)}, {m_ld.group(2)}, {m_ld.group(3)})"

        # calculate creatinine clearance age <age> weight <wt> scr <scr> into <target>
        m_cr = re.match(r"^calculate\s+creatinine\s+clearance\s+age\s+(.+?)\s+weight\s+(.+?)\s+scr\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cr:
            return f"set {m_cr.group(4)} to pharm_cockcroft_gault_crcl({m_cr.group(1)}, {m_cr.group(2)}, {m_cr.group(3)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Pharmacology domain does not define declarative blocks")
