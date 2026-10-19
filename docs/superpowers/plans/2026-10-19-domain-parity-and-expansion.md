# Domain Parity, Upgrade, and Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish semantic parity between execution and native Python export across all domains, upgrade existing domains with production features (data pipelines with explain/dry-run, LeetCode DSA tracing, unified visualization, ML experiment pipelines, DB/Net resilience, reproducible simulation), and introduce three new English-first domains (NLP, Geospatial, and Optimization) adhering to the shared domain contract and maturity ladder.

**Architecture:** A unified domain layer (`src/doomscript/domains/`) where each domain implements `DomainContract` (`DomainIR`, `DomainParser`, `DomainRuntime`, `DomainASTExporter`). A shared conformance test harness validates that interpreting DoomScript in-process and executing its exported Python AST produce identical results, schemas, and return values without unsafe `eval()`. Cross-domain data flows seamlessly as typed interoperable records.

**Tech Stack:** Python 3.10+, Lark, Python `ast`, pandas, numpy, scikit-learn (optional), lets-plot (optional), pytest.

**Spec:** User roadmap for DoomScript domain parity, 70% upgrades to existing domains, 30% new domains (`nlp`, `geo`, `opt`), and domain maturity ladder.

## Global Constraints

- Python >= 3.10 compatibility.
- English-first syntax for all user-facing domain features.
- Zero unsafe `eval()` calls in data transformations: all expression evaluation uses a typed/safe AST evaluator.
- Semantic parity between `engine.execute(code)` and `exec(engine.export_to_python(code))`.
- All optional dependencies (e.g., `lets_plot`, `scikit-learn`, `pandas`, `pyarrow`) must be guarded with graceful fallbacks and proper extras in `pyproject.toml`.
- Every domain adheres to `DomainContract` in `src/doomscript/domains/base.py`.

## Review Focus

1. **Unsafe expression injection in data expressions**: Ensure `SafeASTEvaluator` rejects dunder attributes (`__class__`, `__subclasses__`), imports, calls to non-whitelisted functions, and syntax errors with clear messages.
2. **Aggregation naming discrepancy**: Ensure exported pandas code renames aggregated columns to the target alias (`total_sales`) instead of leaving source column names (`amount`) or failing on `count` without a source column.
3. **DSA benchmark export fidelity**: Ensure exported DSA benchmarks perform live micro-benchmarks with `fit_complexity` and return a real `ComplexityReport` dictionary rather than static spec metadata.
4. **Isolated wheel installation and execution**: Ensure all domain packages, Lark grammars, and optional extras install and run in a clean, isolated virtualenv without relying on source-tree paths.
5. **Clean English syntax compatibility**: Ensure new domain keywords (`optimize`, `tokenize`, `point at`, `distance between`, `validate schema`) do not collide with standard DoomScript variables or existing statements.

---

### Task 1: Safe AST Evaluator & Elimination of eval() in Data Domain

**Files:**
- Create: `src/doomscript/domains/data/expr_eval.py`
- Modify: `src/doomscript/domains/data/runtime.py`
- Test: `tests/domains/test_data_safe_eval.py`

**Interfaces:**
- Produces: `SafeASTEvaluator.evaluate(expr_str: str, row: Dict[str, Any]) -> Any`
- Consumes: Python `ast`, standard safe arithmetic operators

- [ ] **Step 1: Write failing test for SafeASTEvaluator and precise errors on invalid expressions**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `SafeASTEvaluator` with whitelist of safe AST nodes (BinOp, UnaryOp, Compare, Name, Constant, Call on safe builtins)**
- [ ] **Step 4: Replace `eval()` in `src/doomscript/domains/data/runtime.py` with `SafeASTEvaluator.evaluate()`**
- [ ] **Step 5: Run tests and verify they pass**
- [ ] **Step 6: Commit changes**

---

### Task 2: Fix Data Domain Aggregations & DSA Benchmark Export Parity

**Files:**
- Modify: `src/doomscript/domains/data/exporter.py`
- Modify: `src/doomscript/domains/dsa/exporter.py`
- Modify: `src/doomscript/domains/dsa/runtime.py`
- Test: `tests/domains/test_export_parity_fixes.py`

**Interfaces:**
- Consumes: `DataPipelineSpec`, `BenchmarkSpec`
- Produces: Native Python AST generating exact runtime equivalence for aggregations and micro-benchmarks

- [ ] **Step 1: Write failing test comparing execution and exported Python for `calculate ... as count` and `benchmark ...`**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Update `DataASTExporter` to export pandas named aggregations and proper column aliases for `count`, `sum`, `avg`, `min`, `max`**
- [ ] **Step 4: Update `DsaASTExporter` to export the actual benchmarking loop and complexity curve fitting logic**
- [ ] **Step 5: Run tests and verify parity**
- [ ] **Step 6: Commit changes**

