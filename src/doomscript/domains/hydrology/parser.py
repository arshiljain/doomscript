import re
from typing import Optional
from doomscript.domains.base import DomainParser

class HydrologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_mann = re.match(r"^calculate\s+manning\s+flow\s+for\s+roughness\s+(.+?)\s+area\s+(.+?)\s+radius\s+(.+?)\s+slope\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mann:
            return f"set {m_mann.group(5)} to hydrology_manning_flow({m_mann.group(1)}, {m_mann.group(2)}, {m_mann.group(3)}, {m_mann.group(4)})"

        m_run = re.match(r"^calculate\s+peak\s+runoff\s+for\s+coeff\s+(.+?)\s+intensity\s+(.+?)\s+area\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_run:
            return f"set {m_run.group(4)} to hydrology_peak_runoff({m_run.group(1)}, {m_run.group(2)}, {m_run.group(3)})"

        m_darcy = re.match(r"^calculate\s+darcy\s+weisbach\s+head\s+loss\s+for\s+friction\s+(.+?)\s+length\s+(.+?)\s+diameter\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_darcy:
            return f"set {m_darcy.group(5)} to hydrology_darcy_weisbach({m_darcy.group(1)}, {m_darcy.group(2)}, {m_darcy.group(3)}, {m_darcy.group(4)})"

        m_rey = re.match(r"^calculate\s+reynolds\s+number\s+for\s+velocity\s+(.+?)\s+diameter\s+(.+?)(?:\s+viscosity\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rey:
            visc = m_rey.group(3) if m_rey.group(3) else "0.000001"
            return f"set {m_rey.group(4)} to hydrology_reynolds_number({m_rey.group(1)}, {m_rey.group(2)}, {visc})"

        m_jump = re.match(r"^calculate\s+hydraulic\s+jump\s+for\s+depth\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jump:
            return f"set {m_jump.group(3)} to hydrology_hydraulic_jump({m_jump.group(1)}, {m_jump.group(2)})"

        m_theis = re.match(r"^calculate\s+theis\s+drawdown\s+for\s+discharge\s+(.+?)\s+transmissivity\s+(.+?)\s+storativity\s+(.+?)\s+radius\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_theis:
            return f"set {m_theis.group(6)} to hydrology_theis_drawdown({m_theis.group(1)}, {m_theis.group(2)}, {m_theis.group(3)}, {m_theis.group(4)}, {m_theis.group(5)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Hydrology domain does not define declarative blocks")
