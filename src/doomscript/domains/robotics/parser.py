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

        # plan rrt path from <start> to <goal> in bounds <bounds> [with obstacles <obs>] [step <step>] into <target>
        m_rrt = re.match(
            r"^plan\s+rrt\s+path\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:bounds\s+)?(.+?)(?:\s+with\s+obstacles\s+(.+?))?(?:\s+step\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rrt:
            start, goal, bounds = m_rrt.group(1).strip(), m_rrt.group(2).strip(), m_rrt.group(3).strip()
            obs = m_rrt.group(4).strip() if m_rrt.group(4) else "None"
            step = m_rrt.group(5).strip() if m_rrt.group(5) else "1.0"
            target = m_rrt.group(6).strip()
            return f"set {target} to robotics_rrt_plan({start}, {goal}, {bounds}, obstacles={obs}, step_size={step})"

        # plan rrt star path from <start> to <goal> in bounds <bounds> [with obstacles <obs>] [radius <r>] into <target>
        m_rrt_star = re.match(
            r"^plan\s+rrt\s+star\s+path\s+from\s+(.+?)\s+to\s+(.+?)\s+in\s+(?:bounds\s+)?(.+?)(?:\s+with\s+obstacles\s+(.+?))?(?:\s+radius\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rrt_star:
            start, goal, bounds = m_rrt_star.group(1).strip(), m_rrt_star.group(2).strip(), m_rrt_star.group(3).strip()
            obs = m_rrt_star.group(4).strip() if m_rrt_star.group(4) else "None"
            rad = m_rrt_star.group(5).strip() if m_rrt_star.group(5) else "2.5"
            target = m_rrt_star.group(6).strip()
            return f"set {target} to robotics_rrt_star_plan({start}, {goal}, {bounds}, obstacles={obs}, search_radius={rad})"

        # calculate apf force at <pos> for goal <goal> [with obstacles <obs>] into <target>
        m_apf = re.match(
            r"^calculate\s+apf\s+force\s+at\s+(.+?)\s+for\s+goal\s+(.+?)(?:\s+with\s+obstacles\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_apf:
            pos, goal = m_apf.group(1).strip(), m_apf.group(2).strip()
            obs = m_apf.group(3).strip() if m_apf.group(3) else "None"
            target = m_apf.group(4).strip()
            return f"set {target} to robotics_apf_forces({pos}, {goal}, obstacles={obs})"

        # calculate differential drive forward with left <wl> and right <wr> [radius <r>] [base <L>] into <target>
        m_dd = re.match(
            r"^calculate\s+differential\s+drive\s+forward\s+with\s+left\s+(.+?)\s+and\s+right\s+(.+?)(?:\s+radius\s+(.+?))?(?:\s+base\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dd:
            wl, wr = m_dd.group(1).strip(), m_dd.group(2).strip()
            r = m_dd.group(3).strip() if m_dd.group(3) else "0.05"
            base = m_dd.group(4).strip() if m_dd.group(4) else "0.2"
            target = m_dd.group(5).strip()
            return f"set {target} to robotics_diff_drive_forward({wl}, {wr}, wheel_radius={r}, wheel_base={base})"

        # integrate odometry for pose <pose> with v <v> and w <w> over dt <dt> into <target>
        m_odom = re.match(
            r"^integrate\s+odometry\s+for\s+pose\s+(.+?)\s+with\s+v\s+(.+?)\s+and\s+w\s+(.+?)\s+over\s+dt\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_odom:
            pose, v, w, dt, target = m_odom.group(1).strip(), m_odom.group(2).strip(), m_odom.group(3).strip(), m_odom.group(4).strip(), m_odom.group(5).strip()
            return f"set {target} to robotics_diff_drive_odometry({pose}, {v}, {w}, {dt})"

        # pure pursuit steer for pose <pose> along path <path> [lookahead <ld>] into <target>
        m_pp = re.match(
            r"^pure\s+pursuit\s+steer\s+for\s+pose\s+(.+?)\s+along\s+path\s+(.+?)(?:\s+lookahead\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pp:
            pose, path = m_pp.group(1).strip(), m_pp.group(2).strip()
            ld = m_pp.group(3).strip() if m_pp.group(3) else "1.0"
            target = m_pp.group(4).strip()
            return f"set {target} to robotics_pure_pursuit({pose}, {path}, lookahead={ld})"

        # solve stewart platform ik for translation <trans> and rotation <rot> into <target>
        m_sp = re.match(
            r"^solve\s+stewart\s+platform\s+ik\s+for\s+translation\s+(.+?)\s+and\s+rotation\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sp:
            trans, rot, target = m_sp.group(1).strip(), m_sp.group(2).strip(), m_sp.group(3).strip()
            return f"set {target} to robotics_stewart_platform_ik({trans}, {rot})"

        # plan trapezoidal profile for distance <d> with max velocity <v> and max acceleration <a> into <target>
        m_trap = re.match(
            r"^plan\s+trapezoidal\s+profile\s+for\s+distance\s+(.+?)\s+with\s+max\s+velocity\s+(.+?)\s+and\s+max\s+acceleration\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_trap:
            d, v, a, target = m_trap.group(1).strip(), m_trap.group(2).strip(), m_trap.group(3).strip(), m_trap.group(4).strip()
            return f"set {target} to robotics_trapezoidal_profile({d}, {v}, {a})"

        # calculate dubins path from <start> to <goal> with radius <r> into <target>
        m_dub = re.match(
            r"^calculate\s+dubins\s+path\s+from\s+(.+?)\s+to\s+(.+?)\s+with\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dub:
            st, gl, rad, target = m_dub.group(1).strip(), m_dub.group(2).strip(), m_dub.group(3).strip(), m_dub.group(4).strip()
            return f"set {target} to robotics_dubins_path({st}, {gl}, turning_radius={rad})"

        # update occupancy grid with pose <pose> and scan ranges <ranges> into <target>
        m_occ = re.match(
            r"^update\s+occupancy\s+grid\s+with\s+pose\s+(.+?)\s+and\s+scan\s+ranges\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_occ:
            pose, rngs, target = m_occ.group(1).strip(), m_occ.group(2).strip(), m_occ.group(3).strip()
            return f"set {target} to robotics_occupancy_grid_update({pose}, {rngs})"

        # plan rrt star 3d path from <start> to <goal> [with step <step>] into <target>
        m_rrt3 = re.match(
            r"^plan\s+rrt\s*star\s*3d\s+path\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+with\s+step\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rrt3:
            st, gl = m_rrt3.group(1).strip(), m_rrt3.group(2).strip()
            step = m_rrt3.group(3).strip() if m_rrt3.group(3) else "1.0"
            target = m_rrt3.group(4).strip()
            return f"set {target} to robotics_rrt_star_3d({st}, {gl}, step_size={step})"

        # compute / calculate dwa velocity for state <state> and goal <goal> [with speed <v>] into <target>
        m_dwa = re.match(
            r"^(?:calculate|compute)\s+dwa\s+velocity\s+for\s+state\s+(.+?)\s+and\s+goal\s+(.+?)(?:\s+with\s+speed\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dwa:
            st, gl = m_dwa.group(1).strip(), m_dwa.group(2).strip()
            spd = m_dwa.group(3).strip() if m_dwa.group(3) else "1.0"
            target = m_dwa.group(4).strip()
            return f"set {target} to robotics_dwa_velocity({st}, {gl}, max_speed={spd})"

        # calculate 6dof fk dh params <dh> joint angles <q> into <target>
        m_fk6 = re.match(
            r"^calculate\s+6dof\s+fk\s+dh\s+params\s+(.+?)\s+joint\s+angles\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fk6:
            dh, q, target = m_fk6.group(1).strip(), m_fk6.group(2).strip(), m_fk6.group(3).strip()
            return f"set {target} to robotics_6dof_fk({dh}, {q})"

        # solve 6dof ik dh params <dh> target position <target_pos> [initial angles <q0>] into <target>
        m_ik6 = re.match(
            r"^solve\s+6dof\s+ik\s+dh\s+params\s+(.+?)\s+target\s+position\s+(.+?)(?:\s+initial\s+angles\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ik6:
            dh, tgt, init_q, target = m_ik6.group(1).strip(), m_ik6.group(2).strip(), m_ik6.group(3), m_ik6.group(4).strip()
            init_arg = f", initial_q={init_q.strip()}" if init_q else ""
            return f"set {target} to robotics_6dof_ik({dh}, {tgt}{init_arg})"

        # plan state lattice path from <start> to <goal> [obstacles <obs>] [step <step>] into <target>
        m_lat = re.match(
            r"^plan\s+state\s+lattice\s+path\s+from\s+(.+?)\s+to\s+(.+?)(?:\s+obstacles\s+(.+?))?(?:\s+step\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lat:
            st, gl, obs, step, target = m_lat.group(1).strip(), m_lat.group(2).strip(), m_lat.group(3), m_lat.group(4), m_lat.group(5).strip()
            obs_arg = f", obstacles={obs.strip()}" if obs else ""
            step_arg = f", step_len={step.strip()}" if step else ""
            return f"set {target} to robotics_state_lattice_plan({st}, {gl}{obs_arg}{step_arg})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Robotics domain does not define declarative blocks")
