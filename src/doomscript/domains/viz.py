"""Visualization Domain Pack bridging Grammar-of-Graphics into the Domain Registry."""

import ast
import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from doomscript.domains.base import (
    DomainContract,
    DomainParser,
    DomainRuntime,
    DomainASTExporter,
    DomainIR,
)
from doomscript.domains.registry import get_domain_registry
from doomscript.viz.spec import PlotSpec
from doomscript.viz.builder import PlotBuilder
from doomscript.core.record import Record


# ==============================================================================
# ASCII BOXPLOT & FORCE-DIRECTED GRAPH LAYOUT ENGINES
# ==============================================================================


class ASCIIHistogramAndBoxPlotRenderer:
    """Renders statistical five-number summaries, Tukey outlier fences,
    and ASCII/Unicode box-and-whisker and bar plots for terminal visualization.
    """

    @classmethod
    def compute_summary(cls, data: List[float]) -> Dict[str, Any]:
        clean = sorted([float(x) for x in data])
        n = len(clean)
        if n == 0:
            return {"min": 0.0, "q1": 0.0, "median": 0.0, "q3": 0.0, "max": 0.0, "iqr": 0.0, "outliers": []}

        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return clean[int(k)]
            d0 = clean[int(f)] * (c - k)
            d1 = clean[int(c)] * (k - f)
            return d0 + d1

        min_val = clean[0]
        max_val = clean[-1]
        q1 = percentile(0.25)
        median = percentile(0.50)
        q3 = percentile(0.75)
        iqr = q3 - q1

        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outliers = [x for x in clean if x < lower_fence or x > upper_fence]

        return {
            "min": round(min_val, 4),
            "q1": round(q1, 4),
            "median": round(median, 4),
            "q3": round(q3, 4),
            "max": round(max_val, 4),
            "iqr": round(iqr, 4),
            "lower_fence": round(lower_fence, 4),
            "upper_fence": round(upper_fence, 4),
            "outliers": [round(x, 4) for x in outliers],
            "count": n,
        }

    @classmethod
    def render_boxplot(cls, data: List[float], width: int = 50, title: str = "") -> Dict[str, Any]:
        summary = cls.compute_summary(data)
        if summary["count"] == 0:
            return {"summary": summary, "ascii_plot": "Empty dataset"}

        min_v = summary["min"]
        max_v = summary["max"]
        span = max(1e-9, max_v - min_v)

        def pos(val: float) -> int:
            return int(round((val - min_v) / span * (width - 1)))

        p_min = pos(min_v)
        p_q1 = pos(summary["q1"])
        p_med = pos(summary["median"])
        p_q3 = pos(summary["q3"])
        p_max = pos(max_v)

        chars = [" "] * width
        # Draw whisker line
        for i in range(p_min, p_max + 1):
            chars[i] = "-"
        # Draw box
        chars[p_q1] = "["
        for i in range(p_q1 + 1, p_q3):
            chars[i] = "="
        chars[p_med] = "|"
        chars[p_q3] = "]"
        # Draw endpoints
        chars[p_min] = "|"
        chars[p_max] = "|"

        # Mark outliers
        for out in summary["outliers"]:
            idx = pos(out)
            if 0 <= idx < width:
                chars[idx] = "*"

        plot_line = "".join(chars)
        scale_line = f"{min_v:<10.2f}{' ' * max(0, width - 20)}{max_v:>10.2f}"
        header = f"--- {title} ---" if title else "--- Boxplot ---"
        full_text = f"{header}\n{plot_line}\n{scale_line}\n"

        return {
            "summary": Record(summary),
            "ascii_plot": full_text,
            "plot_line": plot_line,
        }

    @classmethod
    def render_barchart(
        cls,
        categories: List[str],
        values: List[float],
        max_bar_width: int = 40,
    ) -> str:
        if not values or not categories:
            return "Empty chart"

        max_val = max(abs(float(v)) for v in values) if values else 1.0
        max_lbl_len = max(len(str(c)) for c in categories) if categories else 10
        lines = []

        for cat, val in zip(categories, values):
            v_float = float(val)
            bar_len = int(round((abs(v_float) / max(1e-9, max_val)) * max_bar_width))
            bar_str = "#" * bar_len
            lbl_padded = str(cat).rjust(max_lbl_len)
            lines.append(f"{lbl_padded} | {bar_str} ({v_float:g})")

        return "\n".join(lines)


