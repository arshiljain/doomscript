# Thought-to-Code: All 4 Phases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform DoomScript into a true "Thought-to-Code" English programming language across all 4 cognitive phases: Deep Anaphoric Discourse Memory & Quantifiers (Phase 1), Contextual Attribute Scoping & Superlatives (Phase 2), Declarative Resilience & Compound Action Chaining (Phase 3), and Conversational Set Reshaping & Analytics (Phase 4), achieving 100% deterministic compilation, zero Python leakage, and 150/150 beginner UX passing benchmarks.

**Architecture:** Extend `ScopeTracker` with a dual-referent discourse stack (`last_singular`, `last_plural`), add quantifier calculus and implicit attribute resolution to `phrases.py`, add runtime resilience/superlative/set-reshaping engines to `runtime.py` and `core/exports.py`, and eliminate all friction points where human English thought diverged from compiler requirements.

**Tech Stack:** Python 3.10+, Lark Parser (EBNF/LALR), Regex normalizer, Pytest, DoomScript AST compiler.

**Spec:** `C:\Users\kanha\.gemini\antigravity\brain\27ecc6a3-1f2e-4fcf-9af1-557bcdde3633\natural_english_thought_to_code_blueprint.md`

## Global Constraints

- Preserve 100% backward compatibility across all 41 domains, 85/85 existing Beginner UX phrasings, and all 1,450+ core test cases.
- Maintain the Zero Python Error Leakage Guarantee: all runtime failures must wrap into `DoomError`, `DoomNameError`, `DoomTypeError`, or `DoomRuntimeError`.
- Pronouns inside string literals or comments must never be altered or corrupted.
- All newly added runtime helpers must be registered in `src/doomscript/core/exports.py` under `CORE_EXPORT_NAMES`.
- Follow strict Test-Driven Development (TDD): write failing test -> verify failure -> implement -> verify pass -> commit.

## Review Focus

1. **`its` Outside vs Inside Classes:** Outside class methods, `its <prop>` must resolve to `last_singular.<prop>`, NOT `self.<prop>`. Inside class methods, `its <prop>` continues to resolve to `self.<prop>`.
2. **Contextual Scope in Filters:** When querying `keep only orders where price > 100`, `price` must be dynamically evaluated against each `order` (supporting both dict keys and object attributes) without crashing with `DoomNameError`.
3. **Empty Collection Quantifiers:** Universal quantification `every` on an empty collection must evaluate to `True` (vacuous truth), while existential `any` must evaluate to `False`.
4. **Retry Backoff Schedule:** Declarative retries must catch transient errors and sleep with exponential/linear backoff without freezing the thread or leaking Python `urllib` / `requests` / `socket` exceptions.
5. **Multi-Action Compound Blocks:** Chaining statements with `then if <cond>:` must preserve subsequent block indentation and execution scope.

---

## Phase 1: Deep Discourse Memory & Set Quantifiers

### Task 1.1: Runtime Quantifier Helpers (`ds_every`, `ds_any`, `ds_none`) & Exports

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Consumes: Standard Python iterables and unary predicate callables.
- Produces:
  - `ds_every(collection, predicate_fn) -> bool`
  - `ds_any(collection, predicate_fn) -> bool`
  - `ds_none(collection, predicate_fn) -> bool`
  - `ds_at_least_n(collection, n, predicate_fn) -> bool`

- [ ] **Step 1.1.1: Write failing unit test in `tests/test_thought_to_code_all_phases.py`**

```python
import pytest
from doomscript.runtime import ds_every, ds_any, ds_none, ds_at_least_n

def test_runtime_quantifiers():
    numbers = [2, 4, 6, 8]
    assert ds_every(numbers, lambda x: x % 2 == 0) is True
    assert ds_every(numbers, lambda x: x > 5) is False
    assert ds_every([], lambda x: False) is True  # Vacuous truth

    assert ds_any(numbers, lambda x: x > 5) is True
    assert ds_any(numbers, lambda x: x > 100) is False
    assert ds_any([], lambda x: True) is False

    assert ds_none(numbers, lambda x: x < 0) is True
    assert ds_none(numbers, lambda x: x == 4) is False

    assert ds_at_least_n(numbers, 2, lambda x: x >= 6) is True
    assert ds_at_least_n(numbers, 3, lambda x: x >= 6) is False
```

