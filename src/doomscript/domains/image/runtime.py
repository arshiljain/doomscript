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


def create_blank_image(width: int, height: int, color: str = "white") -> DoomImage:
    if HAS_PIL:
        raw = PILImage.new("RGB", (int(width), int(height)), color=color)
    else:
        raw = PureImage(int(width), int(height), color=color)
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
