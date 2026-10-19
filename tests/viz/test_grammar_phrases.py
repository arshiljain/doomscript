"""Unit tests for Visualization Grammar and Phrase Normalization."""

import pytest
from doomscript.compiler.engine import transpile, execute
from doomscript.viz.spec import PlotSpec


def test_level1_explore_normalization():
    code = """
sales = [{"a": 1, "b": 2}]
explore sales into my_rep
"""
    scope = {}
    execute(code, scope)
    assert "my_rep" in scope
    assert hasattr(scope["my_rep"], "recommendations")


def test_level1_explore_focus_normalization():
    code = """
sales = [{"month": "Jan", "rev": 100}]
explore sales to understand rev by month into my_rep
"""
    scope = {}
    execute(code, scope)
    assert "my_rep" in scope
    assert scope["my_rep"].focus == "rev by month"


def test_level2_single_line_normalization():
    code = """
sales = [{"x": 1, "y": 10, "cat": "A"}]
plot sales as scatter with x="x", y="y", color="cat" into p
"""
    scope = {}
    execute(code, scope)
    assert "p" in scope
    spec = scope["p"].spec()
    assert spec.mapping.x == "x"
    assert spec.mapping.y == "y"
    assert spec.mapping.color == "cat"
    assert spec.layers[0].geom == "point"


def test_level2_block_normalization():
    code = """
sales = [{"month": "Jan", "rev": 100, "region": "North"}]
plot sales as line into rev_plot:
    x: month
    y: rev
    color: region
    title: "Revenue Over Time"
    theme: minimal

final_spec = rev_plot.spec()
"""
    scope = {}
    execute(code, scope)
    assert "rev_plot" in scope
    spec = scope["final_spec"]
    assert spec.mapping.x == "month"
    assert spec.mapping.y == "rev"
    assert spec.mapping.color == "region"
    assert spec.layers[0].geom == "line"
    assert spec.labels.title == "Revenue Over Time"
    assert spec.theme.name == "minimal"


def test_level3_chart_block_normalization():
    code = """
sales = [{"month": "Jan", "rev": 100, "region": "North"}]
chart "Revenue by Region" from sales into p:
    map month to x
    map rev to y
    map region to color

    draw line
    draw points with size=3, alpha=0.8

    facet by region

    labels:
        x: "Calendar Month"
        y: "Revenue ($ USD)"
        caption: "Source: FY2026 Audit"

    theme: minimal
    scale color as palette "viridis"

final_spec = p.spec()
"""
    scope = {}
    execute(code, scope)
    assert "p" in scope
    spec = scope["final_spec"]
    assert spec.mapping.x == "month"
    assert spec.mapping.y == "rev"
    assert spec.mapping.color == "region"
    assert len(spec.layers) == 2
    assert [l.geom for l in spec.layers] == ["line", "point"]
    assert spec.facet.facets == "region"
    assert spec.labels.x == "Calendar Month"
    assert spec.labels.y == "Revenue ($ USD)"
    assert spec.scales[0].palette_name == "viridis"
    assert spec.theme.name == "minimal"


def test_save_and_show_verbs(tmp_path):
    pytest.importorskip("lets_plot")
    out_html = str(tmp_path / "chart.html").replace("\\", "/")
    code = f"""
sales = [{{"x": 1, "y": 2}}]
plot sales as line into p:
    x: x
    y: y

save p to "{out_html}"
"""
    scope = {}
    execute(code, scope)
    import os

    assert os.path.exists(out_html)
