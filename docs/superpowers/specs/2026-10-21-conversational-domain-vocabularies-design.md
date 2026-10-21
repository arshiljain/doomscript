# Conversational Domain Vocabularies Design Specification
**Track 1: "Talking to the Tools" — English Thought-Stream Domain Syntax**

**Date:** 2026-10-21  
**Status:** Approved / In Implementation  
**Target:** DoomScript 0.6.0 Conversational Domain Layer  

---

## 1. Executive Summary & Vision

DoomScript empowers human beings to express algorithmic and domain-specific intent in standard, idiomatic English. In Track 2 (*Story-Driven Relational Modeling*), we enabled intuitive class and lifecycle definitions without boilerplate (`a BankAccount begins with balance = 100`, `has many`, `belongs to`, `when receiving <amount>:`).

**Track 1 (*Conversational Domain Vocabularies*)** completes this evolution by allowing developers and non-programmers to "talk to the tools" in their natural stream of thought across 4 essential domain ecosystems:
1. **Web & APIs (`web` / `net`):** Natural HTTP requests, payload posting, and nested JSON field extraction.
2. **Data & Analytics (`data` / `db`):** Intuitive tabular file ingestion (`load csv/json from ...`), natural aggregations (`summarize column ... by ...`), and immediate chart generation (`plot ... as a bar chart titled "..."`).
3. **Finance & Simulation (`finance` / `sim`):** Conversational multi-asset portfolio simulation (`simulate portfolio with 50% BTC and 50% ETH`) and readable financial math (`calculate compound interest on principal 1000 at rate 5% over 10 years`).
4. **AI & Agents (`agent` / `nlp`):** Fluid assistant and model querying (`ask the assistant "..." into summary`, `ask the model "..." for <data> into result`).

---

## 2. Architecture & Normalization Pipeline

To guarantee **100% backward compatibility** and **zero runtime overhead**, Track 1 syntax uses a multi-tier dispatch model:

1. **Pre-Parsing Phrase Normalization (`phrases.py`):**
   - High-level conversational sentences (e.g. `send a get request to ... and wait for response into res`) are recognized before tokenization.
   - String literals are masked to prevent accidental corruption of URLs, filenames, or prompts.
   - The conversational forms desugar either directly into canonical DoomScript statements or calls to dedicated, high-performance runtime functions.

2. **Core Runtime Helpers (`runtime.py`):**
   - Pure standard-library, thread-safe helper functions are added to DoomScript's default runtime exports:
     - `extract_json_field(source, field_path: str)`: Traverses dicts, Records, lists, or raw JSON text with dot-notation and index syntax (e.g. `data.items[0].id`).
     - `summarize_data(table, metric_col, group_col, agg_fn="sum")`: Groups tabular records and computes aggregated metrics.
     - `simulate_portfolio(allocations, initial_value=10000.0, horizon_days=30)`: Computes multi-asset returns, volatility, projected value, and VaR risk metrics.
     - `calculate_compound_interest(principal, rate, years, periods=1)`: Computes compound growth and returns the calculated total.
     - `load_json_file(filepath: str)`: Ingests and parses a JSON file into Records.
     - `ask_assistant(prompt: str, context=None, as_json=False)`: Queries AI assistant with conversational system prompt.
     - `ask_model(prompt: str, model="default", context=None, as_json=False)`: Queries AI model with optional context.

3. **Domain Verb Interoperability:**
   - When domain packs are explicitly imported (e.g. `use web`, `use net`, `use data`, `use finance`, `use agent`), the domain parsers also accept these natural phrasing variants as first-class operations.

---

## 3. Domain 1: Web & APIs (`web` / `net`)

### Syntax Specifications

#### A. HTTP Requests (GET & POST)
```doomscript
# 1. Full thought-stream GET
send a get request to "https://api.example.com/items" and wait for response into res
send a get request to "https://api.example.com/items" into res
send get request to "https://api.example.com/items" into res
get "https://api.example.com/items" into res

# 2. Thought-stream POST with payload
send a post request to "https://api.example.com/create" with payload into res
send post request to "https://api.example.com/create" with payload into res
post payload to "https://api.example.com/create" into res
```

**Desugaring:**
- `send (?:a\s+)?get\s+request\s+to\s+(.+?)(?:\s+and\s+wait\s+for\s+response)?\s+into\s+([A-Za-z_]\w*)`  
  -> `set <res> to fetch_url(<url>, method="GET")`
- `send (?:a\s+)?post\s+request\s+to\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <res> to fetch_url(<url>, method="POST", json_body=<payload>)`
- `post\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <res> to fetch_url(<url>, method="POST", json_body=<payload>)`

#### B. JSON Field Extraction
```doomscript
# Extract dot-notation fields from HTTP responses, Records, or JSON strings
extract json field "data.items" from res into items
extract field "user.id" from res into user_id
```

**Desugaring:**
- `extract\s+(?:json\s+)?field\s+(.+?)\s+from\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to extract_json_field(<source>, <field_path>)`

---

## 4. Domain 2: Data & Analytics (`data` / `db`)

### Syntax Specifications

#### A. Conversational File Ingestion
```doomscript
# CSV and JSON files
load csv from "sales.csv" into sales_table
load csv "sales.csv" into sales_table
load json from "config.json" into config_data
load json "data.json" into dataset
```

