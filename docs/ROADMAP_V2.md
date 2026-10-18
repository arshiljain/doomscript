# DoomScript V2 Roadmap: English-First General Purpose Language

## Executive Summary
DoomScript is evolving from a gaming-oriented syntax demo into an English-first, general-purpose programming language compiling to Python AST. Its primary mission is empowering beginners, analysts, students, and automation developers to write robust scripts for everyday computing tasks (files, CSVs, data transformation, HTTP/JSON APIs, text manipulation) using plain, natural English prose.

Legacy game/graphics/audio primitives (`open window`, `beep`, `draw circle`, etc.) remain fully supported but are frozen. All new design and engineering efforts focus on deterministic natural language programming, flexible phrasing, strict AST semantics, and beginner-friendly tooling.

---

## Step 0: Formal Audit Findings

### 1. Test Suite & Baseline Verification
- **Current Test Count**: 31 pytest tests.
- **Pass Rate**: 100% (31/31 passed in 18.6s).
- **Core Pipeline**: Source -> Normalization/Preprocessing -> Lark LALR(1) + PythonIndenter -> DoomToPython Transformer -> Python Standard `ast` -> `exec()` / `ast.unparse()`.

### 2. Grammar Ambiguities & LALR(1) Conflicts
1. **Dual Meaning of "is" (Assignment vs Comparison)**:
   - In Lark: `assign_stmt: target ("=" | "is") expr` vs `CMP_OP: ... | "is"`.
   - Current status: At statement root level, Lark shifts `is` into `assign_stmt` because arbitrary expression statements are restricted to `func_call`. However, inside expressions (`if x is 5`), `is` is a comparison operator.
   - Ambiguity Risk: Chained expressions or bare statements like `x is 5` could be confused with comparisons if bare expressions were allowed as statements.
   - Resolution: Keep assignment syntax deterministic. In the normalization layer, map assignment variants (`let x be 5`, `make x 5`, `set x to 5`, `put 5 into x`) to canonical `x = 5` or `set x to 5`.
2. **Optional Colons (`:?`)**:
   - Rules: `if_stmt`, `repeat_stmt`, `for_stmt`, `func_def`, `attempt_stmt` end in `:? _NEWLINE suite`.
   - In LALR(1), trailing `:?` works cleanly when immediately followed by `_NEWLINE`. However, if expressions are expanded to support Python-like slice syntax `[1:3]` or inline dictionary syntax `{a: b}`, lookahead conflicts can arise if an expression ends right before an optional colon.
   - Resolution: Enforce explicit delimiters on collections and slicing so expressions never leave trailing ambiguous colons before block headers.
3. **Free-form `call_stmt` & Preposition Splitting**:
   - `call_stmt: "call" NAME [atom] ["with" arg_list]`
   - Ambiguity: Without strict keyword boundaries, `call greet target with message` parses well, but free-form English verbs without a leading `call` or canonical verb keyword conflict with identifiers.
   - Resolution: Maintain clear verb lead-ins or normalize natural phrasings in the phrase table layer into canonical keyword forms before parser invocation.
4. **Multi-word Terminal Collisions**:
   - Multi-word tokens (`is empty`, `starts with`, `ends with`, `matches pattern`) require priority (`.3`) in Lark so that the lexer does not break them into separate identifier tokens (`is`, `empty`).
   - Adding multi-word phrases directly into Lark increases terminal collision risks.
   - Resolution: Normalization layer handles multi-word synonyms and transforms them into canonical single/multi-word tokens recognized by Lark.
5. **Preposition `of` Sharing**:
   - Used across `aggregate_expr` (`sum of x`), `count_expr` (`count of x`), `percent_expr` (`15% of x`), and possessive expressions.
   - Resolution: Normalization pre-pass cleans up articles (`the count of x` -> `count of x`, `the length of x` -> `count of x`) so Lark only handles canonical aggregate rules.

---

## Phase Plan & Prioritization

### Phase 1: Normalization & Phrase Layer (The Key Upgrade)
- **Goal**: Flexible on input, strict on meaning. Driven by data tables in `src/doomscript/grammar/phrases.py`.
- **Components**:
  1. **Ignorable Filler Words**: Strip non-essential articles and polite fillers (`the`, `a`, `an`, `please`, `then`, `just`) in statement and expression positions without mutating string literals or identifiers.
  2. **Synonym Dictionaries**:
     - Verbs: `show`, `print`, `display`, `tell` -> `say`; `let ... be ...`, `make ... ...`, `put ... into ...`, `set ... to ...` -> assignment; `give back`, `hand back` -> `return`.
     - Comparisons: `is greater than`, `is bigger than`, `is more than`, `is over`, `exceeds` -> `>`; `is at least`, `is no less than` -> `>=`; `is less than`, `is under`, `is smaller than` -> `<`; `is at most`, `is no more than` -> `<=`; `equals`, `is equal to` -> `==`.
  3. **Sentence Endings & Statement Chaining**:
     - Period `.` or newline terminates a statement.
     - `and then` chains statements on a single line into indented/sequential statements.
  4. **Pronoun Resolution (`it` / `that`)**:
     - Desugars `it` or `that` to reference the last assigned variable or evaluated result within the active scope.
     - Strict unambiguous scoping: If no variable was assigned or scope is ambiguous, raises a helpful compile-time syntax error.
  5. **Possessives & Articles**:
     - `the length of x`, `length of x`, `x's length` -> canonical `count of x`.

