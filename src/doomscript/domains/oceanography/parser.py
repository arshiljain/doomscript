"""Oceanography Domain Parser: Translates natural oceanographic and fluid dynamics expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class OceanographyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_dens = re.match(r"^calculate\s+seawater\s+density\s+temp\s+(.+?)\s+salinity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dens:
            return f"set {m_dens.group(3)} to ocean_seawater_density({m_dens.group(1)}, {m_dens.group(2)})"

        m_cor = re.match(r"^calculate\s+coriolis\s+parameter\s+lat(?:itude)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
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

        # Deepened syntax
        m_ekman = re.match(r"^calculate\s+ekman\s+depth\s+wind\s+(.+?)\s+lat(?:itude)?\s+(.+?)(?:\s+viscosity\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ekman:
            visc = m_ekman.group(3) if m_ekman.group(3) else "0.05"
            return f"set {m_ekman.group(4)} to ocean_ekman_depth({m_ekman.group(1)}, {m_ekman.group(2)}, {visc})"

        m_bv = re.match(r"^calculate\s+buoyancy\s+frequency\s+density\s+(.+?)\s+depth\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bv:
            return f"set {m_bv.group(3)} to ocean_brunt_vaisala_frequency({m_bv.group(1)}, {m_bv.group(2)})"

        m_sverdrup = re.match(r"^calculate\s+sverdrup\s+transport\s+curl\s+(.+?)\s+lat(?:itude)?\s+(.+?)(?:\s+width\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sverdrup:
            w = m_sverdrup.group(3) if m_sverdrup.group(3) else "5000.0"
            return f"set {m_sverdrup.group(4)} to ocean_sverdrup_transport({m_sverdrup.group(1)}, {m_sverdrup.group(2)}, {w})"

        m_sofar = re.match(r"^analyze\s+sound\s+channel\s+temp\s+(.+?)\s+salinity\s+(.+?)\s+depths\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sofar:
            return f"set {m_sofar.group(4)} to ocean_sound_channel_sofar({m_sofar.group(1)}, {m_sofar.group(2)}, {m_sofar.group(3)})"

        m_ts = re.match(r"^classify\s+water\s+mass\s+temp\s+(.+?)\s+salinity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ts:
            return f"set {m_ts.group(3)} to ocean_ts_diagram_analysis({m_ts.group(1)}, {m_ts.group(2)})"

        m_tide = re.match(r"^calculate\s+tidal\s+form\s+factor\s+m2\s+(.+?)\s+s2\s+(.+?)\s+k1\s+(.+?)\s+o1\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tide:
            return f"set {m_tide.group(5)} to ocean_tidal_form_factor({m_tide.group(1)}, {m_tide.group(2)}, {m_tide.group(3)}, {m_tide.group(4)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Oceanography domain does not define declarative blocks")
