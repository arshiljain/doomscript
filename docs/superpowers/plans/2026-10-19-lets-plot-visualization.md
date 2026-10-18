# Lets-Plot Grammar-of-Graphics Visualization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a natural English Grammar-of-Graphics visualization subsystem in DoomScript powered by JetBrains' Lets-Plot with a 3-level surface language (explore, describe, compose), typed `PlotSpec` IR, lazy rendering, and native Python export.

**Architecture:** A pure-Python typed intermediate representation (`PlotSpec`) completely decouples the user-facing `PlotBuilder` API from the backend execution engine and Python exporter. The DoomScript phrase/compiler layer desugars Level 1 (`explore`), Level 2 (`plot ... as ... into ...`), and Level 3 (`chart ... from ... into ...:`) into validated AST calls constructing `PlotBuilder` objects. `LetsPlotRenderer` lazily converts the IR to `lets_plot` objects for rendering to HTML/PNG/SVG, while `LetsPlotExporter` emits idiomatic native Python `ggplot() + geom_*()` AST for `doom export`.

**Tech Stack:** Python 3.10+, DoomScript AST Compiler & Phrase Normalizer, Lets-Plot 4.x (optional runtime dependency for rendering).

**Spec:** [`docs/superpowers/specs/2026-10-19-lets-plot-visualization-design.md`](file:///C:/Users/kanha/.gemini/antigravity/scratch/doomscript/docs/superpowers/specs/2026-10-19-lets-plot-visualization-design.md)

## Global Constraints
- Zero mandatory dependencies for compilation, IR generation, and testing; `lets-plot` is lazily imported only during `.show()` or `.save()`.
- Python 3.10+ standard library compatibility with float64 precision enforcement.
- Strict geometry semantics (e.g. `bar` with only `x` defaults to `stat="count"`; with both `x` and `y` defaults to `stat="identity"`).
- Actionable beginner-friendly error messages for missing required aesthetics.
- Native Python exporter (`doom export`) emits clean `ggplot(...) + geom_...()` code without string `eval()`.

## Review Focus
- Attempting to plot a histogram or density with categorical `x` gives an immediate, clear error suggesting a bar chart instead.
- Column references (`x: month` vs `x: "Gross Month"`) are strictly treated as column identifier strings, never evaluated as variables.
- Missing required aesthetics (e.g., `y` for boxplot/violin, `x` and `y` for scatter/line, `fill` for heatmap) raise clear error with expected aesthetics.
- Level 2 anonymous plots (omitting `into <target>`) assign to `plot` in scope and work seamlessly with `show plot` and `save plot`.
- Exporting to PNG/PDF without required image rasterizer gives an actionable `pip install pypng` message rather than an unhandled crash.

---

### Task 1: Typed Plot Specification IR & PlotBuilder API

**Files:**
- Create: `src/doomscript/viz/__init__.py`
- Create: `src/doomscript/viz/spec.py`
- Create: `src/doomscript/viz/builder.py`
- Test: `tests/viz/test_spec_builder.py`

**Interfaces:**
- Produces:
  - `PlotSpec`, `AestheticMapping`, `LayerSpec`, `FacetSpec`, `ThemeSpec`, `ScaleSpec`, `LabelSpec` in `src/doomscript/viz/spec.py`.
  - `PlotBuilder(data, title=None)` in `src/doomscript/viz/builder.py`:
    - `.map(aes, col)` / `.map_x(col)` / `.map_y(col)` / `.map_color(col)` / `.map_fill(col)` / `.map_size(col)`
    - `.draw(geom, **params)` supporting all 11 geometries: `point`/`scatter`, `line`, `bar`, `histogram`, `boxplot`, `violin`, `density`, `area`, `tile`/`heatmap`, `pie`, `smooth`
    - `.facet(var, type="wrap", scales="fixed", row=None, col=None)`
    - `.labels(title=None, subtitle=None, caption=None, x=None, y=None, color=None, fill=None)`
    - `.theme(name="minimal", dark=False, legend="right")`
    - `.scale(target, type, palette=None)`
    - `.kind(geom_type, **kwargs)` for Level 2 quick chart construction
    - `.spec() -> PlotSpec` returning the validated IR

- [ ] **Step 1: Write the failing tests for PlotSpec and PlotBuilder**

```python
# tests/viz/test_spec_builder.py
import pytest
from doomscript.viz.spec import PlotSpec, AestheticMapping, LayerSpec
from doomscript.viz.builder import PlotBuilder

def test_builder_constructs_valid_scatter_spec():
    data = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    b = PlotBuilder(data).map_x("a").map_y("b").draw("scatter", size=3, alpha=0.8).theme("minimal")
    spec = b.spec()
    assert spec.data == data
    assert spec.mapping.x == "a"
    assert spec.mapping.y == "b"
    assert len(spec.layers) == 1
    assert spec.layers[0].geom == "point"
    assert spec.layers[0].params == {"size": 3, "alpha": 0.8}
    assert spec.theme.name == "minimal"

def test_bar_geometry_stat_rules():
    data = [{"cat": "A", "val": 10}]
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/viz/test_spec_builder.py -v`
Expected: FAIL (ModuleNotFoundError: No module named 'doomscript.viz')

- [ ] **Step 3: Implement `spec.py` and `builder.py`**

Implement pure dataclasses in `spec.py` and validation-rich fluent `PlotBuilder` methods in `builder.py`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/viz/test_spec_builder.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/viz/ tests/viz/test_spec_builder.py
git commit -m "feat(viz): implement typed PlotSpec IR and PlotBuilder API"
```

---

### Task 2: Data-Aware Exploration Engine (`DataExplorer` & `ExplorationReport`)

**Files:**
- Create: `src/doomscript/viz/explorer.py`
- Test: `tests/viz/test_explorer.py`

**Interfaces:**
- Consumes: `PlotBuilder` from `src/doomscript/viz/builder.py`.
- Produces:
  - `explore_dataset(data, focus: Optional[str] = None) -> ExplorationReport`
  - `ExplorationReport`:
    - `summary: str` (Schema, row count, null count observations)
    - `recommendations: List[ExplorationItem]` (each containing `builder: PlotBuilder`, `chart_type: str`, `rationale: str`)
    - `show()` and `save(path)` methods.

- [ ] **Step 1: Write the failing tests for explore_dataset**

```python
# tests/viz/test_explorer.py
import pytest
from doomscript.viz.explorer import explore_dataset

def test_explore_recommends_time_series_and_categorical():
    data = [
        {"date": "2026-01-01", "region": "North", "sales": 100, "profit": 20},
        {"date": "2026-01-02", "region": "South", "sales": 150, "profit": 35},
        {"date": "2026-01-03", "region": "North", "sales": 120, "profit": 25},
    ]
    report = explore_dataset(data)
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
    assert "missing" in report.summary.lower() or "null" in report.summary.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/viz/test_explorer.py -v`
Expected: FAIL (No module named 'doomscript.viz.explorer')

- [ ] **Step 3: Implement `src/doomscript/viz/explorer.py`**

Implement column schema classification (numeric, datetime/temporal, categorical, boolean), null ratio checks, and recommendation heuristics producing `ExplorationItem` and `ExplorationReport`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/viz/test_explorer.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/viz/explorer.py tests/viz/test_explorer.py
git commit -m "feat(viz): implement data-aware exploration engine and report generator"
```

---

### Task 3: Lets-Plot Backend Renderer & Native Python Exporter

**Files:**
- Create: `src/doomscript/viz/renderer.py`
- Create: `src/doomscript/viz/exporter.py`
- Test: `tests/viz/test_renderer_exporter.py`

**Interfaces:**
- Consumes: `PlotSpec` from `src/doomscript/viz/spec.py`.
- Produces:
  - `LetsPlotRenderer.to_lets_plot(spec: PlotSpec)`: constructs `lets_plot.ggplot` object lazily.
  - `LetsPlotRenderer.save(spec: PlotSpec, path: str, width=None, height=None, dpi=None)`: saves HTML/PNG/SVG.
  - `LetsPlotExporter.to_python(spec: PlotSpec, var_name: str = "p") -> str`: generates native Python AST and formatted code string.

- [ ] **Step 1: Write the failing tests for renderer and exporter**

```python
# tests/viz/test_renderer_exporter.py
from doomscript.viz.builder import PlotBuilder
from doomscript.viz.exporter import LetsPlotExporter

def test_exporter_emits_native_lets_plot_code():
    data = [{"month": "Jan", "revenue": 100, "region": "North"}]
    b = (PlotBuilder("sales")
         .map_x("month")
         .map_y("revenue")
         .map_color("region")
         .draw("line")
         .draw("scatter", size=3)
         .theme("minimal"))
    py_code = LetsPlotExporter().to_python(b.spec(), var_name="revenue_plot")
    assert "from lets_plot import ggplot, aes, geom_line, geom_point, theme_minimal" in py_code
    assert 'revenue_plot = (ggplot(sales, aes(x="month", y="revenue", color="region"))' in py_code
    assert "+ geom_line()" in py_code
    assert "+ geom_point(size=3)" in py_code
    assert "+ theme_minimal()" in py_code
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/viz/test_renderer_exporter.py -v`
Expected: FAIL (No module named 'doomscript.viz.renderer')

- [ ] **Step 3: Implement `renderer.py` and `exporter.py`**

Implement lazy-import `LetsPlotRenderer` handling `.html`, `.png`, `.svg` with `ggsave`, and `LetsPlotExporter` translating `PlotSpec` to clean Python AST expressions via `ast.BinOp(op=ast.Add())` and `ast.unparse()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/viz/test_renderer_exporter.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/viz/renderer.py src/doomscript/viz/exporter.py tests/viz/test_renderer_exporter.py
git commit -m "feat(viz): implement Lets-Plot backend renderer and native Python exporter"
```

---

### Task 4: Surface Grammar, Phrase Normalization & Runtime Integration

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/viz/__init__.py`
- Test: `tests/viz/test_grammar_phrases.py`

**Interfaces:**
- Consumes: `PlotBuilder`, `explore_dataset`, `LetsPlotRenderer` from `doomscript.viz`.
- Produces:
  - English syntax desugaring:
    - Level 1: `explore sales [to understand focus]`
    - Level 2: `plot sales as <geom> [into <var>]:` (with `x:`, `y:`, `color:`, etc.) and `plot sales as <geom> with ... into <var>`
    - Level 3: `chart "<title>" from <data> into <var>:` (with `map`, `draw`, `facet`, `labels:`, `theme:`, `scale`)
    - Display/Export verbs: `show <var>`, `save <var> to "<path>" [with width=..., height=..., dpi=...]`

- [ ] **Step 1: Write the failing tests for visualization grammar and phrases**

```python
# tests/viz/test_grammar_phrases.py
from doomscript.compiler.engine import transpile, execute

def test_transpile_level2_block():
    code = """
sales = [{"month": "Jan", "rev": 100}]
plot sales as line into p:
    x: month
    y: rev
    title: "Monthly Revenue"
"""
    py_ast = transpile(code)
    # verify AST calls PlotBuilder and assigns to p

def test_transpile_level3_chart():
    code = """
sales = [{"month": "Jan", "rev": 100, "region": "North"}]
chart "Revenue by Region" from sales into p:
    map month to x
    map rev to y
    draw line
    draw points with size=2
    theme: minimal
"""
    py_ast = transpile(code)
    # verify AST executes and constructs valid PlotSpec
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/viz/test_grammar_phrases.py -v`
Expected: FAIL

- [ ] **Step 3: Implement grammar normalization and runtime export**

Add phrase normalization rules in `phrases.py` recognizing `explore`, `plot ... as ...`, `chart "..." from ... into ...:`, `show`, and `save`. Export runtime visualization helpers in `runtime.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/viz/test_grammar_phrases.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/grammar/phrases.py src/doomscript/runtime.py src/doomscript/viz/__init__.py tests/viz/test_grammar_phrases.py
git commit -m "feat(viz): integrate visualization grammar, phrase normalization, and runtime"
```

---

### Task 5: Packaging Extras, End-to-End Visual Corpus & Capability Suite

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/viz/corpus/01_explore_dataset.doom`
- Create: `tests/viz/corpus/02_line_chart.doom`
- Create: `tests/viz/corpus/03_scatter_plot.doom`
- Create: `tests/viz/corpus/04_bar_frequency.doom`
- Create: `tests/viz/corpus/05_bar_aggregated.doom`
- Create: `tests/viz/corpus/06_distribution_histogram.doom`
- Create: `tests/viz/corpus/07_boxplot_comparison.doom`
- Create: `tests/viz/corpus/08_heatmap_tiles.doom`
- Create: `tests/viz/corpus/09_pie_chart.doom`
- Create: `tests/viz/corpus/10_multilayer_publication_chart.doom`
- Create: `run_viz_capability.py`
- Test: `tests/viz/test_corpus.py`

**Interfaces:**
- Produces:
  - 10 comprehensive runnable `.doom` visualization benchmark scripts.
  - Automated benchmark harness `run_viz_capability.py` achieving 100.0% pass rate.
  - Optional dependency `pip install doomscript[viz]` containing `lets-plot`, `pypng`, `palettable`.

- [ ] **Step 1: Write the visual corpus and capability runner**

Implement 10 `.doom` programs exercising Level 1, Level 2, and Level 3 syntax across all 11 geometries with `save ... to "output.html"`.

- [ ] **Step 2: Run `run_viz_capability.py` to verify all 10 pass**

Run: `python run_viz_capability.py`
Expected: 10/10 PASSED (100.0%)

- [ ] **Step 3: Run full pytest suite across entire repository**

Run: `python -m pytest tests/ -q`
Expected: 335+ tests passed, 0 regressions.

- [ ] **Step 4: Commit and Push**

```bash
git add pyproject.toml run_viz_capability.py tests/viz/
git commit -m "feat(viz): add 10-program visualization corpus, capability runner, and packaging extra"
git push origin main
```
