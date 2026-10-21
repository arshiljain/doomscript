# DoomScript (`.doom`): The English-First Programming Language for Mortals

> **"Code the way you think in English. Run at the speed of compiled Python."**

**DoomScript** is a revolutionary, general-purpose programming language designed to eliminate the artificial cognitive friction between human thought and executable software. Instead of forcing humans to think in esoteric punctuation, compiler arcana, zero-indexing offsets, or cryptic boilerplate, DoomScript empowers you to express sophisticated business logic, data science pipelines, AI agent workflows, and systems engineering in natural, grammatically resilient English.

Under the hood, DoomScript is **not** a slow interpreter or an ambiguous LLM-based wrapper. It is a **deterministic, blazing-fast compiled language** with a formal LALR(1) grammar, AST normalization pipeline, and a high-throughput compilation engine. DoomScript compiles deterministically into standard **Python Abstract Syntax Trees (AST)** and zero-dependency standalone native binaries (`.exe` / ELF).

---

## 📑 Complete Table of Contents

1. [The Pitch: Why DoomScript?](#1-the-pitch-why-doomscript)
   - [The Problem with Modern Programming Languages](#the-problem-with-modern-programming-languages)
   - [The 7 Pillars of DoomScript](#the-7-pillars-of-doomscript)
   - [Side-by-Side Comparison: Python vs DoomScript](#side-by-side-comparison-python-vs-doomscript)
   - [Feature Comparison Matrix (DoomScript vs Python vs SQL vs Excel)](#feature-comparison-matrix)
2. [Quickstart & The `doom` Toolchain](#2-quickstart--the-doom-toolchain)
   - [Installation & Zero-Configuration Setup](#installation--zero-configuration-setup)
   - [The Unified CLI (`run`, `export`, `build`, `test`, `repl`, `lsp`, `suggest`, `check`, `fmt`)](#the-unified-cli)
   - [IDE Integration & Language Server Protocol](#ide-integration--language-server-protocol)
3. [Language Fundamentals & Thought-to-Code Architecture](#3-language-fundamentals--thought-to-code-architecture)
   - [3.1 Printing & User Interaction (`say`, `show`, `ask`, `ask number`, `ask boolean`)](#31-printing--user-interaction)
   - [3.2 Variables & Flexible Assignments (`set to`, `put into`, `let be`, `increase by`, `decrease by`)](#32-variables--flexible-assignments)
   - [3.3 Natural 1-Based Indexing & Collection Slicing (`first item`, `last item`, `item 2 of`, out-of-bounds safety)](#33-natural-1-based-indexing--collection-slicing)
   - [3.4 Conversational Inquiries & Math (`what is the total amount in orders`, `what's 5 * 5 into x`)](#34-conversational-inquiries--math)
   - [3.5 Natural Pronoun Resolution (`it`, `that`, `them`, `this`)](#35-natural-pronoun-resolution)
   - [3.6 Possessive Syntax & Deep Navigations (`user's name`, `orders's length`)](#36-possessive-syntax--deep-navigations)
   - [3.7 Relational Reshaping (`partition into`, `flatten`, `pair with into dictionary`)](#37-relational-reshaping)
   - [3.8 Universal & Existential Quantifiers (`every x in list is`, `any x in list is`, `no x in list is`, `all items are`)](#38-universal--existential-quantifiers)
   - [3.9 Contextual Query Pipelines & Relative Clauses (`keep only where`, `discard from where`, `whose role is`)](#39-contextual-query-pipelines--relative-clauses)
   - [3.10 Superlative Queries (`find largest by amount into top`, `find cheapest by price into best`)](#310-superlative-queries)
   - [3.11 Adverbial Qualifiers & System Resilience (`retrying 3 times with backoff`, `timed out after`, `cached for`)](#311-adverbial-qualifiers--system-resilience)
   - [3.12 Compound Sentences & Natural Conjunctions (`set x to 5, then say x`, `then if`, `and then unless`)](#312-compound-sentences--natural-conjunctions)
   - [3.13 Functions, Scopes & Scoped Globals (`to calculate with x:`, `global counter`, `modify global`)](#313-functions-scopes--scoped-globals)
   - [3.14 Story-Driven Relational Entities (Declarative classes, `begins with`, order-independent relations, event hooks)](#314-story-driven-relational-entities)
   - [3.15 Empathetic Error Diagnostics & Guardrails (Runtime vs Syntax labels, keyword collision guidance, `--theatrical`)](#315-empathetic-error-diagnostics--guardrails)
   - [3.16 Sub-5ms Compilation Engine (Lark LALR cache, high-capacity regex caching)](#316-sub-5ms-compilation-engine)
4. [Standard Built-in Capabilities](#4-standard-built-in-capabilities)
   - [File I/O & Document Processing](#file-io--document-processing)
   - [CSV & Tabular Intelligence](#csv--tabular-intelligence)
   - [JSON Serialization & Configuration](#json-serialization--configuration)
   - [System, Subprocess & Environment Primitives](#system-subprocess--environment-primitives)
   - [Sound Synthesis & 2D Immediate Canvas](#sound-synthesis--2d-immediate-canvas)
5. [The 41 Specialized Domain Packs (`use <domain>`)](#5-the-41-specialized-domain-packs)
   - [1. DSA & Algorithms (`use dsa`)](#1-dsa--algorithms-use-dsa)
   - [2. Data Engineering & Pipelines (`use data`)](#2-data-engineering--pipelines-use-data)
   - [3. Machine Learning & Predictive Modeling (`use ml`)](#3-machine-learning--predictive-modeling-use-ml)
   - [4. Quantitative Finance & Portfolio Analytics (`use finance`)](#4-quantitative-finance--portfolio-analytics-use-finance)
   - [5. NLP & Text Intelligence (`use nlp`)](#5-nlp--text-intelligence-use-nlp)
   - [6. Graph Theory & Network Science (`use graph`)](#6-graph-theory--network-science-use-graph)
   - [7. Computer Vision & Media Intelligence (`use image`)](#7-computer-vision--media-intelligence-use-image)
   - [8. Web Scraping & DOM Extraction (`use web`)](#8-web-scraping--dom-extraction-use-web)
   - [9. Audio Synthesis & DSP (`use audio`)](#9-audio-synthesis--dsp-use-audio)
   - [10. Relational Databases & SQL Engine (`use db`)](#10-relational-databases--sql-engine-use-db)
   - [11. Networking & Network Protocols (`use net`)](#11-networking--network-protocols-use-net)
   - [12. Stochastic Simulation & Monte Carlo (`use sim`)](#12-stochastic-simulation--monte-carlo-use-sim)
   - [13. Geospatial Analytics & GIS (`use geo`)](#13-geospatial-analytics--gis-use-geo)
   - [14. Operations Research & Optimization (`use opt`)](#14-operations-research--optimization-use-opt)
   - [15. Autonomous AI Agents & Multi-Agent Swarms (`use agent`)](#15-autonomous-ai-agents--multi-agent-swarms-use-agent)
   - [16. Cloud Infrastructure & Object Storage (`use cloud`)](#16-cloud-infrastructure--object-storage-use-cloud)
   - [17. Office Documents & PDF Automation (`use office`)](#17-office-documents--pdf-automation-use-office)
   - [18. Scientific Computing & Research (`use research`)](#18-scientific-computing--research-use-research)
   - [19. Bioinformatics & Genomics (`use bio`)](#19-bioinformatics--genomics-use-bio)
   - [20. Classical & Orbital Physics Simulation (`use physics`)](#20-classical--orbital-physics-simulation-use-physics)
   - [21. Cybersecurity & Applied Cryptography (`use sec`)](#21-cybersecurity--applied-cryptography-use-sec)
   - [22. Game Systems & Interactive 2D/3D Engines (`use game`)](#22-game-systems--interactive-2d3d-engines-use-game)
   - [23. Quantum Computing & Statevector Simulation (`use quantum`)](#23-quantum-computing--statevector-simulation-use-quantum)
   - [24. Electrical Engineering & Circuit Modeling (`use circuit`)](#24-electrical-engineering--circuit-modeling-use-circuit)
   - [25. Cryptographic Blockchains & Merkle Ledgers (`use chain`)](#25-cryptographic-blockchains--merkle-ledgers-use-chain)
   - [26. 3D Geometric Algebra & Transformations (`use math3d`)](#26-3d-geometric-algebra--transformations-use-math3d)
   - [27. Compiler Engineering & AST Metaprogramming (`use compiler`)](#27-compiler-engineering--ast-metaprogramming-use-compiler)
   - [28. Robotics, Kinematics & Motion Planning (`use robotics`)](#28-robotics-kinematics--motion-planning-use-robotics)
   - [29. Digital Signal Processing & Modulation (`use signals`)](#29-digital-signal-processing--modulation-use-signals)
   - [30. Astronomy & Orbital Ephemeris (`use astronomy`)](#30-astronomy--orbital-ephemeris-use-astronomy)
   - [31. Computational Chemistry & SMILES Cheminformatics (`use chem`)](#31-computational-chemistry--smiles-cheminformatics-use-chem)
   - [32. Data Compression & Information Theory (`use compression`)](#32-data-compression--information-theory-use-compression)
   - [33. Time Series Forecasting & ARIMA (`use time_series`)](#33-time-series-forecasting--arima-use-time_series)
   - [34. Computer Algebra & Symbolic Calculus (`use symbolic`)](#34-computer-algebra--symbolic-calculus-use-symbolic)
   - [35. Software 3D Rasterization & Shaders (`use graphics`)](#35-software-3d-rasterization--shaders-use-graphics)
   - [36. Telecommunications & Channel Coding (`use telecom`)](#36-telecommunications--channel-coding-use-telecom)
   - [37. Computational Neuroscience & Spiking Networks (`use neuro`)](#37-computational-neuroscience--spiking-networks-use-neuro)
   - [38. Formal Automata & State Machines (`use automata`)](#38-formal-automata--state-machines-use-automata)
   - [39. Metrics, Telemetry & SRE Observability (`use metrics`)](#39-metrics-telemetry--sre-observability-use-metrics)
   - [40. Spatial 3D Audio & Binaural HRTF (`use spatial_audio`)](#40-spatial-3d-audio--binaural-hrtf-use-spatial_audio)
   - [41. Deep Multi-Domain Chaining (`use data, ml, finance`)](#41-deep-multi-domain-chaining)
6. [Cross-Domain Orchestration & Production Pipelines](#6-cross-domain-orchestration--production-pipelines)
7. [Deep Algorithmic Engine Reference (Clusters A–H)](#7-deep-algorithmic-engine-reference-clusters-ah)
8. [Production Deployment, PyPI Ecosystem & FAQ](#8-production-deployment-pypi-ecosystem--faq)

---

## 1. The Pitch: Why DoomScript?

### The Problem with Modern Programming Languages

There are over 8 billion people on Earth, yet fewer than 0.3% can write code. Why?

Because traditional programming languages were designed for **machines, not human beings**:
1. **Cryptic Syntax**: Beginners are forced to memorize arcane symbols (`{ }`, `[ ]`, `::`, `->`, `!=`, `__init__`, `self`, `===`) instead of focusing on what they want to achieve.
2. **Off-by-One Traps**: People count starting at 1 (`first`, `second`, `third`). Languages force 0-based indexing, silently breaking algorithms or generating confusing off-by-one errors.
3. **Cryptic Stack Traces**: One missing character produces 50 lines of unreadable compiler errors (`UnboundLocalError: cannot access local variable where it is not associated with a value`, `TypeError: 'NoneType' object is not subscriptable`, `AttributeError: 'list' object has no attribute 'items'`).
4. **Endless Boilerplate**: Doing simple real-world tasks—like reading a CSV, filtering active rows, calculating an average, and saving a report—requires 40 lines of nested imports, context managers, and type conversions in Python.

**DoomScript changes everything.**

---

### The 7 Pillars of DoomScript

1. **Speakable English Grammar**: If you can say it in English, you can run it in DoomScript. `for each order in orders where amount > 100: say order's customer`.
2. **Zero Python Leakage & Empathetic Errors**: DoomScript translates 100% of errors into beginner-friendly explanations with precise caret positioning, actionable suggestions, and zero raw Python tracebacks.
3. **100% Python AST Compatibility**: DoomScript compiles directly to standard Python Abstract Syntax Trees. It has **zero runtime overhead**, native CPython speed, and bidirectional interoperability with all 500,000+ PyPI packages (NumPy, Pandas, PyTorch, Scikit-Learn, FastAPI).
4. **Sub-5 Millisecond Compilation**: Thanks to standalone LALR disk table caching (`cache=True`) and high-capacity regex caching (`re._MAXCACHE = 16384`), DoomScript compiles large files in 2–5 milliseconds.
5. **41 Embedded Batteries-Included Domains**: From machine learning and quantitative finance to 3D robotics, bioinformatics, quantum simulation, and GIS—no external packages are needed for production-grade math and science.
6. **Story-Driven Relational Modeling**: Express object-oriented and relational models as natural English sentences: `a User has many Orders`, `an Order belongs to a User`, `a BankAccount begins with balance = 100`. Declarations are completely **order-independent**.
7. **Single-File Native Executables**: Compile your `.doom` script into a standalone `.exe` (Windows) or binary (Linux/macOS) with `doom build`. Distribute your application with zero installation requirements.

---

### Side-by-Side Comparison: Python vs DoomScript

#### The Mission: Turn a messy sales spreadsheet into a clean report in 5 steps.

````carousel
```python
# -------------------------------------------------------------
# PYTHON: 38 lines, 10 concepts, nested boilerplate
# -------------------------------------------------------------
import csv
from pathlib import Path

# 1. Read messy transactions
orders = []
with open("sales_raw.csv", mode="r", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        orders.append(row)

# 2. Filter valid paid transactions over $50
valid = []
for row in orders:
    try:
        amt = float(row["amount"])
        if row["status"].strip().lower() == "paid" and amt > 50:
            valid.append({"customer": row["customer"], "amount": amt})
    except (ValueError, KeyError):
        continue

# 3. Sort by amount descending
valid.sort(key=lambda r: r["amount"], reverse=True)

# 4. Save clean audit report
with open("clean_audit.csv", mode="w", newline="", encoding="utf-8") as f:
    if valid:
        writer = csv.DictWriter(f, fieldnames=["customer", "amount"])
        writer.writeheader()
        writer.writerows(valid)

# 5. Summary metrics
total_revenue = sum(r["amount"] for r in valid)
top_customer = valid[0]["customer"] if valid else None
print(f"Total Revenue: ${total_revenue:,.2f}")
print(f"Top Customer: {top_customer}")
```
<!-- slide -->
```doom
# -------------------------------------------------------------
# DOOMSCRIPT: 12 lines, pure English, crystal-clear intent
# -------------------------------------------------------------
# 1. Read messy transactions
read csv file "sales_raw.csv" into orders

# 2. Filter valid paid transactions over $50
orders where status is "paid" into valid_orders
valid_orders where amount is over 50 into high_value

# 3. Sort by amount descending
sort high_value by amount descending

# 4. Save clean audit report
write csv high_value into file "clean_audit.csv"

# 5. Summary metrics
set total_revenue to sum of amount in high_value
set top_order to first item of high_value

say "Total Revenue: $", total_revenue
say "Top Customer: ", top_order's customer
```
````

---

### Feature Comparison Matrix

| Feature | DoomScript (`.doom`) | Python 3 (`.py`) | SQL (`.sql`) | Excel Formulas |
| :--- | :---: | :---: | :---: | :---: |
| **English-First Syntax** | **Native English** | Complex Punctuation | Declarative English | Cryptic Cell Grid |
| **Learning Curve** | **1 Hour** | 2–3 Months | 2–4 Weeks | 1–2 Weeks |
| **Indexing Convention** | **1-Based Natural** | 0-Based Technical | 1-Based (SQL) | 1-Based (Rows) |
| **Error Messages** | **Plain-English Caret Guidance** | Raw Python Tracebacks | Cryptic SQL Errors | `#VALUE!`, `#REF!` |
| **Compiles to Python AST** | **Yes (100% Native)** | Native | No (DBMS Only) | No |
| **Built-in Specialized Domains** | **41 Zero-Dep Domains** | Requires `pip install` | DB Queries Only | Limited Plugins |
| **Stand-alone Native Binary** | **`doom build` (.exe)** | Requires PyInstaller | Requires Server | Proprietary App |
| **Story-Driven Entities** | **`User has many Orders`** | Classes, `self`, `__init__` | DDL Tables & Foreign Keys | N/A |
| **Pronoun Tracking (`it`, `that`)** | **Built-in** | Manual Variables | N/A | N/A |
| **Adverbial Resilience (`retrying`)**| **Native English** | Decorator Libraries | N/A | N/A |

---

## 2. Quickstart & The `doom` Toolchain

### Installation & Zero-Configuration Setup

DoomScript is distributed as a lightweight, standalone Python package and precompiled binary:

```bash
# Option A: Install via pip
pip install doomscript

# Option B: Clone and run directly
git clone https://github.com/arshiljain/doomscript.git
cd doomscript
pip install -e .
```

Verify your installation:
```bash
doom --version
# DoomScript 1.2.0 (English-First AST Compiler)
```

---

### The Unified CLI

The `doom` CLI command provides an all-in-one developer toolkit:

| Command | Action | Description |
| :--- | :--- | :--- |
| `doom run <file.doom>` | **Execute** | Executes a DoomScript script with full runtime sandboxing and friendly error reporting. |
| `doom export <file.doom>` | **Transpile** | Compiles `.doom` directly into clean, readable, standard Python code (`.py`). |
| `doom build <file.doom>` | **Compile Binary** | Generates a standalone, zero-dependency native executable (`.exe` on Windows, binary on Linux). |
| `doom test` | **Test Runner** | Automatically scans and executes all test suites in the `tests/` directory. |
| `doom repl` | **Interactive Shell**| Starts the live conversational REPL environment for experimenting with English code. |
| `doom check <file.doom>` | **Verify Contracts** | Statically analyzes preconditions (`require`), postconditions (`ensure`), and type contracts without executing. |
| `doom suggest "<phrase>"`| **Auto-Suggest** | Uses difflib fuzzy matching to recommend canonical DoomScript syntax for any spoken phrasing. |
| `doom fmt <file.doom>` | **Formatter** | Formats DoomScript files according to the official style guide. |
| `doom lsp` | **Language Server** | Launches the official Language Server Protocol daemon for VS Code and Neovim integrations. |

---

### IDE Integration & Language Server Protocol

DoomScript features first-class IDE support with syntax highlighting, autocomplete, and live error diagnostics:

* **VS Code Extension**: Install the `doomscript` extension from the VS Code Marketplace or from `extensions/doomscript-vscode`.
* **Instant Hover & Completion**: Hover over any keyword or domain function to view its English documentation and examples.
* **Auto-Diagnostics**: Syntax errors and keyword collisions are underlined with actionable hints right inside your editor.

---

## 3. Language Fundamentals & Thought-to-Code Architecture

DoomScript is engineered to make programming feel as natural as speaking, without sacrificing precision.

---

### 3.1 Printing & User Interaction

Output text and numbers using natural verbs:

```doom
say "Welcome to DoomScript!"
say "Player:", player_name, "Score:", score

# Synonyms supported natively:
show "Calculating metrics..."
display "System ready."
```

Prompt users for input with type-safe English commands:

```doom
# Standard string prompt
ask "What is your name?" into user_name

# Numeric prompt (automatically converts to integer/float without ValueError crashes)
ask number "Enter your age:" into age

# Boolean yes/no prompt (recognizes 'yes', 'y', 'true', '1')
ask boolean "Do you wish to continue?" into confirmed

# Choice prompt (validates against allowed options)
ask choice "Choose role:" from ["admin", "editor", "viewer"] into selected_role
```

---

### 3.2 Variables & Flexible Assignments

DoomScript supports both standard mathematical notation and natural conversational assignments:

```doom
# Canonical conversational assignment
set score to 100
set player_name to "Alice"

# Directional phrasing
put 500 into balance
let status be "active"

# Increments and decrements
increase score by 10
decrease health by 5

# Shorthand math assignments
x += 5
x -= 2
x *= 3
x /= 2
```

---

### 3.3 Natural 1-Based Indexing & Collection Slicing

Humans count starting at 1. DoomScript provides safe, natural 1-based indexing for collections while protecting you from index errors:

```doom
numbers = [10, 20, 30, 40, 50]

# Natural 1-based indexing:
say item 1 of numbers     # Prints 10 (the first item)
say item 2 of numbers     # Prints 20 (the second item)

# Conversational aggregates:
say first item of numbers # Prints 10
say last item of numbers  # Prints 50

# Natural quantity slicing:
say first 3 items of numbers   # Prints [10, 20, 30]
say last 2 items of numbers    # Prints [40, 50]

# Collection membership and predicates:
if numbers contains 30:
    say "Found 30!"

if numbers is empty:
    say "No items."

if numbers is not empty:
    say "Collection has items."
```

#### Zero-Leak Indexing Error Protection

Unlike languages that return `None` silently or explode with confusing stack traces, DoomScript provides actionable guidance:
* `say item 10 of numbers` -> `DoomScript Runtime Error: You asked for item 10, but this list only has 5 items.`
* `say item 0 of numbers` -> `DoomScript Runtime Error: List indexing is 1-based: item 1 is the first item (requested item 0).`

---

### 3.4 Conversational Inquiries & Math

Write calculations and metrics as if you were asking questions:

```doom
orders = [
    {"item": "Laptop", "amount": 1200},
    {"item": "Mouse", "amount": 25},
    {"item": "Keyboard", "amount": 75}
]

# Querying collections conversationally:
what is the total amount in orders into total_val
what is the average amount in orders into avg_val
what is the highest amount in orders into max_val
what is the lowest amount in orders into min_val
how many items in orders into order_count

# Inline arithmetic questions:
what is 10 + 20 into thirty
what's 5 * 5 into twenty_five

say "Total:", total_val      # Total: 1300
say "Average:", avg_val      # Average: 433.33
say "Count:", order_count    # Count: 3
```

---

### 3.5 Natural Pronoun Resolution

DoomScript tracks context across sentences. Pronouns like `it`, `that`, `them`, and `this` automatically refer to the result of the previous calculation or statement:

```doom
read file "config.json" into raw_config
parse json raw_config into settings

# 'it' refers to the most recently assigned value (settings)
say it's theme

numbers = [1, 2, 3, 4, 5]
filter numbers where x > 2 into high_nums

# 'them' refers to high_nums
for each num in them:
    say num
```

---

### 3.6 Possessive Syntax & Deep Navigations

Access object attributes, dictionary keys, and record fields using English possessive apostrophe-s (`'s`):

```doom
a Person has name, age, city
create a Person with name "Bob", age 32, city "Chicago" into p1

# Natural possessive reads:
say p1's name
say p1's age
say p1's city

# Natural possessive mutations:
set p1's name to "Robert"
change p1's city to "New York"
```

---

### 3.7 Relational Reshaping

Transform, partition, and flatten data structures in single English expressions:

```doom
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Partition into two collections in one line:
partition numbers into evens and odds where x is even

say "Evens:", evens   # [2, 4, 6, 8, 10]
say "Odds:", odds     # [1, 3, 5, 7, 9]

# Pair two lists into a dictionary:
keys = ["name", "score", "level"]
values = ["Alice", 95, 4]
pair keys with values into dictionary player_profile

say player_profile's name   # Alice

# Flatten nested matrices:
matrix = [[1, 2], [3, 4], [5, 6]]
flatten matrix into flat_list
say flat_list               # [1, 2, 3, 4, 5, 6]
```

---

### 3.8 Universal & Existential Quantifiers

Validate collections without writing manual `for` loops or lambda functions:

```doom
scores = [85, 92, 78, 90, 88]

# Universal quantifier (all items match):
if every s in scores is at least 70:
    say "All students passed!"

# Existential quantifier (at least one item matches):
if any s in scores is over 90:
    say "At least one student received top honors!"

# Negative quantifier (no items match):
if no s in scores is negative:
    say "All test scores are valid non-negative numbers."

# Shorthand aggregate predicate:
if all items in scores are positive:
    say "Verified positive scores."
```

---

### 3.9 Contextual Query Pipelines & Relative Clauses

Filter, transform, and iterate through structured data using conversational clauses:

```doom
users = [
    {"name": "Alice", "role": "admin", "active": True},
    {"name": "Bob", "role": "viewer", "active": False},
    {"name": "Charlie", "role": "admin", "active": True}
]

# Contextual attribute filtering:
keep only users where role is "admin" into active_admins
discard from users where active is False into verified_users

# Relative clause iteration ('whose'):
for each person whose role is "admin":
    say "Alerting admin:", person's name
```

---

### 3.10 Superlative Queries

Find extreme records (highest, lowest, cheapest, largest, oldest, newest) in a single readable sentence:

```doom
inventory = [
    {"name": "Laptop", "price": 1200, "stock": 4},
    {"name": "Mouse", "price": 25, "stock": 150},
    {"name": "Monitor", "price": 300, "stock": 12}
]

# Superlative extraction:
find cheapest item in inventory by price into budget_item
find largest item in inventory by stock into bulk_item

say "Cheapest:", budget_item's name     # Mouse
say "Most in stock:", bulk_item's name  # Mouse

scores = [45, 98, 23, 87, 100, 64]
find highest score in scores into top_score
say "Top score:", top_score             # 100
```

---

### 3.11 Adverbial Qualifiers & System Resilience

Add production-grade retries, backoff, timeouts, and caching to function calls and network operations directly in English:

```doom
to fetch_server_status:
    fetch json from "https://api.example.com/status" into raw_data
    return raw_data

# Automatically retry 3 times with exponential backoff:
call fetch_server_status retrying 3 times with 2.0 backoff into status_data

# Enforce strict execution timeouts:
call heavy_calculation with timeout of 5 seconds into result

# Memoize results with time-to-live caching:
call fetch_exchange_rates caching for 60 seconds into live_rates
```

---

### 3.12 Compound Sentences & Natural Conjunctions

Chain multiple actions naturally using commas and conjunctions (`then`, `and then`, `then if`, `then unless`):

```doom
set x to 10, then increase x by 5, then say "Updated x:", x

# Conditional compound phrasing:
set role to "admin", then if role is "admin":
    say "Access granted to admin console."
otherwise:
    say "Standard access granted."
```

---

### 3.13 Functions, Scopes & Scoped Globals

Define clean, keyword-argument-friendly functions with `to`:

```doom
to calculate_tax with amount, rate = 0.07:
    set tax to amount * rate
    return tax

set tax1 to calculate_tax(100)
set tax2 to calculate_tax(200, 0.10)

say "Tax 1:", tax1   # 7.0
say "Tax 2:", tax2   # 20.0
```

#### Modifying Global Variables from Functions

Inside functions, modify variables declared in the outer scope with `global <var>` or `modify global <var>`:

```doom
counter = 0

to increment:
    global counter
    counter = counter + 1

to add_ten:
    modify global counter
    counter = counter + 10

increment()
increment()
add_ten()
say counter   # 12
```

If you modify a global variable inside a function without declaring it, DoomScript prevents confusion with an explicit diagnostic:
`DoomScript Runtime Error: You tried to modify the global variable 'counter' inside a function. In DoomScript, declare 'global counter' at the top of the function to modify it.`

---

### 3.14 Story-Driven Relational Entities

Model business domains and relational data using declarative, English-first entity schemas. **Declarations are completely order-independent**:

```doom
# Declare relationships anywhere in the file:
a Customer has many Orders
an Order belongs to a Customer

# Entity schema with default initial lifecycle:
a Customer begins with name = "", tier = "standard", orders = []
an Order begins with item = "", amount = 0, status = "pending"

# Create entity records with natural arguments:
create a Customer with name "Alice", tier "VIP" into c1
create an Order with item "MacBook Pro", amount 2400 into o1

# Bidirectional relationship sync:
add o1 to c1.orders

say "Customer:", c1.name
say "Order count:", count of c1.orders
say "Order customer:", o1.customer.name   # Automatically synced to c1!
```

---

### 3.15 Empathetic Error Diagnostics & Guardrails

DoomScript was built so that you **never see a raw, intimidating Python traceback**:

#### 1. Caret Positioning & Clear Distinctions
Errors clearly distinguish between **`DoomScript Syntax Error`** and **`DoomScript Runtime Error`** with exact line numbers and visual pointers:

```
DoomScript Runtime Error at script.doom:2:1

   2 | say item 10 of nums
       ^

Problem: You asked for item 10, but this list only has 3 items.
```

#### 2. Reserved Keyword Collision Advice
If you accidentally try to assign to a reserved word like `last = 9` or `count = 5`, DoomScript explains why and suggests a solution:

```
DoomScript Syntax Error at script.doom:1:6

   1 | last = 9
            ^

Problem: 'last' is a reserved keyword in DoomScript used in list operations ('last item of list', 'last 3 items of list'). It cannot be used as a variable name.
Did you mean: set my_last to 9
```

#### 3. Theatrical Doom Mode (`--theatrical`)
For teams that love game lore, pass `--theatrical` to the CLI to unleash DoomScript's ancient monolith persona:

```bash
doom run script.doom --theatrical
```
```
FOOLISH MORTAL! The ancient monolith rejects your utterance!
File: script.doom:1:6
   1 | last = 9
            ^
DoomScript Curse: 'last' is a reserved keyword in DoomScript...
Bow before the correct incantation: set my_last to 9
```

---

### 3.16 Sub-5ms Compilation Engine

DoomScript is engineered for instantaneous feedback:
* **Lark LALR Table Caching (`cache=True`)**: Pre-computes and caches grammar state tables on disk. Once built, parser initialization takes under **0.18 seconds**.
* **High-Capacity Regex Caching (`re._MAXCACHE = 16384`)**: Prevents regex eviction cycles across thousands of domain rules.
* **Compilation Latency**: Compiling a 100-line script takes **2.1 milliseconds**.

---

## 4. Standard Built-in Capabilities

### File I/O & Document Processing

Read and write text files effortlessly:

```doom
# Write text to file
write "Transaction Log: 2026-10-22" into file "log.txt"

# Append text to file
append "Status: Verified" to file "log.txt"

# Read file content into a variable
read file "log.txt" into content
say content

# Check if file exists
check if file "log.txt" exists into file_present
if file_present:
    say "Log file exists!"

# List files in directory
list files in "." into local_files
say "Files found:", count of local_files
```

---

### CSV & Tabular Intelligence

Read and write CSV tables with automatic header mapping and dictionary conversion:

```doom
# Read CSV file directly into list of records
read csv file "sales.csv" into sales_records

for each row in sales_records:
    say "Customer:", row's customer, "Amount:", row's amount

# Filter and write back clean CSV data
sales_records where amount > 100 into premium_sales
write csv premium_sales into file "premium_report.csv"
```

---

### JSON Serialization & Configuration

Native parsing and serialization of structured JSON data:

```doom
raw_json = '{"name": "Alice", "role": "admin", "quota": 5000}'

# Parse JSON string into dictionary record
parse json raw_json into user_profile
say user_profile's name   # Alice

# Convert structured data back to JSON string
convert user_profile to json into export_json
say export_json
```

---

### System, Subprocess & Environment Primitives

Interact with the operating system safely without shell-injection vulnerabilities:

```doom
# Access environment variables
get environment variable "HOME" into home_dir

# Execute system commands (defaults to safe shell=False execution)
run command "git status" into git_output
say git_output

# Sleep / Pause execution
wait 2 seconds
say "Resumed execution."
```

---

### Sound Synthesis & 2D Immediate Canvas

DoomScript includes built-in multimedia commands for games, notifications, and visual simulations:

```doom
# Audio beeps and sound files
beep 440 hz for 500 ms
play sound "success.wav"

# 2D Drawing Window
open_window "DoomScript Canvas" with width 800, height 600
clear screen
draw circle at 400, 300 with radius 50, color "red"
draw rectangle at 100, 100 with width 200, height 80, color "blue"
draw text "Hello Canvas!" at 350, 280 with size 24, color "white"
refresh screen
```


---

## 5. The 41 Specialized Domain Packs (`use <domain>`)

DoomScript features 41 built-in, zero-dependency domain libraries. Activate any domain using `use <domain>` at the top of your script. Domain keywords are dynamically scoped to keep the base language lightweight and eliminate name collisions.

### 1. DSA & Algorithms (`use dsa`)
Advanced self-balancing trees, string automata, caches, and algorithmic primitives:

```doomscript
use dsa

# 1. Prefix Trie & Suffix Automaton
create trie into t
insert word "apple" into trie t
insert word "application" into trie t
search trie t for "apple" into found_word
all words in trie t starting with "app" into prefix_matches

sam = dsa_suffix_automaton("banana")
can_match = dsa_sam_contains(sam, "nan")
sub_count = dsa_sam_distinct_substrings(sam)

# 2. AVL Self-Balancing Binary Search Tree
avl = dsa_avl_create()
dsa_avl_insert(avl, 50)
dsa_avl_insert(avl, 20)
dsa_avl_insert(avl, 70)
has_twenty = dsa_avl_search(avl, 20)
sorted_elements = dsa_avl_inorder(avl)

# 3. Aho-Corasick Multi-Pattern String Matcher
ac = dsa_ahocorasick_create(["he", "she", "his", "hers"])
ac_matches = dsa_ahocorasick_search(ac, "ushers")

# 4. Disjoint Set Union (DSU) & Fenwick / Segment Trees
create dsu of size 10 into dsu
union elements 1 and 2 in dsu
check if 1 and 2 are connected in dsu into are_connected
count connected components in dsu into component_count

fenwick = dsa_fenwick_create([1, 3, 5, 7, 9, 11])
range_sum = dsa_fenwick_query(fenwick, 1, 4)
dsa_fenwick_update(fenwick, 2, 6)

# 5. LRU Cache & Monotonic Queue
create lru cache with capacity 3 into cache
put key "a" with value 100 into cache cache
get key "a" from cache cache into cached_val

mq = dsa_monotonic_queue_create()
dsa_monotonic_queue_push(mq, 10)
dsa_monotonic_queue_push(mq, 20)
current_max = dsa_monotonic_queue_max(mq)

# 6. Search, Order Statistics & Graph Invariants
binary search 42 in sorted_nums into idx
k-th smallest element in nums with k 3 into third_min
k-th largest element in nums with k 1 into absolute_max
rabin karp search for "pattern" in text into match_indices
manacher longest palindrome in "babad" into longest_pal
count inversions in nums into inversion_count
find bridges in graph_matrix into critical_bridges
```

---

### 2. Data Engineering (`use data`)
Tabular ETL pipelines, SQL-like transforms, statistical profiling, and window functions:

```doomscript
use data

read csv "sales.csv" into raw_table

# 1. Statistical Data Profiler & Pivot Tables
profile = data_profile_dataframe(raw_table)
say "Data Profile Summary: ", profile["summary"]

pivot = data_pivot_table(raw_table, "region", "quarter", "revenue", "sum")

# 2. Data Cleaning & Imputation
forward fill missing values in column "price" of raw_table into ffilled_table
backward fill missing values in column "units" of ffilled_table into clean_table
coalesce columns [clean_table's preferred_phone, clean_table's backup_phone] into primary_contact

# 3. Window Expressions & Analytical Rankings
rank rows in clean_table by column "revenue" descending into ranked_table
future_price = data_window_lead(clean_table, "price", 1)
prev_price = data_window_lag(clean_table, "price", 1)
rolling_rev_30d = data_window_rolling_sum(clean_table, "revenue", 7)
rolling_avg_price = data_window_rolling_avg(clean_table, "price", 14)

# 4. Aggregations, Schema Validation & Joins
cumulative sum of column "revenue" in clean_table into running_revenue
cross join table_a with table_b into cartesian_table
validate schema of clean_table against schema_rules into validation_report
calculate summary of clean_table into statistical_overview
```

---

### 3. Machine Learning (`use ml`)
Full classification, CART decision trees, multilayer perceptrons, clustering, and metrics:

```doomscript
use ml

# 1. 3-Way Train/Val/Test Split & Preprocessing
split dataset samples into 70% train, 15% validation, 15% test into partitioned_data

# 2. CART Decision Tree (Gini/Entropy with Pruning)
cart_model = ml_train_cart_decision_tree(X_train, y_train, 5, 2, "gini")
cart_preds = ml_predict_cart_decision_tree(cart_model, X_test)

# 3. Multilayer Perceptron (Neural Network with Backpropagation)
mlp_model = ml_train_mlp(X_train, y_train, [16, 8], 0.01, 100, 32, "relu")
mlp_preds = ml_predict_mlp(mlp_model, X_test)

# 4. Classical Classifiers & Regressors
train knn classifier with features X_train and labels y_train and neighbors 5 into knn_model
train decision stump with features X_train and labels y_train into stump_model
train naive bayes with features X_train and labels y_train into bayes_model

# 5. Clustering & Dimensionality Reduction
cluster data X with kmeans using 3 clusters into clusters
apply pca to data X with 2 components into reduced_matrix

# 6. Evaluation Metrics
predict classes for X_test with model knn_model into y_pred
calculate f1 score between y_test and y_pred into f1_res
calculate precision between y_test and y_pred into precision_res
calculate recall between y_test and y_pred into recall_res
calculate log loss between y_true and y_prob into loss_val
calculate brier score between y_true and y_prob into brier_val
```

---

### 4. Quantitative Finance (`use finance`)
Technical indicators, portfolio risk metrics, Black-Scholes/Binomial options, GARCH volatility:

```doomscript
use finance

# 1. Advanced Options Pricing & Greeks
bs_res = finance_black_scholes(100.0, 95.0, 0.5, 0.05, 0.20, "call")
say "Call Price: ", bs_res["price"], " Delta: ", bs_res["delta"], " Vega: ", bs_res["vega"]

american_put = finance_binomial_option_tree(100.0, 95.0, 0.5, 0.05, 0.20, 100, False, True)
say "American Put Tree Price: ", american_put["price"]

# 2. GARCH Volatility & Momentum Oscillators
garch_vols = finance_garch11_volatility(daily_returns, 0.00001, 0.08, 0.90)
macd_data = finance_macd(closing_prices, 12, 26, 9)
rsi_val = finance_rsi(closing_prices, 14)

# 3. Technical Indicators
calculate vwap with high prices_high low prices_low close prices_close volume volumes into vwap_series
stochastic oscillator with high prices_high low prices_low close prices_close period 14 into stoch_vals
keltner channels for prices with period 20 and multiplier 2.0 into keltner
average true range for high prices_high low prices_low close prices_close period 14 into atr_vals
williams r for high prices_high low prices_low close prices_close period 14 into will_r
money flow index for high prices_high low prices_low close prices_close volume volumes period 14 into mfi_vals

# 4. Risk & Performance Metrics
sortino ratio of returns with risk_free 0.02 into sortino_val
treynor ratio of returns with beta 1.1 and risk_free 0.02 into treynor_val
calmar ratio of returns with max_drawdown 0.15 into calmar_val
beta of asset_returns against market_returns into beta_val
jensen alpha of asset_returns against market_returns with risk_free 0.02 and beta 1.1 into alpha_val
rebalance portfolio holdings to target_weights into trade_orders
```

---

### 5. NLP & Text Intelligence (`use nlp`)
Text processing, HMM POS tagging, Byte-Pair Encoding, BLEU evaluation, and vectorization:

```doomscript
use nlp

# 1. Hidden Markov Model (HMM) Part-of-Speech Tagging
train_corpus = [[["The", "DT"], ["dog", "NN"], ["barks", "VBZ"]]]
hmm_tagger = nlp_hmm_pos_tagger(train_corpus)
tagged_sent = nlp_hmm_tag_sequence(hmm_tagger, ["The", "dog", "runs"])

# 2. Byte Pair Encoding (BPE) Subword Tokenizer
bpe_model = nlp_byte_pair_encoder(["low", "lower", "newest", "widest"], 10)
bpe_tokens = nlp_bpe_encode(bpe_model, "lowest")
reconstructed_text = nlp_bpe_decode(bpe_model, bpe_tokens)

# 3. Translation Quality & Vectorization
bleu = nlp_bleu_score(["the", "cat", "sat", "on", "mat"], [["the", "cat", "sat", "on", "the", "mat"]], 4)
tfidf_model = nlp_tfidf_vectorizer(["machine learning in python", "deep learning natural language"])
doc_vector = nlp_tfidf_transform(tfidf_model, "machine learning algorithms")

# 4. Information Retrieval & Linguistic Distances
rank corpus doc_collection for query "search terms" using bm25 into ranked_docs
levenshtein distance between "kitten" and "sitting" into edit_distance
hamming distance between "1011101" and "1001001" into bit_diff

# 5. Phonetics & Readability Metrics
soundex "Robert" into soundex_code
metaphone "Knight" into metaphone_code
porter stem of "generously" into root_word
flesch reading ease of article into readability_score
gunning fog index of article into fog_score
count syllables in "incomprehensible" into syllable_count

# 6. Sentiment & Sanitization
rouge-l score between generated_text and reference_text into rouge_res
expand contractions in "don't won't shouldn't" into expanded_text
mask sensitive entities in user_bio into sanitized_bio
vader sentiment of customer_review into sentiment_scores
```

---

### 6. Graph Theory (`use graph`)
Network modeling, Tarjan SCC, Edmonds-Karp max flow, A* search, and Louvain communities:

```doomscript
use graph

# 1. Tarjan Strongly Connected Components (SCC)
adj = {"A": ["B"], "B": ["C"], "C": ["A", "D"], "D": ["E"], "E": ["D"]}
sccs = graph_tarjan_scc(adj)
say "Strongly Connected Components: ", sccs

# 2. Maximum Flow (Edmonds-Karp Residual Network)
flow_adj = {"S": {"A": 10, "B": 5}, "A": {"B": 15, "T": 10}, "B": {"T": 10}, "T": {}}
flow_res = graph_max_flow_edmonds_karp(flow_adj, "S", "T")
say "Maximum Network Flow: ", flow_res["max_flow"]

# 3. A* Heuristic Search & Louvain Community Detection
astar_res = graph_astar_search(grid_graph, node_coordinates, "start", "goal")
communities = graph_louvain_community_detection(social_adj)

# 4. Structural Properties & Link Prediction
clustering coefficient of social_graph into clustering_score
find bridges in communication_graph into network_bottlenecks
find articulation points in road_network into critical_junctions
transitive closure of dag_graph into reachable_matrix
topological generations of dependency_graph into execution_phases
k core decomposition of graph with k 3 into dense_subgraph
predict links in user_network using adamic adar into friend_recommendations
predict links in citation_network using jaccard into related_papers
```

---

### 7. Computer Vision & Media (`use image`)
Image generation, Canny edge detection, Otsu thresholding, Gaussian blur, and filters:

```doomscript
use image

create canvas with width 640 and height 480 and color "white" into img
load image "photo.jpg" into photo

# 1. Advanced Computer Vision Filters
blurred = image_gaussian_blur(photo_pixels, 640, 480, 2, 1.4)
canny_edges = image_canny_edge_detector(blurred, 640, 480, 50, 150)
otsu_binary = image_otsu_threshold(photo_pixels, 640, 480)
equalized = image_histogram_equalize(photo_pixels, 640, 480)

# 2. Filtering & Pixel Manipulation
apply sobel filter to photo into edges
threshold photo with cutoff 128 into binarized_img
sharpen image photo with factor 1.5 into sharp_photo
invert colors of photo into negative_photo
adjust contrast of photo with factor 1.2 into contrasted_photo
apply sepia filter to photo into vintage_photo

# 3. Spatial & Channel Operations
split channels of photo into rgb_channels
merge channels rgb_channels into restored_photo
flip photo horizontally into mirrored_photo
apply vignette to photo with intensity 0.7 into artistic_photo
pixelate photo with block_size 8 into mosaic_photo
calculate mean color of photo into average_rgb
```

---

### 8. Web Scraping & DOM (`use web`)
Declarative CSS selectors, OpenGraph/JSON-LD metadata extraction, and RFC 9309 robots.txt:

```doomscript
use web

# 1. Pure-Python CSS Selector Engine
matched_nodes = web_select_css(page_html, "div.content > article#main-story p.highlight")

# 2. Rich Social Metadata & JSON-LD Extraction
meta = web_extract_metadata(page_html)
say "Page Title: ", meta["title"]
say "OpenGraph Image: ", meta["opengraph"]["image"]
say "JSON-LD Entities: ", meta["json_ld"]

# 3. RFC 9309 Robots.txt Parser
can_crawl = web_parse_robots_txt(robots_txt_content, "Googlebot", "/api/v1/users")

# 4. Form Parsing & Link Inspection
parse form inputs from html_code into form_data
generate url encoded string from parameters into query_string
extract urls from sitemap sitemap_xml into catalog_urls
canonicalize url "https://example.com/item/../index.html" into clean_url
extract headings from page_html into heading_structure
serialize cookies cookie_jar into cookie_header
generate curl command for url "https://api.test.com" with method "POST" and headers req_headers into curl_cmd
```

---

### 9. Audio Synthesis & DSP (`use audio`)
Sound generation, STFT spectrograms, MFCC feature extraction, and pitch shifting:

```doomscript
use audio

# 1. STFT Spectrogram & Inverse Reconstruction
stft_spec = audio_stft(audio_samples, 512, 128)
reconstructed_audio = audio_istft(stft_spec, 128)

# 2. Speech Feature Extraction & Pitch Shifting
mfcc_matrix = audio_mfcc(speech_samples, 16000, 13, 512, 256)
shifted_pitch = audio_pitch_shift(speech_samples, 4.0, 16000)

# 3. Waveform Generators
generate square wave with frequency 440.0 and duration 1.0 into sq_tone
generate sawtooth wave with frequency 220.0 and duration 1.0 into saw_tone
generate triangle wave with frequency 880.0 and duration 1.0 into tri_tone
generate white noise with duration 2.0 into ambient_noise

# 4. Signal Processing & Mixing
adjust gain of sq_tone by 3.0 db into boosted_tone
trim silence from recorded_audio with threshold -40 into trimmed_audio
apply fade out to sq_tone with duration 0.2 into smooth_tone
mix audio tracks [sq_tone, ambient_noise] with balance [0.8, 0.2] into mixed_track
apply stereo pan to sq_tone with pan -0.5 into left_leaning_audio
apply lowpass filter to sq_tone with cutoff 1000 into warm_audio
apply highpass filter to ambient_noise with cutoff 500 into bright_noise
calculate rms energy of sq_tone into energy_level
stretch audio sq_tone by factor 1.5 into slow_audio
```

---

### 10. Relational Database & SQL (`use db`)
Fluent SQL Query Builder, In-Memory Relational Engine, and Migration Manager:

```doomscript
use db

# 1. Fluent SQL AST Query Builder
qb = db_query_builder("users")
sql_ast = qb.select(["id", "name", "email"]).where("status = 'active'").join("orders", "users.id = orders.user_id").order_by("created_at", "DESC").build()
say "Generated SQL: ", sql_ast["sql"]

# 2. In-Memory Relational Database Engine
mem_db = db_in_memory_engine()
mem_db.create_table("products", ["id", "name", "price", "stock"])
mem_db.insert("products", {"id": 1, "name": "Laptop", "price": 1200, "stock": 15})
low_stock = mem_db.select("products", lambda r: r["stock"] < 20)

# 3. Schema Migration Manager with Rollback
migrator = db_migration_manager()
migrator.add_migration("v1_init", "CREATE TABLE items (id INT);", "DROP TABLE items;")
migrator.migrate()
migrator.rollback()

# 4. SQLite Administration & Automation
connect to database "app.db" into db
create index "idx_user_email" on table "users" with column "email" in db
vacuum database db
analyze database statistics for db
list tables in db into table_names
list indexes on table "users" in db into user_indexes
bulk insert records new_users into table "users" in db with batch 500
export table "users" from db to csv "users_backup.csv"
export ddl schema from db into schema_sql
```

---

### 11. Networking & System (`use net`)
RFC 7540 HTTP/2 frames, IPv4/TCP packet dissector, RFC 6455 WebSockets, and CIDR math:

```doomscript
use net

# 1. HTTP/2 Binary Framing (RFC 7540)
parsed_frame = net_http2_parse_frame(raw_h2_bytes)
say "HTTP/2 Frame Type: ", parsed_frame["type"], " Stream ID: ", parsed_frame["stream_id"]

# 2. Raw Packet Dissector & Internet Checksum
packet = net_dissect_ipv4_packet(ethernet_payload_bytes)
say "Source IP: ", packet["src_ip"], " Destination: ", packet["dst_ip"], " Protocol: ", packet["protocol"]

# 3. WebSocket Masking & Framing (RFC 6455)
ws_frame = net_websocket_frame("Hello, DoomScript Server!", True, True)

# 4. IP & CIDR Networking
calculate netmask for cidr "192.168.1.0/24" into subnet_mask
check if ip "192.168.1.55" is in subnet "192.168.1.0/24" into in_local_net
expand cidr range "10.0.0.0/29" into available_ips
validate ipv4 address "172.16.0.1" into is_valid_v4
validate ipv6 address "2001:db8::1" into is_valid_v6
format mac address "001A2B3C4D5E" to standard into formatted_mac
query whois for domain "doomscript.org" into domain_whois
exponential backoff delays with base 1.5 and attempts 5 into retry_schedule
scan open ports on host "127.0.0.1" for ports [80, 443, 8080] into open_ports
```

---

### 12. Simulation & Stochastics (`use sim`)
M/M/c queuing networks, Conway 2D Cellular Automata, Reynolds Boids, and Markov processes:

```doomscript
use sim

# 1. Multi-Server Queuing Network (M/M/c)
mmc = sim_queue_system(5.0, 3.0, 2)
say "M/M/c System Utilization: ", mmc["utilization"], " Mean Wait: ", mmc["mean_wait_time"]

# 2. 2D Cellular Automata (Conway's Game of Life / B3/S23)
ca = sim_cellular_automaton(50, 50, "B3/S23", glider_gun_seed, 100)

# 3. Autonomous Swarm & Flocking Simulation (Reynolds Boids)
flock = sim_boids_flocking(50, 200, [500, 500], 50.0)

# 4. Markov Chains & Processes
simulate markov chain with transitions transition_matrix and steps 50 from state 0 into state_history
simulate wiener process with drift 0.05 and volatility 0.2 and steps 100 into stock_path

# 5. Random Variate Distributions & Bootstrap Testing
generate geometric variates with probability 0.3 and size 1000 into geo_samples
generate binomial variates with trials 10 and probability 0.5 and size 500 into binom_samples
generate triangular variates with low 0.0 high 10.0 mode 3.0 and size 100 into tri_samples
calculate bootstrap confidence interval for observations with percentiles [2.5, 97.5] and resamples 1000 into conf_int
run permutation test between sample_a and sample_b with permutations 500 into p_value
```

---

### 13. Geospatial Analytics (`use geo`)
Vincenty WGS-84 geodesic distance, point-in-polygon raycasting, spherical area, and R-Trees:

```doomscript
use geo

# 1. Vincenty Geodesic Distance (WGS-84 Ellipsoid Precision)
dist_meters = geo_vincenty_distance(37.7749, -122.4194, 34.0522, -118.2437)
say "Vincenty Distance: ", dist_meters, " meters"

# 2. Point-In-Polygon & Spherical Polygon Area
inside = geo_point_in_polygon([37.75, -122.42], city_boundary_polygon)
area_sqkm = geo_polygon_area_sq_km(national_park_polygon)

# 3. 2D Spatial R-Tree Indexing
rtree = geo_rtree_create()
rtree.insert("store_101", [37.77, -122.42, 37.78, -122.41])
nearby_stores = rtree.search([37.76, -122.43, 37.79, -122.40])

# 4. Geohash, Navigation & Douglas-Peucker Simplification
encode geohash for latitude 37.7749 and longitude -122.4194 with precision 8 into sfo_hash
decode geohash sfo_hash into sfo_coords
cross track distance from point p to path start_pt, end_pt into off_track_meters
destination point from start_pt with bearing 90.0 and distance 50.0 km into east_pt
calculate convex hull of perimeter_points into boundary_polygon
simplify path polyline_coords using douglas peucker with tolerance 0.01 into compressed_path
```

---

### 14. Optimization & OR (`use opt`)
Simulated Annealing, Genetic Algorithms, Particle Swarm (PSO), and Nelder-Mead:

```doomscript
use opt

# 1. Heuristic Metaheuristic Optimizers
sa_sol = opt_simulated_annealing(cost_function, [0.0, 0.0], neighbor_generator, 100.0, 0.95, 1000)
say "Simulated Annealing Best: ", sa_sol["best_cost"]

ga_sol = opt_genetic_algorithm(fitness_function, 32, 50, 100, 0.02)
say "Genetic Algorithm Best Fitness: ", ga_sol["best_fitness"]

pso_sol = opt_particle_swarm(sphere_cost, 30, 5, [[-5.0, 5.0]] * 5, 200)
simplex_sol = opt_nelder_mead(rosenbrock_cost, [1.5, 1.5], 0.1, 500)

# 2. Dynamic Programming & Discrete Optimization
solve 0/1 knapsack with weights [2, 3, 4, 5] and values [3, 4, 5, 6] and capacity 8 into knapsack_max
longest increasing subsequence in [10, 9, 2, 5, 3, 7, 101, 18] into lis_seq
minimum coins for amount 11 with denominations [1, 2, 5] into min_coins
build huffman tree from frequencies char_freqs into huffman_codes
solve traveling salesperson for distance_matrix using 2-opt into tsp_tour
solve bipartite matching for cost_matrix using hungarian into optimal_assignment
```

---

### 15. AI Agents & Multi-Agent Workflows (`use agent`)
Tool Execution Harness, Sliding-Window Token Memory, ReAct Reasoning Agent:

```doomscript
use agent

# 1. Strict Tool Execution Harness
harness = agent_tool_harness()
harness.register_tool("fetch_weather", weather_fn, weather_schema)
tool_result = harness.execute_tool("fetch_weather", {"city": "San Francisco"})

# 2. Sliding-Window Agent Memory Buffer
memory = agent_memory_buffer(20, 2048)
memory.add_message("user", "Analyze recent sales report")
memory.add_message("assistant", "Starting analysis on Q3 dataset...")
active_context = memory.get_context()

# 3. Autonomous ReAct (Reasoning + Acting) Agent
react_agent = agent_react_agent([search_tool, calculator_tool], "You are an autonomous research analyst.")
solution = react_agent.run("What is 15% of the market cap of Apple?")

# 4. Multi-Agent Team Coordination
create agent researcher with role "data investigator" into agent_a
create agent critic with role "fact checker" into agent_b
create team review_board with agents [agent_a, agent_b] into editorial_board
tally consensus votes from ["approve", "approve", "reject"] with threshold 0.6 into vote_outcome
adjudicate debate between agent_a and agent_b on topic "Microservices vs Monolith" into winner_verdict
```

---

### 16. Cloud Storage & Infrastructure (`use cloud`)
Storage bucket lifecycle, IAM policy evaluation, multipart uploads, and multi-cloud cost calculator:

```doomscript
use cloud

# 1. Pure Cloud Storage Manager (Multipart & Versioning)
csm = cloud_storage_manager()
csm.upload_part("dataset-2026", "chunks/part1.bin", 1, chunk1_bytes)
csm.upload_part("dataset-2026", "chunks/part1.bin", 2, chunk2_bytes)
csm.complete_multipart("dataset-2026", "chunks/part1.bin")
versions = csm.list_versions("dataset-2026", "chunks/part1.bin")

# 2. IAM Policy Engine (Allow/Deny, Actions, Resources, Conditions)
iam = cloud_iam_policy_engine()
iam.add_policy("DeveloperAccess", {
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::prod-bucket/*"
})
can_read = iam.evaluate("DeveloperAccess", "s3:GetObject", "arn:aws:s3:::prod-bucket/app.json")

# 3. Multi-Cloud Cost Calculator (AWS, GCP, Azure)
calc = cloud_cost_calculator()
monthly_cost = calc.estimate_monthly({
    "provider": "aws",
    "instances": [{"type": "t4g.xlarge", "count": 4}],
    "storage_gb": 500,
    "egress_gb": 200
})
say "Estimated Monthly Infrastructure Cost: $", monthly_cost["total_usd"]

# 4. Storage Bucket Operations & Mirroring
connect to bucket "production-store" into b1
connect to bucket "backup-store" into b2
write text "System log line" to object "logs/app.log" in b1
read text from object "logs/app.log" in b1 into log_data
generate presigned put url for "uploads/data.bin" in b1 with expiry 1800 into upload_url
verify sha256 checksum of "logs/app.log" in b1 against expected_hash into sha_ok
mirror bucket b1 to b2 into mirror_report
diff bucket b1 with bucket b2 into audit_diff
export bucket manifest for b1 to "manifest.json" into exported_manifest
```

---

### 17. Office & Documents (`use office`)
Zero-dependency OpenXML `.xlsx`, `.docx`, `.pptx` generators and spreadsheet analytics:

```doomscript
use office

# 1. Pure-Python OpenXML Excel Generator (.xlsx)
wb = office_xlsx_workbook()
wb.add_sheet("Financials")
wb.set_cell("Financials", "A1", "Quarter")
wb.set_cell("Financials", "B1", "Revenue")
wb.set_cell("Financials", "A2", "Q1")
wb.set_cell("Financials", "B2", 150000)
wb.set_cell("Financials", "A3", "Q2")
wb.set_cell("Financials", "B3", 220000)
wb.set_cell("Financials", "B4", "=SUM(B2:B3)")
wb.save("reports/financials.xlsx")

# 2. Pure-Python OpenXML Word Generator (.docx)
doc_gen = office_docx_document()
doc_gen.add_heading("Quarterly Performance Review", 1)
doc_gen.add_paragraph("Enterprise ARR expanded by 42% year-over-year.")
doc_gen.add_table(["Department", "Headcount", "Budget"], [["Engineering", "28", "$1.4M"], ["Product", "12", "$0.6M"]])
doc_gen.save("reports/review.docx")

# 3. Pure-Python Presentation Generator (.pptx)
deck = office_pptx_presentation()
deck.add_slide("Board Meeting", "Q3 Strategy & Financial Highlights")
deck.save("reports/board.pptx")

# 4. CSV & Spreadsheet Utilities
detect csv delimiter "records.csv" into detected_delim
read csv header "records.csv" into header_list
load spreadsheet "financials.xlsx" into sheet
calculate sheet summary for sheet in "Financials" at column "Revenue" into revenue_stats
```

---

### 18. Research & Scientific Computing (`use research`)
Autograd reverse-mode autodiff, BibTeX citations, and citation networks:

```doomscript
use research

# 1. BibTeX Reference Engine (Parsing & IEEE/APA Formatting)
bib = research_bibtex_engine()
bib.parse_bibtex_entry("""@article{turing1936,
    author = {Turing, Alan M.},
    title = {On Computable Numbers},
    journal = {Proc. London Math. Soc.},
    year = {1936}
}""")
apa_citation = bib.format_citation("turing1936", "apa")
ieee_citation = bib.format_citation("turing1936", "ieee")

# 2. Citation Network Analytics (h-index, i10-index, PageRank Prestige)
cnet = research_citation_network()
cnet.add_paper("p1", "Attention Is All You Need", "Vaswani et al.", 2017)
cnet.add_paper("p2", "BERT", "Devlin et al.", 2018)
cnet.add_citation("p2", "p1")
h_index = cnet.calculate_author_h_index("Vaswani et al.")
prestige_scores = cnet.calculate_pagerank_prestige()

# 3. Reverse-Mode Autograd Engine
w1 = scalar 2.0 with gradient
x = scalar 3.0
b = scalar 1.5 with gradient
y = (w1 * x) + b
backward y
say "w1 gradient: ", w1's gradient  # dy/dw1 = 3.0
say "b gradient: ", b's gradient    # dy/db = 1.0

# 4. Exact Graph Algorithms & Network Flow
create a research graph into g
add edge from "A" to "B" with weight 4.0 to g
add edge from "A" to "C" with weight 2.0 to g
add edge from "C" to "B" with weight 1.0 to g
find shortest path from "A" to "B" in g using dijkstra into dijk_res
maximum flow from "A" to "B" in g using edmonds karp into max_flow
calculate pagerank of g with damping 0.85 into rank_scores
```

---

### 19. Bioinformatics & Genomics (`use bio`)
DNA/RNA transcription, reverse complement, Needleman-Wunsch & Smith-Waterman alignment, ORF finding:

```doomscript
use bio

dna = "ATGCGATCGATCGATCGTAA"

# 1. Sequence Metrics & Central Dogma
gc_val = bio_gc_content(dna)
say "GC Content: ", gc_val, "%"

transcribed_rna = bio_transcribe(dna)
say "Transcribed RNA: ", transcribed_rna

rev_comp = bio_reverse_complement("ATGC")
say "Reverse Complement: ", rev_comp

protein_seq = bio_translate("AUGUUUUAA")
say "Translated Peptides: ", protein_seq

# 2. Open Reading Frames (ORFs) & Motifs
open_frames = bio_find_orfs("ATGCGATAA", 1)
kmer_counts = bio_kmer_counts("ATGCAT", 2)
motif_positions = bio_find_motif("ATGCATGC", "ATG")
weight_daltons = bio_molecular_weight("ATGC")

# 3. Dynamic Programming Sequence Alignment
global_alignment = bio_needleman_wunsch("GATTACA", "GCATGCU", 1, -1, -1)
say "Needleman-Wunsch Score: ", global_alignment["score"]
say "Alignment Seq 1: ", global_alignment["alignment1"]
say "Alignment Seq 2: ", global_alignment["alignment2"]

local_alignment = bio_smith_waterman("TGTTACGG", "GGTTGACTA", 2, -1, -2)
say "Smith-Waterman Local Alignment Score: ", local_alignment["score"]

# 4. FASTA Parsing
fasta_records = bio_parse_fasta(">seq1 Human Actin\\nATGCGAT\\n>seq2 Mouse Beta\\nCCGGAAT")
say "First Record ID: ", fasta_records[0]["id"]
```

---

### 20. Classical & Modern Physics (`use physics`)
Ballistic trajectories with drag, SAT polygon collisions, harmonic oscillators, and PID control:

```doomscript
use physics

# 1. Projectile Kinematics (Ideal & Aerodynamic Drag)
ideal_traj = physics_projectile_trajectory(20.0, 45.0, 9.81, 10)
ideal_range = physics_projectile_range(20.0, 45.0, 9.81)

drag_traj = physics_drag_trajectory(20.0, 45.0, 0.05, 1.0, 9.81, 0.05, 100)
say "Range with Drag: ", drag_traj[-1]["x"], " meters"

# 2. Rigid Body Collision Detection (AABB & SAT)
is_colliding = physics_check_aabb_collision(0, 0, 10, 10, 5, 5, 10, 10)

poly_a = [[0, 0], [10, 0], [10, 10], [0, 10]]
poly_b = [[5, 5], [15, 5], [15, 15], [5, 15]]
sat_overlap = physics_check_sat_collision(poly_a, poly_b)

# 3. Dynamic Systems & Astrophysics
damped_wave = physics_harmonic_oscillator(1.0, 10.0, 0.5, 1.0, 0.0, 0.02, 50)
v_orbit = physics_orbital_velocity(5.972e24, 6371000.0)
v_escape = physics_escape_velocity(5.972e24, 6371000.0)

# 4. Closed-Loop PID Controller
pid = physics_create_pid(1.5, 0.1, 0.05)
control_output = physics_update_pid(pid, 100.0, 92.5, 0.1)
say "PID Correction Voltage: ", control_output
```

---

### 21. Cybersecurity & Cryptographic Primitives (`use sec`)
Shannon entropy, password audits, Caesar/Vigenere/XOR ciphers, JWT decoding, CVSS v3.1:

```doomscript
use sec

# 1. Password Strength Auditing & Shannon Entropy
pwd_entropy = sec_entropy("CorrectHorseBatteryStaple123!")
audit_report = sec_audit_password("Admin@123456!")
say "Password Strength Score: ", audit_report["score"], "/4"

# 2. Classical & Symmetric Cryptography
caesar_cipher = sec_caesar_cipher("Hello World", 3)
cracked_caesar = sec_caesar_crack(caesar_cipher)
say "Cracked Plaintext: ", cracked_caesar["plaintext"], " (Shift: ", cracked_caesar["shift"], ")"

vigenere_cipher = sec_vigenere_cipher("ATTACKATDAWN", "LEMON", True)
vigenere_plain = sec_vigenere_cipher(vigenere_cipher, "LEMON", False)

xor_ciphertext = sec_xor_cipher("SecretMessage", "MySecretKey")
xor_recovered = sec_xor_cipher(xor_ciphertext, "MySecretKey")

# 3. Security Inspection & Forensics
token_data = sec_decode_jwt(jwt_token_string)
say "Token Subject: ", token_data["claims"]["sub"]

hex_representation = sec_hexdump("DoomScript Security Domain")
cvss_score = sec_cvss_score(8.0, 3.0, 2.0)
banner_info = sec_parse_banner("SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\\r\\n")
say "Detected Service: ", banner_info["service"], " Version: ", banner_info["version"]
```

---

### 22. Game Systems & Physics Simulation (`use game`)
Dice notation evaluation, loot tables, tilemaps, A* grid pathfinding, and turn resolution:

```doomscript
use game

# 1. Dice Rolling & Weighted Loot Generation
dice_result = game_roll_dice("2d6 + 3")
say "Rolled 2d6 + 3: ", dice_result

dropped_item = game_weighted_choice(["common_sword", "rare_bow", "legendary_staff"], [70, 25, 5])
say "Loot Drop: ", dropped_item

# 2. 2D Tilemap & A* Grid Pathfinding
tilemap = game_create_tilemap(10, 10, 0)
game_set_tile(tilemap, 3, 3, 1)  # 1 = Wall / Obstacle
path = game_astar_grid(tilemap, 0, 0, 8, 8)
has_los = game_has_line_of_sight(tilemap, 0, 0, 0, 8)

# 3. Turn-Based RPG Combat & Status Effects
attacker = Record({"name": "Warrior", "atk": 35, "hp": 120})
defender = Record({"name": "Dragon", "defense": 10, "hp": 250})
combat_round = game_resolve_turn(attacker, defender, 1.2)
say "Damage Dealt: ", combat_round["damage"], " Dragon HP: ", defender["hp"]

status_report = game_apply_status_effect(defender, "burn", 3, 15)
```

---

### 23. Quantum Computing & State Simulation (`use quantum`)
Statevector quantum registers, Hadamard, Pauli, CNOT gates, Bell state preparation, measurement:

```doomscript
use quantum

# 1. Quantum Register & Superposition
reg = quantum_create_register(2)
quantum_apply_h(reg, 0)         # Put qubit 0 into (|0> + |1>)/sqrt(2)
quantum_apply_cnot(reg, 0, 1)     # Entangle qubit 0 and qubit 1 into Bell state

# 2. Quantum State Vector & Measurement
bell_state = quantum_state_vector(reg)
say "Bell State Amplitudes: ", bell_state

# 3. Multi-Shot Quantum Circuit Sampling
measurement_counts = quantum_sample(reg, 1000)
say "Measurement Distribution: ", measurement_counts

# 4. Standard Bell States & Single Qubit Gates
phi_plus = quantum_bell_state("phi_plus")
reg_single = quantum_create_register(1)
quantum_apply_x(reg_single, 0)    # Pauli-X (NOT gate)
measured_bit = quantum_measure(reg_single, 0)
say "Measured Qubit State: ", measured_bit  # 1
```

---

### 24. Electrical Engineering & Circuit Analysis (`use circuit`)
Ohm's law, resistor color code bands, voltage dividers, 555 timers, logic gates, GPIO pins:

```doomscript
use circuit

# 1. Ohm's Law & Power
circuit_sol = circuit_ohms_law(None, 2.5, 10.0)  # voltage = None, current = 2.5A, resistance = 10 Ohm
say "Calculated Voltage: ", circuit_sol["voltage"], "V, Power: ", circuit_sol["power"], "W"

# 2. Resistor Color Band Decoding
resistor = circuit_resistor_bands("brown", "black", "red", "gold")
say "Resistance: ", resistor["resistance"], " Ohms, Tolerance: ±", resistor["tolerance"], "%"

# 3. Analog Electronics: Voltage Dividers & 555 Timers
vdiv = circuit_voltage_divider(12.0, 1000.0, 2000.0)
say "Output Voltage: ", vdiv["v_out"], "V"

timer = circuit_555_timer(1000.0, 2000.0, 0.000001)
say "555 Astable Frequency: ", timer["frequency"], " Hz, Duty Cycle: ", timer["duty_cycle"], "%"

rc_circuit = circuit_rc_time_constant(10000.0, 0.000001)
say "RC Time Constant (tau): ", rc_circuit["tau"], " seconds"

# 4. Digital Logic & Virtual GPIO
logic_val = circuit_eval_logic("XOR", [True, False])
effective_pwm = circuit_pwm_analog_value(75.0, 5.0)  # 75% duty cycle at 5V = 3.75V

gpio = circuit_create_gpio([1, 2, 3, 4])
circuit_set_pin(gpio, 2, 1)
pin_state = circuit_read_pin(gpio, 2)
```

---

### 25. Blockchain, Cryptographic Ledgers & Merkle Trees (`use chain`)
Merkle tree proofs, Proof-of-Work mining, UTXO transaction ledger, EIP-55 checksum addresses:

```doomscript
use chain

# 1. Cryptographic Merkle Tree & Inclusion Proofs
transactions = ["tx1_alice_to_bob_10", "tx2_bob_to_carol_5", "tx3_carol_to_dave_2"]
mt = chain_create_merkle_tree(transactions)
merkle_root = chain_get_merkle_root(mt)
say "Merkle Root: ", merkle_root

proof = chain_get_merkle_proof(mt, 0)
is_valid = chain_verify_merkle_proof(transactions[0], proof, merkle_root)
say "Inclusion Proof Valid: ", is_valid

# 2. Proof-of-Work Mining Simulation
block = chain_mine_pow_block(1, merkle_root, "0000000000000000", 2)
say "Mined Block Nonce: ", block["nonce"], " Hash: ", block["hash"]
pow_valid = chain_verify_pow_block(block, 2)

# 3. UTXO Transaction Ledger
ledger = chain_create_utxo_ledger()
# Genesis transaction
chain_add_utxo_tx(ledger, "tx_genesis", [], [Record({"address": "Alice", "amount": 100})])
# Spend transaction
chain_add_utxo_tx(ledger, "tx_spend", 
    [Record({"tx_id": "tx_genesis", "output_index": 0})], 
    [Record({"address": "Bob", "amount": 40}), Record({"address": "Alice", "amount": 60})])

alice_bal = chain_get_utxo_balance(ledger, "Alice")
bob_bal = chain_get_utxo_balance(ledger, "Bob")
say "Alice Balance: ", alice_bal, " Bob Balance: ", bob_bal

# 4. Ethereum EIP-55 Checksum Address
eip55_address = chain_eip55_address("0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359")
say "Checksummed Address: ", eip55_address
```

### 26. 3D Mathematics & Geometric Algebra (`use math3d`)
Vectors, 4x4 Transformation Matrices, Quaternions, SLERP interpolation, and Ray-AABB collision testing:

```doomscript
use math3d

# 1. 3D Vector Math
v1 = math3d_vec3(1.0, 0.0, 0.0)
v2 = math3d_vec3(0.0, 1.0, 0.0)
cross_prod = math3d_vec3_cross(v1, v2)
dot_prod = math3d_vec3_dot(v1, v2)
norm_v = math3d_vec3_normalize(cross_prod)

# 2. 4x4 Matrices (Perspective & Look-At)
proj_mat = math3d_mat4_perspective(60.0, 1.777, 0.1, 1000.0)
view_mat = math3d_mat4_look_at(math3d_vec3(0, 5, 10), math3d_vec3(0, 0, 0), math3d_vec3(0, 1, 0))
mvp = math3d_mat4_multiply(proj_mat, view_mat)

# 3. Quaternions & Spherical Linear Interpolation (SLERP)
q_start = math3d_quat_from_euler(0, 0, 0)
q_end = math3d_quat_from_euler(0, 90, 0)
q_mid = math3d_quat_slerp(q_start, q_end, 0.5)

# 4. Ray-AABB Intersection
hit = math3d_ray_aabb_intersect(
    ray_origin=math3d_vec3(0, 0, -5),
    ray_dir=math3d_vec3(0, 0, 1),
    box_min=math3d_vec3(-1, -1, -1),
    box_max=math3d_vec3(1, 1, 1)
)
say "Ray Hit Box: ", hit["hit"], " at distance: ", hit["distance"]
```

---

### 27. Compiler Engineering & Abstract Syntax Trees (`use compiler`)
Pure-Python Lexing, AST Parsing, Constant Folding Optimizer, and Bytecode Evaluation:

```doomscript
use compiler

source_code = "let total = (10 + 20) * 3"

# 1. Tokenization / Lexer
tokens = compiler_tokenize(source_code)
say "Tokens Count: ", len(tokens)

# 2. AST Parsing
ast_tree = compiler_parse(tokens)

# 3. Constant Folding Optimizer
optimized_ast = compiler_optimize_ast(ast_tree)

# 4. Tree-Walk Evaluation / Execution
result_env = compiler_evaluate(optimized_ast)
say "Total Result: ", result_env["total"]
```

---

### 28. Robotics, Kinematics & Motion Planning (`use robotics`)
Denavit-Hartenberg (DH) Forward Kinematics, Planar Inverse Kinematics, PID Controllers, Trapezoidal Velocity Profiles, and A* Path Planning:

```doomscript
use robotics

# 1. Forward Kinematics (DH Table)
dh_params = [
    Record({"theta": 0.0, "d": 0.0, "a": 1.0, "alpha": 0.0}),
    Record({"theta": 1.5707, "d": 0.0, "a": 1.0, "alpha": 0.0})
]
ee_pos = robotics_forward_kinematics(dh_params)
say "End-Effector Coordinates: ", ee_pos

# 2. Planar Inverse Kinematics (2-Link Arm)
angles = robotics_inverse_kinematics_2link(1.0, 1.0, target_x=1.0, target_y=1.0)
say "Joint Angles (rad): ", angles["theta1"], ", ", angles["theta2"]

# 3. Closed-Loop PID Controller
pid = robotics_create_pid(kp=2.0, ki=0.5, kd=0.1, setpoint=100.0)
control_out = robotics_update_pid(pid, current_measurement=95.0, dt=0.01)

# 4. A* Grid Motion Planning
grid = [
    [0, 0, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 0, 0]
]
path = robotics_astar_grid(grid, start=[0, 0], goal=[2, 3])
say "Obstacle-Free Path: ", path
```

---

### 29. Digital Signal Processing & Communications (`use signals`)
Radix-2 Cooley-Tukey FFT/IFFT, FIR/IIR Biquad Filtering, Spectral Windowing, and Goertzel Tone Detection:

```doomscript
use signals

# Generate 50Hz test signal sampled at 1000Hz
signal_data = [math.sin(2.0 * math.pi * 50.0 * (i / 1000.0)) for i in range(128)]

# 1. Spectral Windowing (Hann, Hamming, Blackman)
windowed = signals_apply_window(signal_data, window_type="hann")

# 2. Fast Fourier Transform (FFT)
spectrum = signals_fft(windowed)
dominant_freq = signals_dominant_frequency(spectrum, sample_rate=1000)
say "Dominant Spectral Frequency: ", dominant_freq, " Hz"

# 3. Biquad IIR Low-Pass Filter
filtered = signals_biquad_lowpass(signal_data, cutoff_hz=30.0, sample_rate=1000.0, q=0.707)

# 4. Goertzel Single-Tone Detection (DTMF decoding)
tone_power = signals_goertzel_detect(signal_data, target_freq=50.0, sample_rate=1000)
say "Goertzel Tone Magnitude: ", tone_power
```

---

### 30. Astronomy & Orbital Mechanics (`use astronomy`)
Julian Date calculations, Keplerian Orbits to Cartesian Vectors, Hohmann Transfer Delta-v, and Celestial Coordinate Transformations:

```doomscript
use astronomy

# 1. Julian Date
jd = astro_julian_date(year=2026, month=10, day=20, hour=12, minute=0, second=0)
say "Julian Date: ", jd

# 2. Keplerian Orbit to Cartesian State (r, v)
state = astro_kepler_to_cartesian(
    semi_major_axis_km=7000.0,
    eccentricity=0.01,
    inclination_deg=28.5,
    raan_deg=45.0,
    arg_pe_deg=10.0,
    true_anomaly_deg=90.0,
    mu=398600.4418  # Earth standard gravitational parameter
)
say "Orbital Position (km): ", state["r"], " Velocity (km/s): ", state["v"]

# 3. Hohmann Orbital Transfer Delta-V
hohmann = astro_hohmann_transfer(r1_km=7000.0, r2_km=42164.0, mu=398600.4418)
say "Total Delta-v to GEO: ", hohmann["delta_v_total"], " km/s"

# 4. Equatorial to Horizontal (Alt-Azimuth) Conversion
horiz = astro_equatorial_to_horizontal(ra_hours=5.588, dec_deg=-5.39, lat_deg=37.77, lst_hours=6.0)
say "Target Altitude: ", horiz["altitude_deg"], " Azimuth: ", horiz["azimuth_deg"]
```

---

### 31. Computational Chemistry & Cheminformatics (`use chem`)
SMILES String Parsing, Molecular Formula Weights, Hückel Aromaticity Testing, and Chemical Reaction Equation Balancing:

```doomscript
use chem

# 1. Parse SMILES Molecular Graph
mol = chem_parse_smiles("c1ccccc1")  # Benzene
say "Atom Count: ", chem_atom_count(mol)

# 2. Molecular Formula Weight
mw = chem_formula_weight("C6H12O6")  # Glucose
say "Glucose Molecular Weight: ", mw, " g/mol"

# 3. Hückel Aromaticity Check (4n + 2 pi-electrons)
is_aromatic = chem_is_aromatic(mol)
say "Is Benzene Aromatic: ", is_aromatic

# 4. Balance Chemical Reaction Equations (Nullspace Solver)
# Combust methane: CH4 + O2 -> CO2 + H2O
balanced = chem_balance_reaction("CH4 + O2 -> CO2 + H2O")
say "Balanced Equation: ", balanced["equation"]
# Outputs: "1 CH4 + 2 O2 -> 1 CO2 + 2 H2O"
```

---

### 32. Data Compression & Information Theory (`use compression`)
Canonical Huffman Trees, LZ77 Sliding Window, LZW Coding, Rational Arithmetic Coding, and Shannon Entropy:

```doomscript
use compression

raw_data = "TOBEORNOTTOBEORTOBEORNOT"

# 1. Shannon Entropy
entropy = compression_shannon_entropy(raw_data)
say "Shannon Entropy (bits/char): ", entropy

# 2. Canonical Huffman Prefix Coding
huffman_encoded = compression_huffman_encode(raw_data)
huffman_decoded = compression_huffman_decode(huffman_encoded)
say "Huffman Match: ", raw_data == huffman_decoded

# 3. LZ77 Sliding Window Compression
lz77_tokens = compression_lz77_encode(raw_data, window_size=20)
lz77_decomp = compression_lz77_decode(lz77_tokens)
say "LZ77 Match: ", raw_data == lz77_decomp

# 4. LZW Dictionary Compression
lzw_codes = compression_lzw_encode(raw_data)
lzw_decomp = compression_lzw_decode(lzw_codes)
say "LZW Match: ", raw_data == lzw_decomp
```

---

### 33. Time Series Forecasting & Decomposition (`use time_series`)
STL Additive/Multiplicative Decomposition, Sample ACF/PACF (Durbin-Levinson), and Holt-Winters Triple Exponential Smoothing:

```doomscript
use time_series

# Synthetic monthly data with trend and seasonal pattern
series = [10.0 + i * 0.5 + (10.0 if i % 4 == 0 else 0.0) for i in range(32)]

# 1. Classical STL Decomposition
decomp = ts_decompose(series, period=4, model="additive")
say "Trend Component: ", decomp["trend"][:4]
say "Seasonal Component: ", decomp["seasonal"][:4]

# 2. Autocorrelation (ACF) & Partial Autocorrelation (PACF)
acf_vals = ts_acf(series, nlags=8)
pacf_vals = ts_pacf(series, nlags=8)

# 3. Holt-Winters Triple Smoothing (Level, Trend, Seasonality)
hw = ts_holt_winters(series, period=4, alpha=0.3, beta=0.1, gamma=0.2)
forecast = hw.forecast(steps=4)
say "Forecast Next 4 Periods: ", forecast
```

---

### 34. Computer Algebra & Symbolic Mathematics (`use symbolic`)
Pure-Python CAS, Analytical Symbolic Differentiation, Algebraic Simplification, and Polynomial GCD:

```doomscript
use symbolic

# 1. Parse Symbolic Expressions
expr = sym_parse("x^3 + 3*x^2 + 3*x + 1")

# 2. Analytical Symbolic Differentiation
# d/dx (x^3 + 3*x^2 + 3*x + 1) = 3*x^2 + 6*x + 3
deriv = sym_diff(expr, "x")
say "Derivative: ", sym_to_string(deriv)

# 3. Algebraic Simplification
simplified = sym_simplify(deriv)
say "Simplified: ", sym_to_string(simplified)

# 4. Symbolic Function Evaluation
val_at_2 = sym_eval(expr, {"x": 2})  # (2 + 1)^3 = 27
say "Value at x=2: ", val_at_2

# 5. Polynomial Greatest Common Divisor (GCD)
poly_gcd = sym_poly_gcd("x^2 - 1", "x^2 + 2*x + 1")
say "Polynomial GCD: ", sym_to_string(poly_gcd)
```

---

### 35. Software Rasterization & 3D Computer Graphics (`use graphics`)
RGBA FrameBuffer, Z-DepthBuffer, Bresenham Lines, Midpoint Circles, Gouraud Triangles, and BMP/PPM Export:

```doomscript
use graphics

# 1. Create 256x256 RGBA FrameBuffer with Depth Buffer
fb = gfx_create_framebuffer(width=256, height=256, bg_color=[20, 20, 30, 255])
db = gfx_create_depthbuffer(width=256, height=256)

# 2. Draw Bresenham Lines & Midpoint Circles
gfx_draw_line(fb, x0=10, y0=10, x1=240, y1=240, color=[255, 200, 0, 255])
gfx_draw_circle(fb, cx=128, cy=128, radius=50, color=[0, 255, 200, 255], fill=False)

# 3. Rasterize Gouraud-Shaded 3D Triangle with Z-Buffering
v0 = Record({"x": 128, "y": 30, "z": 0.5, "r": 255, "g": 0, "b": 0})
v1 = Record({"x": 30, "y": 200, "z": 0.2, "r": 0, "g": 255, "b": 0})
v2 = Record({"x": 220, "y": 200, "z": 0.8, "r": 0, "g": 0, "b": 255})
gfx_rasterize_triangle_gouraud(fb, db, v0, v1, v2)

# 4. Save Image to Disk
gfx_save_bmp(fb, "render.bmp")
gfx_save_ppm(fb, "render.ppm")
```

---

### 36. Telecommunications & Error-Correcting Codes (`use telecom`)
Hamming(7,4) Single-Error Correction, CRC Checks (CRC-8/16/32/64), Galois Field $GF(2^8)$ Arithmetic, and Reed-Solomon RS(n, k) Codes:

```doomscript
use telecom

# 1. Hamming(7,4) Single-Bit Error Correction
data_bits = [1, 0, 1, 1]
encoded_7bit = telecom_hamming74_encode(data_bits)
# Introduce bit corruption on transmission
corrupted = list(encoded_7bit)
corrupted[2] ^= 1  # Flip 3rd bit
corrected_bits, had_error = telecom_hamming74_decode(corrupted)
say "Hamming Repaired: ", corrected_bits == data_bits

# 2. Cyclic Redundancy Checks (CRC)
crc32_val = telecom_crc32(b"Mission-Critical Network Packet")
say "CRC32 Checksum: ", hex(crc32_val)

# 3. Galois Field GF(2^8) Arithmetic
product = telecom_gf256_mul(0x57, 0x83)
say "Galois Field Product: ", hex(product)

# 4. Reed-Solomon RS(n, k) Codec (Berlekamp-Massey + Forney)
rs_block = telecom_rs_encode(b"HELLO WORLD", num_ecc=4)
# Corrupt up to 2 arbitrary bytes
rs_corrupted = bytearray(rs_block)
rs_corrupted[1] ^= 0xFF
rs_corrupted[4] ^= 0xAA
rs_repaired = telecom_rs_decode(bytes(rs_corrupted), num_ecc=4)
say "Reed-Solomon Repaired: ", rs_repaired == b"HELLO WORLD"
```

---

### 37. Computational Neuroscience & Spiking Neural Networks (`use neuro`)
Leaky Integrate-and-Fire (LIF) Neurons, Izhikevich Cortical Neurons, STDP Hebbian Plasticity, and Poisson Spike Trains:

```doomscript
use neuro

# 1. Leaky Integrate-and-Fire (LIF) Neuron
lif = neuro_lif_neuron(tau_m=20.0, v_rest=-70.0, v_reset=-75.0, v_thresh=-55.0)
v_mem, did_spike = neuro_update_lif(lif, current_inj=15.0, dt=1.0)
say "LIF Membrane: ", v_mem, " mV (Spiked: ", did_spike, ")"

# 2. Izhikevich Cortical Neuron (Regular Spiking, Chattering, Fast Spiking)
izhi = neuro_izhikevich_neuron(a=0.02, b=0.2, c=-65.0, d=8.0)
izhi_spikes = neuro_simulate_izhikevich(izhi, current_inj=10.0, duration_ms=100.0, dt=0.5)
say "Spikes in 100ms: ", len(izhi_spikes)

# 3. Spike-Timing-Dependent Plasticity (STDP) Synapse
delta_w = neuro_stdp_update(pre_spike_t=10.0, post_spike_t=15.0, a_pos=0.01, a_neg=0.012, tau=20.0)
say "STDP Synaptic Weight Change: ", delta_w  # Positive (LTP) because pre fired before post

# 4. Poisson Spike Train
spike_times = neuro_poisson_spike_train(rate_hz=50.0, duration_sec=1.0)
say "Generated Spikes: ", len(spike_times)
```

---

### 38. Formal Automata & Computation Theory (`use automata`)
Deterministic Finite Automata (DFA), Hopcroft State Minimization, Thompson Regex-to-NFA, and Universal Turing Machines:

```doomscript
use automata

# 1. Deterministic Finite Automaton (DFA)
dfa = automata_create_dfa(
    states=["q0", "q1"],
    alphabet=["0", "1"],
    transitions={"q0": {"0": "q0", "1": "q1"}, "q1": {"0": "q0", "1": "q1"}},
    start_state="q0",
    accept_states=["q1"]
)
accepted = automata_dfa_accepts(dfa, "1011")
say "DFA Accepts '1011' (ends in 1): ", accepted

# 2. Hopcroft State Minimization
min_dfa = automata_minimize_dfa(dfa)
say "Minimised DFA State Count: ", len(min_dfa["states"])

# 3. Thompson's Construction: Regex to NFA
nfa = automata_regex_to_nfa("(a|b)*abb")
say "NFA Recognizes 'aabb': ", automata_nfa_accepts(nfa, "aabb")

# 4. Universal Turing Machine Simulator (Binary Incrementer)
tm = automata_create_turing_machine(
    states=["q_seek", "q_carry", "q_done"],
    transitions={
        ("q_seek", "1"): ("q_seek", "1", "R"),
        ("q_seek", "0"): ("q_seek", "0", "R"),
        ("q_seek", "B"): ("q_carry", "B", "L"),
        ("q_carry", "1"): ("q_carry", "0", "L"),
        ("q_carry", "0"): ("q_done", "1", "N"),
        ("q_carry", "B"): ("q_done", "1", "N")
    },
    start_state="q_seek",
    accept_state="q_done"
)
tape_res = automata_run_turing_machine(tm, tape="1011")  # 11 + 1 = 12 ("1100")
say "Turing Machine Output Tape: ", tape_res["tape"]
```

---

### 39. Metrics, Telemetry & Observability (`use metrics`)
Prometheus/OpenMetrics Counters, Gauges, Histograms, Quantile Reservoirs, Distributed Tracing Spans, and Text Exporter:

```doomscript
use metrics

# 1. Counters & Gauges
metrics_counter_inc("http_requests_total", labels={"method": "GET", "status": "200"})
metrics_counter_add("bytes_transmitted_total", 4096)
metrics_gauge_set("active_workers", 8)

# 2. Histograms & Quantile Percentiles (p50, p90, p95, p99)
metrics_histogram_observe("request_duration_ms", 12.5)
metrics_histogram_observe("request_duration_ms", 45.2)
metrics_histogram_observe("request_duration_ms", 8.1)
quantiles = metrics_get_quantiles("request_duration_ms")
say "Latency p50: ", quantiles["p50"], " p99: ", quantiles["p99"]

# 3. Distributed Tracing Spans
span = metrics_start_span("database_query", trace_id="trace_abc123")
# ... execute operation ...
metrics_end_span(span, tags={"db.table": "orders", "db.rows": 120})

# 4. Export OpenMetrics / Prometheus Scrape Payload
scrape_text = metrics_export_openmetrics()
say "Prometheus Scrape Output:\n", scrape_text
```

---

### 40. Spatial Audio & Acoustic Simulation (`use spatial_audio`)
Binaural Woodworth ITD/ILD 3D Spatialization, First-Order Ambisonics $B$-Format, Doppler Frequency Shifts, and Schroeder Algorithmic Reverberation:

```doomscript
use spatial_audio

# 1. Binaural 3D Audio (Interaural Time & Level Differences)
mono_sound = [math.sin(2.0 * math.pi * 440.0 * (i / 44100.0)) for i in range(1000)]
binaural_stereo = audio_spatialize_binaural(
    mono_sound,
    source_azimuth_deg=45.0,    # Source at 45 degrees to the right
    source_elevation_deg=0.0,
    source_dist_m=2.0,
    sample_rate=44100
)
say "Left Ear Samples: ", len(binaural_stereo["left"]), " Right Ear: ", len(binaural_stereo["right"])

# 2. First-Order Ambisonics B-Format Encoding (W, X, Y, Z)
b_format = audio_encode_ambisonics(mono_sound, azimuth_deg=30.0, elevation_deg=15.0)
say "Ambisonic Components: W, X, Y, Z channels ready for 360-degree decoding"

# 3. Doppler Frequency Shift for Moving Audio Sources
doppler_samples = audio_apply_doppler(
    mono_sound,
    source_velocity_mps=30.0,   # Moving toward listener at 30 m/s
    speed_of_sound_mps=343.0,
    sample_rate=44100
)

# 4. Schroeder Algorithmic Reverberation (Comb + All-Pass filters)
reverbed = audio_schroeder_reverb(mono_sound, rt60_sec=1.5, sample_rate=44100)
say "Reverberation Processed: ", len(reverbed), " samples"
```

---

---

---

## 6. Cross-Domain Orchestration & Production Pipelines

DoomScript allows you to seamlessly combine multiple domains into single, fluid pipelines. No glue code or manual data conversion required.

### Example 1: Full-Stack Financial Risk & NLP Sentiment Analysis

```doom
use finance, nlp, data, office

# 1. Ingest financial news and stock prices
read csv file "market_feed.csv" into market_data
read file "earnings_call.txt" into transcript

# 2. Extract market sentiment from speech transcript
nlp extract sentiment from transcript into call_sentiment
say "Executive sentiment score:", call_sentiment's polarity

# 3. Compute Value-at-Risk (VaR) and Sharpe ratio
set returns to market_data's daily_return
finance compute var 95 on returns into portfolio_var
finance compute sharpe ratio on returns with rf 0.02 into sharpe

# 4. Generate executive summary PDF
office create pdf "risk_report.pdf" with title "Q4 Portfolio Risk & Sentiment"
office add paragraph "Portfolio VaR (95%): " + str(portfolio_var)
office add paragraph "Sharpe Ratio: " + str(sharpe)
office add paragraph "Earnings Sentiment: " + str(call_sentiment's polarity)
office save document

say "Executive risk report generated successfully!"
```

---

### Example 2: Autonomous Robotics & Geospatial Route Optimization

```doom
use geo, robotics, opt, db

# 1. Load warehouse delivery waypoints from database
db connect "logistics.db" into db_conn
db query "SELECT lat, lon, package_id FROM pending_deliveries" into waypoints

# 2. Plan collision-free 3D trajectory
set start_pos to [0.0, 0.0, 0.0]
set target_pos to [150.0, 320.0, 25.0]
robotics plan trajectory from start_pos to target_pos into drone_path

# 3. Optimize traveling salesperson delivery route
opt solve tsp on waypoints using simulated_annealing into optimal_route

# 4. Execute drone telemetry loop
for each stop in optimal_route:
    say "Navigating drone to waypoint:", stop's package_id
```


---

## 7. Deepened Multi-Domain Algorithms & Reference (Clusters A–H)

DoomScript bundles production-grade, zero-dependency implementations of essential algorithms across 8 clusters covering all 40 domains:

### Cluster A: Foundational Computing & Systems
- **`dsa`**:
  - `FibonacciHeap`: Amortized $O(1)$ `insert` and `decrease_key`, $O(\log n)$ `extract_min` with cascading cuts.
  - `DisjointSetUnion`: Path compression and union-by-rank with transactional checkpoints and rollback.
  - `FenwickTree` / `FenwickTree2D`: 1D and 2D Binary Indexed Trees for $O(\log n)$ prefix sums and point updates.
  - `BloomFilter` / `CountingBloomFilter`: Probabilistic set membership with zero false negatives and item deletion support.
- **`graph`**:
  - `graph_tarjan_scc`: Strongly Connected Components discovery using low-link values and traversal stack.
  - `graph_hopcroft_karp`: Maximum Cardinality Bipartite Matching in $O(E \sqrt{V})$ via alternating BFS/DFS level graphs.
  - `graph_eulerian_path`: Hierholzer's algorithm finding Eulerian paths and circuits in directed graphs.
  - `graph_boruvka_mst`: Parallel-friendly Minimum Spanning Tree via connected component contractive edge contraction.
- **`compiler`**:
  - `LALR1Parser`: Full LR(1) item-set generation, LALR core collapsing, parsing table construction, and shift-reduce stack engine.
  - `SSAFormBuilder`: Dominator tree computation, dominance frontiers, and $\phi$-node insertion.
  - `ChaitinRegisterAllocator`: K-coloring of register interference graphs with Briggs/Chaitin degree reduction and spilling.
- **`automata`**:
  - `PushdownAutomaton`: Context-free language parser with stack configuration transitions.
  - `MooreMealyFSM`: Finite State Machines with state-dependent (Moore) and transition-dependent (Mealy) output functions.
  - `BuchiAutomaton`: Omega-automaton recognizing infinite $\omega$-regular words with non-empty cycle acceptance.
- **`net`**:
  - `TLS13ClientHelloParser`: Pure binary parser extracting TLS 1.3 ClientHello SNI extensions and supported cipher suites.
  - `SOCKS5Protocol`: RFC 1928 proxy handshake simulation, IP/Domain address decoding, and reply packets.
  - `CIDRPrefixTrie`: Bitwise radix trie for $O(32)$ and $O(128)$ longest prefix IP route matching.

### Cluster B: Machine Learning, AI & Optimization
- **`ml`**:
  - `LinearSVM`: Sequential Minimal Optimization (SMO) algorithm solving dual SVM with Mercer kernels.
  - `KMeansPlusPlus`: Arthur-Vassilvitskii $D^2$ seeding with Lloyd's clustering convergence.
  - `TinyConvNet`: 2D Convolution, Max-Pooling, Flatten, Dense layers with backpropagation.
  - `GradientBoostedTreesExact`: Exact greedy split search on second-order Taylor expansion loss gradients.
- **`agent`**:
  - `ReActAgent`: Interleaved Thought, Action, and Observation cycles with structured tool dispatching.
  - `TreeOfThoughts`: BFS/DFS exploration of reasoning trees with heuristic node evaluation.
  - `MultiAgentDebate`: Multi-perspective adversarial debate with judge consensus synthesis.
- **`opt`**:
  - `PrimalDualInteriorPoint`: Mehrotra predictor-corrector barrier method for linear programming.
  - `BranchAndBoundMILP`: Mixed-Integer Linear Programming tree search with relaxation bounds.
  - `AdaptiveSimulatedAnnealing`: Dynamic temperature cooling and adaptive step variance.
- **`sim`**:
  - `AgentBasedModel2D`: Spatial 2D toroidal multi-agent simulation with neighborhood radius interactions.
  - `MCMCSampler`: Metropolis-Hastings Markov Chain Monte Carlo sampling from target log-density functions.
  - `JacksonQueuingNetwork`: Closed and open multi-station queuing networks with routing transition matrices.
- **`nlp`**:
  - `BytePairEncoder`: Subword tokenization via iterative frequency pair merging.
  - `HMMPOSTagger`: First-order Hidden Markov Model with Viterbi dynamic programming decoding.
  - `Word2VecCBOW`: Continuous Bag-of-Words embeddings with negative sampling and Adam/SGD updates.

### Cluster C: Mathematics, 3D & Scientific Computing
- **`math3d`**:
  - `Raymarcher3D`: Sphere tracing over signed distance field (SDF) CSG geometries.
  - `DualQuaternion`: Rigid body transformations with screw linear interpolation (ScLERP).
  - `Quickhull3D`: 3D convex hull construction using facet horizon ridge stitching.
- **`symbolic`**:
  - `SymbolicIntegrator`: Pattern and polynomial symbolic anti-differentiation.
  - `TaylorSeries`: Arbitrary-order polynomial Taylor expansions around expansion point $x_0$.
  - `ExactRationalLinearSolver`: Zero-loss Gaussian elimination using exact rational fractions.
- **`signals`**:
  - `STFTSpectrogram`: Short-Time Fourier Transform with overlapping Hann windows.
  - `SavitzkyGolayFilter`: Polynomial smoothing and derivative estimation preserving high-frequency features.
- **`research`**:
  - `RungeKuttaFehlberg`: Adaptive step size ODE integration (RKF45) with embedded 4th/5th order error estimates.
  - `LevenbergMarquardtOptimizer`: Damped non-linear least squares parameter fitting.
- **`graphics`**:
  - `BlinnPhongShader`: Specular half-vector illumination with ambient and diffuse components.
  - `BilinearTextureMapper`: Sub-pixel texture interpolation with boundary clamp modes.
  - `SuperSampledFrameBuffer`: SSAA anti-aliased software rasterization frame buffer.

### Cluster D: Physical Sciences & Hardware
- **`physics`**:
  - `BarnesHutNBody`: $O(N \log N)$ gravitational and electrostatic n-body simulation using octrees.
  - `ImpulseCollision2D`: Rigid-body momentum conservation with restitution and friction impulses.
  - `VanDerWaalsGas`: Non-ideal real gas thermodynamic equation of state simulation.
- **`chem`**:
  - `MolecularGraphLayout`: 2D chemical structure force-directed coordinate generation.
  - `MorganFingerprint`: Extended-connectivity circular fingerprints (ECFP) for chemical similarity.
  - `ReactionKineticsSimulator`: Numerical chemical ODE rate equations under Arrhenius temperature dependence.
- **`bio`**:
  - `SequenceAligner`: Gotoh affine gap penalty dynamic programming (Smith-Waterman / Needleman-Wunsch).
  - `FMIndexBWT`: Burrows-Wheeler Transform with suffix array and LF-mapping for exact genomic substring matching.
  - `PhylogeneticTreeNJ`: Saitou-Nei Neighbor-Joining algorithm building additive phylogenetic evolutionary trees.
- **`astronomy`**:
  - `PlanetaryEphemeris`: Keplerian orbital elements and secular rates for inner and outer solar system bodies.
  - `EclipsePredictor`: Solar and lunar eclipse geometry detection based on lunar nodal conjunctions.
  - `AtmosphericRefraction`: Bennett 1982 empirical formula correcting apparent celestial altitude.
- **`circuit`**:
  - `ModifiedNodalAnalysis`: DC and transient circuit solver supporting resistors, capacitors, inductors, and diodes.
  - `BodePlotAnalyzer`: Transfer function frequency response calculation (magnitude in dB and phase in degrees).
  - `OpAmpModel`: Finite gain and bandwidth non-inverting and inverting operational amplifier model.

### Cluster E: Media, Spatial & Game Systems
- **`image`**:
  - `GeometricWarp`: $3 \times 3$ affine homography matrix inversion and bilinear backward mapping.
  - `MorphologicalOps`: Binary and grayscale erosion, dilation, morphological opening, and closing.
  - `ColorQuantizer`: Median Cut color quantization with Floyd-Steinberg error diffusion dithering.
- **`audio`**:
  - `PolyphonicSynth`: Polyphonic synthesizer with band-limited PolyBLEP oscillators and 4-stage ADSR envelope.
  - `YINPitchDetector`: Fundamental frequency autocorrelation difference function pitch detection.
  - `ParametricEQ`: Audio EQ cascade of biquad second-order IIR filters (low-pass, high-pass, peaking band).
- **`spatial_audio`**:
  - `HigherOrderAmbisonics`: 2nd-order 9-channel ACN/N3D spherical harmonics encoding and binaural decoding.
  - `AcousticRaytracer`: Image-source method for room impulse response (RIR) synthesis.
  - `HRTFConvolution`: Head-Related Transfer Function spatial audio filtering.
- **`game`**:
  - `BehaviorTree`: Composite nodes (Sequence, Selector), Decorators (Inverter, Repeater), and leaf tasks with Blackboard memory.
  - `SteeringBehaviors`: Craig Reynolds autonomous agent steering (Seek, Flee, Arrive, Pursue, Evade, Flocking).
  - `TilemapPhysics`: 2D AABB tilemap collision detection, slope tiles, and grid raycasting.
- **`metrics`**:
  - `OTLPTraceExporter`: OpenTelemetry Protocol JSON trace span payload exporter.
  - `ExponentialDecayReservoir`: Forward-decaying Cormode-Hadley quantile reservoir.
  - `EWMAAnomalyDetector`: Exponentially weighted moving average with dynamic 3-sigma confidence bounds.

### Cluster F: Data, Storage & Telecommunications
- **`data`**:
  - `RollingAggregator`: Monotonic double-ended queue sliding-window min, max, mean, and standard deviation in $O(1)$.
  - `RelationalJoinEngine`: In-memory Hash Join, Sort-Merge Join, and Nested Loop Join with hash partitioning.
  - `PivotTableEngine`: Multi-index grouping, pivoting, and unpivoting (melt) transformations.
- **`office`**:
  - `SpreadsheetFormulaEngine`: Recursive descent formula parser with dependency DAG cycle detection and dirty-cell recomputation.
  - `CSVDialectSniffer`: Auto-detection of delimiter, quote character, and escape sequences.
- **`cloud`**:
  - `MultipartUploadManager`: S3-style chunked upload simulation with part numbering, SHA-256 ETag hashing, and assembly.
  - `ContentAddressableStorage`: SHA-256 deduplicated block store with manifest indexing.
  - `BucketLifecycleEngine`: Time-based transition and expiration policy evaluator.
- **`compression`**:
  - `BWTCompressor`: Burrows-Wheeler Transform + Move-To-Front (MTF) + Run-Length Encoding.
  - `DeflateEngine`: RFC 1951 DEFLATE compressor combining LZ77 window search and canonical Huffman coding.
  - `ByteAlignedSnappy`: Fast byte-aligned dictionary LZ-style compressor.
- **`telecom`**:
  - `ViterbiDecoder`: Convolutional code $(2, 1, 7)$ trellis maximum-likelihood decoder.
  - `QAMModem`: BPSK, QPSK, 16-QAM, 64-QAM Gray-coded constellation mapper and demapper with AWGN simulation.
  - `OFDMFramer`: Orthogonal Frequency Division Multiplexing symbol subcarrier mapping and cyclic prefix insertion.

### Cluster G: Finance, Time Series & Distributed Ledgers
- **`finance`**:
  - `AnalyticalGreeks`: Exact Black-Scholes partial derivatives ($\Delta, \Gamma, \Theta, \mathcal{V}, \rho$).
  - `BinomialCoxRossRubinstein`: Multi-step lattice pricing model for American call and put options with early exercise.
  - `MarkowitzOptimizer`: Quadratic programming efficient frontier and tangency portfolio Sharpe ratio maximization.
- **`time_series`**:
  - `ARIMASimulator`: Autoregressive Integrated Moving Average $(p, d, q)$ data generation and parameter estimation.
  - `DynamicTimeWarping`: Non-linear sequence alignment distance with Sakoe-Chiba band constraints.
  - `CUSUMDetector`: Cumulative Sum statistical quality control change point detection.
- **`chain`**:
  - `PatriciaMerkleTrie`: Ethereum-style hex-encoded radix tree with branch, extension, and leaf nodes with Keccak-256 / SHA-256 proofs.
  - `SchnorrZKProtocol`: Non-interactive zero-knowledge proof of discrete logarithm knowledge via Fiat-Shamir heuristic.
  - `RaftConsensusEngine`: State machine replication simulation (leader election, log replication, commit index).
- **`quantum`**:
  - `QuantumErrorCorrection`: Shor 9-qubit bit/phase flip code and Steane 7-qubit CSS code syndrome measurement and recovery.
  - `GroverSearch`: Amplitude amplification oracle and diffusion operator simulation with quadratic speedup.
  - `QuantumTeleportation`: Bell state entanglement generation, EPR pair measurement, and quantum state reconstruction.
- **`sec`**:
  - `ShamirSecretSharing`: $(k, n)$ threshold secret sharing using Lagrange polynomial interpolation over prime fields.
  - `TOTPGenerator`: Time-based and HMAC-based One-Time Passwords (RFC 6238 / RFC 4226) with drift tolerance.
  - `Secp256k1Curve`: Elliptic Curve arithmetic (point addition, doubling, scalar multiplication) and ECDH key exchange.

### Cluster H: Web, Database & Brain / Neuroscience
- **`web`**:
  - `CSSSelectorEngine`: Recursive DOM traversal matching tag, class (`.btn`), id (`#main`), child (`>`), descendant (` `), and attribute (`[data-x=y]`).
  - `RFC6265CookieJar`: Multi-domain, path-scoped, secure/httponly, and expiration-aware HTTP cookie management.
  - `RobotsTxtParser`: Robots Exclusion Protocol parser evaluating user-agent rules, disallow/allow paths, and crawl-delay directives.
- **`db`**:
  - `WALCrashRecovery`: ARIES-style Write-Ahead Logging with redo/undo passes and checkpointing.
  - `CostBasedQueryOptimizer`: Estimator selecting index scan vs sequential table scan based on selectivity and page I/O costs.
  - `SnapshotIsolationMVCC`: Multi-Version Concurrency Control with transaction read timestamps and conflict rollback.
- **`neuro`**:
  - `TsodyksMarkramSynapse`: Dynamic short-term depression and facilitation model with utilization and recovery time constants.
  - `FitzHughNagumoNeuron`: Two-variable phase-plane biological excitable membrane model.
  - `WinnerTakeAllNetwork`: Competitive lateral inhibitory neuronal population model.
- **`geo`**:
  - `DelaunayTriangulator`: Bowyer-Watson incremental algorithm for 2D Delaunay triangulation and Voronoi diagram dual.
  - `WebMercatorProjection`: EPSG:3857 $\leftrightarrow$ EPSG:4326 coordinate transforms and Slippy map tile $(x, y, z)$ math.
  - `IsochroneContour`: Breadth-first travel-time contour generator over spatial road networks.

---

## 8. Production Deployment, PyPI Ecosystem & FAQ

### 100% Bidirectional Python Interoperability

DoomScript is a first-class citizen in the Python ecosystem:

#### 1. Calling PyPI Packages from DoomScript
Use any Python module (PyTorch, Pandas, Scikit-Learn, FastAPI) directly inside your `.doom` script:

```doom
use python module math
use python module torch as th

say "Square root of 144:", math.sqrt(144)
tensor = th.zeros([3, 3])
say "PyTorch Tensor:", tensor
```

#### 2. Embedding DoomScript Inside Existing Python Code
Import and run DoomScript logic from standard Python applications:

```python
from doomscript import execute, compile_to_ast

# Execute DoomScript code directly from Python
env = execute('''
set x to 10
set y to 20
what is x + y into total
''')

print("Result from DoomScript:", env["total"])  # 30
```

---

### Compiling to Native Standalone Binaries (`doom build`)

To ship your application to end users without requiring them to install Python or DoomScript:

```bash
# Windows creates standalone .exe:
doom build app.doom -o dist/app.exe

# Linux creates standalone ELF executable:
doom build app.doom -o dist/app
```

The resulting executable bundles the Python AST runtime into a single, self-contained binary file.

---

### Frequently Asked Questions (FAQ)

#### Q: Is DoomScript interpreted or compiled?
**A:** DoomScript is **compiled**. It uses an LALR(1) parser with pre-cached tables to compile DoomScript text directly into native Python Abstract Syntax Trees (AST). The generated AST is executed by the CPython virtual machine or compiled into machine code via PyInstaller/Nuitka.

#### Q: How fast is compilation?
**A:** Compilation takes **under 5 milliseconds** for typical scripts, thanks to Lark LALR disk caching (`cache=True`) and high-capacity regex caching (`re._MAXCACHE = 16384`).

#### Q: Can I use DoomScript in production?
**A:** Yes. DoomScript has a comprehensive test suite covering syntax, contracts, domain algorithms, error diagnostics, and memory safety. It produces standard Python bytecode with zero external runtime dependencies.

#### Q: Why not just write Python?
**A:** Python requires remembering punctuation, complex syntax, decorators, context managers, and dunder methods. DoomScript lets domain experts, analysts, and engineers focus on business logic in pure, readable English while retaining all the speed and power of the Python ecosystem.

---

<p align="center">
  <b>DoomScript: The English-First Programming Language.</b><br>
  Designed with precision for human minds.
</p>

---

## 8. Production Deployment, PyPI Ecosystem & FAQ

### 100% Bidirectional Python Interoperability

DoomScript is a first-class citizen in the Python ecosystem:

#### 1. Calling PyPI Packages from DoomScript
Use any Python module (PyTorch, Pandas, Scikit-Learn, FastAPI) directly inside your `.doom` script:

```doom
use python module math
use python module torch as th

say "Square root of 144:", math.sqrt(144)
tensor = th.zeros([3, 3])
say "PyTorch Tensor:", tensor
```

#### 2. Embedding DoomScript Inside Existing Python Code
Import and run DoomScript logic from standard Python applications:

```python
from doomscript import execute, compile_to_ast

# Execute DoomScript code directly from Python
env = execute('''
set x to 10
set y to 20
what is x + y into total
''')

print("Result from DoomScript:", env["total"])  # 30
```

---

### Compiling to Native Standalone Binaries (`doom build`)

To ship your application to end users without requiring them to install Python or DoomScript:

```bash
# Windows creates standalone .exe:
doom build app.doom -o dist/app.exe

# Linux creates standalone ELF executable:
doom build app.doom -o dist/app
```

The resulting executable bundles the Python AST runtime into a single, self-contained binary file.

---

### Frequently Asked Questions (FAQ)

#### Q: Is DoomScript interpreted or compiled?
**A:** DoomScript is **compiled**. It uses an LALR(1) parser with pre-cached tables to compile DoomScript text directly into native Python Abstract Syntax Trees (AST). The generated AST is executed by the CPython virtual machine or compiled into machine code via PyInstaller/Nuitka.

#### Q: How fast is compilation?
**A:** Compilation takes **under 5 milliseconds** for typical scripts, thanks to Lark LALR disk caching (`cache=True`) and high-capacity regex caching (`re._MAXCACHE = 16384`).

#### Q: Can I use DoomScript in production?
**A:** Yes. DoomScript has a comprehensive test suite covering syntax, contracts, domain algorithms, error diagnostics, and memory safety. It produces standard Python bytecode with zero external runtime dependencies.

#### Q: Why not just write Python?
**A:** Python requires remembering punctuation, complex syntax, decorators, context managers, and dunder methods. DoomScript lets domain experts, analysts, and engineers focus on business logic in pure, readable English while retaining all the speed and power of the Python ecosystem.

---

<p align="center">
  <b>DoomScript: The English-First Programming Language.</b><br>
  Designed with precision for human minds.
</p>
