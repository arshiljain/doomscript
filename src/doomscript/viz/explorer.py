"""Data-Aware Exploration Engine (Level 1 Visualization).

Inspects dataset schema, types, nulls, and relationships to recommend
informative Grammar-of-Graphics charts with plain-English rationales.
"""

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from doomscript.viz.builder import PlotBuilder


@dataclass
class ExplorationItem:
    builder: PlotBuilder
    chart_type: str
    title: str
    rationale: str


class ExplorationReport:
    """Container for data exploration findings and recommended charts."""

    def __init__(
        self,
        summary: str,
        recommendations: List[ExplorationItem],
        focus: Optional[str] = None,
    ):
        self.summary = summary
        self.recommendations = recommendations
        self.focus = focus

    def __repr__(self) -> str:
        lines = [
            "=" * 70,
            "DOOMSCRIPT DATA EXPLORATION REPORT",
            "=" * 70,
            self.summary,
            "-" * 70,
            f"Recommended Visualizations ({len(self.recommendations)}):",
        ]
        for idx, rec in enumerate(self.recommendations, 1):
            lines.append(f"\n{idx}. [{rec.chart_type.upper()}] {rec.title}")
            lines.append(f"   Rationale: {rec.rationale}")
        lines.append("=" * 70)
        return "\n".join(lines)

    def show(self):
        """Displays all recommended charts."""
        for rec in self.recommendations:
            rec.builder.show()

    def save(self, path: str):
        """Saves a multi-chart HTML exploration report."""
        html_blocks = [
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>DoomScript EDA Report</title>",
            "<style>body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 30px; background: #fafafa; color: #333; }",
            ".card { background: white; border-radius: 8px; padding: 20px; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.08); }",
            "h1 { color: #1a202c; font-size: 24px; } h2 { color: #2d3748; font-size: 18px; margin-top: 0; }",
            ".meta { font-family: monospace; white-space: pre-wrap; background: #edf2f7; padding: 12px; border-radius: 6px; }",
            ".rationale { color: #4a5568; font-style: italic; margin-bottom: 15px; }</style>",
            "</head><body>",
            "<h1>DoomScript Data Exploration Report</h1>",
            f"<div class='card'><h2>Data Summary</h2><div class='meta'>{self.summary}</div></div>",
        ]

        for idx, rec in enumerate(self.recommendations, 1):
            chart_html = rec.builder.to_html()
            html_blocks.append(
                f"<div class='card'><h2>{idx}. {rec.title}</h2>"
                f"<div class='rationale'><strong>Rationale:</strong> {rec.rationale}</div>"
                f"<div>{chart_html}</div></div>"
            )

        html_blocks.append("</body></html>")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(html_blocks))


def _extract_columns_metadata(data: Any) -> Tuple[int, Dict[str, Dict[str, Any]]]:
    """Analyzes columns, types, nulls, and cardinality."""
    col_meta: Dict[str, Dict[str, Any]] = {}
    row_count = 0

    # Convert pandas DataFrame or list of dicts to standard format
    if hasattr(data, "to_dict") and hasattr(data, "columns"):
        rows = data.to_dict(orient="records")
        cols = list(data.columns)
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        rows = data
        cols = list(data[0].keys())
    elif isinstance(data, dict):
        cols = list(data.keys())
        first_key = cols[0] if cols else None
        length = len(data[first_key]) if first_key else 0
        rows = [{c: data[c][i] for c in cols} for i in range(length)]
    else:
        rows = []
        cols = []

    row_count = len(rows)
    date_regex = re.compile(r"^\d{4}[-/]\d{2}(?:[-/]\d{2})?")

    for col in cols:
        vals = [r.get(col) for r in rows]
        null_count = sum(1 for v in vals if v is None or v == "")
        non_null = [v for v in vals if v is not None and v != ""]

        col_type = "text"
        if non_null:
            first_val = non_null[0]
            if isinstance(first_val, bool):
                col_type = "boolean"
            elif isinstance(first_val, (int, float)):
                col_type = "numeric"
            elif isinstance(first_val, str):
                col_lower = col.lower()
                if (
                    "date" in col_lower
                    or "time" in col_lower
                    or "month" in col_lower
                    or "year" in col_lower
                    or date_regex.match(first_val)
                ):
                    col_type = "temporal"
                else:
                    col_type = "categorical"
            else:
                col_type = "categorical"

        unique_count = len(set(str(v) for v in non_null))
        col_meta[col] = {
            "type": col_type,
            "null_count": null_count,
            "null_pct": (null_count / row_count * 100.0) if row_count > 0 else 0.0,
            "unique_count": unique_count,
        }

    return row_count, col_meta


