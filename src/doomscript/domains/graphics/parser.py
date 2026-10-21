"""Graphics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class GraphicsDomainParser(DomainParser):
    """Parses spoken-English 2D and 3D graphics statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create framebuffer <w> by <h> into <target>
        # OR create canvas width <w> height <h> into <target>
        m_fb = re.match(
            r"^create\s+(?:canvas|framebuffer)\s+(?:with\s+)?(?:width\s+)?(\d+)\s*(?:by|height|\*|x|\s+)\s*(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fb:
            w, h, target = m_fb.group(1), m_fb.group(2), m_fb.group(3).strip()
            return f"set {target} to graphics_create_framebuffer({w}, {h})"

        # draw line on <fb> from <x0>, <y0> to <x1>, <y1> [with color <color>]
        m_line = re.match(
            r"^draw\s+line\s+on\s+([A-Za-z_]\w*)\s+from\s+(.+?),\s*(.+?)\s+to\s+(.+?),\s*(.+?)(?:\s+with\s+color\s+(.+))?$",
            s,
            re.IGNORECASE,
        )
        if m_line:
            fb, x0, y0, x1, y1 = (
                m_line.group(1).strip(),
                m_line.group(2).strip(),
                m_line.group(3).strip(),
                m_line.group(4).strip(),
                m_line.group(5).strip(),
            )
            color = m_line.group(6).strip() if m_line.group(6) else "(255, 255, 255)"
            return f"graphics_draw_line({fb}, {x0}, {y0}, {x1}, {y1}, {color})"

        # draw circle on <fb> at <cx>, <cy> radius <r> [with color <color>]
        m_circ = re.match(
            r"^draw\s+circle\s+on\s+([A-Za-z_]\w*)\s+at\s+(.+?),\s*(.+?)\s+radius\s+(.+?)(?:\s+with\s+color\s+(.+))?$",
            s,
            re.IGNORECASE,
        )
        if m_circ:
            fb, cx, cy, r = (
                m_circ.group(1).strip(),
                m_circ.group(2).strip(),
                m_circ.group(3).strip(),
                m_circ.group(4).strip(),
            )
            color = m_circ.group(5).strip() if m_circ.group(5) else "(255, 255, 255)"
            return f"graphics_draw_circle({fb}, {cx}, {cy}, {r}, {color})"

        # rasterize antialiased line from <x0>, <y0> to <x1>, <y1> [with color <col>] into <target>
        m_wu = re.match(
            r"^rasterize\s+antialiased\s+line\s+from\s+(.+?),\s*(.+?)\s+to\s+(.+?),\s*(.+?)(?:\s+with\s+color\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_wu:
            x0, y0, x1, y1 = m_wu.group(1).strip(), m_wu.group(2).strip(), m_wu.group(3).strip(), m_wu.group(4).strip()
            col = m_wu.group(5).strip() if m_wu.group(5) else "(255, 255, 255)"
            target = m_wu.group(6).strip()
            return f"set {target} to graphics_draw_wu_line({x0}, {y0}, {x1}, {y1}, color={col})"

        # scanline fill polygon <verts> [with color <col>] into <target>
        m_poly = re.match(
            r"^scanline\s+fill\s+polygon\s+(.+?)(?:\s+with\s+color\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_poly:
            verts = m_poly.group(1).strip()
            col = m_poly.group(2).strip() if m_poly.group(2) else "(255, 255, 255)"
            target = m_poly.group(3).strip()
            return f"set {target} to graphics_scanline_fill_polygon({verts}, color={col})"

        # ray march sdf origin <ro> direction <rd> [steps <steps>] into <target>
        m_rm = re.match(
            r"^ray\s+march\s+sdf\s+origin\s+(.+?)\s+direction\s+(.+?)(?:\s+steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rm:
            ro, rd = m_rm.group(1).strip(), m_rm.group(2).strip()
            st = m_rm.group(3).strip() if m_rm.group(3) else "64"
            target = m_rm.group(4).strip()
            return f"set {target} to graphics_ray_march_sdf({ro}, {rd}, max_steps={st})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Graphics domain does not define declarative blocks")
