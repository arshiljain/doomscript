"""
DoomScript Line-by-Line Explainer
Powers 'doom explain file.doom': prints each line, its generated Python,
and a concise, plain-English summary of what it does.
"""

import ast
import re
from typing import List, Dict, Any, Tuple
from doomscript.compiler.engine import compile_to_ast, transpile


def explain_statement_ast(node: ast.AST) -> str:
    """Generates a one-line plain-English explanation from a Python AST statement node."""
    if isinstance(node, ast.Expr):
        val = node.value
        if isinstance(val, ast.Call):
            func_name = getattr(val.func, "id", "")
            if not func_name and isinstance(val.func, ast.Attribute):
                func_name = f"{getattr(val.func.value, 'id', '')}.{val.func.attr}"
            
            if func_name == "print":
                return "Prints values to standard output."
            elif func_name == "sleep":
                return "Pauses execution for a specified duration."
            elif func_name == "insert_list":
                return "Inserts an element into a list at a specified index."
            elif func_name == "sort_records":
                return "Sorts the records list in-place by key."
            elif func_name == "run_command":
                return "Executes an operating system shell command."
            elif func_name == "copy_file":
                return "Copies a file to a new destination."
            elif func_name == "delete_file":
                return "Deletes the specified file from disk."
            elif func_name == "create_dir":
                return "Creates a new directory if it does not already exist."
            elif func_name == "beep":
                return "Emits a hardware sound frequency."
            return f"Executes function '{func_name}'."
        return "Evaluates an expression."

    elif isinstance(node, ast.Assign):
        target_names = []
        for t in node.targets:
            if isinstance(t, ast.Name):
                target_names.append(t.id)
            elif isinstance(t, ast.Attribute):
                target_names.append(f"{getattr(t.value, 'id', '')}.{t.attr}")
        target_str = ", ".join(target_names) or "variable"

        # Inspect value
        val = node.value
        if isinstance(val, ast.Call):
            fname = getattr(val.func, "id", "")
            if fname == "read_csv":
                return f"Reads rows from a CSV file into '{target_str}'."
            elif fname == "read_file":
                return f"Reads contents of a text file into '{target_str}'."
            elif fname == "parse_json":
                return f"Parses JSON text into data records in '{target_str}'."
            elif fname == "group_by":
                return f"Groups records by field into '{target_str}'."
            elif fname == "get_env_var":
                return f"Loads an environment variable into '{target_str}'."
            elif fname == "list_files":
                return f"Lists directory files into '{target_str}'."
            elif fname == "input":
                return f"Prompts user for text input into '{target_str}'."
            elif fname == "ask_number":
                return f"Prompts user for numeric input into '{target_str}'."
            elif fname == "ask_boolean":
                return f"Prompts user for yes/no confirmation into '{target_str}'."
            elif fname == "fetch_json":
                return f"Fetches JSON data from remote HTTP endpoint into '{target_str}'."
        elif isinstance(val, ast.ListComp):
            return f"Filters or transforms records into list '{target_str}'."
        elif isinstance(val, ast.List):
            return f"Initializes list '{target_str}' with {len(val.elts)} item(s)."
        elif isinstance(val, ast.Dict):
            return f"Initializes record '{target_str}' with {len(val.keys)} field(s)."

        return f"Stores a computed value into '{target_str}'."

    elif isinstance(node, ast.AugAssign):
        target_name = getattr(node.target, "id", "variable")
        op_name = "Increases" if isinstance(node.op, ast.Add) else "Decreases"
        return f"{op_name} '{target_name}' by the given amount."

    elif isinstance(node, ast.If):
        return "Checks a condition and branches execution."

    elif isinstance(node, ast.For):
        target_name = getattr(node.target, "id", "item")
        return f"Loops through a collection, binding each element to '{target_name}'."

    elif isinstance(node, ast.While):
        return "Loops continuously while the condition remains true."

    elif isinstance(node, ast.FunctionDef):
        return f"Defines a reusable function named '{node.name}'."

    elif isinstance(node, ast.Return):
        return "Returns a value from the current function."

    elif isinstance(node, ast.Import):
        mods = ", ".join(alias.name for alias in node.names)
        return f"Imports external Python module(s): {mods}."

    elif isinstance(node, ast.ImportFrom):
        return f"Imports specific functions from module '{node.module}'."

    elif isinstance(node, ast.Try):
        return "Guards a block of code with error handling (try/catch)."

    elif isinstance(node, ast.Break):
        return "Breaks out of the surrounding loop immediately."

    elif isinstance(node, ast.Continue):
        return "Skips immediately to the next loop iteration."

    return "Executes statement."


def explain_source(source: str) -> List[Dict[str, Any]]:
    """
    Analyzes a DoomScript source file and returns structured line-by-line
    explanations with the corresponding DoomScript line, generated Python,
    and plain-English summary.
    """
    results = []
    lines = source.splitlines()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            results.append({
                "line_no": idx,
                "doom": line,
                "python": "",
                "explanation": "Comment or empty line." if stripped.startswith("#") else "",
                "is_code": False
            })
            continue

        try:
            # Transpile single statement
            py_mod = compile_to_ast(stripped)
            py_code = ast.unparse(py_mod).strip()
            # If multiple statements in body
            stmt_nodes = py_mod.body if hasattr(py_mod, "body") else []
            if stmt_nodes:
                explanation = explain_statement_ast(stmt_nodes[0])
            else:
                explanation = "Executes statement."
            results.append({
                "line_no": idx,
                "doom": line,
                "python": py_code,
                "explanation": explanation,
                "is_code": True
            })
        except Exception:
            # Fallback heuristic for block headers or partial lines
            explanation = "Executes block statement."
            if re.match(r"^to\s+", stripped, re.I):
                explanation = "Defines a new function."
            elif re.match(r"^(?:if|unless)\s+", stripped, re.I):
                explanation = "Conditional branch test."
            elif re.match(r"^(?:repeat|for|while|until)\s+", stripped, re.I):
                explanation = "Loop block header."
            elif re.match(r"^try\b", stripped, re.I):
                explanation = "Starts an error-guarded block."
            elif re.match(r"^if (?:it|that) fails", stripped, re.I):
                explanation = "Handles error when previous block fails."
            elif re.match(r"^always\b", stripped, re.I):
                explanation = "Runs cleanup block unconditionally."

            results.append({
                "line_no": idx,
                "doom": line,
                "python": "(block component)",
                "explanation": explanation,
                "is_code": True
            })

    return results
