"""Biomechanics Domain Parser: Translates natural movement and kinesiology expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class BiomechanicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
        m_moment = re.match(r"^calculate\s+joint\s+moment\s+force\s+(.+?)\s+arm\s+(.+?)(?:\s+angle\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_moment:
            ang = m_moment.group(3) if m_moment.group(3) else "90.0"
            return f"set {m_moment.group(4)} to biomech_joint_moment({m_moment.group(1)}, {m_moment.group(2)}, {ang})"

        m_com = re.match(r"^calculate\s+center\s+of\s+mass\s+masses\s+(.+?)\s+positions\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_com:
            return f"set {m_com.group(3)} to biomech_center_of_mass({m_com.group(1)}, {m_com.group(2)})"

        m_grf = re.match(r"^calculate\s+grf\s+impulse\s+forces\s+(.+?)\s+dt\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_grf:
            return f"set {m_grf.group(3)} to biomech_grf_impulse({m_grf.group(1)}, {m_grf.group(2)})"

        m_tendon = re.match(r"^calculate\s+muscle\s+tendon\s+force\s+muscle\s+(.+?)\s+pennation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tendon:
            return f"set {m_tendon.group(3)} to biomech_muscle_tendon_force({m_tendon.group(1)}, {m_tendon.group(2)})"

        m_hill = re.match(r"^calculate\s+hill\s+muscle\s+force\s+velocity\s+(.+?)\s+f0\s+(.+?)\s+param_a\s+(.+?)\s+param_b\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hill:
            return f"set {m_hill.group(5)} to biomech_hills_muscle_force_velocity({m_hill.group(1)}, {m_hill.group(2)}, {m_hill.group(3)}, {m_hill.group(4)})"

        m_moi = re.match(r"^calculate\s+segment\s+inertia\s+mass\s+(.+?)\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_moi:
            return f"set {m_moi.group(3)} to biomech_segment_moment_of_inertia_cylinder({m_moi.group(1)}, {m_moi.group(2)})"

        # Deepened syntax
        m_power = re.match(r"^calculate\s+joint\s+power\s+moment\s+(.+?)\s+velocity\s+(.+?)(?:\s+dt\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_power:
            dt_v = m_power.group(3) if m_power.group(3) else "0.01"
            return f"set {m_power.group(4)} to biomech_muscle_mechanical_work_power({m_power.group(1)}, {m_power.group(2)}, {dt_v})"

        m_loading = re.match(r"^calculate\s+loading\s+rate\s+forces\s+(.+?)\s+rate\s+(.+?)\s+weight\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_loading:
            return f"set {m_loading.group(4)} to biomech_vertical_loading_rate({m_loading.group(1)}, {m_loading.group(2)}, {m_loading.group(3)})"

        m_penn = re.match(r"^calculate\s+pennation\s+thickness\s+(.+?)\s+length\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_penn:
            return f"set {m_penn.group(3)} to biomech_pennate_muscle_aponeurosis({m_penn.group(1)}, {m_penn.group(2)})"

        m_contact = re.match(r"^calculate\s+joint\s+contact\s+moment\s+(.+?)\s+arm\s+(.+?)\s+reaction\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_contact:
            return f"set {m_contact.group(4)} to biomech_joint_contact_force({m_contact.group(1)}, {m_contact.group(2)}, {m_contact.group(3)})"

        m_fr = re.match(r"^calculate\s+gait\s+froude\s+velocity\s+(.+?)\s+leg\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fr:
            return f"set {m_fr.group(3)} to biomech_gait_froude_number({m_fr.group(1)}, {m_fr.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Biomechanics domain does not define declarative blocks")
