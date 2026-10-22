import re
from typing import Optional
from doomscript.domains.base import DomainParser

class HydrologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_rey = re.match(r"^calculate\s+reynolds\s+number\s+for\s+velocity\s+(.+?)\s+diameter\s+(.+?)(?:\s+viscosity\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rey:
            nu = m_rey.group(3) or "1.004e-6"
            return f"set {m_rey.group(4)} to hydro_reynolds_number({m_rey.group(1)}, {m_rey.group(2)}, {nu})"

        m_dw = re.match(r"^calculate\s+darcy\s+weisbach\s+head\s+loss\s+for\s+friction\s+(.+?)\s+length\s+(.+?)\s+diameter\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dw:
            return f"set {m_dw.group(5)} to hydro_darcy_weisbach_head_loss({m_dw.group(1)}, {m_dw.group(2)}, {m_dw.group(3)}, {m_dw.group(4)})"

        m_man = re.match(r"^calculate\s+manning\s+flow\s+for\s+roughness\s+(.+?)\s+area\s+(.+?)\s+radius\s+(.+?)\s+slope\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_man:
            return f"set {m_man.group(5)} to hydro_manning_flow({m_man.group(1)}, {m_man.group(2)}, {m_man.group(3)}, {m_man.group(4)})"

        m_run = re.match(r"^calculate\s+peak\s+runoff\s+for\s+coeff\s+(.+?)\s+intensity\s+(.+?)\s+area\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_run:
            return f"set {m_run.group(4)} to hydro_rational_peak_runoff({m_run.group(1)}, {m_run.group(2)}, {m_run.group(3)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Hydrology domain does not define declarative blocks")
