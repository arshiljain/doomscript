# Conversational Domain Vocabularies Implementation Plan
**Track 1: "Talking to the Tools" — English Thought-Stream Domain Syntax**

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement conversational thought-stream syntax across 4 core domain ecosystems (Web & APIs, Data & Analytics, Finance & Simulation, AI & Agents), giving DoomScript 0.6.0 the ability to translate natural spoken developer intents directly into robust tool executions.

**Architecture:**
- Implement pre-parsing conversational desugaring patterns in `src/doomscript/grammar/phrases.py` with string-literal masking protection.
- Implement core thread-safe runtime helpers in `src/doomscript/runtime.py` and export them in `src/doomscript/core/exports.py`:
  - `extract_json_field(source, field_path: str)`
  - `load_json_file(filepath: str)`
  - `summarize_data(table, metric_col, group_col, agg_fn="sum")`
  - `simulate_portfolio(allocations, initial_value=10000.0, horizon_days=30)`
  - `calculate_compound_interest(principal, rate, years, periods=1)`
  - `ask_assistant(prompt: str, context=None, as_json=False)`
  - `ask_model(prompt: str, model="default", context=None, as_json=False)`
- Update domain parsers (`web`, `net`, `data`, `finance`, `agent`) to support these natural forms in both active and standard scripts.

**Tech Stack:** Python 3.10+, Lark Parser, AST Transformer, DoomScript Runtime Engine.

**Spec:** `docs/superpowers/specs/2026-10-21-conversational-domain-vocabularies-design.md`

## Global Constraints
- Preserve 100% backward compatibility across all 40 domains, canonical verbs, and signatures.
- Zero Python exception leakage: wrap internal parsing or runtime failures in `DoomScriptRuntimeError` or descriptive errors.
- String preservation: ensure URLs, queries, prompt strings, and JSON paths are never distorted by regex matching.
- Offline determinism: AI invocations must fall back to deterministic mocks in offline environments without crashing.

## Review Focus
- Nested JSON field extraction: dot syntax (`data.items[0].id` or `user.name`) across Records, dicts, lists, and raw JSON strings.
- Percentages in finance simulations: `50% BTC and 50% ETH` vs `{"BTC": 0.5, "ETH": 0.5}`.
- Single-line chart plotting: `plot sales as a bar chart titled "Sales"` must return or display a valid plot object without crashing.
- File not found errors in `load csv` / `load json` must produce friendly messages rather than raw Python stack traces.
- Prompt commas and prepositions in `ask the assistant "..." for ... into ...` must preserve full prompt strings.

---

### Task 1: Web & APIs Conversational Layer (`web` / `net`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Create: `tests/domains/test_conversational_domains.py`

**Interfaces:**
- Produces:
  - `extract_json_field(source: Any, field_path: str) -> Any` in `runtime.py`
  - Desugaring in `phrases.py`:
    - `send [a] get request to <url> [and wait for response] into <target>`
    - `send [a] post request to <url> with <payload> into <target>`
    - `post <payload> to <url> into <target>`
    - `extract [json] field <path> from <source> into <target>`

- [x] **Step 1: Write failing unit tests for Web & API conversational syntax**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `extract_json_field` in `runtime.py` and exports in `core/exports.py`**
- [x] **Step 4: Implement phrase desugaring in `phrases.py`**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit Task 1**

---

### Task 2: Data & Analytics Conversational Layer (`data` / `db`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/domains/test_conversational_domains.py`

**Interfaces:**
- Produces:
  - `load_json_file(filepath: str) -> Any` in `runtime.py`
  - `summarize_data(table: Any, metric_col: str, group_col: str, agg_fn: str = "sum") -> List[Record]` in `runtime.py`
  - Desugaring in `phrases.py`:
    - `load csv [from] <path> into <target>`
    - `load json [from] <path> into <target>`
    - `summarize column <metric> by <group> [in|from] <table> into <target>`
    - `summarize <table> by <group> calculating <fn> of <metric> into <target>`
    - `plot <data> as [a] <geom> chart [titled <title>] [into <target>]`

- [x] **Step 1: Write failing unit tests for Data & Analytics conversational syntax**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `load_json_file` and `summarize_data` in `runtime.py`**
- [x] **Step 4: Implement phrase desugaring in `phrases.py` for file loading, summaries, and chart plotting**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit Task 2**

---

### Task 3: Finance & Simulation Conversational Layer (`finance` / `sim`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/domains/test_conversational_domains.py`

**Interfaces:**
- Produces:
  - `simulate_portfolio(allocations: Any, initial_value: float = 10000.0, horizon_days: int = 30) -> Record` in `runtime.py`
  - `calculate_compound_interest(principal: Any, rate: Any, years: Any, periods: int = 1) -> float` in `runtime.py`
  - Desugaring in `phrases.py`:
    - `simulate portfolio with <allocations> into <target>` (handling natural percentage strings e.g. `50% BTC and 50% ETH`)
    - `calculate compound interest on principal <p> at rate <r> [over|for] <y> years into <target>`

- [x] **Step 1: Write failing unit tests for Finance & Simulation conversational syntax**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `simulate_portfolio` and `calculate_compound_interest` in `runtime.py`**
- [x] **Step 4: Implement portfolio allocation parsing and compound interest desugaring in `phrases.py`**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit Task 3**

---

### Task 4: AI & Agents Conversational Layer (`agent` / `nlp`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/domains/test_conversational_domains.py`

**Interfaces:**
- Produces:
  - `ask_assistant(prompt: str, context: Optional[Any] = None, as_json: bool = False) -> Any` in `runtime.py`
  - `ask_model(prompt: str, model: str = "default", context: Optional[Any] = None, as_json: bool = False) -> Any` in `runtime.py`
  - Desugaring in `phrases.py`:
    - `ask [the] assistant <prompt> [for <context>] into <target>`
    - `ask [the] model <prompt> [for <context>] into <target>`
    - `ask the agent <name> <prompt> into <target>`
    - `tell the agent <name> <message>`

- [x] **Step 1: Write failing unit tests for AI & Agent conversational syntax**
- [x] **Step 2: Run test to verify it fails**
- [x] **Step 3: Implement `ask_assistant` and `ask_model` in `runtime.py`**
- [x] **Step 4: Implement agent and assistant phrase desugaring in `phrases.py`**
- [x] **Step 5: Run tests to verify they pass**
- [x] **Step 6: Commit Task 4**

---

### Task 5: Comprehensive Verification Gate & System Integration

**Files:**
- Modify: `docs/superpowers/plans/2026-10-21-conversational-domain-vocabularies.ledger.md`
- Test: Full test suite (`pytest tests/`), 85/85 Beginner UX Audit, 92+ Domain Regression Suite

- [x] **Step 1: Run complete conversational domain test suite**
- [x] **Step 2: Run 85-point Beginner UX Audit benchmark**
- [x] **Step 3: Run full 92+ regression suite**
- [x] **Step 4: Update execution ledger with commit hashes, test results, and metrics**
- [x] **Step 5: Commit and push changes to `main` branch**
