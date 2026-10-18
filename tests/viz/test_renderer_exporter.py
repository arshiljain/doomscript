"""Unit tests for Lets-Plot Renderer and Native Python Exporter."""

import os
import pytest
from doomscript.viz.builder import PlotBuilder
from doomscript.viz.exporter import LetsPlotExporter
from doomscript.viz.renderer import LetsPlotRenderer


def test_exporter_emits_native_lets_plot_code():
    data = [{"month": "Jan", "revenue": 100, "region": "North"}]
    b = (
        PlotBuilder("sales")
        .map_x("month")
        .map_y("revenue")
        .map_color("region")
        .draw("line")
        .draw("scatter", size=3)
        .theme("minimal")
    )
    py_code = LetsPlotExporter().to_python(b.spec(), var_name="revenue_plot")
    assert "from lets_plot import" in py_code
    assert "ggplot" in py_code
    assert "geom_line" in py_code
    assert "geom_point" in py_code
    assert "theme_minimal" in py_code
    assert 'revenue_plot = (ggplot(sales, aes(x="month", y="revenue", color="region"))' in py_code
    assert "+ geom_line()" in py_code
    assert "+ geom_point(size=3)" in py_code
    assert "+ theme_minimal()" in py_code


def test_renderer_builds_lets_plot_and_generates_html(tmp_path):
    data = [
        {"x": 1, "y": 10, "cat": "A"},
        {"x": 2, "y": 20, "cat": "B"},
        {"x": 3, "y": 15, "cat": "A"},
    ]
    b = (
        PlotBuilder(data, title="Test Plot")
        .map_x("x")
        .map_y("y")
        .map_color("cat")
        .draw("line")
        .draw("point")
        .theme("minimal")
    )

    spec = b.spec()
    lp_fig = LetsPlotRenderer.to_lets_plot(spec)
    assert lp_fig is not None

    # Test HTML export
    html_file = str(tmp_path / "plot.html")
    LetsPlotRenderer.save(spec, html_file)
    assert os.path.exists(html_file)
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "lets-plot" in content.lower() or "lets_plot" in content.lower() or "script" in content.lower()
