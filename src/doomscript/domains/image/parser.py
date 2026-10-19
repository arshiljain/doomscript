"""Independent Domain Parser for Image & Vision domain."""

import re
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainParser
from doomscript.domains.image.spec import (
    ImageOpenSpec,
    ImageCreateSpec,
    ImageResizeSpec,
    ImageCropSpec,
    ImageRotateSpec,
    ImageFilterSpec,
    ImageSaveSpec,
)


class ImageDomainParser(DomainParser):
    """Independent parser for Image and Vision syntax."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # dimensions of [image] <img_var> into <target>
        m_dim = re.match(
            r"^dimensions\s+of\s+(?:image\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dim:
            img_var = m_dim.group(1).strip()
            target_var = m_dim.group(2).strip()
            return f"set {target_var} to image_dimensions({img_var})"

        # width of [image] <img_var> into <target>
        m_w = re.match(
            r"^width\s+of\s+(?:image\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_w:
            img_var = m_w.group(1).strip()
            target_var = m_w.group(2).strip()
            return f"set {target_var} to image_width({img_var})"

        # height of [image] <img_var> into <target>
        m_h = re.match(
            r"^height\s+of\s+(?:image\s+)?([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_h:
            img_var = m_h.group(1).strip()
            target_var = m_h.group(2).strip()
            return f"set {target_var} to image_height({img_var})"

        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()

        # open image <path> into <target>
        m_open = re.match(
            r"^open\s+image\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_open:
            path_expr = m_open.group(1).strip()
            target_var = m_open.group(2).strip()
            return f"set {target_var} to open_image({path_expr})"

        # create blank image with width <w>, height <h>[, color <col>] into <target>
        m_create = re.match(
            r"^create\s+blank\s+image\s+with\s+width\s+(\d+)\s*,\s*height\s+(\d+)(?:\s*,\s*color\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_create:
            w = m_create.group(1)
            h = m_create.group(2)
            color = m_create.group(3).strip() if m_create.group(3) else '"white"'
            target = m_create.group(4).strip()
            return f"set {target} to create_blank_image({w}, {h}, color={color})"

        # resize [image] <img_var> by <pct> percent into <target>
        m_pct = re.match(
            r"^resize\s+(?:image\s+)?([A-Za-z_]\w*)\s+by\s+(\d+(?:\.\d+)?)\s+percent\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pct:
            img_var = m_pct.group(1).strip()
            pct = m_pct.group(2).strip()
            target = m_pct.group(3).strip()
            return f"set {target} to resize_image({img_var}, percent={pct})"

        # resize [image] <img_var> to width <w>, height <h> into <target>
        m_dim_resize = re.match(
            r"^resize\s+(?:image\s+)?([A-Za-z_]\w*)\s+to\s+width\s+(\d+)\s*,\s*height\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dim_resize:
            img_var = m_dim_resize.group(1).strip()
            w = m_dim_resize.group(2).strip()
            h = m_dim_resize.group(3).strip()
            target = m_dim_resize.group(4).strip()
            return f"set {target} to resize_image({img_var}, width={w}, height={h})"

        # crop [image] <img_var> from <x1>, <y1> to <x2>, <y2> into <target>
        m_crop = re.match(
            r"^crop\s+(?:image\s+)?([A-Za-z_]\w*)\s+from\s+(\d+)\s*,\s*(\d+)\s+to\s+(\d+)\s*,\s*(\d+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_crop:
            img_var = m_crop.group(1).strip()
            x1, y1, x2, y2 = m_crop.group(2), m_crop.group(3), m_crop.group(4), m_crop.group(5)
            target = m_crop.group(6).strip()
            return f"set {target} to crop_image({img_var}, {x1}, {y1}, {x2}, {y2})"

        # rotate [image] <img_var> by <angle> degrees into <target>
        m_rot = re.match(
            r"^rotate\s+(?:image\s+)?([A-Za-z_]\w*)\s+by\s+(-?\d+(?:\.\d+)?)\s+degrees?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rot:
            img_var = m_rot.group(1).strip()
            angle = m_rot.group(2).strip()
            target = m_rot.group(3).strip()
            return f"set {target} to rotate_image({img_var}, {angle})"

        # flip [image] <img_var> (horizontally|vertically) into <target>
        m_flip = re.match(
            r"^flip\s+(?:image\s+)?([A-Za-z_]\w*)\s+(horizontally|vertically)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_flip:
            img_var = m_flip.group(1).strip()
            direction = f'"{m_flip.group(2).strip().lower()}"'
            target = m_flip.group(3).strip()
            return f"set {target} to flip_image({img_var}, {direction})"

        # apply (grayscale|blur|sharpen|contour|invert) to [image] <img_var> [with radius <r>] into <target>
        m_filt = re.match(
            r"^apply\s+(grayscale|blur|sharpen|contour|invert)\s+to\s+(?:image\s+)?([A-Za-z_]\w*)(?:\s+with\s+radius\s+(\d+(?:\.\d+)?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_filt:
            f_name = f'"{m_filt.group(1).strip().lower()}"'
            img_var = m_filt.group(2).strip()
            radius = m_filt.group(3) or "None"
            target = m_filt.group(4).strip()
            return f"set {target} to filter_image({img_var}, {f_name}, radius={radius})"

        # adjust brightness/contrast of [image] <img_var> by <factor> into <target>
        m_adj = re.match(
            r"^adjust\s+(brightness|contrast)\s+of\s+(?:image\s+)?([A-Za-z_]\w*)\s+by\s+(\d+(?:\.\d+)?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_adj:
            prop = m_adj.group(1).lower()
            img_var = m_adj.group(2).strip()
            factor = m_adj.group(3).strip()
            target = m_adj.group(4).strip()
            kw = "brightness" if prop == "brightness" else "contrast"
            return f"set {target} to adjust_image({img_var}, {kw}={factor})"

        # draw text <text> on [image] <img_var> at <x>, <y> [with color <col>]
        m_draw = re.match(
            r"^draw\s+text\s+(.+?)\s+on\s+(?:image\s+)?([A-Za-z_]\w*)\s+at\s+(\d+)\s*,\s*(\d+)(?:\s+with\s+color\s+(.+?))?$",
            s,
            re.IGNORECASE,
        )
        if m_draw:
            text_expr = m_draw.group(1).strip()
            img_var = m_draw.group(2).strip()
            x, y = m_draw.group(3), m_draw.group(4)
            color = m_draw.group(5).strip() if m_draw.group(5) else '"black"'
            return f"draw_on_image({img_var}, {text_expr}, {x}, {y}, color={color})"

        # save [image] <img_var> to <path> [with quality <q>]
        m_save = re.match(
            r"^save\s+(?:image\s+)?([A-Za-z_]\w*)\s+to\s+(.+?)(?:\s+with\s+quality\s+(\d+))?$",
            s,
            re.IGNORECASE,
        )
        if m_save:
            img_var = m_save.group(1).strip()
            path_expr = m_save.group(2).strip()
            quality = m_save.group(3) or "None"
            return f"save_image({img_var}, {path_expr}, quality={quality})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Image domain does not currently define declarative blocks")
