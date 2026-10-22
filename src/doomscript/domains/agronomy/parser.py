import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AgronomyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_water = re.match(r"^calculate\s+crop\s+water\s+requirement\s+et0\s+(.+?)\s+kc\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_water:
            return f"set {m_water.group(3)} to agronomy_crop_water_requirement({m_water.group(1)}, {m_water.group(2)})"

        m_gdd = re.match(r"^calculate\s+growing\s+degree\s+days\s+tmax\s+(.+?)\s+tmin\s+(.+?)\s+tbase\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gdd:
            return f"set {m_gdd.group(4)} to agronomy_growing_degree_days({m_gdd.group(1)}, {m_gdd.group(2)}, {m_gdd.group(3)})"

        m_fert = re.match(r"^calculate\s+fertilizer\s+rate\s+nutrient\s+(.+?)\s+percent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fert:
            return f"set {m_fert.group(3)} to agronomy_fertilizer_rate({m_fert.group(1)}, {m_fert.group(2)})"

        m_cec = re.match(r"^calculate\s+cation\s+exchange\s+ca\s+(.+?)\s+mg\s+(.+?)\s+k\s+(.+?)\s+na\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cec:
            return f"set {m_cec.group(5)} to agronomy_cation_exchange_capacity({m_cec.group(1)}, {m_cec.group(2)}, {m_cec.group(3)}, {m_cec.group(4)})"

        m_por = re.match(r"^calculate\s+soil\s+porosity\s+bulk\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_por:
            return f"set {m_por.group(2)} to agronomy_soil_porosity({m_por.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Agronomy domain does not define declarative blocks")
