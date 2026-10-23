import re
from typing import Optional
from doomscript.domains.base import DomainParser

class GeophysicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate epicentral distance for p arrival <tp> s arrival <ts> into <target>
        m_epi = re.match(r"^calculate\s+epicentral\s+distance\s+(?:for\s+)?p\s+arrival\s+(.+?)\s+s\s+arrival\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_epi:
            return f"set {m_epi.group(3)} to geo_epicentral_distance({m_epi.group(1)}, {m_epi.group(2)})"

        # calculate richter magnitude amplitude <a> distance <d> into <target>
        m_rich = re.match(r"^calculate\s+richter\s+magnitude\s+(?:for\s+)?amplitude\s+(.+?)\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rich:
            return f"set {m_rich.group(3)} to geo_richter_magnitude({m_rich.group(1)}, {m_rich.group(2)})"

        # calculate moment magnitude area <a> slip <s> into <target>
        m_mw = re.match(r"^calculate\s+moment\s+magnitude\s+area\s+(.+?)\s+slip\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mw:
            return f"set {m_mw.group(3)} to geo_moment_magnitude({m_mw.group(1)}, {m_mw.group(2)})"

        # calculate seismic refraction angle <inc> v1 <v1> v2 <v2> into <target>
        m_snell = re.match(r"^calculate\s+seismic\s+refraction\s+(?:for\s+)?angle\s+(.+?)\s+v1\s+(.+?)\s+v2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_snell:
            return f"set {m_snell.group(4)} to geo_snell_refraction_angle({m_snell.group(1)}, {m_snell.group(2)}, {m_snell.group(3)})"

        # calculate bouguer anomaly obs <obs> theo <theo> elevation <h> density <rho> into <target>
        m_boug = re.match(r"^calculate\s+bouguer\s+anomaly\s+(?:for\s+)?(?:obs|observed)\s+(.+?)\s+(?:theo|theoretical)\s+(.+?)\s+elevation\s+(.+?)(?:\s+density\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_boug:
            if m_boug.group(4) is not None:
                return f"set {m_boug.group(5)} to geo_bouguer_anomaly({m_boug.group(1)}, {m_boug.group(2)}, {m_boug.group(3)}, {m_boug.group(4)})"
            return f"set {m_boug.group(5)} to geo_bouguer_anomaly({m_boug.group(1)}, {m_boug.group(2)}, {m_boug.group(3)})"

        # calculate apparent resistivity spacing <a> resistance <r> into <target>
        m_res = re.match(r"^calculate\s+apparent\s+resistivity\s+spacing\s+(.+?)\s+resistance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_res:
            return f"set {m_res.group(3)} to geo_apparent_resistivity_wenner({m_res.group(1)}, {m_res.group(2)})"

        # calculate geothermal heat flow conductivity <k> gradient <g> into <target>
        m_hf = re.match(r"^calculate\s+geothermal\s+heat\s+flow\s+(?:for\s+)?conductivity\s+(.+?)\s+gradient\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hf:
            return f"set {m_hf.group(3)} to geo_geothermal_heat_flow({m_hf.group(1)}, {m_hf.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Geophysics domain does not define declarative blocks")