- [ ] **Step 1.1.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_quantifiers -v`
Expected: FAIL with `ImportError: cannot import name 'ds_every'`

- [ ] **Step 1.1.3: Implement `ds_every`, `ds_any`, `ds_none`, `ds_at_least_n` in `src/doomscript/runtime.py` and register in `src/doomscript/core/exports.py`**

```python
def ds_every(collection, predicate_fn):
    if collection is None:
        return True
    try:
        return all(predicate_fn(item) for item in collection)
    except TypeError:
        return bool(predicate_fn(collection))

def ds_any(collection, predicate_fn):
    if not collection:
        return False
    try:
        return any(predicate_fn(item) for item in collection)
    except TypeError:
        return bool(predicate_fn(collection))

def ds_none(collection, predicate_fn):
    return not ds_any(collection, predicate_fn)

def ds_at_least_n(collection, n, predicate_fn):
    if not collection:
        return n <= 0
    count = 0
    for item in collection:
        if predicate_fn(item):
            count += 1
            if count >= n:
                return True
    return count >= n
```

- [ ] **Step 1.1.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_quantifiers -v`
Expected: PASS

- [ ] **Step 1.1.5: Commit changes**
`git add src/doomscript/runtime.py src/doomscript/core/exports.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(runtime): add ds_every, ds_any, ds_none, and ds_at_least_n quantifier helpers"`

---

### Task 1.2: Dual-Referent Discourse Memory in `ScopeTracker`

**Files:**
- Modify: `src/doomscript/grammar/phrases.py:276-328`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Consumes: Line assignments, loop headers, entity creations, collection operations.
- Produces: `scope.get_last_singular() -> Optional[str]`, `scope.get_last_plural() -> Optional[str]`, `scope.in_class: bool`.

- [ ] **Step 1.2.1: Write failing test for Dual-Referent ScopeTracker**

```python
from doomscript.grammar.phrases import ScopeTracker

def test_scope_tracker_dual_referents():
    tracker = ScopeTracker()
    assert tracker.get_last_singular() is None
    assert tracker.get_last_plural() is None

    tracker.record_singular("client")
    assert tracker.get_last_singular() == "client"

    tracker.record_plural("orders")
    assert tracker.get_last_plural() == "orders"
    assert tracker.get_last_singular() == "client"  # Preserved

    # Nested block inherits
    tracker.update_indent(4)
    assert tracker.get_last_singular() == "client"
    assert tracker.get_last_plural() == "orders"

    tracker.update_indent(0)
    assert tracker.get_last_singular() == "client"
```

- [ ] **Step 1.2.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_scope_tracker_dual_referents -v`
Expected: FAIL with `AttributeError: 'ScopeTracker' object has no attribute 'get_last_singular'`

- [ ] **Step 1.2.3: Upgrade `ScopeTracker` in `src/doomscript/grammar/phrases.py`**
Add `last_singular`, `last_plural`, `in_class` flags to lexical scope frames, and enhance `extract_assigned_var` to classify targets as plural (lists, collections, sets, dicts) vs singular (scalars, entities).

- [ ] **Step 1.2.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_scope_tracker_dual_referents -v`
Expected: PASS

- [ ] **Step 1.2.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): upgrade ScopeTracker with dual singular and plural discourse referents"`

---

### Task 1.3: Natural Pronoun Resolution (`it`, `that`, `its <field>`, `them`, `these`, `those`, `their`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Consumes: Masked DoomScript source lines with pronouns.
- Produces: Desugared statements with bound variable references.

- [ ] **Step 1.3.1: Write failing tests for pronoun resolution**

```python
from doomscript.compiler.engine import execute

def test_singular_and_plural_pronoun_resolution():
    code = """
a Customer has name, balance
create a Customer with name "Alice", balance 150 into client

if its balance > 100:
    client_status = "preferred"

orders = ["Laptop", "Mouse"]
say their count
collected = []
for each item in them:
    add item to collected
"""
    env = execute(code)
    assert env["client_status"] == "preferred"
    assert env["collected"] == ["Laptop", "Mouse"]
```

