import re
from typing import Optional
from doomscript.domains.base import DomainParser

class HydrologyDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate manning flow for roughness <n> area <a> radius <r> slope <s> into <target>
        m_man = re.match(r"^calculate\s+manning\s+flow\s+(?:for\s+)?roughness\s+(.+?)\s+area\s+(.+?)\s+radius\s+(.+?)\s+slope\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_man:
            return f"set {m_man.group(5)} to hydrology_manning_flow({m_man.group(1)}, {m_man.group(2)}, {m_man.group(3)}, {m_man.group(4)})"

        # calculate peak runoff c <c> intensity <i> area <a> into <target>
        m_run = re.match(r"^calculate\s+peak\s+runoff\s+(?:for\s+)?(?:coeff|c)?\s*(.+?)\s+intensity\s+(.+?)\s+area\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_run:
            return f"set {m_run.group(4)} to hydrology_peak_runoff({m_run.group(1)}, {m_run.group(2)}, {m_run.group(3)})"

        # calculate darcy weisbach head loss friction <f> length <l> diameter <d> velocity <v> into <target>
        m_dw = re.match(r"^calculate\s+darcy\s+weisbach\s+(?:head\s+loss\s+)?(?:for\s+)?friction\s+(.+?)\s+length\s+(.+?)\s+diameter\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dw:
            return f"set {m_dw.group(5)} to hydrology_darcy_weisbach({m_dw.group(1)}, {m_dw.group(2)}, {m_dw.group(3)}, {m_dw.group(4)})"

        # calculate reynolds number velocity <v> diameter <d> [viscosity <nu>] into <target>
        m_rey = re.match(r"^calculate\s+reynolds\s+number\s+(?:for\s+)?velocity\s+(.+?)\s+diameter\s+(.+?)(?:\s+viscosity\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rey:
            if m_rey.group(3) is not None:
                return f"set {m_rey.group(4)} to hydrology_reynolds_number({m_rey.group(1)}, {m_rey.group(2)}, {m_rey.group(3)})"
            return f"set {m_rey.group(4)} to hydrology_reynolds_number({m_rey.group(1)}, {m_rey.group(2)})"

        # calculate hydraulic jump for depth <y> velocity <v> into <target>
        m_jump = re.match(r"^calculate\s+hydraulic\s+jump\s+(?:for\s+)?depth\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jump:
            return f"set {m_jump.group(3)} to hydrology_hydraulic_jump({m_jump.group(1)}, {m_jump.group(2)})"

        # calculate theis drawdown discharge <q> transmissivity <t> storativity <s> radius <r> time <time> into <target>
        m_th = re.match(r"^calculate\s+theis\s+drawdown\s+(?:for\s+)?discharge\s+(.+?)\s+transmissivity\s+(.+?)\s+storativity\s+(.+?)\s+radius\s+(.+?)\s+time\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_th:
            return f"set {m_th.group(6)} to hydrology_theis_drawdown({m_th.group(1)}, {m_th.group(2)}, {m_th.group(3)}, {m_th.group(4)}, {m_th.group(5)})"

        # calculate scs runoff curve cn <cn> precipitation <p> into <target>
        m_scs = re.match(r"^calculate\s+scs\s+runoff\s+curve\s+cn\s+(.+?)\s+precipitation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_scs:
            return f"set {m_scs.group(3)} to hydrology_scs_curve_number({m_scs.group(1)}, {m_scs.group(2)})"

        # calculate evapotranspiration rn <rn> temp <t> wind <w> humidity <rh> into <target>
        m_et = re.match(r"^calculate\s+evapotranspiration\s+rn\s+(.+?)\s+temp\s+(.+?)\s+wind\s+(.+?)\s+humidity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_et:
            return f"set {m_et.group(5)} to hydrology_fao_penman_monteith({m_et.group(1)}, {m_et.group(2)}, {m_et.group(3)}, {m_et.group(4)})"

        
        m_pf_alt = re.match(r"^calculate\s+pipe\s+friction\s+for\s+friction\s+factor\s+(.+?)\s+length\s+(.+?)\s+diameter\s+(.+?)\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pf_alt:
            return f"set {m_pf_alt.group(5)} to hydrology_darcy_weisbach_friction({m_pf_alt.group(1)}, {m_pf_alt.group(2)}, {m_pf_alt.group(3)}, {m_pf_alt.group(4)})"

        m_rey_alt = re.match(r"^calculate\s+reynolds\s+number\s+for\s+velocity\s+(.+?)\s+diameter\s+(.+?)\s+viscosity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rey_alt:
            return f"set {m_rey_alt.group(4)} to hydrology_reynolds_number({m_rey_alt.group(1)}, {m_rey_alt.group(2)}, {m_rey_alt.group(3)})"

        m_jump_alt = re.match(r"^calculate\s+hydraulic\s+jump\s+for\s+y1\s+(.+?)\s+froude1\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jump_alt:
            return f"set {m_jump_alt.group(3)} to hydrology_hydraulic_jump_conjugate({m_jump_alt.group(1)}, {m_jump_alt.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Hydrology domain does not define declarative blocks")
