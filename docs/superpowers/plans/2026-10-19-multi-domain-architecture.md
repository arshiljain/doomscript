# Multi-Domain Language Architecture Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform DoomScript into a general-purpose core with a unified Domain-Extension Architecture and implement 6 complete English-first domain packs (Data Engineering, Machine Learning, Databases & SQL, Web & API Automation, Simulation & Optimization, and Testing & Algorithm Analysis) with typed IR, execution runtimes, and native Python AST exporters.

**Architecture:** Introduce `doomscript.domains.base` defining `DomainContract`, `DomainParser`, `DomainIR`, `DomainRuntime`, and `DomainASTExporter`. A central `DomainRegistry` dynamically activates domains via `use <domain>` or unambiguous syntax. Each domain provides independent parsing, semantic validation into typed IR, in-memory execution, and safe Python AST generation for `doom export`.

**Tech Stack:** Python 3.10+, typed AST (`ast` module), Lark, standard library (`urllib`, `sqlite3`, `tracemalloc`, `heapq`, `random`, `math`), optional extras (`pandas`, `scikit-learn`, `lets-plot`).

**Spec:** [docs/superpowers/specs/2026-10-19-multi-domain-architecture-design.md](file:///C:/Users/kanha/.gemini/antigravity/scratch/doomscript/docs/superpowers/specs/2026-10-19-multi-domain-architecture-design.md)

## Global Constraints
- Every domain pack must implement the 3-level contract: Level 1 (Inspect/Explore), Level 2 (Single Operation), Level 3 (Compose Workflow).
- Core language and independent domain runtimes must function with zero mandatory external dependencies; optional accelerators (`pandas`, `scikit-learn`, `lets-plot`) are used when available.
- Code generation in `doom export` must construct typed Python `ast.AST` nodes safely, never concatenating raw source strings or evaluating with `eval()`.
- Backward compatibility: All existing 200 English corpus tests, DSA algorithms, research autograd, and `lets-plot` visualization tests must remain 100% passing.

## Review Focus
- Unregistered domain usage: unambiguous keywords auto-activate the domain or provide a clear hint to add `use <domain>`.
- Mixed-type schema validation in Data Engineering pipelines: reporting descriptive type errors instead of unhandled exceptions.
- Zero-dependency ML fallback: basic classification and regression models execute cleanly when `scikit-learn` is absent.
- SQL injection immunity: queries parameterized with value placeholders rather than string formatting.
- Empirical complexity fit stability: handling small or noisy timing data without failing regression fitting.

---

### Task 1: Core Domain Extension Architecture (`doomscript.domains.base` & Registry)

**Files:**
- Create: `src/doomscript/domains/__init__.py`
- Create: `src/doomscript/domains/base.py`
- Create: `src/doomscript/domains/registry.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `src/doomscript/compiler/engine.py`
- Test: `tests/domains/test_core_registry.py`

**Interfaces:**
- Produces: `DomainIR`, `DomainParser`, `DomainRuntime`, `DomainASTExporter`, `DomainContract`, `DomainRegistry`, `get_domain_registry()`.
- Consumes: Core compiler pipeline in `engine.py` and phrase normalizer in `phrases.py`.

- [ ] **Step 1: Write failing test for domain registry and lifecycle**

```python
# tests/domains/test_core_registry.py
def test_domain_registration_and_activation():
    from doomscript.domains.registry import DomainRegistry
    from doomscript.domains.base import DomainContract, DomainParser, DomainIR, DomainRuntime, DomainASTExporter

    registry = DomainRegistry()
    assert not registry.is_active("mock")
    registry.activate("mock")
    # Fails because mock domain is not registered yet
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_core_registry.py -v`  
Expected: FAIL (ImportError / module not found).

- [ ] **Step 3: Implement `base.py` and `registry.py`**

Define `DomainIR`, `DomainParser`, `DomainRuntime`, `DomainASTExporter`, `DomainContract`, and `DomainRegistry`. Implement namespace activation (`use <domain>`) and line/block dispatch.

- [ ] **Step 4: Integrate domain dispatch in `phrases.py` and `engine.py`**

Hook `use <name>` into phrase normalization to activate registered domains and delegate recognized block headers to domain parsers.

- [ ] **Step 5: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_core_registry.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/doomscript/domains/ tests/domains/test_core_registry.py src/doomscript/grammar/phrases.py src/doomscript/compiler/engine.py
git commit -m "feat(domains): add core domain extension architecture and registry"
```

---

### Task 2: Data Engineering Domain Pack (`use data`)

**Files:**
- Create: `src/doomscript/domains/data/spec.py`
- Create: `src/doomscript/domains/data/parser.py`
- Create: `src/doomscript/domains/data/runtime.py`
- Create: `src/doomscript/domains/data/exporter.py`
- Create: `src/doomscript/domains/data/__init__.py`
- Test: `tests/domains/test_data_domain.py`

**Interfaces:**
- Produces: `PipelineSpec`, `ValidationRule`, `PipelineStep`, `DataDomainParser`, `DataPipelineRuntime`, `DataASTExporter`.
- Consumes: `DomainContract` from `doomscript.domains.base`.

- [ ] **Step 1: Write failing unit and integration tests for Data Engineering**

```python
# tests/domains/test_data_domain.py
def test_pipeline_spec_execution_and_export():
    from doomscript.compiler.engine import execute, export_to_python
    source = """use data
orders = [
    {"id": 1, "region": "North", "amount": 100},
    {"id": 2, "region": "South", "amount": 200},
    {"id": 1, "region": "North", "amount": 100}
]
pipeline "clean_orders" from orders into output_data:
    remove duplicate rows by "id"
    derive "tax" as amount * 0.1
    group by region:
        calculate total as sum of amount
"""
    env = execute(source)
    assert len(env["output_data"]) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_data_domain.py -v`  
Expected: FAIL (unrecognized syntax / domain not loaded).

- [ ] **Step 3: Implement `PipelineSpec` and AST components**

Create `PipelineSpec` with step dataclasses (`DedupeStep`, `FilterStep`, `FillNaStep`, `DeriveStep`, `JoinStep`, `GroupByStep`, `SortStep`, `SinkStep`, `ValidationRule`).

- [ ] **Step 4: Implement `DataDomainParser`**

Parse Level 1 (`inspect dataset`, `profile`), Level 2 (`clean`, `join`, `fill missing`), and Level 3 (`pipeline: ...`).

- [ ] **Step 5: Implement `DataPipelineRuntime` and `DataASTExporter`**

Execute pipeline steps against DoomScript `Record` / dict lists with fallback or Pandas. Construct safe Python AST statements in `DataASTExporter`.

- [ ] **Step 6: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_data_domain.py -v`  
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add src/doomscript/domains/data/ tests/domains/test_data_domain.py
git commit -m "feat(domains): implement Data Engineering domain pack (PipelineSpec, runtime, exporter)"
```

---

### Task 3: Machine Learning Domain Pack (`use ml`)

**Files:**
- Create: `src/doomscript/domains/ml/spec.py`
- Create: `src/doomscript/domains/ml/parser.py`
- Create: `src/doomscript/domains/ml/runtime.py`
- Create: `src/doomscript/domains/ml/fallback.py`
- Create: `src/doomscript/domains/ml/exporter.py`
- Create: `src/doomscript/domains/ml/__init__.py`
- Test: `tests/domains/test_ml_domain.py`

**Interfaces:**
- Produces: `ModelSpec`, `FeatureSpec`, `TrainingSpec`, `MLDomainParser`, `MLRuntime`, `MLASTExporter`.
- Consumes: `DomainContract` from `doomscript.domains.base`.

- [ ] **Step 1: Write failing tests for Machine Learning syntax, training, and export**

```python
# tests/domains/test_ml_domain.py
def test_ml_model_declaration_train_evaluate():
    from doomscript.compiler.engine import execute
    source = """use ml
dataset = [
    {"age": 25, "income": 50000, "buy": 1},
    {"age": 45, "income": 90000, "buy": 1},
    {"age": 18, "income": 15000, "buy": 0},
    {"age": 22, "income": 20000, "buy": 0}
]
model buyer_model from dataset:
    target: "buy"
    features: "age", "income"
    algorithm: decision_tree
    split: 75% training, 25% testing

train buyer_model
evaluate buyer_model into metrics
assert metrics's accuracy >= 0.0
"""
    env = execute(source)
    assert "buyer_model" in env
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_ml_domain.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement `ModelSpec` and pure Python fallback classifiers**

Support `decision_tree`, `random_forest`, `linear_regression`, `logistic_regression`, and `knn` with zero-dependency native estimators when `scikit-learn` is absent.

- [ ] **Step 4: Implement `MLDomainParser`, `MLRuntime`, and `MLASTExporter`**

Parse Level 1 (`inspect model`, `summarize features`), Level 2 (`split`, `predict`, `evaluate`), Level 3 (`model: ...`, `train`). Generate `sklearn` Python AST statements.

- [ ] **Step 5: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_ml_domain.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/doomscript/domains/ml/ tests/domains/test_ml_domain.py
git commit -m "feat(domains): implement Machine Learning domain pack (ModelSpec, zero-dep fallback, sklearn exporter)"
```

---

### Task 4: Databases & SQL Domain Pack (`use db`)

**Files:**
- Create: `src/doomscript/domains/db/spec.py`
- Create: `src/doomscript/domains/db/parser.py`
- Create: `src/doomscript/domains/db/runtime.py`
- Create: `src/doomscript/domains/db/exporter.py`
- Create: `src/doomscript/domains/db/__init__.py`
- Test: `tests/domains/test_db_domain.py`

**Interfaces:**
- Produces: `QuerySpec`, `ConditionSpec`, `JoinSpec`, `DBDomainParser`, `DBRuntime`, `SQLASTExporter`.
- Consumes: `DomainContract` from `doomscript.domains.base`.

- [ ] **Step 1: Write failing tests for SQL queries and schema reflection**

```python
# tests/domains/test_db_domain.py
def test_db_query_execution():
    from doomscript.compiler.engine import execute
    source = """use db
users = [
    {"name": "Alice", "role": "admin", "score": 95},
    {"name": "Bob", "role": "user", "score": 80},
    {"name": "Charlie", "role": "admin", "score": 90}
]
query top_admins from users into top_list:
    select name, score
    where role is "admin" and score >= 90
    order by score descending
    limit 5
"""
    env = execute(source)
    assert len(env["top_list"]) == 2
    assert env["top_list"][0]["name"] == "Alice"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_db_domain.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement `QuerySpec` and `DBDomainParser`**

Parse Level 1 (`inspect schema`, `explain query`), Level 2 (`insert`, `update`, `delete`), Level 3 (`query: ...` with `select`, `where`, `join`, `group by`, `order by`, `limit`).

- [ ] **Step 4: Implement `DBRuntime` and `SQLASTExporter`**

Execute queries against in-memory records and SQLite databases with parameterized SQL. Generate clean `sqlite3` Python AST statements.

- [ ] **Step 5: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_db_domain.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/doomscript/domains/db/ tests/domains/test_db_domain.py
git commit -m "feat(domains): implement Databases & SQL domain pack (QuerySpec, parameterized engine, AST exporter)"
```

---

### Task 5: Web & API Automation Domain Pack (`use net`)

**Files:**
- Create: `src/doomscript/domains/net/spec.py`
- Create: `src/doomscript/domains/net/parser.py`
- Create: `src/doomscript/domains/net/runtime.py`
- Create: `src/doomscript/domains/net/exporter.py`
- Create: `src/doomscript/domains/net/__init__.py`
- Test: `tests/domains/test_net_domain.py`

**Interfaces:**
- Produces: `ApiWorkflowSpec`, `RequestSpec`, `RetryPolicySpec`, `NetDomainParser`, `NetRuntime`, `NetASTExporter`.
- Consumes: `DomainContract` from `doomscript.domains.base`.

- [ ] **Step 1: Write failing tests for API workflows and retries**

```python
# tests/domains/test_net_domain.py
def test_net_api_workflow_definition_and_export():
    from doomscript.compiler.engine import compile_to_ast, export_to_python
    source = """use net
workflow "fetch_orders":
    base url: "https://api.example.com"
    header "Authorization": "Bearer token123"
    retry up to 3 times
    timeout: 5 seconds
    request GET "/v1/orders" into orders_resp
"""
    py_code = export_to_python(source)
    assert "urllib.request" in py_code or "requests" in py_code
    assert "retry" in py_code.lower() or "for attempt in range" in py_code
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_net_domain.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement `ApiWorkflowSpec` and `NetDomainParser`**

Parse Level 1 (`ping`, `inspect response`), Level 2 (`request GET/POST`, `parse response`), Level 3 (`workflow "name": ...`).

- [ ] **Step 4: Implement `NetRuntime` and `NetASTExporter`**

Implement robust zero-dep HTTP client with exponential backoff and timeout support via `urllib.request`. Construct retry-loop Python AST in `NetASTExporter`.

- [ ] **Step 5: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_net_domain.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/doomscript/domains/net/ tests/domains/test_net_domain.py
git commit -m "feat(domains): implement Web & API domain pack (ApiWorkflowSpec, retry engine, AST exporter)"
```

---

### Task 6: Simulation & Optimization Domain Pack (`use sim`)

**Files:**
- Create: `src/doomscript/domains/sim/spec.py`
- Create: `src/doomscript/domains/sim/parser.py`
- Create: `src/doomscript/domains/sim/runtime.py`
- Create: `src/doomscript/domains/sim/exporter.py`
- Create: `src/doomscript/domains/sim/__init__.py`
- Test: `tests/domains/test_sim_domain.py`

**Interfaces:**
- Produces: `SimulationSpec`, `OptimizationSpec`, `SimDomainParser`, `SimRuntime`, `SimASTExporter`.
- Consumes: `DomainContract` from `doomscript.domains.base`.

- [ ] **Step 1: Write failing tests for queue simulation and numerical optimization**

```python
# tests/domains/test_sim_domain.py
def test_sim_queue_simulation():
    from doomscript.compiler.engine import execute
    source = """use sim
simulate queue_test into sim_report:
    arrivals: poisson with rate 10
    service: exponential with rate 12
    servers: 1
    duration: 500 events
    track waiting_time

say "Simulated events:", sim_report's total_events
assert sim_report's total_events >= 500
"""
    env = execute(source)
    assert env["sim_report"]["total_events"] >= 500
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_sim_domain.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement `SimulationSpec`, `OptimizationSpec`, and `SimDomainParser`**

Parse Level 1 (`inspect simulation`, `profile distribution`), Level 2 (`sample`, `minimize`), Level 3 (`simulate: ...`).

- [ ] **Step 4: Implement `SimRuntime` and `SimASTExporter`**

Pure-Python discrete-event queue simulator with `heapq` and Monte Carlo distribution generator. Nelder-Mead / gradient descent function optimizer. Generate Python AST for export.

- [ ] **Step 5: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_sim_domain.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/doomscript/domains/sim/ tests/domains/test_sim_domain.py
git commit -m "feat(domains): implement Simulation & Optimization domain pack (SimulationSpec, queue runtime, AST exporter)"
```

---

### Task 7: Testing & Algorithm Analysis Domain Pack (`use dsa`)

**Files:**
- Create: `src/doomscript/domains/dsa/spec.py`
- Create: `src/doomscript/domains/dsa/parser.py`
- Create: `src/doomscript/domains/dsa/runtime.py`
- Create: `src/doomscript/domains/dsa/exporter.py`
- Create: `src/doomscript/domains/dsa/__init__.py`
- Test: `tests/domains/test_dsa_domain.py`

**Interfaces:**
- Produces: `BenchmarkSpec`, `EmpiricalScalingSpec`, `DSADomainParser`, `DSARuntime`, `DSAASTExporter`.
- Consumes: `DomainContract` from `doomscript.domains.base`.

- [ ] **Step 1: Write failing tests for empirical complexity fitting and benchmarking**

```python
# tests/domains/test_dsa_domain.py
def test_dsa_benchmark_and_complexity():
    from doomscript.compiler.engine import execute
    source = """use dsa
define function simple_loop(n):
    total = 0
    repeat n times:
        total = total + 1
    return total

benchmark test_bench:
    target: simple_loop
    input sizes: [100, 500, 1000]
    repeat: 3
    fit complexity: auto

assert test_bench's complexity_order in ["O(n)", "O(1)"]
"""
    env = execute(source)
    assert "test_bench" in env
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/domains/test_dsa_domain.py -v`  
Expected: FAIL.

- [ ] **Step 3: Implement `BenchmarkSpec` and `DSADomainParser`**

Parse Level 1 (`analyze complexity`), Level 2 (`time execution`, `measure memory`), Level 3 (`benchmark: ...`).

- [ ] **Step 4: Implement `DSARuntime` and `DSAASTExporter`**

High-resolution timing (`perf_counter_ns`), memory tracking (`tracemalloc`), and curve fitting selecting best fit among $O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$. AST exporter emitting stand-alone benchmarking scripts.

- [ ] **Step 5: Run tests and verify they pass**

Run: `python -m pytest tests/domains/test_dsa_domain.py -v`  
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add src/doomscript/domains/dsa/ tests/domains/test_dsa_domain.py
git commit -m "feat(domains): implement Testing & Algorithm Analysis domain pack (BenchmarkSpec, complexity fitter, AST exporter)"
```

---

### Task 8: Domain Unification, Cross-Domain End-to-End Workflow & Release Verification

**Files:**
- Create: `src/doomscript/domains/viz.py` (bridging existing `PlotSpec`/`PlotBuilder`/`LetsPlotExporter` to `DomainContract`)
- Create: `src/doomscript/domains/research.py` (bridging existing research autograd/graph/stats to `DomainContract`)
- Create: `examples/end_to_end_multidomain.doom`
- Create: `tests/domains/test_cross_domain_integration.py`
- Modify: `README.md`
- Test: Full Pytest test suite & English Corpus benchmark

**Interfaces:**
- Produces: Complete unified multi-domain runtime environment where all domains interoperate seamlessly.
- Consumes: All 6 new domain packs + `viz` + `research`.

- [ ] **Step 1: Write integration test exercising cross-domain collaboration**

```python
# tests/domains/test_cross_domain_integration.py
def test_cross_domain_pipeline_to_viz_to_dsa():
    from doomscript.compiler.engine import execute
    source = """use data
use dsa
data = [{"val": 10}, {"val": 20}, {"val": 30}]
pipeline "transform" from data into clean_data:
    derive "doubled" as val * 2

time execution of count_of(clean_data) into elapsed_time
assert len(clean_data) == 3
"""
    env = execute(source)
    assert len(env["clean_data"]) == 3
```

- [ ] **Step 2: Bridge `viz` and `research` to `DomainContract`**

Register `use viz` and `use research` in `DomainRegistry` so all domains share one identical lifecycle and namespace rules.

- [ ] **Step 3: Create `examples/end_to_end_multidomain.doom`**

Showcase the full power: data pipeline ETL -> ML training -> simulation -> visualization -> algorithm benchmark.

- [ ] **Step 4: Update Documentation in `README.md`**

Document the "One Language, Many Domains" architecture, domain namespaces (`use data`, `use ml`, etc.), and syntax tables.

- [ ] **Step 5: Run full test suite and English corpus benchmark**

Run:
```bash
python -m pytest tests/ -v
python run_corpus.py --fail-under 95
```
Expected: All tests pass (Core + Viz + Packaging + Domains) and 200/200 English corpus pass (100%).

- [ ] **Step 6: Commit & Push**

```bash
git add .
git commit -m "feat(domains): complete multi-domain language architecture with 6 full domain packs"
git push origin main
```