---

### Task 3: Shared Conformance Runner

**Files:**
- Create: `src/doomscript/testing/conformance.py`
- Test: `tests/conformance/test_domain_conformance.py`

**Interfaces:**
- Produces: `assert_execution_and_export_parity(source: str, expected_vars: List[str], check_approx: bool = False) -> None`
- Consumes: `engine.execute`, `engine.export_to_python`

- [ ] **Step 1: Write failing test using the conformance runner across core, data, and dsa**
- [ ] **Step 2: Implement `src/doomscript/testing/conformance.py` executing both paths in isolated execution dictionaries and asserting equality**
- [ ] **Step 3: Run conformance test suite to verify it passes**
- [ ] **Step 4: Commit changes**

---

### Task 4: Upgrade Data Engineering Domain (Joins, Schema Contracts, Window Functions, Explain/Dry-Run)

**Files:**
- Modify: `src/doomscript/domains/data/spec.py`
- Modify: `src/doomscript/domains/data/parser.py`
- Modify: `src/doomscript/domains/data/runtime.py`
- Modify: `src/doomscript/domains/data/exporter.py`
- Test: `tests/domains/test_data_engineering_advanced.py`

**Interfaces:**
- Produces:
  - `JoinStep(right_table: str, on: str, join_type: str = "inner")`
  - `SchemaValidateStep(schema: Dict[str, str])`
  - `WindowStep(func: str, target_col: str, order_by: str, partition_by: Optional[str])`
  - `explain_pipeline(spec: DataPipelineSpec) -> str`
  - `dry_run_pipeline(spec: DataPipelineSpec, scope: Dict[str, Any]) -> Dict[str, Any]`

- [ ] **Step 1: Write failing tests for join, schema contract validation, window functions, and `pipeline explain`**
- [ ] **Step 2: Add `JoinStep`, `SchemaValidateStep`, `WindowStep` to `spec.py`**
- [ ] **Step 3: Add English phrase parsing for joins (`join ... with ... on ...`), schema checks (`validate schema ...`), window functions (`calculate row_number over ...`), and explain (`explain pipeline ...`) in `parser.py`**
- [ ] **Step 4: Implement execution in `runtime.py` and AST export in `exporter.py`**
- [ ] **Step 5: Run tests and verify they pass**
- [ ] **Step 6: Commit changes**

---

### Task 5: Upgrade DSA Domain (LeetCode-Compatible Export & Execution Tracing)

**Files:**
- Modify: `src/doomscript/domains/dsa/spec.py`
- Modify: `src/doomscript/domains/dsa/parser.py`
- Modify: `src/doomscript/domains/dsa/runtime.py`
- Modify: `src/doomscript/domains/dsa/exporter.py`
- Test: `tests/domains/test_dsa_leetcode_and_tracing.py`

**Interfaces:**
- Produces:
  - `LeetCodeExportTarget`: generates `class Solution:` with ListNode/TreeNode and exact type annotations
  - `TraceRecursion`: captures execution call tree, stack frames, and returns
  - Built-in `ListNode` and `TreeNode` runtime classes

- [ ] **Step 1: Write failing tests for LeetCode solution export and recursion tracing**
- [ ] **Step 2: Implement `ListNode` and `TreeNode` in DSA domain runtime and export**
- [ ] **Step 3: Implement `trace recursion on <fn>` parser and runtime execution tracer**
- [ ] **Step 4: Update `DsaASTExporter` to generate accepted LeetCode Python class definitions**
- [ ] **Step 5: Run tests and verify they pass**
- [ ] **Step 6: Commit changes**

---

### Task 6: Upgrade Visualization Domain (Grammar of Graphics & Composable Layers)

**Files:**
- Modify: `src/doomscript/domains/viz.py`
- Modify: `src/doomscript/viz/exporter.py`
- Test: `tests/viz/test_composable_grammar.py`

**Interfaces:**
- Produces: Full support for facets (`facet by ...`), annotations (`annotate at ...`), scale transformations (`log scale on ...`), and AST export

- [ ] **Step 1: Write failing test for multi-layer composable plot and Python export**
- [ ] **Step 2: Implement facet, annotation, and scale attributes on `PlotSpec`**
- [ ] **Step 3: Update `VizASTExporter` to export native Lets-Plot or matplotlib AST**
- [ ] **Step 4: Run tests and verify they pass**
- [ ] **Step 5: Commit changes**

