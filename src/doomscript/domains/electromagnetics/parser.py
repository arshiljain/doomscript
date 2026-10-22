import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ElectromagneticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_wire = re.match(r"^calculate\s+magnetic\s+field\s+wire\s+current\s+(.+?)\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wire:
            return f"set {m_wire.group(3)} to em_biot_savart_wire({m_wire.group(1)}, {m_wire.group(2)})"

        m_skin = re.match(r"^calculate\s+skin\s+depth\s+freq\s+(.+?)\s+conductivity\s+(.+?)\s+perm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_skin:
            return f"set {m_skin.group(4)} to em_skin_depth({m_skin.group(1)}, {m_skin.group(2)}, {m_skin.group(3)})"

        m_poynt = re.match(r"^calculate\s+poynting\s+vector\s+efield\s+(.+?)\s+hfield\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_poynt:
            return f"set {m_poynt.group(3)} to em_poynting_vector_magnitude({m_poynt.group(1)}, {m_poynt.group(2)})"

        m_coax = re.match(r"^calculate\s+coax\s+impedance\s+inner\s+(.+?)\s+outer\s+(.+?)\s+eps\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_coax:
            return f"set {m_coax.group(4)} to em_coaxial_characteristic_impedance({m_coax.group(1)}, {m_coax.group(2)}, {m_coax.group(3)})"

        m_att = re.match(r"^calculate\s+wave\s+attenuation\s+freq\s+(.+?)\s+conductivity\s+(.+?)\s+eps\s+(.+?)\s+perm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_att:
            return f"set {m_att.group(5)} to em_plane_wave_attenuation({m_att.group(1)}, {m_att.group(2)}, {m_att.group(3)}, {m_att.group(4)})"

        m_emf = re.match(r"^calculate\s+faraday\s+emf\s+turns\s+(.+?)\s+flux\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_emf:
            return f"set {m_emf.group(4)} to em_faraday_induced_emf({m_emf.group(1)}, {m_emf.group(2)}, {m_emf.group(3)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Electromagnetics domain does not define declarative blocks")
