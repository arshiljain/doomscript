from doomscript.cli import handle_cli_error
from doomscript.compiler.engine import compile_to_ast

syntax_cases = [
    ("numbers is a list of 1, 2, 3", "numbers is a list of 1, 2, 3"),
    ("create a list of numbers from 1 to 10", "create a list of numbers from 1 to 10 into numbers"),
    ("how many items in numbers", "numbers = [1, 2, 3]\nhow many items in numbers"),
    ("join words with comma (expr)", 'words = ["a", "b"]\nset text to join words with ", "'),
    ("join words without into", 'words = ["a", "b"]\njoin words with ", "'),
    ("replace without into", 'sentence = "cat"\nreplace "cat" with "dog" in sentence'),
    ("file variable name", 'file = "data.csv"'),
    ("a Person has name, age", "a Person has name, age"),
    ("create a Person into p1", 'create a Person with name "Alice", age 30 into p1'),
    ("change p1's name", 'p1 = {"name": "Alice"}\nchange p1\'s name to "Bob"'),
    ("ask with trailing as number", 'ask "What is your age?" into age as number'),
    ("if there is an error", 'try:\n    x = 1/0\nif there is an error:\n    say "error"'),
    ("for each number in numbers", 'numbers = [1, 2, 3]\nfor each number in numbers:\n    if number is even:\n        say number'),
]

for name, code in syntax_cases:
    print(f"=== {name} ===")
    try:
        compile_to_ast(code)
    except Exception as e:
        handle_cli_error("test.doom", code, e)
    print()
