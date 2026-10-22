import re
from typing import Optional
from doomscript.domains.base import DomainParser

class PetroleumDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_darcy = re.match(r"^calculate\s+darcy\s+radial\s+flow\s+perm\s+(.+?)\s+pay\s+(.+?)\s+pres\s+(.+?)\s+pwell\s+(.+?)\s+visc\s+(.+?)\s+re\s+(.+?)\s+rw\s+(.+?)\s+skin\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_darcy:
            return f"set {m_darcy.group(9)} to petro_darcy_radial_flow({m_darcy.group(1)}, {m_darcy.group(2)}, {m_darcy.group(3)}, {m_darcy.group(4)}, {m_darcy.group(5)}, {m_darcy.group(6)}, {m_darcy.group(7)}, {m_darcy.group(8)})"

        m_archie = re.match(r"^calculate\s+archie\s+water\s+saturation\s+phi\s+(.+?)\s+rt\s+(.+?)\s+rw\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_archie:
            return f"set {m_archie.group(4)} to petro_archie_water_saturation({m_archie.group(1)}, {m_archie.group(2)}, {m_archie.group(3)})"

        m_api = re.match(r"^convert\s+specific\s+gravity\s+(.+?)\s+to\s+api\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_api:
            return f"set {m_api.group(2)} to petro_api_gravity({m_api.group(1)})"

        m_gor = re.match(r"^calculate\s+gas\s+oil\s+ratio\s+gas\s+(.+?)\s+oil\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gor:
            return f"set {m_gor.group(3)} to petro_solution_gor({m_gor.group(1)}, {m_gor.group(2)})"

        m_pb = re.match(r"^calculate\s+bubble\s+point\s+gor\s+(.+?)\s+gas_grav\s+(.+?)\s+api\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pb:
            return f"set {m_pb.group(5)} to petro_standing_bubble_point({m_pb.group(1)}, {m_pb.group(2)}, {m_pb.group(3)}, {m_pb.group(4)})"

        m_sutton = re.match(r"^calculate\s+pseudocritical\s+gas\s+grav\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sutton:
            return f"set {m_sutton.group(2)} to petro_sutton_pseudocritical({m_sutton.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Petroleum domain does not define declarative blocks")
