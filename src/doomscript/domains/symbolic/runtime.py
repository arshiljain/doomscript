"""Symbolic Mathematics, Analytical Differentiation & Computer Algebra Domain for DoomScript.

Provides a 100% pure Python Computer Algebra System (CAS):
- Symbolic expression tree with Operator Overloading (+, -, *, /, **)
- Exact analytical differentiation with Chain, Product, Quotient & Power rules
- Algebraic simplification engine (identity laws, associative flattening, like-term collection)
- Recursive descent mathematical expression string parser
- Univariate polynomial long division and Euclidean polynomial GCD
Zero external dependencies.
"""

from __future__ import annotations

import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union


class Expr:
    """Abstract Base Class for symbolic expression nodes."""

    def diff(self, var: str) -> Expr:
        raise NotImplementedError

    def simplify(self) -> Expr:
        return self

    def eval(self, subs: Dict[str, float]) -> float:
        raise NotImplementedError

    def __add__(self, other: Union[Expr, int, float]) -> Expr:
        return Add.create(self, _to_expr(other)).simplify()

    def __radd__(self, other: Union[Expr, int, float]) -> Expr:
        return Add.create(_to_expr(other), self).simplify()

    def __sub__(self, other: Union[Expr, int, float]) -> Expr:
        return Add.create(self, Mul.create(Constant(-1), _to_expr(other))).simplify()

    def __rsub__(self, other: Union[Expr, int, float]) -> Expr:
        return Add.create(_to_expr(other), Mul.create(Constant(-1), self)).simplify()

    def __mul__(self, other: Union[Expr, int, float]) -> Expr:
        return Mul.create(self, _to_expr(other)).simplify()

    def __rmul__(self, other: Union[Expr, int, float]) -> Expr:
        return Mul.create(_to_expr(other), self).simplify()

    def __truediv__(self, other: Union[Expr, int, float]) -> Expr:
        return Mul.create(self, Pow.create(_to_expr(other), Constant(-1))).simplify()

    def __rtruediv__(self, other: Union[Expr, int, float]) -> Expr:
        return Mul.create(_to_expr(other), Pow.create(self, Constant(-1))).simplify()

    def __pow__(self, other: Union[Expr, int, float]) -> Expr:
        return Pow.create(self, _to_expr(other)).simplify()

    def __neg__(self) -> Expr:
        return Mul.create(Constant(-1), self).simplify()

    def __repr__(self) -> str:
        return str(self)


def _to_expr(x: Union[Expr, int, float, str]) -> Expr:
    if isinstance(x, Expr):
        return x
    if isinstance(x, (int, float, Fraction)):
        return Constant(x)
    if isinstance(x, str):
        return Symbol(x)
    raise TypeError(f"Cannot convert {type(x)} to Expr")


class Constant(Expr):
    """Represents a numerical constant."""

    def __init__(self, value: Union[int, float, Fraction]):
        if isinstance(value, float) and value.is_integer():
            self.value = int(value)
        else:
            self.value = value

    def diff(self, var: str) -> Expr:
        return Constant(0)

    def eval(self, subs: Dict[str, float]) -> float:
        return float(self.value)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Constant) and self.value == other.value

    def __hash__(self) -> int:
        return hash(("Constant", self.value))

    def __str__(self) -> str:
        return str(self.value)


class Symbol(Expr):
    """Represents an algebraic variable (e.g., x, y, theta)."""

    def __init__(self, name: str):
        self.name = name

    def diff(self, var: str) -> Expr:
        return Constant(1) if self.name == var else Constant(0)

    def eval(self, subs: Dict[str, float]) -> float:
        if self.name in subs:
            return float(subs[self.name])
        raise KeyError(f"Variable '{self.name}' not provided in evaluation substitutions")

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Symbol) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Symbol", self.name))

    def __str__(self) -> str:
        return self.name


