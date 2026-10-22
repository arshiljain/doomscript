import re
from typing import Optional
from doomscript.domains.base import DomainParser

class GeophysicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_dist = re.match(r"^calculate\s+epicentral\s+distance\s+for\s+p\s+arrival\s+(.+?)\s+s\s+arrival\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dist:
            return f"set {m_dist.group(3)} to geo_epicentral_distance({m_dist.group(1)}, {m_dist.group(2)})"

        m_mag = re.match(r"^calculate\s+richter\s+magnitude\s+for\s+amplitude\s+(.+?)\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mag:
            return f"set {m_mag.group(3)} to geo_richter_magnitude({m_mag.group(1)}, {m_mag.group(2)})"

        m_mw = re.match(r"^calculate\s+moment\s+magnitude\s+area\s+(.+?)\s+slip\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mw:
            return f"set {m_mw.group(3)} to geo_moment_magnitude({m_mw.group(1)}, {m_mw.group(2)})"

        m_refr = re.match(r"^calculate\s+seismic\s+refraction\s+for\s+angle\s+(.+?)\s+v1\s+(.+?)\s+v2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_refr:
            return f"set {m_refr.group(4)} to geo_snell_refraction_angle({m_refr.group(1)}, {m_refr.group(2)}, {m_refr.group(3)})"

        m_boug = re.match(r"^calculate\s+bouguer\s+anomaly\s+for\s+observed\s+(.+?)\s+theoretical\s+(.+?)\s+elevation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_boug:
            return f"set {m_boug.group(4)} to geo_bouguer_anomaly({m_boug.group(1)}, {m_boug.group(2)}, {m_boug.group(3)})"

        m_res = re.match(r"^calculate\s+apparent\s+resistivity\s+spacing\s+(.+?)\s+resistance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_res:
            return f"set {m_res.group(3)} to geo_apparent_resistivity_wenner({m_res.group(1)}, {m_res.group(2)})"

        m_heat = re.match(r"^calculate\s+geothermal\s+heat\s+flow\s+for\s+conductivity\s+(.+?)\s+gradient\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_heat:
            return f"set {m_heat.group(3)} to geo_geothermal_heat_flow({m_heat.group(1)}, {m_heat.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Geophysics domain does not define declarative blocks")
