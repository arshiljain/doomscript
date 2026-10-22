import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ControlDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_ss = re.match(r"^step\s+state\s+space\s+a\s+(.+?)\s+b\s+(.+?)\s+state\s+(.+?)\s+input\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_ss:
            return f"set {m_ss.group(5)} to control_state_space_step({m_ss.group(1)}, {m_ss.group(2)}, {m_ss.group(3)}, {m_ss.group(4)})"

        m_kalman = re.match(r"^step\s+kalman\s+filter\s+prior\s+(.+?)\s+cov\s+(.+?)\s+measurement\s+(.+?)\s+noise\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_kalman:
            return f"set {m_kalman.group(5)} to control_kalman_1d_step({m_kalman.group(1)}, {m_kalman.group(2)}, {m_kalman.group(3)}, {m_kalman.group(4)})"

        m_pid = re.match(r"^calculate\s+pid\s+step\s+for\s+error\s+(.+?)\s+dt\s+(.+?)\s+integral\s+(.+?)\s+prev_err\s+(.+?)\s+kp\s+(.+?)\s+ki\s+(.+?)\s+kd\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_pid:
            return f"set {m_pid.group(8)} to control_pid_step({m_pid.group(1)}, {m_pid.group(2)}, {m_pid.group(3)}, {m_pid.group(4)}, {m_pid.group(5)}, {m_pid.group(6)}, {m_pid.group(7)})"

        m_comp = re.match(r"^fuse\s+gyro\s+(.+?)\s+accel\s+(.+?)\s+prev\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_comp:
            return f"set {m_comp.group(4)} to control_complementary_filter({m_comp.group(1)}, {m_comp.group(2)}, {m_comp.group(3)})"

        m_routh = re.match(r"^check\s+stability\s+for\s+polynomial\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_routh:
            return f"set {m_routh.group(2)} to control_routh_hurwitz_stable({m_routh.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Control domain does not define declarative blocks")