- [ ] **Step 1.3.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_singular_and_plural_pronoun_resolution -v`
Expected: FAIL (`its` desugars to `self.balance`, raising `NameError: name 'self' is not defined`)

- [ ] **Step 1.3.3: Implement contextual pronoun replacement in `normalize_statement_text`**
- Check `scope.in_class`: if false, rewrite `\bits\s+([A-Za-z_]\w*)` to `{last_singular}.\1`.
- Rewrite `\b(them|these|those)\b` to `{last_plural}` when used in loop expressions (`in them`, `from them`) or arguments.
- Rewrite `\btheir\s+count\b` to `count of {last_plural}`.

- [ ] **Step 1.3.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_singular_and_plural_pronoun_resolution -v`
Expected: PASS

- [ ] **Step 1.3.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add contextual singular (its) and plural (them, their) pronoun resolution"`

---

### Task 1.4: Universal & Existential Set Quantifier Normalization

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Consumes: `if every X in Y is Z:`, `if all X are Y:`, `if any X in Y has Z:`, `if no X in Y has Z:`.
- Produces: Canonical `if ds_every(Y, lambda X: ...):`, etc.

- [ ] **Step 1.4.1: Write failing tests for Set Quantifiers**

```python
from doomscript.compiler.engine import execute

def test_set_quantifiers_execution():
    code = """
numbers = [2, 4, 6, 8]
all_even = False
if all numbers are even:
    all_even = True

if every n in numbers is positive:
    all_positive = True

mixed = [1, 2, 3]
has_odd = False
if any n in mixed is odd:
    has_odd = True

clean_list = [10, 20, 30]
no_negatives = False
if no x in clean_list is negative:
    no_negatives = True
"""
    env = execute(code)
    assert env["all_even"] is True
    assert env["all_positive"] is True
    assert env["has_odd"] is True
    assert env["no_negatives"] is True
```

- [ ] **Step 1.4.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_set_quantifiers_execution -v`
Expected: FAIL with `DoomSyntaxError: Unexpected token 'numbers'`

- [ ] **Step 1.4.3: Implement quantifier normalizations in `phrases.py`**
Add regex patterns before conditional branching:
- `^\s*if\s+all\s+(.+?)\s+are\s+(.+?):?$` $\rightarrow$ `if ds_every(\1, lambda x: x is \2):`
- `^\s*if\s+every\s+([A-Za-z_]\w*)\s+in\s+(.+?)\s+is\s+(.+?):?$` $\rightarrow$ `if ds_every(\2, lambda \1: \1 is \3):`
- `^\s*if\s+any\s+([A-Za-z_]\w*)\s+in\s+(.+?)\s+is\s+(.+?):?$` $\rightarrow$ `if ds_any(\2, lambda \1: \1 is \3):`
- `^\s*if\s+no\s+([A-Za-z_]\w*)\s+in\s+(.+?)\s+is\s+(.+?):?$` $\rightarrow$ `if ds_none(\2, lambda \1: \1 is \3):`
- Support comparison predicates (`is at least`, `is over`, `>`, `<`, `==`).

- [ ] **Step 1.4.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_set_quantifiers_execution -v`
Expected: PASS

- [ ] **Step 1.4.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add universal, existential, and negative set quantifiers"`

---

## Phase 2: Contextual Attribute Scope, Relative Clauses & Superlatives

### Task 2.1: Runtime Dynamic Attribute & Superlative Helpers

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Produces: `ds_attr(item, attr_name, default=None)`, `ds_find_superlative(collection, order='max', key=None)`.

- [ ] **Step 2.1.1: Write failing unit test for dynamic attribute and superlative helpers**

```python
from doomscript.runtime import ds_attr, ds_find_superlative

def test_runtime_attr_and_superlatives():
    d = {"price": 100}
    class Item: price = 200
    assert ds_attr(d, "price") == 100
    assert ds_attr(Item(), "price") == 200
    assert ds_attr(d, "missing", default=0) == 0

    catalog = [
        {"name": "Widget A", "price": 20},
        {"name": "Widget B", "price": 50},
        {"name": "Widget C", "price": 10},
    ]
    cheapest = ds_find_superlative(catalog, order="min", key="price")
    assert cheapest["name"] == "Widget C"

    largest = ds_find_superlative(catalog, order="max", key="price")
    assert largest["name"] == "Widget B"
```

