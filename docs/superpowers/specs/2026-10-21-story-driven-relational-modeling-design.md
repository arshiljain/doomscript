# Story-Driven Relational Modeling ("Living Domain Entities") Design Specification

**Status:** Draft / Pending Review  
**Date:** 2026-10-21  
**Author:** Pair Programming Agent & System Architect  
**Subsystem:** DoomScript Core Object Model, Entity Grammar & Phrases Normalizer  

---

## 1. Executive Summary

DoomScript has supported declarative entities (`a Person has name, age`) and natural classes with `to init with ...` and `my field = ...`. However, real-world domain and game systems require expressive object lifecycles, relational data models (one-to-many, many-to-one, one-to-one), and event-driven state transitions written as narrative English stories.

This specification introduces **Story-Driven Relational Modeling**:
1. **Initial State Lifecycles (`begins with`):** Define entities with initial default attributes and mutable structures without shared-default pitfalls.
2. **Declarative Relationships (`has many`, `belongs to`, `has one`):** Express entity relationships that maintain automatic bidirectional synchronization between collections and parent objects.
3. **Event-Driven State Transitions (`when ...`):** Define narrative event handlers and state transitions both within entity blocks and as standalone story rules.
4. **Spoken Action Invocations:** Trigger entity actions using conversational English phrases (`tell account to deposit 100`, `deposit 100 into account`, `withdraw 40 from account`) alongside canonical method calls.

---

## 2. Syntax & Grammar Specifications

### 2.1 Initial State & Entity Schemas (`begins with`)

#### Single-line Schema with Defaults:
```doomscript
a BankAccount begins with balance = 0, status = "active", transactions = []
```
*Also valid without leading article:*
```doomscript
BankAccount begins with balance = 0, status = "active", transactions = []
```

#### Block-Scoped Entity Declaration:
```doomscript
a BankAccount begins with balance = 0, status = "active":
    transactions = []
    
    when receiving amount:
        increase my balance by amount
        add amount to my transactions
        return my balance
```

#### Creation & Instantiation:
```doomscript
create a BankAccount into my_account
create a BankAccount with balance 500 into savings
```
- Missing parameters default to their specified `begins with` expressions.
- Mutable defaults (e.g. lists `[]`, records `{}`) are instantiated fresh per instance (using `copy.deepcopy` or lambda factory evaluation), preventing shared mutable state.

---

### 2.2 Declarative Relationships (`has many`, `belongs to`, `has one`)

#### Syntax Rules:
```doomscript
a User has name, email
a User has many Orders
an Order belongs to a User

a User has one Profile
a Profile belongs to a User
```

#### Pluralization & Property Name Resolution:
- `a User has many Orders` -> creates attribute `orders` on `User` initialized to a `RelationshipList(owner=self, inverse_name="user")`.
- `an Order belongs to a User` -> creates attribute `user = None` on `Order`.
- Case tolerance: `a User has many orders` or `a User has many Orders`.

#### Smart Bidirectional Synchronization:
1. **Adding to a Collection:**
   ```doomscript
   create a User with name "Alice" into u1
   create an Order with item "Book", price 20 into o1
   
   add o1 to u1's orders
   # u1's orders contains [o1]
   # o1's user is automatically u1!
   ```
2. **Assigning Parent Object:**
   ```doomscript
   create an Order with item "Laptop", price 1200 into o2
   o2's user = u1
   # u1's orders automatically contains o2!
   ```
3. **Loop & Recursion Safety:**
   - Synchronization employs an internal re-entrancy guard (`_in_sync`) on `DoomEntity` to prevent circular event recursion.

---

### 2.3 Event-Driven State Transitions (`when ...`)

#### Embedded In Entity Block:
```doomscript
a BankAccount begins with balance = 0:
    when receiving amount:
        increase my balance by amount
        return my balance

    when withdrawing amount:
        make sure my balance >= amount otherwise "Insufficient funds"
        decrease my balance by amount
        return my balance
```
- `when <action> with <args>:` and `when <action>:` desugar into instance methods `to <action> with <args>:`.
- Present-participle normalization: `receiving` normalizes to `receive` (or can be called as either `receive` or `receiving`).
- `my <prop>` seamlessly refers to `self.<prop>`.

#### Standalone Narrative Story Rules:
```doomscript
when a BankAccount receives amount:
    increase my balance by amount
    return my balance

when a BankAccount withdraws amount:
    make sure my balance >= amount otherwise "Insufficient funds"
    decrease my balance by amount
    return my balance
```
- Attaches the action handler to the target entity class.

---

### 2.4 Spoken Action Invocations

Actions defined on entities can be called using multiple natural English phrasings:

