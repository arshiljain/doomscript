# Explicit Runtime Export Registry & Domain Implementation Extraction Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the dynamic `globals()` denylist discovery in `doomscript.runtime` with an immutable allowlist registry, extract domain-oriented IR executors and utilities out of `runtime.py` into their respective domain packages with compatibility re-exports, and verify zero regressions.

**Architecture:**
- Create an immutable allowlist mapping `_CORE_RUNTIME_EXPORTS: types.MappingProxyType` in `runtime.py` containing only curated language primitives, with `get_runtime_exports()` returning a defensive copy.
- Relocate early IR executors (`execute_data_ir`, `execute_ml_ir`, `execute_dsa_ir`, `execute_geo_ir`, etc.) and domain classes (`_DoomORM`) into their native domain packages (`domains.data`, `domains.ml`, `domains.dsa`, `domains.geo`, `domains.db`, etc.).
- Maintain re-exports in `doomscript.runtime` for 100% backward compatibility.
- Enforce strict test assertions verifying that no accidental modules leak into the runtime namespace and that importing basic DoomScript does not eagerly pull in extraneous modules.

**Tech Stack:** Pure Python standard library (`types.MappingProxyType`, `dict`), `pytest`.

**Spec:** `docs/superpowers/specs/2026-10-21-explicit-runtime-registry-spec.md`

---

## Global Constraints
- Pure Python standard library only (zero external pip packages).
- 100% backward compatibility: all 1,234 existing tests must remain passing.
- All 46 `vspython.md` examples must remain passing.
- Immutable registry: `_CORE_RUNTIME_EXPORTS` cannot be mutated; `get_runtime_exports()` returns a new dictionary copy.

---

## Tasks

### Task 1: Explicit Immutable Runtime Allowlist Registry
- [ ] Define the complete allowlist of core language functions, classes, and compatibility helpers in `src/doomscript/runtime.py`.
- [ ] Wrap in `types.MappingProxyType` to guarantee immutability.
- [ ] Update `get_runtime_exports()` to return `dict(_CORE_RUNTIME_EXPORTS)` (defensive copy), eliminating `globals()` iteration and `_EXCLUDED_MODULE_NAMES`.
- [ ] Add unit tests in `tests/test_runtime_export_registry.py` testing:
  - Immutability of the underlying mapping proxy.
  - Defensive copy behavior of `get_runtime_exports()`.
  - Absence of unwanted Python standard library modules (`os`, `sys`, `subprocess`, `re`, `time`, etc.).
  - Presence of critical core symbols (`Record`, `sleep`, `write_file`, `fetch_json`, etc.).
- [ ] Verify Task 1 tests pass.

### Task 2: Domain Implementation Extraction from `runtime.py`
- [ ] Extract Data IR executor and table helpers (`execute_data_ir`, `load_table`, `save_table`, `filter_table`, etc.) into `src/doomscript/domains/data/runtime.py`.
- [ ] Extract ML IR executor and helpers (`execute_ml_ir`, `train_direct_model`, `accuracy_score_fn`) into `src/doomscript/domains/ml/runtime.py`.
- [ ] Extract Database IR executor, ORM, and query helpers (`execute_db_ir`, `_DoomORM`, `orm_*`, `db_*`) into `src/doomscript/domains/db/runtime.py`.
- [ ] Extract DSA IR executor, heaps, benchmarks, and complexity helpers (`execute_dsa_ir`, `dsa_push`, `dsa_heap_*`, `run_dsa_benchmark`, `analyze_complexity`, etc.) into `src/doomscript/domains/dsa/runtime.py`.
- [ ] Extract Geo IR executor and spatial helpers (`execute_geo_ir`, `geo_delaunay_triangulate`, `geo_voronoi_diagram`, `geo_compute_isochrone`, etc.) into `src/doomscript/domains/geo/runtime.py`.
- [ ] Extract Sim, Opt, Net, and NLP IR executors (`execute_sim_ir`, `execute_opt_ir`, `execute_net_ir`, `execute_nlp_ir`) into their respective domain packages.
- [ ] Add re-exports in `src/doomscript/runtime.py` for backward compatibility.
- [ ] Update `tests/test_runtime_export_registry.py` to verify re-exports and domain package locations.
- [ ] Verify Task 2 tests pass.

### Task 3: Full Regression Verification & Security Documentation
- [ ] Run all domain test suites (`tests/domains/`).
- [ ] Run all research test suites (`tests/research/`).
- [ ] Run all 46 `vspython.md` tests (`tests/test_vspython_all_examples.py`).
- [ ] Run full test suite across the entire repository (`python -m pytest -q`).
- [ ] Verify clear documentation in `runtime.py` and `compiler/engine.py` stating that the runtime export registry provides namespace hygiene and maintainability, not an `exec()` sandbox.
