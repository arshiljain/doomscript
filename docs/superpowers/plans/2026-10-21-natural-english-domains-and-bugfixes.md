# Natural English Specialized Domains & P0 Bugfixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the 3 P0 string/filter/percentage bugs and expand natural English verb forms across DoomScript's specialized domains (Robotics, Finance, Quantum, ML/Data, Bio, Chem, Physics, Graph, Net, Sec) so algorithms can be invoked via intuitive English phrases instead of standard function calls.

**Architecture:**
1. **P0 Bugfixes:**
   - Eliminate `F_STRING_PREFIX_REGEX` quote corruption in `mask_strings` by integrating prefix extraction into `STRING_REGEX` with token boundary guards.
   - Map symbolic comparison operators (`>=`, `<=`, `>`, `<`, `!=`, `==`) in `filter_records_stmt` and dynamically resolve scalar vs. attribute fields so `scores where score >= 80 into passed` works on number lists and record collections alike.
   - Expand `percent_of` phrase pattern to support dotted attribute accesses (`student.midterm`), possessives (`student's midterm`), and subscript expressions.
2. **Specialized Domain Spoken English:**
   - Enrich domain parsers in `src/doomscript/domains/<domain>/parser.py` with spoken English phrases (e.g. `move arm to...`, `read lidar...`, `calculate black-scholes...`, `apply hadamard gate...`, `train regression model...`).
   - Wire domain phrases into `try_parse_domain_line` with automatic domain routing so domain statements can be used intuitively with `use <domain>` or auto-dispatch.

**Tech Stack:** Python 3.10+, Lark 1.1.9+, AST transpiler, Pytest.

**Spec:** User request specifying 3 P0 bugs and natural English verb forms for key domains.

## Global Constraints
- Zero regressions on existing 1,336 unit tests.
- 100% pass rate on beginner UX benchmark (85/85).
- Zero external dependencies beyond standard library and Lark.
- Preserve all existing domain functions and contracts.

---

## Tasks

### Task 1: Fix P0 Bug 1 — String Normalization Corrupting "F"
- [ ] Write failing test in `tests/test_natural_operations.py` checking `say "F"`, `say "Grade F"`, `say "FFFF"`, `say "f"`, and `say f"hello {name}"`.
- [ ] Run test to verify failure.
- [ ] In `src/doomscript/grammar/phrases.py`, remove `F_STRING_PREFIX_REGEX` and integrate optional prefix into `STRING_REGEX` with boundary guard: `(?<![\w"\'\\])([fF]?)(("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"(?:[^"\\]|\\.)*"|(?<!\w)\'(?:[^\'\\]|\\.)*\'))`.
- [ ] Run tests and verify they pass.
- [ ] Commit: `fix(phrases): prevent string masking from stripping trailing F in string literals`.

### Task 2: Fix P0 Bug 2 — Symbolic Comparisons Silently Becoming Equality in Filters
- [ ] Write failing test in `tests/test_natural_operations.py` checking `scores = [92, 74, 88]; scores where score >= 80 into passed` and `people where age > 21 into adults`.
- [ ] Run test to verify failure.
- [ ] In `src/doomscript/compiler/transformer.py`, update `filter_records_stmt`:
  - Add symbolic operators (`>=`, `<=`, `>`, `<`, `!=`, `==`) to `op_map`.
  - Add runtime/AST helper resolving scalar vs record attribute access (`_x[field]` / `_x.field` if exists, else `_x`).
- [ ] Run tests and verify they pass.
- [ ] Commit: `fix(compiler): support symbolic operators and scalar item filtering in where-into statements`.

### Task 3: Fix P0 Bug 3 — Percentage Calculations with Property Access
- [ ] Write failing test in `tests/test_natural_operations.py` for `student = {name: "Alex", midterm: 88}; part = 40% of student.midterm` and `part = 40% of student's midterm`.
- [ ] Run test to verify failure.
- [ ] In `src/doomscript/grammar/phrases.py`, update percentage regex to support property accesses, possessives, and subscripts: `r"(\d+(?:\.\d+)?)\s*%\s+of\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*|'s\s+[A-Za-z_]\w*|\[[^\]]+\])*|\d+(?:\.\d+)?|\([^)]+\))"`.
- [ ] Run tests and verify they pass.
- [ ] Commit: `fix(phrases): support property and possessive access in percentage calculations`.

