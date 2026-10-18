# DoomScript Task-Oriented Language Reference Manual

**DoomScript** (`.doom`) is a general-purpose, English-first programming language designed for beginners, data analysts, students, and automation engineers. It transpiles deterministically to Python AST.

### Core Design Principle: Flexible on Input, Strict on Meaning
DoomScript permits multiple natural English phrasings for the same intent, but every accepted sentence maps deterministically to exactly **one** unambiguous Python AST construct.

---

## Table of Contents
1. [How do I print and format text?](#1-how-do-i-print-and-format-text)
2. [How do I store and update variables?](#2-how-do-i-store-and-update-variables)
3. [How do I get user input?](#3-how-do-i-get-user-input)
4. [How do I work with lists?](#4-how-do-i-work-with-lists)
5. [How do I work with records / dictionaries?](#5-how-do-i-work-with-records--dictionaries)
6. [How do I filter, group, and query data?](#6-how-do-i-filter-group-and-query-data)
7. [How do I write conditions?](#7-how-do-i-write-conditions)
8. [How do I write loops?](#8-how-do-i-write-loops)
9. [How do I define and call functions?](#9-how-do-i-define-and-call-functions)
10. [How do I handle errors safely?](#10-how-do-i-handle-errors-safely)
11. [How do I read and write files?](#11-how-do-i-read-and-write-files)
12. [How do I work with CSV spreadsheets?](#12-how-do-i-work-with-csv-spreadsheets)
13. [How do I parse and serialize JSON?](#13-how-do-i-parse-and-serialize-json)
14. [How do I work with dates and times?](#14-how-do-i-work-with-dates-and-times)
15. [How do I perform math and rounding?](#15-how-do-i-perform-math-and-rounding)
16. [How do I clean and manipulate text?](#16-how-do-i-clean-and-manipulate-text)
17. [How do I use Python libraries?](#17-how-do-i-use-python-libraries)
18. [How do I interact with the OS and shell?](#18-how-do-i-interact-with-the-os-and-shell)
19. [How do I use CLI tools and diagnose errors?](#19-how-do-i-use-cli-tools-and-diagnose-errors)
20. [Legacy Primitives (Frozen)](#20-legacy-primitives-frozen)
21. [How do I scrape web pages and parse HTML? (Phase 4)](#21-how-do-i-scrape-web-pages-and-parse-html-phase-4)
22. [How do I make HTTP requests with headers and auth? (Phase 4)](#22-how-do-i-make-http-requests-with-headers-and-auth-phase-4)
23. [How do I compose and send emails? (Phase 4)](#23-how-do-i-compose-and-send-emails-phase-4)
24. [How do I join datasets in English? (Phase 4)](#24-how-do-i-join-datasets-in-english-phase-4)
25. [How do I handle timezones and intervals? (Phase 4)](#25-how-do-i-handle-timezones-and-intervals-phase-4)
26. [How do I use the Language Server (LSP)? (Phase 5)](#26-how-do-i-use-the-language-server-lsp-phase-5)
27. [How do I use the interactive REPL and Jupyter kernel? (Phase 6)](#27-how-do-i-use-the-interactive-repl-and-jupyter-kernel-phase-6)
28. [How do I manage packages and dependencies? (Phase 7)](#28-how-do-i-manage-packages-and-dependencies-phase-7)
29. [How do I enforce Type Contracts and Gradual Safety? (Phase 8)](#29-how-do-i-enforce-type-contracts-and-gradual-safety-phase-8)
30. [How do I use English Pattern Matching and Destructuring? (Phase 9)](#30-how-do-i-use-english-pattern-matching-and-destructuring-phase-9)
31. [How do I write and run unit tests? (Phase 10)](#31-how-do-i-write-and-run-unit-tests-phase-10)
32. [How do I build declarative CLI applications? (Phase 11)](#32-how-do-i-build-declarative-cli-applications-phase-11)
33. [How do I run background tasks and concurrency? (Phase 12)](#33-how-do-i-run-background-tasks-and-concurrency-phase-12)
34. [How do I create declarative web microservices? (Phase 13)](#34-how-do-i-create-declarative-web-microservices-phase-13)
35. [How do I invoke AI and LLM models in English? (Phase 14)](#35-how-do-i-invoke-ai-and-llm-models-in-english-phase-14)
36. [How do I declare Database Entities and ORM queries? (Phase 15)](#36-how-do-i-declare-database-entities-and-orm-queries-phase-15)
37. [How do I generate automated API documentation? (Phase 16)](#37-how-do-i-generate-automated-api-documentation-phase-16)
38. [How do I build Markdown and HTML documents? (Phase 17)](#38-how-do-i-build-markdown-and-html-documents-phase-17)
39. [How do I use file watching and live reloading? (Phase 18)](#39-how-do-i-use-file-watching-and-live-reloading-phase-18)
40. [How do I schedule recurring jobs and timers? (Phase 19)](#40-how-do-i-schedule-recurring-jobs-and-timers-phase-19)
41. [How do I use cryptography, hashing, and encryption? (Phase 20)](#41-how-do-i-use-cryptography-hashing-and-encryption-phase-20)
42. [How do I build streaming pipelines and process batches? (Phase 21)](#42-how-do-i-build-streaming-pipelines-and-process-batches-phase-21)
43. [How do I serialize binary buffers and hex numbers? (Phase 22)](#43-how-do-i-serialize-binary-buffers-and-hex-numbers-phase-22)
44. [How do I manage INI, JSON, and ENV configuration? (Phase 23)](#44-how-do-i-manage-ini-json-and-env-configuration-phase-23)
45. [How do I benchmark and profile script latency? (Phase 24)](#45-how-do-i-benchmark-and-profile-script-latency-phase-24)
46. [How do I pack standalone zero-dependency executables? (Phase 25)](#46-how-do-i-pack-standalone-zero-dependency-executables-phase-25)

---

## 1. How do I print and format text?
Use `say`, `print`, `show`, or `display`. You can pass multiple comma-separated items or use curly-brace `{var}` interpolation.
```doomscript
say "Hello, world!"
show "Status OK"

name = "Alice"
score = 95

# Multiple items
say "Player:", name, "Score:", score

# String interpolation
greeting = "Welcome {name}! Your final score is {score}."
say greeting
```

---

## 2. How do I store and update variables?
The canonical assignment syntax in DoomScript is `<target> = <expr>`. Natural English aliases (`set ... to`, `let ... be`, `put ... into`) are fully supported and normalize to canonical assignment:
```doomscript
# Canonical assignment
score = 100
total = 500

# Natural English aliases
set tax to 0.08
let attempts be 3
put 250 into balance

# Note: 'x is 10' is deprecated legacy syntax from 1.0 (use '=' instead; 'is' is reserved for comparisons)

# Arithmetic mutations
increase score by 25
decrease balance by 50

# Pronoun tracking: 'it' and 'that' refer to the last assigned variable
price = 200
increase it by 15.    # Increases price by 15
say that              # Prints 215

# Name the last result
call it final_price
```

---

## 3. How do I get user input?
Prompt users for text, validated numbers, or yes/no booleans. DoomScript automatically handles interactive terminals as well as piped stdin or shell redirection (`echo data | doom run script.doom`), suppressing prompts during piping and safely returning `""` on EOF without raising errors:
```doomscript
ask "Enter your name: " into user_name
ask into piped_data                     # reads line from piped stdin
ask number "Enter your age: " into user_age
ask boolean "Do you wish to proceed? " into is_confirmed
```

---

## 4. How do I work with lists?
Create, inspect, slice, and transform collections in English:
```doomscript
# Creation
items = a list of 10, 20, 30, 40
empty_list = an empty list
tags = ["admin", "staff", "verified"]

# English 1-based indexing & slicing
second_val = item 2 of items             # 20
first_two = first 2 items of items       # [10, 20]
last_two = last 2 items of items         # [30, 40]

# Mutation
add 50 to items                          # Appends 50
insert 5 at 1 in items                   # Inserts 5 at index 1
remove 20 from items                     # Removes value 20

# Non-destructive transforms
s = sorted items
r = reversed items
u = unique items of [1, 2, 2, 3, 1]      # [1, 2, 3]

# Inspection
size is the count of items
if items contains 30
    say "Found 30!"
if empty_list is empty
    say "Nothing inside"
```

---

## 5. How do I work with records / dictionaries?
Define structured key-value maps and access fields using dot notation or English possessives (`'s`):
```doomscript
user = {name: "Sarah", role: "Engineer", salary: 120000}

# Field access
say user.name
say user's role

# Update field
user.salary = 135000
```

---

## 6. How do I filter, group, and query data?
DoomScript provides SQL-like readable English verbs for data tables and records:
```doomscript
people = [
    {name: "Alice", age: 25, dept: "Tech"},
    {name: "Bob", age: 17, dept: "Design"},
    {name: "Charlie", age: 30, dept: "Tech"}
]

# Extract field list (comprehension)
names is the name of each person in people

# Filter records
adults = people where age is over 18 into adult_records

# Group records by category
group people by dept into dept_groups
# dept_groups.Tech contains Alice and Charlie

# Sort records
sort people by age descending

# Field aggregates
tot_age is total of age in people
avg_age is average of age in people
oldest is highest age in people
youngest is lowest age in people
```

---

## 7. How do I write conditions?
Write conditions naturally with optional colons:
```doomscript
score = 85

if score is at least 90
    say "Grade: A"
otherwise if score is at least 80
    say "Grade: B"
otherwise
    say "Grade: C"

# Range check
if score is between 80 and 100
    say "Score is in target range"

# Membership check
allowed_roles = ["manager", "admin"]
if user_role is one of allowed_roles
    say "Access granted"

# Type checks
if score is a number
    say "Valid numeric input"

# String conditions
if filename ends with ".csv"
    say "CSV detected"
if username starts with "admin_"
    say "Privileged account"

# Negative conditional (unless)
unless is_locked
    say "Door is open"
```

---

## 8. How do I write loops?
```doomscript
# Repeat N times
repeat 5 times
    say "Processing batch..."

# Range loop (inclusive start and stop, optional step)
repeat with i from 1 to 10 by 2
    say "Odd number:", i

# Filtered for-each loop
numbers = [2, 15, 8, 22, 5]
for each n in numbers where n is over 10
    say "Large number:", n

# While / Until
repeat while health is over 0
    call take_turn

until game_over
    call check_state

# Loop control
repeat with i from 1 to 100
    if i equals 50
        stop    # Break
    if i equals 25
        skip    # Continue
```

---

## 9. How do I define and call functions?
Define functions with `to`, optional defaults, and return values:
```doomscript
# Function with default parameter
to greet person with greeting "Hello"
    return "{greeting}, {person}!"

# Call standardly
msg1 = greet("Alice")
msg2 = greet("Bob", greeting="Greetings")

# Functions in expressions ('result of <func> on <arg>')
to tax on price
    return price * 0.08

subtotal = 200
tax_due is the result of tax on subtotal
say "Tax Due: ${tax_due}"
```

---

## 10. How do I handle errors safely?
```doomscript
try
    result = 100 / divisor
if that fails as problem
    say "Division failed:", problem
always
    say "Computation attempt finished."

# Verification assertions
verify that balance is at least 0 otherwise "Insufficient funds!"
```

---

## 11. How do I read and write files?
```doomscript
# Write text
write "Log entry 1" into file "system.log"
append "Log entry 2" to file "system.log"

# Read text
read file "system.log" into log_data

# Directories & Files
create directory "archives/2026"
list files in "archives" into folder_files
if file "system.log" exists
    copy file "system.log" to "archives/2026/system.log"
```

---

## 12. How do I work with CSV spreadsheets?
```doomscript
rows = [
    {sku: "A1", qty: 10, price: 5.50},
    {sku: "B2", qty: 3, price: 12.00}
]

# Write CSV
write csv rows into file "inventory.csv"

# Append single record or list
append csv {sku: "C3", qty: 7, price: 9.25} to file "inventory.csv"

# Read CSV into list of records
read csv file "inventory.csv" into loaded_inventory
```

---

## 13. How do I parse and serialize JSON?
```doomscript
raw_json = '{"server": "alpha", "port": 8080, "active": true}'

# Parse
parse json raw_json into config
say "Port:", config.port

# Stringify
convert config to json into exported_text
```

---

## 14. How do I work with dates and times?
```doomscript
today_date = today         # e.g., "2026-10-18"
current_timestamp = now    # e.g., "2026-10-18 17:30:00"

# Relative time calculations
due_date = 7 days from now
past_date = 2 hours ago
```

---

## 15. How do I perform math and rounding?
```doomscript
round 3.1415926 to 2 places into pi       # 3.14
abs_num = absolute value of -42           # 42
root = square root of 64                  # 8.0
pct = 15% of 200                          # 30.0
```

---

## 16. How do I clean and manipulate text?
```doomscript
raw_text = "  Hello World  "
trim raw_text into cleaned

replace "World" with "DoomScript" in cleaned into updated
split updated by " " into words
join words with "-" into slug
convert slug to uppercase into upper_slug
convert slug to lowercase into lower_slug
capitalize "doom" into cap_word
```

---

## 17. How do I use Python libraries?
DoomScript interoperates 100% seamlessly with native Python standard libraries:
```doomscript
use python module math
from python module math use ceil, floor

c = ceil(4.2)
f = floor(4.8)
pi_const = math.pi
```

---

## 18. How do I interact with the OS and shell?
```doomscript
get environment variable "USERNAME" into current_user
run command "git status" into git_out
say git_out
```

---

## 19. How do I use CLI tools and diagnose errors?

### Running and Checking
```bash
doom run script.doom
doom check script.doom
```

### Explaining Code (`doom explain`)
Prints each line with its generated Python AST and a plain-English explanation:
```bash
doom explain script.doom
```

### Asking for Suggestions (`doom suggest`)
```bash
doom suggest "make x = 10"
doom suggest "repeat 5 time"
```

### Formatting Code (`doom fmt`)
```bash
doom fmt script.doom --write
```

### Scaffolding New Projects (`doom new`)
```bash
doom new my_analytics_project
```

### Compiling to Native Executable (`doom build`)
```bash
doom build script.doom --onefile
```

### Theatrical Mode (`--theatrical`)
For nostalgic villain-voice compiler feedback:
```bash
doom run script.doom --theatrical
```

---

## 20. Legacy Primitives (Frozen)
The following primitives remain fully working for backward compatibility with older demos, but are frozen:
- Audio: `beep 440 hz for 0.5 seconds`, `play sound "audio.wav"`
- Window & Canvas: `open window "Game" with width 800, height 600`, `draw circle at x, y with radius r, color c`, `draw rectangle at x, y with width w, height h, color c`, `draw text "..." at x, y with size s, color c`, `clear screen`, `refresh screen`.
- SQLite: `save record rec into database "db.sqlite" table "records"`, `load records from database "db.sqlite" table "records" into target`.

---

## 21. How do I join relational datasets? (Phase 4)
Combine list-of-record tables using inner, left, right, or outer joins without SQL:
```doomscript
combine users and orders on "user_id" with style "inner" into user_orders
combine employees and departments on "dept_id" into staff_overview
```

---

## 22. How do I scrape text and links from HTML? (Phase 4)
Extract text or hyperlinks from HTML payloads or web pages:
```doomscript
extract text from html html_string into page_text
extract links from html html_string into page_links
```

---

## 23. How do I make HTTP requests and download files? (Phase 4)
Native HTTP GET, POST, and file downloads using pure Python stdlib:
```doomscript
fetch url "https://api.github.com/zen" into zen_quote
post json {"status": "ok"} to "https://httpbin.org/post" into response
download "https://example.com/data.csv" to file "data.csv"
```

---

## 24. How do I send emails? (Phase 4)
Send emails via SMTP or save to local `.eml` spool:
```doomscript
send email to "client@example.com" with subject "Weekly Report" and body "Hello, here is your report."
```

---

## 25. How do I handle timezones and business days? (Phase 4)
Inspect timezones and calculate business day skips:
```doomscript
set current_utc to now in "UTC"
set next_work_day to next business day from "2026-10-16"
if today is weekend:
    say "Enjoy your weekend!"
```

---

## 26. How do I use the Language Server (LSP)? (Phase 5)
Start the pure standard-library DoomScript Language Server over stdio JSON-RPC for real-time IDE diagnostics, hovers, completions, and definitions:
```bash
doom lsp
```
Compatible with VS Code, PyCharm, Neovim, and Sublime Text.

---

## 27. How do I use the interactive REPL and Jupyter kernel? (Phase 6)
Interactive multi-line REPL buffering:
```bash
doom repl
```
Install Jupyter kernel specification:
```bash
doom kernel install
```
Use `%doom` line magic and `%%doom` cell magic directly in Jupyter notebooks.

---

## 28. How do I manage packages and dependencies? (Phase 7)
Project manifest and dependency management via `doom.toml`:
```bash
doom init
doom add requests
doom add "rich@^13.0.0" --dev
doom install
```

---

## 29. How do I enforce Type Contracts and Gradual Safety? (Phase 8)
DoomScript supports gradual English typing, preconditions, postconditions, and compile-time contract checks:

### Typed Function Parameters
```doomscript
to calculate_bonus with salary as number, bonus as number:
    return salary + bonus

to greet with name as text, is_vip as boolean:
    if is_vip:
        say "Welcome VIP {name}!"
    else:
        say "Hello {name}!"
```

### Preconditions and Postconditions (`require` and `ensure`)
```doomscript
to withdraw with balance as number, amount as number:
    require amount is greater than 0 otherwise "Amount must be positive"
    require balance is at least amount otherwise "Insufficient funds"
    
    set new_balance to balance - amount
    ensure new_balance is at least 0
    return new_balance
```

### Typed Variable Declarations
```doomscript
set score as number to 100
set username as text to "DoomDev"
set flag as boolean to true
```

### Type Comparisons & Invariants
```doomscript
if score is a number and username is text:
    say "Types verified."

if score is not text and items is a list:
    say "Structure intact."
```

### Strict Compile-Time Checking
Pass `--strict` to `doom check` to inspect AST and detect literal contract mismatches statically before execution:
```bash
doom check script.doom --strict
```

---

## 30. How do I use English Pattern Matching and Destructuring? (Phase 9)
Expressive, multi-clause structural pattern matching and sequence unpacking in plain English:

### Multi-Branch Pattern Matching
```doomscript
to categorize with role:
    match role:
        when "admin":
            return "Full Access"
        when "guest" or "anon":
            return "Read Only"
        when a number where it is greater than 100:
            return "VIP Number"
        when a list:
            return "Group"
        when over 50:
            return "High Value"
        otherwise:
            return "Standard"
```

### English Destructuring & Unpacking
Unpack lists, tuples, or records into individual variables:
```doomscript
# Unpack list or tuple elements
unpack x, y, z from coordinates

# Extract dictionary / record fields by key
unpack name, age, city from user_profile

# List head / tail decomposition
first item into head, remaining items into tail from [10, 20, 30, 40]
# head == 10, tail == [20, 30, 40]
```

---

## 31. How do I write and run unit tests? (Phase 10)
DoomScript includes an integrated, zero-dependency English test runner:

### Writing Test Suites
Use `test "name":` and declarative English expectations:
```doomscript
test "calculator addition":
    set a to 10
    set b to 20
    expect a + b to equal 30

test "data validation":
    set user to {"name": "Alice", "age": 30}
    expect user to be a record
    expect user.age to be at least 18
    expect user.name to equal "Alice"

test "list operations":
    set fruits to ["apple", "banana"]
    expect fruits to be a list
    expect fruits to contain "banana"
```

### Running Tests from CLI
Execute tests with color-coded timings and diff reporting:
```bash
# Run all tests in the project (or tests/ directory)
doom test

# Run a specific test file
doom test tests/test_calc.doom
```

---

## 32. How do I build declarative CLI applications? (Phase 11)
Quickly define command-line interfaces with automatic help generation and argument parsing:

```doomscript
program description "DoomScript Data Processing Utility"

option input_file with default "data.csv" and description "Path to input file"
option max_rows as number with default 100 and description "Maximum rows to process"
flag verbose with description "Enable verbose logging"

parse arguments into cli_args

say "Processing file: {cli_args.input_file}"
say "Max rows: {cli_args.max_rows}"
if cli_args.verbose:
    say "Verbose mode enabled."
```

Run your script with standard CLI flags:
```bash
doom run app.doom -- --input_file data.txt --max_rows 500 --verbose
doom run app.doom -- --help
```

---

## 33. How do I run background tasks and concurrency? (Phase 12)
Execute long-running functions in parallel worker threads or apply execution timeouts:

### Spawning and Awaiting Tasks
```doomscript
to fetch_data with source:
    say "Fetching {source}..."
    return "Data from {source}"

# Run tasks concurrently in background worker threads
run in background fetch_data("Service A") into task1
run in background fetch_data("Service B") into task2

# Wait for individual task
wait for task1 into res1

# Wait for all background tasks
wait for all [task1, task2] into all_results
say "Combined results: {all_results}"
```

### Timeouts
Safely limit execution time for potentially slow operations:
```doomscript
timeout 2.0 seconds for slow_calculation() into calc_result
```

---

## 34. How do I create declarative web microservices? (Phase 13)
Build lightweight HTTP APIs with English declarative route handlers:

```doomscript
on get "/api/v1/status":
    reply with json {"status": "healthy", "uptime": 3600}

on get "/hello":
    reply with "Hello from DoomScript Web Server!"

on post "/api/v1/echo":
    reply with json {"message": "received"}

# Launch the microservice
serve on port 8080
```

---

## 35. How do I invoke AI and LLM models in English? (Phase 14)
Call LLMs directly from plain English with zero external dependencies:
```doomscript
# Natural text completion
ask ai "Explain recursion simply" into explanation
say explanation

# Structured JSON response
ask ai "Extract name and role from: Dr. Smith, Chief Surgeon" as json into parsed_data
say "Role:", parsed_data.role

# Specific model selection
ask ai "Analyze sentiment: I love this language!" with model "gemini-1.5-flash" into sentiment
```

---

## 36. How do I declare Database Entities and ORM queries? (Phase 15)
Define relational entities and execute typed queries without SQL:
```doomscript
define entity Customer with name as text, email as text, balance as number

save new Customer with name "Alice", email "alice@corp.com", balance 1500 into c1
save new Customer with name "Bob", email "bob@corp.com", balance 450 into c2

find all Customers into all_cust
find first Customer into top_cust
say "First customer:", top_cust.name
```

---

## 37. How do I generate automated API documentation? (Phase 16)
Generate interactive static HTML documentation sites for all `.doom` files:
```bash
doom doc
doom doc src/ --output docs/site/index.html
```

---

## 38. How do I build Markdown and HTML documents? (Phase 17)
Create reports, tables, and formatted documents in code:
```doomscript
create markdown document into report
add heading "Quarterly Executive Brief" at level 1 to report
add paragraph "All primary business objectives met for Q4." to report
add table with headers ["Product", "Sales"] and rows [["Enterprise", 85000], ["Pro", 42000]] to report
add bullet list ["Infrastructure scaled 4x", "Zero downtime deploy"] to report

render document report as markdown into md_text
render document report as html into html_page
save document report to file "output/executive_brief.md"
```

---

## 39. How do I use file watching and live reloading? (Phase 18)
Automatically re-run or re-test scripts whenever `.doom` files are modified:
```bash
doom watch script.doom
doom watch tests/ --action test
```

---

## 40. How do I schedule recurring jobs and timers? (Phase 19)
Schedule functions to execute at intervals without external cron daemons:
```doomscript
set heartbeats to {"count": 0}
to ping_healthcheck:
    increase heartbeats.count by 1
    say "Health check ping #{heartbeats.count}"

schedule every 5 seconds ping_healthcheck
run scheduler for 30 seconds
```

---

## 41. How do I use cryptography, hashing, and encryption? (Phase 20)
Secure hashing, random tokens, and authenticated encryption:
```doomscript
hash text "Password123" with algorithm "sha256" into password_hash
generate secure token of length 32 into session_token

encode text "Confidential data" as base64 into encoded_b64
decode base64 encoded_b64 into plain_text

encrypt text "Sensitive message" with secret "system_key_99" into cipher
decrypt text cipher with secret "system_key_99" into original_msg
```

---

## 42. How do I build streaming pipelines and process batches? (Phase 21)
Pipe data through transformations and process large datasets in chunks:
```doomscript
to sanitize with s: return s.strip()
to scream with s: return s.upper()

pipe "  hello doomscript  " into sanitize, scream into result

set records to [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
take first 3 items from records into top_three
drop first 7 items from records into bottom_three
batch records by 4 into chunks
```

---

## 43. How do I serialize binary buffers and hex numbers? (Phase 22)
Low-level hexadecimal and binary packing for network protocols and files:
```doomscript
convert number 4096 to hex into hex_addr
convert hex "0x1000" to number into decimal_val

pack numbers [10, 20, 30] as "int32" into bin_buffer
size of buffer bin_buffer in bytes into total_bytes
unpack binary "int32" from buffer bin_buffer into numbers_list
```

---

## 44. How do I manage INI, JSON, and ENV configuration? (Phase 23)
Unified configuration management for applications:
```doomscript
load config from "config.ini" into app_config
get config "server.host" with default "127.0.0.1" from app_config into host
set config "server.active" to true in app_config
save config app_config to file "config_backup.json"
```

---

## 45. How do I benchmark and profile script latency? (Phase 24)
Measure function throughput and latency:
```doomscript
to workload:
    set n to 0
    repeat with i from 1 to 1000:
        increase n by i

benchmark "Math Loop" with 500 iterations for workload into stats
```
Or from the CLI:
```bash
doom bench script.doom --iterations 20
```

---

## 46. How do I pack standalone zero-dependency executables? (Phase 25)
Package any `.doom` file into a single-file, portable `.pyz` executable bundle:
```bash
doom pack script.doom
# Produces script.pyz which runs anywhere without installing DoomScript:
python script.pyz
```

---

## 47. How do I manage processes, system resources & file locks? (Phases 26–32)
Execute commands with captured stdout/stderr, inspect processes, and handle cooperative cross-process locking:
```doomscript
# Piped subprocess execution
run command "whoami" piped into who_res
say "User: {who_res.stdout}, Return Code: {who_res.exit_code}"

# Process existence check
check if process "python" is running into is_running
if is_running:
    say "Python runtime is currently active"

# Disk metrics & System Path
get system disk space into disk_stats
say "Free Space: {disk_stats.free_gb} GB"
add directory "/opt/custom/bin" to system path

# Cross-process file locking
acquire file lock "app.lock" into lock_ref
# critical section ...
release file lock lock_ref
```

---

## 48. How do I resolve DNS, ping hosts & manage cookie jars? (Phases 33–40)
Standard-library network diagnostics and stateful HTTP session handling:
```doomscript
# Network Diagnostics
resolve dns of "example.com" into ip_list
say "IP Addresses: {ip_list}"

ping host "1.1.1.1" into ping_stat
say "Latency: {ping_stat.latency_ms} ms (Alive: {ping_stat.alive})"

# Stateful Cookie Jar
create cookie jar into jar
set cookie "token" to "abc-123-session" in jar
get cookie "token" from jar into auth_token
get cookie "theme" with default "dark" from jar into ui_theme
```

---

## 49. How do I compress data, create archives & calculate checksums? (Phases 41–48)
High-performance Gzip, BZ2, ZIP compression, CRC32/Adler32, and Great-Circle Geolocation:
```doomscript
# Gzip Compression & Decompression
compress text "High volume log stream" with gzip into compressed_bytes
decompress gzip compressed_bytes into restored_text

# BZ2 Compression & Decompression
compress text "High density dataset" with bz2 into bz2_bytes
decompress bz2 bz2_bytes into restored_bz2

# ZIP Archiving and Extraction
create zip archive "backup.zip" from files ["main.doom", "config.ini"]
extract zip archive "backup.zip" into folder "unpacked_dir"

# Checksums
calculate crc32 of "payload" into crc_hash
calculate adler32 of "payload" into adler_hash

# Geolocation Distance (Haversine formula in km)
calculate geo distance between 40.7128, -74.0060 and 34.0522, -118.2437 into dist_ny_la
say "Distance NYC to LA: {dist_ny_la} km"
```

---

## 50. How do I compute vector math, statistics & financial loans? (Phases 49–56)
Linear algebra, statistical distributions, compound interest, and amortization:
```doomscript
# Linear Algebra
vector [1, 2, 3] dot vector [4, 5, 6] into dot_product
vector magnitude of [3, 4] into length_vec
matrix [[1, 2], [3, 4]] multiply matrix [[2, 0], [1, 2]] into mat_product

# Descriptive Statistics
set sample to [10, 12, 15, 18, 20, 22, 25, 30]
standard deviation of sample into std_dev
variance of sample into var_res
median of sample into median_val

# Financial Mathematics
# Rate can be written as 7%, 0.07, or 7. Compounding defaults to annual:
compound interest on 5000 at 7% for 5 years into future_value
# Or specify compounding frequency (annually, semi-annually, quarterly, monthly, daily):
compound interest on 5000 at 7% for 5 years compounded monthly into monthly_fv
loan payment for principal 250000 rate 6.5% months 360 into monthly_mortgage
```

---

## 51. How do I build reactive event buses, priority queues & circuit breakers? (Phases 57–64)
Decoupled event-driven architectures, prioritized task queues, and fault-tolerant service breakers:
```doomscript
# Reactive Pub/Sub EventBus
create event bus into bus
to on_user_signup:
    say "New user notification received!"

event_subscribe("user.signup", on_user_signup)
publish event "user.signup" with data {"user": "Alice"}

# Priority Queue
create priority queue into task_queue
enqueue task "Background Report" with priority 100 into task_queue
enqueue task "Critical Security Alert" with priority 1 into task_queue
dequeue next task from task_queue into next_action

# Resilient Circuit Breaker
create circuit breaker named "payment_gateway" into gateway_breaker
to execute_payment:
    return "Payment Processed"

call circuit breaker gateway_breaker with execute_payment into tx_status
```

---

## 52. How do I generate SVG graphics & calculate record diffs? (Phases 65–72)
Generative vector graphics and object state difference analysis:
```doomscript
# Generative SVG Vector Graphics
create svg circle at 100, 100 radius 50 fill "#ff4444" into red_circle
create svg rect at 20, 20 width 160 height 40 fill "#336699" into blue_rect
create svg canvas width 300 height 300 with elements [red_circle, blue_rect] into svg_output

# Structural Record Diffing
set v1 to {"theme": "dark", "build": 10, "debug": false}
set v2 to {"theme": "light", "build": 11, "released": true}
diff records v1 and v2 into patch_diff
say "Changed fields: {patch_diff.changed}"
say "Added fields: {patch_diff.added}"
say "Removed fields: {patch_diff.removed}"
```

---

## 53. How do I build AI Agents, RAG indexes & conversation memory? (Phases 73–80)
Local vector retrieval-augmented generation and conversational history:
```doomscript
# Semantic Knowledge Index (Local Vector RAG with token BM25 scoring)
create knowledge index into brain_index
index document "doc1" text "DoomScript transpiles to Python AST" into brain_index
add document "doc2" with text "All standard libraries are self-contained" to brain_index
search knowledge index brain_index for "Python transpiler" into matches

# Vector Cosine Similarity
cosine similarity of [1.0, 0.0] and [0.8, 0.6] into sim_score

# Conversation Memory
create conversation memory into memory
remember in memory memory role "user" content "Hello, agent"
remember in memory memory role "assistant" content "Greetings, creator"
get recall history from memory into chat_transcript
```

---

## 54. How do I sign JWTs, hash passwords & mask PII? (Phases 81–88)
Zero-dependency cryptographic tokens, PBKDF2 salting, and privacy sanitization:
```doomscript
# JSON Web Tokens (HS256)
create jwt with payload {"sub": "user_123", "role": "admin"} and secret "supersecret" into jwt_token
verify jwt jwt_token with secret "supersecret" into claims

# PBKDF2 Secure Password Hashing
secure hash password "MyStrongPass123!" into password_hash
verify password "MyStrongPass123!" matches password_hash into valid_login

# Privacy Redaction & PII Masking
set dirty_text to "Send invoice to billing@corp.com or text 555-432-1000 regarding 123-45-6789"
mask pii in text dirty_text into clean_text
say clean_text
# Output: "Send invoice to [EMAIL_MASKED] or text [PHONE_MASKED] regarding [SSN_MASKED]"
```

---

## 55. How do I generate container configurations & export Prometheus metrics? (Phases 89–95)
Microservice observability and containerization:
```doomscript
# Automated Dockerfile Generation
generate dockerfile for entrypoint "server.doom" into dockerfile_text

# Prometheus Metrics
increment metric "api_requests_total"
increment metric "api_requests_total"
set metric "active_connections" to 42
export prometheus metrics into prometheus_scrape_data
```

---

## 56. How do I invoke C libraries (FFI) & minify DoomScript source? (Phases 96–100)
Low-level Foreign Function Interface with cross-platform libc resolution:
```doomscript
# Ctypes Foreign Function Interface (cross-platform libc support)
call c library "libc.so.6" function "abs" with args [-5] into abs_val
call c library "msvcrt" function "puts" with args ["Hello from C runtime!"] into result

# AST Minifier
set raw_code to "# Comment\nset x to 10\n\nset y to 20\nsay x + y"
minify doomscript raw_code into compact_code
say compact_code
```