class Add(Expr):
    """Represents symbolic addition of expressions."""

    def __init__(self, args: Sequence[Expr]):
        self.args = tuple(args)

    @classmethod
    def create(cls, *args: Expr) -> Expr:
        flat_args: List[Expr] = []
        for a in args:
            if isinstance(a, Add):
                flat_args.extend(a.args)
            else:
                flat_args.append(a)
        return cls(flat_args)

    def diff(self, var: str) -> Expr:
        return Add.create(*[arg.diff(var) for arg in self.args]).simplify()

    def simplify(self) -> Expr:
        # Flatten nested additions
        flat: List[Expr] = []
        for a in self.args:
            simp = a.simplify()
            if isinstance(simp, Add):
                flat.extend(simp.args)
            else:
                flat.append(simp)

        # Collect constants and terms
        const_sum = 0
        non_const: List[Expr] = []

        for a in flat:
            if isinstance(a, Constant):
                const_sum += a.value
            else:
                non_const.append(a)

        # Group like terms (e.g. 2*x + 3*x = 5*x)
        term_coeffs: Dict[Expr, Union[int, float]] = {}
        for item in non_const:
            if isinstance(item, Mul) and len(item.args) == 2 and isinstance(item.args[0], Constant):
                c = item.args[0].value
                base = item.args[1]
            else:
                c = 1
                base = item
            term_coeffs[base] = term_coeffs.get(base, 0) + c

        result_terms: List[Expr] = []
        for base, c in term_coeffs.items():
            if c != 0:
                if c == 1:
                    result_terms.append(base)
                else:
                    result_terms.append(Mul.create(Constant(c), base))

        if const_sum != 0 or not result_terms:
            result_terms.append(Constant(const_sum))

        # Filter out 0 if multiple terms
        if len(result_terms) > 1:
            result_terms = [t for t in result_terms if t != Constant(0)]

        if len(result_terms) == 1:
            return result_terms[0]
        return Add(result_terms)

    def eval(self, subs: Dict[str, float]) -> float:
        return sum(arg.eval(subs) for arg in self.args)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Add) and set(self.args) == set(other.args)

    def __hash__(self) -> int:
        return hash(("Add", frozenset(self.args)))

    def __str__(self) -> str:
        parts = []
        for a in self.args:
            s = str(a)
            parts.append(s)
        return " + ".join(parts).replace("+ -", "- ")


class Mul(Expr):
    """Represents symbolic multiplication."""

    def __init__(self, args: Sequence[Expr]):
        self.args = tuple(args)

    @classmethod
    def create(cls, *args: Expr) -> Expr:
        flat_args: List[Expr] = []
        for a in args:
            if isinstance(a, Mul):
                flat_args.extend(a.args)
            else:
                flat_args.append(a)
        return cls(flat_args)

    def diff(self, var: str) -> Expr:
        # Product rule: sum(d(a_i)/dx * prod_{j != i} a_j)
        terms: List[Expr] = []
        for i in range(len(self.args)):
            other_args = [self.args[j] for j in range(len(self.args)) if j != i]
            terms.append(Mul.create(self.args[i].diff(var), *other_args))
        return Add.create(*terms).simplify()

    def simplify(self) -> Expr:
        flat: List[Expr] = []
        for a in self.args:
            simp = a.simplify()
            if isinstance(simp, Mul):
                flat.extend(simp.args)
            else:
                flat.append(simp)

        # Check for 0
        if any(a == Constant(0) for a in flat):
            return Constant(0)

        const_prod = 1
        non_const: List[Expr] = []
        for a in flat:
            if isinstance(a, Constant):
                const_prod *= a.value
            else:
                non_const.append(a)

        # Combine powers of identical bases (e.g. x * x = x^2)
        power_map: Dict[Expr, Expr] = {}
        for item in non_const:
            if isinstance(item, Pow):
                base = item.base
                exp = item.exp
            else:
                base = item
                exp = Constant(1)
            if base in power_map:
                power_map[base] = (power_map[base] + exp).simplify()
            else:
                power_map[base] = exp

        result_factors: List[Expr] = []
        if const_prod != 1 or not power_map:
            result_factors.append(Constant(const_prod))

        for base, exp in power_map.items():
            if exp == Constant(1):
                result_factors.append(base)
            elif exp != Constant(0):
                result_factors.append(Pow.create(base, exp))

        if len(result_factors) == 0:
            return Constant(1)
        if len(result_factors) == 1:
            return result_factors[0]
        return Mul(result_factors)

    def eval(self, subs: Dict[str, float]) -> float:
        prod = 1.0
        for arg in self.args:
            prod *= arg.eval(subs)
        return prod

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Mul) and set(self.args) == set(other.args)

    def __hash__(self) -> int:
        return hash(("Mul", frozenset(self.args)))

    def __str__(self) -> str:
        parts = []
        for a in self.args:
            s = str(a)
            if isinstance(a, Add):
                s = f"({s})"
            parts.append(s)
        return " * ".join(parts)


