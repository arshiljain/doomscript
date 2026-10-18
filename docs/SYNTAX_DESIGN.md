# DoomScript Canonical Syntax Design & Specification

This document defines the canonical syntax specification, accepted natural aliases, operator precedence, ambiguity resolution, and backward-compatibility policies for DoomScript (`.doom`).

---

## 1. Design Philosophy

DoomScript follows the principle: **"Flexible on input, canonical in form, deterministic in execution."**

1. **One Canonical Form**: Every language feature has exactly one unambiguous, canonical syntax used in official documentation, error messages, compiler AST generation, and the `doom fmt` tool.
2. **Predictable English**: Natural English aliases are permitted for readability and beginner friendliness, but they normalize deterministically to the canonical representation.
3. **Strict Separation of Concerns**: Assignment and comparison are syntactically and semantically distinct. The `is` keyword is reserved strictly for comparisons and predicates.
4. **Idempotent Tooling**: Formatting canonicalizes supported aliases and structure without altering runtime semantics or corrupting string literals, expressions, or comments.

---

## 2. Canonical Syntax Specification

| Construct | Canonical Syntax | Example | Transpiled Python / Meaning |
|---|---|---|---|
| **Assignment** | `<target> = <expr>` | `score = 100` | `score = 100` |
| **Augmented Assign** | `<target> += <expr>`<br>`<target> -= <expr>`<br>`<target> *= <expr>`<br>`<target> /= <expr>` | `score += 10`<br>`balance -= 50` | `score += 10`<br>`balance -= 50` |
| **Output** | `say <expr>, ...` | `say "Score:", score` | `print("Score:", score)` |
| **Input** | `ask <prompt> into <target>`<br>`ask number <prompt> into <target>`<br>`ask boolean <prompt> into <target>` | `ask "Name: " into name`<br>`ask number "Age: " into age` | Interactive prompt or piped stdin reader |
| **Equality Comparison** | `<expr> equals <expr>` or `<expr> == <expr>` | `if status equals "active":` | `status == "active"` |
| **Inequality Comparison** | `<expr> is not <expr>` or `<expr> != <expr>` | `if status is not "banned":` | `status != "banned"` |
| **Relational Comparison** | `<expr> is greater than <expr>` (`>`)<br>`<expr> is less than <expr>` (`<`)<br>`<expr> is at least <expr>` (`>=`)<br>`<expr> is at most <expr>` (`<=`) | `if score is at least 90:`<br>`if age is greater than 18:` | `score >= 90`<br>`age > 18` |
| **Range Check** | `<expr> is between <min> and <max>` | `if age is between 18 and 65:` | `18 <= age <= 65` |
| **Membership** | `<expr> is in <collection>`<br>`<collection> contains <expr>` | `if role is in allowed_roles:`<br>`if items contains "apple":` | `role in allowed_roles`<br>`"apple" in items` |
| **One Of** | `<expr> is one of <collection>` | `if role is one of ["admin", "editor"]:` | `role in ["admin", "editor"]` |
| **Type Predicates** | `<expr> is a number`<br>`<expr> is text`<br>`<expr> is a boolean`<br>`<expr> is a list`<br>`<expr> is a record` | `if val is a number:`<br>`if s is text:` | `isinstance(val, (int, float))`<br>`isinstance(s, str)` |
| **Value Predicates** | `<expr> is empty`<br>`<expr> is even`<br>`<expr> is odd`<br>`<expr> is positive`<br>`<expr> is negative`<br>`<expr> is zero` | `if list is empty:`<br>`if count is even:` | `len(list) == 0`<br>`count % 2 == 0` |
| **Branching** | `if <cond>:`<br>`elif <cond>:`<br>`else:`<br>`unless <cond>:` | `if score > 80:`<br>`    say "Pass"`<br>`else:`<br>`    say "Retry"` | `if ...: elif ...: else ...:` |
| **Counted Loop** | `repeat <expr> times:` | `repeat 3 times:`<br>`    say "Hello"` | `for _ in range(3):` |
| **Range Loop** | `repeat with <var> from <start> to <end> [by <step>]:` | `repeat with i from 1 to 10 by 2:` | `for i in range(1, 11, 2):` |
| **Collection Loop** | `for each <var> in <collection>:`<br>`for each <var> in <collection> where <cond>:` | `for each person in users:`<br>`for each order in orders where order's amount > 100:` | `for person in users:`<br>`for order in (o for o in orders if ...):` |
| **While / Until Loop** | `while <cond>:`<br>`until <cond>:` | `while running:`<br>`until count is 10:` | `while running:`<br>`while not (count == 10):` |
| **Loop Control** | `skip`<br>`stop` | `if item is empty: skip`<br>`if found: stop` | `continue`<br>`break` |
| **Function Definition** | `to <name> with <arg1>, <arg2>:`<br>`to <name>:` | `to calculate_tax with price, rate:`<br>`    return price * rate` | `def calculate_tax(price, rate):` |
| **Return** | `return <expr>` | `return total` | `return total` |
| **Field Access** | `<record>'s <field>` or `<record>.<field>` | `user's email`<br>`order.total` | `user.get("email")` / `order.get("total")` |
| **Collection Indexing** | `item <n> of <list>` (1-based index) | `first = item 1 of items` | `items[0]` |
| **Collection Slices** | `first <n> items of <list>`<br>`last <n> items of <list>` | `top_five = first 5 items of scores` | `scores[:5]` |
| **Error Handling** | `try:`<br>`    ...`<br>`if it fails as <err>:`<br>`    ...`<br>`always:`<br>`    ...` | `try:`<br>`    read file "data.txt" into text`<br>`if it fails as err:`<br>`    say "Failed:", err`<br>`always:`<br>`    say "Done"` | `try ... except Exception as err: ... finally: ...` |
| **Data Querying** | `sort <col> by <field> [descending]`<br>`group <col> by <field> into <target>`<br>`<col> where <field> <op> <val> into <target>` | `sort sales by revenue descending`<br>`group orders by customer into by_cust` | In-memory table pipelines |

