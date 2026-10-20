"""Math3D Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class Math3DDomainParser(DomainParser):
    """Parses spoken-English 3D mathematics, vector, and raytracing statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create vector3 [with] x <x> [and] y <y> [and] z <z> into <target>
        m_v3 = re.match(
            r"^create\s+vector3\s+(?:with\s+)?(?:x\s+)?([-\d.]+)\s*(?:,|and|\s+)?\s*(?:y\s+)?([-\d.]+)\s*(?:,|and|\s+)?\s*(?:z\s+)?([-\d.]+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_v3:
            x, y, z, target = m_v3.group(1).strip(), m_v3.group(2).strip(), m_v3.group(3).strip(), m_v3.group(4).strip()
            return f"set {target} to math3d_create_vec3({x}, {y}, {z})"

        # calculate cross product of <v1> and <v2> into <target>
        m_cross = re.match(
            r"^calculate\s+cross\s+product\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cross:
            v1, v2, target = m_cross.group(1).strip(), m_cross.group(2).strip(), m_cross.group(3).strip()
            return f"set {target} to math3d_cross_product({v1}, {v2})"

        # calculate dot product of <v1> and <v2> into <target>
        m_dot = re.match(
            r"^calculate\s+dot\s+product\s+of\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dot:
            v1, v2, target = m_dot.group(1).strip(), m_dot.group(2).strip(), m_dot.group(3).strip()
            return f"set {target} to math3d_dot_product({v1}, {v2})"

        # normalize vector <v> into <target>
        m_norm = re.match(
            r"^normalize\s+vector\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_norm:
            v, target = m_norm.group(1).strip(), m_norm.group(2).strip()
            return f"set {target} to math3d_normalize_vec({v})"

        # create look at matrix from <eye> to <target_pt> with up <up> into <target>
        m_look = re.match(
            r"^create\s+look\s+at\s+matrix\s+from\s+(.+?)\s+to\s+(.+?)\s+with\s+up\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_look:
            eye, tgt_pt, up, target = m_look.group(1).strip(), m_look.group(2).strip(), m_look.group(3).strip(), m_look.group(4).strip()
            return f"set {target} to math3d_look_at({eye}, {tgt_pt}, {up})"

        # create perspective matrix with fov <fov> and aspect <asp> and near <znear> and far <zfar> into <target>
        m_persp = re.match(
            r"^create\s+perspective\s+matrix\s+with\s+fov\s+(.+?)\s+and\s+aspect\s+(.+?)\s+and\s+near\s+(.+?)\s+and\s+far\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_persp:
            fov, asp, znear, zfar, target = m_persp.group(1).strip(), m_persp.group(2).strip(), m_persp.group(3).strip(), m_persp.group(4).strip(), m_persp.group(5).strip()
            return f"set {target} to math3d_perspective({fov}, {asp}, {znear}, {zfar})"

        # slerp quaternion <q1> and <q2> with t <t> into <target>
        m_slerp = re.match(
            r"^slerp\s+quaternion\s+(.+?)\s+and\s+(.+?)\s+with\s+t\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_slerp:
            q1, q2, t_val, target = m_slerp.group(1).strip(), m_slerp.group(2).strip(), m_slerp.group(3).strip(), m_slerp.group(4).strip()
            return f"set {target} to math3d_slerp({q1}, {q2}, {t_val})"

        # intersect ray <ray> with sphere at <center> and radius <r> into <target>
        m_sph = re.match(
            r"^intersect\s+ray\s+(.+?)\s+with\s+sphere\s+at\s+(.+?)\s+and\s+radius\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sph:
            ray, center, radius, target = m_sph.group(1).strip(), m_sph.group(2).strip(), m_sph.group(3).strip(), m_sph.group(4).strip()
            return f"set {target} to math3d_ray_sphere_intersect({ray}, {center}, {radius})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Math3D domain does not define declarative blocks")
