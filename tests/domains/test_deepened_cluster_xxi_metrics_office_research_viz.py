"""Comprehensive unit tests for Deepened Cluster XXI:
Metrics, Office, Research, and Viz domains in DoomScript.
"""

import textwrap
import pytest
from doomscript.compiler.engine import execute

# Domain runtime classes & algorithms
from doomscript.domains.metrics.runtime import (
    ConfusionMatrixMultiClassMetrics,
    PrecisionRecallCurveAP,
    metrics_confusion_matrix_multiclass,
    metrics_precision_recall_ap,
)
from doomscript.domains.office.runtime import (
    SpreadsheetDependencyDAGTopologicalEvaluator,
    PivotTableMultiDimensionalAggregation,
    office_spreadsheet_dag_eval,
    office_pivot_table_aggregate,
)
from doomscript.domains.research.runtime import (
    HIndexAndCitationBibliometrics,
    BenjaminiHochbergMultipleTesting,
    research_calculate_bibliometrics,
    research_multiple_testing_correction,
)
from doomscript.domains.viz import (
    ASCIIHistogramAndBoxPlotRenderer,
    ForceDirectedGraphLayout2D,
    viz_ascii_boxplot,
    viz_ascii_bar_chart,
    viz_force_directed_layout,
    viz_render_ascii_network,
)


# ==============================================================================
# METRICS DOMAIN TESTS
# ==============================================================================


def test_metrics_confusion_matrix_multiclass():
    y_true = [0, 0, 1, 1, 2, 2, 2]
    y_pred = [0, 1, 1, 1, 2, 2, 0]
    res = ConfusionMatrixMultiClassMetrics.compute(y_true, y_pred)

    assert res["sample_count"] == 7
    assert res["classes_count"] == 3
    assert res["accuracy"] == round(5 / 7, 4)
    assert res["matthews_corrcoef"] > 0.5
    assert res["cohen_kappa"] > 0.5
    assert len(res["per_class"]) == 3


def test_metrics_precision_recall_ap():
    y_true = [1, 1, 0, 1, 0, 0, 1, 0]
    scores = [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2]
    res = PrecisionRecallCurveAP.compute(y_true, scores)

    assert res["total_positive_samples"] == 4
    assert res["average_precision"] > 0.6
    assert 0.0 < res["optimal_threshold"] < 1.0
    assert res["max_f1"] > 0.6


def test_metrics_spoken_english():
    script = textwrap.dedent("""
    use metrics
    set actual_labels to ["cat", "cat", "dog", "dog", "bird", "bird"]
    set pred_labels to ["cat", "dog", "dog", "dog", "bird", "bird"]
    calculate confusion metrics actual actual_labels predicted pred_labels into cm_res

    set binary_true to [1, 1, 0, 1, 0]
    set pred_scores to [0.95, 0.85, 0.40, 0.75, 0.10]
    calculate precision recall ap actual binary_true scores pred_scores into ap_res
    """).strip()
    env = execute(script)
    assert env["cm_res"]["accuracy"] > 0.8
    assert env["ap_res"]["average_precision"] > 0.9


# ==============================================================================
# OFFICE DOMAIN TESTS
# ==============================================================================


def test_office_spreadsheet_dag_topological():
    cells = {
        "A1": 10,
        "A2": 20,
        "A3": "=SUM(A1:A2)",
        "B1": "=A3 * 2",
        "B2": "=B1 + 5",
    }
    res = SpreadsheetDependencyDAGTopologicalEvaluator.evaluate(cells)

    assert res["has_circular_dependency"] is False
    assert res["values"]["A3"] == 30
    assert res["values"]["B1"] == 60
    assert res["values"]["B2"] == 65
    assert res["evaluation_order"].index("A3") < res["evaluation_order"].index("B1")


def test_office_spreadsheet_circular_dependency():
    cells = {
        "A1": "=B1 + 1",
        "B1": "=A1 * 2",
        "C1": 100,
    }
    res = SpreadsheetDependencyDAGTopologicalEvaluator.evaluate(cells)

    assert res["has_circular_dependency"] is True
    assert set(res["circular_cells"]) == {"A1", "B1"}
    assert "#REF!" in res["values"]["A1"]
    assert res["values"]["C1"] == 100


def test_office_pivot_table_aggregate():
    records = [
        {"Region": "North", "Rep": "Alice", "Sales": 100},
        {"Region": "North", "Rep": "Bob", "Sales": 150},
        {"Region": "North", "Rep": "Alice", "Sales": 200},
        {"Region": "South", "Rep": "Charlie", "Sales": 300},
    ]
    res = PivotTableMultiDimensionalAggregation.compute(
        records, row_dimensions=["Region", "Rep"], value_column="Sales", aggregation_function="sum"
    )

    assert res["total_records"] == 4
    assert res["grand_total"] == 750
    assert len(res["rows"]) == 3
    # North, Alice should have 300
    alice_row = [r for r in res["rows"] if r["Rep"] == "Alice"][0]
    assert alice_row["value"] == 300


