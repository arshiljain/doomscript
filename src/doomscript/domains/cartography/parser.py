import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CartographyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_hav = re.match(r"^calculate\s+haversine\s+distance\s+lat1\s+(.+?)\s+lon1\s+(.+?)\s+lat2\s+(.+?)\s+lon2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hav:
            return f"set {m_hav.group(5)} to carto_haversine_distance({m_hav.group(1)}, {m_hav.group(2)}, {m_hav.group(3)}, {m_hav.group(4)})"

        m_bear = re.match(r"^calculate\s+initial\s+bearing\s+lat1\s+(.+?)\s+lon1\s+(.+?)\s+lat2\s+(.+?)\s+lon2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bear:
            return f"set {m_bear.group(5)} to carto_initial_bearing({m_bear.group(1)}, {m_bear.group(2)}, {m_bear.group(3)}, {m_bear.group(4)})"

        m_merc = re.match(r"^calculate\s+mercator\s+projection\s+lat\s+(.+?)\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_merc:
            return f"set {m_merc.group(3)} to carto_mercator_projection({m_merc.group(1)}, {m_merc.group(2)})"

        m_utm = re.match(r"^calculate\s+utm\s+zone\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_utm:
            return f"set {m_utm.group(2)} to carto_utm_zone({m_utm.group(1)})"

        m_scale = re.match(r"^calculate\s+ground\s+distance\s+map_cm\s+(.+?)\s+scale\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_scale:
            return f"set {m_scale.group(3)} to carto_ground_distance({m_scale.group(1)}, {m_scale.group(2)})"

        m_tissot = re.match(r"^calculate\s+mercator\s+distortion\s+lat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tissot:
            return f"set {m_tissot.group(2)} to carto_tissot_indicatrix_distortion({m_tissot.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Cartography domain does not define declarative blocks")