class Pow(Expr):
    """Represents exponentiation base^exp."""

    def __init__(self, base: Expr, exp: Expr):
        self.base = base
        self.exp = exp

    @classmethod
    def create(cls, base: Expr, exp: Expr) -> Expr:
        return cls(base, exp)

    def diff(self, var: str) -> Expr:
        # Generalized power rule: d(u^v)/dx = u^v * (v' * ln(u) + v * u' / u)
        # If exp is constant n: n * u^(n-1) * u'
        if isinstance(self.exp, Constant):
            n = self.exp.value
            return Mul.create(Constant(n), Pow.create(self.base, Constant(n - 1)), self.base.diff(var)).simplify()
        # General case
        return Mul.create(
            self,
            Add.create(
                Mul.create(self.exp.diff(var), Ln(self.base)),
                Mul.create(self.exp, self.base.diff(var), Pow.create(self.base, Constant(-1))),
            ),
        ).simplify()

    def simplify(self) -> Expr:
        b = self.base.simplify()
        e = self.exp.simplify()
        if e == Constant(0):
            return Constant(1)
        if e == Constant(1):
            return b
        if b == Constant(0):
            return Constant(0)
        if b == Constant(1):
            return Constant(1)
        if isinstance(b, Constant) and isinstance(e, Constant):
            return Constant(b.value ** e.value)
        return Pow(b, e)

    def eval(self, subs: Dict[str, float]) -> float:
        return self.base.eval(subs) ** self.exp.eval(subs)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Pow) and self.base == other.base and self.exp == other.exp

    def __hash__(self) -> int:
        return hash(("Pow", self.base, self.exp))

    def __str__(self) -> str:
        b_str = f"({self.base})" if isinstance(self.base, (Add, Mul)) else str(self.base)
        e_str = f"({self.exp})" if isinstance(self.exp, (Add, Mul)) else str(self.exp)
        return f"{b_str}^{e_str}"


class Sin(Expr):
    """Trigonometric sine function."""

    def __init__(self, arg: Expr):
        self.arg = arg

    def diff(self, var: str) -> Expr:
        return Mul.create(Cos(self.arg), self.arg.diff(var)).simplify()

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if a == Constant(0):
            return Constant(0)
        return Sin(a)

    def eval(self, subs: Dict[str, float]) -> float:
        return math.sin(self.arg.eval(subs))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Sin) and self.arg == other.arg

    def __hash__(self) -> int:
        return hash(("Sin", self.arg))

    def __str__(self) -> str:
        return f"sin({self.arg})"


class Cos(Expr):
    """Trigonometric cosine function."""

    def __init__(self, arg: Expr):
        self.arg = arg

    def diff(self, var: str) -> Expr:
        return Mul.create(Constant(-1), Sin(self.arg), self.arg.diff(var)).simplify()

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if a == Constant(0):
            return Constant(1)
        return Cos(a)

    def eval(self, subs: Dict[str, float]) -> float:
        return math.cos(self.arg.eval(subs))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Cos) and self.arg == other.arg

    def __hash__(self) -> int:
        return hash(("Cos", self.arg))

    def __str__(self) -> str:
        return f"cos({self.arg})"


