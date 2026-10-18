# DoomScript Core Specification (The 30 Guaranteed Stable Forms)

> **Stability Guarantee**: Every program written exclusively with these 30 forms is guaranteed to compile and execute identically across all DoomScript versions and platforms. We deliberately keep this core small and rock-solid to avoid the unpredictability of historical English-like languages.

---

## The Core 30 Forms

### 1. Output
- **Statement**: `say <expr>` or `say <expr>, <expr>, ...`
- **Example**: `say "Hello, world!"` / `say "Total:", total, "Status:", status`

### 2. Assignment
- **Canonical Statement**: `<target> = <expr>`
- **Supported English Alias**: `set <target> to <expr>`
- **Deprecated Legacy Statement (1.x)**: `<target> is <expr>` (deprecated; use `=`; `is` is reserved for comparisons)
- **Example**: `total = 500` / `set count to 10` / `status = "active"`

### 3. Augmented Assignment & Mutation
- **Statements**:
  - `<target> += <expr>`, `<target> -= <expr>`, `<target> *= <expr>`, `<target> /= <expr>`
  - `increase <target> by <expr>`
  - `decrease <target> by <expr>`
- **Example**: `increase score by 15` / `decrease balance by 50`

### 4. Arithmetic & Mathematical Functions
- **Operators**: `+`, `-`, `*`, `/`
- **Expressions**:
  - `<percent>% of <expr>`
  - `absolute of <expr>` / `abs of <expr>`
  - `square root of <expr>` / `sqrt of <expr>`
  - `round of <expr> to <decimals> decimals` / `round of <expr>`
- **Example**: `say 15% of 200` / `say round of 3.14159 to 2 decimals`

### 5. Comparisons
- **Forms**:
  - `==`, `!=`, `<`, `>`, `<=`, `>=`
  - `is`, `is not` / `isn't`
  - `is greater than` / `is over`
  - `is less than` / `is under`
  - `is at least` / `is at most`
- **Example**: `if score is over 90:` / `if amount is at least 100:`

### 6. Range & Membership
- **Forms**:
  - `<expr> is between <min> and <max>`
  - `<expr> is one of <collection>`
  - `<collection> contains <item>`
- **Example**: `if age is between 18 and 65:` / `if role is one of ["admin", "editor"]:`

### 7. Math & Parity Predicates
- **Forms**:
  - `<expr> is even`, `<expr> is odd`
  - `<expr> is positive`, `<expr> is negative`, `<expr> is zero`
- **Example**: `if count is even:` / `if balance is positive:`

### 8. Boolean Logic
- **Operators**: `and`, `or`, `not`
- **Example**: `if is_admin and not is_banned:`

### 9. Branching (If / Else / Elif)
- **Forms**: Colons `:` are optional.
- **Example**:
  ```doomscript
  if score is over 90:
      say "Grade A"
  elif score is over 80:
      say "Grade B"
  else:
      say "Grade C"
  ```

### 10. Negative Conditionals (Unless)
- **Form**: `unless <condition>:`
- **Example**:
  ```doomscript
  unless is_ready:
      say "Please wait..."
  ```

### 11. Counted Loops
- **Form**: `repeat <N> times:`
- **Example**:
  ```doomscript
  repeat 3 times:
      say "DoomScript!"
  ```

### 12. Range Loops
- **Form**: `repeat with <var> from <start> to <stop> [by <step>]:`
- **Example**:
  ```doomscript
  repeat with i from 1 to 5:
      say "Step", i
  ```

### 13. While & Until Loops
- **Forms**:
  - `repeat while <cond>:` / `while <cond>:`
  - `repeat until <cond>:` / `until <cond>:`
- **Example**:
  ```doomscript
  repeat while count > 0:
      decrease count by 1
  ```

### 14. Iteration Loops
- **Form**: `for each <item> in <collection>:`
- **Example**:
  ```doomscript
  for each name in customers:
      say "Hello", name
  ```

### 15. Functions & Return Values
- **Form**: `to <name> [with <param1>, <param2>]: ... return <val>`
- **Example**:
  ```doomscript
  to calculate_tax with price, rate:
      return price * rate
  ```

### 16. Lists
- **Literals**: `[item1, item2, item3]`
- **Append**: `add <item> to <list>` / `append <item> to <list>`
- **Example**:
  ```doomscript
  set tasks to ["eat", "sleep"]
  add "code" to tasks
  ```

