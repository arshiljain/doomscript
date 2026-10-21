"""
DoomScript Beginner UX Syntax & Usability Audit Script
Tests 65+ intuitive English phrasings against DoomScript's parser and engine.
Evaluates outcomes, captures exact error messages, and detects Python leakage.
"""

import sys
import io
import os
import json
import traceback
from typing import Dict, Any, List, Optional

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = r"C:\Users\kanha\.gemini\antigravity\scratch\doomscript"
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "src"))

from doomscript.compiler.engine import compile_to_ast, transpile, execute
from doomscript.grammar.phrases import normalize
from doomscript.exceptions import DoomScriptSyntaxError, DoomError, DoomSyntaxError, DoomScopeError

TEST_CASES = [
    # -------------------------------------------------------------------------
    # 1. ARITHMETIC & NUMERIC PREDICATES / MUTATIONS
    # -------------------------------------------------------------------------
    {
        "id": "ARITH-01",
        "category": "Arithmetic & Predicates",
        "name": "Canonical increase by",
        "code": "x = 10\nincrease x by 1\nsay x",
        "expected": "x becomes 11, prints 11",
    },
    {
        "id": "ARITH-02",
        "category": "Arithmetic & Predicates",
        "name": "Canonical decrease by",
        "code": "x = 10\ndecrease x by 2\nsay x",
        "expected": "x becomes 8, prints 8",
    },
    {
        "id": "ARITH-03",
        "category": "Arithmetic & Predicates",
        "name": "Natural 'add 5 to x' (numeric addition)",
        "code": "x = 10\nadd 5 to x\nsay x",
        "expected": "x becomes 15",
    },
    {
        "id": "ARITH-04",
        "category": "Arithmetic & Predicates",
        "name": "Natural 'double x'",
        "code": "x = 10\ndouble x\nsay x",
        "expected": "x becomes 20",
    },
    {
        "id": "ARITH-05",
        "category": "Arithmetic & Predicates",
        "name": "Natural 'halve x'",
        "code": "x = 20\nhalve x\nsay x",
        "expected": "x becomes 10",
    },
    {
        "id": "ARITH-06",
        "category": "Arithmetic & Predicates",
        "name": "Natural 'multiply x by 3'",
        "code": "x = 10\nmultiply x by 3\nsay x",
        "expected": "x becomes 30",
    },
    {
        "id": "ARITH-07",
        "category": "Arithmetic & Predicates",
        "name": "Natural 'divide x by 2'",
        "code": "x = 10\ndivide x by 2\nsay x",
        "expected": "x becomes 5.0",
    },
    {
        "id": "ARITH-08",
        "category": "Arithmetic & Predicates",
        "name": "Predicate 'if x is even:'",
        "code": "x = 10\nif x is even:\n    say \"EVEN\"\nelse:\n    say \"ODD\"",
        "expected": "prints EVEN",
    },
    {
        "id": "ARITH-09",
        "category": "Arithmetic & Predicates",
        "name": "Predicate 'if x is odd:'",
        "code": "x = 11\nif x is odd:\n    say \"ODD\"\nelse:\n    say \"EVEN\"",
        "expected": "prints ODD",
    },
    {
        "id": "ARITH-10",
        "category": "Arithmetic & Predicates",
        "name": "Predicate 'if x is between 10 and 20:'",
        "code": "x = 15\nif x is between 10 and 20:\n    say \"IN_RANGE\"",
        "expected": "prints IN_RANGE",
    },
    {
        "id": "ARITH-11",
        "category": "Arithmetic & Predicates",
        "name": "Predicate 'if x is outside 10 and 20:'",
        "code": "x = 25\nif x is outside 10 and 20:\n    say \"OUTSIDE\"",
        "expected": "prints OUTSIDE",
    },
    {
        "id": "ARITH-12",
        "category": "Arithmetic & Predicates",
        "name": "Predicate 'if x is divisible by 5:'",
        "code": "x = 25\nif x is divisible by 5:\n    say \"DIVISIBLE\"",
        "expected": "prints DIVISIBLE",
    },

    # -------------------------------------------------------------------------
    # 2. COLLECTIONS & LISTS
    # -------------------------------------------------------------------------
    {
        "id": "COLL-01",
        "category": "Collections & Lists",
        "name": "Bracket list literal",
        "code": "numbers = [1, 2, 3]\nsay numbers",
        "expected": "prints [1, 2, 3]",
    },
    {
        "id": "COLL-02",
        "category": "Collections & Lists",
        "name": "'numbers = a list of 1, 2, 3'",
        "code": "numbers = a list of 1, 2, 3\nsay numbers",
        "expected": "prints [1, 2, 3]",
    },
    {
        "id": "COLL-03",
        "category": "Collections & Lists",
        "name": "'numbers is a list of 1, 2, 3'",
        "code": "numbers is a list of 1, 2, 3\nsay numbers",
        "expected": "prints [1, 2, 3]",
    },
    {
        "id": "COLL-04",
        "category": "Collections & Lists",
        "name": "'create a list of numbers from 1 to 10'",
        "code": "create a list of numbers from 1 to 10\nsay numbers",
        "expected": "numbers is [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
    },
    {
        "id": "COLL-05",
        "category": "Collections & Lists",
        "name": "'create a list of numbers from 1 to 10 into numbers'",
        "code": "create a list of numbers from 1 to 10 into numbers\nsay numbers",
        "expected": "numbers is [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
    },
    {
        "id": "COLL-06",
        "category": "Collections & Lists",
        "name": "'make a list of numbers from 1 to 10 into numbers'",
        "code": "make a list of numbers from 1 to 10 into numbers\nsay numbers",
        "expected": "numbers is [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
    },
    {
        "id": "COLL-07",
        "category": "Collections & Lists",
        "name": "'make a list of squares from 1 to 5'",
        "code": "make a list of squares from 1 to 5\nsay that",
        "expected": "creates squares list [1, 4, 9, 16, 25]",
    },
    {
        "id": "COLL-08",
        "category": "Collections & Lists",
        "name": "'make a list of squares from 1 to 5 into sq'",
        "code": "make a list of squares from 1 to 5 into sq\nsay sq",
        "expected": "sq is [1, 4, 9, 16, 25]",
    },
    {
        "id": "COLL-09",
        "category": "Collections & Lists",
        "name": "Loop with parity: 'for each number in numbers: if number is even: say number'",
        "code": "numbers = [1, 2, 3, 4, 5, 6]\nfor each number in numbers:\n    if number is even:\n        say number",
        "expected": "prints 2, 4, 6",
    },
    {
        "id": "COLL-10",
        "category": "Collections & Lists",
        "name": "Standalone query 'how many items in numbers'",
        "code": "numbers = [1, 2, 3]\nhow many items in numbers",
        "expected": "evaluates to 3 or returns 3",
    },
    {
        "id": "COLL-11",
        "category": "Collections & Lists",
        "name": "Say count: 'say how many items in numbers'",
        "code": "numbers = [1, 2, 3]\nsay how many items in numbers",
        "expected": "prints 3",
    },
    {
        "id": "COLL-12",
        "category": "Collections & Lists",
        "name": "Canonical 'say count of numbers'",
        "code": "numbers = [1, 2, 3]\nsay count of numbers",
        "expected": "prints 3",
    },
    {
        "id": "COLL-13",
        "category": "Collections & Lists",
        "name": "Length of: 'say length of numbers'",
        "code": "numbers = [1, 2, 3]\nsay length of numbers",
        "expected": "prints 3",
    },
    {
        "id": "COLL-14",
        "category": "Collections & Lists",
        "name": "Possessive length: 'say numbers's length'",
        "code": "numbers = [1, 2, 3]\nsay numbers's length",
        "expected": "prints 3",
    },
    {
        "id": "COLL-15",
        "category": "Collections & Lists",
        "name": "Canonical 'say first item of numbers'",
        "code": "numbers = [10, 20, 30]\nsay first item of numbers",
        "expected": "prints 10",
    },
    {
        "id": "COLL-16",
        "category": "Collections & Lists",
        "name": "Canonical 'say last item of numbers'",
        "code": "numbers = [10, 20, 30]\nsay last item of numbers",
        "expected": "prints 30",
    },
    {
        "id": "COLL-17",
        "category": "Collections & Lists",
        "name": "Natural 1-based indexing: 'say item 2 of numbers'",
        "code": "numbers = [10, 20, 30]\nsay item 2 of numbers",
        "expected": "prints 20",
    },
    {
        "id": "COLL-18",
        "category": "Collections & Lists",
        "name": "Out of bounds access: 'say item 10 of numbers'",
        "code": "numbers = [10, 20, 30]\nsay item 10 of numbers",
        "expected": "friendly out-of-bounds error or None, NOT raw IndexError",
    },
    {
        "id": "COLL-19",
        "category": "Collections & Lists",
        "name": "Natural 'add 10 to numbers'",
        "code": "numbers = [1, 2, 3]\nadd 10 to numbers\nsay numbers",
        "expected": "numbers is [1, 2, 3, 10]",
    },
    {
        "id": "COLL-20",
        "category": "Collections & Lists",
        "name": "Natural 'remove 2 from numbers' (item in list)",
        "code": "numbers = [1, 2, 3]\nremove 2 from numbers\nsay numbers",
        "expected": "numbers is [1, 3]",
    },
    {
        "id": "COLL-21",
        "category": "Collections & Lists",
        "name": "Natural 'remove 99 from numbers' (item not in list)",
        "code": "numbers = [1, 2, 3]\nremove 99 from numbers\nsay numbers",
        "expected": "friendly warning or no-op, NOT raw Python ValueError",
    },
    {
        "id": "COLL-22",
        "category": "Collections & Lists",
        "name": "In-place sort: 'sort numbers'",
        "code": "numbers = [3, 1, 2]\nsort numbers\nsay numbers",
        "expected": "numbers is [1, 2, 3]",
    },
    {
        "id": "COLL-23",
        "category": "Collections & Lists",
        "name": "Expression sort: 'sorted_nums = sorted numbers'",
        "code": "numbers = [3, 1, 2]\nsorted_nums = sorted numbers\nsay sorted_nums",
        "expected": "sorted_nums is [1, 2, 3]",
    },

    # -------------------------------------------------------------------------
    # 3. TEXT & STRINGS
    # -------------------------------------------------------------------------
    {
        "id": "STR-01",
        "category": "Text & Strings",
        "name": "Canonical 'split \"a b c\" by \" \" into words'",
        "code": "split \"a b c\" by \" \" into words\nsay words",
        "expected": "words is ['a', 'b', 'c']",
    },
    {
        "id": "STR-02",
        "category": "Text & Strings",
        "name": "'set words to split \"a b c\" by \" \"'",
        "code": "set words to split \"a b c\" by \" \"\nsay words",
        "expected": "words is ['a', 'b', 'c']",
    },
    {
        "id": "STR-03",
        "category": "Text & Strings",
        "name": "'words is split \"a b c\" by \" \"'",
        "code": "words is split \"a b c\" by \" \"\nsay words",
        "expected": "words is ['a', 'b', 'c']",
    },
    {
        "id": "STR-04",
        "category": "Text & Strings",
        "name": "Standalone statement 'join words with \", \"'",
        "code": "words = [\"a\", \"b\", \"c\"]\njoin words with \", \"\nsay that",
        "expected": "evaluates to 'a, b, c'",
    },
    {
        "id": "STR-05",
        "category": "Text & Strings",
        "name": "Canonical 'join words with \", \" into text'",
        "code": "words = [\"a\", \"b\", \"c\"]\njoin words with \", \" into text\nsay text",
        "expected": "text is 'a, b, c'",
    },
    {
        "id": "STR-06",
        "category": "Text & Strings",
        "name": "Expression 'set text to join words with \", \"'",
        "code": "words = [\"a\", \"b\", \"c\"]\nset text to join words with \", \"\nsay text",
        "expected": "text is 'a, b, c'",
    },
    {
        "id": "STR-07",
        "category": "Text & Strings",
        "name": "Assignment 'text = join words with \", \"'",
        "code": "words = [\"a\", \"b\", \"c\"]\ntext = join words with \", \"\nsay text",
        "expected": "text is 'a, b, c'",
    },
    {
        "id": "STR-08",
        "category": "Text & Strings",
        "name": "In-place 'replace \"cat\" with \"dog\" in sentence'",
        "code": "sentence = \"the cat is happy\"\nreplace \"cat\" with \"dog\" in sentence\nsay sentence",
        "expected": "sentence becomes 'the dog is happy'",
    },
    {
        "id": "STR-09",
        "category": "Text & Strings",
        "name": "Canonical 'replace \"cat\" with \"dog\" in sentence into new_text'",
        "code": "sentence = \"the cat is happy\"\nreplace \"cat\" with \"dog\" in sentence into new_text\nsay new_text",
        "expected": "new_text is 'the dog is happy'",
    },
    {
        "id": "STR-10",
        "category": "Text & Strings",
        "name": "Expression 'set new_text to replace \"cat\" with \"dog\" in sentence'",
        "code": "sentence = \"the cat is happy\"\nset new_text to replace \"cat\" with \"dog\" in sentence\nsay new_text",
        "expected": "new_text is 'the dog is happy'",
    },
    {
        "id": "STR-11",
        "category": "Text & Strings",
        "name": "Standalone 'trim \"  hello  \"'",
        "code": "trim \"  hello  \"\nsay that",
        "expected": "evaluates to 'hello'",
    },
    {
        "id": "STR-12",
        "category": "Text & Strings",
        "name": "Canonical 'trim \"  hello  \" into cleaned'",
        "code": "trim \"  hello  \" into cleaned\nsay cleaned",
        "expected": "cleaned is 'hello'",
    },
    {
        "id": "STR-13",
        "category": "Text & Strings",
        "name": "Expression 'say trim of \"  hello  \"'",
        "code": "say trim of \"  hello  \"",
        "expected": "prints hello",
    },
    {
        "id": "STR-14",
        "category": "Text & Strings",
        "name": "Standalone 'uppercase \"hello\"'",
        "code": "uppercase \"hello\"\nsay that",
        "expected": "evaluates to 'HELLO'",
    },
    {
        "id": "STR-15",
        "category": "Text & Strings",
        "name": "'uppercase \"hello\" into up'",
        "code": "uppercase \"hello\" into up\nsay up",
        "expected": "up is 'HELLO'",
    },
    {
        "id": "STR-16",
        "category": "Text & Strings",
        "name": "Canonical 'convert \"hello\" to uppercase into up'",
        "code": "convert \"hello\" to uppercase into up\nsay up",
        "expected": "up is 'HELLO'",
    },
    {
        "id": "STR-17",
        "category": "Text & Strings",
        "name": "Expression 'say uppercase of \"hello\"'",
        "code": "say uppercase of \"hello\"",
        "expected": "prints HELLO",
    },
    {
        "id": "STR-18",
        "category": "Text & Strings",
        "name": "Standalone 'lowercase \"HELLO\"'",
        "code": "lowercase \"HELLO\"\nsay that",
        "expected": "evaluates to 'hello'",
    },
    {
        "id": "STR-19",
        "category": "Text & Strings",
        "name": "'lowercase \"HELLO\" into low'",
        "code": "lowercase \"HELLO\" into low\nsay low",
        "expected": "low is 'hello'",
    },
    {
        "id": "STR-20",
        "category": "Text & Strings",
        "name": "Predicate 'if name starts with \"Dr.\"'",
        "code": "name = \"Dr. Watson\"\nif name starts with \"Dr.\":\n    say \"DOCTOR\"",
        "expected": "prints DOCTOR",
    },
    {
        "id": "STR-21",
        "category": "Text & Strings",
        "name": "Predicate 'if file ends with \".csv\"'",
        "code": "file = \"data.csv\"\nif file ends with \".csv\":\n    say \"CSV\"",
        "expected": "prints CSV",
    },
    {
        "id": "STR-22",
        "category": "Text & Strings",
        "name": "Predicate 'if sentence contains \"error\"'",
        "code": "sentence = \"system failed with error\"\nif sentence contains \"error\":\n    say \"FOUND_ERROR\"",
        "expected": "prints FOUND_ERROR",
    },
    {
        "id": "STR-23",
        "category": "Text & Strings",
        "name": "Predicate 'if name does not start with \"Dr.\"'",
        "code": "name = \"John\"\nif name does not start with \"Dr.\":\n    say \"CIVILIAN\"",
        "expected": "prints CIVILIAN",
    },

    # -------------------------------------------------------------------------
    # 4. ENTITIES, OBJECTS & RECORDS
    # -------------------------------------------------------------------------
    {
        "id": "ENT-01",
        "category": "Entities & Records",
        "name": "Natural schema 'a Person has name, age'",
        "code": "a Person has name, age",
        "expected": "declares Person entity schema",
    },
    {
        "id": "ENT-02",
        "category": "Entities & Records",
        "name": "ORM schema 'define entity Person with name as text, age as number'",
        "code": "define entity Person with name as text, age as number",
        "expected": "registers entity schema",
    },
    {
        "id": "ENT-03",
        "category": "Entities & Records",
        "name": "Natural instantiation 'create a Person with name \"Alice\", age 30 into p1'",
        "code": "create a Person with name \"Alice\", age 30 into p1\nsay p1's name",
        "expected": "p1 created, prints Alice",
    },
    {
        "id": "ENT-04",
        "category": "Entities & Records",
        "name": "ORM save 'save new Person with name: \"Alice\", age: 30 into p1'",
        "code": "define entity Person with name as text, age as number\nsave new Person with name: \"Alice\", age: 30 into p1\nsay p1's name",
        "expected": "prints Alice",
    },
    {
        "id": "ENT-05",
        "category": "Entities & Records",
        "name": "Dictionary record shorthand",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\nsay p1's name",
        "expected": "prints Alice",
    },
    {
        "id": "ENT-06",
        "category": "Entities & Records",
        "name": "Missing field access 'p1's missing_field'",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\nsay p1's missing_field",
        "expected": "friendly missing property explanation, NOT raw KeyError/AttributeError",
    },
    {
        "id": "ENT-07",
        "category": "Entities & Records",
        "name": "Direct possessive assignment 'p1's name = \"Bob\"'",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\np1's name = \"Bob\"\nsay p1's name",
        "expected": "prints Bob",
    },
    {
        "id": "ENT-08",
        "category": "Entities & Records",
        "name": "Set possessive 'set p1's name to \"Bob\"'",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\nset p1's name to \"Bob\"\nsay p1's name",
        "expected": "prints Bob",
    },
    {
        "id": "ENT-09",
        "category": "Entities & Records",
        "name": "Natural verb 'change p1's name to \"Bob\"'",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\nchange p1's name to \"Bob\"\nsay p1's name",
        "expected": "prints Bob",
    },
    {
        "id": "ENT-10",
        "category": "Entities & Records",
        "name": "Natural verb 'modify p1's name to \"Bob\"'",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\nmodify p1's name to \"Bob\"\nsay p1's name",
        "expected": "prints Bob",
    },
    {
        "id": "ENT-11",
        "category": "Entities & Records",
        "name": "Natural verb 'update p1's name to \"Bob\"'",
        "code": "p1 = {\"name\": \"Alice\", \"age\": 30}\nupdate p1's name to \"Bob\"\nsay p1's name",
        "expected": "prints Bob",
    },
    {
        "id": "ENT-12",
        "category": "Entities & Records",
        "name": "Class definition with 'to init with name:' and 'my name = name'",
        "code": "class Person:\n    to init with name:\n        my name = name\np = Person(\"Alice\")\nsay p's name",
        "expected": "prints Alice",
    },
    {
        "id": "ENT-13",
        "category": "Entities & Records",
        "name": "Class definition with 'constructor with name:' and 'my name = name'",
        "code": "class Person:\n    constructor with name:\n        my name = name\np = Person(\"Alice\")\nsay p's name",
        "expected": "prints Alice",
    },
    {
        "id": "ENT-14",
        "category": "Entities & Records",
        "name": "Class definition requiring Python '__init__' and 'self'",
        "code": "class Person:\n    to __init__ with self, name:\n        self.name = name\np = Person(\"Alice\")\nsay p's name",
        "expected": "prints Alice (Pythonic style)",
    },
    {
        "id": "ENT-15",
        "category": "Entities & Records",
        "name": "Class accessing undefined property 'p's height'",
        "code": "class Person:\n    constructor with name:\n        my name = name\np = Person(\"Alice\")\nsay p's height",
        "expected": "friendly property error, NOT raw AttributeError",
    },

    # -------------------------------------------------------------------------
    # 5. INPUT, OUTPUT & ERROR HANDLING
    # -------------------------------------------------------------------------
    {
        "id": "IO-01",
        "category": "Input & Output",
        "name": "Canonical 'say \"Hello World\"'",
        "code": "say \"Hello World\"",
        "expected": "prints Hello World",
    },
    {
        "id": "IO-02",
        "category": "Input & Output",
        "name": "Say multiple values",
        "code": "name = \"Alice\"\nage = 30\nsay \"Name:\", name, \"Age:\", age",
        "expected": "prints Name: Alice Age: 30",
    },
    {
        "id": "IO-03",
        "category": "Input & Output",
        "name": "Canonical 'ask \"What is your name?\" into name'",
        "code": "ask \"What is your name?\" into name\nsay \"Hello \", name",
        "expected": "reads user name and prints greeting",
        "stdin": "Charlie\n",
    },
    {
        "id": "IO-04",
        "category": "Input & Output",
        "name": "Intuitive trailing cast 'ask \"What is your age?\" into age as number'",
        "code": "ask \"What is your age?\" into age as number\nsay age + 5",
        "expected": "reads age, converts to int/float, prints age+5",
        "stdin": "25\n",
    },
    {
        "id": "IO-05",
        "category": "Input & Output",
        "name": "Prefix type cast 'ask number \"What is your age?\" into age'",
        "code": "ask number \"What is your age?\" into age\nsay age + 5",
        "expected": "reads age as number, prints age+5",
        "stdin": "25\n",
    },
    {
        "id": "IO-06",
        "category": "Input & Output",
        "name": "Prefix type cast 'ask boolean \"Continue?\" into confirmed'",
        "code": "ask boolean \"Continue?\" into confirmed\nsay \"Confirmed: \", confirmed",
        "expected": "reads bool confirmation, prints true/false",
        "stdin": "yes\n",
    },
    {
        "id": "IO-07",
        "category": "Error Handling",
        "name": "Assertion pass 'verify that age is at least 18 otherwise \"Must be an adult\"'",
        "code": "age = 20\nverify that age is at least 18 otherwise \"Must be an adult\"\nsay \"Access granted\"",
        "expected": "prints Access granted",
    },
    {
        "id": "IO-08",
        "category": "Error Handling",
        "name": "Assertion fail 'verify that age is at least 18 otherwise \"Must be an adult\"'",
        "code": "age = 16\nverify that age is at least 18 otherwise \"Must be an adult\"",
        "expected": "fails with message 'Must be an adult', check if AssertionError leaks",
        "expect_error": "DoomAssertionError",
    },
    {
        "id": "IO-09",
        "category": "Error Handling",
        "name": "Canonical 'try: ... if that fails: ...'",
        "code": "try:\n    x = 10 / 0\nif that fails:\n    say \"CAUGHT_ERROR\"",
        "expected": "recovers gracefully, prints CAUGHT_ERROR",
    },
    {
        "id": "IO-10",
        "category": "Error Handling",
        "name": "Canonical 'try: ... if it fails: ...'",
        "code": "try:\n    x = 10 / 0\nif it fails:\n    say \"CAUGHT_ERROR\"",
        "expected": "recovers gracefully, prints CAUGHT_ERROR",
    },
    {
        "id": "IO-11",
        "category": "Error Handling",
        "name": "Try with exception naming 'if that fails as problem:'",
        "code": "try:\n    x = 10 / 0\nif that fails as problem:\n    say \"ERROR: \", problem",
        "expected": "prints caught problem",
    },
    {
        "id": "IO-12",
        "category": "Error Handling",
        "name": "Natural phrasing 'try: ... if there is an error: ...'",
        "code": "try:\n    x = 10 / 0\nif there is an error:\n    say \"RECOVERED\"",
        "expected": "recovers gracefully",
    },
]