- [ ] **Step 2.1.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_attr_and_superlatives -v`
Expected: FAIL with `ImportError: cannot import name 'ds_attr'`

- [ ] **Step 2.1.3: Implement `ds_attr` and `ds_find_superlative` in `src/doomscript/runtime.py` and register in `src/doomscript/core/exports.py`**

- [ ] **Step 2.1.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_attr_and_superlatives -v`
Expected: PASS

- [ ] **Step 2.1.5: Commit changes**
`git add src/doomscript/runtime.py src/doomscript/core/exports.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(runtime): add ds_attr safe accessor and ds_find_superlative helper"`

---

### Task 2.2: Contextual Attribute Binding in Thought Queries (`keep only`, `discard from`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py:605-645`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Consumes: `keep only <coll> where <cond> into <target>`, `discard from <coll> where <cond> into <target>`.
- Produces: Desugared filter with contextual attribute resolution.

- [ ] **Step 2.2.1: Write failing test for contextual field query**

```python
from doomscript.compiler.engine import execute

def test_contextual_attribute_query():
    code = """
orders = [
    {"id": 1, "price": 50},
    {"id": 2, "price": 150},
    {"id": 3, "price": 250}
]
keep only orders where price > 100 into expensive_orders
discard from orders where price >= 200 into affordable_orders
"""
    env = execute(code)
    assert len(env["expensive_orders"]) == 2
    assert env["expensive_orders"][0]["id"] == 2
    assert len(env["affordable_orders"]) == 2
    assert env["affordable_orders"][1]["id"] == 2
```

- [ ] **Step 2.2.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_contextual_attribute_query -v`
Expected: FAIL with `DoomNameError: I don't know what 'price' is`

- [ ] **Step 2.2.3: Implement contextual rewriting in `_rewrite_keep_only` and `_rewrite_discard`**
In `phrases.py`:
Inspect tokens in `cond`. If a token is an identifier not in built-in globals or scope, and the item identifier is `item`, rewrite `price` to `ds_attr(item, 'price')`.

- [ ] **Step 2.2.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_contextual_attribute_query -v`
Expected: PASS

- [ ] **Step 2.2.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add implicit contextual attribute resolution for keep only and discard from"`

---

### Task 2.3: Relative Clauses in Loops (`for each X whose Y is Z`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

- [ ] **Step 2.3.1: Write failing test for relative clause loops**

```python
from doomscript.compiler.engine import execute

def test_relative_clause_loop():
    code = """
users = [
    {"name": "Alice", "role": "admin"},
    {"name": "Bob", "role": "guest"},
    {"name": "Charlie", "role": "admin"}
]
admins = []
for each user whose role is "admin":
    add user["name"] to admins
"""
    env = execute(code)
    assert env["admins"] == ["Alice", "Charlie"]
```

- [ ] **Step 2.3.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_relative_clause_loop -v`
Expected: FAIL with `DoomSyntaxError`

- [ ] **Step 2.3.3: Implement `whose` relative clause normalization in `phrases.py`**
Normalize `for each <item> in <coll> where <cond>:` and `for each <item> whose <attr> <cmp> <val>:` by referencing `scope.last_plural` when `<coll>` is omitted or inferring the collection from the plural noun.

- [ ] **Step 2.3.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_relative_clause_loop -v`
Expected: PASS

- [ ] **Step 2.3.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add support for relative clause loops using 'whose'"`

---

### Task 2.4: Natural Superlatives (`find the largest/cheapest/highest X in Y`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

- [ ] **Step 2.4.1: Write failing test for natural superlatives**

```python
from doomscript.compiler.engine import execute

def test_natural_superlatives_syntax():
    code = """
orders = [
    {"id": 101, "amount": 45.0},
    {"id": 102, "amount": 120.0},
    {"id": 103, "amount": 15.0}
]
find the largest order in orders by amount into top_order
find the cheapest order in orders by amount into budget_order
"""
    env = execute(code)
    assert env["top_order"]["id"] == 102
    assert env["budget_order"]["id"] == 103
```

