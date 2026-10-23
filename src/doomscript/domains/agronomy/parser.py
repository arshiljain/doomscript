"""Agronomy Domain Parser: Translates natural crop science and soil physics expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class AgronomyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_etc = re.match(r"^calculate\s+crop\s+water\s+requirement\s+et0\s+(.+?)\s+kc\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_etc:
            return f"set {m_etc.group(3)} to agronomy_crop_water_requirement({m_etc.group(1)}, {m_etc.group(2)})"

        m_gdd = re.match(r"^calculate\s+growing\s+degree\s+days\s+tmax\s+(.+?)\s+tmin\s+(.+?)(?:\s+tbase\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gdd:
            tb = m_gdd.group(3) if m_gdd.group(3) else "10.0"
            return f"set {m_gdd.group(4)} to agronomy_growing_degree_days({m_gdd.group(1)}, {m_gdd.group(2)}, {tb})"

        m_fert = re.match(r"^calculate\s+fertilizer\s+rate\s+nutrient\s+(.+?)\s+percent\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fert:
            return f"set {m_fert.group(3)} to agronomy_fertilizer_rate({m_fert.group(1)}, {m_fert.group(2)})"

        m_cec = re.match(r"^calculate\s+cation\s+exchange\s+ca\s+(.+?)\s+mg\s+(.+?)\s+k\s+(.+?)\s+na\s+(.+?)(?:\s+acid\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cec:
            acid = m_cec.group(5) if m_cec.group(5) else "0.0"
            return f"set {m_cec.group(6)} to agronomy_cation_exchange_capacity({m_cec.group(1)}, {m_cec.group(2)}, {m_cec.group(3)}, {m_cec.group(4)}, {acid})"

        m_por = re.match(r"^calculate\s+soil\s+porosity\s+bulk\s+(.+?)(?:\s+particle\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_por:
            ps = m_por.group(2) if m_por.group(2) else "2.65"
            return f"set {m_por.group(3)} to agronomy_soil_porosity({m_por.group(1)}, {ps})"

        # Deepened syntax
        m_usle = re.match(r"^calculate\s+usle\s+erosion\s+r\s+(.+?)\s+k\s+(.+?)\s+ls\s+(.+?)\s+c\s+(.+?)\s+p\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_usle:
            return f"set {m_usle.group(6)} to agronomy_universal_soil_loss_equation({m_usle.group(1)}, {m_usle.group(2)}, {m_usle.group(3)}, {m_usle.group(4)}, {m_usle.group(5)})"

        m_awc = re.match(r"^calculate\s+available\s+water\s+capacity\s+fc\s+(.+?)\s+pwp\s+(.+?)\s+depth\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_awc:
            return f"set {m_awc.group(4)} to agronomy_available_water_capacity({m_awc.group(1)}, {m_awc.group(2)}, {m_awc.group(3)})"

        m_n = re.match(r"^calculate\s+nitrogen\s+balance\s+om\s+(.+?)\s+demand\s+(.+?)(?:\s+bulk\s+(.+?)\s+depth\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_n:
            bd = m_n.group(3) if m_n.group(3) else "1.3"
            d = m_n.group(4) if m_n.group(4) else "30.0"
            return f"set {m_n.group(5)} to agronomy_nitrogen_mineralization_balance({m_n.group(1)}, {m_n.group(2)}, {bd}, {d})"

        m_irrig = re.match(r"^calculate\s+irrigation\s+schedule\s+deficit\s+(.+?)\s+efficiency\s+(.+?)\s+rate\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_irrig:
            return f"set {m_irrig.group(4)} to agronomy_irrigation_depth_schedule({m_irrig.group(1)}, {m_irrig.group(2)}, {m_irrig.group(3)})"

        m_lai = re.match(r"^calculate\s+leaf\s+area\s+index\s+foliage\s+(.+?)\s+ground\s+(.+?)(?:\s+k\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lai:
            k = m_lai.group(3) if m_lai.group(3) else "0.6"
            return f"set {m_lai.group(4)} to agronomy_leaf_area_index({m_lai.group(1)}, {m_lai.group(2)}, {k})"

        m_sar = re.match(r"^calculate\s+sar\s+na\s+(.+?)\s+ca\s+(.+?)\s+mg\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sar:
            return f"set {m_sar.group(4)} to agronomy_sodium_adsorption_ratio({m_sar.group(1)}, {m_sar.group(2)}, {m_sar.group(3)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Agronomy domain does not define declarative blocks")