---

## 3. Accepted Aliases and Normalization Rules

DoomScript accepts familiar conversational and historical phrasings. The normalizer and `doom fmt` convert aliases into canonical statements as detailed below:

### 3.1 Assignment Aliases

| Alias Phrasing | Canonical Normalization | Example |
|---|---|---|
| `set <target> to <expr>` | `<target> = <expr>` | `set count to 10` $\to$ `count = 10` |
| `let <target> be <expr>` | `<target> = <expr>` | `let x be 42` $\to$ `x = 42` |
| `put <expr> into <target>` | `<target> = <expr>` | `put 100 into score` $\to$ `score = 100` |
| `assign <expr> to <target>` | `<target> = <expr>` | `assign 5 to attempts` $\to$ `attempts = 5` |
| `store <expr> in <target>` | `<target> = <expr>` | `store val in cache` $\to$ `cache = val` |
| `save <expr> as <target>` | `<target> = <expr>` | `save result as output` $\to$ `output = result` |
| `initialize <target> with <expr>` | `<target> = <expr>` | `initialize items with []` $\to$ `items = []` |
| `reset <target> to <expr>` | `<target> = <expr>` | `reset count to 0` $\to$ `count = 0` |
| `make <target> be <expr>` | `<target> = <expr>` | `make flag be true` $\to$ `flag = true` |
| `<target> is <expr>` *(Deprecated 1.x)* | `<target> = <expr>` | `score is 100` $\to$ `score = 100` |

### 3.2 Verb and Keyword Aliases

| Alias Phrasing | Canonical Normalization | Example |
|---|---|---|
| `print`, `print out`, `show`, `display`, `echo`, `tell`, `log` | `say` | `print "Hello"` $\to$ `say "Hello"` |
| `give back`, `hand back`, `yield back`, `result is` | `return` | `give back val` $\to$ `return val` |
| `otherwise if`, `else if` | `elif` | `otherwise if score > 80:` $\to$ `elif score > 80:` |
| `otherwise` | `else` | `otherwise:` $\to$ `else:` |
| `attempt ... if it/that fails` | `try ... if it fails` | `attempt:` $\to$ `try:` |
| `as long as <cond>:` | `while <cond>:` | `as long as running:` $\to$ `while running:` |
| `break`, `break out of loop`, `exit loop`, `stop loop` | `stop` | `break` $\to$ `stop` |
| `continue`, `skip to next`, `next iteration` | `skip` | `continue` $\to$ `skip` |
| `how to <name>:`, `define <name>:`, `function <name>:` | `to <name>:` | `how to add with a, b:` $\to$ `to add with a, b:` |

### 3.3 Comparison Aliases