### 17. List Element Accessors
- **Forms**:
  - `item <i> of <list>` (1-indexed English)
  - `first item of <list>`
  - `last item of <list>`
- **Example**: `say first item of tasks` / `say item 2 of tasks`

### 18. Sorting (Statement & Expression)
- **Statement**: `sort <list> [by <field>] [descending]`
- **Expression**: `sorted of <list>`
- **Example**:
  ```doomscript
  sort scores descending
  set ordered to sorted of scores
  ```

### 19. Reversing (Statement & Expression)
- **Statement**: `reverse <list>`
- **Expression**: `reversed of <list>`
- **Example**:
  ```doomscript
  reverse items
  set backwards to reversed of items
  ```

### 20. Deduplication (Statement & Expression)
- **Statement**: `unique items of <list> into <target>`
- **Expression**: `unique of <list>`
- **Example**:
  ```doomscript
  unique items of raw_ids into clean_ids
  set distinct to unique of raw_ids
  ```

### 21. Aggregates
- **Forms**:
  - `count of <col>` / `length of <col>`
  - `sum of <col>`
  - `average of <col>`
  - `highest in <col>` / `maximum in <col>`
  - `lowest in <col>` / `minimum in <col>`
- **Example**: `say "Average:", average of test_scores`

### 22. Declarative Collection Filtering
- **Form**: `<collection> where <field> <op> <val> into <target>`
- **Example**:
  ```doomscript
  orders where status is "paid" into paid_orders
  paid_orders where amount is over 100 into high_value
  ```

### 23. Records (Dictionaries / Objects)
- **Literal**: `{field: value, ...}`
- **Field Access**: `<record>'s <field>` or `<record>.<field>`
- **Example**:
  ```doomscript
  set user to {name: "Alice", role: "admin"}
  say user's name
  ```

### 24. String Transformation (Statement & Expression)
- **Trim**: `trim <text> into <target>` | `trim of <text>`
- **Uppercase**: `uppercase <text> into <target>` | `uppercase of <text>`
- **Lowercase**: `lowercase <text> into <target>` | `lowercase of <text>`
- **Example**:
  ```doomscript
  trim raw_email into clean_email
  set title to uppercase of book_name
  ```

### 25. Explicit Type Coercion
- **Forms**:
  - `<expr> as number` (coerces strings/floats to numbers)
  - `<expr> as text` (coerces to string)
  - `<expr> as boolean` (coerces to boolean)
- **Example**:
  ```doomscript
  set total to (row's amount as number) * 1.1
  ```

### 26. Text File I/O
- **Forms**:
  - `read file <path> into <target>`
  - `write <text> into file <path>`
  - `append <text> to file <path>`
- **Example**: `write "Log entry" into file "audit.log"`

### 27. CSV Data Processing (Auto-Coerced)
- **Forms**:
  - `read csv file <path> into <target>` (Auto-coerces numeric columns)
  - `write csv <rows> into file <path>`
  - `append csv <row> to file <path>`
- **Example**:
  ```doomscript
  read csv file "data.csv" into rows
  write csv clean_rows into file "report.csv"
  ```

### 28. JSON Data Processing (Auto-Coerced)
- **Forms**:
  - `parse json <text> into <target>` (Auto-coerces numeric values into Records)
  - `convert <obj> to json into <target>`
  - `fetch json from <url> into <target>`
- **Example**:
  ```doomscript
  parse json payload into order
  say order's total
  ```

### 29. Interactive User Input
- **Forms**:
  - `ask <prompt> into <target>` (Text input, handles piped input cleanly)
  - `ask number <prompt> into <target>` (Numeric input)
  - `ask choice <prompt> from <options> into <target>`
- **Example**: `ask "Enter your name:" into username`

### 30. Robust Error Handling
- **Form**:
  ```doomscript
  try:
      total = 100 / 0
  if it fails as problem:
      say "Caught error:", problem
  ```

---

## Experimental Extensions

Any features outside the Core 30 are designated as **Experimental Extensions**:
- C Foreign Function Interface (`call c library ...`)
- Vector Knowledge Index & semantic embeddings
- Reactive Pub/Sub Event Bus & Circuit Breakers
- WebGL & SVG Generation
- DNS, Ping, and Raw Network Sockets

While available, experimental features may evolve or require platform-specific permissions. For all production scripting, automations, and data reports, **stick to the 30 Core Forms**.
