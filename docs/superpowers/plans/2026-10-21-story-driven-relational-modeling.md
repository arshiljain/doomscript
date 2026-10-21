# Story-Driven Relational Modeling ("Living Domain Entities") Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement Story-Driven Relational Modeling in DoomScript, enabling entities with initial state lifecycles (`begins with`), declarative smart-syncing relationships (`has many`, `belongs to`, `has one`), event-driven state transitions (`when ...`), and spoken action invocations (`tell account to deposit 100`, `deposit 100 into account`).

**Architecture:** Introduce `DoomEntity` and `RelationshipList` in `src/doomscript/core/entity.py` (extending `Record`) providing bidirectional reference management and recursion guards. Desugar `begins with` declarations, relationship statements, `when` event blocks, and spoken action verbs in `src/doomscript/grammar/phrases.py`.

**Tech Stack:** Python 3.10+, Lark Parser, AST Transformer, DoomScript Runtime Engine.

**Spec:** `docs/superpowers/specs/2026-10-21-story-driven-relational-modeling-design.md`

## Global Constraints
- Preserve 100% backward compatibility with existing classes, entities (`a Person has name, age`), and ORM entities (`define entity ...`).
- Zero Python exception leakage: all property and relational access errors must raise DoomScript-native exceptions or return `None` gracefully.
- Prevent infinite recursion during bidirectional relationship synchronization with re-entrancy flags.
- Mutable initial defaults (lists `[]`, dictionaries `{}`) must evaluate per-instance to prevent Python shared default argument traps.

## Review Focus
- Cyclic linking: adding an item already present in a relationship must not duplicate or cause infinite loops.
- Empty instantiation: creating an entity without arguments must cleanly populate all `begins with` defaults.
- Case tolerance: `a User has many orders` vs `a User has many Orders`.
- Present participle normalization: `when receiving amount:` must be callable via both `account.receive(100)` and `account.receiving(100)`.
- Preposition action calls: `deposit 100 into my_account` vs `withdraw 50 from my_account`.

---

### Task 1: Core Runtime Entity Base (`DoomEntity` and `RelationshipList`)

**Files:**
- Create: `src/doomscript/core/entity.py`
- Modify: `src/doomscript/core/exports.py`
- Create: `tests/test_story_driven_entities.py`

**Interfaces:**
- Produces: `DoomEntity` (subclass of `Record` with `_in_sync` flag and relational property hooks), `RelationshipList` (subclass of `list` with owner and inverse auto-sync on `append`).

- [ ] **Step 1: Write the failing unit tests for `DoomEntity` and `RelationshipList`**

```python
# in tests/test_story_driven_entities.py
from doomscript.core.entity import DoomEntity, RelationshipList

def test_relationship_list_auto_sync():
    class User(DoomEntity):
        pass

    class Order(DoomEntity):
        pass

    u = User({"name": "Alice"})
    u.orders = RelationshipList(owner=u, inverse_attr="user")
    o = Order({"item": "Book"})

    u.orders.append(o)
    assert o.user is u
    assert len(u.orders) == 1

def test_entity_inverse_assignment_sync():
    class User(DoomEntity):
        pass

    class Order(DoomEntity):
        _relations_belongs_to = {"user": "orders"}

    u = User({"name": "Alice"})
    u.orders = RelationshipList(owner=u, inverse_attr="user")
    o = Order({"item": "Laptop"})

    o.user = u
    assert o in u.orders
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_story_driven_entities.py -v`  
Expected: FAIL with `ModuleNotFoundError: No module named 'doomscript.core.entity'`

- [ ] **Step 3: Implement `DoomEntity` and `RelationshipList` in `src/doomscript/core/entity.py` and register in `exports.py`**

Provide `RelationshipList` with `append(item)` and `extend(items)` updating `item.<inverse_attr> = owner` safely, and `DoomEntity` overriding `__setattr__` with `_in_sync` guard to update inverse collections. Expose both in `src/doomscript/core/exports.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_story_driven_entities.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/core/entity.py src/doomscript/core/exports.py tests/test_story_driven_entities.py
git commit -m "feat(core): add DoomEntity and RelationshipList runtime foundation"
```

