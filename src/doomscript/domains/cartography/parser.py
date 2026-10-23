import re
from typing import Optional
from doomscript.domains.base import DomainParser

class CartographyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate haversine distance lat1 <lat1> lon1 <lon1> lat2 <lat2> lon2 <lon2> into <target>
        m_hav = re.match(r"^calculate\s+haversine\s+distance\s+lat1\s+(.+?)\s+lon1\s+(.+?)\s+lat2\s+(.+?)\s+lon2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hav:
            return f"set {m_hav.group(5)} to carto_haversine_distance({m_hav.group(1)}, {m_hav.group(2)}, {m_hav.group(3)}, {m_hav.group(4)})"

        # calculate initial bearing lat1 <lat1> lon1 <lon1> lat2 <lat2> lon2 <lon2> into <target>
        m_brg = re.match(r"^calculate\s+initial\s+bearing\s+lat1\s+(.+?)\s+lon1\s+(.+?)\s+lat2\s+(.+?)\s+lon2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_brg:
            return f"set {m_brg.group(5)} to carto_initial_bearing({m_brg.group(1)}, {m_brg.group(2)}, {m_brg.group(3)}, {m_brg.group(4)})"

        # calculate mercator projection lat <lat> lon <lon> into <target>
        m_merc = re.match(r"^calculate\s+mercator\s+projection\s+lat\s+(.+?)\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_merc:
            return f"set {m_merc.group(3)} to carto_mercator_projection({m_merc.group(1)}, {m_merc.group(2)})"

        # calculate utm zone lon <lon> into <target>
        m_utm = re.match(r"^calculate\s+utm\s+zone\s+lon\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_utm:
            return f"set {m_utm.group(2)} to carto_utm_zone({m_utm.group(1)})"

        # calculate ground distance map_cm <cm> scale <scale> into <target>
        m_grd = re.match(r"^calculate\s+ground\s+distance\s+map_cm\s+(.+?)\s+scale\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_grd:
            return f"set {m_grd.group(3)} to carto_ground_distance({m_grd.group(1)}, {m_grd.group(2)})"

        # calculate mercator distortion lat <lat> into <target>
        m_dist = re.match(r"^calculate\s+mercator\s+distortion\s+lat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dist:
            return f"set {m_dist.group(2)} to carto_tissot_indicatrix_distortion({m_dist.group(1)})"

        # calculate wgs84 ecef lat <lat> lon <lon> height <h> into <target>
        m_ecef = re.match(r"^calculate\s+wgs84\s+ecef\s+lat\s+(.+?)\s+lon\s+(.+?)\s+height\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ecef:
            return f"set {m_ecef.group(4)} to carto_wgs84_to_ecef({m_ecef.group(1)}, {m_ecef.group(2)}, {m_ecef.group(3)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Cartography domain does not define declarative blocks")