class ForceDirectedGraphLayout2D:
    """Fruchterman-Reingold 2D force-directed layout simulation for graph networks.

    Simulates pairwise Coulomb electrostatic repulsion and Hooke spring edge
    attraction with simulated annealing temperature cooling.
    """

    @classmethod
    def layout(
        cls,
        nodes: List[Any],
        edges: List[Tuple[Any, Any]],
        iterations: int = 100,
        width: float = 100.0,
        height: float = 100.0,
    ) -> Dict[str, Any]:
        node_list = [str(n) for n in nodes]
        v_count = len(node_list)
        if v_count == 0:
            return {"positions": {}, "nodes": [], "iterations": 0}

        # Initial circular layout
        pos: Dict[str, List[float]] = {}
        for i, n in enumerate(node_list):
            angle = 2.0 * math.pi * i / v_count
            pos[n] = [
                width / 2.0 + (width * 0.4) * math.cos(angle),
                height / 2.0 + (height * 0.4) * math.sin(angle),
            ]

        area = width * height
        k = math.sqrt(area / max(1, v_count))
        temp = width / 10.0
        cooling = temp / max(1, iterations)

        clean_edges = []
        for e in edges:
            if isinstance(e, (list, tuple)) and len(e) >= 2:
                u, v = str(e[0]), str(e[1])
                if u in pos and v in pos and u != v:
                    clean_edges.append((u, v))

        for it in range(iterations):
            disp: Dict[str, List[float]] = {n: [0.0, 0.0] for n in node_list}

            # 1. Repulsive forces between all node pairs
            for i in range(v_count):
                u = node_list[i]
                for j in range(i + 1, v_count):
                    v = node_list[j]
                    dx = pos[u][0] - pos[v][0]
                    dy = pos[u][1] - pos[v][1]
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < 1e-4:
                        dx = 1e-3
                        dy = 1e-3
                        dist = math.sqrt(dx * dx + dy * dy)
                    f_rep = (k * k) / dist
                    disp[u][0] += (dx / dist) * f_rep
                    disp[u][1] += (dy / dist) * f_rep
                    disp[v][0] -= (dx / dist) * f_rep
                    disp[v][1] -= (dy / dist) * f_rep

            # 2. Attractive forces along edges
            for u, v in clean_edges:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = max(1e-4, math.sqrt(dx * dx + dy * dy))
                f_att = (dist * dist) / k
                disp[u][0] -= (dx / dist) * f_att
                disp[u][1] -= (dy / dist) * f_att
                disp[v][0] += (dx / dist) * f_att
                disp[v][1] += (dy / dist) * f_att

            # 3. Update positions bounded by temperature
            for n in node_list:
                d_len = max(1e-4, math.sqrt(disp[n][0] ** 2 + disp[n][1] ** 2))
                pos[n][0] += (disp[n][0] / d_len) * min(d_len, temp)
                pos[n][1] += (disp[n][1] / d_len) * min(d_len, temp)

                # Clamp to bounding box
                pos[n][0] = max(0.0, min(width, pos[n][0]))
                pos[n][1] = max(0.0, min(height, pos[n][1]))

            temp = max(1e-4, temp - cooling)

        # Normalize coordinates to [0.0, 1.0]
        norm_pos = {}
        for n in node_list:
            norm_pos[n] = {
                "x": round(pos[n][0] / width, 4),
                "y": round(pos[n][1] / height, 4),
            }

        return {
            "positions": {n: Record(norm_pos[n]) for n in node_list},
            "nodes_count": v_count,
            "edges_count": len(clean_edges),
            "iterations": iterations,
        }

    @classmethod
    def render_canvas(
        cls,
        layout_res: Dict[str, Any],
        canvas_width: int = 60,
        canvas_height: int = 20,
    ) -> str:
        positions = layout_res.get("positions", {})
        if not positions:
            return "Empty network layout"

        grid = [[" " for _ in range(canvas_width)] for _ in range(canvas_height)]

        for node_name, p in positions.items():
            px = int(round(p["x"] * (canvas_width - 1)))
            py = int(round(p["y"] * (canvas_height - 1)))
            px = max(0, min(canvas_width - 1, px))
            py = max(0, min(canvas_height - 1, py))
            label = str(node_name)[:3]
            for ch_idx, ch in enumerate(label):
                if px + ch_idx < canvas_width:
                    grid[py][px + ch_idx] = ch

        return "\n".join("".join(row) for row in grid)


