# Explicit Runtime Export Registry & Domain Extraction Architecture Spec

## 1. Problem Statement & Motivation
Currently, `doomscript.runtime.get_runtime_exports()` dynamically iterates over Python's `globals()` dictionary and filters out names using `_EXCLUDED_MODULE_NAMES` (a denylist). This discovery mechanism causes two major architectural problems:
1. **Accidental Visibility**: Any new public function or imported symbol added to `runtime.py` automatically leaks into the language execution namespace.
2. **Mixed Responsibilities in `runtime.py`**: At ~4,853 lines, `runtime.py` houses general-purpose runtime primitives alongside domain-oriented executors (`execute_data_ir`, `execute_ml_ir`, `execute_dsa_ir`, `execute_geo_ir`, etc.) and domain-specific logic (`_DoomORM`, `db_save`, `geo_voronoi_diagram`, `sec_shamir_split`, etc.).

## 2. Target Architecture

```
+--------------------------------------------------------------------+
|                         Compiler / Engine                          |
+--------------------------------------------------------------------+
          |                                        |
          v                                        v
+-----------------------------+       +------------------------------+
| Core Runtime Allowlist      |       | Domain Registry (Scoped)     |
| (MappingProxyType)          |       | (Activated via `use <dom>`)  |
+-----------------------------+       +------------------------------+
| - Record, CLI, Docs, Sched  |       | - dsa.runtime (executors)    |
| - File I/O, Strings, Math   |       | - data.runtime (executors)   |
| - Network/HTTP, Async, Date |       | - ml.runtime (executors)     |
| - Immutable & Defensive cpy |       | - geo.runtime (executors)    |
+-----------------------------+       | - db.runtime (ORM/executors) |
                                      +------------------------------+
```

### Principle 1: Deliberate, Immutable Export Registry
- Define `_CORE_RUNTIME_EXPORTS: types.MappingProxyType` containing only supported, curated core language primitives.
- `get_runtime_exports()` returns `dict(_CORE_RUNTIME_EXPORTS)` (a defensive copy).
- Neither `globals()` scanning nor denylists are used.
- Explicit tests assert:
  - Every exported symbol is callable or a supported class.
  - No Python standard library modules (`sys`, `os`, `math`, `re`, `subprocess`, etc.) or typing artifacts are in the registry.
  - Mutating the internal mapping proxy raises `TypeError`.

### Principle 2: Domain Implementation Extraction
- Extract domain executors and domain-specific helpers from `runtime.py` into their respective domain packages:
  - `doomscript.domains.data.runtime`: `execute_data_ir`, `load_table`, `save_table`, `filter_table`, etc.
  - `doomscript.domains.ml.runtime`: `execute_ml_ir`, `train_direct_model`, `accuracy_score_fn`.
  - `doomscript.domains.db.runtime`: `execute_db_ir`, `_DoomORM`, `orm_*`, `db_*`.
  - `doomscript.domains.dsa.runtime`: `execute_dsa_ir`, `dsa_push`, `dsa_heap_*`, `dsa_deque_*`, `run_dsa_benchmark`, etc.
  - `doomscript.domains.geo.runtime`: `execute_geo_ir`, `geo_delaunay_triangulate`, `geo_voronoi_diagram`, etc.
  - `doomscript.domains.sim.runtime`: `execute_sim_ir`, `sim_sample_*`, `run_trials`, `sweep_parameter`.
  - `doomscript.domains.opt.runtime`: `execute_opt_ir`, `solve_linear_program`.
  - `doomscript.domains.net.runtime`: `execute_net_ir`.
  - `doomscript.domains.nlp.runtime`: `execute_nlp_ir`.
- In `doomscript.runtime`, maintain backward-compatible re-exports (`from doomscript.domains.dsa.runtime import execute_dsa_ir`, etc.) so external callers and legacy test suites continue to resolve without disruption.

### Principle 3: Clear Security & Execution Boundary
- Explicit documentation in both `runtime.py` and `compiler/engine.py` stating clearly:
  > **Security Notice**: An explicit runtime registry enforces namespace hygiene and API maintainability; it is **NOT** a security sandbox. Untrusted DoomScript source code executes natively as Python bytecode.