- [ ] **Step 2.4.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_natural_superlatives_syntax -v`
Expected: FAIL with `DoomSyntaxError: Unexpected token 'largest'`

- [ ] **Step 2.4.3: Implement superlative normalization in `phrases.py`**
Map `find (the )?(largest|biggest|highest|maximum|cheapest|smallest|lowest|minimum) ([A-Za-z_]\w*) in (.+?)( by ([A-Za-z_]\w*))? into ([A-Za-z_]\w*)` to `set \7 to ds_find_superlative(\4, order="...", key="...")`.

- [ ] **Step 2.4.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_natural_superlatives_syntax -v`
Expected: PASS

- [ ] **Step 2.4.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add natural superlatives (largest, cheapest, highest, lowest)"`

---

## Phase 3: Declarative Resilience & Compound Action Chaining

### Task 3.1: Runtime Resilience Engine (`ds_retry`, `ds_with_timeout`, `ds_cached_call`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Produces:
  - `ds_retry(action_fn, max_attempts=3, backoff=0.1) -> Any`
  - `ds_with_timeout(action_fn, seconds=5.0) -> Any`
  - `ds_cached_call(cache_key, action_fn, ttl_seconds=300) -> Any`

- [ ] **Step 3.1.1: Write failing unit tests for runtime resilience engine**

```python
import time
import pytest
from doomscript.runtime import ds_retry, ds_with_timeout, ds_cached_call
from doomscript.exceptions import DoomRuntimeError

def test_runtime_resilience():
    # Retry test
    attempts = [0]
    def flaky():
        attempts[0] += 1
        if attempts[0] < 3:
            raise ValueError("Network glitch")
        return "success"

    res = ds_retry(flaky, max_attempts=4, backoff=0.01)
    assert res == "success"
    assert attempts[0] == 3

    # Caching test
    calc_count = [0]
    def slow_calc():
        calc_count[0] += 1
        return 42

    c1 = ds_cached_call("test_key", slow_calc, ttl_seconds=60)
    c2 = ds_cached_call("test_key", slow_calc, ttl_seconds=60)
    assert c1 == 42
    assert c2 == 42
    assert calc_count[0] == 1  # Cache hit
```

- [ ] **Step 3.1.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_resilience -v`
Expected: FAIL with `ImportError: cannot import name 'ds_retry'`

- [ ] **Step 3.1.3: Implement resilience engine in `src/doomscript/runtime.py` and register in `src/doomscript/core/exports.py`**

- [ ] **Step 3.1.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_resilience -v`
Expected: PASS

- [ ] **Step 3.1.5: Commit changes**
`git add src/doomscript/runtime.py src/doomscript/core/exports.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(runtime): add ds_retry, ds_with_timeout, and ds_cached_call resilience helpers"`

---

### Task 3.2: Adverbial Statement Qualifiers (`retrying`, `with timeout of`, `caching for`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

- [ ] **Step 3.2.1: Write failing test for adverbial qualifiers in DoomScript**

```python
from doomscript.compiler.engine import execute

def test_adverbial_qualifiers():
    code = """
run_count = 0
to fetch_data:
    increase run_count by 1
    if run_count < 2:
        zero_div = 1 / 0
    return "ok"

call fetch_data retrying 3 times with 0.01 seconds backoff into res
"""
    env = execute(code)
    assert env["res"] == "ok"
    assert env["run_count"] == 2
```

- [ ] **Step 3.2.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_adverbial_qualifiers -v`
Expected: FAIL with `DoomSyntaxError`

- [ ] **Step 3.2.3: Implement adverbial qualifier desugaring in `phrases.py`**
Normalize trailing clauses:
- `... retrying (\d+) times(?: with ([\d.]+) seconds? backoff)? into ([A-Za-z_]\w*)`
- `... with timeout of ([\d.]+) seconds? into ([A-Za-z_]\w*)`
- `... caching for ([\d.]+) (seconds|minutes|hours) into ([A-Za-z_]\w*)`
Wrapping the core action into a lambda passed to the runtime helper.

- [ ] **Step 3.2.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_adverbial_qualifiers -v`
Expected: PASS

- [ ] **Step 3.2.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add adverbial statement qualifiers for retries, timeouts, and caching"`

---

### Task 3.3: Compound Multi-Action Sentences with Block Continuation

**Files:**
- Modify: `src/doomscript/grammar/phrases.py:3200-3275`
- Test: `tests/test_thought_to_code_all_phases.py`

