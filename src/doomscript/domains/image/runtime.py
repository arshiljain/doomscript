"""Runtime execution engine for Image & Vision domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import os
from doomscript.domains.base import DomainRuntime, DomainIR
from doomscript.domains.image.spec import (
    ImageOpenSpec,
    ImageCreateSpec,
    ImageResizeSpec,
    ImageCropSpec,
    ImageRotateSpec,
    ImageFilterSpec,
    ImageSaveSpec,
)

try:
    from PIL import Image as PILImage, ImageFilter as PILFilter, ImageEnhance, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class PureImage:
    """Lightweight pure-Python fallback representation of an image when Pillow is unavailable."""

    def __init__(self, width: int, height: int, color: str = "white", mode: str = "RGB"):
        self.width = width
        self.height = height
        self.mode = mode
        self.format = "PNG"
        self.color = color

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    def resize(self, width: int, height: int) -> "PureImage":
        return PureImage(width, height, color=self.color, mode=self.mode)

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> "PureImage":
        return PureImage(max(1, x2 - x1), max(1, y2 - y1), color=self.color, mode=self.mode)

    def rotate(self, angle: float) -> "PureImage":
        return PureImage(self.width, self.height, color=self.color, mode=self.mode)

    def transpose(self, method: int) -> "PureImage":
        return PureImage(self.width, self.height, color=self.color, mode=self.mode)

    def filter(self, filter_obj: Any) -> "PureImage":
        return PureImage(self.width, self.height, color=self.color, mode=self.mode)

    def convert(self, mode: str) -> "PureImage":
        return PureImage(self.width, self.height, color=self.color, mode=mode)

    def save(self, path: str, **kwargs) -> None:
        # Create minimal 1x1 dummy file or metadata stub
        with open(path, "wb") as f:
            f.write(b"PNG_FALLBACK")


class DoomImage:
    """A high-level ergonomic wrapper around images in DoomScript."""

    def __init__(self, raw_img: Any):
        self._img = raw_img

    @property
    def width(self) -> int:
        return self._img.width

    @property
    def height(self) -> int:
        return self._img.height

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    @property
    def format(self) -> str:
        return getattr(self._img, "format", "PNG") or "PNG"

    @property
    def mode(self) -> str:
        return self._img.mode

    def resize(
        self,
        width: Optional[int] = None,
        height: Optional[int] = None,
        percent: Optional[float] = None,
    ) -> "DoomImage":
        if percent is not None:
            factor = percent / 100.0
            new_w = max(1, int(self.width * factor))
            new_h = max(1, int(self.height * factor))
        else:
            new_w = int(width) if width is not None else self.width
            new_h = int(height) if height is not None else self.height

        if HAS_PIL and isinstance(self._img, PILImage.Image):
            res = self._img.resize((new_w, new_h), PILImage.Resampling.LANCZOS)
        else:
            res = self._img.resize(new_w, new_h)
        return DoomImage(res)

    def crop(self, x1: int, y1: int, x2: int, y2: int) -> "DoomImage":
        box = (int(x1), int(y1), int(x2), int(y2))
        res = self._img.crop(box)
        return DoomImage(res)

    def rotate(self, angle: float) -> "DoomImage":
        if HAS_PIL and isinstance(self._img, PILImage.Image):
            res = self._img.rotate(float(angle), expand=True)
        else:
            res = self._img.rotate(float(angle))
        return DoomImage(res)

    def flip(self, direction: str = "horizontal") -> "DoomImage":
        d = direction.lower()
        if HAS_PIL and isinstance(self._img, PILImage.Image):
            method = (
                PILImage.Transpose.FLIP_LEFT_RIGHT
                if "horiz" in d
                else PILImage.Transpose.FLIP_TOP_BOTTOM
            )
            res = self._img.transpose(method)
        else:
            res = self._img.transpose(1)
        return DoomImage(res)

    def apply_filter(self, name: str, radius: Optional[float] = None) -> "DoomImage":
        n = name.lower()
        if n == "grayscale":
            res = self._img.convert("L")
            return DoomImage(res)

        if HAS_PIL and isinstance(self._img, PILImage.Image):
            if n == "blur":
                r = float(radius) if radius is not None else 2.0
                res = self._img.filter(PILFilter.GaussianBlur(radius=r))
            elif n == "sharpen":
                res = self._img.filter(PILFilter.SHARPEN)
            elif n == "contour":
                res = self._img.filter(PILFilter.CONTOUR)
            elif n == "invert":
                from PIL import ImageOps
                res = ImageOps.invert(self._img.convert("RGB"))
            else:
                res = self._img
        else:
            res = self._img
        return DoomImage(res)

    def adjust(
        self,
        brightness: Optional[float] = None,
        contrast: Optional[float] = None,
    ) -> "DoomImage":
        img = self._img
        if HAS_PIL and isinstance(img, PILImage.Image):
            if brightness is not None:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(float(brightness))
            if contrast is not None:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(float(contrast))
        return DoomImage(img)

    def draw_text(
        self,
        text: str,
        x: int = 10,
        y: int = 10,
        color: str = "black",
        size: int = 20,
    ) -> "DoomImage":
        img_copy = self._img.copy() if hasattr(self._img, "copy") else self._img
        if HAS_PIL and isinstance(img_copy, PILImage.Image):
            draw = ImageDraw.Draw(img_copy)
            draw.text((x, y), text, fill=color)
        return DoomImage(img_copy)

    def save(self, path: str, quality: Optional[int] = None) -> str:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        save_kwargs = {}
        if quality is not None:
            save_kwargs["quality"] = int(quality)
        self._img.save(path, **save_kwargs)
        return path

    def __repr__(self) -> str:
        return f"DoomImage(size={self.size}, format='{self.format}', mode='{self.mode}')"


# Standalone Helper Functions
def open_image(path: str) -> DoomImage:
    if HAS_PIL:
        raw = PILImage.open(path)
    else:
        raw = PureImage(100, 100)
    return DoomImage(raw)


def create_blank_image(width: int, height: int, color: Any = "white") -> DoomImage:
    col = tuple(color) if isinstance(color, list) else color
    if HAS_PIL:
        raw = PILImage.new("RGB", (int(width), int(height)), color=col)
    else:
        raw = PureImage(int(width), int(height), color=col)
    return DoomImage(raw)


def image_dimensions(img: DoomImage) -> Tuple[int, int]:
    return img.size


def image_width(img: DoomImage) -> int:
    return img.width


def image_height(img: DoomImage) -> int:
    return img.height


def resize_image(
    img: DoomImage,
    width: Optional[int] = None,
    height: Optional[int] = None,
    percent: Optional[float] = None,
) -> DoomImage:
    return img.resize(width=width, height=height, percent=percent)


def crop_image(img: DoomImage, x1: int, y1: int, x2: int, y2: int) -> DoomImage:
    return img.crop(x1, y1, x2, y2)


def rotate_image(img: DoomImage, angle: float) -> DoomImage:
    return img.rotate(angle)


def flip_image(img: DoomImage, direction: str) -> DoomImage:
    return img.flip(direction)


def filter_image(img: DoomImage, filter_name: str, radius: Optional[float] = None) -> DoomImage:
    return img.apply_filter(filter_name, radius=radius)


def adjust_image(
    img: DoomImage,
    brightness: Optional[float] = None,
    contrast: Optional[float] = None,
) -> DoomImage:
    return img.adjust(brightness=brightness, contrast=contrast)


def draw_on_image(img: DoomImage, text: str, x: int, y: int, color: str = "black") -> DoomImage:
    return img.draw_text(text, x=x, y=y, color=color)


def save_image(img: DoomImage, path: str, quality: Optional[int] = None) -> str:
    return img.save(path, quality=quality)


class ImageRuntime(DomainRuntime):
    """Runtime execution engine for Image & Vision specifications."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        errors = ir.validate()
        if errors:
            raise ValueError(f"Image spec validation failed: {'; '.join(errors)}")

        if isinstance(ir, ImageOpenSpec):
            path = scope.get(ir.path_expr, ir.path_expr)
            return open_image(str(path))
        elif isinstance(ir, ImageCreateSpec):
            return create_blank_image(ir.width, ir.height, color=ir.color)
        elif isinstance(ir, ImageResizeSpec):
            img = scope.get(ir.image_var)
            return resize_image(img, width=ir.width, height=ir.height, percent=ir.percent)
        elif isinstance(ir, ImageCropSpec):
            img = scope.get(ir.image_var)
            return crop_image(img, ir.x1, ir.y1, ir.x2, ir.y2)
        elif isinstance(ir, ImageRotateSpec):
            img = scope.get(ir.image_var)
            return rotate_image(img, ir.angle)
        elif isinstance(ir, ImageFilterSpec):
            img = scope.get(ir.image_var)
            return filter_image(img, ir.filter_name, radius=ir.radius)
        elif isinstance(ir, ImageSaveSpec):
            img = scope.get(ir.image_var)
            path = scope.get(ir.path_expr, ir.path_expr)
            return save_image(img, str(path), quality=ir.quality)

        raise NotImplementedError(f"Unsupported IR: {type(ir)}")


