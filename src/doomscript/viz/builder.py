"""PlotBuilder API.

Fluent, declarative construction API for Grammar of Graphics visualizations.
Produces a validated PlotSpec IR.
"""

from typing import Any, Dict, List, Optional, Union
from doomscript.viz.spec import (
    PlotSpec,
    AestheticMapping,
    LayerSpec,
    FacetSpec,
    ThemeSpec,
    ScaleSpec,
    LabelSpec,
    AnnotationSpec,
)


GEOM_ALIASES = {
    "scatter": "point",
    "points": "point",
    "point": "point",
    "line": "line",
    "lines": "line",
    "bar": "bar",
    "bars": "bar",
    "column": "bar",
    "columns": "bar",
    "histogram": "histogram",
    "density": "density",
    "boxplot": "boxplot",
    "box": "boxplot",
    "violin": "violin",
    "area": "area",
    "tile": "tile",
    "tiles": "tile",
    "heatmap": "tile",
    "pie": "pie",
    "smooth": "smooth",
    "trend": "smooth",
    "trend line": "smooth",
    "text": "text",
    "errorbar": "errorbar",
}


def _check_is_numeric_col(data: Any, col: str) -> bool:
    """Helper to check if a column in data contains numeric values."""
    if not col:
        return False
    # If pandas DataFrame
    if hasattr(data, "columns") and col in data.columns:
        import numpy as np

        dtype = str(data[col].dtype).lower()
        return "int" in dtype or "float" in dtype or "number" in dtype
    # If list of dicts
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        for row in data:
            val = row.get(col)
            if val is not None:
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    return True
                else:
                    return False
    # If dict of lists
    if isinstance(data, dict) and col in data:
        vals = data[col]
        for val in vals:
            if val is not None:
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    return True
                else:
                    return False
    return True


