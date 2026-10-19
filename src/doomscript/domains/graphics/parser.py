"""Graphics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class GraphicsDomainParser(DomainParser):
    """Parses spoken-English 2D and 3D graphics statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # create framebuffer <w> by <h> into <target>
        m_fb = re.match(
            r"^create\s+framebuffer\s+(\d+)\s+by\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fb:
            w, h, target = m_fb.group(1), m_fb.group(2), m_fb.group(3).strip()
            return f"set {target} to graphics_create_framebuffer({w}, {h})"

        # draw line on <fb> from <x0>, <y0> to <x1>, <y1> with color <color>
        m_line = re.match(
            r"^draw\s+line\s+on\s+([A-Za-z_]\w*)\s+from\s+(.+?),\s*(.+?)\s+to\s+(.+?),\s*(.+?)\s+with\s+color\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_line:
            fb, x0, y0, x1, y1, color = (
                m_line.group(1).strip(),
                m_line.group(2).strip(),
                m_line.group(3).strip(),
                m_line.group(4).strip(),
                m_line.group(5).strip(),
                m_line.group(6).strip(),
            )
            return f"call graphics_draw_line({fb}, {x0}, {y0}, {x1}, {y1}, {color})"

        # draw circle on <fb> at <cx>, <cy> radius <r> with color <color>
        m_circ = re.match(
            r"^draw\s+circle\s+on\s+([A-Za-z_]\w*)\s+at\s+(.+?),\s*(.+?)\s+radius\s+(.+?)\s+with\s+color\s+(.+)$",
            s,
            re.IGNORECASE,
        )
        if m_circ:
            fb, cx, cy, r, color = (
                m_circ.group(1).strip(),
                m_circ.group(2).strip(),
                m_circ.group(3).strip(),
                m_circ.group(4).strip(),
                m_circ.group(5).strip(),
            )
            return f"call graphics_draw_circle({fb}, {cx}, {cy}, {r}, {color})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Graphics domain does not define declarative blocks")
