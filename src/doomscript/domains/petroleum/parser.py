import re
from typing import Optional
from doomscript.domains.base import DomainParser

class PetroleumDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate darcy radial flow perm <k> pay <h> pres <pr> pwell <pw> visc <mu> re <re> rw <rw> skin <s> into <target>
        m_darcy = re.match(r"^calculate\s+darcy\s+radial\s+flow\s+perm\s+(.+?)\s+pay\s+(.+?)\s+pres\s+(.+?)\s+pwell\s+(.+?)\s+visc\s+(.+?)\s+re\s+(.+?)\s+rw\s+(.+?)\s+skin\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_darcy:
            return f"set {m_darcy.group(9)} to petro_darcy_radial_flow({m_darcy.group(1)}, {m_darcy.group(2)}, {m_darcy.group(3)}, {m_darcy.group(4)}, {m_darcy.group(5)}, {m_darcy.group(6)}, {m_darcy.group(7)}, {m_darcy.group(8)})"

        # calculate archie water saturation phi <phi> rt <rt> rw <rw> into <target>
        m_arc = re.match(r"^calculate\s+archie\s+water\s+saturation\s+phi\s+(.+?)\s+rt\s+(.+?)\s+rw\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_arc:
            return f"set {m_arc.group(4)} to petro_archie_water_saturation({m_arc.group(1)}, {m_arc.group(2)}, {m_arc.group(3)})"

        # convert specific gravity <sg> to api into <target>
        m_api = re.match(r"^convert\s+specific\s+gravity\s+(.+?)\s+to\s+api\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_api:
            return f"set {m_api.group(2)} to petro_api_gravity({m_api.group(1)})"

        # calculate gas oil ratio gas <qg> oil <qo> into <target>
        m_gor = re.match(r"^calculate\s+gas\s+oil\s+ratio\s+gas\s+(.+?)\s+oil\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gor:
            return f"set {m_gor.group(3)} to petro_solution_gor({m_gor.group(1)}, {m_gor.group(2)})"

        # calculate bubble point gor <rs> gas_grav <gg> api <api> temp <t> into <target>
        m_bp = re.match(r"^calculate\s+bubble\s+point\s+gor\s+(.+?)\s+gas_grav\s+(.+?)\s+api\s+(.+?)\s+temp\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bp:
            return f"set {m_bp.group(5)} to petro_standing_bubble_point({m_bp.group(1)}, {m_bp.group(2)}, {m_bp.group(3)}, {m_bp.group(4)})"

        # calculate pseudocritical gas grav <sg> into <target>
        m_pc = re.match(r"^calculate\s+pseudocritical\s+gas\s+grav\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pc:
            return f"set {m_pc.group(2)} to petro_sutton_pseudocritical({m_pc.group(1)})"

        # forecast arps decline rate <qi> nominal <d> time <t> b_factor <b> into <target>
        m_arps = re.match(r"^forecast\s+arps\s+decline\s+rate\s+(.+?)\s+nominal\s+(.+?)\s+time\s+(.+?)\s+b_factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_arps:
            return f"set {m_arps.group(5)} to petro_arps_decline({m_arps.group(1)}, {m_arps.group(2)}, {m_arps.group(3)}, {m_arps.group(4)})"

        # calculate vogel ipr qmax <qm> pres <pr> pwf <pwf> into <target>
        m_vogel = re.match(r"^calculate\s+vogel\s+ipr\s+qmax\s+(.+?)\s+pres\s+(.+?)\s+pwf\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vogel:
            return f"set {m_vogel.group(4)} to petro_vogel_ipr({m_vogel.group(1)}, {m_vogel.group(2)}, {m_vogel.group(3)})"

        # calculate gas z factor ppr <ppr> tpr <tpr> into <target>
        m_z = re.match(r"^calculate\s+gas\s+z\s+factor\s+ppr\s+(.+?)\s+tpr\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_z:
            return f"set {m_z.group(3)} to petro_dranchuk_z_factor({m_z.group(1)}, {m_z.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Petroleum domain does not define declarative blocks")
