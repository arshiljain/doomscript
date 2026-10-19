"""Declarative specifications and Intermediate Representation for the Image & Vision domain."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from doomscript.domains.base import DomainIR


@dataclass
class ImageOpenSpec(DomainIR):
    """Specification for loading an image file."""

    path_expr: str
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if not self.path_expr:
            errors.append("ImageOpenSpec requires a file path")
        if not self.target_var:
            errors.append("ImageOpenSpec requires a target variable")
        return errors


@dataclass
class ImageCreateSpec(DomainIR):
    """Specification for creating a new blank image canvas."""

    width: int
    height: int
    color: str = "white"
    target_var: str = "canvas"

    def validate(self) -> List[str]:
        errors = []
        if self.width <= 0 or self.height <= 0:
            errors.append("Image dimensions must be positive integers")
        return errors


@dataclass
class ImageResizeSpec(DomainIR):
    """Specification for resizing an image by explicit dimensions or percentage."""

    image_var: str
    target_var: str
    width: Optional[int] = None
    height: Optional[int] = None
    percent: Optional[float] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.image_var:
            errors.append("ImageResizeSpec requires a source image variable")
        if self.percent is None and (self.width is None or self.height is None):
            errors.append("ImageResizeSpec requires either percent or both width and height")
        return errors


@dataclass
class ImageCropSpec(DomainIR):
    """Specification for cropping an image to a bounding box."""

    image_var: str
    x1: int
    y1: int
    x2: int
    y2: int
    target_var: str

    def validate(self) -> List[str]:
        errors = []
        if self.x2 <= self.x1 or self.y2 <= self.y1:
            errors.append("Crop bounds must satisfy x2 > x1 and y2 > y1")
        return errors


@dataclass
class ImageRotateSpec(DomainIR):
    """Specification for rotating an image by degrees."""

    image_var: str
    angle: float
    target_var: str

    def validate(self) -> List[str]:
        return []


@dataclass
class ImageFilterSpec(DomainIR):
    """Specification for applying a visual filter or adjustment to an image."""

    image_var: str
    filter_name: str
    target_var: str
    radius: Optional[float] = None

    def validate(self) -> List[str]:
        errors = []
        valid_filters = {"grayscale", "blur", "sharpen", "contour", "invert"}
        if self.filter_name.lower() not in valid_filters:
            errors.append(f"Unknown image filter '{self.filter_name}'. Valid: {', '.join(valid_filters)}")
        return errors


@dataclass
class ImageSaveSpec(DomainIR):
    """Specification for saving an image to disk."""

    image_var: str
    path_expr: str
    quality: Optional[int] = None

    def validate(self) -> List[str]:
        errors = []
        if not self.path_expr:
            errors.append("ImageSaveSpec requires a destination file path")
        return errors
