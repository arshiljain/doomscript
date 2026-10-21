# Stream-of-Thought Programming Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable natural human thought phrasing in DoomScript ("suppose x is 10", "how to calculate tax with price:", "as long as queue is not empty:", "keep only users where age >= 18 into adults", "what is 15 percent of 200") with 100% deterministic compilation, zero Python leaks, and zero regression.

**Architecture:** Extend phrase normalization in `phrases.py` and runtime helpers in `runtime.py` to desugar conversational assumptions, intentional goal definitions, thought queries, and interrogatives into canonical AST primitives.

**Tech Stack:** Python 3.10+, Lark Parser, Regex phrase normalizer, Pytest.

**Spec:** `docs/superpowers/specs/2026-10-21-thoughts-into-code-design.md`

## Global Constraints
- Preserve 100% backward compatibility across all 41 domains and existing 1,433+ test cases.
- Maintain zero Python error leakage (all runtime exceptions wrap into `DoomError` types).
- Use strict word boundaries and line anchors to prevent collisions with existing variables or strings.

## Review Focus
- `what is <expr>` inside string literals or comments must never be altered.
- `as long as` must handle complex conditions (`queue is not empty and attempts < 5`).
- `keep only` and `discard from` must support records, dicts, and primitive lists.
- `find first in` returns `None` safely when no element matches, rather than raising `IndexError`.
- Multiple conversational clauses in a single file must chain without line-map drift.

---

### Task 1: Runtime Helper for Thought Queries (`ds_find_first`)

**Files:**
- Modify: `src/doomscript/runtime.py`
- Modify: `src/doomscript/core/exports.py`
- Test: `tests/test_thoughts_into_code.py`

- [ ] **Step 1.1**: Write failing unit test for `ds_find_first` in `tests/test_thoughts_into_code.py`.
- [ ] **Step 1.2**: Implement `ds_find_first(collection, predicate)` in `src/doomscript/runtime.py` and register it in `CORE_EXPORT_NAMES`.
- [ ] **Step 1.3**: Run `python -m pytest tests/test_thoughts_into_code.py -k "find_first"` to verify.
- [ ] **Step 1.4**: Commit changes: `git commit -m "feat(runtime): add ds_find_first helper for thought queries"`.

---

### Task 2: Conversational Hypotheses & Intent-Driven Definitions (Pillar A)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thoughts_into_code.py`

- [ ] **Step 2.1**: Write tests in `tests/test_thoughts_into_code.py` for:
  - `suppose total is 500`, `assume rate is 0.05`
  - `let's say discount is 10 percent of total`
  - `remember score * 2 as bonus`
  - `how to calculate_tax with price, rate:`
  - `in order to find_hypotenuse with a, b:`
  - `the goal is to process_payment with account, amount:`
- [ ] **Step 2.2**: Add regex patterns in `phrases.py` for hypotheses and function goal phrasing.
- [ ] **Step 2.3**: Run `python -m pytest tests/test_thoughts_into_code.py -k "hypotheses or definitions"` to verify.
- [ ] **Step 2.4**: Commit changes: `git commit -m "feat(grammar): add conversational hypotheses and intentional definitions"`.

---

### Task 3: Stream-of-Thought Control Flow & Natural Guards (Pillar B)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thoughts_into_code.py`

- [ ] **Step 3.1**: Write tests in `tests/test_thoughts_into_code.py` for:
  - `as long as queue is not empty:`
  - `for every user in users:`, `for each and every item in items:`
  - `in case balance is negative:`, `if it turns out that attempts > 3:`
  - `in the worst case:`
  - `make sure that age >= 18 otherwise "Must be an adult"`
  - `try to:` ... `if it goes wrong as problem:`
- [ ] **Step 3.2**: Add normalizations in `phrases.py` for loops, guards, and error phrases.
- [ ] **Step 3.3**: Run `python -m pytest tests/test_thoughts_into_code.py -k "control_flow or guards"` to verify.
- [ ] **Step 3.4**: Commit changes: `git commit -m "feat(grammar): add stream-of-thought control flow and natural guards"`.

---

### Task 4: Thought Queries & Intuitive Filtering (Pillar C)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thoughts_into_code.py`

- [ ] **Step 4.1**: Write tests in `tests/test_thoughts_into_code.py` for:
  - `keep only users where age is at least 18 into adults`
  - `discard from scores where score < 50 into passing`
  - `find first in transactions where amount > 1000 into flagged`
  - `check whether score >= 90 into is_honors`
  - `check if blacklist contains ip into is_blocked`
- [ ] **Step 4.2**: Implement phrase rules for keep/discard, find first, and check whether/if.
- [ ] **Step 4.3**: Run `python -m pytest tests/test_thoughts_into_code.py -k "thought_queries or filtering"` to verify.
- [ ] **Step 4.4**: Commit changes: `git commit -m "feat(grammar): add thought queries and intuitive filtering"`.

---

### Task 5: Interrogative Inquiries & Collaborative Outputs (Pillar D)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Test: `tests/test_thoughts_into_code.py`

- [ ] **Step 5.1**: Write tests in `tests/test_thoughts_into_code.py` for:
  - `what is 15 percent of 200`
  - `what is the average of scores`
  - `tell me "Processing complete"` / `tell us result`
  - `show me top_3`
  - `how many items in orders into total_orders`
  - `does catalog contain "SKU-99" into has_item`
- [ ] **Step 5.2**: Add phrase normalizations for interrogative questions and output requests.
- [ ] **Step 5.3**: Run `python -m pytest tests/test_thoughts_into_code.py -k "interrogatives"` to verify.
- [ ] **Step 5.4**: Commit changes: `git commit -m "feat(grammar): add interrogative questions and conversational outputs"`.

---

### Task 6: Full Regression & Audit Conformance

**Files:**
- Verify: `tests/`
- Verify: `scratch/audit_beginner_phrasings.py`

- [ ] **Step 6.1**: Run `python -m pytest tests/test_thoughts_into_code.py` (all tests pass).
- [ ] **Step 6.2**: Run `python scratch/audit_beginner_phrasings.py` to confirm 85/85 Beginner UX benchmark passes with zero Python leaks.
- [ ] **Step 6.3**: Run key test suites to ensure zero regressions across existing syntax.
- [ ] **Step 6.4**: Commit final integration: `git commit -m "chore: complete stream-of-thought verification gate"`.
