# Deep Syntax Expansion Execution Ledger

**Plan:** `docs/superpowers/plans/2026-10-21-deep-syntax-expansion.md`  
**Spec:** `docs/superpowers/specs/2026-10-21-deep-syntax-expansion-design.md`  
**Base Commit:** `36431fb`  
**Started:** 2026-10-21  

## Task Status
- [x] Task 1: Runtime Primitives for Statistics, Slicing & Pipelines (Commit: 4abb0ab)
- [x] Task 2: English Mathematical, Statistical & Percentage Expressions (Commit: a79e999)
- [x] Task 3: Pattern Matching & Decision Blocks (`match ... when ... otherwise`) (Commit: 3e2b868)
- [x] Task 4: Collection Querying, Slicing & Spoken Pipelining (Commit: 13e38ef)
- [x] Task 5: Deepened Looping & English Quantifiers (Commit: d0f4b1d)
- [x] Task 6: Full Regression & Audit Conformance (77/77 regression tests passed, 85/85 Beginner UX Audit passed)

## Decisions & Rulings Log
- Ruling: In `match` statements, pattern matching on predicates (`is greater than`, `is between`, `is even/odd/positive/negative/zero`) lowers to explicit comparisons against a synthetic temporary variable `_match_val` to guarantee full deterministic behavior.
- Ruling: Quantity slicing (`first N items of`, `last N items of`) uses `NUMBER` in the grammar to avoid any token collision with `agg_first` (`first item of`), guaranteeing zero shift/reduce ambiguity.
- Ruling: Multi-step pipelining with `then` (`pipe X into f1 then f2 into Y`) is normalized into `ds_pipe(X, f1, f2)` in the phrase layer, supporting both statement and inline expression forms.
- Ruling: Descending ranges (`for each n from 5 down to 1:`) are supported by allowing `down to` in `for_range_stmt` and automatically defaulting the step in `range_inclusive` to `-1` when `start > stop`.