def execute_image_ir(spec_id: str) -> Any:
    from doomscript.domains.registry import get_domain_registry
    spec = get_domain_registry().get_spec(spec_id)
    if spec is None:
        raise KeyError(f"Image spec not found: {spec_id}")
    return ImageRuntime().execute_ir(spec, {})


# --- Batch 8 Spoken English Image Verbs ---

def image_to_grayscale(img: Any) -> Any:
    """Convert image to grayscale."""
    if isinstance(img, DoomImage):
        return DoomImage(img._img.convert("L"))
    return img


def image_blur(img: Any, radius: Any = 2) -> Any:
    """Blur image with specified radius."""
    if isinstance(img, DoomImage):
        return filter_image(img, "blur", radius=float(radius))
    return img


def image_resize(img: Any, width: Any = 100, height: Any = 100) -> Any:
    """Resize image to width and height."""
    if isinstance(img, DoomImage):
        return resize_image(img, width=int(width), height=int(height))
    return img


def image_crop_box(img: Any, box: Any) -> Any:
    """Crop image with box coordinates [x1, y1, x2, y2]."""
    if isinstance(img, DoomImage):
        b = list(box)
        return crop_image(img, int(b[0]), int(b[1]), int(b[2]), int(b[3]))
    return img


def image_rotate(img: Any, angle: Any) -> Any:
    """Rotate image by angle in degrees."""
    if isinstance(img, DoomImage):
        return rotate_image(img, float(angle))
    return img


