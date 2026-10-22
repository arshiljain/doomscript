import re
from typing import Optional
from doomscript.domains.base import DomainParser

class BiomechanicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_moment = re.match(r"^calculate\s+joint\s+moment\s+force\s+(.+?)\s+arm\s+(.+?)\s+angle\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_moment:
            return f"set {m_moment.group(4)} to biomech_joint_moment({m_moment.group(1)}, {m_moment.group(2)}, {m_moment.group(3)})"

        m_com = re.match(r"^calculate\s+center\s+of\s+mass\s+masses\s+(.+?)\s+positions\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_com:
            return f"set {m_com.group(3)} to biomech_center_of_mass({m_com.group(1)}, {m_com.group(2)})"

        m_impulse = re.match(r"^calculate\s+grf\s+impulse\s+forces\s+(.+?)\s+dt\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_impulse:
            return f"set {m_impulse.group(3)} to biomech_grf_impulse({m_impulse.group(1)}, {m_impulse.group(2)})"

        m_tendon = re.match(r"^calculate\s+muscle\s+tendon\s+force\s+muscle\s+(.+?)\s+pennation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tendon:
            return f"set {m_tendon.group(3)} to biomech_muscle_tendon_force({m_tendon.group(1)}, {m_tendon.group(2)})"

        m_hill = re.match(r"^calculate\s+hill\s+muscle\s+force\s+velocity\s+(.+?)\s+f0\s+(.+?)\s+param_a\s+(.+?)\s+param_b\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hill:
            return f"set {m_hill.group(5)} to biomech_hills_muscle_force_velocity({m_hill.group(1)}, {m_hill.group(2)}, {m_hill.group(3)}, {m_hill.group(4)})"

        m_moi = re.match(r"^calculate\s+segment\s+inertia\s+mass\s+(.+?)\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_moi:
            return f"set {m_moi.group(3)} to biomech_segment_moment_of_inertia_cylinder({m_moi.group(1)}, {m_moi.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Biomechanics domain does not define declarative blocks")
