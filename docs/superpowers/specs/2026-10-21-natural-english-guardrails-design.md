# Design Specification: Natural English Architectural Guardrails for DoomScript

**Date**: 2026-10-21  
**Author**: Antigravity & Pair Programming Partner  
**Status**: Approved (Brainstorming Complete)

---

## 1. Executive Summary & Problem Statement

DoomScript's core value proposition is enabling developers to express complex domain operations in clear, spoken English prose without punctuation friction. However, as the language grew to 41 specialized domain packs, two architectural vulnerabilities emerged:
1. **Syntactic Rigidity & Synonym Brittleness**: Different users (and documentation writers) intuitively use synonymous verbs (e.g., `calculate` vs. `compute`, `missing values` vs. `missing`, `desc` vs. `descending`). Hard-coded regular expressions in individual domain parsers failed when a synonym was used.
2. **Global Domain Collision & Ambiguity**: Any candidate line could be inspected by all 41 registered domains even if the script never imported them, allowing unrelated domains to hijack core English syntax (e.g., relational `db` hijacking `find all` from the declarative ORM).
3. **Opaque Parse Failures**: When a user wrote an English phrase with a missing parameter or slight typo, Lark produced generic parser exceptions (`UnexpectedToken`) without hints about the expected syntax signature.

This specification introduces three architectural guardrails to solve these challenges permanently.

---

## 2. Guardrail 1: Synonym Canonicalization

### 2.1 Overview
An early canonicalization pass runs during the normalization phase in `doomscript/grammar/phrases.py`. All string literals are masked prior to canonicalization to guarantee that data contents are never mutated.

### 2.2 Canonicalization Table
The preprocessor normalizes equivalent phrases to their canonical representation:
- **Math & Metric Verbs**:
  - `\bcalculate\b` $\rightarrow$ `compute`
  - `\bevaluate\b` $\rightarrow$ `compute`
- **Creation Verbs**:
  - `\bconstruct\b` $\rightarrow$ `create`
  - `\bmake\b` (in declarative statements like `make record`) $\rightarrow$ `create`
- **Data & Imputation Clauses**:
  - `\bmissing\s+values?\b` $\rightarrow$ `missing`
  - `\bnulls?\b` $\rightarrow$ `missing`
- **Sorting Direction**:
  - `\bdesc\b` $\rightarrow$ `descending`
  - `\basc\b` $\rightarrow$ `ascending`
- **Inspection Verbs**:
  - `\bexamine\b` $\rightarrow$ `inspect`
  - `\bpreview\b` $\rightarrow$ `inspect`

### 2.3 Preserving String Literals
String literals (`"..."`, `'...'`) are masked with unique placeholders `__STR_TOKEN_N__` before replacement and unmasked immediately after, ensuring that strings like `"Please calculate total"` remain unmodified.

---

## 3. Guardrail 2: Strict Scoped Domain Routing (Option A)

### 3.1 Overview
Under **Option A (Strict Active Scoping)**, only domains explicitly declared via `use <domain>` (or namespaced expressions `domain.<verb>`) are queried during line transformation.

### 3.2 Compilation Lifecycle & Scope Isolation
1. **Activation via `use`**: When `use <domain>` (e.g. `use db`, `use ml`, `use viz`) is encountered, the domain is pushed to `DomainRegistry._active_domains`.
2. **Restricted Dispatch**: In `DomainRegistry.try_parse_domain_line`:
   - If `self._active_domains` is populated, only domains in `self._active_domains` are queried in LIFO precedence order.
   - The fallback scan over inactive candidate domains is completely bypassed.
3. **Core Precedence**: Core English syntax (`find all <Entity>`, `filter ... where ...`, `say`, `read file ...`, `write ... to file ...`) is handled directly by core grammar rules and cannot be shadowed by unimported domains.
4. **Clean Scope Reset**: Every call to `compile_to_ast`, `transpile`, or `execute` starts with an explicit `reset_active()`, preventing scope leakage between runs or concurrent test executions.

---

## 4. Guardrail 3: Helpful "Did-You-Mean" Diagnostics

### 4.1 Overview
When an English statement in an active domain is malformed or missing parameters, DoomScript intercepts the failure and provides an actionable suggestion indicating the closest valid syntax pattern.

### 4.2 Signature Registry
Each domain registers human-readable canonical phrase templates in its `verbs` metadata or via an explicit `phrase_signatures` property (e.g.):
- `price (call|put) option with spot <spot> strike <strike> expiry <expiry> rate <rate> vol <vol> into <target>`
- `train knn classifier with features <X> and labels <y> and neighbors <k> into <target>`
- `chart <type> of <data> with x <col> and y <col> titled <title> into <target>`

### 4.3 Error Interception & Similarity Matching
1. **Advisor Component (`DidYouMeanAdvisor`)**:
   - Compares the failed source line against registered signatures of active domains.
   - Computes token overlap (Jaccard similarity on keyword tokens) and Levenshtein distance on leading phrase verbs.
2. **Error Formatting**:
   If token similarity exceeds a threshold ($\ge 0.45$), the advisor intercepts the Lark `UnexpectedToken` / `UnexpectedCharacters` and raises a clean `DoomScriptSyntaxError`:
   ```text
   DoomScript Syntax Error on line 4:
       price call option with spot 100 strike 95 expiry 0.5 into price

   Did you mean:
       price call option with spot <spot> strike <strike> expiry <expiry> rate <rate> vol <vol> into <target>
   ```

---

## 5. Verification & Testing Strategy

1. **Regression Safety**: All 1,221 existing unit tests and all 46 test cases in `tests/test_vspython_all_examples.py` must continue to pass without errors.
2. **Synonym Equivalence Tests**: Verify that both `calculate f1 score ...` and `compute f1 score ...`, `forward fill missing values` and `forward fill missing` execute identically.
3. **Strict Domain Scoping Tests**:
   - Verify that calling a domain statement without `use <domain>` does not trigger domain line transformation.
   - Verify that adding `use <domain>` cleanly enables the domain.
   - Verify that two independent `execute()` calls do not leak active domain state.
4. **Did-You-Mean Diagnostic Tests**:
   - Write intentional near-miss statements (e.g. missing `rate` or `vol` in option pricing) and assert that the raised exception contains the `"Did you mean:"` suggestion.
