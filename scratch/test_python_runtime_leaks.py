from doomscript.compiler.engine import execute
import traceback

cases = [
    ("Division by zero", "x = 10 / 0"),
    ("String + Number", 'x = "hello" + 5'),
    ("Undefined variable", 'say nonexistent_var'),
    ("Item non-int index", 'nums = [1, 2, 3]\nsay item "two" of nums'),
    ("Dict missing key subscript", 'd = {"a": 1}\nsay d["b"]'),
    ("Iterate number", 'for each i in 123:\n    say i'),
    ("Call func wrong args", 'to greet with name:\n    say name\ngreet()'),
    ("Call non-function", 'x = 10\nx()'),
]

for name, code in cases:
    try:
        execute(code)
        print(f"{name}: SUCCESS (unexpected)")
    except Exception as e:
        print(f"{name}:")
        print(f"  Type: {type(e).__name__}")
        print(f"  Msg : {str(e)}")
