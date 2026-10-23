"""Materials Domain Parser: Translates natural materials science and solid mechanics expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class MaterialsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_ss = re.match(r"^calculate\s+engineering\s+stress\s+and\s+strain\s+for\s+force\s+(.+?)\s+area\s+(.+?)\s+delta\s+(.+?)\s+initial\s+length\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ss:
            return f"set {m_ss.group(5)} to materials_stress_strain({m_ss.group(1)}, {m_ss.group(2)}, {m_ss.group(3)}, {m_ss.group(4)})"

        m_mohr = re.match(r"^calculate\s+mohrs\s+circle\s+principal\s+stresses\s+for\s+sigma\s+x\s+(.+?)\s+sigma\s+y\s+(.+?)\s+tau\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mohr:
            return f"set {m_mohr.group(4)} to materials_mohrs_circle({m_mohr.group(1)}, {m_mohr.group(2)}, {m_mohr.group(3)})"

        m_therm = re.match(r"^calculate\s+thermal\s+expansion\s+for\s+length\s+(.+?)\s+coeff\s+(.+?)\s+delta\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_therm:
            return f"set {m_therm.group(4)} to materials_thermal_expansion({m_therm.group(1)}, {m_therm.group(2)}, {m_therm.group(3)})"

        m_k1 = re.match(r"^calculate\s+stress\s+intensity\s+for\s+stress\s+(.+?)\s+crack\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_k1:
            return f"set {m_k1.group(3)} to materials_stress_intensity({m_k1.group(1)}, {m_k1.group(2)})"

        m_rom = re.match(r"^calculate\s+composite\s+modulus\s+fiber\s+(.+?)\s+matrix\s+(.+?)\s+fraction\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rom:
            return f"set {m_rom.group(4)} to materials_rule_of_mixtures({m_rom.group(1)}, {m_rom.group(2)}, {m_rom.group(3)})"

        # Deepened syntax
        m_yield = re.match(r"^evaluate\s+yield\s+criteria\s+s1\s+(.+?)\s+s2\s+(.+?)\s+s3\s+(.+?)\s+sy\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_yield:
            return f"set {m_yield.group(5)} to materials_tresca_von_mises_yield({m_yield.group(1)}, {m_yield.group(2)}, {m_yield.group(3)}, {m_yield.group(4)})"

        m_ro = re.match(r"^calculate\s+ramberg\s+osgood\s+stress\s+(.+?)\s+modulus\s+(.+?)\s+alpha\s+(.+?)\s+sigma0\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ro:
            return f"set {m_ro.group(6)} to materials_ramberg_osgood_strain({m_ro.group(1)}, {m_ro.group(2)}, {m_ro.group(3)}, {m_ro.group(4)}, {m_ro.group(5)})"

        m_jc = re.match(r"^calculate\s+johnson\s+cook\s+strain\s+(.+?)\s+rate\s+(.+?)\s+temp\s+(.+?)\s+a\s+(.+?)\s+b\s+(.+?)\s+n\s+(.+?)\s+c\s+(.+?)\s+m\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jc:
            return f"set {m_jc.group(9)} to materials_johnson_cook_flow_stress({m_jc.group(1)}, {m_jc.group(2)}, {m_jc.group(3)}, {m_jc.group(4)}, {m_jc.group(5)}, {m_jc.group(6)}, {m_jc.group(7)}, {m_jc.group(8)})"

        m_dbtt = re.match(r"^calculate\s+dbtt\s+temps\s+(.+?)\s+energies\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dbtt:
            return f"set {m_dbtt.group(3)} to materials_charpy_dbtt_hyperbolic({m_dbtt.group(1)}, {m_dbtt.group(2)})"

        m_ht = re.match(r"^calculate\s+halpin\s+tsai\s+fiber\s+(.+?)\s+matrix\s+(.+?)\s+fraction\s+(.+?)\s+aspect\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ht:
            return f"set {m_ht.group(5)} to materials_halpin_tsai_short_fiber({m_ht.group(1)}, {m_ht.group(2)}, {m_ht.group(3)}, {m_ht.group(4)})"

        m_hb = re.match(r"^convert\s+hardness\s+hb\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hb:
            return f"set {m_hb.group(2)} to materials_brinell_hardness_conversion({m_hb.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Materials domain does not define declarative blocks")
