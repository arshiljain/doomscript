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
from doomscript.domains.matcher import VerbSpec
from doomscript.domains.image.exporter import ImageASTExporter
from doomscript.domains.registry import get_domain_registry


class ImageDomain(DomainContract):
    """Image & Computer Vision domain pack."""

    name = "image"
    aliases = ["vision", "media", "img"]
    description = "Image processing, resizing, cropping, rotation, filters, and formats"
    parser = ImageDomainParser()
    runtime = ImageRuntime()
    exporter = ImageASTExporter()
    capabilities = ["image", "resize", "crop", "rotate", "filters", "drawing"]
    optional_dependencies = ["Pillow", "opencv-python"]

    verbs = [
        VerbSpec(
            name="open_image",
            pattern="open image {path_expr:expr} into {target:ident}",
            arg_schema={"path_expr": "expr", "target": "ident"},
            returns="Image",
            description="Open and decode bitmap or vector image from disk",
        ),
        VerbSpec(
            name="create_blank_image",
            pattern="create blank image of {width:int} by {height:int} [with color {color:expr}] into {target:ident}",
            arg_schema={"width": "int", "height": "int", "target": "ident"},
            returns="Image",
            description="Create new empty raster canvas",
        ),
        VerbSpec(
            name="resize_image",
            pattern="resize image {img_var:ident} to {width:int} by {height:int} into {target:ident}",
            arg_schema={"img_var": "ident", "width": "int", "height": "int", "target": "ident"},
            returns="Image",
            description="Scale image dimensions using bilinear interpolation",
        ),
        VerbSpec(
            name="crop_image",
            pattern="crop image {img_var:ident} to {coords:expr} into {target:ident}",
            arg_schema={"img_var": "ident", "coords": "expr", "target": "ident"},
            returns="Image",
            description="Crop bounding box rectangle from image",
        ),
        VerbSpec(
            name="rotate_image",
            pattern="rotate image {img_var:ident} by {deg:expr} [degrees] into {target:ident}",
            arg_schema={"img_var": "ident", "deg": "expr", "target": "ident"},
            returns="Image",
            description="Rotate image clockwise by angle degrees",
        ),
        VerbSpec(
            name="apply_filter",
            pattern="apply (grayscale|blur|sharpen) to [image] {img_var:ident} into {target:ident}",
            arg_schema={"img_var": "ident", "target": "ident"},
            returns="Image",
            description="Apply convolution or color transform filter",
        ),
        VerbSpec(
            name="save_image",
            pattern="save image {img_var:ident} to {path:expr}",
            arg_schema={"img_var": "ident", "path": "expr"},
            returns="str",
            description="Write encoded image to disk as PNG or JPEG",
        ),
    ]

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