PYTHON_LEAK_KEYWORDS = [
    "AttributeError",
    "TypeError",
    "IndexError",
    "KeyError",
    "ValueError",
    "NameError",
    " AssertionError",
    "SyntaxError",
    "__init__",
    "self",
    "list index out of range",
    "has no attribute 'append'",
    "has no attribute 'remove'",
    "traceback",
    "object has no attribute",
]

def detect_python_leakage(text: str) -> List[str]:
    leaks = []
    for kw in PYTHON_LEAK_KEYWORDS:
        if kw.lower() in text.lower():
            leaks.append(kw)
    return list(set(leaks))

def run_single_test(tc: Dict[str, Any]) -> Dict[str, Any]:
    test_id = tc["id"]
    code = tc["code"]
    expected = tc["expected"]
    stdin_content = tc.get("stdin", "")

    result = {
        "id": test_id,
        "category": tc["category"],
        "name": tc["name"],
        "code": code,
        "expected": expected,
        "status": "UNKNOWN",
        "normalized_code": "",
        "transpiled_code": "",
        "stdout": "",
        "error_type": None,
        "error_message": "",
        "suggestion": None,
        "python_leakage": [],
        "details": "",
    }

    # 1. Normalization check
    try:
        norm = normalize(code)
        result["normalized_code"] = norm
    except Exception as e:
        result["status"] = "NORMALIZATION_ERROR"
        result["error_type"] = type(e).__name__
        result["error_message"] = str(e)
        result["python_leakage"] = detect_python_leakage(str(e))
        return result

    # 2. Compilation check
    try:
        py_ast = compile_to_ast(code)
        import ast
        result["transpiled_code"] = ast.unparse(py_ast)
    except DoomScriptSyntaxError as se:
        result["status"] = "SYNTAX_ERROR"
        result["error_type"] = "DoomScriptSyntaxError"
        result["error_message"] = str(se)
        result["suggestion"] = getattr(se, "suggestion", None)
        result["python_leakage"] = detect_python_leakage(str(se))
        return result
    except Exception as ce:
        result["status"] = "COMPILATION_ERROR"
        result["error_type"] = type(ce).__name__
        result["error_message"] = str(ce)
        result["python_leakage"] = detect_python_leakage(str(ce))
        return result

    # 3. Runtime execution check
    old_stdout = sys.stdout
    old_stdin = sys.stdin
    captured_stdout = io.StringIO()
    sys.stdout = captured_stdout

    if stdin_content:
        sys.stdin = io.StringIO(stdin_content)
    else:
        sys.stdin = io.StringIO("")

    try:
        exec_env = execute(code)
        captured = captured_stdout.getvalue()
        result["stdout"] = captured.strip()
        result["status"] = "SUCCESS"
    except Exception as re_err:
        captured = captured_stdout.getvalue()
        result["stdout"] = captured.strip()
        result["status"] = "RUNTIME_ERROR"
        result["error_type"] = type(re_err).__name__
        result["error_message"] = str(re_err)
        tb_str = traceback.format_exc()
        result["details"] = tb_str
        err_name = type(re_err).__name__
        result["python_leakage"] = detect_python_leakage(f"{err_name}: {str(re_err)}")
        if tc.get("expect_error") and tc.get("expect_error") == err_name:
            result["status"] = "SUCCESS"
    finally:
        sys.stdout = old_stdout
        sys.stdin = old_stdin

    return result

def main():
    print(f"Executing DoomScript Beginner UX Audit on {len(TEST_CASES)} intuitive phrasings...")
    results = []
    
    summary_counts = {
        "SUCCESS": 0,
        "SYNTAX_ERROR": 0,
        "COMPILATION_ERROR": 0,
        "RUNTIME_ERROR": 0,
        "NORMALIZATION_ERROR": 0,
    }
    
    leakage_count = 0

    for idx, tc in enumerate(TEST_CASES, start=1):
        res = run_single_test(tc)
        results.append(res)
        st = res["status"]
        summary_counts[st] = summary_counts.get(st, 0) + 1
        if res["python_leakage"]:
            leakage_count += 1
        print(f"[{idx:02d}/{len(TEST_CASES)}] {res['id']}: {res['name']} -> {res['status']}")

    # Save JSON results
    json_path = os.path.join(WORKSPACE_ROOT, "scratch", "audit_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved detailed JSON to {json_path}")

    # Summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY:")
    print("=" * 60)
    for k, v in summary_counts.items():
        print(f"  {k:20s}: {v}")
    print(f"  Cases with Python Leaks : {leakage_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