---

### Task 7: Upgrade Machine Learning Domain (Pipelines, Split Seeds, Cross-Validation, Persistence)

**Files:**
- Modify: `src/doomscript/domains/ml/spec.py`
- Modify: `src/doomscript/domains/ml/parser.py`
- Modify: `src/doomscript/domains/ml/runtime.py`
- Modify: `src/doomscript/domains/ml/exporter.py`
- Test: `tests/domains/test_ml_advanced.py`

**Interfaces:**
- Produces:
  - `split data into 80% train, 20% test with seed 42`
  - `cross validate model with 5 folds into cv_results`
  - `save model to "model.pkl"` / `load model from "model.pkl"`
  - `preprocess data: scale [...], encode [...]`

- [ ] **Step 1: Write failing tests for ML reproducible splits, CV, preprocessing, and persistence**
- [ ] **Step 2: Add spec and parser support for preprocessing, cross-validation, and persistence**
- [ ] **Step 3: Implement runtime logic with fallback and scikit-learn support**
- [ ] **Step 4: Update `MlASTExporter` to generate standalone Python script with sklearn**
- [ ] **Step 5: Run tests and verify they pass**
- [ ] **Step 6: Commit changes**

---

### Task 8: Upgrade Databases & Networking Domains (Resilience, Safety, & Boundaries)

**Files:**
- Modify: `src/doomscript/domains/db/` (`spec.py`, `parser.py`, `runtime.py`, `exporter.py`)
- Modify: `src/doomscript/domains/net/` (`spec.py`, `parser.py`, `runtime.py`, `exporter.py`)
- Test: `tests/domains/test_db_net_resilience.py`

**Interfaces:**
- Produces:
  - `query db "..." with [...]`: strictly parameterized query execution preventing injection
  - `transaction db:` context-managed atomic transactions
  - `request GET "..." with timeout 5 seconds retry 3 times with bearer token "..."`
  - Permission checks for mutating network methods (POST, PUT, DELETE)

- [ ] **Step 1: Write failing tests for parameterized DB queries, transactions, and net retry/timeout/auth**
- [ ] **Step 2: Implement parameterized SQL parsing and transaction block execution in `db`**
- [ ] **Step 3: Implement timeout, retry with backoff, and bearer token auth in `net`**
- [ ] **Step 4: Implement corresponding Python AST exporters for `db` (sqlite3) and `net` (requests / urllib)**
- [ ] **Step 5: Run tests and verify they pass**
- [ ] **Step 6: Commit changes**

---

### Task 9: Upgrade Simulation Domain (Seeds, Sweeps, Uncertainty, & Provenance)

**Files:**
- Modify: `src/doomscript/domains/sim/` (`spec.py`, `parser.py`, `runtime.py`, `exporter.py`)
- Test: `tests/domains/test_sim_experiments.py`

**Interfaces:**
- Produces:
  - `seed simulation with 42`
  - `sweep param over [...]`
  - `run N trials into results`
  - `summarize uncertainty of ... into ...` (confidence intervals, mean, std error)

- [ ] **Step 1: Write failing tests for reproducible seeds, parameter sweeps, and uncertainty summaries**
- [ ] **Step 2: Implement simulation seed and parameter sweep parser and runtime**
- [ ] **Step 3: Implement uncertainty calculation (95% CI) and simulation exporter**
- [ ] **Step 4: Run tests and verify they pass**
- [ ] **Step 5: Commit changes**

---

### Task 10: New Domain — NLP and Text Analytics (`use nlp`)

**Files:**
- Create: `src/doomscript/domains/nlp/__init__.py`
- Create: `src/doomscript/domains/nlp/spec.py`
- Create: `src/doomscript/domains/nlp/parser.py`
- Create: `src/doomscript/domains/nlp/runtime.py`
- Create: `src/doomscript/domains/nlp/exporter.py`
- Modify: `src/doomscript/domains/registry.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/domains/test_nlp_domain.py`

**Interfaces:**
- Produces:
  - `use nlp`
  - `tokenize text into tokens` / `sentences`
  - `clean text in s into clean_s`
  - `extract N-grams from text into ngrams`
  - `calculate tfidf of docs into matrix`
  - `extract frequent phrases from text into keywords`
  - `analyze sentiment of text into sentiment`

- [ ] **Step 1: Write failing unit and integration tests for NLP domain**
- [ ] **Step 2: Create `NlpSpec`, `NlpParser`, `NlpRuntime`, and `NlpASTExporter` with pure-python fallback and scikit-learn compatibility**
- [ ] **Step 3: Register `NlpDomain` in `get_domain_registry()` and add phrase mappings in `phrases.py`**
- [ ] **Step 4: Run tests and verify NLP execution and Python export parity**
- [ ] **Step 5: Commit changes**

