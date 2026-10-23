# DoomScript (`.doom`)

> **Turn a messy spreadsheet or folder into a clean report in plain English.**

DoomScript is an English-first programming language designed for analysts, operations teams, and beginners who need to automate data work without wrestling with Python boilerplate, cryptic syntax, or confusing compiler errors.

DoomScript compiles directly to standard Python Abstract Syntax Trees (AST) with zero external runtime dependencies.

---

## The Pitch: One Job Done Better Than Python

Most daily automation comes down to a simple 5-step job:
1. Read a messy CSV or folder of files.
2. Filter valid records and clean up messy values.
3. Calculate key summary metrics.
4. Export a clean report spreadsheet.
5. Print an executive briefing.

Here is the exact same 5-step task written in **Python** vs **DoomScript**:

### Side-by-Side Comparison

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
with open("clean_report.csv", mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["customer", "amount"])
    writer.writeheader()
    writer.writerows(valid)

# 5. Print summary
total = sum(r["amount"] for r in valid)
print(f"Cleaned {len(valid)} orders. Total volume: ${total:,.2f}")
if valid:
    print(f"Top order: {valid[0]['customer']} (${valid[0]['amount']})")
```
<!-- slide -->
```doom
# -------------------------------------------------------------
# DOOMSCRIPT: 7 lines, 0 imports, reads like spoken English
# -------------------------------------------------------------

# 1. Read messy transactions
read csv file "sales_raw.csv" into orders

# 2. Filter valid paid transactions over $50
orders where status is "paid" into valid
valid where amount is over 50 into high_value

# 3. Sort by amount descending
sort high_value by amount descending

# 4. Save clean audit report
write csv high_value into file "clean_report.csv"

# 5. Print executive summary
say "Cleaned", count of high_value, "orders."
say "Top customer:", first item of high_value
```
````

| Metric | Python | DoomScript |
| :--- | :--- | :--- |
| **Lines of Code** | 38 lines | **7 lines** |
| **Imports & Ceremonies** | `csv`, `DictReader`, `DictWriter`, `with open`, `lambda`, `try/except` | **0 imports**, plain English statements |
| **Cognitive Load** | High (mutations, exception guards, newline formatting) | **Low** (reads like an operational checklist) |
| **Typing & Numeric Inference** | Manual string-to-float conversions | **Automatic** numeric & boolean inference |

---

## Try It in 30 Seconds

### 1. Interactive Web Playground
Launch the zero-install web IDE directly from your terminal:
```bash
doom playground
```
Or open [`playground/index.html`](playground/index.html) directly in any web browser to test scripts, view transpiled Python side-by-side, and explore live step-by-step explanations.

### 2. One-Line Install

**macOS / Linux:**
```bash
curl -fsSL https://raw.githubusercontent.com/arshiljain/doomscript/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
irm https://raw.githubusercontent.com/arshiljain/doomscript/main/install.ps1 | iex
```

**Via Pip:**
```bash
pip install git+https://github.com/arshiljain/doomscript.git
```

---

## The Predictability Guarantee: Avoiding the AppleScript Trap

English-like languages historically fail when users can phrase things twenty different ways, cannot predict which ways work, and the language feels random. DoomScript solves this with four non-negotiable principles:

1. **A Guaranteed 30-Form Core**: A rock-solid, fully specified subset (~30 forms) that is guaranteed to always work identically across every version and platform. See [docs/CORE_SPEC.md](docs/CORE_SPEC.md).
2. **Dual-Form Consistency**: Every data operation is available as **both** a statement and an expression:
   - Statement: `trim raw_name into cleaned` $\leftrightarrow$ Expression: `say trim of raw_name`
   - Statement: `uppercase name into upper` $\leftrightarrow$ Expression: `set upper to uppercase of name`
   - Statement: `sort items` $\leftrightarrow$ Expression: `for each x in sorted of items:`
   - Statement: `reverse items` $\leftrightarrow$ Expression: `say reversed of items`
   - Statement: `unique items of list into u` $\leftrightarrow$ Expression: `say unique of list`
3. **Auto-Coerced CSV & JSON Numerics**: Numerical columns and fields in spreadsheets and JSON APIs auto-coerce to integers and floats without manual parsing boilerplate, with explicit `<val> as number` casting available when needed.
4. **Natural Multi-Clause Sentence Chaining**: Connect sequential operations seamlessly using `and` or `then` without forced semicolons or rigid line-breaks:
   - `read file "data.csv" into raw and split raw by "\n" into lines`
   - `create a Person with name "Bob", age 25 into p and say p's name`
   - `set x to 10 then say x`
   - Preserves conditional `and` (`if x > 10 and y < 20:`) and expression operands (`between 10 and 20`).