### Task 4: Expose Natural English Verb Forms for Robotics Domain
- [ ] Write unit tests in `tests/domains/test_robotics_spoken_english.py`:
  - `move arm to x: 10, y: 20, z: 30 into target`
  - `read lidar sensor "front_lidar" into scan`
  - `calculate forward kinematics for dh parameters <dh> into fk`
  - `solve 2link inverse kinematics with link1 10 and link2 10 for target 5, 5 into ik`
  - `plan rrt path from [0, 0] to [10, 10] in bounds [[-5, -5], [15, 15]] into path`
- [ ] Inspect and update `src/doomscript/domains/robotics/parser.py` and `runtime.py` to support these natural phrases.
- [ ] Run tests and verify all pass.
- [ ] Commit: `feat(domains/robotics): expose spoken natural English phrases for arm movement, lidar, kinematics, and path planning`.

### Task 5: Expose Natural English Verb Forms for Finance Domain
- [ ] Write unit tests in `tests/domains/test_finance_spoken_english.py`:
  - `calculate black-scholes price for call option on asset 100 with strike 105, time 1.0, rate 0.05, vol 0.2 into call_price`
  - `calculate black-scholes price for put option on asset 100 with strike 95, time 0.5, rate 0.03, vol 0.25 into put_price`
  - `calculate delta for call option on asset 100 with strike 100, time 1.0, rate 0.05, vol 0.2 into d`
  - `calculate sharpe ratio for returns [0.01, 0.02, -0.005, 0.015] with risk free rate 0.001 into sr`
  - `calculate value at risk for returns [-0.02, 0.01, -0.05, 0.03] at confidence 0.95 into var_val`
- [ ] Inspect and update `src/doomscript/domains/finance/parser.py` and `runtime.py` to support these natural phrases.
- [ ] Run tests and verify all pass.
- [ ] Commit: `feat(domains/finance): expose spoken natural English phrases for Black-Scholes, Greeks, Sharpe ratio, and VaR`.

### Task 6: Expose Natural English Verb Forms for Quantum Domain
- [ ] Write unit tests in `tests/domains/test_quantum_spoken_english.py`:
  - `create quantum circuit with 2 qubits into qc`
  - `apply hadamard gate to qubit 0 in circuit qc`
  - `apply cnot gate with control 0 and target 1 in circuit qc`
  - `measure qubit 0 in circuit qc into m0`
  - `simulate quantum circuit qc into state`
- [ ] Inspect and update `src/doomscript/domains/quantum/parser.py` and `runtime.py` to support these natural phrases.
- [ ] Run tests and verify all pass.
- [ ] Commit: `feat(domains/quantum): expose spoken natural English phrases for quantum circuits, gates, and measurement`.

### Task 7: Expose Natural English Verb Forms for Data & Machine Learning (ML) Domain
- [ ] Write unit tests in `tests/domains/test_ml_spoken_english.py`:
  - `train linear regression on features X and targets y into model`
  - `predict with model model on features X_test into preds`
  - `train logistic regression on features X and targets y into clf`
  - `calculate mean squared error between y_true and y_pred into mse`
  - `calculate accuracy between y_true and y_pred into acc`
- [ ] Inspect and update `src/doomscript/domains/ml/parser.py` and `src/doomscript/domains/data/parser.py`.
- [ ] Run tests and verify all pass.
- [ ] Commit: `feat(domains/ml): expose spoken natural English phrases for model training, prediction, and metrics`.

### Task 8: Expose Natural English Verb Forms for Additional Key Domains (Bio, Chem, Physics, Graph, Net, Sec)
- [ ] Inspect and enrich spoken English phrases in:
  - `src/doomscript/domains/bio/parser.py`: sequence transcription, translation, alignment
  - `src/doomscript/domains/chem/parser.py`: molecular weight calculation, SMILES parsing
  - `src/doomscript/domains/physics/parser.py`: harmonic oscillator, gravitational force, wave simulation
  - `src/doomscript/domains/graph/parser.py`: shortest path, Dijkstra, BFS/DFS traversal
  - `src/doomscript/domains/net/parser.py`: ping latency, packet throughput, subnet masking
  - `src/doomscript/domains/sec/parser.py`: hash generation, HMAC, symmetric encryption
- [ ] Add comprehensive tests in `tests/domains/test_all_specialized_spoken_english.py`.
- [ ] Run tests and verify all pass.
- [ ] Commit: `feat(domains): enrich spoken natural English across Bio, Chem, Physics, Graph, Net, and Sec`.

### Task 9: Final Conformance Gate & Full Regression Audit
- [ ] Run entire test suite (`python -m pytest`). All 1,336+ tests must pass.
- [ ] Re-run beginner UX benchmark (`python scratch/audit_beginner_phrasings.py`). 85/85 (100%) must pass.
- [ ] Verify clean git state and push to `origin/main`.
