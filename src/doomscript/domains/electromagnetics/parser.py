import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ElectromagneticsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate magnetic field wire current <i> distance <r> into <target>
        m_wire = re.match(r"^calculate\s+magnetic\s+field\s+wire\s+current\s+(.+?)\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wire:
            return f"set {m_wire.group(3)} to em_biot_savart_wire({m_wire.group(1)}, {m_wire.group(2)})"

        # calculate skin depth freq <f> conductivity <sigma> perm <ur> into <target>
        m_skin = re.match(r"^calculate\s+skin\s+depth\s+freq\s+(.+?)\s+conductivity\s+(.+?)\s+perm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_skin:
            return f"set {m_skin.group(4)} to em_skin_depth({m_skin.group(1)}, {m_skin.group(2)}, {m_skin.group(3)})"

        # calculate poynting vector efield <e> hfield <h> into <target>
        m_poy = re.match(r"^calculate\s+poynting\s+vector\s+efield\s+(.+?)\s+hfield\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_poy:
            return f"set {m_poy.group(3)} to em_poynting_vector_magnitude({m_poy.group(1)}, {m_poy.group(2)})"

        # calculate coax impedance inner <a> outer <b> eps <eps> into <target>
        m_coax = re.match(r"^calculate\s+coax\s+impedance\s+inner\s+(.+?)\s+outer\s+(.+?)\s+eps\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_coax:
            return f"set {m_coax.group(4)} to em_coaxial_characteristic_impedance({m_coax.group(1)}, {m_coax.group(2)}, {m_coax.group(3)})"

        # calculate wave attenuation freq <f> conductivity <sigma> eps <eps> perm <ur> into <target>
        m_wave = re.match(r"^calculate\s+wave\s+attenuation\s+freq\s+(.+?)\s+conductivity\s+(.+?)\s+eps\s+(.+?)\s+perm\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wave:
            return f"set {m_wave.group(5)} to em_plane_wave_attenuation({m_wave.group(1)}, {m_wave.group(2)}, {m_wave.group(3)}, {m_wave.group(4)})"

        # calculate faraday emf turns <n> flux <flux> time <dt> into <target>
        m_far = re.match(r"^calculate\s+faraday\s+emf\s+turns\s+(.+?)\s+flux\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_far:
            return f"set {m_far.group(4)} to em_faraday_induced_emf({m_far.group(1)}, {m_far.group(2)}, {m_far.group(3)})"

        # calculate vswr zl <zl> z0 <z0> into <target>
        m_vswr = re.match(r"^calculate\s+vswr\s+zl\s+(.+?)\s+z0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vswr:
            return f"set {m_vswr.group(3)} to em_vswr_reflection({m_vswr.group(1)}, {m_vswr.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Electromagnetics domain does not define declarative blocks")