5. **Actionable Suggestions for Everything Outside Core**: When you make a typo or use an unsupported phrasing, DoomScript uses edit-distance matching to suggest the exact documented command.

---

## Friendly Errors: Built for Humans, Not Compilers

A beginner's first failure is almost always a syntax error. Cryptic parser traces discourage newcomers. DoomScript translates syntax errors and runtime failures into clear, plain-English guidance with caret pointers and actionable suggestions.

### 1. Typo & Keyword Suggestions
Did you mistype a command or keyword? DoomScript uses Levenshtein edit-distance to guide you:

```text
DoomScript Syntax Error at script.doom:1:1

   1 | sya "Hello, world!"
       ^

Problem: I didn't recognize the command 'sya'. Did you mean 'say'?
Did you mean: say "Hello, world!"
```

### 2. Keyword-Collision Prevention
Accidentally named a variable after a language keyword? DoomScript explains the conflict instead of throwing a generic parser error:

```text
DoomScript Syntax Error at script.doom:1:1

   1 | to = 5
       ^

Problem: 'to' is a reserved keyword in DoomScript used to define functions ('to my_function with x:'). It cannot be used as a variable name.
Did you mean: set my_to to 5
```

### 3. Syntax Diagnostics & Missing Destinations
```text
DoomScript Syntax Error at report.doom:3:18

   3 | read csv file "data.csv"
                            ^

Problem: A CSV read command needs a destination variable after 'into'.
Did you mean: read csv file "data.csv" into rows
```

```text
DoomScript Syntax Error at script.doom:5:22

   5 | say "Total revenue:
                         ^

Problem: It looks like an unclosed double quote ("). Every opening quote needs a matching closing quote.
Did you mean: say "Total revenue:"
```

### 4. Plain-English Runtime Exception Shield
When an operation fails at runtime (divide by zero, missing keys, out of bounds indices, missing files), DoomScript intercepts raw Python tracebacks and wraps them in dual-inheritance `DoomError` instances. Beginners see source line pointers and actionable English explanations, while Python tooling and test frameworks retain full `isinstance` compatibility:

```text
+-----------------------------------------------------------------------------+
| DoomScript Runtime Error in script.doom                                     |
+-----------------------------------------------------------------------------+
   2 | say user_total
       ^

Problem: I don't know what 'user_total' is. Did you set it earlier?
```

- **Division by Zero**: *"Cannot divide by zero. You tried to divide by zero. Make sure the number you're dividing by is not 0."*
- **Out of Bounds Index**: *"You asked for item 10, but this list only has 3 items."*
- **Missing File**: *"I couldn't find the file 'data.csv'. Check that the name and folder are correct."*
- **Type Mismatch**: *"You tried to add a int and a str. These types can't be combined this way."*

---

## Core Capabilities for Automation & Data

### 1. Files, Folders & Spreadsheets
```doom
# Read & write spreadsheets effortlessly
read csv file "input.csv" into records
write csv records into file "output.csv"
append csv {name: "Dana", score: 95} to file "output.csv"

# File & directory operations
read file "notes.txt" into content
write "Done" into file "status.txt"
list files in "reports" into filenames
check if file "config.json" exists into has_config
```

### 2. Filtering, Sorting & Aggregates
```doom
orders where status is "completed" into completed_orders
sort completed_orders by total descending

say "Total Revenue:", sum of total in completed_orders
say "Average Order:", average of total in completed_orders
say "Highest Order:", highest total in completed_orders
say "Order Count:", count of completed_orders
```