def test_office_spoken_english():
    script = textwrap.dedent("""
    use office
    set sheet_cells to {"X1": 5, "X2": 15, "X3": "=SUM(X1:X2)", "TOTAL": "=X3 * 3"}
    evaluate spreadsheet dag sheet_cells into sheet_res

    set sales_data to [{"City": "NY", "Sales": 500}, {"City": "NY", "Sales": 300}, {"City": "LA", "Sales": 400}]
    create multidimensional pivot table from sales_data rows ["City"] values "Sales" agg "sum" into pivot_res
    """).strip()
    env = execute(script)
    assert env["sheet_res"]["values"]["TOTAL"] == 60
    assert env["pivot_res"]["grand_total"] == 1200


# ==============================================================================
# RESEARCH DOMAIN TESTS
# ==============================================================================


def test_research_bibliometrics():
    citations = [50, 25, 12, 10, 8, 5, 4, 2, 1, 0]
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2024, 2025, 2026]
    res = HIndexAndCitationBibliometrics.compute(citations, publication_years=years, current_year=2026)

    # h-index: 5 papers with >= 5 citations (50, 25, 12, 10, 8 >= 5)
    assert res["h_index"] == 5
    assert res["i10_index"] == 4
    assert res["total_citations"] == 117
    assert res["g_index"] >= 5


def test_research_multiple_testing_correction():
    p_vals = [0.001, 0.005, 0.02, 0.04, 0.15, 0.40, 0.80]
    res = BenjaminiHochbergMultipleTesting.correct(p_vals, alpha=0.05)

    assert res["total_hypotheses"] == 7
    assert res["significant_count"] >= 2
    assert res["adjusted_q_values"][0] < 0.01
    assert res["bonferroni_p_values"][0] == 0.007


def test_research_spoken_english():
    script = textwrap.dedent("""
    use research
    set pub_cites to [30, 20, 15, 12, 10, 4, 2]
    calculate bibliometrics for citations pub_cites into bib_res

    set raw_p_values to [0.0001, 0.002, 0.03, 0.06, 0.25]
    correct p values raw_p_values with fdr alpha 0.05 into fdr_res
    """).strip()
    env = execute(script)
    assert env["bib_res"]["h_index"] == 5
    assert env["fdr_res"]["significant_count"] >= 2


# ==============================================================================
# VIZ DOMAIN TESTS
# ==============================================================================


def test_viz_ascii_boxplot_and_barchart():
    data = [10, 12, 14, 15, 18, 20, 22, 25, 30, 50]
    box_res = ASCIIHistogramAndBoxPlotRenderer.render_boxplot(data, width=40, title="Latency")

    summary = box_res["summary"]
    assert summary["min"] == 10
    assert summary["max"] == 50
    assert summary["median"] > 15
    assert len(box_res["plot_line"]) == 40

    chart = ASCIIHistogramAndBoxPlotRenderer.render_barchart(
        ["CPU", "Memory", "Disk"], [25.0, 75.0, 50.0], max_bar_width=30
    )
    assert "CPU" in chart
    assert "Memory" in chart
    assert "#" in chart


def test_viz_force_directed_layout():
    nodes = ["Router", "Server1", "Server2", "Client"]
    edges = [("Router", "Server1"), ("Router", "Server2"), ("Router", "Client")]
    res = ForceDirectedGraphLayout2D.layout(nodes, edges, iterations=50, width=80.0, height=40.0)

    assert res["nodes_count"] == 4
    assert res["edges_count"] == 3
    positions = res["positions"]
    for n in nodes:
        assert 0.0 <= positions[n]["x"] <= 1.0
        assert 0.0 <= positions[n]["y"] <= 1.0

    canvas = ForceDirectedGraphLayout2D.render_canvas(res, canvas_width=40, canvas_height=15)
    assert len(canvas.splitlines()) == 15


def test_viz_spoken_english():
    script = textwrap.dedent("""
    use viz
    set response_times to [5.0, 10.0, 12.0, 15.0, 18.0, 20.0, 22.0, 35.0]
    render ascii boxplot for data response_times with width 50 into box_res

    set svc_names to ["Auth", "Billing", "Gateway"]
    set svc_loads to [45.0, 90.0, 60.0]
    render ascii bar chart labels svc_names values svc_loads with width 30 into bar_res

    set topo_nodes to ["A", "B", "C"]
    set topo_edges to [["A", "B"], ["B", "C"]]
    simulate force layout for nodes topo_nodes edges topo_edges iterations 30 into layout_res
    """).strip()
    env = execute(script)
    assert env["box_res"]["summary"]["count"] == 8
    assert "Auth" in env["bar_res"]
    assert env["layout_res"]["nodes_count"] == 3
