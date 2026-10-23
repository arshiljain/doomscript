import re
from typing import Optional
from doomscript.domains.base import DomainParser

class StructuralDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate beam max moment load <w> span <l> into <target>
        m_mom = re.match(r"^calculate\s+beam\s+max\s+moment\s+load\s+(.+?)\s+span\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mom:
            return f"set {m_mom.group(3)} to structural_beam_max_moment({m_mom.group(1)}, {m_mom.group(2)})"

        # calculate beam max deflection load <w> span <l> modulus <e> inertia <i> into <target>
        m_def = re.match(r"^calculate\s+beam\s+max\s+deflection\s+load\s+(.+?)\s+span\s+(.+?)\s+modulus\s+(.+?)\s+inertia\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_def:
            return f"set {m_def.group(5)} to structural_beam_max_deflection({m_def.group(1)}, {m_def.group(2)}, {m_def.group(3)}, {m_def.group(4)})"

        # calculate column buckling load modulus <e> inertia <i> length <l> factor <k> into <target>
        m_bkl = re.match(r"^calculate\s+column\s+buckling\s+load\s+modulus\s+(.+?)\s+inertia\s+(.+?)\s+length\s+(.+?)\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bkl:
            return f"set {m_bkl.group(5)} to structural_euler_buckling_load({m_bkl.group(1)}, {m_bkl.group(2)}, {m_bkl.group(3)}, {m_bkl.group(4)})"

        # calculate section modulus width <b> height <h> into <target>
        m_sec = re.match(r"^calculate\s+section\s+modulus\s+width\s+(.+?)\s+height\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sec:
            return f"set {m_sec.group(3)} to structural_section_modulus_rectangular({m_sec.group(1)}, {m_sec.group(2)})"

        # calculate mohr principal stresses sx <sx> sy <sy> txy <txy> into <target>
        m_mohr = re.match(r"^calculate\s+mohr\s+principal\s+stresses\s+sx\s+(.+?)\s+sy\s+(.+?)\s+txy\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mohr:
            return f"set {m_mohr.group(4)} to structural_mohr_circle_principal_stresses({m_mohr.group(1)}, {m_mohr.group(2)}, {m_mohr.group(3)})"

        # calculate slenderness ratio length <l> radius <r> into <target>
        m_sln = re.match(r"^calculate\s+slenderness\s+ratio\s+length\s+(.+?)\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sln:
            return f"set {m_sln.group(3)} to structural_slenderness_ratio({m_sln.group(1)}, {m_sln.group(2)})"

        # calculate von mises stress sx <sx> sy <sy> sz <sz> txy <txy> into <target>
        m_vm = re.match(r"^calculate\s+von\s+mises\s+stress\s+sx\s+(.+?)\s+sy\s+(.+?)\s+sz\s+(.+?)\s+txy\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vm:
            return f"set {m_vm.group(5)} to structural_von_mises_stress({m_vm.group(1)}, {m_vm.group(2)}, {m_vm.group(3)}, {m_vm.group(4)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Structural domain does not define declarative blocks")
