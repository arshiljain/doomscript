from doomscript.compiler.engine import compile_to_ast

names_to_test = ["file", "line", "word", "text", "number", "default", "step", "first", "last", "sum", "count", "items", "item"]

for name in names_to_test:
    code = f"{name} = 123"
    try:
        compile_to_ast(code)
        print(f"Variable '{name} = 123': OK")
    except Exception as e:
        print(f"Variable '{name} = 123': FAILED ({type(e).__name__}: {str(e)[:60]})")
