# Architecture Specification: DoomScript Multi-Domain Language Architecture

**Date**: 2026-10-19  
**Status**: Proposed  
**Author**: Antigravity & DoomScript Core Team  
**Scope**: Core Domain Architecture + 6 Complete Domain Packs (Data Engineering, Machine Learning, Databases & SQL, Web & API Automation, Simulation & Optimization, Testing & Algorithm Analysis)

---

## 1. Executive Summary & Vision

DoomScript is evolving from a single monolithic English syntax into a **General-Purpose Core Language with a First-Class Domain Extension Architecture**. 

Instead of cramming hundreds of domain-specific verbs into a single unbounded regex preprocessor or bloating the core LALR(1) grammar into ambiguity, DoomScript introduces **independent domain parsers behind a shared domain contract**. 

Users write idiomatic DoomScript for general-purpose programming (variables, functions, loops, contracts, records), and seamlessly activate domain languages using explicit namespaces (`use data`, `use ml`, `use db`, `use net`, `use sim`, `use dsa`, `use viz`, `use research`) with automatic unqualified resolution when phrasings are unambiguous.

Each domain conforms strictly to the **DoomScript Domain Contract**:
1. **Level 1 — Inspect & Explore**: Introspect structures, profile data, inspect schemas, query metadata.
2. **Level 2 — Single Operation**: Execute focused actions directly (clean, predict, query, request, sample, time).
3. **Level 3 — Compose Workflow**: Declarative blocks constructing a domain specification (`pipeline`, `model`, `query`, `workflow`, `simulate`, `benchmark`, `chart`).
4. **Typed Intermediate Representation (IR)**: Validated, inspectable, serialization-ready AST dataclasses.
5. **Execution Runtime**: In-memory execution engine with zero mandatory third-party runtime dependencies, leveraging accelerated libraries (`pandas`, `scikit-learn`, `lets-plot`) when installed.
6. **Native Python AST Exporter**: Direct compilation of domain IR into clean, standalone Python AST statements (via `ast` nodes, unparsed cleanly) for `doom export`.

---

## 2. Shared Domain Architecture (`doomscript.domains.base`)

### 2.1 The Domain Contract

Every domain pack implements `DomainContract`:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple, Type
import ast

class DomainIR(ABC):
    """Abstract base class for all domain specification intermediate representations."""
    @abstractmethod
    def validate(self) -> List[str]:
        """Returns list of semantic validation errors if any."""
        ...

class DomainParser(ABC):
    """Independent domain parser operating on source tokens or block lines."""
    @abstractmethod
    def parse_inspect(self, line: str, line_no: int) -> Optional[DomainIR]:
        ...
    @abstractmethod
    def parse_operation(self, line: str, line_no: int) -> Optional[ast.stmt]:
        ...
    @abstractmethod
    def parse_block(self, header: str, body_lines: List[Tuple[int, str]], indent: int) -> Tuple[DomainIR, str]:
        """Parses a Level 3 declarative block into a DomainIR and target variable name."""
        ...

class DomainRuntime(ABC):
    """Execution engine for domain operations and workflows."""
    @abstractmethod
    def execute_ir(self, ir: DomainIR, scope: Dict[str, Any]) -> Any:
        ...

class DomainASTExporter(ABC):
    """Translates DomainIR into safe native Python AST statements."""
    @abstractmethod
    def to_ast(self, ir: DomainIR, var_name: str, scope: Optional[Dict[str, Any]] = None) -> Tuple[Set[str], List[ast.stmt]]:
        ...

class DomainContract(ABC):
    """Formal contract required for all DoomScript domain packs."""
    name: str
    aliases: List[str]
    parser: DomainParser
    runtime: DomainRuntime
    exporter: DomainASTExporter

    @abstractmethod
    def can_handle_line(self, line: str) -> bool:
        ...

    @abstractmethod
    def can_handle_block(self, header: str) -> bool:
        ...
