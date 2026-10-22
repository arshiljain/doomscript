import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AstrophysicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_rs = re.match(r"^calculate\s+schwarzschild\s+radius\s+mass\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rs:
            return f"set {m_rs.group(2)} to astro_schwarzschild_radius({m_rs.group(1)})"

        m_sb = re.match(r"^calculate\s+stellar\s+luminosity\s+radius\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sb:
            return f"set {m_sb.group(3)} to astro_stefan_boltzmann_luminosity({m_sb.group(1)}, {m_sb.group(2)})"

        m_edd = re.match(r"^calculate\s+eddington\s+luminosity\s+mass\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_edd:
            return f"set {m_edd.group(2)} to astro_eddington_luminosity({m_edd.group(1)})"

        m_hub = re.match(r"^calculate\s+hubble\s+velocity\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hub:
            return f"set {m_hub.group(2)} to astro_hubble_velocity({m_hub.group(1)})"

        m_jeans = re.match(r"^calculate\s+jeans\s+mass\s+temp\s+(.+?)\s+density\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jeans:
            return f"set {m_jeans.group(3)} to astro_jeans_mass({m_jeans.group(1)}, {m_jeans.group(2)})"

        m_crit = re.match(r"^calculate\s+critical\s+density\s+h0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_crit:
            return f"set {m_crit.group(2)} to astro_friedmann_critical_density({m_crit.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Astrophysics domain does not define declarative blocks")
