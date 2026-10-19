"""Unit and integration tests for composable Grammar of Graphics visualization.

Tests multi-layer plots, facets, annotations, scale transformations,
and native Python AST export parity.
"""

import ast
import pytest
from doomscript.compiler.engine import execute, transpile
from doomscript.viz.spec import PlotSpec, AnnotationSpec
from doomscript.viz.builder import PlotBuilder
from doomscript.viz.exporter import LetsPlotExporter


def test_builder_with_annotations_and_scales():
    data = [{"x": 1, "y": 10}, {"x": 2, "y": 20}]
    b = (
        PlotBuilder(data, title="Annotated Plot")
        .map_x("x")
        .map_y("y")
        .draw("line")
        .draw("point", size=3)
        .annotate("Peak", x=2, y=20, color="red")
        .scale("y", "log")
        .facet("category")
    )
    spec = b.spec()
    assert len(spec.layers) == 2
    assert len(spec.annotations) == 1
    assert spec.annotations[0].text == "Peak"
    assert spec.annotations[0].x == 2
    assert spec.annotations[0].y == 20
    assert spec.annotations[0].color == "red"
    assert spec.facet.facets == "category"
    assert any(s.target == "y" and s.type == "log" for s in spec.scales)


def test_lets_plot_exporter_includes_annotations_and_facets():
    data = [{"x": 1, "y": 10}]
    b = (
        PlotBuilder("df")
        .map_x("x")
        .map_y("y")
        .draw("point")
        .annotate("Target", x=1, y=10, color="blue")
        .facet("grp")
    )
    spec = b.spec()
    exporter = LetsPlotExporter()
    imports, assign_node = exporter.to_ast(spec, var_name="p")

    assert "geom_text" in imports
    assert "facet_wrap" in imports

    py_code = exporter.to_python(spec, var_name="p")
    assert "geom_text(" in py_code
    assert 'label="Target"' in py_code or "label='Target'" in py_code
    assert "facet_wrap(" in py_code
    ast.parse(py_code)


def test_english_chart_block_with_annotation():
    code = """
data = [{"x": 1, "y": 10}, {"x": 2, "y": 30}]
chart "Performance" from data into p:
    map x to x
    map y to y
    draw line
    draw point
    annotate "Record High" at x=2, y=30 with color="red"
    scale y as log

spec = p.spec()
"""
    scope = {}
    execute(code, scope)
    assert "spec" in scope
    spec: PlotSpec = scope["spec"]
    assert len(spec.annotations) == 1
    assert spec.annotations[0].text == "Record High"
    assert spec.annotations[0].x == 2
    assert spec.annotations[0].y == 30
    assert spec.annotations[0].color == "red"
    assert any(s.target == "y" and s.type == "log" for s in spec.scales)
