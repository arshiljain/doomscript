"""
DoomScript Static Contracts & Safety Checker (Phase 8)
Inspects AST for type contracts, preconditions, and postconditions.
Supports compile-time strict verification of constant contracts and signatures.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple, Any
import ast
from doomscript.compiler.engine import compile_to_ast


@dataclass
class ContractViolation:
    line: int
    message: str
    severity: str = "error"


class ContractAnalyzer(ast.NodeVisitor):
    """
    Traverses Python AST generated from DoomScript to detect:
    1. Direct literal contract failures (require 5 < 0, verify 10 is text, etc.)
    2. Function call literal argument type mismatches against contracts.
    """
    def __init__(self):
        self.violations: List[ContractViolation] = []
        # func_name -> {param_idx: (param_name, expected_type)}
        self.func_contracts: Dict[str, Dict[int, Tuple[str, str]]] = {}

    def visit_FunctionDef(self, node: ast.FunctionDef):
        param_names = [arg.arg for arg in node.args.args]
        contracts: Dict[int, Tuple[str, str]] = {}
        for stmt in node.body:
            if isinstance(stmt, ast.Assert):
                test = stmt.test
                if isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == "isinstance":
                    if len(test.args) >= 2 and isinstance(test.args[0], ast.Name):
                        var_name = test.args[0].id
                        if var_name in param_names:
                            param_idx = param_names.index(var_name)
                            target_type = self._resolve_target_type(test.args[1])
                            if target_type:
                                contracts[param_idx] = (var_name, target_type)
            else:
                if not (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)):
                    break
        if contracts:
            self.func_contracts[node.name] = contracts
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        test = node.test
        lineno = getattr(node, "lineno", 1)

        # 1. Assert on constant boolean: assert False
        if isinstance(test, ast.Constant) and test.value is False:
            msg = self._get_assert_msg(node) or "Contract assertion is statically False"
            self.violations.append(ContractViolation(line=lineno, message=f"Static contract violation: {msg}"))

        # 2. Assert on isinstance(Constant, type)
        elif isinstance(test, ast.Call) and isinstance(test.func, ast.Name) and test.func.id == "isinstance":
            if len(test.args) >= 2 and isinstance(test.args[0], ast.Constant):
                val = test.args[0].value
                target_type = self._resolve_target_type(test.args[1])
                if target_type and not self._check_type_match(val, target_type):
                    self.violations.append(ContractViolation(
                        line=lineno,
                        message=f"Static contract violation: expected {target_type}, but got literal {type(val).__name__} ({val!r})"
                    ))

        # 3. Assert on constant comparison: 5 > 10 (evaluated safely via AST operator inspection, without eval)
        elif isinstance(test, ast.Compare):
            if isinstance(test.left, ast.Constant) and len(test.comparators) == 1 and isinstance(test.comparators[0], ast.Constant):
                try:
                    left_val = test.left.value
                    right_val = test.comparators[0].value
                    op = test.ops[0]
                    res = None
                    if isinstance(op, ast.Eq):
                        res = (left_val == right_val)
                    elif isinstance(op, ast.NotEq):
                        res = (left_val != right_val)
                    elif isinstance(op, ast.Lt):
                        res = (left_val < right_val)
                    elif isinstance(op, ast.LtE):
                        res = (left_val <= right_val)
                    elif isinstance(op, ast.Gt):
                        res = (left_val > right_val)
                    elif isinstance(op, ast.GtE):
                        res = (left_val >= right_val)
                    elif isinstance(op, ast.In):
                        res = (left_val in right_val)
                    elif isinstance(op, ast.NotIn):
                        res = (left_val not in right_val)
                    elif isinstance(op, ast.Is):
                        res = (left_val is right_val)
                    elif isinstance(op, ast.IsNot):
                        res = (left_val is not right_val)

                    if res is False:
                        self.violations.append(ContractViolation(
                            line=lineno,
                            message=f"Static contract violation: condition is statically False ({ast.unparse(test)})"
                        ))
                except Exception:
                    pass

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        lineno = getattr(node, "lineno", 1)
        if isinstance(node.func, ast.Name) and node.func.id in self.func_contracts:
            contracts = self.func_contracts[node.func.id]
            for idx, arg in enumerate(node.args):
                if idx in contracts and isinstance(arg, ast.Constant):
                    param_name, expected_type = contracts[idx]
                    if not self._check_type_match(arg.value, expected_type):
                        self.violations.append(ContractViolation(
                            line=lineno,
                            message=f"Static contract violation in call to '{node.func.id}': argument '{param_name}' expects {expected_type}, but received {type(arg.value).__name__} ({arg.value!r})"
                        ))
        self.generic_visit(node)

    def _resolve_target_type(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            if node.id == "str":
                return "text"
            if node.id == "bool":
                return "boolean"
            if node.id == "list":
                return "list"
            if node.id == "dict":
                return "record"
        elif isinstance(node, ast.Tuple):
            names = [elt.id for elt in node.elts if isinstance(elt, ast.Name)]
            if "int" in names or "float" in names:
                return "number"
        return None

    def _check_type_match(self, val: Any, expected_type: str) -> bool:
        if expected_type == "number":
            return isinstance(val, (int, float)) and not isinstance(val, bool)
        elif expected_type == "text":
            return isinstance(val, str)
        elif expected_type == "boolean":
            return isinstance(val, bool)
        elif expected_type == "list":
            return isinstance(val, list)
        elif expected_type == "record":
            return isinstance(val, dict)
        return True

    def _get_assert_msg(self, node: ast.Assert) -> Optional[str]:
        if node.msg and isinstance(node.msg, ast.Constant) and isinstance(node.msg.value, str):
            return node.msg.value
        return None


def analyze_contracts(source: str) -> List[ContractViolation]:
    """
    Parses and checks DoomScript source code for static contract violations.
    """
    tree = compile_to_ast(source)
    analyzer = ContractAnalyzer()
    analyzer.visit(tree)
    return analyzer.violations
