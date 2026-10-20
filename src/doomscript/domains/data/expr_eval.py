"""Safe AST-based expression evaluator for data pipelines, replacing unsafe eval()."""

import ast
import operator
import re
from typing import Any, Callable, Dict


class SafeEvalError(Exception):
    """Raised when an expression cannot be evaluated or contains unknown columns."""
    pass


class SafeEvalSecurityError(SafeEvalError):
    """Raised when an expression attempts unsafe operations or violates safety policy."""
    pass


SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Not: operator.not_,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
}

SAFE_BUILTINS: Dict[str, Callable] = {
    "abs": abs,
    "round": round,
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "len": len,
    "min": min,
    "max": max,
    "sum": sum,
}


class SafeASTEvaluator:
    """Evaluates Python mathematical and logical expressions securely on a data record."""

    def __init__(self, custom_functions: Dict[str, Callable] = None):
        self.functions = dict(SAFE_BUILTINS)
        if custom_functions:
            self.functions.update(custom_functions)

    def evaluate(self, expr_str: str, record: Dict[str, Any]) -> Any:
        """Parses and evaluates an expression string against a data record."""
        if not expr_str or not expr_str.strip():
            raise SafeEvalError("Empty expression cannot be evaluated")

        s = expr_str.strip()
        s = re.sub(r"\bis\s+greater\s+than\s+or\s+equal\s+to\b", ">=", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+less\s+than\s+or\s+equal\s+to\b", "<=", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+at\s+least\b", ">=", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+at\s+most\b", "<=", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+greater\s+than\b", ">", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+less\s+than\b", "<", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+equal\s+to\b", "==", s, flags=re.IGNORECASE)
        s = re.sub(r"\bis\s+not\b", "!=", s, flags=re.IGNORECASE)

        try:
            tree = ast.parse(s, mode="eval")
        except SyntaxError as e:
            raise SafeEvalError(f"Syntax error in expression '{expr_str}': {e.msg}") from e

        return self._eval_node(tree.body, record)

    def _eval_node(self, node: ast.AST, record: Dict[str, Any]) -> Any:
        if isinstance(node, ast.Constant):
            return node.value

        elif isinstance(node, ast.Name):
            name = node.id
            if name.startswith("__"):
                raise SafeEvalSecurityError(f"Access to private/dunder identifier '{name}' is forbidden")
            if name in record:
                return record[name]
            if name in self.functions:
                return self.functions[name]
            if name == "True":
                return True
            if name == "False":
                return False
            if name == "None":
                return None
            raise SafeEvalError(f"Column or variable '{name}' not found in record")

        elif isinstance(node, ast.BinOp):
            op_func = SAFE_OPERATORS.get(type(node.op))
            if not op_func:
                raise SafeEvalSecurityError(f"Unsupported binary operator: {type(node.op).__name__}")
            left = self._eval_node(node.left, record)
            right = self._eval_node(node.right, record)
            try:
                return op_func(left, right)
            except Exception as e:
                raise SafeEvalError(f"Evaluation error in binary operation: {e}") from e

        elif isinstance(node, ast.UnaryOp):
            op_func = SAFE_OPERATORS.get(type(node.op))
            if not op_func:
                raise SafeEvalSecurityError(f"Unsupported unary operator: {type(node.op).__name__}")
            operand = self._eval_node(node.operand, record)
            try:
                return op_func(operand)
            except Exception as e:
                raise SafeEvalError(f"Evaluation error in unary operation: {e}") from e

        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                for val_node in node.values:
                    val = self._eval_node(val_node, record)
                    if not val:
                        return val
                return val
            elif isinstance(node.op, ast.Or):
                for val_node in node.values:
                    val = self._eval_node(val_node, record)
                    if val:
                        return val
                return val
            else:
                raise SafeEvalSecurityError(f"Unsupported boolean operator: {type(node.op).__name__}")

        elif isinstance(node, ast.Compare):
            left = self._eval_node(node.left, record)
            for op, comparator in zip(node.ops, node.comparators):
                op_func = SAFE_OPERATORS.get(type(op))
                if not op_func:
                    raise SafeEvalSecurityError(f"Unsupported comparison operator: {type(op).__name__}")
                right = self._eval_node(comparator, record)
                try:
                    if not op_func(left, right):
                        return False
                except Exception as e:
                    raise SafeEvalError(f"Evaluation error in comparison: {e}") from e
                left = right
            return True

        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                if func_name.startswith("__"):
                    raise SafeEvalSecurityError(f"Access to private/dunder function '{func_name}' is forbidden")
                if func_name not in self.functions:
                    raise SafeEvalSecurityError(f"Function '{func_name}' is not in the safe whitelist")
                fn = self.functions[func_name]
            elif isinstance(node.func, ast.Attribute):
                # Safe method call on string/list (e.g. s.strip(), s.lower())
                attr_name = node.func.attr
                if attr_name.startswith("__"):
                    raise SafeEvalSecurityError(f"Access to dunder attribute '{attr_name}' is forbidden")
                target_obj = self._eval_node(node.func.value, record)
                if not hasattr(target_obj, attr_name):
                    raise SafeEvalError(f"Object {target_obj!r} has no attribute '{attr_name}'")
                fn = getattr(target_obj, attr_name)
            else:
                raise SafeEvalSecurityError("Arbitrary call targets are not permitted")

            args = [self._eval_node(arg, record) for arg in node.args]
            kwargs = {kw.arg: self._eval_node(kw.value, record) for kw in node.keywords}
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                raise SafeEvalError(f"Error calling function: {e}") from e

        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("__"):
                raise SafeEvalSecurityError(f"Access to dunder attribute '{node.attr}' is forbidden")
            val = self._eval_node(node.value, record)
            if isinstance(val, dict) and node.attr in val:
                return val[node.attr]
            if hasattr(val, node.attr):
                return getattr(val, node.attr)
            raise SafeEvalError(f"Attribute '{node.attr}' not found")

        elif isinstance(node, ast.Subscript):
            val = self._eval_node(node.value, record)
            key = self._eval_node(node.slice, record)
            try:
                return val[key]
            except Exception as e:
                raise SafeEvalError(f"Index or key error: {e}") from e

        elif isinstance(node, ast.List):
            return [self._eval_node(elt, record) for elt in node.elts]

        elif isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt, record) for elt in node.elts)

        elif isinstance(node, ast.Dict):
            return {
                self._eval_node(k, record): self._eval_node(v, record)
                for k, v in zip(node.keys, node.values)
            }

        else:
            raise SafeEvalSecurityError(f"AST node type '{type(node).__name__}' is not permitted in safe expressions")