def image_adjust_brightness(img: Any, factor: Any) -> Any:
    """Adjust image brightness by multiplier factor."""
    if isinstance(img, DoomImage):
        return adjust_image(img, brightness=float(factor))
    return img


def image_histogram(img: Any) -> List[int]:
    """Calculate color channel histogram."""
    if isinstance(img, DoomImage):
        if HAS_PIL and hasattr(img._img, "histogram"):
            return list(img._img.histogram())
    return [0] * 256


# --- 350-Expansion 20 Image Operations ---

def _unwrap_img(img: Any) -> Any:
    if isinstance(img, DoomImage):
        return img._img
    return img


def image_sobel_edge_detection(img: Any) -> Any:
    """Sobel 2D convolution edge magnitude detection."""
    import math
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    gray = raw.convert("L")
    w, h = gray.size
    px = gray.load()
    out = PILImage.new("L", (w, h), 0)
    out_px = out.load()
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            gx = (-px[x - 1, y - 1] + px[x + 1, y - 1]
                  - 2 * px[x - 1, y] + 2 * px[x + 1, y]
                  - px[x - 1, y + 1] + px[x + 1, y + 1])
            gy = (-px[x - 1, y - 1] - 2 * px[x, y - 1] - px[x + 1, y - 1]
                  + px[x - 1, y + 1] + 2 * px[x, y + 1] + px[x + 1, y + 1])
            mag = min(255, int(math.hypot(gx, gy)))
            out_px[x, y] = mag
    return DoomImage(out)


