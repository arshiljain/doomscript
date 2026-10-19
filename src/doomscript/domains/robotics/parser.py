"""Robotics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class RoboticsDomainParser(DomainParser):
    """Parses spoken-English robotics kinematics, trajectory, and Kalman filtering statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate forward kinematics for dh parameters <params> into <target>
        m_fk = re.match(
            r"^calculate\s+forward\s+kinematics\s+for\s+dh\s+parameters\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fk:
            params, target = m_fk.group(1).strip(), m_fk.group(2).strip()
            return f"set {target} to robotics_forward_kinematics({params})"

        # solve 2link inverse kinematics with link1 <l1> and link2 <l2> for target <x>, <y> into <target>
        m_ik = re.match(
            r"^solve\s+2link\s+inverse\s+kinematics\s+with\s+link1\s+(.+?)\s+and\s+link2\s+(.+?)\s+for\s+target\s+(.+?),\s*(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ik:
            l1, l2, x, y, target = m_ik.group(1).strip(), m_ik.group(2).strip(), m_ik.group(3).strip(), m_ik.group(4).strip(), m_ik.group(5).strip()
            return f"set {target} to robotics_inverse_kinematics_2link({l1}, {l2}, {x}, {y})"

        # create ekf tracker with x <x> and y <y> into <target>
        m_ekf = re.match(
            r"^create\s+ekf\s+tracker\s+with\s+x\s+(.+?)\s+and\s+y\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ekf:
            x, y, target = m_ekf.group(1).strip(), m_ekf.group(2).strip(), m_ekf.group(3).strip()
            return f"set {target} to robotics_create_ekf({x}, {y})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Robotics domain does not define declarative blocks")
