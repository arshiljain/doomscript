import re
from typing import Optional
from doomscript.domains.base import DomainParser

class StructuralDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_moment = re.match(r"^calculate\s+beam\s+max\s+moment\s+load\s+(.+?)\s+span\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_moment:
            return f"set {m_moment.group(3)} to structural_beam_max_moment({m_moment.group(1)}, {m_moment.group(2)})"

        m_def = re.match(r"^calculate\s+beam\s+max\s+deflection\s+load\s+(.+?)\s+span\s+(.+?)\s+modulus\s+(.+?)\s+inertia\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_def:
            return f"set {m_def.group(5)} to structural_beam_max_deflection({m_def.group(1)}, {m_def.group(2)}, {m_def.group(3)}, {m_def.group(4)})"

        m_buck = re.match(r"^calculate\s+column\s+buckling\s+load\s+modulus\s+(.+?)\s+inertia\s+(.+?)\s+length\s+(.+?)\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_buck:
            return f"set {m_buck.group(5)} to structural_euler_buckling_load({m_buck.group(1)}, {m_buck.group(2)}, {m_buck.group(3)}, {m_buck.group(4)})"

        m_mod = re.match(r"^calculate\s+section\s+modulus\s+width\s+(.+?)\s+height\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mod:
            return f"set {m_mod.group(3)} to structural_section_modulus_rectangular({m_mod.group(1)}, {m_mod.group(2)})"

        m_mohr = re.match(r"^calculate\s+mohr\s+principal\s+stresses\s+sx\s+(.+?)\s+sy\s+(.+?)\s+txy\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mohr:
            return f"set {m_mohr.group(4)} to structural_mohr_circle_principal_stresses({m_mohr.group(1)}, {m_mohr.group(2)}, {m_mohr.group(3)})"

        m_slender = re.match(r"^calculate\s+slenderness\s+ratio\s+length\s+(.+?)\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_slender:
            return f"set {m_slender.group(3)} to structural_slenderness_ratio({m_slender.group(1)}, {m_slender.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Structural domain does not define declarative blocks")
