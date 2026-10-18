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

## Friendly Errors: Built for Humans, Not Compilers

A beginner's first failure is almost always a syntax error. Cryptic parser traces discourage newcomers. DoomScript translates syntax errors and runtime failures into clear, plain-English guidance with caret pointers and actionable suggestions.

### Syntax Diagnostics
Instead of cryptic parser output (`UnexpectedCharacters: No terminal matches '\n'`), DoomScript tells you exactly what went wrong:

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

### Runtime Diagnostics
When a variable isn't found or an operation fails, DoomScript explains the fix in plain English:

```text
+-----------------------------------------------------------------------------+
| DoomScript Runtime Error in script.doom                                     |
+-----------------------------------------------------------------------------+
   2 | say user_total
       ^

Problem: I don't know what 'user_total' is. Did you set it earlier?
```

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

---

## Development & Test Verification

DoomScript is tested against a strict 200-sentence English corpus and unit test suite:
- **Corpus Pass Rate**: 200 / 200 sentences (100.0%)
- **Test Suite**: 141 passed in ~10 seconds
- **Parser Speed**: LALR parser cached in-memory with sub-millisecond compilation latency

Run tests locally:
```bash
python -m pytest
python run_corpus.py --fail-under 98
```

---

## License

MIT License. Crafted for mortals who want clean automation in plain English.
