"""Image & Vision Domain Pack for DoomScript."""

import re
from doomscript.domains.base import DomainContract
from doomscript.domains.image.spec import (
    ImageOpenSpec,
    ImageCreateSpec,
    ImageResizeSpec,
    ImageCropSpec,
    ImageRotateSpec,
    ImageFilterSpec,
    ImageSaveSpec,
)
from doomscript.domains.image.parser import ImageDomainParser
from doomscript.domains.image.runtime import (
    DoomImage,
    ImageRuntime,
    open_image,
    create_blank_image,
    image_dimensions,
    image_width,
    image_height,
    resize_image,
    crop_image,
    rotate_image,
    flip_image,
    filter_image,
    adjust_image,
    draw_on_image,
    save_image,
    execute_image_ir,
)
from doomscript.domains.image.exporter import ImageASTExporter
from doomscript.domains.registry import get_domain_registry


class ImageDomain(DomainContract):
    """Image & Computer Vision domain pack."""

    name = "image"
    aliases = ["vision", "media", "img"]
    parser = ImageDomainParser()
    runtime = ImageRuntime()
    exporter = ImageASTExporter()

    def can_handle_line(self, line: str) -> bool:
        s = line.strip().lower()
        if (
            s.startswith("open image ")
            or s.startswith("create blank image ")
            or s.startswith("dimensions of ")
            or s.startswith("width of ")
            or s.startswith("height of ")
            or s.startswith("rotate image ")
            or s.startswith("flip image ")
            or s.startswith("crop image ")
            or s.startswith("resize image ")
            or s.startswith("apply grayscale ")
            or s.startswith("apply blur ")
            or s.startswith("apply sharpen ")
            or s.startswith("apply contour ")
            or s.startswith("apply invert ")
            or s.startswith("adjust brightness ")
            or s.startswith("adjust contrast ")
            or s.startswith("save image ")
        ):
            return True

        if s.startswith("resize ") and ("width" in s or "percent" in s):
            return True
        if s.startswith("crop ") and "from" in s and "to" in s:
            return True
        if s.startswith("rotate ") and "degree" in s:
            return True
        if s.startswith("flip ") and ("horizontally" in s or "vertically" in s):
            return True
        if s.startswith("draw text ") and " on " in s:
            return True

        from doomscript.domains.registry import get_domain_registry
        if get_domain_registry().is_active("image"):
            if s.startswith("save ") and ("image" in s or "img" in s):
                return True

        return False

    def can_handle_block(self, header: str) -> bool:
        return False


# Register with central registry
IMAGE_DOMAIN = ImageDomain()
get_domain_registry().register(IMAGE_DOMAIN)

__all__ = [
    "ImageDomain",
    "IMAGE_DOMAIN",
    "ImageOpenSpec",
    "ImageCreateSpec",
    "ImageResizeSpec",
    "ImageCropSpec",
    "ImageRotateSpec",
    "ImageFilterSpec",
    "ImageSaveSpec",
    "ImageDomainParser",
    "ImageRuntime",
    "ImageASTExporter",
    "DoomImage",
    "open_image",
    "create_blank_image",
    "image_dimensions",
    "image_width",
    "image_height",
    "resize_image",
    "crop_image",
    "rotate_image",
    "flip_image",
    "filter_image",
    "adjust_image",
    "draw_on_image",
    "save_image",
    "execute_image_ir",
]
