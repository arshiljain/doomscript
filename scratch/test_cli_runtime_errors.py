from doomscript.cli import handle_cli_error
from doomscript.compiler.engine import execute

snippets = [
    ("add 5 to x", "x = 10\nadd 5 to x"),
    ("item 10 of numbers", "numbers = [10, 20, 30]\nsay item 10 of numbers"),
    ("remove 99 from numbers", "numbers = [1, 2, 3]\nremove 99 from numbers"),
    ("missing field", 'p1 = {"name": "Alice"}\nsay p1\'s age'),
    ("verify failed", 'age = 16\nverify that age is at least 18 otherwise "Must be an adult"'),
    ("for each in number", "for each i in 123:\n    say i"),
]

for name, code in snippets:
    print(f"=== {name} ===")
    try:
        execute(code)
    except Exception as e:
        handle_cli_error("test.doom", code, e)
    print()
