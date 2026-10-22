import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CrystallographyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_bragg = re.match(r"^calculate\s+bragg\s+angle\s+wavelength\s+(.+?)\s+spacing\s+(.+?)\s+order\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bragg:
            return f"set {m_bragg.group(4)} to crystal_bragg_angle({m_bragg.group(1)}, {m_bragg.group(2)}, {m_bragg.group(3)})"

        m_spacing = re.match(r"^calculate\s+interplanar\s+spacing\s+lattice\s+(.+?)\s+h\s+(.+?)\s+k\s+(.+?)\s+l\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_spacing:
            return f"set {m_spacing.group(5)} to crystal_cubic_interplanar_spacing({m_spacing.group(1)}, {m_spacing.group(2)}, {m_spacing.group(3)}, {m_spacing.group(4)})"

        m_apf = re.match(r"^calculate\s+atomic\s+packing\s+factor\s+system\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_apf:
            return f"set {m_apf.group(2)} to crystal_atomic_packing_factor({m_apf.group(1)})"

        m_den = re.match(r"^calculate\s+crystal\s+density\s+atoms\s+(.+?)\s+weight\s+(.+?)\s+volume\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_den:
            return f"set {m_den.group(4)} to crystal_density({m_den.group(1)}, {m_den.group(2)}, {m_den.group(3)})"

        m_size = re.match(r"^calculate\s+crystallite\s+size\s+wavelength\s+(.+?)\s+fwhm\s+(.+?)\s+theta\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_size:
            return f"set {m_size.group(4)} to crystal_scherrer_crystallite_size({m_size.group(1)}, {m_size.group(2)}, {m_size.group(3)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Crystallography domain does not define declarative blocks")