- [ ] **Step 3.3.1: Write failing test for compound block chaining**

```python
from doomscript.compiler.engine import execute

def test_compound_sentence_block_chaining():
    code = """
data = [10, 20]
status = ""
set count to count of data, then if count > 0:
    status = "non-empty"
"""
    env = execute(code)
    assert env["status"] == "non-empty"
```

- [ ] **Step 3.3.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_compound_sentence_block_chaining -v`
Expected: FAIL with indentation or syntax error

- [ ] **Step 3.3.3: Update multi-clause sentence splitter in `phrases.py`**
In `normalize_with_map`:
When splitting a line on `, then if `, emit the prefix statement at current indent, then emit `if ...:` at current indent, allowing the following indented suite to cleanly attach to the if-statement.

- [ ] **Step 3.3.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_compound_sentence_block_chaining -v`
Expected: PASS

- [ ] **Step 3.3.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): support compound sentence chaining into indented blocks"`

---

## Phase 4: Conversational Set Reshaping, Statistical Introspection & UX Certification

### Task 4.1: Runtime Set Reshaping Builtins (`ds_pair`, `ds_partition`, `ds_flatten`, `ds_pluck`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Test: `tests/test_thought_to_code_all_phases.py`

**Interfaces:**
- Produces:
  - `ds_pair(list_a, list_b, as_dict=False) -> list | dict`
  - `ds_partition(collection, predicate_fn) -> tuple[list, list]`
  - `ds_flatten(iterable) -> list`
  - `ds_pluck(collection, key) -> list`

- [ ] **Step 4.1.1: Write failing unit tests for set reshaping helpers**

```python
from doomscript.runtime import ds_pair, ds_partition, ds_flatten, ds_pluck

def test_runtime_set_reshaping():
    names = ["Alice", "Bob"]
    scores = [95, 88]
    pairs = ds_pair(names, scores)
    assert pairs == [("Alice", 95), ("Bob", 88)]
    pair_dict = ds_pair(names, scores, as_dict=True)
    assert pair_dict == {"Alice": 95, "Bob": 88}

    nums = [1, 2, 3, 4, 5, 6]
    evens, odds = ds_partition(nums, lambda x: x % 2 == 0)
    assert evens == [2, 4, 6]
    assert odds == [1, 3, 5]

    nested = [[1, 2], [3, 4]]
    assert ds_flatten(nested) == [1, 2, 3, 4]

    records = [{"age": 20}, {"age": 30}]
    assert ds_pluck(records, "age") == [20, 30]
```

- [ ] **Step 4.1.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_set_reshaping -v`
Expected: FAIL with `ImportError: cannot import name 'ds_pair'`

- [ ] **Step 4.1.3: Implement set reshaping helpers in `src/doomscript/runtime.py` and register in `src/doomscript/core/exports.py`**

- [ ] **Step 4.1.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_runtime_set_reshaping -v`
Expected: PASS

- [ ] **Step 4.1.5: Commit changes**
`git add src/doomscript/runtime.py src/doomscript/core/exports.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(runtime): add ds_pair, ds_partition, ds_flatten, and ds_pluck builtins"`

---

### Task 4.2: Relational Set Reshaping Syntax (`pair`, `partition`, `flatten`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

- [ ] **Step 4.2.1: Write failing test for relational set syntax**

```python
from doomscript.compiler.engine import execute

def test_relational_set_syntax():
    code = """
students = ["Alice", "Bob"]
mentors = ["Dr. Smith", "Dr. Jones"]
pair students with mentors into assignments
pair students with mentors into dictionary mentor_map

numbers = [1, 2, 3, 4, 5, 6]
partition numbers into evens, odds where x is even

matrix = [[10, 20], [30, 40]]
flatten matrix into flat_list
"""
    env = execute(code)
    assert env["assignments"] == [("Alice", "Dr. Smith"), ("Bob", "Dr. Jones")]
    assert env["mentor_map"] == {"Alice": "Dr. Smith", "Bob": "Dr. Jones"}
    assert env["evens"] == [2, 4, 6]
    assert env["odds"] == [1, 3, 5]
    assert env["flat_list"] == [10, 20, 30, 40]
```