**Desugaring:**
- `load\s+csv\s+(?:from\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `read csv file <path> into <target>`
- `load\s+json\s+(?:from\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to load_json_file(<path>)`

#### B. Natural Group Summaries
```doomscript
# Summarize a metric column by a category/group
summarize column "revenue" by "region" in sales_table into regional_sales
summarize column "revenue" by "region" from sales_table into regional_sales
summarize sales_table by "region" calculating sum of "revenue" into regional_sales
```

**Desugaring:**
- `summarize\s+column\s+(.+?)\s+by\s+(.+?)\s+(?:in|from)\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to summarize_data(<table_expr>, <metric_col>, <group_col>, agg_fn="sum")`
- `summarize\s+(.+?)\s+by\s+(.+?)\s+calculating\s+([A-Za-z_]\w*)\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to summarize_data(<table_expr>, <val_col>, <group_col>, agg_fn="<agg_fn>")`

#### C. Immediate Chart Generation
```doomscript
# Plot as chart
plot regional_sales as a bar chart titled "Q4 Sales" into chart
plot regional_sales as a bar chart titled "Q4 Sales"
plot sales_data as a line chart titled "Monthly Trend"
```

**Desugaring:**
- `plot\s+(.+?)\s+as\s+(?:a\s+)?([A-Za-z_]\w+)\s+chart(?:\s+titled\s+(.+?))?(?:\s+into\s+([A-Za-z_]\w*))?$`  
  -> `set <target or plot> to PlotBuilder(<data>, title=<title>).draw("<geom>")`

---

## 5. Domain 3: Finance & Simulation (`finance` / `sim`)

### Syntax Specifications

#### A. Conversational Multi-Asset Portfolio Simulation
```doomscript
# Percentage allocation or dictionary weights
simulate portfolio with 50% BTC and 50% ETH into sim_result
simulate portfolio with {"AAPL": 0.6, "MSFT": 0.4} into sim_result
```

**Allocation Syntax:**
`50% BTC and 50% ETH` or `40% AAPL, 30% MSFT, 30% GOOG` is converted to a dictionary `{"BTC": 0.50, "ETH": 0.50}`.

**Desugaring:**
- `simulate\s+portfolio\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to simulate_portfolio(<allocations_dict>)`

**Result Structure:**
`sim_result` is a `Record` with:
- `allocations`: Map of asset symbols to fractional weights.
- `initial_value`: Baseline capital (default 10000.0).
- `projected_value`: Simulated future value over horizon.
- `expected_annual_return`: Portfolio weighted return.
- `annual_volatility`: Portfolio risk standard deviation.
- `sharpe_ratio`: Annualized Sharpe ratio.
- `var_95`: 95% Value-at-Risk percentage.

#### B. Readable Financial Math (Compound Interest)
```doomscript
calculate compound interest on principal 1000 at rate 5% over 10 years into total
calculate compound interest on principal 5000 at rate 0.07 over 5 years into total
```

**Desugaring:**
- `calculate\s+compound\s+interest\s+on\s+principal\s+(.+?)\s+at\s+rate\s+(.+?)\s+(?:over|for)\s+(.+?)\s+years\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to calculate_compound_interest(<principal>, <rate>, <years>)`

---

## 6. Domain 4: AI & Agents (`agent` / `nlp`)

### Syntax Specifications

#### A. Fluid Assistant & Model Invocations
```doomscript
# 1. Ask assistant
ask the assistant "Summarize this report" into summary
ask assistant "Generate 3 title ideas" into ideas
ask the assistant "Explain this" for document_text into explanation

# 2. Ask model with context
ask the model "Classify sentiment" for review_text into sentiment
ask model "Translate to French" for input_phrase into translation

# 3. Flexible article tolerance for existing agent commands
ask the agent researcher "Find papers on CRDTs" into papers
tell the agent researcher "Log this note"
```

**Desugaring:**
- `ask\s+(?:the\s+)?assistant\s+(.+?)(?:\s+for\s+(.+?))?\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to ask_assistant(<prompt>, context=<context>)`
- `ask\s+(?:the\s+)?model\s+(.+?)(?:\s+for\s+(.+?))?\s+into\s+([A-Za-z_]\w*)`  
  -> `set <target> to ask_model(<prompt>, context=<context>)`
- `ask\s+the\s+agent\s+([A-Za-z_]\w*)\s+(.+?)\s+into\s+([A-Za-z_]\w*)`  
  -> `ask agent <name> <prompt> into <target>`
- `tell\s+the\s+agent\s+([A-Za-z_]\w*)\s+(.+)`  
  -> `tell agent <name> <message>`

---

## 7. Error Handling & Zero Python Leakage

All runtime helpers wrap native exceptions and raise domain-appropriate DoomScript errors:
- If a CSV or JSON file does not exist: raises friendly `DoomScriptRuntimeError("File not found: ...")` instead of raw Python `FileNotFoundError`.
- If a field is missing during `extract json field`: returns `None` or raises an informative error explaining which key in the path failed to resolve.
- If invalid percentages or allocations are provided in portfolio simulation: raises a descriptive error explaining allocation normalization.

---

## 8. Verification Strategy & Acceptance Criteria

1. **Unit Test Suite:**  
   `tests/domains/test_conversational_domains.py` containing dedicated test cases for all 4 domain ecosystems.
2. **UX Benchmark:**  
   Run the 85-point Beginner UX Audit suite to ensure zero regressions on all intuitive beginner programs.
3. **Regression Suite:**  
   Run the 92+ core test suite across compiler, parser, runtime, and all 40 domains.
4. **Git Hygiene:**  
   TDD task-by-task commits followed by final push to `main`.
