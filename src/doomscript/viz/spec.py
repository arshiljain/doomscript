"""Typed Plot Specification Intermediate Representation (IR).

Pure Python dataclasses representing visual Grammar of Graphics intent
without requiring lets-plot or graphical backends to be imported.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


@dataclass
class AestheticMapping:
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    fill: Optional[str] = None
    size: Optional[str] = None
    shape: Optional[str] = None
    alpha: Optional[str] = None
    group: Optional[str] = None
    weight: Optional[str] = None
    slice: Optional[str] = None
    value: Optional[str] = None


@dataclass
class LayerSpec:
    geom: str
    mapping: Optional[AestheticMapping] = None
    stat: Optional[str] = None
    position: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FacetSpec:
    type: str = "wrap"  # "wrap" | "grid"
    facets: Optional[Union[str, List[str]]] = None
    row: Optional[str] = None
    col: Optional[str] = None
    scales: str = "fixed"


@dataclass
class ThemeSpec:
    name: str = "minimal"  # "minimal", "classic", "bw", "light", "void", "grey", "dark"
    legend_position: str = "right"
    dark_mode: bool = False


@dataclass
class ScaleSpec:
    target: str  # "x", "y", "color", "fill"
    type: str  # "log", "reverse", "palette", "continuous", "discrete"
    palette_name: Optional[str] = None


@dataclass
class LabelSpec:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    caption: Optional[str] = None
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    fill: Optional[str] = None


@dataclass
class AnnotationSpec:
    text: str
    x: Any
    y: Any
    color: Optional[str] = None
    size: Optional[float] = None
    alpha: Optional[float] = None


@dataclass
class PlotSpec:
    data: Any
    mapping: AestheticMapping = field(default_factory=AestheticMapping)
    layers: List[LayerSpec] = field(default_factory=list)
    facet: Optional[FacetSpec] = None
    theme: ThemeSpec = field(default_factory=ThemeSpec)
    scales: List[ScaleSpec] = field(default_factory=list)
    labels: LabelSpec = field(default_factory=LabelSpec)
    annotations: List[AnnotationSpec] = field(default_factory=list)