def viz_ascii_boxplot(data: List[float], width: int = 50, title: str = "") -> Any:
    """Renders ASCII boxplot and statistical summary."""
    return Record(ASCIIHistogramAndBoxPlotRenderer.render_boxplot(data, width=width, title=title))


def viz_ascii_bar_chart(categories: List[str], values: List[float], max_bar_width: int = 40) -> str:
    """Renders terminal ASCII horizontal bar chart."""
    return ASCIIHistogramAndBoxPlotRenderer.render_barchart(categories, values, max_bar_width=max_bar_width)


def viz_force_directed_layout(
    nodes: List[Any],
    edges: List[Tuple[Any, Any]],
    iterations: int = 100,
    width: float = 100.0,
    height: float = 100.0,
) -> Any:
    """Simulates Fruchterman-Reingold 2D force layout for network visualization."""
    return Record(
        ForceDirectedGraphLayout2D.layout(nodes, edges, iterations=iterations, width=width, height=height)
    )


def viz_render_ascii_network(layout_res: Any, canvas_width: int = 60, canvas_height: int = 20) -> str:
    """Renders 2D character grid canvas of network graph layout."""
    res_dict = layout_res.as_dict() if hasattr(layout_res, "as_dict") else dict(layout_res)
    return ForceDirectedGraphLayout2D.render_canvas(res_dict, canvas_width=canvas_width, canvas_height=canvas_height)