---

### Task 2: Initial State Lifecycles (`begins with`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/test_story_driven_entities.py`

**Interfaces:**
- Consumes: `DoomEntity` from Task 1.
- Produces: Phrase normalization for `[a|an] <Entity> begins with <field> = <val>, ...[:]`.

- [ ] **Step 1: Write the failing tests for `begins with` single-line and block declarations**

```python
def test_entity_begins_with_defaults():
    source = """
a BankAccount begins with balance = 100, status = "active", transactions = []

create a BankAccount into acc1
create a BankAccount with balance 500 into acc2

add 50 to acc1.transactions
"""
    env = execute(source)
    assert env["acc1"].balance == 100
    assert env["acc1"].status == "active"
    assert env["acc1"].transactions == [50]
    assert env["acc2"].balance == 500
    assert env["acc2"].transactions == []  # Not shared with acc1!
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_story_driven_entities.py::test_entity_begins_with_defaults -v`  
Expected: FAIL (syntax/normalization error on `begins with`)

- [ ] **Step 3: Implement `begins with` normalization in `src/doomscript/grammar/phrases.py`**

Parse `(?:(?:a|an)\s+)?([A-Z]\w*)\s+begins\s+with\s+(.+?)(:)?$` in line loop:
- Extract field assignments `name = default_expr`.
- Generate class inheriting from `DoomEntity` with `to init with ...` parameter defaults and per-instance deepcopy or default assignments for collections.
- Support both single line and indented block bodies.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_story_driven_entities.py::test_entity_begins_with_defaults -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/grammar/phrases.py tests/test_story_driven_entities.py
git commit -m "feat(grammar): add entity begins with initial state lifecycle"
```

---

### Task 3: Declarative Relationships (`has many`, `belongs to`, `has one`)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/test_story_driven_entities.py`

**Interfaces:**
- Consumes: `RelationshipList` from Task 1.
- Produces: Normalization for `[a|an] <Entity> has many <Target>`, `[a|an] <Entity> belongs to [a|an] <Target>`, `[a|an] <Entity> has one <Target>`.

- [ ] **Step 1: Write failing tests for declarative relationships and inverse syncing**

```python
def test_declarative_relationships_smart_sync():
    source = """
a User has name
an Order has item, price

a User has many Orders
an Order belongs to a User

create a User with name "Alice" into u1
create an Order with item "Laptop", price 1200 into o1

add o1 to u1.orders
"""
    env = execute(source)
    assert env["o1"].user is env["u1"]
    assert env["u1"].orders == [env["o1"]]

    # Test inverse assignment sync
    source2 = """
a User has name
an Order has item, price

a User has many Orders
an Order belongs to a User

create a User with name "Bob" into u2
create an Order with item "Book", price 15 into o2

o2.user = u2
"""
    env2 = execute(source2)
    assert env2["o2"] in env2["u2"].orders
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_story_driven_entities.py::test_declarative_relationships_smart_sync -v`  
Expected: FAIL (syntax error on `has many` / `belongs to`)

- [ ] **Step 3: Implement relationship normalization in `src/doomscript/grammar/phrases.py`**

- Recognize `a/an <Entity> has many <Target>` -> register `RelationshipList` initialization in `<Entity>`.
- Recognize `a/an <Entity> belongs to a/an <Target>` -> register inverse link attribute in `<Entity>`.
- Recognize `a/an <Entity> has one <Target>` -> register one-to-one synchronization.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_story_driven_entities.py::test_declarative_relationships_smart_sync -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/grammar/phrases.py tests/test_story_driven_entities.py
git commit -m "feat(grammar): add declarative has many and belongs to relationships"
```

---

### Task 4: Event-Driven State Transitions (`when ...` Embedded and Standalone)

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/test_story_driven_entities.py`

**Interfaces:**
- Produces: Normalization for `when <action> [with <args>]:` inside entity definitions, and `when [a|an] <Entity> <action> [with <args>]:` standalone.

- [ ] **Step 1: Write failing tests for `when` event handlers**