class PlotBuilder:
    """Fluent construction API for Grammar-of-Graphics plots."""

    def __init__(self, data: Any, title: Optional[str] = None):
        self._data = data
        self._mapping = AestheticMapping()
        self._layers: List[LayerSpec] = []
        self._facet: Optional[FacetSpec] = None
        self._theme = ThemeSpec()
        self._scales: List[ScaleSpec] = []
        self._labels = LabelSpec(title=title)
        self._annotations: List[AnnotationSpec] = []

    # -----------------------------------------------------------------------
    # Aesthetic Mappings
    # -----------------------------------------------------------------------

    def map(self, aes_name: str, col_name: str) -> "PlotBuilder":
        aes = aes_name.lower().strip()
        col = str(col_name) if col_name is not None else None
        if aes == "x":
            self._mapping.x = col
        elif aes == "y":
            self._mapping.y = col
        elif aes in ("color", "colour"):
            self._mapping.color = col
        elif aes == "fill":
            self._mapping.fill = col
        elif aes == "size":
            self._mapping.size = col
        elif aes == "shape":
            self._mapping.shape = col
        elif aes == "alpha":
            self._mapping.alpha = col
        elif aes == "group":
            self._mapping.group = col
        elif aes == "weight":
            self._mapping.weight = col
        elif aes == "slice":
            self._mapping.slice = col
        elif aes == "value":
            self._mapping.value = col
        else:
            setattr(self._mapping, aes, col)
        return self

    def map_x(self, col: str) -> "PlotBuilder":
        return self.map("x", col)

    def map_y(self, col: str) -> "PlotBuilder":
        return self.map("y", col)

    def map_color(self, col: str) -> "PlotBuilder":
        return self.map("color", col)

    def map_fill(self, col: str) -> "PlotBuilder":
        return self.map("fill", col)

    def map_size(self, col: str) -> "PlotBuilder":
        return self.map("size", col)

    # -----------------------------------------------------------------------
    # Layers & Geometry
    # -----------------------------------------------------------------------

    def draw(
        self,
        geom: str,
        mapping: Optional[AestheticMapping] = None,
        stat: Optional[str] = None,
        position: Optional[str] = None,
        **params,
    ) -> "PlotBuilder":
        norm_geom = GEOM_ALIASES.get(geom.lower().strip(), geom.lower().strip())
        layer = LayerSpec(
            geom=norm_geom,
            mapping=mapping,
            stat=stat,
            position=position,
            params=params,
        )
        self._layers.append(layer)
        return self

    # -----------------------------------------------------------------------
    # Level 2 Kind Shortcut
    # -----------------------------------------------------------------------

    def kind(self, geom_type: str, **kwargs) -> "PlotBuilder":
        """Configures aesthetics and adds primary layer in one call."""
        layer_params = {}
        for k, v in kwargs.items():
            k_lower = k.lower()
            if k_lower in (
                "x",
                "y",
                "color",
                "colour",
                "fill",
                "size",
                "shape",
                "alpha",
                "group",
                "slice",
                "value",
            ):
                self.map(k_lower, v)
            elif k_lower == "title":
                self.title(v)
            elif k_lower == "theme":
                self.theme(v)
            else:
                layer_params[k] = v

        norm_geom = GEOM_ALIASES.get(
            geom_type.lower().strip(), geom_type.lower().strip()
        )
        return self.draw(norm_geom, **layer_params)

    # -----------------------------------------------------------------------
    # Facets, Scales, Themes, Labels
    # -----------------------------------------------------------------------

    def facet(
        self,
        facets: Optional[Union[str, List[str]]] = None,
        type: str = "wrap",
        row: Optional[str] = None,
        col: Optional[str] = None,
        scales: str = "fixed",
    ) -> "PlotBuilder":
        self._facet = FacetSpec(
            type=type, facets=facets, row=row, col=col, scales=scales
        )
        return self

    def title(self, title_text: str) -> "PlotBuilder":
        self._labels.title = title_text
        return self

    def labels(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        caption: Optional[str] = None,
        x: Optional[str] = None,
        y: Optional[str] = None,
        color: Optional[str] = None,
        fill: Optional[str] = None,
    ) -> "PlotBuilder":
        if title:
            self._labels.title = title
        if subtitle:
            self._labels.subtitle = subtitle
        if caption:
            self._labels.caption = caption
        if x:
            self._labels.x = x
        if y:
            self._labels.y = y
        if color:
            self._labels.color = color
        if fill:
            self._labels.fill = fill
        return self

    def theme(
        self,
        name: str = "minimal",
        dark: bool = False,
        legend: str = "right",
    ) -> "PlotBuilder":
        clean_name = name.lower().strip()
        if clean_name == "dark":
            dark = True
            clean_name = "dark"
        self._theme = ThemeSpec(name=clean_name, dark_mode=dark, legend_position=legend)
        return self

    def scale(
        self,
        target: str,
        type: str,
        palette: Optional[str] = None,
    ) -> "PlotBuilder":
        self._scales.append(
            ScaleSpec(target=target, type=type, palette_name=palette)
        )
        return self

    def annotate(
        self,
        text: str,
        x: Any,
        y: Any,
        color: Optional[str] = None,
        size: Optional[float] = None,
        alpha: Optional[float] = None,
    ) -> "PlotBuilder":
        self._annotations.append(
            AnnotationSpec(text=text, x=x, y=y, color=color, size=size, alpha=alpha)
        )
        return self

    # -----------------------------------------------------------------------
    # Validation & IR Generation
    # -----------------------------------------------------------------------

    def spec(self) -> PlotSpec:
        """Validates all visual mappings and layer constraints, returning the PlotSpec IR."""
        if not self._layers:
            # Default to scatter if x and y mapped, or line if temporal
            if self._mapping.x and self._mapping.y:
                self.draw("point")
            elif self._mapping.x:
                self.draw("bar")
            else:
                raise ValueError("Plot has no geometry layers and no aesthetic mappings.")

        # Validate each layer against semantics
        for layer in self._layers:
            g = layer.geom
            # Effective mappings
            eff_x = (layer.mapping.x if layer.mapping and layer.mapping.x else self._mapping.x)
            eff_y = (layer.mapping.y if layer.mapping and layer.mapping.y else self._mapping.y)
            eff_fill = (layer.mapping.fill if layer.mapping and layer.mapping.fill else self._mapping.fill)
            eff_slice = (layer.mapping.slice if layer.mapping and layer.mapping.slice else self._mapping.slice)
            eff_value = (layer.mapping.value if layer.mapping and layer.mapping.value else self._mapping.value)

            if g == "point":
                if not eff_x or not eff_y:
                    raise ValueError("Scatter/point plot requires both 'x' and 'y' aesthetics.")
            elif g == "line":
                if not eff_x or not eff_y:
                    raise ValueError("Line plot requires both 'x' and 'y' aesthetics.")
            elif g == "bar":
                if not eff_x:
                    raise ValueError("Bar plot requires an 'x' aesthetic.")
                if layer.stat is None:
                    layer.stat = "identity" if eff_y else "count"
            elif g in ("histogram", "density"):
                if not eff_x:
                    raise ValueError(f"{g.capitalize()} requires an 'x' aesthetic.")
                if not _check_is_numeric_col(self._data, eff_x):
                    raise ValueError(
                        f"Histogram requires numeric values on x-axis, but '{eff_x}' is text. "
                        "Did you mean to use a bar chart?"
                    )
                if layer.stat is None:
                    layer.stat = "bin" if g == "histogram" else "density"
            elif g in ("boxplot", "violin"):
                if not eff_y:
                    raise ValueError(f"Boxplot requires 'y' aesthetic (the continuous metric).")
            elif g == "tile":
                if not eff_x or not eff_y or not eff_fill:
                    raise ValueError("Heatmap/tile requires 'x', 'y', and 'fill' aesthetics.")
            elif g == "pie":
                if not eff_slice or not eff_value:
                    raise ValueError("Pie chart requires both 'slice' (categories) and 'value' (magnitudes).")
            elif g == "area":
                if not eff_x or not eff_y:
                    raise ValueError("Area chart requires both 'x' and 'y' aesthetics.")
            elif g == "smooth":
                if not eff_x or not eff_y:
                    raise ValueError("Smooth trend line requires both 'x' and 'y' aesthetics.")

        return PlotSpec(
            data=self._data,
            mapping=self._mapping,
            layers=self._layers,
            facet=self._facet,
            theme=self._theme,
            scales=self._scales,
            labels=self._labels,
            annotations=self._annotations,
        )

    # -----------------------------------------------------------------------
    # Execution & Display Bridge
    # -----------------------------------------------------------------------

    def show(self):
        """Renders and displays the plot in the active environment."""
        from doomscript.viz.renderer import LetsPlotRenderer

        return LetsPlotRenderer.show(self.spec())

    def save(self, path: str, width: Optional[int] = None, height: Optional[int] = None, dpi: Optional[int] = None):
        """Saves the plot to an HTML, PNG, SVG, or PDF file."""
        from doomscript.viz.renderer import LetsPlotRenderer

        return LetsPlotRenderer.save(self.spec(), path, width=width, height=height, dpi=dpi)

    def to_html(self) -> str:
        """Returns standalone HTML representation."""
        from doomscript.viz.renderer import LetsPlotRenderer

        return LetsPlotRenderer.to_html(self.spec())
