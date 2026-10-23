import re
from typing import Optional
from doomscript.domains.base import DomainParser

class MetallurgyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate hall petch strength friction <s0> locking <ky> grain <d> into <target>
        m_hp = re.match(r"^calculate\s+hall\s+petch\s+strength\s+friction\s+(.+?)\s+locking\s+(.+?)\s+grain\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hp:
            return f"set {m_hp.group(4)} to metal_hall_petch_yield_strength({m_hp.group(1)}, {m_hp.group(2)}, {m_hp.group(3)})"

        # calculate hollomon true stress k <k> strain <eps> n <n> into <target>
        m_hol = re.match(r"^calculate\s+hollomon\s+true\s+stress\s+k\s+(.+?)\s+strain\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hol:
            return f"set {m_hol.group(4)} to metal_hollomon_true_stress({m_hol.group(1)}, {m_hol.group(2)}, {m_hol.group(3)})"

        # calculate lever rule overall <c0> alpha <ca> beta <cb> into <target>
        m_lev = re.match(r"^calculate\s+lever\s+rule\s+overall\s+(.+?)\s+alpha\s+(.+?)\s+beta\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lev:
            return f"set {m_lev.group(4)} to metal_lever_rule({m_lev.group(1)}, {m_lev.group(2)}, {m_lev.group(3)})"

        # calculate scheil composition initial <c0> partition <k> solid <fs> into <target>
        m_sch = re.match(r"^calculate\s+scheil\s+composition\s+initial\s+(.+?)\s+partition\s+(.+?)\s+solid\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sch:
            return f"set {m_sch.group(4)} to metal_scheil_solidification({m_sch.group(1)}, {m_sch.group(2)}, {m_sch.group(3)})"

        # calculate jmak recrystallization time <t> k <k> exponent <n> into <target>
        m_jmak = re.match(r"^calculate\s+jmak\s+recrystallization\s+time\s+(.+?)\s+k\s+(.+?)\s+exponent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jmak:
            return f"set {m_jmak.group(4)} to metal_jmak_recrystallization({m_jmak.group(1)}, {m_jmak.group(2)}, {m_jmak.group(3)})"

        # calculate metal / arrhenius diffusion d0 <d0> energy/q <q> temp <t> into <target>
        m_diff = re.match(r"^calculate\s+(?:metal|arrhenius)\s+diffusion\s+d0\s+(.+?)\s+(?:energy|q)\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_diff:
            return f"set {m_diff.group(4)} to metal_arrhenius_diffusion({m_diff.group(1)}, {m_diff.group(2)}, {m_diff.group(3)})"

        # calculate martensite fraction ms <ms> temp <t> into <target>
        m_mar = re.match(r"^calculate\s+martensite\s+fraction\s+ms\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mar:
            return f"set {m_mar.group(3)} to metal_koistinen_marburger_martensite({m_mar.group(1)}, {m_mar.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Metallurgy domain does not define declarative blocks")