### 3. Natural Control Flow & Loops
```doom
# Plain English while and repeat loops
set balance to 100
while balance > 0:
    balance -= 10

repeat 5 times:
    say "Pinging server..."

repeat with i from 1 to 10 by 2:
    say "Step:", i
```

### 4. Robust Error Handling
```doom
try:
    read file "remote_config.json" into conf
    parse json conf into settings
if it fails as problem:
    say "Could not load settings:", problem
always:
    say "Cleanup complete."
```

### 5. 100% Python Ecosystem Interop
Call any Python module directly when you need specialized libraries:
```doom
use python module math
from python module datetime use datetime

say "Square root of 144:", math's sqrt(144)
```

### 6. Natural Units of Measurement & Dimensional Analysis
Numbers and variables carry natural English units with automatic dimensional algebra, conversions, and type-checked safety:
```doom
# Speed, Time & Automatic Distance Calculation
set speed to 60 miles per hour
set travel_time to 2.5 hours
set distance to speed * travel_time
say distance                                 # "150 miles"

# Unit Conversions (Statement & Expression)
convert distance to kilometers into dist_km  # "241.4016 kilometers"
say distance in meters                       # "241401.6 meters"

# Affine Temperature Scales & Financials
set room_temp to 72 degrees fahrenheit
convert room_temp to celsius into temp_c     # "22.2222 celsius"
set price to $100
set budget to 500 dollars
```

---

## English-First Domain Extensions: One Language, Many Domains

DoomScript features a modular Domain Extension Architecture where you write ordinary core code, then activate specialized domain syntax via `use <domain>`. Every domain follows the **Three-Level Surface Pattern**:
- **Level 1 (Inspect & Explore)**: Discover schema, inspect metadata, summary statistics.
- **Level 2 (Single Operation)**: Direct, expressive single-line verbs.
- **Level 3 (Compose Workflow)**: Multi-step pipeline, model training, simulation, or query blocks.

All domains compile to zero-dependency execution engines or export into safe, idiomatic Python AST (`pandas`, `scikit-learn`, `sqlite3`, `lets-plot`, `urllib`).

### 1. Data Engineering (`use data`)
```doom
use data

raw_sales = [{"id": 1, "region": "North", "amount": 100}, {"id": 1, "region": "North", "amount": 100}]

pipeline "clean_sales" from raw_sales into cleaned_sales:
    validate:
        require "region" is text
        require "amount" is positive number
        forbid nulls in "id"
    remove duplicate rows
    filter where amount is greater than 50
    group by region:
        calculate total_revenue as sum of amount
        calculate order_count as count
    sort by total_revenue descending
    write to "output.csv"
```
*AST Export*: Lowers directly to `pandas.DataFrame.drop_duplicates()`, `.query()`, `.groupby()`, and `.to_csv()`.

### 2. Machine Learning (`use ml`)
```doom
use ml

model churn_predictor from customer_data:
    target: churned
    features: age, usage, monthly_fee
    algorithm: random_forest
    split: 80% training, 20% testing

train churn_predictor
evaluate churn_predictor into report
say "Model Accuracy:", report["accuracy"]
```
*AST Export*: Generates idiomatic `sklearn.ensemble.RandomForestClassifier` and train/test pipelines. Built-in zero-dependency fallback algorithms run anywhere without external packages.

### 3. Relational Data & SQL (`use db`)
```doom
use db

query employees into senior_devs:
    select id, name, salary
    where salary is over 100000 and department equals "Engineering"
    order by salary descending
    limit 10
```
*AST Export*: Compiles to safe, parameterized `sqlite3.Cursor.execute()` with placeholder bindings, completely eliminating SQL injection risks.

