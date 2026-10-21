# Deep Syntax Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deepen DoomScript's syntax across 4 core pillars (Pattern Matching, Natural Math & %, Query/Slicing/Pipelines, Advanced Looping & Quantifiers) while maintaining 100% backward compatibility and zero Python abstraction leaks.

**Architecture:** Extend `doom.lark` with explicit grammar rules for `match_stmt`, math expressions (`squared`, `to the power of`, `percent of`), query/slice constructs (`first N items of`, `take/drop`), and spoken pipelines (`pipe ... then ...`). Lower each in `transformer.py` into clean Python AST nodes backed by isolated runtime helpers in `runtime.py`.

**Tech Stack:** Python 3.10+, Lark Parser (LALR(1)), Python AST module, Pytest.

**Spec:** `docs/superpowers/specs/2026-10-21-deep-syntax-expansion-design.md`

## Global Constraints
- Preserve 100% backward compatibility across all 41 domains and existing 1,433 test cases.
- Maintain zero Python error leakage (all runtime exceptions wrap into `DoomError` types).
- Zero LALR(1) shift/reduce conflicts in `doom.lark`.
- Deterministic, reentrant compilation context.

## Review Focus
- Division by zero in percentage and root operations raises friendly `DoomZeroDivisionError`.
- `first N items of` with `N > len(items)` returns the full list gracefully without out-of-bounds error.
- Pattern matching against `None` / `nothing` correctly compares `is None` rather than throwing `DoomAttributeError`.
- Variable name collisions with synthetic variables (`_match_val`, `_pipe`) use hygienic naming.
- Downward ranges `from 10 down to 1` terminate at 1 inclusive.

---

### Task 1: Runtime Primitives for Statistics, Slicing & Pipelines

**Files:**
- Modify: `src/doomscript/runtime.py`
- Test: `tests/test_deep_syntax_expansion.py`

- [ ] **Step 1.1**: Write failing unit tests for `ds_median`, `ds_stdev`, `ds_variance`, `ds_enumerate`, `ds_take`, `ds_drop` in `tests/test_deep_syntax_expansion.py`.
- [ ] **Step 1.2**: Implement `ds_median`, `ds_stdev`, `ds_variance`, `ds_enumerate`, `ds_take`, `ds_drop` in `src/doomscript/runtime.py` with pure standard library `statistics` and safe slicing.
- [ ] **Step 1.3**: Run `pytest tests/test_deep_syntax_expansion.py` and verify all runtime primitive tests pass.
- [ ] **Step 1.4**: Commit changes: `git commit -m "feat(runtime): add deep syntax helpers for statistics, slicing, and enumeration"`.

---

### Task 2: English Mathematical, Statistical & Percentage Expressions

**Files:**
- Modify: `src/doomscript/grammar/doom.lark`
- Modify: `src/doomscript/compiler/transformer.py`
- Test: `tests/test_deep_syntax_expansion.py`

- [ ] **Step 2.1**: Write tests in `tests/test_deep_syntax_expansion.py` testing:
  - `x squared`, `x cubed`
  - `base to the power of exp`, `base raised to exp`
  - `square root of 144`, `cube root of 27`
  - `15 percent of total`, `20 % of 500`
  - `median of numbers`, `variance of numbers`, `stdev of numbers`, `product of numbers`
- [ ] **Step 2.2**: Add grammar rules in `doom.lark` for power expressions (`squared`, `cubed`, `to the power of`), roots (`square root of`, `cube root of`), percentage (`percent of`), and statistical aggregates.
- [ ] **Step 2.3**: Implement AST transformer methods in `src/doomscript/compiler/transformer.py` for each newly introduced rule.
- [ ] **Step 2.4**: Run `pytest tests/test_deep_syntax_expansion.py -k "math or percent or stats"` and confirm they pass.
- [ ] **Step 2.5**: Commit changes: `git commit -m "feat(grammar): add spoken math, percentage, and statistical expressions"`.

---

### Task 3: Pattern Matching & Decision Blocks (`match ... when ... otherwise`)

**Files:**
- Modify: `src/doomscript/grammar/doom.lark`
- Modify: `src/doomscript/compiler/transformer.py`
- Test: `tests/test_deep_syntax_expansion.py`

