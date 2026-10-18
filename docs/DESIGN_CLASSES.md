# DoomScript OOP Design Specification: English-First Classes

## Overview
Object-Oriented Programming (OOP) is a pillar of computer science education (CS2).
DoomScript provides a dual-syntax approach for classes:
1. **English-First Syntax**: An idiomatic, natural phrasing fitting DoomScript's philosophy.
2. **Python Fallback Syntax**: Standard Python-style `class Name:` and `class Name(Parent):` allowing students to seamlessly port or reference existing Python examples.

---

## 1. Class Declaration & Inheritance

### English-First Syntax
```doom
define a Stack:
    ...

define a MinStack that is a Stack:
    ...
```
Accepted variations:
- `define a <Name>:`
- `define an <Name>:`
- `define a <Name> that is a <Parent>:`
- `define a <Name> that extends <Parent>:`
- `define a <Name> inherits from <Parent>:`

### Python Syntax
```doom
class Stack:
    ...

class MinStack(Stack):
    ...
```

---

## 2. Constructor & Initialization (`__init__`)

In DoomScript, initialization uses the friendly `to start` phrase:
```doom
define a Stack:
    to start:
        my items = []
```
With parameters:
```doom
define a Node:
    to start with value:
        my value = value
        my next = none
```
Compiled to Python AST:
- `to start:` -> `def __init__(self):`
- `to start with value:` -> `def __init__(self, value):`

### Calling Base Class Constructors
To call the parent constructor, use `base start`:
```doom
define a MinStack that is a Stack:
    to start:
        base start
        my min_items = []
```
With arguments:
```doom
define a SpecialNode that is a Node:
    to start with val, tag:
        base start with val
        my tag = tag
```
Compiled to:
- `base start` -> `super().__init__()`
- `base start with val` -> `super().__init__(val)`

---

## 3. Instance Variables & Fields (`my` and `its`)

Within instance methods, refer to instance fields using `my <field>` or `its <field>`:
- `my items = []` -> `self.items = []`
- `my next = none` -> `self.next = None`
- `add x to my items` -> `self.items.append(x)`
- `count of my items` -> `len(self.items)`
- `say my value` -> `print(self.value)`

Standard `self.<field>` is also valid for direct Python interop.

---

## 4. Method Definitions & Implicit `self`

Methods are defined with `to <method> [with <params>]:`.
Inside a class block, `self` is automatically injected as the first parameter by the compiler if not explicitly declared:
```doom
define a Stack:
    to push with x:
        add x to my items

    to pop:
        return pop my items

    to is_empty:
        return count of my items == 0
```
Compiled to:
```python
class Stack:
    def push(self, x):
        self.items.append(x)

    def pop(self):
        return pop(self.items)

    def is_empty(self):
        return len(self.items) == 0
```

---

## 5. Dunder & Special Methods in English

Common Python dunders are expressed naturally in English:
- `to describe:` -> `def __repr__(self):` and `def __str__(self):`
- `to get length:` -> `def __len__(self):`
- `to get item with index:` -> `def __getitem__(self, index):`
- `to set item with index, value:` -> `def __setitem__(self, index, value):`

Example:
```doom
define a CustomList:
    to start:
        my data = []
    to describe:
        return "CustomList(" + str(my data) + ")"
    to get length:
        return len(my data)
    to get item with i:
        return my data[i]
```

---

## 6. Instance Creation and Usage

Instances are instantiated and invoked naturally:
```doom
st = Stack()
st.push(10)
st.push(20)
val = st.pop()
say val
```
