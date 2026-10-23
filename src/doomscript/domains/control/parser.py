"""Control Domain Parser: Translates natural control engineering expressions into DoomScript calls."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class ControlDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # Existing syntax
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

        # Deepened syntax
        m_bode = re.match(r"^calculate\s+bode\s+response\s+omega_n\s+(.+?)\s+zeta\s+(.+?)\s+frequencies\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_bode:
            return f"set {m_bode.group(4)} to control_bode_second_order({m_bode.group(1)}, {m_bode.group(2)}, {m_bode.group(3)})"

        m_tustin = re.match(r"^discretize\s+pole\s+(.+?)\s+sampling\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tustin:
            return f"set {m_tustin.group(3)} to control_tustin_bilinear_transform({m_tustin.group(1)}, {m_tustin.group(2)})"

        m_lqr = re.match(r"^calculate\s+lqr\s+cost\s+q\s+(.+?)\s+r\s+(.+?)\s+states\s+(.+?)\s+inputs\s+(.+?)(?:\s+dt\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_lqr:
            dt_v = m_lqr.group(5) if m_lqr.group(5) else "0.01"
            return f"set {m_lqr.group(6)} to control_lqr_cost_evaluation({m_lqr.group(1)}, {m_lqr.group(2)}, {m_lqr.group(3)}, {m_lqr.group(4)}, {dt_v})"

        m_step = re.match(r"^evaluate\s+step\s+response\s+times\s+(.+?)\s+values\s+(.+?)\s+target\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_step:
            return f"set {m_step.group(4)} to control_step_response_metrics({m_step.group(1)}, {m_step.group(2)}, {m_step.group(3)})"

        m_zn = re.match(r"^tune\s+ziegler\s+nichols\s+ku\s+(.+?)\s+tu\s+(.+?)(?:\s+type\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_zn:
            ct = m_zn.group(3) if m_zn.group(3) else '"PID"'
            return f"set {m_zn.group(4)} to control_ziegler_nichols_tuning({m_zn.group(1)}, {m_zn.group(2)}, {ct})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Control domain does not define declarative blocks")
