"""Geospatial Analytics Domain Specification and Intermediate Representation (IR)."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from doomscript.domains.base import DomainIR


@dataclass
class GeoPointSpec(DomainIR):
    """Specification for creating a geographic point."""

    lat_expr: str
    lon_expr: str
    target_var: str = "pt"

    def validate(self) -> List[str]:
        errors = []
        if not self.lat_expr or not self.lon_expr:
            errors.append("Latitude and Longitude expressions cannot be empty")
        return errors


@dataclass
class GeoPolygonSpec(DomainIR):
    """Specification for creating a geographic polygon from coordinate rings."""

    coords_expr: str
    target_var: str = "poly"

    def validate(self) -> List[str]:
        errors = []
        if not self.coords_expr:
            errors.append("Coordinates expression cannot be empty")
        return errors


@dataclass
class GeoDistanceSpec(DomainIR):
    """Specification for great-circle distance calculation between two points."""

    p1_expr: str
    p2_expr: str
    unit: str = "km"  # km, miles, meters
    target_var: str = "dist"

    def validate(self) -> List[str]:
        errors = []
        if not self.p1_expr or not self.p2_expr:
            errors.append("Both points must be specified for distance calculation")
        return errors


@dataclass
class GeoContainmentSpec(DomainIR):
    """Specification for point-in-polygon containment test."""

    point_expr: str
    polygon_expr: str
    target_var: str = "is_inside"

    def validate(self) -> List[str]:
        errors = []
        if not self.point_expr or not self.polygon_expr:
            errors.append("Point and polygon expressions must be specified")
        return errors


@dataclass
class GeoBoundingBoxSpec(DomainIR):
    """Specification for computing minimum bounding box across points or geometries."""

    geom_expr: str
    target_var: str = "bbox"

    def validate(self) -> List[str]:
        errors = []
        if not self.geom_expr:
            errors.append("Geometry expression cannot be empty")
        return errors


@dataclass
class GeoSpatialJoinSpec(DomainIR):
    """Specification for spatial join matching points inside polygons."""

    points_expr: str
    polygons_expr: str
    target_var: str = "spatial_matches"

    def validate(self) -> List[str]:
        errors = []
        if not self.points_expr or not self.polygons_expr:
            errors.append("Points and polygons must be specified for spatial join")
        return errors