- [ ] **Step 3.1**: Write tests in `tests/test_deep_syntax_expansion.py` covering:
  - `match x:` with literal values (`when 1:`, `when "hello":`)
  - `match x:` with unary predicates (`when is even:`, `when is positive:`)
  - `match x:` with binary predicates (`when is greater than 10:`, `when is between 5 and 15:`)
  - `match x:` with list membership (`when one of [1, 2, 3]:`)
  - `otherwise:` fallback
- [ ] **Step 3.2**: Add `match_stmt`, `when_clause`, `otherwise_clause`, and `when_condition` rules to `doom.lark`.
- [ ] **Step 3.3**: Implement `match_stmt` in `src/doomscript/compiler/transformer.py` to emit an `ast.If` ladder comparing against temporary `_match_val`.
- [ ] **Step 3.4**: Run `pytest tests/test_deep_syntax_expansion.py -k "match"` and confirm all tests pass.
- [ ] **Step 3.5**: Commit changes: `git commit -m "feat(grammar): add English pattern matching with when and otherwise"`.

---

### Task 4: Collection Querying, Slicing & Spoken Pipelining

**Files:**
- Modify: `src/doomscript/grammar/doom.lark`
- Modify: `src/doomscript/compiler/transformer.py`
- Test: `tests/test_deep_syntax_expansion.py`

- [ ] **Step 4.1**: Write tests in `tests/test_deep_syntax_expansion.py` testing:
  - `first 3 items of scores`, `last 2 items of scores`
  - `take 4 from items into sample`, `drop 2 from items into rest`
  - `pipe raw into clean_text then tokenize then count_words into result`
  - `set res to pipe x into f1 then f2`
- [ ] **Step 4.2**: Add grammar rules for quantity slicing (`slice_first_n`, `slice_last_n`), `take_n_stmt`, `drop_n_stmt`, and `pipe_stmt` / `pipe_expr`.
- [ ] **Step 4.3**: Implement AST transformer methods in `src/doomscript/compiler/transformer.py`.
- [ ] **Step 4.4**: Run `pytest tests/test_deep_syntax_expansion.py -k "slice or pipe"` and confirm they pass.
- [ ] **Step 4.5**: Commit changes: `git commit -m "feat(grammar): add first/last slicing, take/drop, and spoken pipelines"`.

---

### Task 5: Deepened Looping & English Quantifiers

**Files:**
- Modify: `src/doomscript/grammar/doom.lark`
- Modify: `src/doomscript/compiler/transformer.py`
- Test: `tests/test_deep_syntax_expansion.py`

- [ ] **Step 5.1**: Write tests in `tests/test_deep_syntax_expansion.py` testing:
  - `for each item and its index in items:`
  - `for each x from 10 down to 1:`
  - `if all of items are positive:`, `if any of items is negative:`, `if none of items is zero:`
- [ ] **Step 5.2**: Add grammar rules in `doom.lark` for indexed loops, downward ranges, and quantifier expressions (`all of`, `any of`, `none of`).
- [ ] **Step 5.3**: Implement AST transformer methods in `src/doomscript/compiler/transformer.py`.
- [ ] **Step 5.4**: Run `pytest tests/test_deep_syntax_expansion.py -k "loop or quantifier"` and verify they pass.
- [ ] **Step 5.5**: Commit changes: `git commit -m "feat(grammar): add indexed looping, downward ranges, and English quantifiers"`.

---

### Task 6: Full Regression & Audit Conformance

**Files:**
- Verify: `tests/`
- Verify: `scratch/audit_beginner_phrasings.py`

- [ ] **Step 6.1**: Run `pytest tests/test_deep_syntax_expansion.py` to verify all new syntax tests pass.
- [ ] **Step 6.2**: Run `pytest tests/` (full test suite) to ensure 0 regressions across all existing tests.
- [ ] **Step 6.3**: Run `python scratch/audit_beginner_phrasings.py` to confirm 85/85 Beginner UX benchmark passes with zero Python leaks.
- [ ] **Step 6.4**: Commit final integration: `git commit -m "chore: complete deep syntax expansion verification gate"`.
