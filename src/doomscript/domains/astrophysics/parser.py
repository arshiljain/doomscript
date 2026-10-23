import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AstrophysicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate schwarzschild radius mass <m> into <target>
        m_sch = re.match(r"^calculate\s+schwarzschild\s+radius\s+mass\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sch:
            return f"set {m_sch.group(2)} to astro_schwarzschild_radius({m_sch.group(1)})"

        # calculate stellar luminosity radius <r> temp <t> into <target>
        m_lum = re.match(r"^calculate\s+stellar\s+luminosity\s+radius\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lum:
            return f"set {m_lum.group(3)} to astro_stefan_boltzmann_luminosity({m_lum.group(1)}, {m_lum.group(2)})"

        # calculate eddington luminosity mass <m> into <target>
        m_edd = re.match(r"^calculate\s+eddington\s+luminosity\s+mass\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_edd:
            return f"set {m_edd.group(2)} to astro_eddington_luminosity({m_edd.group(1)})"

        # calculate hubble velocity distance <d> into <target>
        m_hub = re.match(r"^calculate\s+hubble\s+velocity\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hub:
            return f"set {m_hub.group(2)} to astro_hubble_velocity({m_hub.group(1)})"

        # calculate jeans mass temp <t> density <n> into <target>
        m_jean = re.match(r"^calculate\s+jeans\s+mass\s+temp\s+(.+?)\s+density\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jean:
            return f"set {m_jean.group(3)} to astro_jeans_mass({m_jean.group(1)}, {m_jean.group(2)})"

        # calculate critical density h0 <h0> into <target>
        m_crit = re.match(r"^calculate\s+critical\s+density\s+h0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_crit:
            return f"set {m_crit.group(2)} to astro_friedmann_critical_density({m_crit.group(1)})"

        # calculate hawking radiation mass <m> into <target>
        m_hawk = re.match(r"^calculate\s+hawking\s+radiation\s+mass\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hawk:
            return f"set {m_hawk.group(2)} to astro_hawking_radiation({m_hawk.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Astrophysics domain does not define declarative blocks")
