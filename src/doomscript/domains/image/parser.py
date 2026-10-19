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
            r"^create\s+blank\s+image\s+with\s+width\s+(\d+)\s*(?:,|and)?\s*height\s+(\d+)(?:\s*(?:,|and)?\s*color\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
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

        # resize [image] <img_var> to width <w>[,] height <h> into <target>
        m_dim_resize = re.match(
            r"^resize\s+(?:image\s+)?([A-Za-z_]\w*)\s+to\s+width\s+(\d+)\s*(?:,|and)?\s*height\s+(\d+)\s+into\s+([A-Za-z_]\w*)$",
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

        # convert image <img_var> to grayscale into <target>
        m_gray = re.match(
            r"^convert\s+image\s+(.+?)\s+to\s+grayscale\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gray:
            img, target = m_gray.group(1).strip(), m_gray.group(2).strip()
            return f"set {target} to image_to_grayscale({img})"

        # blur image <img_var> with radius <r> into <target> OR apply blur with radius <r> to image <img_var> into <target>
        m_blur = re.match(
            r"^(?:apply\s+blur\s+with\s+radius\s+(.+?)\s+to\s+(?:image\s+)?(.+?)|blur\s+image\s+(.+?)\s+with\s+radius\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_blur:
            if m_blur.group(1) is not None:
                r, img, target = m_blur.group(1).strip(), m_blur.group(2).strip(), m_blur.group(5).strip()
            else:
                img, r, target = m_blur.group(3).strip(), m_blur.group(4).strip(), m_blur.group(5).strip()
            return f"set {target} to image_blur({img}, radius={r})"

        # crop box <box> from image <img_var> into <target> OR crop image <img_var> with box <box> into <target>
        m_cbox = re.match(
            r"^(?:crop\s+box\s+(.+?)\s+from\s+(?:image\s+)?(.+?)|crop\s+image\s+(.+?)\s+with\s+box\s+(.+?))\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cbox:
            if m_cbox.group(1) is not None:
                box, img, target = m_cbox.group(1).strip(), m_cbox.group(2).strip(), m_cbox.group(5).strip()
            else:
                img, box, target = m_cbox.group(3).strip(), m_cbox.group(4).strip(), m_cbox.group(5).strip()
            return f"set {target} to image_crop_box({img}, {box})"

        # rotate image <img_var> by [angle] <deg> [degrees] into <target>
        m_rot = re.match(
            r"^rotate\s+image\s+(.+?)\s+by\s+(?:angle\s+)?(-?\d+(?:\.\d+)?)(?:\s+degrees?)?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rot:
            img, deg, target = m_rot.group(1).strip(), m_rot.group(2).strip(), m_rot.group(3).strip()
            return f"set {target} to image_rotate({img}, {deg})"

        # adjust brightness of <img_var> by factor <f> into <target>
        m_bright = re.match(
            r"^adjust\s+brightness\s+of\s+(?:image\s+)?(.+?)\s+by\s+factor\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bright:
            img, f, target = m_bright.group(1).strip(), m_bright.group(2).strip(), m_bright.group(3).strip()
            return f"set {target} to image_adjust_brightness({img}, {f})"

        # color histogram of <img_var> into <target> OR calculate histogram of image <img_var> into <target>
        m_hist = re.match(
            r"^(?:calculate\s+histogram\s+of\s+(?:image\s+)?|color\s+histogram\s+of\s+(?:image\s+)?)(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_hist:
            img, target = m_hist.group(1).strip(), m_hist.group(2).strip()
            return f"set {target} to image_histogram({img})"

        # sobel edge detection on <img_var> into <target>
        m_sobel = re.match(
            r"^(?:sobel\s+edge\s+detection\s+(?:on|of)\s+(?:image\s+)?|detect\s+edges\s+with\s+sobel\s+on\s+)(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sobel:
            img, target = m_sobel.group(1).strip(), m_sobel.group(2).strip()
            return f"set {target} to image_sobel_edge_detection({img})"

        # binarize <img_var> with threshold <t> into <target>
        m_bin = re.match(
            r"^(?:binarize|threshold)\s+(?:image\s+)?(.+?)\s+with\s+threshold\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bin:
            img, t, target = m_bin.group(1).strip(), m_bin.group(2).strip(), m_bin.group(3).strip()
            return f"set {target} to image_threshold_binarize({img}, threshold={t})"

        # sharpen image <img_var> into <target>
        m_sharp = re.match(
            r"^sharpen\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sharp:
            img, target = m_sharp.group(1).strip(), m_sharp.group(2).strip()
            return f"set {target} to image_sharpen({img})"

        # invert colors of <img_var> into <target>
        m_inv = re.match(
            r"^invert\s+colors\s+of\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_inv:
            img, target = m_inv.group(1).strip(), m_inv.group(2).strip()
            return f"set {target} to image_invert_colors({img})"

        # adjust contrast of <img_var> by factor <f> into <target>
        m_cont = re.match(
            r"^adjust\s+contrast\s+of\s+(?:image\s+)?(.+?)\s+by\s+(?:factor\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cont:
            img, f, target = m_cont.group(1).strip(), m_cont.group(2).strip(), m_cont.group(3).strip()
            return f"set {target} to image_adjust_contrast({img}, factor={f})"

        # split channels of <img_var> into <target>
        m_split = re.match(
            r"^split\s+channels\s+of\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_split:
            img, target = m_split.group(1).strip(), m_split.group(2).strip()
            return f"set {target} to image_split_channels({img})"

        # merge channels <r>, <g>, <b> into <target>
        m_merge = re.match(
            r"^merge\s+channels\s+(.+?)\s*,\s*(.+?)\s*,\s*(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_merge:
            r, g, b, target = m_merge.group(1).strip(), m_merge.group(2).strip(), m_merge.group(3).strip(), m_merge.group(4).strip()
            return f"set {target} to image_merge_channels({r}, {g}, {b})"

        # apply sepia to <img_var> into <target>
        m_sepia = re.match(
            r"^apply\s+sepia\s+to\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sepia:
            img, target = m_sepia.group(1).strip(), m_sepia.group(2).strip()
            return f"set {target} to image_apply_sepia({img})"

        # flip <img_var> horizontally into <target>
        m_fh = re.match(
            r"^flip\s+(?:image\s+)?(.+?)\s+horizontally\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fh:
            img, target = m_fh.group(1).strip(), m_fh.group(2).strip()
            return f"set {target} to image_flip_horizontal({img})"

        # flip <img_var> vertically into <target>
        m_fv = re.match(
            r"^flip\s+(?:image\s+)?(.+?)\s+vertically\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fv:
            img, target = m_fv.group(1).strip(), m_fv.group(2).strip()
            return f"set {target} to image_flip_vertical({img})"

        # apply vignette to <img_var> [with radius <r>] into <target>
        m_vig = re.match(
            r"^apply\s+vignette\s+to\s+(?:image\s+)?(.+?)(?:\s+with\s+radius\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_vig:
            img, r, target = m_vig.group(1).strip(), m_vig.group(2), m_vig.group(3).strip()
            r_arg = f", radius={r.strip()}" if r else ""
            return f"set {target} to image_color_vignette({img}{r_arg})"

        # pad borders of <img_var> with <pad_size> [and color <col>] into <target>
        m_pad = re.match(
            r"^pad\s+borders\s+of\s+(?:image\s+)?(.+?)\s+with\s+(.+?)(?:\s+and\s+color\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pad:
            img, ps, col, target = m_pad.group(1).strip(), m_pad.group(2).strip(), m_pad.group(3), m_pad.group(4).strip()
            col_arg = f", color={col.strip()}" if col else ""
            return f"set {target} to image_pad_borders({img}, pad_size={ps}{col_arg})"

        # compute mean color of <img_var> into <target>
        m_mean = re.match(
            r"^(?:compute\s+mean\s+color\s+of|mean\s+color\s+of)\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mean:
            img, target = m_mean.group(1).strip(), m_mean.group(2).strip()
            return f"set {target} to image_compute_mean_color({img})"

        # center crop <img_var> to width <w> and height <h> into <target>
        m_ccrop = re.match(
            r"^(?:center\s+crop|crop\s+center\s+of)\s+(?:image\s+)?(.+?)\s+to\s+width\s+(.+?)\s+and\s+height\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ccrop:
            img, w, h, target = m_ccrop.group(1).strip(), m_ccrop.group(2).strip(), m_ccrop.group(3).strip(), m_ccrop.group(4).strip()
            return f"set {target} to image_crop_center({img}, width={w}, height={h})"

        # apply gamma correction to <img_var> with gamma <g> into <target>
        m_gam = re.match(
            r"^apply\s+gamma\s+correction\s+to\s+(?:image\s+)?(.+?)\s+with\s+gamma\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gam:
            img, g, target = m_gam.group(1).strip(), m_gam.group(2).strip(), m_gam.group(3).strip()
            return f"set {target} to image_gamma_correction({img}, gamma={g})"

        # apply emboss to <img_var> into <target>
        m_emb = re.match(
            r"^apply\s+emboss\s+to\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_emb:
            img, target = m_emb.group(1).strip(), m_emb.group(2).strip()
            return f"set {target} to image_emboss({img})"

        # posterize <img_var> with <levels> levels into <target>
        m_post = re.match(
            r"^posterize\s+(?:image\s+)?(.+?)\s+with\s+(.+?)\s+levels\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_post:
            img, lev, target = m_post.group(1).strip(), m_post.group(2).strip(), m_post.group(3).strip()
            return f"set {target} to image_posterize({img}, levels={lev})"

        # pixelate <img_var> with block size <bs> into <target>
        m_pix = re.match(
            r"^(?:pixelate|mosaic)\s+(?:image\s+)?(.+?)\s+with\s+block\s+size\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pix:
            img, bs, target = m_pix.group(1).strip(), m_pix.group(2).strip(), m_pix.group(3).strip()
            return f"set {target} to image_mosaic_pixelate({img}, block_size={bs})"

        # blend <img1> and <img2> with alpha <a> into <target>
        m_bl = re.match(
            r"^blend\s+(?:image\s+)?(.+?)\s+and\s+(?:image\s+)?(.+?)\s+with\s+alpha\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bl:
            i1, i2, a, target = m_bl.group(1).strip(), m_bl.group(2).strip(), m_bl.group(3).strip(), m_bl.group(4).strip()
            return f"set {target} to image_blend_overlay({i1}, {i2}, alpha={a})"

        # difference between <img1> and <img2> into <target>
        m_diff = re.match(
            r"^(?:difference\s+between\s+(?:image\s+)?|pixel\s+difference\s+between\s+)(.+?)\s+and\s+(?:image\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_diff:
            i1, i2, target = m_diff.group(1).strip(), m_diff.group(2).strip(), m_diff.group(3).strip()
            return f"set {target} to image_difference({i1}, {i2})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[Any, str]:
        raise NotImplementedError("Image domain does not currently define declarative blocks")