### Phase 2: Everyday Programming in English
- **Goal**: Enable complete non-game scripting with standard library utilities.
- **Features**:
  1. **Input/Output & Interpolation**:
     - `ask "Question" into target`, numeric prompt `ask number "Age?" into age`, boolean prompt `ask yes/no "Continue?" into proceed`.
     - String interpolation `say "Hello {name}"` and multi-item printing `say "Total:", total`.
  2. **Lists, Records & Transformations**:
     - English list syntax: `a list of 1, 2, 3`, `an empty list`.
     - Operations: `add x to list`, `remove x from list`, `insert x at index 1 in list`.
     - Accessors: `item 2 of list` (1-indexed English or 0-indexed), `first 3 items of list`, `sorted list`, `reversed list`, `unique items of list`.
     - Predicates: `list contains x`, `list is empty`, `list is not empty`.
  3. **Data Operations & Query Expressions**:
     - `sort people by age (descending)`.
     - Filter: `people where age is over 18 into adults`.
     - Mapping: `names is the name of each person in people`.
     - Grouping: `group orders by customer into customer_orders`.
     - Aggregates: `total of price in orders`, `average of`, `highest`, `lowest`, `count of`.
  4. **Conditions & Logic**:
     - `if`, `otherwise if` (elif), `otherwise` (else), `unless <cond>` (if not).
     - Predicates: `is between A and B`, `is one of [A, B, C]`, `starts with`, `ends with`, `contains`, `is a number`, `is text`.
  5. **Loops**:
     - `repeat n times`, `repeat with i from 1 to 10 (by 2)`, `for each item in list where item is over 10`, `while`, `until`, `stop` (break), `skip` (continue).
  6. **Functions & Named Arguments**:
     - `to greet a person with greeting "Hello":`
     - Default parameter values, named argument calls.
     - `give back <expr>`.
     - In-expression calls: `total is the result of tax on price`.
  7. **Real-world Stdlib Helpers**:
     - CSV: `read csv file "data.csv" into rows`, `write csv rows into file "out.csv"`.
     - JSON: `json parse text into obj`, `json stringify obj into text`.
     - Web: `fetch json from url into data`, `fetch text from url into body`.
     - Filesystem & System: `list files in folder`, `environment variable "KEY"`, `run command "cmd" into result`.
     - Math & Dates: `today`, `now`, `3 days ago`, `round x to 2 places`, `square root of x`, `absolute value of x`.
  8. **Python Interop**:
     - `use python module math` -> `import math`.
     - `from python module random use choice` -> `from random import choice`.
     - `use "module.doom"` -> import DoomScript module.

### Phase 3: Learning & Error Experience
- **Goal**: Uncompromising developer experience for human learners.
- **Features**:
  1. **Enhanced Error Formatting**:
     - Intercept all Lark exceptions; format with source line, underline caret `^`, and clear conversational guidance.
     - `difflib`-based suggestion engine ("Did you mean: ...?").
  2. **CLI Enhancements**:
     - `doom explain <file.doom>`: Side-by-side or line-by-line breakdown of DoomScript vs generated Python with plain-English commentary.
     - `doom suggest "<sentence>"`: Instant fuzzy match against phrase tables and grammar recipes.
     - `doom fmt <file.doom>`: Formats source into canonical DoomScript phrasing.
     - `doom new <project_name>`: Scaffolds a clean DoomScript project structure.
  3. **Traceback Mapping**:
     - Map runtime Python exceptions back to `.doom` source line numbers.
  4. **Theatrical Mode**:
     - Flag `--theatrical` enables vintage villain commentary on syntax errors; default is clean and educational.

---

## Deliverables & Acceptance Checklist
- [x] Step 0: Audit completed, conflicts analyzed, `ROADMAP_V2.md` written.
- [ ] Phase 1: `src/doomscript/grammar/phrases.py` normalization engine + comprehensive phrase tests.
- [ ] Phase 2: Full everyday language features, stdlib modules, query operations, and tests.
- [ ] Phase 3: Error experience, CLI commands (`explain`, `suggest`, `fmt`, `new`), traceback mapping.
- [ ] Documentation: Updated `docs/LANGUAGE_REFERENCE.md` and `CHANGELOG.md`.
- [ ] Examples: 6 production scripts (`todo_app.doom`, `csv_report.doom`, `file_organizer.doom`, `api_fetcher.doom`, `grade_calculator.doom`, `text_cleaner.doom`).
- [ ] 100% test pass rate maintained at every step.
