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

        # create obb at <center> with extents <extents> into <target>
        m_obb = re.match(
            r"^create\s+obb\s+at\s+(.+?)\s+with\s+extents\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_obb:
            center, extents, target = m_obb.group(1).strip(), m_obb.group(2).strip(), m_obb.group(3).strip()
            return f"set {target} to math3d_obb_create({center}, {extents})"

        # test obb collision between <obb1> and <obb2> into <target>
        m_obb_col = re.match(
            r"^test\s+obb\s+collision\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_obb_col:
            obb1, obb2, target = m_obb_col.group(1).strip(), m_obb_col.group(2).strip(), m_obb_col.group(3).strip()
            return f"set {target} to math3d_obb_test_collision({obb1}, {obb2})"

        # create frustum with fov <fov> and aspect <asp> and near <znear> and far <zfar> into <target>
        m_frust = re.match(
            r"^create\s+frustum\s+with\s+fov\s+(.+?)\s+and\s+aspect\s+(.+?)\s+and\s+near\s+(.+?)\s+and\s+far\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_frust:
            fov, asp, znear, zfar, target = m_frust.group(1).strip(), m_frust.group(2).strip(), m_frust.group(3).strip(), m_frust.group(4).strip(), m_frust.group(5).strip()
            return f"set {target} to math3d_frustum_create({fov}, {asp}, {znear}, {zfar})"

        # cull sphere at <center> with radius <r> against frustum <frustum> into <target>
        m_cull_sph = re.match(
            r"^cull\s+sphere\s+at\s+(.+?)\s+with\s+radius\s+(.+?)\s+against\s+frustum\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cull_sph:
            center, radius, frustum, target = m_cull_sph.group(1).strip(), m_cull_sph.group(2).strip(), m_cull_sph.group(3).strip(), m_cull_sph.group(4).strip()
            return f"set {target} to math3d_frustum_cull_sphere({frustum}, {center}, {radius})"

        # build bvh tree from triangles <tris> into <target>
        m_bvh = re.match(
            r"^build\s+bvh\s+tree\s+from\s+triangles\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bvh:
            tris, target = m_bvh.group(1).strip(), m_bvh.group(2).strip()
            return f"set {target} to math3d_bvh_build({tris})"

        # trace ray <origin> with direction <direction> in bvh <bvh> into <target>
        m_ray_bvh = re.match(
            r"^trace\s+ray\s+(.+?)\s+with\s+direction\s+(.+?)\s+in\s+bvh\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ray_bvh:
            origin, direction, bvh, target = m_ray_bvh.group(1).strip(), m_ray_bvh.group(2).strip(), m_ray_bvh.group(3).strip(), m_ray_bvh.group(4).strip()
            return f"set {target} to math3d_bvh_raycast({bvh}, {origin}, {direction})"

        # transform points with dual quaternion translation <trans> rotation <rot> points <pts> into <target>
        m_dq_tr = re.match(
            r"^transform\s+points\s+with\s+dual\s+quaternion\s+translation\s+(.+?)\s+rotation\s+(.+?)\s+points\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dq_tr:
            trans, rot, pts, target = m_dq_tr.group(1).strip(), m_dq_tr.group(2).strip(), m_dq_tr.group(3).strip(), m_dq_tr.group(4).strip()
            return f"set {target} to math3d_dual_quaternion_transform({trans}, {rot}, {pts})"

        # interpolate dual quaternions trans1 <t1> rot1 <r1> trans2 <t2> rot2 <r2> at <t> into <target>
        m_sclerp = re.match(
            r"^interpolate\s+dual\s+quaternions\s+trans1\s+(.+?)\s+rot1\s+(.+?)\s+trans2\s+(.+?)\s+rot2\s+(.+?)\s+at\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sclerp:
            t1, r1, t2, r2, t, target = m_sclerp.group(1).strip(), m_sclerp.group(2).strip(), m_sclerp.group(3).strip(), m_sclerp.group(4).strip(), m_sclerp.group(5).strip(), m_sclerp.group(6).strip()
            return f"set {target} to math3d_dual_quaternion_sclerp({t1}, {r1}, {t2}, {r2}, {t})"

        # test gjk collision between <shape1> and <shape2> into <target>
        m_gjk = re.match(
            r"^test\s+gjk\s+collision\s+between\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gjk:
            s1, s2, target = m_gjk.group(1).strip(), m_gjk.group(2).strip(), m_gjk.group(3).strip()
            return f"set {target} to math3d_gjk_intersection({s1}, {s2})"

        # query kdtree points <pts> for target <target_pt> into <target>
        m_kd = re.match(
            r"^query\s+kdtree\s+points\s+(.+?)\s+for\s+target\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kd:
            pts, tgt, target = m_kd.group(1).strip(), m_kd.group(2).strip(), m_kd.group(3).strip()
            return f"set {target} to math3d_kdtree_query({pts}, {tgt})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Math3D domain does not define declarative blocks")