def image_threshold_binarize(img: Any, threshold: Any = 128) -> Any:
    """Binarize image to pure black/white using threshold."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    t = int(threshold)
    gray = raw.convert("L")
    out = gray.point(lambda p: 255 if p >= t else 0, mode="1")
    return DoomImage(out.convert("RGB"))


def image_sharpen(img: Any) -> Any:
    """High-pass sharpening filter."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    return DoomImage(raw.filter(PILFilter.SHARPEN))


def image_invert_colors(img: Any) -> Any:
    """Negative photographic color inversion."""
    from PIL import ImageOps
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    rgb = raw.convert("RGB")
    return DoomImage(ImageOps.invert(rgb))


def image_adjust_contrast(img: Any, factor: Any = 1.5) -> Any:
    """Adjust contrast around midpoint 128."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    enhancer = ImageEnhance.Contrast(raw)
    return DoomImage(enhancer.enhance(float(factor)))


def image_split_channels(img: Any) -> Dict[str, Any]:
    """Separate RGB image into red, green, blue channels."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return {"r": img, "g": img, "b": img}
    rgb = raw.convert("RGB")
    r, g, b = rgb.split()
    return {"r": DoomImage(r), "g": DoomImage(g), "b": DoomImage(b)}


def image_merge_channels(r_img: Any, g_img: Any, b_img: Any) -> Any:
    """Combine 3 single-channel images into one RGB image."""
    r_raw = _unwrap_img(r_img)
    g_raw = _unwrap_img(g_img)
    b_raw = _unwrap_img(b_img)
    if not (HAS_PIL and isinstance(r_raw, PILImage.Image)):
        return r_img
    r = r_raw.convert("L")
    g = g_raw.convert("L").resize(r.size)
    b = b_raw.convert("L").resize(r.size)
    merged = PILImage.merge("RGB", (r, g, b))
    return DoomImage(merged)