---

### Task 11: New Domain — Geospatial Analytics (`use geo`)

**Files:**
- Create: `src/doomscript/domains/geo/__init__.py`
- Create: `src/doomscript/domains/geo/spec.py`
- Create: `src/doomscript/domains/geo/parser.py`
- Create: `src/doomscript/domains/geo/runtime.py`
- Create: `src/doomscript/domains/geo/exporter.py`
- Modify: `src/doomscript/domains/registry.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/domains/test_geo_domain.py`

**Interfaces:**
- Produces:
  - `use geo`
  - `point at (lat, lon) into p` / `point at latitude ..., longitude ...`
  - `polygon with coords [...] into poly`
  - `distance between p1 and p2 into dist` (Haversine formula in km/miles)
  - `spatial join points with polygons on contains into mapped`
  - `aggregate points by region into region_stats`
  - `export layer as geojson into "layer.geojson"`

- [ ] **Step 1: Write failing unit and integration tests for Geospatial domain**
- [ ] **Step 2: Create `GeoSpec`, `GeoParser`, `GeoRuntime`, and `GeoASTExporter` with pure-python geometry and optional shapely fallback**
- [ ] **Step 3: Register `GeoDomain` in `get_domain_registry()` and add phrase mappings in `phrases.py`**
- [ ] **Step 4: Run tests and verify Geospatial execution and Python export parity**
- [ ] **Step 5: Commit changes**

---

### Task 12: New Domain — Optimization & Operations Research (`use opt`)

**Files:**
- Create: `src/doomscript/domains/opt/__init__.py`
- Create: `src/doomscript/domains/opt/spec.py`
- Create: `src/doomscript/domains/opt/parser.py`
- Create: `src/doomscript/domains/opt/runtime.py`
- Create: `src/doomscript/domains/opt/exporter.py`
- Modify: `src/doomscript/domains/registry.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/domains/test_opt_domain.py`

**Interfaces:**
- Produces:
  - `use opt`
  - Declarative optimization block:
    ```doomscript
    optimize production:
        maximize: 5 * x + 4 * y
        subject to:
            x + 2 * y <= 14
            3 * x - y >= 0
            x >= 0, y >= 0
    solve production into result
    ```
  - Solves linear programs and extracts optimal variable values and objective value
  - Pure Python Simplex solver with Scipy `scipy.optimize.linprog` exporter

- [x] **Step 1: Write failing unit and integration tests for Optimization domain**
- [x] **Step 2: Create `OptimizationSpec`, `OptParser`, `OptRuntime` (with Simplex solver), and `OptASTExporter`**
- [x] **Step 3: Register `OptDomain` in `get_domain_registry()` and add phrase mappings in `phrases.py`**
- [x] **Step 4: Run tests and verify Optimization execution and Python export parity**
- [x] **Step 5: Commit changes**

---

### Task 13: Domain Maturity Ladder & Documentation

**Files:**
- Create: `docs/DOMAIN_MATURITY.md`
- Modify: `src/doomscript/domains/base.py`
- Modify: `pyproject.toml`
- Test: `tests/test_domain_maturity.py`

**Interfaces:**
- Produces:
  - Domain maturity registry metadata: `domain.maturity` ("prototype", "usable", "stable", "professional")
  - Complete documentation and CLI listing of domain status
  - Updated `pyproject.toml` optional dependencies for all domains

- [x] **Step 1: Write test verifying all registered domains declare valid maturity level and optional dependencies**
- [x] **Step 2: Update `DomainContract` with maturity metadata and update all domain implementations**
- [x] **Step 3: Update `pyproject.toml` with `nlp`, `geo`, `opt`, and `all` extras**
- [x] **Step 4: Write comprehensive `docs/DOMAIN_MATURITY.md` table and guide**
- [x] **Step 5: Run tests and verify they pass**
- [x] **Step 6: Commit changes**

---

### Task 14: Final Full Conformance & Wheel Packaging Validation

**Files:**
- Modify: `tests/test_wheel_packaging.py`
- Test: Full test suite (`pytest`)

**Interfaces:**
- Verifies all 9 domains pass isolated wheel packaging tests and full test suite

- [x] **Step 1: Build wheel with all package data and dependencies**
- [x] **Step 2: Execute comprehensive multi-domain program in clean isolated virtualenv**
- [x] **Step 3: Run full pytest suite across all 400+ tests**
- [x] **Step 4: Commit changes and push to origin/main**
