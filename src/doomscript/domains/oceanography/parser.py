import re
from typing import Optional
from doomscript.domains.base import DomainParser

class OceanographyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_dens = re.match(r"^calculate\s+seawater\s+density\s+temp\s+(.+?)\s+salinity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dens:
            return f"set {m_dens.group(3)} to ocean_seawater_density({m_dens.group(1)}, {m_dens.group(2)})"

        m_cor = re.match(r"^calculate\s+coriolis\s+parameter\s+lat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cor:
            return f"set {m_cor.group(2)} to ocean_coriolis_parameter({m_cor.group(1)})"

        m_wave = re.match(r"^calculate\s+ocean\s+wave\s+speed\s+wavelength\s+(.+?)\s+depth\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_wave:
            return f"set {m_wave.group(3)} to ocean_gravity_wave_speed({m_wave.group(1)}, {m_wave.group(2)})"

        m_press = re.match(r"^calculate\s+depth\s+pressure\s+depth\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_press:
            return f"set {m_press.group(2)} to ocean_hydrostatic_pressure({m_press.group(1)})"

        m_snd = re.match(r"^calculate\s+seawater\s+sound\s+speed\s+temp\s+(.+?)\s+salinity\s+(.+?)\s+depth\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_snd:
            return f"set {m_snd.group(4)} to ocean_sound_speed_mackenzie({m_snd.group(1)}, {m_snd.group(2)}, {m_snd.group(3)})"

        m_stress = re.match(r"^calculate\s+wind\s+stress\s+speed\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_stress:
            return f"set {m_stress.group(2)} to ocean_wind_stress({m_stress.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Oceanography domain does not define declarative blocks")