def explore_dataset(data: Any, focus: Optional[str] = None) -> ExplorationReport:
    """Inspects dataset and synthesizes data-aware Grammar-of-Graphics charts with rationales."""
    row_count, col_meta = _extract_columns_metadata(data)

    numeric_cols = [c for c, m in col_meta.items() if m["type"] == "numeric"]
    temporal_cols = [c for c, m in col_meta.items() if m["type"] == "temporal"]
    categorical_cols = [
        c
        for c, m in col_meta.items()
        if m["type"] in ("categorical", "text", "boolean")
    ]

    # Build summary
    summary_lines = [f"Analyzed {row_count} rows across {len(col_meta)} columns."]
    null_issues = [
        f"'{c}' ({m['null_count']} missing, {m['null_pct']:.1f}%)"
        for c, m in col_meta.items()
        if m["null_count"] > 0
    ]
    if null_issues:
        summary_lines.append(f"Missing data observed in: {', '.join(null_issues)}.")
    else:
        summary_lines.append("No missing values detected.")

    summary = " ".join(summary_lines)
    recommendations: List[ExplorationItem] = []

    # Check focus matching
    focused_cols = []
    if focus:
        focus_lower = focus.lower()
        for col in col_meta.keys():
            if col.lower() in focus_lower:
                focused_cols.append(col)

    # 1. Temporal Line Chart
    if temporal_cols and numeric_cols:
        t_col = temporal_cols[0]
        n_col = numeric_cols[0]
        # Match focus if possible
        for fc in focused_cols:
            if fc in temporal_cols:
                t_col = fc
            elif fc in numeric_cols:
                n_col = fc

        group_col = None
        for cc in categorical_cols:
            if col_meta[cc]["unique_count"] <= 8 and (
                focus and cc.lower() in focus.lower()
            ):
                group_col = cc
                break

        b = (
            PlotBuilder(data, title=f"{n_col} over {t_col}")
            .map_x(t_col)
            .map_y(n_col)
        )
        if group_col:
            b.map_color(group_col)
        b.draw("line").theme("minimal")

        recommendations.append(
            ExplorationItem(
                builder=b,
                chart_type="line",
                title=f"{n_col} Trend over {t_col}",
                rationale=(
                    f"Because '{t_col}' is temporal and '{n_col}' is continuous, a line chart "
                    f"reveals trend trajectory and cyclical behavior over time."
                ),
            )
        )

    # 2. Categorical Comparison (Bar chart)
    if categorical_cols and numeric_cols:
        c_col = categorical_cols[0]
        n_col = numeric_cols[0]
        for fc in focused_cols:
            if fc in categorical_cols:
                c_col = fc
            elif fc in numeric_cols:
                n_col = fc

        b = (
            PlotBuilder(data, title=f"{n_col} by {c_col}")
            .map_x(c_col)
            .map_y(n_col)
            .draw("bar")
            .theme("minimal")
        )
        recommendations.append(
            ExplorationItem(
                builder=b,
                chart_type="bar",
                title=f"{n_col} Comparison across {c_col}",
                rationale=(
                    f"Comparing '{n_col}' across '{c_col}' categories highlights relative "
                    f"volume, concentration, and performance leaders."
                ),
            )
        )

    # 3. Numeric Correlation (Scatter plot)
    if len(numeric_cols) >= 2:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        for fc in focused_cols:
            if fc in numeric_cols:
                y_col = fc

        b = (
            PlotBuilder(data, title=f"Correlation: {x_col} vs {y_col}")
            .map_x(x_col)
            .map_y(y_col)
            .draw("point", size=3, alpha=0.7)
            .theme("minimal")
        )
        recommendations.append(
            ExplorationItem(
                builder=b,
                chart_type="scatter",
                title=f"{x_col} vs {y_col}",
                rationale=(
                    f"Plotting '{x_col}' against '{y_col}' in a scatter plot helps identify "
                    f"linear or non-linear correlation, clustering, and anomalous points."
                ),
            )
        )

    # 4. Distribution Histogram
    if numeric_cols:
        d_col = numeric_cols[0]
        b = (
            PlotBuilder(data, title=f"Distribution of {d_col}")
            .map_x(d_col)
            .draw("histogram")
            .theme("minimal")
        )
        recommendations.append(
            ExplorationItem(
                builder=b,
                chart_type="histogram",
                title=f"Distribution of {d_col}",
                rationale=(
                    f"A histogram of '{d_col}' shows sample frequency distribution, "
                    f"central tendency, variance, and potential multi-modal spread."
                ),
            )
        )

    return ExplorationReport(
        summary=summary, recommendations=recommendations, focus=focus
    )
