# Natural English Architectural Guardrails Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement three architectural guardrails in DoomScript: (1) Synonym Canonicalization in phrase normalization, (2) Strict Scoped Domain Routing (Option A) to prevent domain cross-talk, and (3) Helpful Did-You-Mean error diagnostics for near-miss English phrases.

**Architecture:** A string-safe synonym canonicalizer in `grammar/phrases.py` standardizes verbs early. `DomainRegistry.try_parse_domain_line` in `domains/registry.py` enforces strict active-domain dispatching based on `use <domain>`. A new `DidYouMeanAdvisor` in `compiler/advisor.py` matches failed lines against active domain syntax templates and decorates Lark syntax errors with actionable suggestions.

**Tech Stack:** Python 3.14, Lark LALR parser, pure Python standard library (no pip dependencies).

**Spec:** [docs/superpowers/specs/2026-10-21-natural-english-guardrails-design.md](file:///C:/Users/kanha/.gemini/antigravity/scratch/doomscript/docs/superpowers/specs/2026-10-21-natural-english-guardrails-design.md)

## Global Constraints

- Pure Python standard library only; zero external pip dependencies.
- 100% backward compatibility preserved across all 41 domains, the 45 `vspython.md` examples, and the 1,220+ test suite.
- String literals in source code must never be mutated by synonym canonicalization.
- Compilation units must have isolated active domain state without leakage across runs.

## Review Focus

1. String literal protection: `"calculate total"` inside quotes must not become `"compute total"`.
2. Core grammar precedence: Core phrases (`find all <Entity> into <target>`, `filter ... where ...`) must execute properly without requiring `use`.
3. Strict domain isolation: Phrases from unactivated domains must not be executed or hijack syntax when `use <domain>` is absent.
4. Error diagnostic clarity: Non-matching phrases with $\ge 45\%$ token similarity to a domain signature must produce a clear `"Did you mean: ..."` diagnostic.
5. Compilation performance: Parse times must improve or remain sub-millisecond per line with strict domain scoping.

---

### Task 1: Synonym Canonicalization Pipeline

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_synonym_canonicalization.py`

**Interfaces:**
- Produces: `canonicalize_synonyms(text: str) -> str` in `src/doomscript/grammar/phrases.py`.
- Consumes: `mask_strings` and `unmask_strings` in `src/doomscript/grammar/phrases.py`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_synonym_canonicalization.py
from doomscript.grammar.phrases import canonicalize_synonyms
from doomscript.compiler.engine import execute

def test_canonicalize_synonyms_transforms_keywords():
    code = 'calculate f1 score between y_test and y_pred into score'
    result = canonicalize_synonyms(code)
    assert result.startswith('compute f1 score')

def test_canonicalize_synonyms_preserves_strings():
    code = 'say "calculate total price" and calculate 10 + 20'
    result = canonicalize_synonyms(code)
    assert '"calculate total price"' in result
    assert 'compute 10 + 20' in result

def test_canonicalize_synonyms_end_to_end():
    # Both calculate and compute execute identically
    env1 = execute('set x to calculate 15 * 3')
    env2 = execute('set x to compute 15 * 3')
    assert env1["x"] == env2["x"] == 45
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_synonym_canonicalization.py -v`  
Expected: FAIL with `ImportError: cannot import name 'canonicalize_synonyms'`

- [ ] **Step 3: Implement `canonicalize_synonyms` and wire into `normalize_with_map`**

In `src/doomscript/grammar/phrases.py`:
1. Implement `canonicalize_synonyms(text: str) -> str`:
   - Mask strings with `mask_strings(text)`.
   - Apply word-boundary substitutions:
     - `\bcalculate\b` $\rightarrow$ `compute`
     - `\bevaluate\b` $\rightarrow$ `compute`
     - `\bmissing\s+values?\b` $\rightarrow$ `missing`
     - `\bnulls?\b` $\rightarrow$ `missing`
     - `\bdesc\b` $\rightarrow$ `descending`
     - `\basc\b` $\rightarrow$ `ascending`
     - `\bconstruct\b` $\rightarrow$ `create`
     - `\bpreview\b` $\rightarrow$ `inspect`
     - `\bexamine\b` $\rightarrow$ `inspect`
   - Unmask strings with `unmask_strings(masked, strings)`.
2. Call `canonicalize_synonyms` at the start of `normalize_with_map` before phrase rules.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_synonym_canonicalization.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/grammar/phrases.py tests/test_synonym_canonicalization.py
git commit -m "feat(grammar): add synonym canonicalization pipeline with string literal preservation"
```

---

### Task 2: Strict Scoped Domain Routing (Option A)

**Files:**
- Modify: `src/doomscript/domains/registry.py`
- Modify: `src/doomscript/compiler/engine.py`
- Test: `tests/test_scoped_domain_routing.py`

**Interfaces:**
- Consumes: `DomainRegistry._active_domains`
- Produces: Strict LIFO dispatch in `DomainRegistry.try_parse_domain_line` when active domains exist, bypassing global scans.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scoped_domain_routing.py
import pytest
from doomscript.compiler.engine import execute
from doomscript.exceptions import DoomScriptSyntaxError

def test_unactivated_domain_does_not_hijack():
    # Without 'use sim', Markov chain simulation shouldn't be executed by domain matcher
    code = """
    trans_matrix = [[0.8, 0.2], [0.4, 0.6]]
    simulate markov chain with transitions trans_matrix and steps 10 from state 0 into history
    """
    with pytest.raises(Exception):
        execute(code)

def test_activated_domain_works():
    code = """
    use sim
    trans_matrix = [[0.8, 0.2], [0.4, 0.6]]
    simulate markov chain with transitions trans_matrix and steps 10 from state 0 into history
    """
    env = execute(code)
    assert len(env["history"]) == 11

def test_compilation_unit_isolation():
    # Run a script with 'use sim'
    execute("use sim\n")
    # Next execution without 'use sim' must start with fresh active domains
    with pytest.raises(Exception):
        execute("simulate markov chain with transitions [[1.0]] and steps 1 from state 0 into h")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_scoped_domain_routing.py -v`  
Expected: FAIL (unactivated domain does match because fallback scan checks all domains)

- [ ] **Step 3: Update `DomainRegistry.try_parse_domain_line` and compiler reset**

In `src/doomscript/domains/registry.py`:
1. In `try_parse_domain_line(line, line_no)`:
   - If `self._active_domains` is populated, only query `self._active_domains` in reverse (LIFO) order.
   - If no active domain matches, return `None` immediately (do not scan inactive candidate domains).
   - If `self._active_domains` is empty, only check domains if line is explicitly namespaced (e.g. `domain.operation`). Otherwise, return `None`.
2. In `src/doomscript/compiler/engine.py`:
   - In `compile_to_ast`, call `get_domain_registry().reset_active()` before `normalize_with_map` to ensure total isolation per script run.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_scoped_domain_routing.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/domains/registry.py src/doomscript/compiler/engine.py tests/test_scoped_domain_routing.py
git commit -m "feat(domains): enforce strict scoped domain routing with isolated compilation lifecycle"
```

---

### Task 3: Helpful "Did-You-Mean" Error Diagnostics

**Files:**
- Create: `src/doomscript/compiler/advisor.py`
- Modify: `src/doomscript/compiler/engine.py`
- Modify: `src/doomscript/exceptions.py`
- Test: `tests/test_did_you_mean_advisor.py`

**Interfaces:**
- Produces: `DidYouMeanAdvisor.find_suggestion(line: str, active_domains: List[str]) -> Optional[str]`
- Consumes: Domain signatures and active domain registry.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_did_you_mean_advisor.py
import pytest
from doomscript.compiler.engine import execute
from doomscript.exceptions import DoomScriptSyntaxError

def test_did_you_mean_finance_option_suggestion():
    # Missing rate and vol
    code = """
    use finance
    price call option with spot 100.0 strike 95.0 expiry 0.5 into call_price
    """
    with pytest.raises(DoomScriptSyntaxError) as exc_info:
        execute(code)
    err_msg = str(exc_info.value)
    assert "Did you mean:" in err_msg
    assert "price" in err_msg
    assert "option with spot" in err_msg
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_did_you_mean_advisor.py -v`  
Expected: FAIL with generic Lark error / `DoomScriptSyntaxError` without "Did you mean:"

- [ ] **Step 3: Implement `DidYouMeanAdvisor` and integrate into `engine.py`**

1. Create `src/doomscript/compiler/advisor.py`:
   - Define canonical signature index per domain (e.g. for finance, ml, sim, viz, audio, db, etc.).
   - Implement `find_suggestion(line: str, active_domains: List[str]) -> Optional[str]`:
     - Tokenize line into words.
     - For each signature in active domains, compute keyword Jaccard overlap: $\frac{|words \cap sig\_words|}{|words \cup sig\_words|}$.
     - If score $\ge 0.40$ and first keyword matches, return the signature.
2. In `src/doomscript/exceptions.py`:
   - Add `DoomScriptSyntaxError(Exception)` with rich formatting (line number, original source excerpt, and suggestion).
3. In `src/doomscript/compiler/engine.py`:
   - In `compile_to_ast`, wrap `parser.parse(normalized_source)` in `try...except lark.exceptions.LarkError as e`.
   - On error, determine the source line from `line_map`.
   - Query `DidYouMeanAdvisor.find_suggestion(orig_line, active_domains)`.
   - Raise `DoomScriptSyntaxError` with line, excerpt, and suggestion.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_did_you_mean_advisor.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/compiler/advisor.py src/doomscript/compiler/engine.py src/doomscript/exceptions.py tests/test_did_you_mean_advisor.py
git commit -m "feat(compiler): add DidYouMeanAdvisor for actionable English syntax diagnostics"
```

---

### Task 4: Full Regression & Documentation Verification

**Files:**
- Test: `tests/test_vspython_all_examples.py`
- Full test suite: `python -m pytest -q`

- [ ] **Step 1: Run all 46 vspython examples test**

Run: `python -m pytest tests/test_vspython_all_examples.py -v`  
Expected: 46 passed in ~10s

- [ ] **Step 2: Run full regression test suite**

Run: `python -m pytest -q`  
Expected: All tests pass (0 failures across all 1,220+ tests)

- [ ] **Step 3: Commit and Push**

```bash
git push origin main
```
