# DoomScript Grammar-of-Graphics Visualization Specification (Lets-Plot)

**Author:** DoomScript Team  
**Date:** 2026-10-19  
**Status:** Approved for Implementation  
**Topic:** English Grammar-of-Graphics Visualization Engine powered by Lets-Plot  

---

## 1. Executive Summary

This specification defines a comprehensive, English-first visualization subsystem for DoomScript powered by JetBrains' **Lets-Plot** (the Grammar of Graphics implementation in Python).

### Key Architectural Tenets
1. **Three-Level Surface Language**:
   - **Level 1 — Explore**: Autonomous, data-aware Exploratory Data Analysis (`explore dataset`) synthesizing 2–4 sensible charts with plain-English rationales.
   - **Level 2 — Describe**: Fast, one-line and concise block syntax for everyday standard charts (`plot sales as line into p:`).
   - **Level 3 — Compose**: Declarative Grammar-of-Graphics block syntax (`chart "Title" from dataset into p:`) for multi-layered, publication-grade figures.
2. **Decoupled Architecture with Typed Plot Specification IR**:
   - The parser and `PlotBuilder` construct a pure, typed **`PlotSpec` IR**.
   - Zero hard dependency on `lets-plot` for compiling, validating, and testing code.
   - `LetsPlotRenderer` lazily imports `lets_plot` only when rendering (`show`, `save to "chart.html"`, `save to "chart.png"`).
3. **Native Python Exporter**:
   - `doom export` translates DoomScript charts directly into clean, idiomatic `lets_plot.ggplot(...) + geom_...()` Python AST code (no `eval()` or string templating).
4. **Consistent Semantics & Error Handling**:
   - Strict geometry rules (e.g. `bar` frequency counting vs identity values).
   - Actionable, beginner-friendly error messages when aesthetics are missing or inappropriate.

---

## 2. The 3-Level Surface Language

### 2.1 Level 1 — Explore (Automated Data-Aware EDA)

#### Syntax
```doomscript
explore sales
explore sales to understand revenue by region
```

#### Compiler Desugaring
```python
report = explore_dataset(sales, focus="revenue by region")
```

#### Behavior & Output
- Inspects dataset columns (types, cardinality, null counts).
- Evaluates suitability rules:
  - Temporal column + continuous numeric $\rightarrow$ Line trend chart.
  - $\ge 2$ continuous numeric columns $\rightarrow$ Correlation scatter chart.
  - Low-cardinality categorical + numeric $\rightarrow$ Aggregated bar chart.
  - Continuous numeric $\rightarrow$ Distribution histogram / density plot.
- Generates an `ExplorationReport` containing:
  - Column schema summary with null/missingness warnings.
  - 2–4 recommended `PlotBuilder` instances.
  - Plain-English rationales for each recommendation.
- Can be viewed in interactive sessions or saved individually:
  ```doomscript
  show report
  save report to "eda_summary.html"
  ```

---

### 2.2 Level 2 — Describe (Everyday Visualizations)

#### Syntax Forms

**Indented Block Form:**
```doomscript
plot sales as line into revenue_plot:
    x: month
    y: revenue
    color: region
    title: "Revenue over time"
    theme: minimal
```

**Single-Line Form:**
```doomscript
plot sales as scatter with x="temperature", y="revenue", color="region" into p
plot sales as bar with x="region", y="revenue" into bar_chart
plot sales as histogram with x="revenue" into dist_chart
```

**Anonymous / In-Place Form:**
If `into <target>` is omitted, the plot is assigned to a default variable `plot` and can be immediately shown:
```doomscript
plot sales as line:
    x: month
    y: revenue
show plot
```

#### Column Reference Rules
- Identifier format (`x: month`) and quoted string format (`x: "Calendar Month"`) are both supported.
- Column references are strictly treated as string column identifiers; they are never evaluated as variable expressions.

---

### 2.3 Level 3 — Compose (Grammar-of-Graphics Declarative Block)

#### Syntax
```doomscript
chart "Revenue by Region" from sales into p:
    map month to x
    map revenue to y
    map region to color

    draw line
    draw points with size=3, alpha=0.8
    draw smooth trend line

    facet by region

    labels:
        x: "Calendar Month"
        y: "Revenue ($ USD)"
        caption: "Source: FY2026 Audit"

    theme: minimal
    scale color as palette "viridis"
```

#### Block Directives
1. **Aesthetic Mappings**:
   - `map <col> to <aes>` where `<aes>` is one of `x`, `y`, `color`, `fill`, `size`, `shape`, `alpha`, `group`, `weight`.
2. **Geometry Layers**:
   - `draw <geom> [with <params>]`
   - Supported geoms: `points` (or `scatter`), `line`, `bar`, `histogram`, `boxplot`, `violin`, `density`, `area`, `tile` (or `heatmap`), `pie`, `smooth` (or `trend line`), `text`, `errorbar`.
   - Keyword parameters: `size`, `alpha`, `color`, `fill`, `linetype`, `width`, `bins`.
3. **Faceting**:
   - `facet by <col>` $\rightarrow$ `facet_wrap(facets=col)`.
   - `facet grid by row=<col1>, col=<col2>` $\rightarrow$ `facet_grid(x=col2, y=col1)`.
4. **Labels**:
   - `labels:` block with fields `x:`, `y:`, `title:`, `subtitle:`, `caption:`, `color:`, `fill:`.
5. **Themes**:
   - `theme: <name>` where name is `minimal`, `classic`, `bw`, `light`, `void`, `grey`, `dark`.
   - `theme dark` maps to `theme_minimal() + flavor_darcula()`.
