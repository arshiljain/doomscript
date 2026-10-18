"""Unit tests for Typed Plot Specification IR and PlotBuilder API."""

import pytest
from doomscript.viz.spec import (
    PlotSpec,
    AestheticMapping,
    LayerSpec,
    FacetSpec,
    ThemeSpec,
    ScaleSpec,
    LabelSpec,
)
from doomscript.viz.builder import PlotBuilder


def test_builder_constructs_valid_scatter_spec():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    b = (
        PlotBuilder(data, title="My Scatter")
        .map_x("a")
        .map_y("b")
        .draw("scatter", size=3, alpha=0.8)
        .theme("minimal")
    )
    spec = b.spec()
    assert spec.data == data
    assert spec.mapping.x == "a"
    assert spec.mapping.y == "b"
    assert len(spec.layers) == 1
    assert spec.layers[0].geom == "point"
    assert spec.layers[0].params == {"size": 3, "alpha": 0.8}
    assert spec.labels.title == "My Scatter"
    assert spec.theme.name == "minimal"


def test_bar_geometry_stat_rules():
    data = [{"cat": "A", "val": 10}, {"cat": "B", "val": 20}]
    # x only -> count
    b1 = PlotBuilder(data).map_x("cat").draw("bar")
    assert b1.spec().layers[0].stat == "count"

    # x and y -> identity
    b2 = PlotBuilder(data).map_x("cat").map_y("val").draw("bar")
    assert b2.spec().layers[0].stat == "identity"


def test_missing_required_aesthetic_validation():
    data = [{"cat": "A"}]
    b = PlotBuilder(data).map_x("cat").draw("scatter")
    with pytest.raises(ValueError, match="Scatter/point plot requires both 'x' and 'y'"):
        b.spec()

    # Boxplot requires y
    b2 = PlotBuilder(data).map_x("cat").draw("boxplot")
    with pytest.raises(ValueError, match="Boxplot requires 'y' aesthetic"):
        b2.spec()

    # Heatmap requires x, y, and fill
    b3 = PlotBuilder(data).map_x("a").map_y("b").draw("tile")
    with pytest.raises(ValueError, match="Heatmap/tile requires 'x', 'y', and 'fill'"):
        b3.spec()


def test_histogram_numeric_validation():
    # If data is provided as dict of lists or list of dicts, check categorical detection
    data = [{"name": "Alice"}, {"name": "Bob"}]
    b = PlotBuilder(data).map_x("name").draw("histogram")
    with pytest.raises(ValueError, match="Histogram requires numeric values on x-axis"):
        b.spec()


def test_pie_geometry_rules():
    data = [{"category": "Tech", "share": 45}]
    b = PlotBuilder(data).map("slice", "category").map("value", "share").draw("pie")
    spec = b.spec()
    assert spec.layers[0].geom == "pie"
    assert spec.mapping.slice == "category"
    assert spec.mapping.value == "share"


def test_kind_shortcut_level2():
    data = [{"month": "Jan", "revenue": 100, "region": "North"}]
    b = (
        PlotBuilder(data)
        .kind("line", x="month", y="revenue", color="region")
        .title("Revenue Trend")
        .theme("classic")
    )
    spec = b.spec()
    assert spec.mapping.x == "month"
    assert spec.mapping.y == "revenue"
    assert spec.mapping.color == "region"
    assert spec.layers[0].geom == "line"
    assert spec.labels.title == "Revenue Trend"
    assert spec.theme.name == "classic"


def test_composition_level3():
    data = [{"x": 1, "y": 2, "g": "A"}]
    b = (
        PlotBuilder(data)
        .map_x("x")
        .map_y("y")
        .map_color("g")
        .draw("line")
        .draw("points", size=2)
        .draw("smooth")
        .facet("g")
        .labels(x="X Axis", y="Y Axis", caption="Note")
        .scale("color", "palette", palette="viridis")
        .theme("dark")
    )
    spec = b.spec()
    assert len(spec.layers) == 3
    assert [l.geom for l in spec.layers] == ["line", "point", "smooth"]
    assert spec.facet is not None
    assert spec.facet.facets == "g"
    assert spec.labels.x == "X Axis"
    assert spec.scales[0].palette_name == "viridis"
    assert spec.theme.name == "dark"
