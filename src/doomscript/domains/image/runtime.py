"""Runtime execution engine for Image & Vision domain."""

from typing import Any, Dict, List, Optional, Tuple, Union
import math
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

    def __getitem__(self, item: int) -> Any:
        grid, _, _ = _to_gray_grid(self)
        return grid[item]

    def __len__(self) -> int:
        return self.height

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


# =========================================================================
# Deepened Computer Vision: Canny, Otsu, Bilateral Filter, Hough Lines
# =========================================================================

def _to_gray_grid(img_or_pixels: Any) -> Tuple[List[List[float]], int, int]:
    """Extract a 2D float intensity grid (H, W) from DoomImage, PIL Image, or nested lists."""
    raw = _unwrap_img(img_or_pixels)
    if HAS_PIL and isinstance(raw, PILImage.Image):
        gray = raw.convert("L")
        w, h = gray.size
        data = list(gray.getdata())
        grid = [[float(data[y * w + x]) for x in range(w)] for y in range(h)]
        return grid, w, h
    elif isinstance(img_or_pixels, (list, tuple)) and img_or_pixels:
        if isinstance(img_or_pixels[0], (list, tuple)):
            h = len(img_or_pixels)
            w = len(img_or_pixels[0])
            grid = []
            for row in img_or_pixels:
                g_row = []
                for val in row:
                    if isinstance(val, (tuple, list)):
                        # Average RGB
                        g_row.append(sum(val[:3]) / max(1, len(val[:3])))
                    else:
                        g_row.append(float(val))
                grid.append(g_row)
            return grid, w, h
    # Fallback 10x10 zero grid
    return [[0.0] * 10 for _ in range(10)], 10, 10


