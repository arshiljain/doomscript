# DoomScript Changelog

All notable changes to DoomScript are documented in this file.

## [1.1.0] - 2026-10-19 - Postgraduate & PhD Research Extension
### Added
- **Pure-Standard-Library Scientific Research Engine (`src/doomscript/research/`)**:
  - Zero mandatory runtime dependencies: runs entirely on Python 3.10+ stdlib with optional explicit backend acceleration (`numpy`, `torch`).
  - Strict float64 precision policy and deterministic behavior guarantees.
- **Scientific Reproducibility Contract & 64-bit SplitMix PRNG (`backend.py`)**:
  - `ResearchRNG`: Pure 64-bit SplitMix64 generator instance with 53-bit float precision generation, eliminating cross-library seed divergence.
  - No silent switching: raises `CapabilityError` when backend lacks a primitive rather than secretly defaulting.
  - Deterministic provenance logging (`create_provenance_log`, `verify_provenance`) with cryptographic SHA-256 state hashing and isolated volatile runtime metrics (timestamp, host).
- **Direct Survival Functions & Statistical Distributions (`distributions.py`)**:
  - Accurate incomplete gamma and incomplete beta continued fractions with symmetry switches, providing precision $\le 10^{-10}$ relative tolerance against SciPy.
  - Direct upper-tail survival functions: `t_sf`, `f_sf`, `chi2_sf`, and `normal_sf` eliminating catastrophic $1 - p$ cancellation for near-zero $p$-values.
  - Direct quantile inverse CDFs for normal, Student's $t$, Fisher's $F$, and $\chi^2$ via bracketed bisection.
- **Hypothesis Testing & Bayesian Inference Engine (`stats.py`)**:
  - Parametric tests: Welch's $t$-test (default unequal variances), Student's two-sample $t$-test, paired $t$-test, one-way ANOVA with $\eta^2$ effect size, and two-way factorial ANOVA with interaction effects.
  - Non-parametric tests: Mann-Whitney $U$ with exact combinatorial distribution for small samples ($n \le 20$) and continuity/tie corrections for large samples; Wilcoxon signed-rank test.
  - Categorical analysis: Pearson's $\chi^2$ test of independence and Fisher's exact test ($2 \times 2$ hypergeometric odds ratio).
  - Resampling & Calibration: BCa bootstrap confidence intervals with percentile fallback on zero acceleration; Wilson score intervals with continuity correction for binomial proportions.
  - Multiple testing corrections: Holm-Bonferroni (FWER) and Benjamini-Hochberg (FDR) $p$-value adjustments.
  - MCMC Sampling: Metropolis-Hastings Markov Chain Monte Carlo with adaptive proposal scale tuning frozen post-burn-in, split-$\hat{R}$ (Gelman-Rubin) convergence diagnostics, and effective sample size (ESS).
- **Graph Algorithms & Dynamic Programming (`graph.py`, `algorithms.py`)**:
  - Deterministic tie-breaking by node insertion order for all traversal and graph shortest paths.
  - Dijkstra shortest path with negative weight rejection; Bellman-Ford with negative-cycle detection.
  - Floyd-Warshall all-pairs shortest paths, Kahn's topological sort, Edmonds-Karp maximum flow, min $s\text{-}t$ cut, Kruskal's minimum spanning tree with Union-Find, and $A^*$ heuristic pathfinding.
  - Exact dynamic programming solvers: Levenshtein edit distance, longest common subsequence (LCS with reconstruction), 0/1 knapsack, matrix chain multiplication, longest increasing subsequence, and PageRank with power iteration.
- **Reverse-Mode Scalar Autograd & Optimizers (`autograd.py`, `optim.py`)**:
  - Pure Python scalar computational DAG with dynamic reverse-mode automatic differentiation.
  - Dual-form activations & losses: ReLU, GELU, Sigmoid, Tanh, Binary Cross-Entropy (BCE), Softmax Cross-Entropy with stable log-sum-exp.
  - Relative-error numerical gradient checking ($(\hat{g} - g) / \max(|g|, |\hat{g}|, \epsilon) \le 10^{-4}$) with subgradient tolerance at non-differentiable points.
  - First-order optimizers: SGD, Momentum, Adam, with $L_2$ weight decay regularization and exponential/cosine learning rate schedulers.
  - Pure Python Tensor matrix operations (matmul, 2D sum reductions, transpose).
- **Single Source of Truth Research Phrase Registry (`registry.py`, `phrases.py`)**:
  - `RESEARCH_REGISTRY`: Unified grammar specification generating both statement forms (`test hypothesis that ... into res`) and natural dual-form property expressions (`res's p value`, `p value of res`, `t[0, 0]'s gradient`).
  - Scoped activation behind `use research` block context, guaranteeing zero collisions with general-purpose programming phrases.
