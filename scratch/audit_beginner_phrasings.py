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
        "expect_error": ["AssertionError", "DoomAssertionError", "DoomError"],
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

    # -------------------------------------------------------------------------
    # 6. THOUGHT-TO-CODE PHASE 1: DISCOURSE PRONOUNS & QUANTIFIERS
    # -------------------------------------------------------------------------
    {
        "id": "P1-01",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Pronoun 'it' after assignment",
        "code": "x = 10\ndouble it\nsay x",
        "expected": "x becomes 20, prints 20",
    },
    {
        "id": "P1-02",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Pronoun 'it' in condition",
        "code": "score = 95\nif it is at least 90:\n    say \"EXCELLENT\"",
        "expected": "prints EXCELLENT",
    },
    {
        "id": "P1-03",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Dual referents 'it' (singular) and 'them' (plural)",
        "code": "numbers = [1, 2, 3]\nx = 10\nadd x to them\nsay count of numbers",
        "expected": "count becomes 4",
    },
    {
        "id": "P1-04",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Pronoun 'that' referring to previous result",
        "code": "x = 5\ndouble it\nhalve that\nsay x",
        "expected": "x becomes 5",
    },
    {
        "id": "P1-05",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Possessive 'its' property access",
        "code": "user = {\"name\": \"Alice\", \"age\": 30}\nsay its name",
        "expected": "prints Alice",
    },
    {
        "id": "P1-06",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Plural 'their count' query",
        "code": "items = [10, 20, 30]\nsay their count",
        "expected": "prints 3",
    },
    {
        "id": "P1-07",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Universal quantifier 'all numbers are even'",
        "code": "numbers = [2, 4, 6]\nif all numbers are even:\n    say \"ALL_EVEN\"",
        "expected": "prints ALL_EVEN",
    },
    {
        "id": "P1-08",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Universal quantifier 'every x in numbers is positive'",
        "code": "numbers = [1, 2, 3]\nif every x in numbers is positive:\n    say \"ALL_POS\"",
        "expected": "prints ALL_POS",
    },
    {
        "id": "P1-09",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Universal quantifier false branch",
        "code": "numbers = [2, 3, 4]\nif all numbers are even:\n    say \"YES\"\nelse:\n    say \"NOT_ALL\"",
        "expected": "prints NOT_ALL",
    },
    {
        "id": "P1-10",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Existential quantifier 'any x in mixed is odd'",
        "code": "mixed = [2, 3, 4]\nif any x in mixed is odd:\n    say \"HAS_ODD\"",
        "expected": "prints HAS_ODD",
    },
    {
        "id": "P1-11",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Existential quantifier false branch",
        "code": "evens = [2, 4, 6]\nif any x in evens is odd:\n    say \"YES\"\nelse:\n    say \"NONE_ODD\"",
        "expected": "prints NONE_ODD",
    },
    {
        "id": "P1-12",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Negative quantifier 'no x in list is negative'",
        "code": "clean = [1, 2, 3]\nif no x in clean is negative:\n    say \"ALL_NON_NEG\"",
        "expected": "prints ALL_NON_NEG",
    },
    {
        "id": "P1-13",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Negative quantifier false branch",
        "code": "dirty = [1, -2, 3]\nif no x in dirty is negative:\n    say \"CLEAN\"\nelse:\n    say \"HAS_NEG\"",
        "expected": "prints HAS_NEG",
    },
    {
        "id": "P1-14",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Universal quantifier 'all items are positive'",
        "code": "vals = [10, 20]\nif all vals are positive:\n    say \"POSITIVE\"",
        "expected": "prints POSITIVE",
    },
    {
        "id": "P1-15",
        "category": "Discourse Pronouns & Quantifiers",
        "name": "Plural membership 'in them'",
        "code": "fruits = [\"apple\", \"banana\"]\nif \"apple\" is in them:\n    say \"FOUND\"",
        "expected": "prints FOUND",
    },

    # -------------------------------------------------------------------------
    # 7. THOUGHT-TO-CODE PHASE 2: CONTEXTUAL ATTRIBUTES, SUPERLATIVES & WHOSE
    # -------------------------------------------------------------------------
    {
        "id": "P2-01",
        "category": "Contextual Attributes & Superlatives",
        "name": "Contextual attribute filter 'keep only orders where price > 100'",
        "code": "orders = [{\"id\": 1, \"price\": 150}, {\"id\": 2, \"price\": 50}]\nkeep only orders where price > 100\nsay count of orders",
        "expected": "prints 1",
    },
    {
        "id": "P2-02",
        "category": "Contextual Attributes & Superlatives",
        "name": "Contextual attribute discard 'discard from orders where price >= 100'",
        "code": "orders = [{\"id\": 1, \"price\": 150}, {\"id\": 2, \"price\": 50}]\ndiscard from orders where price >= 100\nsay count of orders",
        "expected": "prints 1",
    },
    {
        "id": "P2-03",
        "category": "Contextual Attributes & Superlatives",
        "name": "Compound contextual attribute filter",
        "code": "users = [{\"name\": \"Alice\", \"active\": true, \"age\": 25}, {\"name\": \"Bob\", \"active\": false, \"age\": 30}]\nkeep only users where age > 20 and active is true\nsay count of users",
        "expected": "prints 1",
    },
    {
        "id": "P2-04",
        "category": "Contextual Attributes & Superlatives",
        "name": "Relative clause loop 'whose role is admin'",
        "code": "users = [{\"name\": \"Alice\", \"role\": \"admin\"}, {\"name\": \"Bob\", \"role\": \"user\"}]\nfor each user in users whose role is \"admin\":\n    say user's name",
        "expected": "prints Alice",
    },
    {
        "id": "P2-05",
        "category": "Contextual Attributes & Superlatives",
        "name": "Relative clause loop numeric 'whose score >= 90'",
        "code": "students = [{\"name\": \"A\", \"score\": 95}, {\"name\": \"B\", \"score\": 70}]\nfor each s in students whose score >= 90:\n    say s's name",
        "expected": "prints A",
    },
    {
        "id": "P2-06",
        "category": "Contextual Attributes & Superlatives",
        "name": "Superlative 'find largest order in orders by amount into top'",
        "code": "orders = [{\"id\": 1, \"amount\": 100}, {\"id\": 2, \"amount\": 300}, {\"id\": 3, \"amount\": 200}]\nfind the largest order in orders by amount into top\nsay top's id",
        "expected": "prints 2",
    },
    {
        "id": "P2-07",
        "category": "Contextual Attributes & Superlatives",
        "name": "Superlative 'find cheapest item in items by price into best'",
        "code": "items = [{\"name\": \"Pen\", \"price\": 5}, {\"name\": \"Book\", \"price\": 20}]\nfind the cheapest item in items by price into best\nsay best's name",
        "expected": "prints Pen",
    },
    {
        "id": "P2-08",
        "category": "Contextual Attributes & Superlatives",
        "name": "Superlative 'find oldest person in people by age into elder'",
        "code": "people = [{\"name\": \"Anna\", \"age\": 25}, {\"name\": \"Grandpa\", \"age\": 80}]\nfind the oldest person in people by age into elder\nsay elder's name",
        "expected": "prints Grandpa",
    },
    {
        "id": "P2-09",
        "category": "Contextual Attributes & Superlatives",
        "name": "Superlative 'find newest event in events by timestamp into latest'",
        "code": "events = [{\"name\": \"E1\", \"timestamp\": 100}, {\"name\": \"E2\", \"timestamp\": 200}]\nfind the newest event in events by timestamp into latest\nsay latest's name",
        "expected": "prints E2",
    },
    {
        "id": "P2-10",
        "category": "Contextual Attributes & Superlatives",
        "name": "Superlative 'find smallest number in nums into min_val'",
        "code": "nums = [15, 3, 42, 8]\nfind the smallest n in nums by x into min_n\nsay min_n",
        "expected": "prints 3",
    },
    {
        "id": "P2-11",
        "category": "Contextual Attributes & Superlatives",
        "name": "Superlative 'find highest score in scores into top'",
        "code": "scores = [88, 92, 79, 99]\nfind the highest s in scores by x into top\nsay top",
        "expected": "prints 99",
    },
    {
        "id": "P2-12",
        "category": "Contextual Attributes & Superlatives",
        "name": "Relative clause loop 'whose status is done'",
        "code": "tasks = [{\"title\": \"T1\", \"status\": \"done\"}, {\"title\": \"T2\", \"status\": \"todo\"}]\nfor each t in tasks whose status is \"done\":\n    say t's title",
        "expected": "prints T1",
    },
    {
        "id": "P2-13",
        "category": "Contextual Attributes & Superlatives",
        "name": "Contextual attribute filter on dict items",
        "code": "items = [{\"val\": 10}, {\"val\": 50}]\nkeep only items where val > 20\nsay count of items",
        "expected": "prints 1",
    },
    {
        "id": "P2-14",
        "category": "Contextual Attributes & Superlatives",
        "name": "Filter with equality on string attribute",
        "code": "people = [{\"name\": \"Alice\", \"dept\": \"eng\"}, {\"name\": \"Bob\", \"dept\": \"sales\"}]\nkeep only people where dept is \"eng\"\nsay count of people",
        "expected": "prints 1",
    },
    {
        "id": "P2-15",
        "category": "Contextual Attributes & Superlatives",
        "name": "Discard with equality on string attribute",
        "code": "people = [{\"name\": \"Alice\", \"dept\": \"eng\"}, {\"name\": \"Bob\", \"dept\": \"sales\"}]\ndiscard from people where dept is \"sales\"\nsay count of people",
        "expected": "prints 1",
    },

    # -------------------------------------------------------------------------
    # 8. THOUGHT-TO-CODE PHASE 3: DECLARATIVE RESILIENCE & COMPOUND ACTIONS
    # -------------------------------------------------------------------------
    {
        "id": "P3-01",
        "category": "Resilience & Compound Actions",
        "name": "Adverbial qualifier 'retrying 3 times'",
        "code": "attempts = [0]\nto flaky:\n    attempts[0] = attempts[0] + 1\n    if attempts[0] < 2:\n        make error \"Flaky error\"\n    return 42\ncall flaky retrying 3 times into res\nsay res",
        "expected": "prints 42",
    },
    {
        "id": "P3-02",
        "category": "Resilience & Compound Actions",
        "name": "Adverbial qualifier with backoff",
        "code": "attempts = [0]\nto flaky:\n    attempts[0] = attempts[0] + 1\n    if attempts[0] < 2:\n        make error \"Transient\"\n    return \"OK\"\ncall flaky retrying 2 times with 0.01 seconds backoff into res\nsay res",
        "expected": "prints OK",
    },
    {
        "id": "P3-03",
        "category": "Resilience & Compound Actions",
        "name": "Adverbial qualifier with timeout",
        "code": "to fast_op:\n    return 99\ncall fast_op with timeout of 2 seconds into res\nsay res",
        "expected": "prints 99",
    },
    {
        "id": "P3-04",
        "category": "Resilience & Compound Actions",
        "name": "Adverbial qualifier caching",
        "code": "calls = [0]\nto compute_expensive:\n    calls[0] = calls[0] + 1\n    return calls[0]\ncall compute_expensive caching for 5 minutes into r1\ncall compute_expensive caching for 5 minutes into r2\nsay r1, r2",
        "expected": "prints 1 1",
    },
    {
        "id": "P3-05",
        "category": "Resilience & Compound Actions",
        "name": "Adverbial qualifier bare call",
        "code": "flag = [0]\nto run_action:\n    flag[0] = 1\ncall run_action retrying 2 times\nsay flag[0]",
        "expected": "prints 1",
    },
    {
        "id": "P3-06",
        "category": "Resilience & Compound Actions",
        "name": "Compound sentence 'then if'",
        "code": "items = [1, 2, 3]\nset c to count of items, then if c > 0:\n    say \"HAS_ITEMS\"",
        "expected": "prints HAS_ITEMS",
    },
    {
        "id": "P3-07",
        "category": "Resilience & Compound Actions",
        "name": "Compound sentence 'and then if'",
        "code": "val = 10\nincrease val by 5, and then if val > 12:\n    say \"BIG\"",
        "expected": "prints BIG",
    },
    {
        "id": "P3-08",
        "category": "Resilience & Compound Actions",
        "name": "Compound sentence with 'then unless'",
        "code": "val = 0\nincrease val by 1, then unless val is zero:\n    say \"NON_ZERO\"",
        "expected": "prints NON_ZERO",
    },
    {
        "id": "P3-09",
        "category": "Resilience & Compound Actions",
        "name": "Sequential compound 'and then' statements",
        "code": "x = 10\nadd 5 to x, and then say x",
        "expected": "prints 15",
    },
    {
        "id": "P3-10",
        "category": "Resilience & Compound Actions",
        "name": "Compound sentence with assignment",
        "code": "x = 2\ndouble it, and then double it\nsay x",
        "expected": "prints 8",
    },
    {
        "id": "P3-11",
        "category": "Resilience & Compound Actions",
        "name": "Compound sentence with loop",
        "code": "nums = [1, 2]\nadd 3 to nums, then for each n in nums:\n    say n",
        "expected": "prints 1\n2\n3",
    },
    {
        "id": "P3-12",
        "category": "Resilience & Compound Actions",
        "name": "Retry exceeding attempts recovery",
        "code": "to always_fail:\n    make error \"Failed completely\"\ntry:\n    call always_fail retrying 2 times\nif that fails:\n    say \"HANDLED\"",
        "expected": "prints HANDLED",
    },
    {
        "id": "P3-13",
        "category": "Resilience & Compound Actions",
        "name": "Adverbial qualifier bare function syntax",
        "code": "to ping:\n    return \"PONG\"\nping retrying 2 times into out\nsay out",
        "expected": "prints PONG",
    },
    {
        "id": "P3-14",
        "category": "Resilience & Compound Actions",
        "name": "Compound sentence 'set x to 5, then say x'",
        "code": "set x to 5, then say x",
        "expected": "prints 5",
    },
    {
        "id": "P3-15",
        "category": "Resilience & Compound Actions",
        "name": "Sequential compound with multiple actions",
        "code": "x = 1\nincrease x by 1, and then increase x by 2\nsay x",
        "expected": "prints 4",
    },

    # -------------------------------------------------------------------------
    # 9. THOUGHT-TO-CODE PHASE 4: SET RESHAPING & STATISTICAL INQUIRIES
    # -------------------------------------------------------------------------
    {
        "id": "P4-01",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Relational 'pair A with B into C'",
        "code": "a = [\"x\", \"y\"]\nb = [1, 2]\npair a with b into pairs\nsay count of pairs",
        "expected": "prints 2",
    },
    {
        "id": "P4-02",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Relational 'pair A with B into dictionary C'",
        "code": "keys = [\"k1\", \"k2\"]\nvals = [10, 20]\npair keys with vals into dictionary d\nsay d's k1",
        "expected": "prints 10",
    },
    {
        "id": "P4-03",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Relational 'partition numbers into evens, odds where x is even'",
        "code": "numbers = [1, 2, 3, 4]\npartition numbers into evens, odds where x is even\nsay count of evens, count of odds",
        "expected": "prints 2 2",
    },
    {
        "id": "P4-04",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Relational 'partition numbers into evens and odds where x is even'",
        "code": "numbers = [1, 2, 3, 4]\npartition numbers into evens and odds where x is even\nsay count of evens",
        "expected": "prints 2",
    },
    {
        "id": "P4-05",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Relational 'partition with contextual attribute'",
        "code": "orders = [{\"amt\": 150}, {\"amt\": 50}]\npartition orders into high, low where amt > 100\nsay count of high, count of low",
        "expected": "prints 1 1",
    },
    {
        "id": "P4-06",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Relational 'flatten matrix into flat'",
        "code": "matrix = [[1, 2], [3, 4]]\nflatten matrix into flat\nsay count of flat",
        "expected": "prints 4",
    },
    {
        "id": "P4-07",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'what is the total amount in orders into total_val'",
        "code": "orders = [{\"amount\": 100}, {\"amount\": 200}]\nwhat is the total amount in orders into total_val\nsay total_val",
        "expected": "prints 300",
    },
    {
        "id": "P4-08",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'what is the average amount in orders into avg_val'",
        "code": "orders = [{\"amount\": 100}, {\"amount\": 300}]\nwhat is the average amount in orders into avg_val\nsay avg_val",
        "expected": "prints 200.0",
    },
    {
        "id": "P4-09",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'what is the highest amount in orders into max_val'",
        "code": "orders = [{\"amount\": 100}, {\"amount\": 500}]\nwhat is the highest amount in orders into max_val\nsay max_val",
        "expected": "prints 500",
    },
    {
        "id": "P4-10",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'what is the lowest amount in orders into min_val'",
        "code": "orders = [{\"amount\": 50}, {\"amount\": 200}]\nwhat is the lowest amount in orders into min_val\nsay min_val",
        "expected": "prints 50",
    },
    {
        "id": "P4-11",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'how many items in orders into count_val'",
        "code": "orders = [1, 2, 3, 4]\nhow many items in orders into count_val\nsay count_val",
        "expected": "prints 4",
    },
    {
        "id": "P4-12",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'how many in orders into count_val'",
        "code": "orders = [10, 20]\nhow many in orders into count_val\nsay count_val",
        "expected": "prints 2",
    },
    {
        "id": "P4-13",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational inquiry without into 'what is the total amount in orders'",
        "code": "orders = [{\"amount\": 10}, {\"amount\": 20}]\nwhat is the total amount in orders",
        "expected": "prints 30",
    },
    {
        "id": "P4-14",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational inquiry without into 'what is the average amount in orders'",
        "code": "orders = [{\"amount\": 10}, {\"amount\": 30}]\nwhat is the average amount in orders",
        "expected": "prints 20.0",
    },
    {
        "id": "P4-15",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational question mark 'what is the total amount in orders?'",
        "code": "orders = [{\"amount\": 100}, {\"amount\": 50}]\nwhat is the total amount in orders?",
        "expected": "prints 150",
    },
    {
        "id": "P4-16",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational question mark 'how many items in orders?'",
        "code": "orders = [1, 2, 3]\nhow many items in orders?",
        "expected": "prints 3",
    },
    {
        "id": "P4-17",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational math inquiry 'what is 10 + 20 into thirty'",
        "code": "what is 10 + 20 into thirty\nsay thirty",
        "expected": "prints 30",
    },
    {
        "id": "P4-18",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational contraction 'what's 5 * 5 into twenty_five'",
        "code": "what's 5 * 5 into twenty_five\nsay twenty_five",
        "expected": "prints 25",
    },
    {
        "id": "P4-19",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'what is count of orders into c'",
        "code": "orders = [\"a\", \"b\"]\nwhat is count of orders into c\nsay c",
        "expected": "prints 2",
    },
    {
        "id": "P4-20",
        "category": "Set Reshaping & Analytics Inquiries",
        "name": "Conversational 'what is sum of numbers into s'",
        "code": "numbers = [10, 20, 30]\nwhat is sum of numbers into s\nsay s",
        "expected": "prints 60",
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
        exp = tc.get("expect_error")
        if exp:
            if isinstance(exp, list) and (err_name in exp or any(e in err_name for e in exp)):
                result["status"] = "SUCCESS"
            elif isinstance(exp, str) and (err_name == exp or exp in err_name):
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
        print(f"[{idx:03d}/{len(TEST_CASES)}] {res['id']}: {res['name']} -> {res['status']}", flush=True)

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