6. **Scales & Palettes**:
   - `scale color as palette "viridis"` (or `"magma"`, `"plasma"`, `"inferno"`).
   - `scale x as log` / `scale y as log`.
   - `scale y as reverse`.

---

### 2.4 Display & Export Verbs

```doomscript
show p
save p to "chart.html"
save p to "chart.png" with width=1600, height=900, dpi=300
save p to "chart.svg"
save p to "chart.pdf" with width=1200, height=800
```

---

## 3. Typed Plot Specification Intermediate Representation (IR)

Located at `src/doomscript/viz/spec.py`:

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

@dataclass
class AestheticMapping:
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    fill: Optional[str] = None
    size: Optional[str] = None
    shape: Optional[str] = None
    alpha: Optional[str] = None
    group: Optional[str] = None
    weight: Optional[str] = None
    slice: Optional[str] = None

@dataclass
class LayerSpec:
    geom: str
    mapping: Optional[AestheticMapping] = None
    stat: Optional[str] = None
    position: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FacetSpec:
    type: str  # "wrap" | "grid"
    facets: Optional[Union[str, List[str]]] = None
    row: Optional[str] = None
    col: Optional[str] = None
    scales: str = "fixed"

@dataclass
class ThemeSpec:
    name: str = "minimal"
    legend_position: str = "right"
    dark_mode: bool = False

@dataclass
class ScaleSpec:
    target: str  # "x", "y", "color", "fill"
    type: str    # "log", "reverse", "palette", "continuous", "discrete"
    palette_name: Optional[str] = None

@dataclass
class LabelSpec:
    title: Optional[str] = None
    subtitle: Optional[str] = None
    caption: Optional[str] = None
    x: Optional[str] = None
    y: Optional[str] = None
    color: Optional[str] = None
    fill: Optional[str] = None

@dataclass
class PlotSpec:
    data: Any
    mapping: AestheticMapping = field(default_factory=AestheticMapping)
    layers: List[LayerSpec] = field(default_factory=list)
    facet: Optional[FacetSpec] = None
    theme: ThemeSpec = field(default_factory=ThemeSpec)
    scales: List[ScaleSpec] = field(default_factory=list)
    labels: LabelSpec = field(default_factory=LabelSpec)
```

---

## 4. Geometry Semantics & Verification Table

| Geometry | Required Aesthetics | Optional Aesthetics | Default Stat | Validation / Error Message |
|:---|:---|:---|:---|:---|
| `scatter` / `point` | `x`, `y` | `color`, `fill`, `size`, `alpha`, `shape` | `"identity"` | Fails if `x` or `y` is missing. |
| `line` | `x`, `y` | `color`, `size`, `alpha`, `group` | `"identity"` | Fails if `x` or `y` is missing. |
| `bar` | `x` | `y`, `color`, `fill`, `group` | `count` (x only), `identity` (x and y) | Fails if `x` is missing. |
| `histogram` | `x` | `fill`, `color`, `alpha`, `bins` | `"bin"` | Fails if `x` is categorical: *"Histogram requires numeric values on x-axis"*. |
| `density` | `x` | `fill`, `color`, `alpha` | `"density"` | Fails if `x` is categorical. |
| `boxplot` | `y` | `x`, `color`, `fill` | `"boxplot"` | Fails if `y` is missing. |
| `violin` | `y` | `x`, `color`, `fill` | `"violin"` | Fails if `y` is missing. |
| `tile` / `heatmap` | `x`, `y`, `fill` | `alpha` | `"identity"` | Fails if `x`, `y`, or `fill` is missing. |
| `pie` | `slice` (or `fill`), `value` | `color`, `alpha` | `"identity"` | Fails if `slice` or `value` is missing. |
| `area` | `x`, `y` | `fill`, `color`, `alpha`, `group` | `"identity"` | Fails if `x` or `y` is missing. |
| `smooth` | `x`, `y` | `color`, `linetype` | `"smooth"` | Fails if `x` or `y` is missing. |

---

## 5. Exporter Architecture (`doom export`)

`LetsPlotExporter` translates `PlotSpec` into Python AST expressions conforming to idiomatic Lets-Plot patterns:

```python
from lets_plot import (
    ggplot, aes, geom_line, geom_point, geom_smooth,
    facet_wrap, ggtitle, labs, theme_minimal, scale_color_viridis
)

p = (
    ggplot(sales, aes(x="month", y="revenue", color="region"))
    + geom_line()
    + geom_point(size=3, alpha=0.8)
    + geom_smooth()
    + facet_wrap(facets="region")
    + labs(x="Calendar Month", y="Revenue ($ USD)", caption="Source: FY2026 Audit")
    + ggtitle("Revenue by Region")
    + theme_minimal()
    + scale_color_viridis()
)
```

---

## 6. Testing & Acceptance Criteria

1. **Unit Tests (`tests/viz/test_spec.py`)**:
   - Validates `PlotSpec` generation for all 11 geometry types without importing `lets-plot`.
   - Validates error messages for missing aesthetics.
2. **Compiler & Exporter Tests (`tests/viz/test_compiler.py`, `tests/viz/test_export.py`)**:
   - Asserts AST desugaring for Level 1, Level 2, and Level 3 blocks.
   - Verifies `doom export` generates syntax-valid Python code.
3. **Renderer Integration Tests (`tests/viz/test_renderer.py`)**:
   - Generates HTML, verifies bundle inclusion and structure.
   - Tests `save_plot` with width/height/dpi parameters.
4. **End-to-End Visual Corpus (`tests/viz/corpus/`)**:
   - 10 runnable `.doom` visualization programs covering all three levels.
