# Domain Excellence & Spoken-English Phrase Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Elevate all 19 DoomScript domains to spoken-English excellence by establishing a declarative phrase matching engine, explicit interoperability value taxonomy, and universal explainability framework.

**Architecture:** A layered architecture where the core owns the `EnglishPhraseMatcher` and diagnostic near-miss suggestions; the `data` domain owns spoken-English filtering, sorting, and file I/O; an explicit value taxonomy standardizes cross-domain conversions; and a universal introspection protocol powers `explain`, `summary of`, and `preview of` across all domains.

**Tech Stack:** Python 3.10+, Lark Parser, Python standard library (`ast`, `dataclasses`, `typing`, `difflib`).

**Spec:** [`docs/superpowers/specs/2026-10-19-domain-excellence-architecture-design.md`](file:///C:/Users/kanha/.gemini/antigravity/scratch/doomscript/docs/superpowers/specs/2026-10-19-domain-excellence-architecture-design.md)

## Global Constraints

- **Pure English-First**: DoomScript code must read like spoken English and be 3-5x shorter than equivalent Python.
- **Zero Core Grammar Pollution**: Domain operations belong to domain packs; the core grammar handles language constructs (variables, expressions, loops, assignments).
- **Advisory Diagnostics Only**: Incomplete or near-miss phrases produce helpful "Did you mean?" suggestions; the engine never silently guesses or executes malformed input.
- **Zero Mandatory Dependencies**: Core phrase engine and standard runtime must run with standard library Python; optional dependencies remain isolated with clear diagnostics.
- **100% Conformance**: Direct interpreter execution and exported native Python AST must exhibit identical runtime semantics.
- **Backward Compatibility**: All 496 existing pytest tests and 40/40 Coursework Capability Benchmarks must continue to pass with 100% success rate.

## Review Focus

1. **Near-miss verb matching**: A user writes `orders where status is "paid"` without `into <var>`; engine must raise `DoomSyntaxError` with "Did you mean: `orders where status is "paid" into <variable>`?" and not silently proceed or crash.
2. **Preposition and synonym variations**: `fetch stock prices for "AAPL" into p`, `fetch stock "AAPL" into p`, `fetch "AAPL" into p` must all resolve to the same semantic operation with identical arguments.
3. **Lossless Table/RecordList conversions**: `Table.to_records()` and `Table.from_records()` must preserve column order, dtypes, null values, and dict/attribute access without type coercion errors.
4. **Introspection robustness**: `explain` on uninitialized, empty, or custom domain objects must return structured metadata gracefully rather than raising unhandled exceptions.
5. **Cross-domain fluent pipelines**: Piping data from `finance` quotes $\rightarrow$ `data` filter $\rightarrow$ `office` spreadsheet $\rightarrow$ `cloud` bucket upload must execute seamlessly without type mismatches.

---

### Task 1: Core Spoken-English Phrase Engine (`EnglishPhraseMatcher`)

**Files:**
- Create: `src/doomscript/domains/matcher.py`
- Modify: `src/doomscript/domains/base.py`, `src/doomscript/domains/registry.py`
- Test: `tests/domains/test_phrase_matcher.py`

**Interfaces:**
- Consumes: Python `re`, `difflib`, `dataclasses`
- Produces: `VerbSpec`, `BlockSpec`, `EnglishPhraseMatcher`, `PhraseMatchResult`, `suggest_near_miss_verb(line, verbs)`

- [ ] **Step 1: Write the failing test**

```python
# tests/domains/test_phrase_matcher.py
import pytest
from doomscript.domains.matcher import EnglishPhraseMatcher, VerbSpec, suggest_near_miss_verb

def test_phrase_matcher_basic_and_synonyms():
    v = VerbSpec(
        pattern="[fetch] stock [prices] [for] {symbol:expr} [from {start:expr}] [to {end:expr}] into {target:ident}",
        emit="set {target} to fetch_stock_prices({symbol}, start_date={start|'2024-01-01'}, end_date={end|'2024-12-31'})",
        doc="Fetches stock prices",
    )
    matcher = EnglishPhraseMatcher([v])

    # Test full phrase
    res1 = matcher.match('fetch stock prices for "AAPL" from "2024-01-01" to "2024-12-31" into quotes')
    assert res1 is not None
    assert res1.emitted == 'set quotes to fetch_stock_prices("AAPL", start_date="2024-01-01", end_date="2024-12-31")'

    # Test optional tokens omitted
    res2 = matcher.match('fetch stock "AAPL" into q')
    assert res2 is not None
    assert res2.emitted == "set q to fetch_stock_prices(\"AAPL\", start_date='2024-01-01', end_date='2024-12-31')"


def test_near_miss_diagnostic():
    v = VerbSpec(
        pattern="orders where {condition:expr} into {target:ident}",
        emit="set {target} to filter_records(orders, {condition})",
        doc="Filters records",
    )
    suggestion = suggest_near_miss_verb('orders where status is "paid"', [v])
    assert suggestion is not None
    assert "into" in suggestion
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/domains/test_phrase_matcher.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.domains.matcher'`

- [ ] **Step 3: Implement `EnglishPhraseMatcher` in `src/doomscript/domains/matcher.py` and integrate in `base.py`**

Compile declarative pattern templates into regex tokens, extract `{name:type}` slots, substitute defaults, and implement Levenshtein token distance in `suggest_near_miss_verb`. Update `DomainContract` to hold `verbs: List[VerbSpec] = field(default_factory=list)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/domains/test_phrase_matcher.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/domains/matcher.py src/doomscript/domains/base.py src/doomscript/domains/registry.py tests/domains/test_phrase_matcher.py
git commit -m "feat(domains): Implement declarative EnglishPhraseMatcher and near-miss diagnostics"
```

---

### Task 2: Interoperability Value Taxonomy & Conversion Protocols

**Files:**
- Create: `src/doomscript/taxonomy.py`
- Modify: `src/doomscript/runtime.py`
- Test: `tests/test_interoperability_taxonomy.py`

**Interfaces:**
- Consumes: `Record` from `runtime.py`
- Produces: `Table`, `RecordList`, `ValueTaxonomy`, `to_table(obj)`, `to_records(obj)`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_interoperability_taxonomy.py
import pytest
from doomscript.taxonomy import Table, to_table, to_records
from doomscript.runtime import Record

def test_table_recordlist_conversion():
    records = [
        Record(name="Alice", score=95, active=True),
        Record(name="Bob", score=82, active=False),
    ]
    tbl = to_table(records)
    assert tbl.row_count == 2
    assert tbl.columns == ["name", "score", "active"]
    assert tbl.schema["score"] in ("int", "number")

    # Roundtrip conversion
    restored = to_records(tbl)
    assert len(restored) == 2
    assert restored[0]["name"] == "Alice"
    assert restored[0].score == 95

    # Markdown & HTML representation
    md = tbl.to_markdown()
    assert "| name | score | active |" in md
    html = tbl.to_html()
    assert "<table>" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/test_interoperability_taxonomy.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.taxonomy'`

- [ ] **Step 3: Implement `Table` and conversions in `src/doomscript/taxonomy.py`**

Implement columnar and row-oriented `Table` data structure with type inference, `to_records()`, `from_records()`, `to_markdown()`, and `to_html()`. Re-export `Table` in `runtime.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/test_interoperability_taxonomy.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/taxonomy.py src/doomscript/runtime.py tests/test_interoperability_taxonomy.py
git commit -m "feat: Add interoperability value taxonomy Table and RecordList protocols"
```

---

### Task 3: Universal Introspection Framework (`explain`, `summary of`, `preview of`)

**Files:**
- Create: `src/doomscript/introspection.py`
- Modify: `src/doomscript/runtime.py`, `src/doomscript/grammar/phrases.py`
- Test: `tests/test_universal_introspection.py`

**Interfaces:**
- Consumes: `Table`, `RecordList`, `DomainRegistry`, `DomainContract`
- Produces: `explain(target)`, `summary_of(target)`, `preview_of(target)`, phrase rewrites for `explain <target>`, `summary of <target>`, `preview of <target>`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_universal_introspection.py
import pytest
from doomscript.compiler.engine import execute
from doomscript.taxonomy import Table
from doomscript.runtime import Record

def test_explain_domain():
    source = """use finance
explain domain finance into fin_info
"""
    env = execute(source)
    assert "verbs" in env["fin_info"]
    assert len(env["fin_info"]["verbs"]) > 0


def test_explain_table_and_preview():
    source = """
data = [
    {"product": "Apples", "sales": 100},
    {"product": "Oranges", "sales": 150}
]
explain data into info
preview of data into p
summary of data into s
"""
    env = execute(source)
    assert env["info"]["row_count"] == 2
    assert "sales" in env["info"]["columns"]
    assert len(env["p"]) == 2
    assert "sales" in env["s"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/test_universal_introspection.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement introspection engine in `src/doomscript/introspection.py` and wire into `phrases.py`**

Support `explain domain <name>`, `explain <var>`, `summary of <var>`, `preview of <var>` across all taxonomy types (`Table`, `RecordList`, `DoomGraph`, `DoomAudio`, `DoomSpreadsheet`, `ModelContainer`).

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/test_universal_introspection.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/introspection.py src/doomscript/runtime.py src/doomscript/grammar/phrases.py tests/test_universal_introspection.py
git commit -m "feat: Implement universal introspection explain, summary of, and preview of"
```

---

### Task 4: Data Domain Spoken-English Upgrade

**Files:**
- Modify: `src/doomscript/domains/data/parser.py`, `src/doomscript/domains/data/runtime.py`, `src/doomscript/domains/data/__init__.py`
- Test: `tests/domains/test_data_spoken_english.py`

**Interfaces:**
- Consumes: `EnglishPhraseMatcher`, `Table`, `RecordList`
- Produces: First-class English verbs in `DATA_DOMAIN`:
  - `read (csv|json|text) file {path:expr} into {target:ident}`
  - `{source:ident} where {condition:expr} into {target:ident}`
  - `sort {source:ident} by {field:ident} [ascending|descending]`
  - `write (csv|json) {source:ident} into [file] {path:expr}`

- [ ] **Step 1: Write the failing test**

```python
# tests/domains/test_data_spoken_english.py
import pytest
from doomscript.compiler.engine import execute

def test_data_spoken_english_seven_liner(tmp_path):
    raw_file = tmp_path / "sales_raw.csv"
    raw_file.write_text("customer,status,amount\nAlice,paid,120.0\nBob,pending,25.0\nCharlie,paid,80.0\nDavid,paid,30.0\n", encoding="utf-8")
    clean_file = tmp_path / "clean_report.csv"

    source = f"""use data

read csv file "{raw_file.as_posix()}" into orders
orders where status is "paid" into valid
valid where amount is over 50 into high_value
sort high_value by amount descending
write csv high_value into file "{clean_file.as_posix()}"
"""
    env = execute(source)
    assert len(env["orders"]) == 4
    assert len(env["valid"]) == 3
    assert len(env["high_value"]) == 2
    assert env["high_value"][0]["customer"] == "Alice"
    assert env["high_value"][1]["customer"] == "Charlie"
    assert clean_file.exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/domains/test_data_spoken_english.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement spoken-English verbs in `data` domain using `EnglishPhraseMatcher`**

Register the conversational verb specs on `DataDomain`, handle sorting, filtering, reading, and writing in `DataRuntime`.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/domains/test_data_spoken_english.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/domains/data/ tests/domains/test_data_spoken_english.py
git commit -m "feat(data): Add spoken-English filtering, sorting, and file verbs"
```

---

### Task 5: Upgrade Flagship Domains (`finance`, `viz`, `office`, `cloud`, `graph`, `audio`) onto Declarative Phrase Engine

**Files:**
- Modify:
  - `src/doomscript/domains/finance/{parser.py, __init__.py}`
  - `src/doomscript/domains/office/{parser.py, __init__.py}`
  - `src/doomscript/domains/cloud/{parser.py, __init__.py}`
  - `src/doomscript/domains/graph/{parser.py, __init__.py}`
  - `src/doomscript/domains/audio/{parser.py, __init__.py}`
- Test: `tests/domains/test_flagship_phrase_engine.py`

**Interfaces:**
- Consumes: `VerbSpec`, `EnglishPhraseMatcher`, `Table`, `RecordList`
- Produces: Declarative `verbs` registered on each domain contract, eliminating manual regex boilerplate.

- [ ] **Step 1: Write the failing test**

```python
# tests/domains/test_flagship_phrase_engine.py
import pytest
from doomscript.compiler.engine import execute

def test_flagship_fluent_orchestration(tmp_path):
    report_xlsx = str(tmp_path / "summary.xlsx").replace("\\", "/")
    source = f"""use finance
use data
use office
use cloud

fetch stock prices for "AAPL" from "2024-01-01" to "2024-01-20" into prices
prices where close is over 100 into rally
create spreadsheet into sheet
add rows from rally to sheet
save spreadsheet sheet to "{report_xlsx}"
connect to bucket "vault" into b
upload file "{report_xlsx}" to bucket b as "reports/rally.xlsx"
list all files in bucket b into cloud_files
"""
    env = execute(source)
    assert len(env["rally"]) > 0
    assert "reports/rally.xlsx" in env["cloud_files"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/domains/test_flagship_phrase_engine.py -v`  
Expected: FAIL (missing `add rows from <records> to sheet` or declarative routing)

- [ ] **Step 3: Migrate flagship domain parsers to `EnglishPhraseMatcher` & add conversions**

Replace manual regex blocks with `VerbSpec` declarations. Implement `add rows from <records> to <sheet>` in `office`.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/domains/test_flagship_phrase_engine.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/domains/finance/ src/doomscript/domains/office/ src/doomscript/domains/cloud/ src/doomscript/domains/graph/ src/doomscript/domains/audio/ tests/domains/test_flagship_phrase_engine.py
git commit -m "refactor(domains): Migrate flagship domains to declarative phrase engine"
```

---

### Task 6: Upgrade Remaining Domains (`agent`, `image`, `web`, `ml`, `db`, `net`, `sim`, `dsa`, `nlp`, `geo`, `opt`, `research`)

**Files:**
- Modify: `src/doomscript/domains/{agent, image, web, ml, db, net, sim, dsa, nlp, geo, opt, research}/`
- Test: `tests/domains/test_remaining_phrase_engine.py`

**Interfaces:**
- Consumes: `EnglishPhraseMatcher`, `DomainContract.verbs`
- Produces: Uniform declarative `verbs` across all remaining 12 domains.

- [ ] **Step 1: Write the failing test**

```python
# tests/domains/test_remaining_phrase_engine.py
import pytest
from doomscript.domains.registry import get_domain_registry

def test_all_domains_have_verbs():
    reg = get_domain_registry()
    for name, domain in reg._domains.items():
        assert hasattr(domain, "verbs"), f"Domain {name} missing verbs attribute"
        assert len(domain.verbs) > 0 or hasattr(domain, "blocks"), f"Domain {name} has no declared verbs or blocks"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `py -m pytest tests/domains/test_remaining_phrase_engine.py -v`  
Expected: FAIL

- [ ] **Step 3: Define `verbs` on each remaining domain contract**

Migrate lines to `VerbSpec` patterns while keeping `DomainParser` backwards compatible.

- [ ] **Step 4: Run test to verify it passes**

Run: `py -m pytest tests/domains/test_remaining_phrase_engine.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/domains/ tests/domains/test_remaining_phrase_engine.py
git commit -m "refactor(domains): Standardize remaining domains on declarative VerbSpec declarations"
```

---

### Task 7: Conformance, Parity, and Zero-Regression Benchmark

**Files:**
- Modify: `tests/conformance/test_domain_conformance.py`
- Test: All tests (`py -m pytest`), Coursework capability benchmarks (`py run_capability.py`)

**Interfaces:**
- Consumes: All 19 domains and core language engine
- Produces: 100% test pass rate across unit, conformance, and capability benchmarks.

- [ ] **Step 1: Update domain conformance suite with spoken-English fixtures**

Add test cases in `tests/conformance/test_domain_conformance.py` testing export parity for all new spoken-English data and domain verbs.

- [ ] **Step 2: Run full pytest suite**

Run: `py -m pytest -q`  
Expected: 500+ passed, 0 failed.

- [ ] **Step 3: Run capability benchmarks**

Run: `py run_capability.py`  
Expected: 40/40 passed (100.0%).

- [ ] **Step 4: Commit and Push**

```bash
git add tests/conformance/test_domain_conformance.py
git commit -m "test(conformance): Verify 100% execution/export parity and 40/40 capability benchmark"
git push origin main
```