class Ln(Expr):
    """Natural logarithm."""

    def __init__(self, arg: Expr):
        self.arg = arg

    def diff(self, var: str) -> Expr:
        return Mul.create(self.arg.diff(var), Pow.create(self.arg, Constant(-1))).simplify()

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if a == Constant(1):
            return Constant(0)
        return Ln(a)

    def eval(self, subs: Dict[str, float]) -> float:
        val = self.arg.eval(subs)
        return math.log(val)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Ln) and self.arg == other.arg

    def __hash__(self) -> int:
        return hash(("Ln", self.arg))

    def __str__(self) -> str:
        return f"ln({self.arg})"


class Exp(Expr):
    """Exponential function e^arg."""

    def __init__(self, arg: Expr):
        self.arg = arg

    def diff(self, var: str) -> Expr:
        return Mul.create(self, self.arg.diff(var)).simplify()

    def simplify(self) -> Expr:
        a = self.arg.simplify()
        if a == Constant(0):
            return Constant(1)
        return Exp(a)

    def eval(self, subs: Dict[str, float]) -> float:
        return math.exp(self.arg.eval(subs))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Exp) and self.arg == other.arg

    def __hash__(self) -> int:
        return hash(("Exp", self.arg))

    def __str__(self) -> str:
        return f"exp({self.arg})"


# --- String Expression Parser ---

class ExpressionParser:
    """Recursive descent parser for arithmetic and algebraic string expressions."""

    def __init__(self, text: str):
        self.tokens = self._tokenize(text)
        self.pos = 0

    def _tokenize(self, s: str) -> List[Tuple[str, str]]:
        token_spec = [
            ("NUMBER", r"\d+(\.\d+)?"),
            ("IDENT", r"[A-Za-z_]\w*"),
            ("POW", r"\*\*|\^"),
            ("PLUS", r"\+"),
            ("MINUS", r"\-"),
            ("MUL", r"\*"),
            ("DIV", r"\/"),
            ("LPAREN", r"\("),
            ("RPAREN", r"\)"),
            ("SKIP", r"\s+"),
        ]
        tok_regex = "|".join(f"(?P<{p[0]}>{p[1]})" for p in token_spec)
        tokens = []
        for mo in re.finditer(tok_regex, s):
            kind = mo.lastgroup
            val = mo.group()
            if kind != "SKIP":
                tokens.append((kind, val))
        return tokens

    def current(self) -> Optional[Tuple[str, str]]:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def match(self, expected_kind: str) -> Optional[str]:
        cur = self.current()
        if cur and cur[0] == expected_kind:
            self.pos += 1
            return cur[1]
        return None

    def parse(self) -> Expr:
        expr = self._parse_add_sub()
        return expr

    def _parse_add_sub(self) -> Expr:
        left = self._parse_mul_div()
        while True:
            if self.match("PLUS"):
                right = self._parse_mul_div()
                left = left + right
            elif self.match("MINUS"):
                right = self._parse_mul_div()
                left = left - right
            else:
                break
        return left

    def _parse_mul_div(self) -> Expr:
        left = self._parse_pow()
        while True:
            if self.match("MUL"):
                right = self._parse_pow()
                left = left * right
            elif self.match("DIV"):
                right = self._parse_pow()
                left = left / right
            else:
                break
        return left

    def _parse_pow(self) -> Expr:
        base = self._parse_unary()
        if self.match("POW"):
            exp = self._parse_pow()  # Right associative
            return (base ** exp).simplify()
        return base

    def _parse_unary(self) -> Expr:
        if self.match("MINUS"):
            return -self._parse_unary()
        if self.match("PLUS"):
            return self._parse_unary()
        return self._parse_atom()

    def _parse_atom(self) -> Expr:
        cur = self.current()
        if not cur:
            raise SyntaxError("Unexpected end of expression")

        kind, val = cur
        if self.match("NUMBER"):
            return Constant(float(val) if "." in val else int(val))
        if self.match("LPAREN"):
            node = self._parse_add_sub()
            if not self.match("RPAREN"):
                raise SyntaxError("Mismatched parentheses")
            return node
        if self.match("IDENT"):
            name = val
            if self.match("LPAREN"):
                # Function call
                arg = self._parse_add_sub()
                if not self.match("RPAREN"):
                    raise SyntaxError(f"Mismatched parentheses in function {name}")
                if name.lower() == "sin":
                    return Sin(arg).simplify()
                if name.lower() == "cos":
                    return Cos(arg).simplify()
                if name.lower() in ("ln", "log"):
                    return Ln(arg).simplify()
                if name.lower() == "exp":
                    return Exp(arg).simplify()
                raise ValueError(f"Unknown symbolic function '{name}'")
            return Symbol(name)

        raise SyntaxError(f"Unexpected token: {kind} ({val})")


