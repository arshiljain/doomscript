"""Thermodynamics Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ThermodynamicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate carnot efficiency hot <th> cold <tc> into <target>
        m_car = re.match(r"^calculate\s+carnot\s+efficiency\s+hot\s+(.+?)\s+cold\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_car:
            return f"set {m_car.group(3)} to thermo_carnot_efficiency({m_car.group(1)}, {m_car.group(2)})"

        # calculate entropy change mass <m> specific heat <c> t1 <t1> t2 <t2> into <target>
        m_ent = re.match(r"^calculate\s+entropy\s+change\s+mass\s+(.+?)\s+specific\s+heat\s+(.+?)\s+t1\s+(.+?)\s+t2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ent:
            return f"set {m_ent.group(5)} to thermo_entropy_change({m_ent.group(1)}, {m_ent.group(2)}, {m_ent.group(3)}, {m_ent.group(4)})"

                # calculate vapor pressure p1 <p1> t1 <t1> t2 <t2> delta h <dh> into <target>
        m_vap = re.match(r"^calculate\s+vapor\s+pressure\s+p1\s+(.+?)\s+t1\s+(.+?)\s+t2\s+(.+?)\s+(?:delta\s*h|deltah)\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vap:
            return f"set {m_vap.group(5)} to thermo_clausius_clapeyron({m_vap.group(1)}, {m_vap.group(2)}, {m_vap.group(3)}, {m_vap.group(4)})"

        # step polytropic p1 <p1> v1 <v1> v2 <v2> index <n> into <target>
        m_poly = re.match(r"^step\s+polytropic\s+p1\s+(.+?)\s+v1\s+(.+?)\s+v2\s+(.+?)\s+index\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_poly:
            return f"set {m_poly.group(5)} to thermo_polytropic_process({m_poly.group(1)}, {m_poly.group(2)}, {m_poly.group(3)}, {m_poly.group(4)})"

        # calculate rankine cycle boiler <h2> turbine <h3> condenser <h4> pump <h1> into <target>
        m_rnk = re.match(r"^calculate\s+rankine\s+cycle\s+boiler\s+(.+?)\s+turbine\s+(.+?)\s+condenser\s+(.+?)\s+pump\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rnk:
            return f"set {m_rnk.group(5)} to thermo_rankine_cycle_efficiency({m_rnk.group(1)}, {m_rnk.group(2)}, {m_rnk.group(3)}, {m_rnk.group(4)})"

        # calculate joule thomson drop pressure <dp> coefficient <mu> into <target>
        m_jt = re.match(r"^calculate\s+joule\s+thomson\s+drop\s+pressure\s+(.+?)\s+coefficient\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_jt:
            return f"set {m_jt.group(3)} to thermo_joule_thomson_expansion({m_jt.group(1)}, {m_jt.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Thermodynamics domain does not define declarative blocks")
