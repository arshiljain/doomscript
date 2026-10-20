"""Physics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class PhysicsDomainParser(DomainParser):
    """Parses spoken-English physics, collision, and kinematics statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate kinetic energy with mass <m> and velocity <v> into <target>
        m_ke = re.match(
            r"^calculate\s+kinetic\s+energy\s+with\s+mass\s+(.+?)\s+and\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ke:
            m = m_ke.group(1).strip()
            v = m_ke.group(2).strip()
            target = m_ke.group(3).strip()
            return f"set {target} to physics_kinetic_energy({m}, {v})"

        # calculate trajectory with velocity <v> and angle <deg> [with gravity <g>] into <target>
        m_traj = re.match(
            r"^calculate\s+trajectory\s+with\s+velocity\s+(.+?)\s+and\s+angle\s+(.+?)(?:\s+with\s+gravity\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_traj:
            v = m_traj.group(1).strip()
            deg = m_traj.group(2).strip()
            g = m_traj.group(3).strip() if m_traj.group(3) else "9.81"
            target = m_traj.group(4).strip()
            return f"set {target} to physics_trajectory({v}, {deg}, {g})"

        # calculate ballistic range with velocity <v> and angle <deg> [with gravity <g>] into <target>
        m_range = re.match(
            r"^calculate\s+ballistic\s+range\s+with\s+velocity\s+(.+?)\s+and\s+angle\s+(.+?)(?:\s+with\s+gravity\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_range:
            v = m_range.group(1).strip()
            deg = m_range.group(2).strip()
            g = m_range.group(3).strip() if m_range.group(3) else "9.81"
            target = m_range.group(4).strip()
            return f"set {target} to physics_ballistic_range({v}, {deg}, {g})"

        # calculate projectile with drag for mass <m> and velocity <v> and angle <deg> and drag <c_d> into <target>
        m_drag = re.match(
            r"^calculate\s+projectile\s+with\s+drag\s+for\s+mass\s+(.+?)\s+and\s+velocity\s+(.+?)\s+and\s+angle\s+(.+?)\s+and\s+drag\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_drag:
            m = m_drag.group(1).strip()
            v = m_drag.group(2).strip()
            deg = m_drag.group(3).strip()
            cd = m_drag.group(4).strip()
            target = m_drag.group(5).strip()
            return f"set {target} to physics_projectile_drag({m}, {v}, {deg}, {cd})"

        # check collision between aabb <b1> and <b2> into <target>
        m_aabb = re.match(
            r"^check\s+collision\s+between\s+aabb\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_aabb:
            b1 = m_aabb.group(1).strip()
            b2 = m_aabb.group(2).strip()
            target = m_aabb.group(3).strip()
            return f"set {target} to physics_aabb_collision({b1}, {b2})"

        # check polygon collision between <p1> and <p2> using sat into <target>
        m_sat = re.match(
            r"^check\s+polygon\s+collision\s+between\s+(.+?)\s+and\s+(.+?)\s+using\s+sat\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sat:
            p1 = m_sat.group(1).strip()
            p2 = m_sat.group(2).strip()
            target = m_sat.group(3).strip()
            return f"set {target} to physics_sat_polygon_collision({p1}, {p2})"

        # simulate spring damper with mass <m> and k <k> and c <c> and x0 <x0> into <target>
        m_spring = re.match(
            r"^simulate\s+spring\s+damper\s+with\s+mass\s+(.+?)\s+and\s+k\s+(.+?)\s+and\s+c\s+(.+?)\s+and\s+x0\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_spring:
            m = m_spring.group(1).strip()
            k = m_spring.group(2).strip()
            c = m_spring.group(3).strip()
            x0 = m_spring.group(4).strip()
            target = m_spring.group(5).strip()
            return f"set {target} to physics_spring_damper({m}, {k}, {c}, {x0})"

        # orbital velocity for mass <m> at radius <r> into <target>
        m_orb = re.match(
            r"^orbital\s+velocity\s+for\s+mass\s+(.+?)\s+at\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_orb:
            m = m_orb.group(1).strip()
            r = m_orb.group(2).strip()
            target = m_orb.group(3).strip()
            return f"set {target} to physics_orbital_velocity({m}, {r})"

        # escape velocity for mass <m> at radius <r> into <target>
        m_esc = re.match(
            r"^escape\s+velocity\s+for\s+mass\s+(.+?)\s+at\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_esc:
            m = m_esc.group(1).strip()
            r = m_esc.group(2).strip()
            target = m_esc.group(3).strip()
            return f"set {target} to physics_escape_velocity({m}, {r})"

        # create pid controller with kp <kp> and ki <ki> and kd <kd> into <target>
        m_pid_new = re.match(
            r"^create\s+pid\s+controller\s+with\s+kp\s+(.+?)\s+and\s+ki\s+(.+?)\s+and\s+kd\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pid_new:
            kp = m_pid_new.group(1).strip()
            ki = m_pid_new.group(2).strip()
            kd = m_pid_new.group(3).strip()
            target = m_pid_new.group(4).strip()
            return f"set {target} to physics_pid_create({kp}, {ki}, {kd})"

        # update pid <pid> with setpoint <sp> and measurement <meas> and dt <dt> into <target>
        m_pid_up = re.match(
            r"^update\s+pid\s+(.+?)\s+with\s+setpoint\s+(.+?)\s+and\s+measurement\s+(.+?)(?:\s+and\s+dt\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pid_up:
            pid = m_pid_up.group(1).strip()
            sp = m_pid_up.group(2).strip()
            meas = m_pid_up.group(3).strip()
            dt = m_pid_up.group(4).strip() if m_pid_up.group(4) else "0.1"
            target = m_pid_up.group(5).strip()
            return f"set {target} to physics_pid_update({pid}, {sp}, {meas}, {dt})"

        # simulate cloth with rows <rows> cols <cols> [steps <steps>] into <target>
        m_cloth = re.match(
            r"^simulate\s+cloth\s+with\s+rows\s+(.+?)\s+cols\s+(.+?)(?:\s+steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cloth:
            rows, cols = m_cloth.group(1).strip(), m_cloth.group(2).strip()
            steps = m_cloth.group(3) if m_cloth.group(3) else "40"
            target = m_cloth.group(4).strip()
            return f"set {target} to physics_simulate_cloth({rows}, {cols}, {steps})"

        # simulate rigid body 3d with mass <m> inertia <ixx> <iyy> <izz> torque <t> [duration <dur>] into <target>
        m_rb = re.match(
            r"^simulate\s+rigid\s+body\s+3d\s+with\s+mass\s+(.+?)\s+inertia\s+(.+?)\s+(.+?)\s+(.+?)\s+torque\s+(.+?)(?:\s+duration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rb:
            m = m_rb.group(1).strip()
            ixx, iyy, izz = m_rb.group(2).strip(), m_rb.group(3).strip(), m_rb.group(4).strip()
            torque = m_rb.group(5).strip()
            dur = m_rb.group(6).strip() if m_rb.group(6) else "1.0"
            target = m_rb.group(7).strip()
            return f"set {target} to physics_rigid_body_3d({m}, {ixx}, {iyy}, {izz}, {torque}, duration={dur})"

        # simulate sph fluid with particles <n> [steps <steps>] into <target>
        m_sph = re.match(
            r"^simulate\s+sph\s+fluid\s+with\s+particles\s+(.+?)(?:\s+steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sph:
            n = m_sph.group(1).strip()
            steps = m_sph.group(2) if m_sph.group(2) else "20"
            target = m_sph.group(3).strip()
            return f"set {target} to physics_simulate_sph({n}, {steps})"

        # calculate biot savart field for current <i> and radius <r> at distance <z> into <target>
        m_bs = re.match(
            r"^calculate\s+biot\s+savart\s+field\s+for\s+current\s+(.+?)\s+and\s+radius\s+(.+?)\s+at\s+distance\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bs:
            cur, rad, z, target = m_bs.group(1).strip(), m_bs.group(2).strip(), m_bs.group(3).strip(), m_bs.group(4).strip()
            return f"set {target} to physics_biot_savart_loop({cur}, {rad}, {z})"

        # calculate lorentz force for charge <q> velocity <v> efield <e> bfield <b> into <target>
        m_lf = re.match(
            r"^calculate\s+lorentz\s+force\s+for\s+charge\s+(.+?)\s+velocity\s+(.+?)\s+efield\s+(.+?)\s+bfield\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lf:
            q, v, e, b, target = m_lf.group(1).strip(), m_lf.group(2).strip(), m_lf.group(3).strip(), m_lf.group(4).strip(), m_lf.group(5).strip()
            return f"set {target} to physics_lorentz_force({q}, {v}, {e}, {b})"

        # calculate carnot efficiency for thot <th> and tcold <tc> with heat <q> into <target>
        m_carnot = re.match(
            r"^calculate\s+carnot\s+efficiency\s+for\s+thot\s+(.+?)\s+and\s+tcold\s+(.+?)\s+with\s+heat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_carnot:
            th, tc, q, target = m_carnot.group(1).strip(), m_carnot.group(2).strip(), m_carnot.group(3).strip(), m_carnot.group(4).strip()
            return f"set {target} to physics_carnot_cycle({th}, {tc}, {q})"

        # calculate otto efficiency for compression <r> with heat <q> into <target>
        m_otto = re.match(
            r"^calculate\s+otto\s+efficiency\s+for\s+compression\s+(.+?)\s+with\s+heat\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_otto:
            r, q, target = m_otto.group(1).strip(), m_otto.group(2).strip(), m_otto.group(3).strip()
            return f"set {target} to physics_otto_cycle({r}, {q})"

        # calculate lorentz factor for velocity <v> into <target>
        m_lor = re.match(
            r"^calculate\s+lorentz\s+factor\s+for\s+velocity\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lor:
            v, target = m_lor.group(1).strip(), m_lor.group(2).strip()
            return f"set {target} to physics_lorentz_factor({v})"

        # simulate symplectic verlet with x <x0> and v <v0> [duration <dur>] into <target>
        m_symp = re.match(
            r"^simulate\s+symplectic\s+verlet\s+with\s+x\s+(.+?)\s+and\s+v\s+(.+?)(?:\s+duration\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_symp:
            x0, v0 = m_symp.group(1).strip(), m_symp.group(2).strip()
            dur = m_symp.group(3).strip() if m_symp.group(3) else "10.0"
            target = m_symp.group(4).strip()
            return f"set {target} to physics_symplectic_verlet(x0={x0}, v0={v0}, duration={dur})"

        # calculate brachistochrone from origin to x <x> and y <y> into <target>
        m_brach = re.match(
            r"^calculate\s+brachistochrone\s+from\s+origin\s+to\s+x\s+(.+?)\s+and\s+y\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_brach:
            x_end, y_end, target = m_brach.group(1).strip(), m_brach.group(2).strip(), m_brach.group(3).strip()
            return f"set {target} to physics_brachistochrone({x_end}, {y_end})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Physics domain does not define declarative blocks")