1. **Imperative Verb with Preposition (`into` / `from` / `to`):**
   ```doomscript
   deposit 100 into my_account
   # Desugars to: my_account.deposit(100) or my_account.receive(100)
   
   withdraw 40 from my_account
   # Desugars to: my_account.withdraw(40)
   ```
2. **Collaborative Directive (`tell <target> to ...`):**
   ```doomscript
   tell my_account to deposit 100
   tell my_account to withdraw 40
   # Desugars to: my_account.deposit(100) / my_account.withdraw(40)
   ```
3. **Canonical Method Call Parity:**
   ```doomscript
   my_account.deposit(100)
   my_account.withdraw(40)
   ```

---

## 3. Architecture & Runtime Design

### 3.1 Runtime Foundation: `src/doomscript/core/entity.py`

A new dedicated core module:
```python
class DoomEntity(Record):
    """Base class for all story-driven domain entities in DoomScript."""
    _relationships: Dict[str, Tuple[str, str]] # attr_name -> (rel_type, inverse_attr)
    ...
```

#### `RelationshipList` Class:
```python
class RelationshipList(list):
    def __init__(self, owner: Any, inverse_attr: str, iterable=None):
        super().__init__(iterable or [])
        self.owner = owner
        self.inverse_attr = inverse_attr

    def append(self, item: Any) -> None:
        super().append(item)
        if hasattr(item, self.inverse_attr):
            if getattr(item, self.inverse_attr) is not self.owner:
                setattr(item, self.inverse_attr, self.owner)
```

#### Inverse Assignment Interception:
In `DoomEntity.__setattr__`:
```python
if key in self._relations_belongs_to:
    target_rel = self._relations_belongs_to[key] # e.g. "orders" on User
    if value is not None and hasattr(value, target_rel):
        col = getattr(value, target_rel)
        if isinstance(col, list) and self not in col:
            col.append(self)
```

### 3.2 Compiler & Normalization Pipeline

1. **`src/doomscript/core/exports.py`:**
   - Expose `DoomEntity`, `RelationshipList` to the global execution scope.
2. **`src/doomscript/grammar/phrases.py`:**
   - Handle `a/an <Entity> begins with <defaults>:` and `a/an <Entity> begins with <defaults>`.
   - Handle relationship declarations:
     - `^(?:a|an)?\s*([A-Z]\w*)\s+has\s+many\s+([A-Za-z_]\w*)`
     - `^(?:a|an)?\s*([A-Z]\w*)\s+belongs\s+to\s+(?:a|an)?\s*([A-Z]\w*)`
     - `^(?:a|an)?\s*([A-Z]\w*)\s+has\s+one\s+([A-Za-z_]\w*)`
   - Handle `when <action> [with <args>]:` inside class suites.
   - Handle `when (?:a|an)?\s*([A-Z]\w*)\s+([a-z_]\w*)\s*(?:with\s+(.+?))?:` as standalone rules.
   - Handle spoken action calls:
     - `^\s*tell\s+(.+?)\s+to\s+([a-z_]\w*)(?:\s+(.+))?$` -> `\1.\2(\3)`
     - `^\s*deposit\s+(.+?)\s+into\s+(.+)$` -> `\2.deposit(\1)`
     - `^\s*withdraw\s+(.+?)\s+from\s+(.+)$` -> `\2.withdraw(\1)`

---

## 4. Verification & Testing Plan

### 4.1 Unit Test Suite: `tests/test_story_driven_entities.py`
1. **Initial State & Defaults:**
   - Test default scalars, strings, and independent mutable lists/dicts.
   - Test instantiation without arguments using defaults.
   - Test instantiation with custom overrides.
2. **Bidirectional Relationships:**
   - Test `User has many Orders` and `Order belongs to User`.
   - Verify `user.orders.append(order)` sets `order.user = user`.
   - Verify `order.user = user` appends `order` into `user.orders`.
   - Verify `user has one profile` / `profile belongs to user`.
3. **Event Transitions & Handlers (`when ...`):**
   - Test embedded `when receiving amount:` and `when withdrawing amount:`.
   - Test standalone `when a BankAccount receives amount:`.
   - Test assertion guards inside when blocks (`make sure ... otherwise ...`).
4. **Spoken Invocations:**
   - Test `tell account to deposit 100`.
   - Test `deposit 100 into account`.
   - Test `withdraw 40 from account`.
   - Test equivalence with `account.deposit(100)`.

### 4.2 Regression Gate
- Run all existing test suites: `tests/test_natural_classes.py`, `tests/test_thoughts_into_code.py`, `tests/test_deep_syntax_expansion.py`.
- Run Beginner UX Audit benchmark (85/85 must pass).
- Verify zero Python exception leakages.
