import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AerospaceDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_ld = re.match(r"^calculate\s+lift\s+and\s+drag\s+for\s+density\s+(.+?)\s+velocity\s+(.+?)\s+area\s+(.+?)\s+cl\s+(.+?)\s+cd\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ld:
            return f"set {m_ld.group(6)} to aero_lift_drag({m_ld.group(1)}, {m_ld.group(2)}, {m_ld.group(3)}, {m_ld.group(4)}, {m_ld.group(5)})"

        m_mach = re.match(r"^calculate\s+mach\s+number\s+for\s+velocity\s+(.+?)(?:\s+at\s+temp\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mach:
            t = m_mach.group(2) if m_mach.group(2) else "288.15"
            return f"set {m_mach.group(3)} to aero_mach_number({m_mach.group(1)}, {t})"

        m_rng = re.match(r"^calculate\s+breguet\s+range\s+for\s+ld\s+(.+?)\s+velocity\s+(.+?)\s+sfc\s+(.+?)\s+w0\s+(.+?)\s+w1\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rng:
            return f"set {m_rng.group(6)} to aero_breguet_range({m_rng.group(1)}, {m_rng.group(2)}, {m_rng.group(3)}, {m_rng.group(4)}, {m_rng.group(5)})"

        m_orb = re.match(r"^calculate\s+orbital\s+velocity\s+for\s+altitude\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_orb:
            return f"set {m_orb.group(2)} to aerospace_orbital_velocity({m_orb.group(1)})"

        m_hoh = re.match(r"^calculate\s+hohmann\s+transfer\s+r1\s+(.+?)\s+r2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hoh:
            return f"set {m_hoh.group(3)} to aerospace_hohmann_transfer({m_hoh.group(1)}, {m_hoh.group(2)})"

        m_kep = re.match(r"^calculate\s+kepler\s+orbit\s+periapsis\s+(.+?)\s+apoapsis\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_kep:
            return f"set {m_kep.group(3)} to aerospace_kepler_orbit({m_kep.group(1)}, {m_kep.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Aerospace domain does not define declarative blocks")