def image_canny_edge_detector(
    img: Any,
    low_thresh: float = 20.0,
    high_thresh: float = 50.0,
) -> Any:
    """Full 5-stage Canny Edge Detection pipeline."""
    import math
    grid, w, h = _to_gray_grid(img)
    if h < 3 or w < 3:
        return img

    # 1. 5x5 Gaussian Blur
    kernel = [
        [2, 4, 5, 4, 2],
        [4, 9, 12, 9, 4],
        [5, 12, 15, 12, 5],
        [4, 9, 12, 9, 4],
        [2, 4, 5, 4, 2],
    ]
    k_sum = 159.0
    blurred = [[0.0] * w for _ in range(h)]
    for y in range(2, h - 2):
        for x in range(2, w - 2):
            val = sum(grid[y + ky - 2][x + kx - 2] * kernel[ky][kx] for ky in range(5) for kx in range(5))
            blurred[y][x] = val / k_sum

    # 2. Sobel Gradients
    gx = [[0.0] * w for _ in range(h)]
    gy = [[0.0] * w for _ in range(h)]
    mag = [[0.0] * w for _ in range(h)]
    angle = [[0.0] * w for _ in range(h)]

    kx_sobel = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    ky_sobel = [[1, 2, 1], [0, 0, 0], [-1, -2, -1]]

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            val_x = sum(blurred[y + ky - 1][x + kx - 1] * kx_sobel[ky][kx] for ky in range(3) for kx in range(3))
            val_y = sum(blurred[y + ky - 1][x + kx - 1] * ky_sobel[ky][kx] for ky in range(3) for kx in range(3))
            gx[y][x] = val_x
            gy[y][x] = val_y
            m = math.sqrt(val_x * val_x + val_y * val_y)
            mag[y][x] = m
            ang = (math.atan2(val_y, val_x) * 180.0 / math.pi) % 180.0
            angle[y][x] = ang

    # 3. Non-Maximum Suppression
    nms = [[0.0] * w for _ in range(h)]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            ang = angle[y][x]
            m = mag[y][x]
            q, r = 255.0, 255.0

            # 0 deg (east-west)
            if (0 <= ang < 22.5) or (157.5 <= ang <= 180):
                q = mag[y][x + 1]
                r = mag[y][x - 1]
            # 45 deg (northeast-southwest)
            elif 22.5 <= ang < 67.5:
                q = mag[y + 1][x - 1]
                r = mag[y - 1][x + 1]
            # 90 deg (north-south)
            elif 67.5 <= ang < 112.5:
                q = mag[y + 1][x]
                r = mag[y - 1][x]
            # 135 deg (northwest-southeast)
            elif 112.5 <= ang < 157.5:
                q = mag[y - 1][x - 1]
                r = mag[y + 1][x + 1]

            if m >= q and m >= r:
                nms[y][x] = m
            else:
                nms[y][x] = 0.0

    # 4. Double Hysteresis Thresholding
    edges = [[0] * w for _ in range(h)]
    strong, weak = 255, 50

    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if nms[y][x] >= high_thresh:
                edges[y][x] = strong
            elif nms[y][x] >= low_thresh:
                edges[y][x] = weak

    # 5. Edge Tracking by Hysteresis
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if edges[y][x] == weak:
                if any(edges[y + dy][x + dx] == strong for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                    edges[y][x] = strong
                else:
                    edges[y][x] = 0

    if HAS_PIL:
        flat_bytes = bytes([edges[y][x] for y in range(h) for x in range(w)])
        out_pil = PILImage.frombytes("L", (w, h), flat_bytes)
        return DoomImage(out_pil)
    return edges


def image_otsu_threshold(img: Any) -> Dict[str, Any]:
    """Otsu automated binarization threshold maximizing inter-class variance."""
    grid, w, h = _to_gray_grid(img)
    total_pixels = w * h
    if total_pixels == 0:
        return {"threshold": 128, "binary_image": grid}

    # Histogram
    hist = [0] * 256
    for y in range(h):
        for x in range(w):
            v = max(0, min(255, int(round(grid[y][x]))))
            hist[v] += 1

    sum_all = sum(i * hist[i] for i in range(256))
    sum_b = 0.0
    w_b = 0.0
    max_var = -1.0
    best_thresholds: List[int] = [128]

    for t in range(256):
        w_b += hist[t]
        if w_b == 0:
            continue
        w_f = total_pixels - w_b
        if w_f == 0:
            break

        sum_b += t * hist[t]
        m_b = sum_b / w_b
        m_f = (sum_all - sum_b) / w_f

        # Between class variance
        var_between = w_b * w_f * ((m_b - m_f) ** 2)
        if var_between > max_var + 1e-5:
            max_var = var_between
            best_thresholds = [t]
        elif abs(var_between - max_var) <= 1e-5 and max_var >= 0.0:
            best_thresholds.append(t)

    best_thresh = sum(best_thresholds) // len(best_thresholds)
    binary = [[255 if grid[y][x] >= best_thresh else 0 for x in range(w)] for y in range(h)]
    res: Dict[str, Any] = {"threshold": best_thresh, "binary_grid": binary}

    if HAS_PIL:
        flat_bytes = bytes([binary[y][x] for y in range(h) for x in range(w)])
        out_pil = PILImage.frombytes("L", (w, h), flat_bytes)
        res["image"] = DoomImage(out_pil)

    return res


def image_bilateral_filter(
    img: Any,
    d: int = 5,
    sigma_color: float = 30.0,
    sigma_space: float = 30.0,
) -> Any:
    """Edge-preserving bilateral smoothing filter."""
    import math
    grid, w, h = _to_gray_grid(img)
    rad = d // 2
    out = [[0.0] * w for _ in range(h)]

    two_sigma_color_sq = 2.0 * (sigma_color ** 2)
    two_sigma_space_sq = 2.0 * (sigma_space ** 2)

    for y in range(h):
        for x in range(w):
            center_val = grid[y][x]
            weight_sum = 0.0
            val_sum = 0.0

            y_min = max(0, y - rad)
            y_max = min(h, y + rad + 1)
            x_min = max(0, x - rad)
            x_max = min(w, x + rad + 1)

            for ny in range(y_min, y_max):
                for nx in range(x_min, x_max):
                    n_val = grid[ny][nx]
                    space_dist_sq = (x - nx) ** 2 + (y - ny) ** 2
                    color_dist_sq = (center_val - n_val) ** 2

                    w_spatial = math.exp(-space_dist_sq / two_sigma_space_sq)
                    w_color = math.exp(-color_dist_sq / two_sigma_color_sq)
                    weight = w_spatial * w_color

                    val_sum += n_val * weight
                    weight_sum += weight

            out[y][x] = round(val_sum / (weight_sum or 1.0), 2)

    if HAS_PIL:
        flat_bytes = bytes([max(0, min(255, int(out[y][x]))) for y in range(h) for x in range(w)])
        out_pil = PILImage.frombytes("L", (w, h), flat_bytes)
        return DoomImage(out_pil)
    return out


def image_hough_lines(
    edge_map: Any,
    threshold: int = 20,
    rho_res: float = 1.0,
    theta_res_deg: float = 1.0,
) -> List[Dict[str, Any]]:
    """Hough Transform detecting geometric straight lines in edge maps."""
    import math
    grid, w, h = _to_gray_grid(edge_map)
    diag_len = int(math.ceil(math.sqrt(w * w + h * h)))

    n_thetas = int(180 / theta_res_deg)
    thetas = [math.radians(i * theta_res_deg) for i in range(n_thetas)]
    cos_t = [math.cos(t) for t in thetas]
    sin_t = [math.sin(t) for t in thetas]

    n_rhos = int(2 * diag_len / rho_res) + 1
    accumulator = [[0] * n_thetas for _ in range(n_rhos)]

    for y in range(h):
        for x in range(w):
            if grid[y][x] > 100:  # Edge pixel
                for t_idx in range(n_thetas):
                    rho = x * cos_t[t_idx] + y * sin_t[t_idx]
                    rho_idx = int(round((rho + diag_len) / rho_res))
                    if 0 <= rho_idx < n_rhos:
                        accumulator[rho_idx][t_idx] += 1

    lines = []
    for r_idx in range(n_rhos):
        for t_idx in range(n_thetas):
            votes = accumulator[r_idx][t_idx]
            if votes >= threshold:
                rho_val = (r_idx * rho_res) - diag_len
                theta_deg = round(t_idx * theta_res_deg, 2)
                lines.append({
                    "rho": round(rho_val, 2),
                    "theta_deg": theta_deg,
                    "votes": votes,
                })

    lines.sort(key=lambda l: l["votes"], reverse=True)
    return lines


# ==============================================================================
# Advanced Image Deepening: Geometric Warp, Morphological Ops & Quantization
# ==============================================================================

class GeometricWarp:
    """Affine & Perspective homography transformations with inverse bilinear mapping."""

    @staticmethod
    def _invert_3x3(m: List[List[float]]) -> List[List[float]]:
        # Determinant
        det = (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )
        if abs(det) < 1e-12:
            raise ValueError("Singular transformation matrix cannot be inverted")

        inv_det = 1.0 / det
        return [
            [
                (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det,
                (m[0][2] * m[2][1] - m[0][1] * m[2][2]) * inv_det,
                (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det,
            ],
            [
                (m[1][2] * m[2][0] - m[1][0] * m[2][2]) * inv_det,
                (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det,
                (m[0][2] * m[1][0] - m[0][0] * m[1][2]) * inv_det,
            ],
            [
                (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det,
                (m[0][1] * m[2][0] - m[0][0] * m[2][1]) * inv_det,
                (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det,
            ],
        ]

    @classmethod
    def affine_matrix(
        cls,
        translation: Tuple[float, float] = (0.0, 0.0),
        rotation_deg: float = 0.0,
        scale: Tuple[float, float] = (1.0, 1.0),
        shear: Tuple[float, float] = (0.0, 0.0),
    ) -> List[List[float]]:
        """Constructs 3x3 forward 2D affine transformation matrix."""
        rad = math.radians(rotation_deg)
        cos_t, sin_t = math.cos(rad), math.sin(rad)
        sx, sy = scale
        shx, shy = shear
        tx, ty = translation

        # T * R * Sh * S
        # Scale & Shear
        # [sx,      shx * sy, 0]
        # [shy * sx, sy,      0]
        # [0,       0,        1]
        m00 = cos_t * sx - sin_t * shy * sx
        m01 = cos_t * shx * sy - sin_t * sy
        m02 = tx
        m10 = sin_t * sx + cos_t * shy * sx
        m11 = sin_t * shx * sy + cos_t * sy
        m12 = ty

        return [
            [m00, m01, m02],
            [m10, m11, m12],
            [0.0, 0.0, 1.0],
        ]

    @classmethod
    def warp(
        cls,
        img: Any,
        matrix: List[List[float]],
        out_dims: Optional[Tuple[int, int]] = None,
        fill_val: float = 0.0,
    ) -> List[List[float]]:
        """
        Applies forward 3x3 transformation matrix to grayscale image via inverse bilinear interpolation.
        """
        grid, in_w, in_h = _to_gray_grid(img)
        out_w, out_h = out_dims if out_dims is not None else (in_w, in_h)

        inv_m = cls._invert_3x3(matrix)
        out = [[fill_val] * out_w for _ in range(out_h)]

        for yd in range(out_h):
            for xd in range(out_w):
                # Map destination (xd, yd) to source (xs, ys)
                w_norm = inv_m[2][0] * xd + inv_m[2][1] * yd + inv_m[2][2]
                if abs(w_norm) < 1e-9:
                    continue
                xs = (inv_m[0][0] * xd + inv_m[0][1] * yd + inv_m[0][2]) / w_norm
                ys = (inv_m[1][0] * xd + inv_m[1][1] * yd + inv_m[1][2]) / w_norm

                if 0.0 <= xs <= in_w - 1.0 and 0.0 <= ys <= in_h - 1.0:
                    x0 = int(math.floor(xs))
                    y0 = int(math.floor(ys))
                    x1 = min(in_w - 1, x0 + 1)
                    y1 = min(in_h - 1, y0 + 1)

                    dx = xs - x0
                    dy = ys - y0

                    v00 = grid[y0][x0]
                    v01 = grid[y0][x1]
                    v10 = grid[y1][x0]
                    v11 = grid[y1][x1]

                    interp = (
                        (1.0 - dx) * (1.0 - dy) * v00
                        + dx * (1.0 - dy) * v01
                        + (1.0 - dx) * dy * v10
                        + dx * dy * v11
                    )
                    out[yd][xd] = round(interp, 2)

        return out


class MorphologicalOps:
    """Grayscale and binary morphological filtering (dilation, erosion, opening, closing)."""

    @staticmethod
    def _get_structuring_element(shape: str = "rect", size: int = 3) -> List[Tuple[int, int]]:
        rad = size // 2
        offsets = []
        for dy in range(-rad, rad + 1):
            for dx in range(-rad, rad + 1):
                if shape == "cross":
                    if dx == 0 or dy == 0:
                        offsets.append((dx, dy))
                elif shape == "disk":
                    if dx * dx + dy * dy <= rad * rad:
                        offsets.append((dx, dy))
                else:  # rect
                    offsets.append((dx, dy))
        return offsets

    @classmethod
    def dilate(cls, img: Any, size: int = 3, shape: str = "rect") -> List[List[float]]:
        """Morphological dilation (maximum filter within kernel)."""
        grid, w, h = _to_gray_grid(img)
        offsets = cls._get_structuring_element(shape, size)
        out = [[0.0] * w for _ in range(h)]

        for y in range(h):
            for x in range(w):
                max_v = -float("inf")
                for dx, dy in offsets:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        v = grid[ny][nx]
                        if v > max_v:
                            max_v = v
                out[y][x] = max(0.0, max_v)
        return out

    @classmethod
    def erode(cls, img: Any, size: int = 3, shape: str = "rect") -> List[List[float]]:
        """Morphological erosion (minimum filter within kernel)."""
        grid, w, h = _to_gray_grid(img)
        offsets = cls._get_structuring_element(shape, size)
        out = [[0.0] * w for _ in range(h)]

        for y in range(h):
            for x in range(w):
                min_v = float("inf")
                for dx, dy in offsets:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        v = grid[ny][nx]
                        if v < min_v:
                            min_v = v
                out[y][x] = min_v if min_v != float("inf") else 0.0
        return out

    @classmethod
    def open(cls, img: Any, size: int = 3, shape: str = "rect") -> List[List[float]]:
        """Morphological opening (erosion followed by dilation)."""
        return cls.dilate(cls.erode(img, size, shape), size, shape)

    @classmethod
    def close(cls, img: Any, size: int = 3, shape: str = "rect") -> List[List[float]]:
        """Morphological closing (dilation followed by erosion)."""
        return cls.erode(cls.dilate(img, size, shape), size, shape)

    @classmethod
    def gradient(cls, img: Any, size: int = 3, shape: str = "rect") -> List[List[float]]:
        """Morphological gradient (dilation minus erosion)."""
        dil = cls.dilate(img, size, shape)
        ero = cls.erode(img, size, shape)
        h = len(dil)
        w = len(dil[0]) if h > 0 else 0
        return [[round(max(0.0, dil[y][x] - ero[y][x]), 2) for x in range(w)] for y in range(h)]


class ColorQuantizer:
    """Median Cut color palette reduction and Floyd-Steinberg error diffusion dithering."""

    @classmethod
    def median_cut(cls, pixels_rgb: List[Tuple[int, int, int]], num_colors: int = 16) -> List[Tuple[int, int, int]]:
        """Reduces RGB color space to `num_colors` representative palette using Median Cut."""
        if not pixels_rgb:
            return [(0, 0, 0)]
        boxes = [list(pixels_rgb)]

        while len(boxes) < num_colors:
            # Pick box with largest color channel spread
            best_idx = -1
            best_spread = -1
            best_channel = 0

            for idx, box in enumerate(boxes):
                if len(box) <= 1:
                    continue
                min_r = min(p[0] for p in box)
                max_r = max(p[0] for p in box)
                min_g = min(p[1] for p in box)
                max_g = max(p[1] for p in box)
                min_b = min(p[2] for p in box)
                max_b = max(p[2] for p in box)

                spread_r = max_r - min_r
                spread_g = max_g - min_g
                spread_b = max_b - min_b
                max_s = max(spread_r, spread_g, spread_b)

                if max_s > best_spread:
                    best_spread = max_s
                    best_idx = idx
                    if max_s == spread_r:
                        best_channel = 0
                    elif max_s == spread_g:
                        best_channel = 1
                    else:
                        best_channel = 2

            if best_idx == -1 or best_spread == 0:
                break

            target_box = boxes.pop(best_idx)
            target_box.sort(key=lambda p: p[best_channel])
            mid = len(target_box) // 2
            boxes.append(target_box[:mid])
            boxes.append(target_box[mid:])

        palette = []
        for box in boxes:
            if not box:
                continue
            r_avg = sum(p[0] for p in box) // len(box)
            g_avg = sum(p[1] for p in box) // len(box)
            b_avg = sum(p[2] for p in box) // len(box)
            palette.append((r_avg, g_avg, b_avg))

        return palette

    @classmethod
    def dither_floyd_steinberg(
        cls,
        image_rgb: List[List[Tuple[int, int, int]]],
        palette: List[Tuple[int, int, int]],
    ) -> List[List[Tuple[int, int, int]]]:
        """Floyd-Steinberg 2D error diffusion dithering."""
        h = len(image_rgb)
        w = len(image_rgb[0]) if h > 0 else 0

        # Mutable float buffer
        buf = [[[float(c) for c in image_rgb[y][x]] for x in range(w)] for y in range(h)]
        out = [[(0, 0, 0)] * w for _ in range(h)]

        for y in range(h):
            for x in range(w):
                old_r, old_g, old_b = buf[y][x]
                old_r = max(0.0, min(255.0, old_r))
                old_g = max(0.0, min(255.0, old_g))
                old_b = max(0.0, min(255.0, old_b))

                # Find nearest palette color
                best_color = palette[0]
                best_dist = float("inf")
                for pr, pg, pb in palette:
                    dist = (old_r - pr) ** 2 + (old_g - pg) ** 2 + (old_b - pb) ** 2
                    if dist < best_dist:
                        best_dist = dist
                        best_color = (pr, pg, pb)

                out[y][x] = best_color
                er = old_r - best_color[0]
                eg = old_g - best_color[1]
                eb = old_b - best_color[2]

                # Distribute error to 4 neighbors:
                # (x+1, y): 7/16, (x-1, y+1): 3/16, (x, y+1): 5/16, (x+1, y+1): 1/16
                if x + 1 < w:
                    buf[y][x + 1][0] += er * (7.0 / 16.0)
                    buf[y][x + 1][1] += eg * (7.0 / 16.0)
                    buf[y][x + 1][2] += eb * (7.0 / 16.0)
                if y + 1 < h:
                    if x - 1 >= 0:
                        buf[y + 1][x - 1][0] += er * (3.0 / 16.0)
                        buf[y + 1][x - 1][1] += eg * (3.0 / 16.0)
                        buf[y + 1][x - 1][2] += eb * (3.0 / 16.0)
                    buf[y + 1][x][0] += er * (5.0 / 16.0)
                    buf[y + 1][x][1] += eg * (5.0 / 16.0)
                    buf[y + 1][x][2] += eb * (5.0 / 16.0)
                    if x + 1 < w:
                        buf[y + 1][x + 1][0] += er * (1.0 / 16.0)
                        buf[y + 1][x + 1][1] += eg * (1.0 / 16.0)
                        buf[y + 1][x + 1][2] += eb * (1.0 / 16.0)

        return out


def image_warp_affine(
    img: Any,
    translation: Tuple[float, float] = (0.0, 0.0),
    rotation_deg: float = 0.0,
    scale: Tuple[float, float] = (1.0, 1.0),
) -> List[List[float]]:
    """Warps image using affine transformation with bilinear interpolation."""
    mat = GeometricWarp.affine_matrix(translation, rotation_deg, scale)
    return GeometricWarp.warp(img, mat)


def image_morphology(img: Any, operation: str = "dilate", size: int = 3, shape: str = "rect") -> List[List[float]]:
    """Applies morphological operator: dilate, erode, open, close, gradient."""
    op = operation.strip().lower()
    if op == "dilate":
        return MorphologicalOps.dilate(img, size, shape)
    elif op == "erode":
        return MorphologicalOps.erode(img, size, shape)
    elif op == "open":
        return MorphologicalOps.open(img, size, shape)
    elif op == "close":
        return MorphologicalOps.close(img, size, shape)
    elif op == "gradient":
        return MorphologicalOps.gradient(img, size, shape)
    raise ValueError(f"Unknown morphological operation: {operation}")


def image_quantize_palette(pixels_rgb: List[Tuple[int, int, int]], num_colors: int = 16) -> List[Tuple[int, int, int]]:
    """Extracts optimal discrete color palette using median-cut."""
    return ColorQuantizer.median_cut(pixels_rgb, num_colors)



