"""End-to-end integration tests for exporting DoomScript visualization programs to native Python and running them."""

import os
import subprocess
import sys
from pathlib import Path
import pytest
from doomscript.compiler.engine import export_to_python


def test_export_and_execute_level2_plot(tmp_path):
    pytest.importorskip("lets_plot")

    doom_source = """monthly_sales = [
    {"month": "Jan", "revenue": 12000},
    {"month": "Feb", "revenue": 14500},
    {"month": "Mar", "revenue": 16000}
]

plot monthly_sales as line into rev_trend:
    x: month
    y: revenue
    title: "FY2026 Monthly Revenue Growth"
    theme: minimal

save rev_trend to "revenue.html"
"""
    # 1. Export DoomScript source to native Python code
    exported_py = export_to_python(doom_source)

    # Verify native lets_plot syntax is generated
    assert "from lets_plot import" in exported_py
    assert "ggplot(monthly_sales, aes(" in exported_py
    assert "geom_line()" in exported_py
    assert "ggtitle('FY2026 Monthly Revenue Growth')" in exported_py
    assert "theme_minimal()" in exported_py
    assert "ggsave(rev_trend, 'revenue.html', path='.')" in exported_py

    # 2. Save generated Python script to tmp_path
    script_path = tmp_path / "exported_plot.py"
    script_path.write_text(exported_py, encoding="utf-8")

    # 3. Execute the exported Python script in a subprocess
    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Script failed with stderr:\n{res.stderr}"

    # 4. Verify output artifact exists and contains valid HTML
    html_output = tmp_path / "revenue.html"
    assert html_output.exists(), f"Output file {html_output} was not created."
    content = html_output.read_text(encoding="utf-8")
    assert "lets-plot" in content.lower() or "lets_plot" in content.lower() or "html" in content.lower()


def test_export_and_execute_level3_chart(tmp_path):
    pytest.importorskip("lets_plot")

    doom_source = """measurements = [
    {"speed": 10, "dist": 20, "vehicle": "Car"},
    {"speed": 20, "dist": 50, "vehicle": "Truck"},
    {"speed": 30, "dist": 90, "vehicle": "Car"}
]

chart "Stopping Distance by Speed" from measurements into stopping_chart:
    map speed to x
    map dist to y
    map vehicle to color
    draw points with size=3
    draw line
    theme: minimal

save stopping_chart to "stopping.html"
"""
    exported_py = export_to_python(doom_source)

    assert "from lets_plot import" in exported_py
    assert "ggplot(measurements, aes(" in exported_py
    assert "geom_point(size=3)" in exported_py
    assert "geom_line()" in exported_py
    assert "theme_minimal()" in exported_py

    script_path = tmp_path / "chart_export.py"
    script_path.write_text(exported_py, encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Script failed with stderr:\n{res.stderr}"

    html_output = tmp_path / "stopping.html"
    assert html_output.exists()
    content = html_output.read_text(encoding="utf-8")
    assert len(content) > 100


def test_export_single_line_plot(tmp_path):
    pytest.importorskip("lets_plot")

    doom_source = """pts = [{"x": 1, "y": 2}, {"x": 2, "y": 4}]
plot pts as scatter with x="x", y="y" into p
save p to "scatter.html"
"""
    exported_py = export_to_python(doom_source)
    assert "from lets_plot import" in exported_py
    assert "geom_point()" in exported_py

    script_path = tmp_path / "single_line_export.py"
    script_path.write_text(exported_py, encoding="utf-8")

    res = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"Script failed with stderr:\n{res.stderr}"
    assert (tmp_path / "scatter.html").exists()
