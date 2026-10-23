import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CombustionDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate equivalence ratio fuel <f> air <a> stoich <stoich> into <target>
        m_eq = re.match(r"^calculate\s+equivalence\s+ratio\s+fuel\s+(.+?)\s+air\s+(.+?)\s+stoich\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_eq:
            return f"set {m_eq.group(4)} to combust_equivalence_ratio({m_eq.group(1)}, {m_eq.group(2)}, {m_eq.group(3)})"

        # calculate arrhenius rate preexp <a> ea <ea> temp <t> into <target>
        m_arr = re.match(r"^calculate\s+arrhenius\s+rate\s+preexp\s+(.+?)\s+ea\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_arr:
            return f"set {m_arr.group(4)} to combust_arrhenius_rate({m_arr.group(1)}, {m_arr.group(2)}, {m_arr.group(3)})"

        # calculate heat release rate flow <m> lhv <lhv> eff <eff> into <target>
        m_hrr = re.match(r"^calculate\s+heat\s+release\s+rate\s+flow\s+(.+?)\s+lhv\s+(.+?)\s+eff\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hrr:
            return f"set {m_hrr.group(4)} to combust_heat_release_rate({m_hrr.group(1)}, {m_hrr.group(2)}, {m_hrr.group(3)})"

        # calculate adiabatic flame temp t0 <t0> lhv <lhv> cp <cp> afr <afr> into <target>
        m_aft = re.match(r"^calculate\s+adiabatic\s+flame\s+temp\s+t0\s+(.+?)\s+lhv\s+(.+?)\s+cp\s+(.+?)\s+afr\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_aft:
            return f"set {m_aft.group(5)} to combust_adiabatic_flame_temp({m_aft.group(1)}, {m_aft.group(2)}, {m_aft.group(3)}, {m_aft.group(4)})"

        # calculate mixture flammability fractions <y> limits <limits> into <target>
        m_flam = re.match(r"^calculate\s+mixture\s+flammability\s+fractions\s+(.+?)\s+limits\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_flam:
            return f"set {m_flam.group(3)} to combust_le_chatelier_flammability_limit({m_flam.group(1)}, {m_flam.group(2)})"

        # calculate thermal nox temp <t> oxygen <xo2> into <target>
        m_nox = re.match(r"^calculate\s+thermal\s+nox\s+temp\s+(.+?)\s+oxygen\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_nox:
            return f"set {m_nox.group(3)} to combust_zeldovich_nox_scaling({m_nox.group(1)}, {m_nox.group(2)})"

        # calculate wobbe index hhv <hhv> gravity <sg> into <target>
        m_wob = re.match(r"^calculate\s+wobbe\s+index\s+hhv\s+(.+?)\s+gravity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wob:
            return f"set {m_wob.group(3)} to combust_wobbe_index({m_wob.group(1)}, {m_wob.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Combustion domain does not define declarative blocks")