```

### 2.2 The Central Domain Registry (`DomainRegistry`)

* Maintains active domain scopes per compilation context.
* Tracks declared namespaces: `use data`, `use ml`, `use db`, `use net`, `use sim`, `use dsa`, `use viz`, `use research`.
* Intercepts `use <domain>` declarations during lexical preprocessing and activates domain-specific parsers.
* Provides graceful fallback: if unambiguous domain keywords are used without an explicit `use`, the registry detects the domain signature and auto-activates it with an informative compilation trace.

---

## 3. The Six Domain Packs

### 3.1 Data Engineering Pack (`use data`)

Transforms raw files, records, and tables into validated, cleaned, and aggregated data pipelines.

#### Syntax Surface:
* **Level 1 (Inspect)**:
  * `inspect dataset <data>`
  * `profile <data> into <summary>`
* **Level 2 (Single Operation)**:
  * `clean <data> by removing nulls in "<col>" into <target>`
  * `fill missing "<col>" with <val> in <data> into <target>`
  * `join <left> and <right> on "<key>" as (inner|left|right|outer) into <target>`
* **Level 3 (Pipeline Block)**:
  ```doomscript
  pipeline "monthly_sales" from "data/sales.csv" into monthly_report:
      validate:
          require "region" is text
          require "revenue" is positive number
          forbid nulls in "order_id"

      remove duplicate rows by "order_id"
      fill missing "discount" with 0.0
      derive "net_revenue" as revenue * (1.0 - discount)

      group by region, month:
          calculate total_revenue as sum of net_revenue
          calculate average_order as mean of net_revenue
          calculate order_count as count

      sort by total_revenue descending
      write to "output/monthly_report.csv"
  ```

#### Intermediate Representation (`PipelineSpec`):
* `PipelineSpec(name, source, target, validations, steps, sink)`
* `ValidationRule(kind, column, rule_type)`
* `PipelineStep`: `DedupeStep`, `FilterStep`, `FillNaStep`, `DeriveStep`, `JoinStep`, `GroupByStep`, `SortStep`, `SinkStep`.

#### Runtime Engine:
* Works seamlessly on native DoomScript `Record` objects, standard lists of dicts, and tabular data.
* If `pandas` is installed, uses vectorized DataFrame transforms; otherwise falls back to pure Python standard library data engines.

#### Exporter (`DataASTExporter`):
* Emits readable, idiomatic native Python AST using `pandas` (or standard `csv` + dictionary processing) for `doom export`.

---

### 3.2 Machine Learning Pack (`use ml`)

Brings human-readable model definition, feature extraction, train/test splitting, training, and evaluation to DoomScript.

#### Syntax Surface:
* **Level 1 (Inspect)**:
  * `inspect model <model_var>`
  * `summarize features of <data> for target "<target_col>"`
* **Level 2 (Single Operation)**:
  * `split <data> into train_data, test_data with ratio 0.8`
  * `predict <model> on <new_data> into predictions`
  * `evaluate <model> on <test_data> into metrics`
* **Level 3 (Model Workflow Block)**:
  ```doomscript
  model churn_predictor from customers:
      target: "churned"
      features: "age", "monthly_spend", "support_tickets", "plan_type"
      algorithm: random_forest
      hyperparameters:
          trees: 100
          max_depth: 10
      split: 80% training, 20% testing

  train churn_predictor
  evaluate churn_predictor into eval_results
  say "Model Accuracy:", eval_results's accuracy
  ```

#### Intermediate Representation (`ModelSpec`):
* `ModelSpec(name, dataset, target_col, feature_cols, algorithm, hyperparameters, split_ratio)`
* Supported algorithms: `random_forest`, `decision_tree`, `linear_regression`, `logistic_regression`, `knn`, `naive_bayes`.

#### Runtime Engine:
* Integrates with `scikit-learn` if present.
* Includes a lightweight built-in decision tree and regression fallback in `doomscript.domains.ml.fallback` for zero-dependency execution.

#### Exporter (`MLASTExporter`):
* Generates native Python AST:
  ```python
  from sklearn.ensemble import RandomForestClassifier
  from sklearn.model_selection import train_test_split
  from sklearn.metrics import accuracy_score, classification_report
  ...
  ```

---

### 3.3 Databases & SQL Pack (`use db`)

Safe, parameterized relational queries and schema reflection.

#### Syntax Surface:
* **Level 1 (Inspect)**:
  * `inspect schema of <db_connection_or_table>`
  * `explain query <query_var>`
* **Level 2 (Single Operation)**:
  * `insert into "employees" values (name="Alice", salary=120000)`
  * `update "employees" set salary=130000 where name is "Alice"`
  * `delete from "employees" where salary is less than 50000`
* **Level 3 (Query Block)**:
  ```doomscript
  query high_earners from "employees" into top_talent:
      select name, department, salary
      where salary is over 100000 and status is "active"
      join "departments" on employees.dept_id equals departments.id
      group by department:
          calculate max_salary as max of salary
      order by max_salary descending
      limit 10
  ```

#### Intermediate Representation (`QuerySpec`):
* `QuerySpec(table, target, columns, conditions, joins, group_by, aggregations, order_by, limit)`
* Separates query structure from parameters to prevent SQL injection.

#### Runtime Engine:
* Connects to SQLite (built-in `sqlite3`), in-memory tables, or active DB-API 2.0 connections.

#### Exporter (`SQLASTExporter`):
* Generates clean Python code executing parameterized SQL statements via `sqlite3` with bound parameters.

---

### 3.4 Web & API Automation Pack (`use net`)

Readable HTTP requests, authentication, retries, and API workflows with built-in permission safeguards.

#### Syntax Surface:
* **Level 1 (Inspect)**:
  * `ping "https://api.github.com"`
  * `inspect response api_resp`
* **Level 2 (Single Operation)**:
  * `request GET "https://api.example.com/items" into resp`
  * `request POST "https://api.example.com/orders" with body=order_payload into resp`
  * `parse response resp as json into items`
* **Level 3 (API Workflow Block)**:
  ```doomscript
  workflow "sync_inventory":
      base url: "https://api.inventory.internal"
      headers:
          "Authorization": "Bearer " + api_token
          "Content-Type": "application/json"
      retry failed request up to 3 times with backoff exponential
      timeout: 10 seconds

      request GET "/v1/products" into raw_products
      parse raw_products as json into product_catalog
      save product_catalog to "cache/products.json"
  ```

#### Intermediate Representation (`ApiWorkflowSpec`):
* `ApiWorkflowSpec(name, base_url, headers, timeout, retry_policy, steps)`
* `RetryPolicy(max_retries, backoff_type, status_codes)`

#### Runtime Engine:
* Powered by Python standard library `urllib.request` + `ssl` with zero mandatory external dependencies. Supports `requests`/`httpx` when present.

#### Exporter (`NetASTExporter`):
* Emits standard library `urllib.request` or `requests` Python AST code with proper try/except retry loops and timeout configuration.

---

### 3.5 Simulation & Optimization Pack (`use sim`)

Monte Carlo simulation, discrete-event queueing, and numerical function optimization.

#### Syntax Surface:
* **Level 1 (Inspect)**:
  * `inspect simulation bank_sim`
  * `profile distribution normal with mean 10 and stdev 2`
* **Level 2 (Single Operation)**:
  * `sample 1000 numbers from normal with mean 50, stdev 10 into samples`
  * `minimize cost_fn starting at [0.0, 0.0] into optimal_point`
* **Level 3 (Simulation Block)**:
  ```doomscript
  simulate checkout_queue into queue_results:
      arrivals: poisson with rate 12
      service: exponential with rate 15
      servers: 2
      duration: 5000 events

      track waiting_time
      track queue_length

  summarize queue_results's waiting_time into wait_summary
  say "Average Wait Time:", wait_summary's mean
  ```

#### Intermediate Representation (`SimulationSpec`, `OptimizationSpec`):
* `SimulationSpec(name, arrival_dist, service_dist, server_count, duration, tracked_metrics)`
* `OptimizationSpec(target_fn, initial_guess, bounds, method)`

#### Runtime Engine:
* Discrete-event queue engine and Monte Carlo generator implemented in pure Python (`math`, `random`, `heapq`).
* Optimization routines support Nelder-Mead and gradient descent with numerical differentiation.

#### Exporter (`SimASTExporter`):
* Emits standalone Python AST simulation loops utilizing standard `random` and `heapq` structures.

---

### 3.6 Testing & Algorithm Analysis Pack (`use dsa`)

Empirical complexity analysis, execution time/memory benchmarking, and algorithm contract validation.

#### Syntax Surface:
* **Level 1 (Inspect / Analyze)**:
  * `analyze complexity of binary_search with sizes [100, 1000, 10000]`
  * `inspect structure my_graph`
* **Level 2 (Single Operation)**:
  * `time execution of quicksort(data) into elapsed_ms`
  * `measure memory of build_tree(items) into memory_kb`
* **Level 3 (Benchmark Block)**:
  ```doomscript
  benchmark sort_comparison:
      target: quicksort
      input sizes: [100, 500, 1000, 5000, 10000]
      input generator: random_integers
      measure: execution_time, peak_memory
      repeat: 10
      fit complexity: auto

  say "Empirical Fit:", sort_comparison's complexity_order
  ```

#### Intermediate Representation (`BenchmarkSpec`):
* `BenchmarkSpec(name, target_fn, input_sizes, generator, metrics, repeat_count, fit_model)`

#### Runtime Engine:
* High-precision timing via `time.perf_counter_ns` and memory profiling via `tracemalloc`.
* OLS curve fitting against theoretical growth orders: $O(1)$, $O(\log n)$, $O(n)$, $O(n \log n)$, $O(n^2)$, $O(2^n)$ selecting the highest $R^2$ fit with residual penalties.

#### Exporter (`BenchmarkASTExporter`):
* Emits self-contained Python benchmarking scripts with automated measurement tables and curve-fit statistics.

---

## 4. Integration with Core Compiler (`engine.py`)

1. **Compilation Lowering**:
   ```
   [Source Code]
         │
         ▼
   [Phrases / Lexer Tokenizer] ──> Intercepts `use <domain>`
         │
         ├──> [Core Lark Parser] (Variables, loops, functions, contracts)
         │
         └──> [Domain Registry Dispatcher]
                 ├──> DataDomainParser   ──> PipelineSpec  ──> Lowered AST Call
                 ├──> MLDomainParser     ──> ModelSpec     ──> Lowered AST Call
                 ├──> DBDomainParser     ──> QuerySpec     ──> Lowered AST Call
                 ├──> NetDomainParser    ──> NetSpec       ──> Lowered AST Call
                 ├──> SimDomainParser    ──> SimSpec       ──> Lowered AST Call
                 └──> DSADomainParser    ──> BenchmarkSpec ──> Lowered AST Call
   ```

2. **Execution**:
   * Domain runtime helpers are injected into `execute()`'s globals dynamically when domains are registered.

3. **Standalone Python Export (`doom export`)**:
   * `export_to_python()` runs the domain AST transformers, replacing high-level domain representations with native, readable Python code (e.g. Pandas, Sklearn, Urllib, SQLite).

---

## 5. Verification & Test Plan

1. **Unit Tests per Domain**:
   * `tests/domains/test_data_domain.py`: Pipeline parsing, validation error reporting, execution on native records, Pandas interop, AST export.
   * `tests/domains/test_ml_domain.py`: ModelSpec validation, train/test split, train & evaluate execution, Scikit-learn AST export.
   * `tests/domains/test_db_domain.py`: SQL query construction, parameter binding, SQLite execution, AST export.
   * `tests/domains/test_net_domain.py`: API workflow parsing, retry logic, mock response parsing, AST export.
   * `tests/domains/test_sim_domain.py`: Queueing simulation event loop, distribution profiling, AST export.
   * `tests/domains/test_dsa_domain.py`: Benchmark execution, empirical complexity fit ($O(n \log n)$ verification on sort), AST export.
2. **End-to-End Inter-Domain Integration Tests**:
   * `tests/domains/test_cross_domain_integration.doom`:
     1. Read & clean data via `use data`.
     2. Train a classifier via `use ml`.
     3. Plot the confusion matrix via `use viz`.
     4. Benchmark the inference speed via `use dsa`.
3. **English Corpus & CLI Verification**:
   * Verify all 200 existing English corpus benchmarks continue to pass at 100%.
   * CLI: `doom run`, `doom transpile`, `doom export`, `doom check` work across all domains.
