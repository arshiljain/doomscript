# DoomScript Domain Maturity Ladder & Architecture

DoomScript is an English-first programming language built around a general-purpose core extended by modular domain-specific languages.

Each domain provides readable English syntax tailored to a specific discipline while sharing a single compilation pipeline, Intermediate Representation (IR) contract, AST evaluator, and execution engine.

---

## The 4-Level Domain Maturity Ladder

```
[ Level 1: Prototype ]   Syntax proposed, experimental grammar, mock or partial execution.
         │
[ Level 2: Usable ]      Pure-Python native execution engine, zero mandatory external dependencies.
         │
[ Level 3: Stable ]      Strict semantic parity between DoomScript execution and Python AST export.
         │               Full conformance test suite with zero `eval()`.
         ▼
[ Level 4: Professional] Production-ready resilience: transactions, schema contracts, explain/dry-run,
                         uncertainty bounds, execution tracing, and target compatibility (e.g. LeetCode).
```

---

## Domain Portfolio & Maturity Matrix

| Domain | Namespace Alias | Maturity Level | Core Capabilities | Primary Export Target |
| :--- | :--- | :--- | :--- | :--- |
| **Data Engineering** | `use data`, `etl`, `pipeline` | **Level 4: Professional** | Schema contracts, inner/left/right/outer joins, window functions (rank, row_number, lag, lead, cumulative sum), `explain` / `dry-run`, zero-eval AST expressions. | Python / Pandas / Polars |
| **DSA & Algorithms** | `use dsa`, `algo` | **Level 4: Professional** | Empirical Big-O complexity profiling ($O(1)$ to $O(2^n)$), peak memory tracing, recursion step visualization, LeetCode `class Solution:` target with `ListNode` and `TreeNode`. | Python / LeetCode |
| **Visualization** | `use viz`, `chart`, `plot` | **Level 4: Professional** | Unified Grammar of Graphics (Explore, Describe, Compose), typed `PlotSpec`, multi-layer geometry composability, text annotations, facet grids, color palettes. | Lets-Plot / Matplotlib |
| **Databases & SQL** | `use db`, `sql`, `database` | **Level 4: Professional** | Parameterized SQL query interpolation, table inspection, schema reflection, atomic transaction blocks (`transaction db:`) with auto-rollback. | `sqlite3` / SQLAlchemy |
| **Web & API Automation** | `use net`, `web`, `http` | **Level 4: Professional** | Declarative HTTP verbs (`request GET ...`), JSON parsing, exponential backoff retries, configurable timeouts, Bearer authentication, mutating request security policy gates. | `urllib` / `requests` |
| **Machine Learning** | `use ml` | **Level 4: Professional** | Data scaling, random seed control, K-fold cross validation (`cross validate ...`), model evaluation metrics, model persistence (`save model` / `load model`). | Scikit-Learn |
| **Simulation & Optimization** | `use sim`, `simulation` | **Level 4: Professional** | M/M/c queue discrete-event simulation, Monte Carlo sampling, Nelder-Mead downhill simplex, 95% uncertainty quantification, multi-trial experiments, parameter sweeps. | Pure Python / `scipy` |
| **NLP & Text Analytics** | `use nlp`, `text` | **Level 3: Stable** | Text cleaning and normalization, word/sentence tokenization, n-gram extraction, lexicon sentiment analysis with negation, TF-IDF vectorization, entity extraction. | Scikit-Learn / Regex |
| **Geospatial Analytics** | `use geo`, `spatial`, `gis` | **Level 3: Stable** | Geographic Points and Polygons, Haversine great-circle distance (km/miles/meters), ray-casting point-in-polygon containment, bounding box calculation, spatial joins, GeoJSON serialization. | Shapely / GeoPandas |
| **Operations Research** | `use opt`, `lp` | **Level 3: Stable** | Declarative linear programming (`maximize:` / `minimize:` / `subject to:`), linear expression parsing, pure-Python Two-Phase Simplex and Dual Simplex solver. | SciPy `linprog` |

---

## Domain Architecture & Contracts

Every domain implements the `DomainContract` ABC:

```python
class DomainContract(ABC):
    name: str
    aliases: List[str]
    parser: DomainParser
    runtime: DomainRuntime
    exporter: DomainASTExporter

    def can_handle_line(self, line: str) -> bool: ...
    def can_handle_block(self, header: str) -> bool: ...
```

1. **Independent Domain Parsers**: Domain grammars do not pollute the core Lark grammar. Each domain extracts and validates its own domain phrases into typed `DomainIR` objects.
2. **Safe AST Evaluation**: Dynamic expression filtering and calculated metrics execute via a sandboxed Python AST visitor (`SafeAstEvaluator`), completely eliminating unsafe `eval()`.
3. **Dual Execution Engine**:
   - **Interpreter Mode**: Evaluates `DomainIR` directly in the process scope for instant feedback and interactive learning.
   - **Export Mode**: Translates `DomainIR` into idiomatic, PEP 8-compliant Python AST nodes via `DomainASTExporter`.
4. **Conformance Testing**: The conformance test suite validates identical results between interpreter execution and exported Python AST scripts.