| Alias Phrasing | Canonical Normalization |
|---|---|
| `is bigger than`, `is more than`, `is higher than`, `is longer than`, `is above`, `exceeds` | `is greater than` |
| `is smaller than`, `is lower than`, `is shorter than`, `is below` | `is less than` |
| `is greater than or equal to`, `is no less than`, `is no smaller than`, `is at minimum` | `is at least` |
| `is less than or equal to`, `is no greater than`, `is no more than`, `is at maximum` | `is at most` |
| `is equal to`, `is identical to`, `is strictly equal to`, `is the same as` | `equals` |
| `is not equal to`, `does not equal`, `is different from` | `is not` |
| `is within` | `is between` |

### 3.4 Filler Words

Leading polite filler words (`please`, `kindly`, `just`, `simply`, `go ahead and`, `go ahead`) are stripped automatically by the normalizer and `doom fmt`:
- `please say "Hello"` $\to$ `say "Hello"`
- `kindly set count to 10` $\to$ `count = 10`

---

## 4. Operator Precedence and Ambiguity Resolution

### 4.1 Operator Precedence (Highest to Lowest)

1. **Primary & Access**: Grouping `(...)`, Field access (`record's field`, `record.field`), Indexing (`item 1 of list`, `list[0]`), Slicing (`first N items of list`)
2. **Function Calls**: `func(a, b)`
3. **Exponentiation**: `to the power of`, `squared`, `math_pow`
4. **Unary**: `not`, `-` (negation)
5. **Multiplicative**: `*`, `/`, `mod`, `%`, `divided by`, `times`
6. **Additive**: `+`, `-`, `plus`, `minus`
7. **Comparisons & Predicates**:
   - Relational: `<`, `>`, `<=`, `>=`, `is greater than`, `is less than`, `is at least`, `is at most`
   - Equality: `==`, `!=`, `equals`, `is`, `is not`
   - Predicates: `is between`, `is in`, `is inside`, `is one of`, `is empty`, `is a number`, `is text`, `is even`, `is odd`, `is positive`, `is negative`, `is zero`
8. **Logical AND**: `and`
9. **Logical OR**: `or`
10. **Assignment**: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `set ... to`

### 4.2 Ambiguity Resolution: Assignment vs Comparison (`is`)

In historical versions of DoomScript, the `is` keyword was overloaded in the grammar to mean both assignment (`score is 100`) and comparison (`if score is 100:`). This introduced severe ambiguity:
- A standalone expression `x is 5` could be interpreted either as an assignment (`x = 5`) or as a discarded comparison (`x == 5`).
- Predicate checks like `x is positive` risked colliding with assignment semantics.

**Resolution Rule**:
1. **Grammar Decoupling**: In the formal Lark grammar (`doom.lark`), `assign_stmt` exclusively matches `target "=" expr`. The `is` token is removed completely from assignment rules and reserved exclusively for `CMP_OP` and predicate rules.
2. **Expression Context**: Inside expressions, conditions, and predicates (`if x is 5:`, `where status is "active"`, `until val is 0:`), `is` is **strictly an equality comparison** (`==`).
3. **Standalone Statement Context**: In standalone statement positions, legacy `target is expr` is normalized to `set target to expr` during the 1.x deprecation window, preserving backward compatibility while ensuring unambiguous AST generation.

---

## 5. Backward-Compatibility & Deprecation Policy

DoomScript adheres to Semantic Versioning (`MAJOR.MINOR.PATCH`):

### 5.1 The `target is expr` Assignment Deprecation Schedule
- **DoomScript 1.0.x**: Permitted `target is expr` as grammar assignment.
- **DoomScript 1.1.0 (Current)**:
  - Canonical assignment is established as `target = expr`.
  - Canonical Lark grammar recognizes `=` as the sole assignment operator.
  - `target is expr` assignment is marked **deprecated**.
  - The normalizer continues to rewrite standalone legacy assignments (`x is 10` $\to$ `set x to 10`) to guarantee existing scripts and test suites run without modification.
  - `doom fmt` automatically updates legacy assignments to `target = expr`.
- **DoomScript 2.0.0 (Target)**:
  - The legacy statement rewrite will be retired. Standalone `x is 10` will evaluate as a pure boolean comparison expression statement (`ast.Expr(ast.Compare(...))`), raising a compiler warning for unused comparison results.

### 5.2 Formatting Stability Guarantee
Running `doom fmt` on any valid DoomScript program:
1. Never alters program execution semantics or variable values.
2. Preserves all string literal content (including internal quotes, colons, or punctuation).
3. Preserves inline comments (`# ...`) and whole-line comments.
4. Normalizes indentation to standard 4-space blocks without silently deleting block levels.
5. Is guaranteed to be **idempotent**: formatting twice produces the exact same file as formatting once.
