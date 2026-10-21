# DoomScript Deep Syntax Expansion: Design Specification

**Date:** 2026-10-21  
**Status:** Approved  
**Scope:** Core Grammar, AST Transformer, Lexer, and Runtime Primitives  

---

## 1. Executive Summary & Goals

DoomScript is designed as an English-first, deterministic programming language. While previous phases established domain vocabulary and core phrase normalization, several fundamental English language patterns—such as pattern matching, natural mathematical and percentage expressions, collection querying/slicing, spoken pipelining, and collective quantifiers—either required cumbersome syntactic workarounds or lacked native grammar support.

This specification deepens DoomScript's syntax across **four core pillars**:
1. **Pattern Matching & Decision Blocks (`match ... when ... otherwise`)**
2. **English Mathematical, Statistical & Percentage Expressions**
3. **First-Class Collection Querying, Slicing & Spoken Pipelining**
4. **Deepened Looping (with 1-based index) & English Quantifiers**

---

## 2. Pillar 1: Pattern Matching & Decision Blocks

### 2.1 Grammar Additions (`doom.lark`)
```ebnf
?compound_stmt: ...
              | match_stmt

match_stmt: "match" expr ":"? _NEWLINE _INDENT when_clause+ [otherwise_clause] _DEDENT -> match_stmt
when_clause: "when" when_condition ":"? _NEWLINE suite -> when_clause
otherwise_clause: ("otherwise" | "else") ":"? _NEWLINE suite -> otherwise_clause

?when_condition: IS_EVEN                                        -> when_is_even
               | IS_ODD                                         -> when_is_odd
               | IS_POSITIVE                                    -> when_is_positive
               | IS_NEGATIVE                                    -> when_is_negative
               | IS_ZERO                                        -> when_is_zero
               | IS_BETWEEN bitwise_or "and" bitwise_or          -> when_between
               | IS_OUTSIDE bitwise_or "and" bitwise_or          -> when_outside
               | (IS_ONE_OF | "one" "of") factor               -> when_one_of
               | CMP_OP bitwise_or                              -> when_cmp
               | expr                                           -> when_val
```

### 2.2 AST Lowering (`transformer.py`)
- Evaluates the subject expression once into a synthetic temporary identifier `_match_target`.
- Compiles `when` clauses into an `if / elif / else` ladder:
  - `when 100:` $\rightarrow$ `_match_target == 100`
  - `when is even:` $\rightarrow$ `_match_target % 2 == 0`
  - `when is between 10 and 20:` $\rightarrow$ `10 <= _match_target <= 20`
  - `when is greater than 50:` $\rightarrow$ `_match_target > 50`
  - `when one of [1, 2, 3]:` $\rightarrow$ `_match_target in [1, 2, 3]`
- `otherwise:` maps directly to the final `else:` block.

---

## 3. Pillar 2: English Mathematical, Statistical & Percentage Expressions

### 3.1 Exponentiation & Roots
- `atom "squared"` $\rightarrow$ `(atom ** 2)`
- `atom "cubed"` $\rightarrow$ `(atom ** 3)`
- `atom ("to" "the" "power" ["of"] | "raised" "to") factor` $\rightarrow$ `(atom ** factor)`
- `("square" "root" | "sqrt") "of" factor` $\rightarrow$ `math.sqrt(factor)`
- `("cube" "root") "of" factor` $\rightarrow$ `(factor ** (1.0 / 3.0))`

### 3.2 Percentage Operations
- `factor ("percent" | "%") "of" factor` $\rightarrow$ `((factor / 100.0) * factor)`
  - Example: `15 percent of total` $\rightarrow$ `((15 / 100.0) * total)`
  - Example: `15 % of 200` $\rightarrow$ `30.0`

### 3.3 Statistical Aggregates
- Extends `aggregate_expr` with:
  - `"median" "of" factor` $\rightarrow$ `ds_median(factor)`
  - `("standard" "deviation" | "stdev") "of" factor` $\rightarrow$ `ds_stdev(factor)`
  - `"variance" "of" factor` $\rightarrow$ `ds_variance(factor)`
  - `"product" "of" factor` $\rightarrow$ `math.prod(factor)`

---

## 4. Pillar 3: Collection Querying, Slicing & Spoken Pipelining

### 4.1 Quantity Slicing
- In `aggregate_expr`:
  - `"first" atom ["items" | "item"] ("of" | "in") factor` $\rightarrow$ `factor[:atom]`
  - `"last" atom ["items" | "item"] ("of" | "in") factor` $\rightarrow$ `factor[-atom:]`
- In `simple_stmt`:
  - `"take" atom "from" expr ["into" target]` $\rightarrow$ `target = expr[:atom]`
  - `"drop" atom "from" expr ["into" target]` $\rightarrow$ `target = expr[atom:]`

### 4.2 Spoken Pipelining
- `"pipe" expr "into" ident ("then" ident)+ ["into" target]`
  - Statement lowering:
    ```python
    _pipe = fn1(expr)
    _pipe = fn2(_pipe)
    target = fn3(_pipe)
    ```
- Inline expression form:
  - `"pipe" expr "into" ident ("then" ident)+` $\rightarrow$ returns chained call result.

---

## 5. Pillar 4: Deepened Looping & English Quantifiers

### 5.1 Enumerate Looping (1-Based Indexing)
- `"for" ["each"] ident "and" ("its" | "their") "index" "in" expr ":"? _NEWLINE suite`
  - Lowers to:
    ```python
    for index, ident in ds_enumerate(expr, start=1):
        ...
    ```

### 5.2 Descending Step Ranges
- `"for" ["each"] for_target "from" expr "down" "to" expr ["by" expr] ":"? _NEWLINE suite`
  - Lowers to negative step `range(start, end - 1, -step)`.

### 5.3 Collective English Quantifiers
- In `compare_expr`:
  - `"all" "of" factor "are" (IS_POSITIVE | IS_NEGATIVE | IS_EVEN | IS_ODD | IS_ZERO)`
  - `"any" "of" factor "is" (IS_POSITIVE | IS_NEGATIVE | IS_EVEN | IS_ODD | IS_ZERO)`
  - `"none" "of" factor "is" (IS_POSITIVE | IS_NEGATIVE | IS_EVEN | IS_ODD | IS_ZERO)`
- Lowered cleanly to Python comprehension generator expressions wrapped in `all(...)` / `any(...)`.

---

## 6. Zero Regression & Invariants Guarantee
1. **LALR(1) Conflict Prevention:** All grammar additions are scoped to unambiguous prefix tokens (`match`, `when`, `pipe`, `take`, `drop`, `squared`, `percent of`).
2. **Backward Compatibility:** All existing 1,433 unit tests and 85/85 Beginner UX Audit tests must continue to pass 100%.
3. **Pure English Runtime:** All errors translate into `DoomError` or clear syntactic guidance without Python traceback leakage.