- [ ] **Step 4.2.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_relational_set_syntax -v`
Expected: FAIL with `DoomSyntaxError`

- [ ] **Step 4.2.3: Implement relational transformations in `phrases.py`**
Normalize:
- `^\s*pair\s+(.+?)\s+with\s+(.+?)\s+into\s+dictionary\s+([A-Za-z_]\w*)$` $\rightarrow$ `set \3 to ds_pair(\1, \2, as_dict=True)`
- `^\s*pair\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$` $\rightarrow$ `set \3 to ds_pair(\1, \2)`
- `^\s*partition\s+(.+?)\s+into\s+([A-Za-z_]\w*)\s*,\s*([A-Za-z_]\w*)\s+where\s+(.+?)$` $\rightarrow$ `set \2, \3 to ds_partition(\1, lambda x: \4)`
- `^\s*flatten\s+(.+?)\s+into\s+([A-Za-z_]\w*)$` $\rightarrow$ `set \2 to ds_flatten(\1)`

- [ ] **Step 4.2.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_relational_set_syntax -v`
Expected: PASS

- [ ] **Step 4.2.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add relational pairing, partitioning, and flattening syntax"`

---

### Task 4.3: Conversational Introspection & Analytics Inquiries

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thought_to_code_all_phases.py`

- [ ] **Step 4.3.1: Write failing test for conversational analytics inquiries**

```python
from doomscript.compiler.engine import execute

def test_conversational_analytics_inquiries(capsys):
    code = """
orders = [{"amount": 100}, {"amount": 250}, {"amount": 50}]
what is the total amount in orders
what is the average amount in orders
"""
    env = execute(code)
    out = capsys.readouterr().out
    assert "400" in out
    assert "133.33" in out or "133.3" in out
```

- [ ] **Step 4.3.2: Run test to verify it fails**
`pytest tests/test_thought_to_code_all_phases.py::test_conversational_analytics_inquiries -v`
Expected: FAIL

- [ ] **Step 4.3.3: Implement analytics question desugaring in `phrases.py`**
Map `what is the (total|sum|average|mean|highest|lowest) ([A-Za-z_]\w*) in (.+?)$` to:
`say (total|average|highest|lowest) of ds_pluck(\3, '\2')`.

- [ ] **Step 4.3.4: Run test to verify it passes**
`pytest tests/test_thought_to_code_all_phases.py::test_conversational_analytics_inquiries -v`
Expected: PASS

- [ ] **Step 4.3.5: Commit changes**
`git add src/doomscript/grammar/phrases.py tests/test_thought_to_code_all_phases.py`
`git commit -m "feat(grammar): add conversational analytics inquiries (what is the total/average X in Y)"`

---

### Task 4.4: 150-Phrasing Beginner UX Benchmark Expansion & Zero-Leakage Certification

**Files:**
- Modify: `scratch/audit_beginner_phrasings.py`
- Test: Full test suite (`pytest`)

- [ ] **Step 4.4.1: Expand `scratch/audit_beginner_phrasings.py` with 65 new natural English phrasings**
Add tests covering all 4 phases:
- Plural and possessive discourse referents (`them`, `their`, `its`)
- Universal and existential quantifiers (`all`, `every`, `any`, `no`)
- Contextual attribute filtering without explicit element variables
- Relative clauses (`whose`) and superlatives (`largest`, `cheapest`)
- Adverbial resilience qualifiers (`retrying`, `with timeout of`, `caching for`)
- Relational set transformations (`pair`, `partition`, `flatten`)
- Total test cases expanded from 85 to 150.

- [ ] **Step 4.4.2: Execute audit script and verify 100% pass rate**
`python scratch/audit_beginner_phrasings.py`
Expected: 150/150 SUCCESS (100% Pass Rate), 0 Python Leaks, 0 Syntax Errors.

- [ ] **Step 4.4.3: Run full DoomScript regression test suite**
`pytest tests/ -v`
Expected: All 1,450+ unit and integration tests PASS.

- [ ] **Step 4.4.4: Final Commit & Push**
`git add scratch/audit_beginner_phrasings.py scratch/audit_results.json`
`git commit -m "docs: certify 150/150 beginner UX phrasings passing with zero Python leakage"`
`git push origin main`
