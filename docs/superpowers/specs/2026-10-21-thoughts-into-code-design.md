# DoomScript Stream-of-Thought Programming Design Specification

**Date:** 2026-10-21  
**Status:** Approved  
**Scope:** Conversational Phrasing, Intent-Driven Statements, Thought Queries, Interrogative Output  

---

## 1. Overview & Vision

In everyday human thinking, people do not conceptualize programming in mechanical imperatives like `assign value to register` or `execute loop counter`. Instead, humans think in:
- **Hypotheses & Assumptions**: *"Suppose the tax rate is 5%..."*, *"Let's say total is 200..."*, *"Remember this result as final_total..."*
- **Intentional Goals**: *"How to calculate area given length and width..."*, *"In order to process order..."*
- **Reasoning Conditions**: *"As long as we have items left..."*, *"In case of an error..."*, *"If it turns out that attempts > 3..."*
- **Mental Queries**: *"Keep only adults where age >= 18..."*, *"Find the first transaction where amount > 1000..."*, *"Check whether user is verified..."*
- **Interrogatives & Inquiries**: *"What is 15 percent of 200?"*, *"Tell me the result..."*, *"Does the list contain target?"*

This specification establishes native support for **Stream-of-Thought Programming** across four cohesive pillars.

---

## 2. Pillar A: Conversational Hypotheses & Intent-Driven Definitions

### 2.1 Hypotheses & Assumptions (Variable Bindings)
- `suppose <var> is <expr>` $\rightarrow$ `set <var> to <expr>`
- `assume <var> is <expr>` $\rightarrow$ `set <var> to <expr>`
- `let's say <var> is <expr>` $\rightarrow$ `set <var> to <expr>`
- `remember <expr> as <var>` $\rightarrow$ `set <var> to <expr>`

### 2.2 Intentional Goals (Function Definitions)
- `"how" "to" NAME ["with" param_list] ":"` $\rightarrow$ `to NAME with param_list:`
- `"in" "order" "to" NAME ["with" param_list] ":"` $\rightarrow$ `to NAME with param_list:`
- `"the" "goal" "is" "to" NAME ["with" param_list] ":"` $\rightarrow$ `to NAME with param_list:`

---

## 3. Pillar B: Stream-of-Thought Control Flow & Natural Guards

### 3.1 Conversational Loops & Conditions
- `as long as <expr>:` $\rightarrow$ `while <expr>:`
- `for every <item> in <collection>:` $\rightarrow$ `for each <item> in <collection>:`
- `for each and every <item> in <collection>:` $\rightarrow$ `for each <item> in <collection>:`
- `in case <expr>:` $\rightarrow$ `if <expr>:`
- `if it turns out that <expr>:` $\rightarrow$ `if <expr>:`
- `in the worst case:` $\rightarrow$ `else:`

### 3.2 Human Error Handling & Safeguards
- `make sure that <expr> otherwise <msg>` $\rightarrow$ `verify that <expr> otherwise <msg>`
- `try to:` ... `if it goes wrong [as NAME]:` $\rightarrow$ `try: ... if that fails [as NAME]:`
- `try to:` ... `if anything goes wrong [as NAME]:` $\rightarrow$ `try: ... if that fails [as NAME]:`

---

## 4. Pillar C: Thought Queries & Intuitive Filtering

### 4.1 Intent Filtering
- `keep only <collection> where <cond> into <target>` $\rightarrow$ filters elements satisfying `<cond>` into `<target>`.
- `discard from <collection> where <cond> into <target>` $\rightarrow$ filters elements NOT satisfying `<cond>` into `<target>`.

### 4.2 Thought Lookups
- `find first in <collection> where <cond> into <target>` $\rightarrow$ returns first matching element or `None`.
- `check whether <cond> into <target>` $\rightarrow$ `set <target> to (<cond>)`.
- `check if <collection> contains <item> into <target>` $\rightarrow$ `set <target> to (<item> in <collection>)`.

---

## 5. Pillar D: Interrogative Inquiries & Spoken Outputs

### 5.1 Direct Questions as Outputs
- `what is <expr>` $\rightarrow$ `say <expr>` (e.g. `what is 15 percent of 200` $\rightarrow$ outputs `30.0`).
- `what is the <agg> of <collection>` $\rightarrow$ `say <agg> of <collection>`.
- `tell me <expr>` / `tell us <expr>` $\rightarrow$ `say <expr>`.
- `show me <expr>` / `show us <expr>` $\rightarrow$ `say <expr>`.

### 5.2 Conversational Question Inquiries
- `how many items in <collection> into <target>` $\rightarrow$ `set <target> to count of <collection>`.
- `does <collection> contain <item> into <target>` $\rightarrow$ `set <target> to (<item> is inside <collection>)`.

---

## 6. Implementation Architecture & Invariants

1. **Desugaring to Deterministic Primitives:** All stream-of-thought phrases lower cleanly into canonical AST representations (`assign`, `set_var`, `func_def`, `for_stmt`, `while_stmt`, `try_stmt`, `say_multi`) or explicit runtime helpers (`ds_find_first`, `ds_filter_val`).
2. **Zero Ambiguity:** Regexes and tokens use word boundaries (`\b`) and sentence-start anchors (`^\s*`) ensuring standard identifiers (like variable `total` or string `"in case"`) are never corrupted.
3. **Regression Safety:** All 1,433 existing tests, 85/85 Beginner UX benchmark, and new deep syntax tests must continue passing 100%.