# --- Polynomial Operations & Euclidean GCD ---

class PolyOps:
    """Univariate polynomial algorithms with rational coefficients."""

    @staticmethod
    def poly_divmod(p1: List[float], p2: List[float]) -> Tuple[List[float], List[float]]:
        """Polynomial division p1 / p2 returning (quotient, remainder).
        Polynomials are represented as lists of coefficients from highest degree to constant.
        e.g., [1, -5, 6] represents x^2 - 5x + 6.
        """
        # Trim leading zeros
        def trim(p: List[float]) -> List[float]:
            while p and abs(p[0]) < 1e-12:
                p.pop(0)
            return p

        dividend = trim(list(p1))
        divisor = trim(list(p2))

        if not divisor:
            raise ZeroDivisionError("Polynomial division by zero polynomial")
        if not dividend or len(dividend) < len(divisor):
            return [0.0], dividend or [0.0]

        quotient: List[float] = []
        rem = list(dividend)

        while len(rem) >= len(divisor):
            lead_coeff = rem[0] / divisor[0]
            quotient.append(lead_coeff)
            for j in range(len(divisor)):
                rem[j] -= lead_coeff * divisor[j]
            rem.pop(0)

        return quotient, trim(rem) or [0.0]

    @staticmethod
    def poly_gcd(p1: List[float], p2: List[float]) -> List[float]:
        """Calculates Greatest Common Divisor (GCD) of two polynomials via Euclidean algorithm."""
        a = list(p1)
        b = list(p2)

        while any(abs(x) > 1e-12 for x in b):
            _, rem = PolyOps.poly_divmod(a, b)
            a = b
            b = rem

        # Make monic (leading coefficient = 1)
        lead = a[0]
        if abs(lead) > 1e-12:
            return [round(c / lead, 4) for c in a]
        return [1.0]


# --- High-Level Public Functions ---

def symbolic_parse(expr_str: str) -> Expr:
    """Parses mathematical string expression into symbolic expression tree."""
    return ExpressionParser(expr_str).parse()


def symbolic_diff(expr: Union[str, Expr], var: str = "x") -> Expr:
    """Calculates exact analytical derivative with respect to var."""
    if isinstance(expr, str):
        expr = symbolic_parse(expr)
    return expr.diff(var).simplify()


def symbolic_simplify(expr: Union[str, Expr]) -> Expr:
    """Simplifies expression using algebraic rewrite rules."""
    if isinstance(expr, str):
        expr = symbolic_parse(expr)
    return expr.simplify()


def symbolic_eval(expr: Union[str, Expr], subs: Dict[str, float]) -> float:
    """Evaluates expression numerically with variable substitutions."""
    if isinstance(expr, str):
        expr = symbolic_parse(expr)
    return expr.eval(subs)


def symbolic_poly_gcd(p1: List[float], p2: List[float]) -> List[float]:
    """Computes monic Euclidean polynomial GCD."""
    return PolyOps.poly_gcd(p1, p2)