### 4. Web & API Automation (`use net`)
```doom
use net

# Single-line request with automatic JSON parsing
request GET "https://api.example.com/orders" into resp
parse resp as JSON into orders

# Composed workflow with backoff retries and authentication
api "order_sync":
    base_url: "https://api.example.com"
    timeout: 10 seconds
    retries: 3 times
    get "/v1/inventory" into inv_resp
    parse inv_resp as JSON into inventory
    save inventory to "inventory.json"
```
*AST Export*: Translates to standard `urllib.request` with exponential backoff and timeout handling.

### 5. Simulation & Optimization (`use sim`)
```doom
use sim

# Discrete-event queue simulation (M/M/c)
simulate customer_support:
    arrivals: poisson with rate 12.0
    service: exponential with rate 15.0
    duration: 1000 events
    servers: 2

say "Average Waiting Time:", customer_support["summary"]["waiting_time"]["mean"]
say "Server Utilization:", customer_support["utilization"]
```
*AST Export*: Lowers to stochastic event loops using Python's standard `random` and `heapq`.

### 6. Testing & Algorithm Analysis (`use dsa`)
```doom
use dsa

to quick_sort with items:
    # ... sorting implementation ...
    return sorted_items

benchmark quick_sort:
    input_sizes: [100, 500, 1000, 5000]
    repeat: 5
    measure: execution_time, memory

say "Inferred Complexity:", quick_sort_benchmark["best_fit"]
say "Peak Memory:", quick_sort_benchmark["peak_memory_bytes"]
```
*AST Export*: Uses `time.perf_counter_ns()` and `tracemalloc` to generate empirical runtime profiles with asymptotic $R^2$ curve fitting.

### 7. Grammar-of-Graphics Visualization (`use viz`)
```doom
use viz

plot sales as line into rev_trend:
    x: month
    y: revenue
    color: region
    title: "FY2026 Monthly Revenue Growth"
    theme: minimal

save rev_trend to "revenue.html" with width=1200, height=600
```
*AST Export*: Compiles directly into native `lets_plot.ggplot() + geom_line() + theme_minimal()` AST calls.

---

## Documentation & Complete Reference Manual

For the complete, exhaustive guide covering all syntax rules, 80 embedded computational domains, conversational inquiries, superlatives, quantifiers, adverbials, story-driven entities, and algorithmic benchmarks, see:

📖 **[Complete DoomScript Documentation & Reference Manual (documentation.md)](documentation.md)**

---

## Development & Test Verification

DoomScript is tested against rigorous corpus benchmarks, full regression suites, and empirical beginner UX audits:
- **Test Suite**: 1,492+ automated unit & integration tests passing (100% pass rate)
- **Beginner UX Benchmark**: 150 / 150 intuitive phrasings passing (0 Python leaks)
- **Corpus Pass Rate**: 200 / 200 sentences (100.0%)
- **Domain Coverage**: 80 embedded computational domain libraries (`use <domain>`)
- **Compilation Speed**: Standalone LALR disk table caching (`cache=True`) and high-capacity regex cache delivering sub-5ms compilations

Run tests locally:
```bash
python -m pytest
python scratch/audit_beginner_phrasings.py
python run_corpus.py --fail-under 98
```

---

---

## The 4 Phases of Natural English Thought-to-Code

DoomScript's parser and AST compilation engine support natural, fluent English thought-to-code paradigms across four major dimensions:

### 1. Fluent Expression Chaining & Preposition Flexibility
- **Pipe Operator (`|>`)**: Compose operations naturally from left to right without nested parentheses or intermediate temporary variables:
  ```doom
  set words to ["alpha", "beta", "gamma", "delta"]
  words |> take 2 |> join with " / " into short_label
  # Result: "alpha / beta"
  
  set nums to [10, 20, 30, 40, 50]
  set top_three to nums |> drop 1 |> take 3 |> sorted descending
  # Result: [40, 30, 20]
  ```
- **Article Tolerance (`the`, `a`, `an`)**: Optional articles are gracefully accepted before variables, queries, and loops:
  ```doom
  set the total to 500
  the subtotal is 250
  add 50 to the total
  set count to the count of the items
  for each item in the items:
      say the item
  ```