```python
def test_embedded_and_standalone_when_handlers():
    source = """
a BankAccount begins with balance = 0:
    when receiving amount:
        increase my balance by amount
        return my balance

    when withdrawing amount:
        make sure my balance >= amount otherwise "Insufficient funds"
        decrease my balance by amount
        return my balance

create a BankAccount into acc
acc.receive(100)
acc.withdraw(30)
"""
    env = execute(source)
    assert env["acc"].balance == 70
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_story_driven_entities.py::test_embedded_and_standalone_when_handlers -v`  
Expected: FAIL

- [ ] **Step 3: Implement `when` handler rewrites in `src/doomscript/grammar/phrases.py`**

Inside class blocks:
- `^\s*when\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?))?:` -> normalize present participles (`receiving` -> `receive`, `withdrawing` -> `withdraw`) and emit `to <verb> with <args>:`. Also alias the present participle if different.
Standalone:
- `^\s*when\s+(?:a|an\s+)?([A-Z]\w*)\s+([A-Za-z_]\w*)(?:\s+with\s+(.+?))?:` -> generate method and attach to entity class.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_story_driven_entities.py::test_embedded_and_standalone_when_handlers -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/grammar/phrases.py tests/test_story_driven_entities.py
git commit -m "feat(grammar): add embedded and standalone when event transitions"
```

---

### Task 5: Spoken Action Invocations

**Files:**
- Modify: `src/doomscript/grammar/phrases.py`
- Modify: `tests/test_story_driven_entities.py`

**Interfaces:**
- Produces: Normalization for `tell <target> to <action> <args...>`, `deposit <amount> into <target>`, `withdraw <amount> from <target>`.

- [ ] **Step 1: Write failing tests for spoken action calls**

```python
def test_spoken_action_invocations():
    source = """
a BankAccount begins with balance = 0:
    when receiving amount:
        increase my balance by amount
        return my balance
    when withdrawing amount:
        make sure my balance >= amount otherwise "Insufficient funds"
        decrease my balance by amount
        return my balance

create a BankAccount into my_account

deposit 100 into my_account
tell my_account to withdraw 40
"""
    env = execute(source)
    assert env["my_account"].balance == 60
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_story_driven_entities.py::test_spoken_action_invocations -v`  
Expected: FAIL

- [ ] **Step 3: Implement spoken action invocations in `src/doomscript/grammar/phrases.py`**

Add statement normalizations:
- `tell <target> to <action> <arg...>` -> `<target>.<action>(<arg...>)`
- `deposit <amount> into <target>` -> `<target>.deposit(<amount>)` or `.receive(<amount>)`
- `withdraw <amount> from <target>` -> `<target>.withdraw(<amount>)`
Add `tell`, `deposit`, `withdraw` to `STATEMENT_START_KEYWORDS`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_story_driven_entities.py::test_spoken_action_invocations -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/doomscript/grammar/phrases.py tests/test_story_driven_entities.py
git commit -m "feat(grammar): add spoken action invocations"
```

---

### Task 6: Full Regression & Verification Gate

**Files:**
- Test: `tests/test_story_driven_entities.py`
- Test: `scratch/audit_beginner_phrasings.py`
- Test: Key regression suites

- [ ] **Step 1: Run all tests in `tests/test_story_driven_entities.py`**

Run: `python -m pytest tests/test_story_driven_entities.py -v`  
Expected: ALL PASS

- [ ] **Step 2: Run the 85-point Beginner UX Audit**

Run: `python scratch/audit_beginner_phrasings.py`  
Expected: 85/85 PASS, 0 syntax errors, 0 compilation errors, 0 Python leaks.

- [ ] **Step 3: Run comprehensive regression suites**

Run: `python -m pytest tests/test_deep_syntax_expansion.py tests/test_thoughts_into_code.py tests/test_sentence_chaining.py tests/test_expression_statement_parity.py tests/test_natural_predicates.py tests/test_natural_parity.py tests/test_natural_operations.py tests/test_natural_classes.py tests/domains/test_cross_domain_showcases.py tests/test_syntax_quality.py`  
Expected: ALL PASS.

- [ ] **Step 4: Commit and Push**

```bash
git push origin main
```