- **50-Program Postgraduate Research Benchmark Corpus (`tests/research/corpus/`, `run_research_capability.py`)**:
  - 15 Graph & Discrete Algorithms benchmarks (Dijkstra through PageRank).
  - 15 Statistical Inference benchmarks (Welch's $t$ through Metropolis-Hastings MCMC).
  - 20 Machine Learning & Optimization benchmarks (Autograd chain rule through K-Fold cross validation).
  - 100.0% pass rate achieved across all 50 programs (50/50 passed in 1.79s).

## [1.0.9] - 2026-10-19 - Phase 7: Capability Benchmark & Python Exporter
### Added
- **Python Transpiler & Exporter**:
  - `export_to_python(source)` in `src/doomscript/compiler/engine.py` compiling any DoomScript source to formatted, clean, standalone Python source code via AST unparsing.
  - CLI subcommand `doom export <file.doom> -o <file.py>` (or stdout) with clean banners and header comments.
- **Extended Runtime Math & Statistics Aliases**:
  - `mean`, `median`, `std_dev`, `variance` as top-level runtime functions for scientific computing.
  - Constants `PI`, `E`, `INF` directly exported in `src/doomscript/runtime.py`.
- **40 Undergraduate & Postgraduate CS/Data Science Benchmarks**:
  - 10 CS1 benchmarks (`tests/capability/cs1/`): Bubble sort, Linear search, Binary search, Palindrome check, Word frequency, Matrix transposition, Flatten nested list, Caesar cipher, Vowel counter, Multiplication table.
  - 10 CS2 benchmarks (`tests/capability/cs2/`): Stack with min element, Queue FIFO, Singly linked list, Doubly linked list, Binary search tree, Tree traversals (preorder, inorder), Graph BFS, Graph DFS, Recursive Fibonacci with memoization, Tower of Hanoi.
  - 10 Data Science benchmarks (`tests/capability/datascience/`): CSV load & filter, Missing value imputation, Summary statistics, Group-by aggregation, Column transformation, Outlier filtering, Top-K ranking, Pearson correlation coefficient, Pivot table summary, End-to-end data pipeline.
  - 10 ML & Numerical Math benchmarks (`tests/capability/ml_math/`): Simple linear regression, Mean squared error, Euclidean distance, K-Nearest Neighbors classifier, Min-Max scaler, Standard scaler (z-score), Matrix multiplication, Vector dot product, Cosine similarity, Single-step gradient descent.
- **Capability Benchmark Test Suite & Runner**:
  - `run_capability.py`: automated test harness verifying all 40 benchmark programs compile, execute, assert correctly, and export to valid Python (100.0% pass rate achieved, exceeding the 95.0% target).
  - Pytest regression coverage in `tests/test_phase7_benchmark_export.py`.

## [1.0.8] - 2026-10-19 - Phase 6: Friendly Error Experience
### Added
- **Accurate Syntax Error Line Number Tracking**:
  - `format_syntax_error` now resolves normalized lines through `line_map` from `normalize_with_map()`.
  - Errors in raw files with comments, multi-statement chains (`and then`), or line expansions point to the exact original line and column.
- **Typo Keyword & Verb Suggestions**:
  - Suggestions powered by `difflib` over core keywords and verb synonyms:
    - Misspelled commands like `sya "hello"` -> `Did you mean: say "hello"?`.
    - Keyword aliases like `prnt "hello"` -> `Did you mean: say "hello"?`.
    - Loop headers like `repeta 5 times:` -> `Did you mean: repeat 5 times:`.
  - Prevented silent absorption of command typos by call-statement normalization.
- **Traceback-Aware Variable Typo Suggestions**:
  - Misspelled variable names in runtime exceptions inspect the executing frame's scope and suggest closest matches (`say usre_name` when `user_name` exists -> `Did you mean 'user_name'?`).
- **Beginner-Friendly Translations for Top 10 Python Runtime Exceptions**:
  1. `NameError` -> `I don't know what '<var>' is. Did you mean '<suggestion>'? / Did you set it earlier?`.
  2. `TypeError` (unsupported operands) -> `You tried to <op> a <type1> and a <type2>. These types can't be combined this way.`.
  3. `IndexError` -> Intelligently inspects container length and index when available: `You asked for item <idx>, but this list only has <len> items.`.
  4. `KeyError` -> `This dictionary doesn't have a key called '<key>'.`.
  5. `ZeroDivisionError` -> `Cannot divide by zero. You tried to divide by zero.`.
  6. `FileNotFoundError` -> `I couldn't find the file '<path>'. Check that the name and folder are correct.`.
  7. `AttributeError` -> `A '<type>' doesn't have a '<attr>' property.`.
  8. `ValueError` (unpacking) -> `Tried to unpack <N> values, but got <M>.`.
  9. `RecursionError` -> `This function called itself too many times. Did you forget a base case?`.
  10. `PermissionError` -> `I don't have permission to access '<path>'.`.

## [1.0.7] - 2026-10-19 - Phase 5: Data Science Verbs over pandas
### Added
- **High-Level Tabular Verbs (pandas Backend)**:
  - `load table <path> into <name>` loading CSVs into pandas DataFrames.
  - `save table <name> into <path>` saving tables to clean CSVs (`index=False`).
  - `filter <table> where <col> <op> <val> into <name>` with full comparison operator support (`==`, `!=`, `<`, `<=`, `>`, `>=`, English comparison words).
  - `sort <table> by <col> descending into <name>` and `sort <table> by <col> into <name>`.
  - `group <table> by <col> and average <metric> into <name>` and `group <table> by <col> and sum <metric> into <name>`.
  - `plot <col_y> against <col_x> from <table>` and `plot line <table> with x="...", y="..."` generating matplotlib figures.
- **Transparent Pandas Interop**:
  - Full interoperability between English data science verbs and raw pandas calls (`df.groupby("dept")["salary"].mean()`).
  - Seamless end-to-end data pipelines: load -> filter -> group -> sort -> export.

## [1.0.6] - 2026-10-19 - Phase 4: Comprehensions, Lambdas, Generators, and Math Builtins
### Added
- **List, Dict, and Set Comprehensions**:
  - Python-style list comprehensions: `[x * x for x in range(5)]`, `[x for x in xs if x > 0]`.
  - Python-style dict comprehensions: `{k: v for k, v in pairs}`, `{x: x * x for x in range(4)}`.
  - Python-style set comprehensions: `{x * 2 for x in [1, 2, 2, 3]}`.
  - English comprehensions:
    - `each x * x for x in range(5)`
    - `each x in xs where x > 0`
    - `each x * 2 for x in xs where x % 2 == 0`
- **Anonymous Functions (Lambdas)**:
  - English phrasing: `a function of x giving x + 1`, `a function of a, b giving a + b`.
  - Python-style lambdas: `lambda x: x + 1`, `lambda x, y: x * y`, `lambda: 42`.
  - First-class higher-order function support (e.g. `pairs.sort(key=a function of p giving p[1])`).
- **Generators and Yield**:
  - `yield expr` statement and `(yield expr)` expression support.
  - Generator functions with loop yields (e.g. `to count_up with n:`).
- **Math & Statistics Global Builtins**:
  - `mean(xs)`, `median(xs)`, `std_dev(xs)`, `variance(xs)`.
  - Universal support for `min(xs)`, `max(xs)`, `sum(xs)` across collections.
  - Math constants: `PI`, `E`, `INF`.
- **Coursework Algorithms & Tests**:
  - Sieve of Eratosthenes using set difference and range.
  - QuickSort implementation using recursive list comprehensions.
  - Linear Regression from scratch using `mean`, `sum`, and variance calculations.

## [1.0.5] - 2026-10-19 - Phase 3: Classes — English-First OOP (CS2 Core)
### Added
- **Design Document**:
  - Authored `docs/DESIGN_CLASSES.md` documenting English-first OOP syntax, semantics, and dunder mappings.
- **English-First Class Definitions**:
  - `define a <Name>:` and `define an <Name>:` creating standard Python classes.
  - Inheritance via `define a Dog that is an Animal:`, `that extends`, and `inherits from`.
  - Python-style `class Name:` and `class Name(Base):` supported directly.
- **Constructors & Special Methods**:
  - `to start with <params>:` and `to start:` translating to `__init__`.
  - `to describe:` translating to `__repr__` and automatic fallback `__str__`.
  - `to get length:` translating to `__len__`.
  - `to get item with <index>:` translating to `__getitem__`.
  - `to set item with <index>, <val>:` translating to `__setitem__`.
  - `base start with <args>` and `base start` calling `super().__init__(...)`.
- **Instance Field Shorthand**:
  - `my <field>` and `its <field>` automatically resolved to `self.<field>` with full load/store context support.
  - Automatic `self` parameter injection for class methods.
- **CS2 Data Structure Acceptance Tests**:
  - Singly Linked List with `Node` pointers and traversal.
  - Stack with `push`, `pop`, `peek`, and `is_empty`.
  - Queue (FIFO) with `enqueue`, `dequeue`, and `is_empty`.
  - Binary Search Tree with recursive `insert` and `inorder` traversal.

## [1.0.4] - 2026-10-19 - Phase 2: Indexing, Slicing, Tuples, and Essential Operators (CS1 Core)
### Added
- **Subscripting & Slicing**:
  - Python-standard 0-based subscripts: `xs[0]`, `m[1][0]`, `d["key"]`, negative indices `xs[-1]`.
  - Full slicing syntax: `xs[1:4]`, `xs[:3]`, `xs[3:]`, `xs[::2]`, `xs[1:5:2]`, `xs[:-1]`.
  - Subscript assignments and augmented assignments: `xs[i] = v`, `freq[w] += 1`, `grid[r][c] = total`.
- **English Coexistence**:
  - `set item 2 of xs to 99` (1-based natural English) seamlessly coexists with `xs[1] = 99` (0-based).
  - List mutation functions `pop(st)`, supporting statement forms `pop st`, `pop from st`, `remove last from st`, and expression forms `val = pop st`, `say pop st`.
- **Tuples & Multi-Assignment**:
  - Tuple packing, unpacking, and variable swap: `a, b = b, a`, `t = (1, 2)`, `t = ()`, `t = (5,)`.
  - Multi-target loops: `for i, f in enumerate(fruits):` and `for each i, f in enumerate(fruits):`.
- **Sets & Dictionaries**:
  - Set literals `{1, 2, 3}` alongside dictionary literals `{"a": 1, "b": 2}` and `{a: 1}`.
  - Set / bitwise operators: union `a | b`, intersection `a & b`, difference `a - b`, symmetric difference `a ^ b`.
- **Symbol Operators**:
  - Floor division `//` and augmented `//=` (e.g. `mid = (lo + hi) // 2`).
  - Modulo `%` and augmented `%=` (e.g. `7 % 2`), coexisting with `mod` and `remainder of`.
  - Exponentiation `**` (e.g. `2 ** 3`), coexisting with `to the power of`.
  - Python-style `not in` and `in` comparisons (e.g. `if w not in freq:`).
- **CS1 Algorithm Acceptance Tests**:
  - Bubble sort with `a, b = b, a` swap.
  - Word-frequency counter using a dict (`freq[w] += 1`).
  - Binary search with `mid = (lo + hi) // 2`.
  - 2D matrix multiply with nested lists `A[i][k] * B[k][j]`.

## [1.0.3] - 2026-10-19 - Phase 1: Dotted Calls & Full Python Interop
### Added
- **Dotted Calls & Attribute Access**:
  - Dotted attribute access (`obj.attr`), method calls (`obj.method(args)`), chained method calls (`s.lower().split(" ")`), and calls on call results (`f()(x)`).
  - Subscript method chaining (`df["y"].mean()`).
  - Method calls with keyword arguments (`s.split(",", maxsplit=1)`).
- **Python Module Import Aliasing & Dotted Paths**:
  - Support for aliased imports: `use python module numpy as np`, `use python module matplotlib.pyplot as plt`.
  - Support for dotted from-imports: `from python module sklearn.linear_model use LinearRegression`.
- **Packaging Extras**:
  - Added `data` optional dependency group to `pyproject.toml` (`pip install doomscript[data]`) for `numpy`, `pandas`, `matplotlib`, and `scikit-learn`.
- **Test Suite**:
  - Added comprehensive test suite `tests/test_phase1_interop.py` covering standard library calls, chained methods, numpy, pandas, matplotlib, and scikit-learn.

### Fixed
- **Dot Rewriting Mangle**:
  - Removed normalizer rewrite that forcibly converted dots into possessives (`random.seed(1)` -> `random's seed(1)`). Dots with no whitespace now represent standard attribute access.
- **Keyword Variable Access**:
  - Fixed dotted access on variables named after keywords (e.g. `first = {revenue: 3}; first.revenue`).
- **Callable Identifier Disambiguation**:
  - Fixed function definitions and calls named `square` (`square(5)`) by normalizing `square root of` to `sqrt of` in the phrase pipeline, releasing `square` from being a reserved grammar terminal.

## [1.0.2] - 2026-10-19 - Phase 0: Safety & Spec Integrity
### Added
- **MIT License & Packaging Metadata**:
  - Added project root `LICENSE` (MIT).
  - Populated `authors`, `license = { text = "MIT" }`, and `[project.urls]` in `pyproject.toml`.
- **Conformance & Safety Test Suites**:
  - `tests/test_safety_and_integrity.py`: Validates playground 127.0.0.1 binding and subprocess shell isolation.
  - `tests/test_core_spec_conformance.py`: Validates that all 30 guaranteed Core Spec forms (fenced blocks and inline examples) parse and execute without error.

### Security
- **Subprocess Shell Injection Defense**:
  - `subprocess.run` in `runtime.py` and `runtime_extended.py` now defaults to `shell=False`.
  - String commands are safely parsed using platform-aware `shlex.split`, stripping outer quotes on Windows while preserving path backslashes and ensuring shell metacharacters cannot trigger command injection.
  - Shell execution is strictly opt-in via explicit `run command ... using shell` syntax.
- **Playground Localhost Binding**:
  - `launch_playground` in `src/doomscript/playground.py` now explicitly binds to `("127.0.0.1", port)` by default, preventing unintended network exposure on all interfaces.

### Fixed
- **Core Spec Form #20 Deduplication Statement**:
  - Added phrase normalization for `unique items of <list> into <target>` (`clean_ids = unique_items(raw_ids)`).
- **Python 3.14 AST Constant Safety**:
  - Coerced `True`, `False`, and `None` identifiers to `ast.Constant` in `DoomToPython.var()` to prevent AST compiler errors on modern Python versions.
- **Core Spec Example Executability**:
  - Updated Form #30 in `docs/CORE_SPEC.md` with an executable division operation inside `try:` to ensure reproducible execution.

## [1.0.1] - 2026-10-18 - Critical Bug Fixes
### Fixed
- **Compound Interest Rate Normalization & Compounding Frequency**:
  - Fixed percent rates like `5%` causing astronomical results (`1.4e21`). Rates are now normalized automatically whether specified as `5%`, `0.05`, or `5`.
  - Default compounding frequency is now documented and mathematically standard annual compounding ($n=1$, $1000 \times 1.05^{10} = 1628.89$).
  - Added full support for custom compounding frequencies: `compounded monthly` ($n=12$), `compounded quarterly` ($n=4$), `compounded semi-annually` ($n=2$), and `compounded daily` ($n=365$).
- **Semantic Knowledge Index & Embedding Relevance**:
  - Replaced naive whole-string SHA-256 hash embeddings with deterministic token-level feature hashing (unigram + bigram hashing trick) and BM25 / TF-IDF term scoring.
  - Queries like `"my cat purrs"` now reliably rank relevant documents first rather than producing pseudo-random avalanche results.
  - Added support for natural synonyms: `add document ... with text ... to ...` alongside `index document ... text ... into ...`.
- **C Foreign Function Interface (FFI) Argument Unpacking & Cross-Platform Libc**:
  - Fixed `call_c_function` crashing on list arguments like `with args [-5]`. Single list/tuple arguments are now automatically unpacked and converted for the C ABI.
  - Added transparent cross-platform standard C library resolution (`libc.so.6`, `libc`, `c` mapping to `msvcrt` on Windows and dynamic `find_library` on Linux/macOS).
  - Calling `call c library "libc.so.6" function "abs" with args [-5]` now returns `5` across all platforms.
- **Piped Stdin & Graceful EOF Handling in `ask`**:
  - Replaced raw Python `input()` call in `ask_input`, `ask_number`, `ask_boolean`, and `ask_choice` with pipe-aware stream reading.
  - Automatically suppresses prompt output during piped stdin redirection (`echo Bob | doom run script.doom`), reads lines directly from stdin, and safely returns empty string `""` on EOF instead of raising uncaught `EOFError`.
  - Prevented infinite loops on EOF in `ask_choice`.

## [1.0.0] - 2026-10-18 - Phases 26-100: Complete Language Milestone (10 Thematic Clusters)
### Added
- **Cluster 1 (Phases 26–32: Systems, OS, Processes & Signals)**:
  - `run command <cmd> piped into <var>`: Subprocess execution capturing stdout, stderr, and exit codes into a Record.
  - `check if process <name> is running into <var>`: Pure-stdlib process existence check.
  - `get system disk space into <var>`: Disk capacity, usage, and free metrics in gigabytes.
  - `add directory <dir> to system path`: Dynamic PATH modification and sys.path injection.
  - `acquire file lock <path> into <var>` and `release file lock <var>`: Cooperative cross-process file locking.
- **Cluster 2 (Phases 33–40: Network Protocols, DNS & Cookies)**:
  - `resolve dns of <host> into <var>`: Zero-dependency DNS resolution.
  - `ping host <host> into <var>`: Network reachability and latency benchmarking.
  - `create cookie jar into <var>`, `set cookie <key> to <val> in <jar>`, `get cookie <key> from <jar> into <var>`.
- **Cluster 3 (Phases 41–48: Advanced Data Engineering, Compression & Geolocation)**:
  - `compress text <txt> with gzip into <var>` / `decompress gzip <bytes> into <var>`.
  - `compress text <txt> with bz2 into <var>` / `decompress bz2 <bytes> into <var>`.
  - `create zip archive <dest> from files <list>` and `extract zip archive <src> into folder <dest>`.
  - `calculate crc32 of <txt> into <var>` and `calculate adler32 of <txt> into <var>`.
  - `calculate geo distance between <lat1>, <lon1> and <lat2>, <lon2> into <var>`: Great-circle Haversine distance in kilometers.
- **Cluster 4 (Phases 49–56: Mathematics, Linear Algebra, Statistics & Finance)**:
  - `vector <v1> dot vector <v2> into <var>`: Vector dot products.
  - `vector magnitude of <v> into <var>`: Euclidean vector norm.
  - `matrix <m1> multiply matrix <m2> into <var>`: Pure Python matrix multiplication.
  - `standard deviation of <list>`, `variance of <list>`, and `median of <list>`.
  - `compound interest on <p> at <r>% for <t> years into <var>`: Future value compounding.
  - `loan payment for principal <p> rate <r>% months <m> into <var>`: Monthly amortization payments.
- **Cluster 5 (Phases 57–64: Reactive EventBus, Priority Queues & Resiliency)**:
  - `create event bus into <var>`, `event_subscribe(<topic>, <handler>)`, `publish event <topic> with data <data>`.
  - `create priority queue into <var>`, `enqueue task <item> with priority <p> into <q>`, `dequeue next task from <q> into <var>`.
  - `create circuit breaker named <name> into <var>`, `call circuit breaker <cb> with <fn> into <var>`: Fault-tolerant CLOSED/HALF-OPEN/OPEN state machine.
- **Cluster 6 (Phases 65–72: Modern Web, UI & Components, SVG Canvas)**:
  - `create svg circle at <cx>, <cy> radius <r> fill <fill> into <var>`.
  - `create svg rect at <x>, <y> width <w> height <h> fill <fill> into <var>`.
  - `create svg canvas width <w> height <h> with elements <list> into <var>`.
  - `diff records <r1> and <r2> into <var>`: Structural object difference engine reporting added, removed, and changed attributes.
- **Cluster 7 (Phases 73–80: AI Agents, RAG & Cognitive Loops)**:
  - `create knowledge index into <var>`: In-memory vector database.
  - `index document <doc_id> text <txt> into <idx>`: Document indexing with deterministic semantic embeddings.
  - `search knowledge index <idx> for <q> into <var>`: Cosine similarity vector search and retrieval.
  - `cosine similarity of <v1> and <v2> into <var>`.
  - `create conversation memory into <var>`, `remember in memory <mem> role <role> content <content>`, `get recall history from <mem> into <var>`.
- **Cluster 8 (Phases 81–88: Security, Identity, Auth & Compliance)**:
  - `create jwt with payload <data> and secret <secret> into <var>`: Zero-dependency HMAC-SHA256 JWT generator.
  - `verify jwt <token> with secret <secret> into <var>`: Signature and claims validation.
  - `secure hash password <pwd> into <var>` and `verify password <pwd> matches <hash> into <var>`: Salted PBKDF2-HMAC-SHA256 password security.
  - `mask pii in text <txt> into <var>`: Redaction engine masking emails, phone numbers, and SSNs.
- **Cluster 9 (Phases 89–95: Cloud, Containers & Prometheus Metrics)**:
  - `generate dockerfile for entrypoint <entry> into <var>`: Production container configuration generator.
  - `increment metric <name>`, `set metric <name> to <val>`, `export prometheus metrics into <var>`: Prometheus scrape exporter.
- **Cluster 10 (Phases 96–100: Metaprogramming, FFI & Self-Hosting)**:
  - `call c library <lib> function <fn> with args <args> into <var>`: Foreign Function Interface via ctypes.
  - `minify doomscript <src> into <var>`: AST comment stripper and whitespace compressor.

## [0.8.0] - 2026-10-18 - Phases 14-25: AI Primitives, ORM, DocGen, Markdown, Cryptography, Streaming, Config, Benchmarking & Packager
### Added
- **Phase 14: English AI & LLM Primitives**:
  - `ask ai <prompt> into <var>`: Plain-English AI query using standard library HTTP with support for Gemini, OpenAI, Ollama, and offline simulation fallback.
  - `ask ai <prompt> as json into <var>`: Structured JSON decoding directly into a DoomScript Record.
  - `ask ai <prompt> with model <name> into <var>`: Explicit model selection.
- **Phase 15: Declarative English Database ORM & Migrations**:
  - `define entity <Name> with <fields>`: In-memory & SQLite-backed relational schema definitions.
  - `save new <Entity> with <fields> into <var>`: Auto-increment primary key generation and record persistence.
  - `find all <Entities> into <var>` and `find first <Entity> into <var>`.
- **Phase 16: Automated Documentation Generator (`doom doc`)**:
  - Static HTML documentation generation inspecting functions, entities, CLI flags, routes, and comments across all `.doom` files.
- **Phase 17: English Markdown & Rich Document Generator**:
  - Code-based document construction: `create markdown document`, `add heading`, `add paragraph`, `add table`, `add bullet list`.
  - Output formats: `render document as markdown`, `render document as html`, and `save document to file`.
- **Phase 18: File Watching & Live Reload Daemon (`doom watch`)**:
  - `doom watch <path> [--action run|test]`: Pure stdlib modification monitoring that automatically recompiles and runs upon file save.
- **Phase 19: English Cron & Event Scheduling**:
  - `schedule every <N> seconds <function>` and `run scheduler for <N> seconds`.
- **Phase 20: Secure English Cryptography & Secrets**:
  - `hash text <txt> with algorithm "sha256"|"md5"|"sha512" into <var>`.
  - `generate secure token of length <N> into <var>`.
  - `encode text as base64` / `decode base64`.
  - `encrypt text <txt> with secret <key>` and `decrypt text <cipher> with secret <key>`.
- **Phase 21: Streaming Data & Pipeline Operators**:
  - `pipe <val> into <fn1>, <fn2> into <var>`: Function composition pipelines.
  - `take first <N> items from <list>` and `drop first <N> items from <list>`.
  - `batch <list> by <N> into <var>`: Chunked array splitting.
- **Phase 22: Binary & Hex Data Serialization**:
  - `convert number <n> to hex` and `convert hex <h> to number`.
  - `pack numbers <list> as <format>` and `unpack binary <format> from buffer <buf>`.
  - `size of buffer <buf> in bytes into <var>`.
- **Phase 23: English Configuration Manager**:
  - Unified configuration loader supporting `.ini`, `.json`, and environment variables.
  - `load config from <file>`, `get config <key> [with default <val>]`, `set config <key> to <val>`, `save config to file`.
- **Phase 24: Visual Benchmark & Latency Profiler (`doom bench`)**:
  - Language level: `benchmark <name> with <N> iterations for <fn> into <var>`.
  - CLI command: `doom bench <file.doom> [--iterations N]`: Reports min/max/avg latency, throughput (runs/sec), and peak memory consumption.
- **Phase 25: Standalone Packager (`doom pack`)**:
  - `doom pack <file.doom> [--output app.pyz]`: Bundles a DoomScript script and runtime into a single portable zipapp executable anywhere with Python 3.10+ without installing DoomScript.
- **Automated Test Coverage**:
  - Added `tests/test_phase14_to_25.py` (12 comprehensive tests). Total test suite expanded to 105 tests, 100% passing.

## [0.7.0] - 2026-10-18 - Phases 9-13: Pattern Matching, Testing, CLI Builder, Concurrency & Declarative Web
### Added
- **Phase 9: English Pattern Matching & Destructuring**:
  - Multi-branch pattern matching: `match <expr>:` with `when <literal>`, `when <type>`, `when over/under/at least/at most/between`, `when a or b`, and `otherwise:`.
  - Type-guarded numeric matching to ensure safe evaluation across mixed data types without runtime TypeErrors.
  - Tuple, list, and dictionary destructuring: `unpack a, b, c from data`.
  - Head/tail list decomposition: `first item into head, remaining items into tail from list`.
- **Phase 10: Native English Test Runner**:
  - Test suite declaration: `test "name":` blocks.
  - Fluent English expectations: `expect a + b to equal c`, `expect val to be a number|text|boolean|list|record`, `expect val to be greater than|at least|less than|at most`, and `expect collection to contain item`.
  - Standalone CLI command: `doom test [path]` with discovery of `test_*.doom` or files in `tests/`, formatted ANSI checkmarks/crosses, and execution duration reporting.
- **Phase 11: Declarative CLI App Builder**:
  - Declarative program definition: `program description "..."`.
  - Command-line option definition: `option name [as type] with default <val> and description "..."`.
  - Boolean flag definition: `flag name with description "..."`.
  - Automatic parsing into structured records: `parse arguments into cli_args` with automatic `--help` flag handling.
- **Phase 12: Background Concurrency & Timers**:
  - ThreadPool worker dispatch: `run in background fn(args) into task`.
  - Single and multi-task synchronization: `wait for task into res` and `wait for all [tasks] into results`.
  - Execution timeouts: `timeout N seconds for fn(args) into result` returning None upon timeout.
- **Phase 13: Declarative Web Microservices**:
  - English HTTP route handlers: `on get|post|put|delete "/path":` with `reply with json ...` and `reply with "..."`.
  - Pure Python stdlib HTTP microservice server: `serve on port <port>`.
  - Multi-route deferred registration ensuring reliable routing execution.
- **Complete Test Coverage**:
  - Added `tests/test_phase9_to_13_advanced.py`. Total test suite expanded to 93 unit tests, 100% passing.

## [0.6.0] - 2026-10-18 - Phases 4-8: Automation, LSP, REPL/Kernel, Package Management & English Type Contracts
### Added
- **Phase 4: Automation & Data Stdlib**:
  - Relational joins without SQL: `combine table_a and table_b on "key" with style "inner|left|right|outer" into target`.
  - HTML scraping: `extract text from html html_str into text_var`, `extract links from html html_str into links_var`.
  - HTTP requests & downloads: `fetch url ... into ...`, `post json ... to ... into ...`, `download ... to file ...`.
  - Email sending: `send email to "..." with subject "..." and body "..."`.
  - Timezones & business days: `now in "UTC"`, `next business day from "..."`, `today is weekend`.
  - Multi-line triple-quoted string literals (`"""` and `'''`) in grammar and compiler.
- **Phase 5: Language Server Protocol (LSP)**:
  - Pure Python stdlib JSON-RPC Language Server (`src/doomscript/lsp/server.py`).
  - Diagnostic reporting, keyword/identifier hovers, English completions, and function definition navigation.
  - CLI command: `doom lsp` for integration with VS Code, PyCharm, and other editors.
- **Phase 6: Multi-line REPL & Interactive Kernel**:
  - Multi-line block buffering (`... ` prompt) for loops, conditions, and functions in `doom repl`.
  - Interactive cell execution and Jupyter kernel specification generator (`src/doomscript/kernel.py`).
  - CLI command: `doom kernel install` for native Jupyter notebook integration.
- **Phase 7: Package Management & Project Manifest**:
  - `doom.toml` project manifest engine (`src/doomscript/package.py`).
  - CLI commands: `doom init`, `doom add <package> [--dev]`, and `doom install`.
- **Phase 8: English Type Contracts & Gradual Safety**:
  - Full type comparisons: `is a number`, `is text`, `is a boolean`, `is a list`, `is a record`, plus negative forms (`is not text`, `is not a number`, etc.).
  - Preconditions and postconditions: `require <cond> [otherwise <msg>]` and `ensure <cond> [otherwise <msg>]`.
  - Typed function parameter signatures: `to func with arg1 as number, arg2 as text:` desugaring to leading body type assertions.
  - Typed variable assignments: `set score as number to 100`.
  - Static contract analyzer (`src/doomscript/contracts.py`).
  - CLI flag: `doom check --strict` to verify literal contracts and constant argument types statically at check time.
  - Complete test coverage across 86 unit tests, 100% passing.

## [0.5.0] - Phase 3: Learning & Error Experience
### Added
- **Human-Centric Error Experience (`src/doomscript/errors.py`)**:
  - Eliminated raw Lark error messages from user output.
  - Every syntax error displays: source file, line number, column, caret `^` pointing directly under the error token, and a clear plain-English explanation.
  - `difflib`-powered "Did you mean: <closest valid sentence>?" engine comparing user input against canonical sentence templates.
  - Optional `--theatrical` villain mode for humorous, retro compiler feedback while defaulting to polite, clear English.
- **Code Explainer Engine (`src/doomscript/explainer.py` & `doom explain`)**:
  - `doom explain <file.doom>` prints a side-by-side rich table displaying the original DoomScript line, its transpiled Python AST equivalent, and a plain-English explanation of its runtime behavior.
- **Interactive Phrasing Suggester (`doom suggest`)**:
  - `doom suggest "<sentence>"` validates sentences and suggests the closest 3 canonical alternatives if syntax is unrecognized.
- **Canonical Code Formatter (`src/doomscript/formatter.py` & `doom fmt`)**:
  - `doom fmt <file.doom> [--write]` normalizes code to standard 4-space indentation, canonical verbs, standardized comparisons, and stripped filler words.
- **Starter Project Generator (`doom new`)**:
  - `doom new <project_name>` scaffolds an automation project with `main.doom`, `README.md`, and sample CSV data.
- **Runtime Traceback Line Mapping**:
  - Runtime errors in `doom run` now locate the active frame and print the corresponding `.doom` source line with caret indicator.
- **VS Code Extension Upgrade (`extensions/doomscript-vscode/`)**:
  - Upgraded to v0.4.0 with expanded keyword highlighting, rich code snippets for all constructs, and `doom check` problem matcher diagnostics.
- **Complete Test Coverage**:
  - Added `tests/test_phase3_experience.py` (8 tests). Test suite expanded to 65 tests, 100% passing.

## [0.4.0] - Phase 2: Everyday Programming in English
### Added
- **Everyday I/O & String Interpolation**:
  - `say` with multiple comma-separated expressions (e.g. `say "Player:", name, "Level:", level`).
  - Native string interpolation with `{variable}`, `{record.field}`, and `{record's field}` compiling directly to Python AST `JoinedStr`.
  - Type-safe user input: `ask number "Age?" into age`, `ask boolean "Proceed?" into confirmed`.
- **List & Record Manipulation**:
  - Natural list constructors: `a list of 1, 2, 3`, `an empty list`, `[]`.
  - List indexing and slicing: `item 2 of list` (1-based English indexing), `first 3 items of list`, `last 3 items of list`.
  - In-place mutation: `insert x at 1 in list`, `add x to list`, `remove x from list`.
  - Non-destructive list transformations: `sorted list`, `reversed list`, `unique items of list`.
  - Collection predicates: `list is empty`, `list is not empty`, `list contains x`.
- **English Data Operations & Queries**:
  - Comprehensions: `names is the name of each person in people`.
  - Record filtering: `people where age is over 18 into adults` and `adults = people where age is over 18`.
  - Grouping: `group orders by customer into customer_orders` (yields grouped dictionary of lists).
  - Record sorting: `sort orders by amount descending` and `sort orders by amount`.
  - Field aggregates: `total of price in orders`, `average of price in orders`, `highest price in orders`, `lowest price in orders`.
- **Extended Conditions & Control Flow**:
  - Range conditions: `val is between 10 and 20` (inclusive chaining).
  - Membership conditions: `val is one of options`.
  - Type checking: `val is a number`, `val is text`.
  - Control flow: `otherwise if` (`elif`), `otherwise` (`else`), postfix and block `unless <cond>`.
  - Loops: `repeat with i from 1 to 10 by 2`, `for each item in items where item is over 5`, `while <cond>`, `until <cond>`.
  - Loop controls: `stop` (`break`), `skip` (`continue`).
- **Functions with Defaults & Expressions**:
  - Default arguments: `to greet person with greeting "Hello":`.
  - Keyword arguments and function calls in expressions: `result of tax on price`.
  - Natural phrasing: `to tax on price` -> `to tax with price`.
- **Error Handling**:
  - `try ... if that fails [as problem] ... always ...` desugaring to Python `try/except/finally`.
- **Pure Standard Library Runtime Helpers**:
  - CSV files: `read csv file "..." into rows`, `write csv rows into file "..."`, `append csv row to file "..."`.
  - JSON serialization: `parse json text into obj`, `convert obj to json into text`.
  - Date & Time: `today`, `now` / `current time`.
  - Math & System: `round x to 2 places into y`, `absolute value of x`, `square root of x`, `environment variable "NAME" into val`, `run command "..." into output`.
  - Python interop: `use python module math`, `from python module math use ceil, floor`, dot notation `math.pi` / `math's pi`.
  - DoomScript module interop: `use "helpers.doom"`.
- **Test Suite**:
  - Added `tests/test_phase2_everyday.py` with 14 comprehensive tests covering all Phase 2 features. 100% of all 57 tests passing.

## [0.3.0] - Phase 1: Normalization & Phrase Layer
### Added
- **Data-Driven Phrase Layer (`src/doomscript/grammar/phrases.py`)**:
  - Implemented pre-parser preprocessing pipeline driven entirely by data tables.
  - Adding new synonyms or fillers no longer requires editing grammar or CST/AST transformers.
- **Filler Word Stripping**:
  - Polite prefixes: `please`, `kindly` (e.g., `please add 5 to the list`).
  - Adverbs & fillers: `just`, `simply`, `then`.
  - Articles: `the` before nouns/identifiers without affecting strings or variable names.
- **Synonym Tables**:
  - Output verbs: `show`, `print`, `tell`, `display` (non-colored) canonicalize to `say`.
  - Return verbs: `give back`, `hand back`, `yield back` canonicalize to `return`.
  - Comparisons: `is bigger than`, `is more than`, `exceeds`, `is higher than` -> `is greater than` (`>`); `is no less than`, `is greater than or equal to` -> `is at least` (`>=`); `is smaller than`, `is lower than` -> `is less than` (`<`); `is no more than`, `is less than or equal to` -> `is at most` (`<=`); `is equal to`, `is the same as` -> `equals` (`==`); `is different from`, `is not equal to` -> `is not` (`!=`).
- **Flexible Assignment**:
  - `x is 5`, `x = 5`, `set x to 5`, `let x be 5`, `make x 5`, `make x be 5`, `put 5 into x`.
  - `call it <target>` / `call that <target>`: Aliases the last evaluated/assigned value to a new identifier.
- **Pronoun Tracking (`it` / `that`)**:
  - Lexical scope tracking of the most recently assigned variable name.
  - Resolves pronouns in sequential statements (e.g. `total = 100 \n increase it by 25`).
  - Strict scope safety: Raises descriptive `DoomScopeError` if pronoun is referenced before any variable is assigned.
  - Context preservation: Protects grammar keywords like `verify that` and `if (it|that) fails` from accidental pronoun replacement.
- **Sentence Endings & Statement Chaining**:
  - Statements can end in period `.` (e.g., `set x to 10.`).
  - Multiple statements on a single line separated by `.` or `and then` are cleanly split while preserving block indentation.
- **Articles & Possessives**:
  - Normalized `the length of x`, `length of x`, `x's length`, and `x's count` into `count of x`.
- **Protected String Literals**:
  - String contents are masked during preprocessing and unmasked faithfully so text contents are never altered.
- **Test Suite**:
  - Added `tests/test_phrases.py` with 12 comprehensive tests. Total test count increased to 43 passing tests.