- **Preposition Flexibility**: Interchangable prepositions across common idioms:
  ```doom
  take 2 from words into first_two
  drop 2 from words into last_two
  join first_two by " + " into joined
  split "one,two,three" with "," into parts
  ```

### 2. Units, Currencies & Magnitude Scale Arithmetic
- **Currency Prefixes**: Directly write monetary values with commas:
  ```doom
  set unit_price to $1,250.50
  set tax_rate to 15%
  set subtotal to unit_price * 10
  set discount to 10% of subtotal
  ```
- **Magnitude Suffixes**: Express human scales directly:
  ```doom
  set valuation to 2.5 million       # 2,500,000.0
  set monthly_active_users to 500k   # 500,000
  set national_debt to 10 billion    # 10,000,000,000.0
  ```
- **Postfix Conditionals (`unless`, `only if`)**: Guard statements intuitively without extra indentation blocks:
  ```doom
  say "Operation aborted" unless is_authenticated
  send_push_notification() only if battery_level > 20
  ```

### 3. Multi-Field Sorting, Grouping & Natural Projections
- **Multi-Field Sorting**: Order complex collections with mixed ascending and descending keys:
  ```doom
  sort employees by department ascending and tenure descending into ranked_team
  sort transactions by customer, amount desc into sorted_tx
  ```
- **Multi-Key Group Aggregations**: Group by multiple categorical dimensions while computing totals, averages, minimums, or maximums:
  ```doom
  group sales by region and quarter calculating total revenue into quarterly_summary
  group tickets by category, priority calculating average response_time into triage_metrics
  ```
- **Natural Field Access with `of`**: Read object attributes and record fields in conversational order:
  ```doom
  set user_name to name of user
  set order_status to status of order
  set book_author to author of book
  ```

### 5. Universal Syntax Consistency & Natural Compositionality
- **Statement vs. Expression Parity**: Any data verb works both as an action and as an expression (`split text by "," into words` vs `set words to text split by ","`).
- **Complete Preposition & Synonym Coverage**: Natural variations (`add` / `append` / `push`; `remove` / `delete` / `discard`; `increase` / `increment`; `has` / `contains`) resolve to identical canonical operations.
- **Nested Expression Composition**: Seamlessly chain natural operations (`uppercase of first item of words`, `trim of uppercase of text`).
- **Quantifier Implied Equality**: Express predicates concisely (`if every user in team has role "admin":`).

### 4. Background Concurrency & Pure-English OOP
- **Asynchronous Background Execution**: Run long-running tasks in worker threads without blocking:
  ```doom
  run in background heavy_analytics(dataset) into analytics_job
  # Continue doing other interactive work...
  wait for analytics_job into final_report
  wait for all tasks in background_jobs into results
  ```
- **Pure-English Entity & OOP Modeling**: Declare schemas and methods without Python `self` or `__init__`:
  ```doom
  a Customer has name, email, balance = 0.0
  
  create a Customer with name "Alice", email "alice@corp.com" into vip
  say vip's name
  change vip's balance to $500.00
  ```
- **Scope-Aware Comparison & Ambiguity Warnings**:
  In DoomScript, writing `if status is "active":` compares equality. When writing `if x is word:`, the compiler checks if `word` is a declared variable in scope; if so, it performs a value comparison; otherwise it tests an entity property, and emits an empathetic warning if ambiguous.
- **Python Module Interoperability**:
  Seamlessly bring in external Python libraries:
  ```doom
  use python module math as m
  from python module json use loads
  say m.sqrt(144)
  ```

## Execution Model & Security Boundary

DoomScript is an ergonomic, human-friendly syntax layer that compiles directly into standard Python Abstract Syntax Trees (AST) and executes within the host Python runtime.

> [!WARNING]
> **Not a Security Sandbox**: DoomScript's execution engine executes in-process and is **NOT** a security sandbox. English syntax does not restrict script capabilities. Never execute untrusted or unsanitized `.doom` scripts without external operating system sandboxing (such as Docker containers, gVisor, or dedicated virtual machines).

---

## License

MIT License. Crafted for mortals who want clean automation in plain English.