def image_apply_sepia(img: Any) -> Any:
    """Classic warm sepia photographic transformation."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    rgb = raw.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    out = PILImage.new("RGB", (w, h))
    out_px = out.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            tr = min(255, int(0.393 * r + 0.769 * g + 0.189 * b))
            tg = min(255, int(0.349 * r + 0.686 * g + 0.168 * b))
            tb = min(255, int(0.272 * r + 0.534 * g + 0.131 * b))
            out_px[x, y] = (tr, tg, tb)
    return DoomImage(out)


def image_flip_horizontal(img: Any) -> Any:
    """Flip image horizontally (left-to-right)."""
    return flip_image(img, "horizontal") if isinstance(img, DoomImage) else img


def image_flip_vertical(img: Any) -> Any:
    """Flip image vertically (top-to-bottom)."""
    return flip_image(img, "vertical") if isinstance(img, DoomImage) else img


def image_color_vignette(img: Any, radius: Any = 0.8) -> Any:
    """Apply radial photographic vignette darkening towards edges."""
    import math
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    rgb = raw.convert("RGB")
    w, h = rgb.size
    px = rgb.load()
    out = PILImage.new("RGB", (w, h))
    out_px = out.load()
    cx, cy = w / 2.0, h / 2.0
    max_d = math.hypot(cx, cy) * float(radius) or 1.0
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, y - cy)
            falloff = max(0.0, min(1.0, 1.0 - (d / max_d) ** 2))
            r, g, b = px[x, y]
            out_px[x, y] = (int(r * falloff), int(g * falloff), int(b * falloff))
    return DoomImage(out)


def image_pad_borders(img: Any, pad_size: Any = 10, color: Any = "black") -> Any:
    """Pad borders of image with a solid color."""
    from PIL import ImageOps
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    col = tuple(color) if isinstance(color, list) else color
    out = ImageOps.expand(raw, border=int(pad_size), fill=col)
    return DoomImage(out)


def image_compute_mean_color(img: Any) -> List[float]:
    """Average [R, G, B] color across all pixels."""
    from PIL import ImageStat
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return [0.0, 0.0, 0.0]
    stat = ImageStat.Stat(raw.convert("RGB"))
    return [round(c, 2) for c in stat.mean[:3]]


def image_crop_center(img: Any, width: Any = 100, height: Any = 100) -> Any:
    """Symmetrical center crop of image to desired dimensions."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    w, h = raw.size
    cw, ch = int(width), int(height)
    left = max(0, (w - cw) // 2)
    top = max(0, (h - ch) // 2)
    right = min(w, left + cw)
    bottom = min(h, top + ch)
    return DoomImage(raw.crop((left, top, right, bottom)))


def image_gamma_correction(img: Any, gamma: Any = 1.2) -> Any:
    """Exponential gamma luminance correction."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    g = max(1e-4, float(gamma))
    lut = [int(((i / 255.0) ** (1.0 / g)) * 255) for i in range(256)]
    rgb = raw.convert("RGB")
    out = rgb.point(lut * 3)
    return DoomImage(out)


def image_emboss(img: Any) -> Any:
    """Directional 3D embossing convolution filter."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    return DoomImage(raw.filter(PILFilter.EMBOSS))


def image_posterize(img: Any, levels: Any = 4) -> Any:
    """Reduce color depth quantization to N discrete levels."""
    import math
    from PIL import ImageOps
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    lev = max(2, int(levels))
    bits = max(1, min(8, int(round(math.log2(lev)))) or 2)
    rgb = raw.convert("RGB")
    out = ImageOps.posterize(rgb, bits)
    return DoomImage(out)


def image_mosaic_pixelate(img: Any, block_size: Any = 10) -> Any:
    """Pixelate image into uniform mosaic tiles."""
    raw = _unwrap_img(img)
    if not (HAS_PIL and isinstance(raw, PILImage.Image)):
        return img
    bs = max(1, int(block_size))
    w, h = raw.size
    bw = max(1, w // bs)
    bh = max(1, h // bs)
    small = raw.resize((bw, bh), PILImage.Resampling.NEAREST)
    out = small.resize((w, h), PILImage.Resampling.NEAREST)
    return DoomImage(out)


def image_blend_overlay(img1: Any, img2: Any, alpha: Any = 0.5) -> Any:
    """Linear alpha blend of two images."""
    r1 = _unwrap_img(img1)
    r2 = _unwrap_img(img2)
    if not (HAS_PIL and isinstance(r1, PILImage.Image) and isinstance(r2, PILImage.Image)):
        return img1
    rgb1 = r1.convert("RGB")
    rgb2 = r2.convert("RGB").resize(rgb1.size)
    a = max(0.0, min(1.0, float(alpha)))
    out = PILImage.blend(rgb1, rgb2, a)
    return DoomImage(out)


def image_difference(img1: Any, img2: Any) -> Any:
    """Absolute pixel-by-pixel difference map."""
    from PIL import ImageChops
    r1 = _unwrap_img(img1)
    r2 = _unwrap_img(img2)
    if not (HAS_PIL and isinstance(r1, PILImage.Image) and isinstance(r2, PILImage.Image)):
        return img1
    rgb1 = r1.convert("RGB")
    rgb2 = r2.convert("RGB").resize(rgb1.size)
    out = ImageChops.difference(rgb1, rgb2)
    return DoomImage(out)


