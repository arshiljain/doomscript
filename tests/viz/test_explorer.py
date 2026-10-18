"""Unit tests for Data-Aware Exploration Engine."""

import pytest
from doomscript.viz.explorer import explore_dataset, ExplorationReport


def test_explore_recommends_time_series_and_categorical():
    data = [
        {"date": "2026-01-01", "region": "North", "sales": 100, "profit": 20},
        {"date": "2026-01-02", "region": "South", "sales": 150, "profit": 35},
        {"date": "2026-01-03", "region": "North", "sales": 120, "profit": 25},
    ]
    report = explore_dataset(data)
    assert isinstance(report, ExplorationReport)
    assert len(report.recommendations) >= 2

    types = [rec.chart_type for rec in report.recommendations]
    assert "line" in types or "scatter" in types
    assert any("sales" in rec.rationale for rec in report.recommendations)


def test_explore_flags_nulls():
    data = [
        {"a": 1, "b": None},
        {"a": 2, "b": None},
        {"a": 3, "b": 10},
    ]
    report = explore_dataset(data)
    summary_lower = report.summary.lower()
    assert "missing" in summary_lower or "null" in summary_lower


def test_explore_with_focus_revenue_by_region():
    data = [
        {"month": "Jan", "region": "East", "revenue": 1000},
        {"month": "Feb", "region": "East", "revenue": 1200},
        {"month": "Jan", "region": "West", "revenue": 800},
        {"month": "Feb", "region": "West", "revenue": 950},
    ]
    report = explore_dataset(data, focus="revenue by region")
    assert len(report.recommendations) >= 1
    # Focused chart should map region and revenue
    first_spec = report.recommendations[0].builder.spec()
    assert (
        first_spec.mapping.x in ("region", "month")
        or first_spec.mapping.color in ("region", "month")
    )
    assert "revenue" in report.recommendations[0].rationale.lower()