class VizDomainParser(DomainParser):
    """Bridge parser for visualization domain."""

    def parse_inspect(self, line: str, line_no: int) -> Optional[str]:
        return None

    def parse_operation(self, line: str, line_no: int) -> Optional[str]:
        s = line.strip()
        # render ascii boxplot for data <data> [with width <w>] into <target>
        m_box = re.match(
            r"^render\s+ascii\s+boxplot\s+for\s+data\s+(.+?)(?:\s+with\s+width\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_box:
            data = m_box.group(1).strip()
            width = m_box.group(2).strip() if m_box.group(2) else "50"
            target = m_box.group(3).strip()
            return f"set {target} to viz_ascii_boxplot({data}, width={width})"

        # render ascii bar chart labels <labels> values <values> [with width <w>] into <target>
        m_bar = re.match(
            r"^render\s+ascii\s+bar\s+chart\s+labels\s+(.+?)\s+values\s+(.+?)(?:\s+with\s+width\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bar:
            lbls = m_bar.group(1).strip()
            vals = m_bar.group(2).strip()
            width = m_bar.group(3).strip() if m_bar.group(3) else "40"
            target = m_bar.group(4).strip()
            return f"set {target} to viz_ascii_bar_chart({lbls}, {vals}, max_bar_width={width})"

        # simulate force layout for nodes <nodes> edges <edges> [iterations <iter>] into <target>
        m_fr = re.match(
            r"^simulate\s+force\s+layout\s+for\s+nodes\s+(.+?)\s+edges\s+(.+?)(?:\s+iterations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fr:
            nodes = m_fr.group(1).strip()
            edges = m_fr.group(2).strip()
            iters = m_fr.group(3).strip() if m_fr.group(3) else "100"
            target = m_fr.group(4).strip()
            return f"set {target} to viz_force_directed_layout({nodes}, {edges}, iterations={iters})"

        # render ascii network from layout <layout> [width <w>] [height <h>] into <target>
        m_net = re.match(
            r"^render\s+ascii\s+network\s+from\s+layout\s+(.+?)(?:\s+width\s+(\d+))?(?:\s+height\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_net:
            layout = m_net.group(1).strip()
            w = m_net.group(2).strip() if m_net.group(2) else "60"
            h = m_net.group(3).strip() if m_net.group(3) else "20"
            target = m_net.group(4).strip()
            return f"set {target} to viz_render_ascii_network({layout}, canvas_width={w}, canvas_height={h})"

        return None

    def parse_block(
        self, header: str, body_lines: List[Tuple[int, str]], indent: int = 0
    ) -> Tuple[DomainIR, str]:
        raise NotImplementedError("Viz blocks are parsed by the specialized visual grammar.")


class VizRuntime(DomainRuntime):
    """Bridge runtime for visualization execution."""

    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        if isinstance(ir, PlotBuilder):
            return ir.build()
        return ir


class VizASTExporter(DomainASTExporter):
    """Bridge exporter translating PlotSpec into native Lets-Plot AST."""

    def to_ast(self, ir: DomainIR, target_var: str = "p") -> Tuple[Set[str], List[ast.stmt]]:
        from doomscript.viz.exporter import LetsPlotExporter

        if isinstance(ir, PlotSpec):
            exporter = LetsPlotExporter()
            imports, assign_node = exporter.to_ast(ir, var_name=target_var)
            return imports, [assign_node]
        return set(), []


from doomscript.domains.matcher import VerbSpec


class VizDomain(DomainContract):
    """Visualization Domain Pack (Grammar of Graphics, Lets-Plot)."""

    name = "viz"
    aliases = ["visualization", "charts", "plots", "plot"]
    description = "Grammar of Graphics data visualization with layers, scales, themes, and facets"
    parser = VizDomainParser()
    runtime = VizRuntime()
    exporter = VizASTExporter()
    capabilities = ["plots", "charts", "facets", "themes", "layers", "scales"]
    optional_dependencies = ["lets_plot"]

    verbs = [
        VerbSpec(
            name="explore",
            pattern="explore {dataset:ident} [to understand {focus:expr}] [into {target:ident}]",
            arg_schema={"dataset": "ident", "focus": "expr", "target": "ident"},
            returns="Record",
            description="Automated exploratory visualization and statistical insights",
        ),
        VerbSpec(
            name="show_plot",
            pattern="show {target_var:ident}",
            arg_schema={"target_var": "ident"},
            returns="None",
            description="Display interactive plot figure",
        ),
        VerbSpec(
            name="save_plot",
            pattern="save {target_var:ident} to {path_str:expr}",
            arg_schema={"target_var": "ident", "path_str": "expr"},
            returns="str",
            description="Save plot figure to PNG, SVG, or HTML file",
        ),
        VerbSpec(
            name="plot",
            pattern="plot {dataset:ident} as {geom:ident} with {params:expr} [into {target:ident}]",
            arg_schema={"dataset": "ident", "geom": "ident", "params": "expr", "target": "ident"},
            returns="Plot",
            description="Construct single-layer plot figure",
        ),
    ]

    def can_handle_line(self, line: str) -> bool:
        if self.parser.parse_operation(line, 0) is not None:
            return True
        return False

    def can_handle_block(self, header: str) -> bool:
        return False


VIZ_DOMAIN = VizDomain()
get_domain_registry().register(VIZ_DOMAIN)

__all__ = [
    "VizDomain",
    "VIZ_DOMAIN",
    "VizDomainParser",
    "VizRuntime",
    "VizASTExporter",
    "ASCIIHistogramAndBoxPlotRenderer",
    "ForceDirectedGraphLayout2D",
    "viz_ascii_boxplot",
    "viz_ascii_bar_chart",
    "viz_force_directed_layout",
    "viz_render_ascii_network",
]
