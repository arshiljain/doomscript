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
from doomscript.runtime import Record


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


class SymbolicIntegrator:
    """Exact analytical and numerical integration for symbolic expressions."""

    def __init__(self):
        pass

    @classmethod
    def integrate_polynomial(cls, coeffs: List[float]) -> List[float]:
        """
        Integrates a polynomial given in standard form: c_n x^n + ... + c_1 x + c_0.
        Returns integrated polynomial coefficients with constant of integration 0.0.
        """
        n = len(coeffs)
        if n == 0:
            return [0.0]
        integrated = []
        for i, c in enumerate(coeffs):
            power = n - i
            integrated.append(round(c / power, 6))
        integrated.append(0.0)  # Constant term + C
        return integrated

    @classmethod
    def definite_integral_poly(cls, coeffs: List[float], a: float, b: float) -> float:
        """Evaluates definite integral of a polynomial from a to b."""
        integ = cls.integrate_polynomial(coeffs)
        deg = len(integ) - 1

        def eval_at(x: float) -> float:
            val = 0.0
            for i, c in enumerate(integ):
                p = deg - i
                val += c * (x ** p)
            return val

        return round(eval_at(b) - eval_at(a), 6)

    @classmethod
    def integrate_term(cls, term_str: str, var: str = "x") -> str:
        """
        Integrates common single mathematical terms:
        - 'x^n' -> '(1/(n+1))*x^(n+1)'
        - 'c' -> 'c*x'
        - 'e^(a*x)' -> '(1/a)*e^(a*x)'
        - 'cos(a*x)' -> '(1/a)*sin(a*x)'
        - 'sin(a*x)' -> '(-1/a)*cos(a*x)'
        """
        s = term_str.strip().lower()
        if s == var:
            return f"(0.5 * {var}^2)"
        if s == f"sin({var})":
            return f"-cos({var})"
        if s == f"cos({var})":
            return f"sin({var})"
        if s == f"exp({var})" or s == f"e^{var}":
            return f"exp({var})"

        # Check for x^n
        m = re.match(rf"^{var}\^(\d+)$", s)
        if m:
            n = int(m.group(1))
            return f"({round(1.0 / (n + 1), 4)} * {var}^{n + 1})"

        # Check for constant number
        try:
            val = float(s)
            return f"({val} * {var})"
        except ValueError:
            pass

        return f"Integral({term_str}, {var})"


class TaylorSeries:
    """Computes Taylor / Maclaurin series expansions of mathematical expressions."""

    def __init__(self, expr: Union[str, Expr], var: str = "x", x0: float = 0.0):
        self.var = var
        self.x0 = float(x0)
        if isinstance(expr, str):
            self.expr = symbolic_parse(expr)
        else:
            self.expr = expr

    def expand(self, order: int = 4) -> Dict[str, Any]:
        """
        Generates Taylor polynomial terms up to degree 'order'.
        T_n(x) = sum_{k=0}^n (f^(k)(x0) / k!) * (x - x0)^k
        """
        terms = []
        coefficients = []
        curr_deriv = self.expr

        for k in range(order + 1):
            fact = math.factorial(k)
            # Evaluate derivative at x0
            try:
                deriv_val = curr_deriv.eval({self.var: self.x0})
            except Exception:
                deriv_val = 0.0

            coeff = deriv_val / fact
            coefficients.append(round(coeff, 6))

            if abs(coeff) > 1e-9:
                if k == 0:
                    terms.append(f"{coeff:.4f}")
                elif k == 1:
                    if self.x0 == 0.0:
                        terms.append(f"{coeff:.4f}*{self.var}")
                    else:
                        terms.append(f"{coeff:.4f}*({self.var} - {self.x0})")
                else:
                    if self.x0 == 0.0:
                        terms.append(f"{coeff:.4f}*{self.var}^{k}")
                    else:
                        terms.append(f"{coeff:.4f}*({self.var} - {self.x0})^{k}")

            curr_deriv = curr_deriv.diff(self.var).simplify()

        polynomial_str = " + ".join(terms) if terms else "0.0"
        return {
            "order": order,
            "center": self.x0,
            "coefficients": coefficients,
            "polynomial": polynomial_str,
        }


class ExactRationalLinearSolver:
    """Exact rational arithmetic linear solver using fractions.Fraction."""

    def __init__(self):
        pass

    @classmethod
    def solve(cls, A: List[List[Union[int, float, str, Fraction]]], b: List[Union[int, float, str, Fraction]]) -> Dict[str, Any]:
        """Solves A x = b exactly over Q."""
        m = len(A)
        n = len(A[0]) if m > 0 else 0
        if m != n:
            raise ValueError("Matrix A must be square for exact unique linear solver")

        # Convert to Fraction matrix
        aug = [
            [Fraction(A[r][c]) for c in range(n)] + [Fraction(b[r])]
            for r in range(m)
        ]

        # Gaussian elimination
        for col in range(n):
            pivot_row = None
            for r in range(col, m):
                if aug[r][col] != 0:
                    pivot_row = r
                    break

            if pivot_row is None:
                return {"success": False, "solution": [], "error": "Singular matrix"}

            aug[col], aug[pivot_row] = aug[pivot_row], aug[col]
            pivot = aug[col][col]

            for c in range(col, n + 1):
                aug[col][c] /= pivot

            for r in range(m):
                if r != col and aug[r][col] != 0:
                    factor = aug[r][col]
                    for c in range(col, n + 1):
                        aug[r][c] -= factor * aug[col][c]

        solution = [aug[r][n] for r in range(n)]
        return {
            "success": True,
            "solution": [f"{s.numerator}/{s.denominator}" if s.denominator != 1 else str(s.numerator) for s in solution],
            "solution_floats": [float(s) for s in solution],
        }

    @classmethod
    def determinant(cls, A: List[List[Union[int, float, str, Fraction]]]) -> Fraction:
        """Calculates exact determinant of square matrix A over Q."""
        n = len(A)
        M = [[Fraction(A[r][c]) for c in range(n)] for r in range(n)]
        det = Fraction(1, 1)

        for col in range(n):
            pivot_row = None
            for r in range(col, n):
                if M[r][col] != 0:
                    pivot_row = r
                    break
            if pivot_row is None:
                return Fraction(0, 1)

            if pivot_row != col:
                M[col], M[pivot_row] = M[pivot_row], M[col]
                det = -det

            pivot = M[col][col]
            det *= pivot

            for r in range(col + 1, n):
                if M[r][col] != 0:
                    factor = M[r][col] / pivot
                    for c in range(col, n):
                        M[r][c] -= factor * M[col][c]

        return det


def symbolic_integrate(coeffs: List[float], a: Optional[float] = None, b: Optional[float] = None) -> Any:
    """Analytically integrates a polynomial or computes its definite integral."""
    if a is not None and b is not None:
        return SymbolicIntegrator.definite_integral_poly(coeffs, a, b)
    return SymbolicIntegrator.integrate_polynomial(coeffs)


def symbolic_taylor_series(
    expr: Union[str, Expr],
    var: str = "x",
    x0: float = 0.0,
    center: Optional[float] = None,
    order: int = 4,
) -> Record:
    """Generates order-N Taylor expansion of symbolic expression."""
    c = float(center if center is not None else x0)
    ts = TaylorSeries(expr, var=var, x0=c)
    res = ts.expand(order)
    res["center"] = c
    return Record(res)


def symbolic_solve_rational_linear(A: List[List[Any]], b: List[Any]) -> Dict[str, Any]:
    """Solves A x = b over exact rational fractions."""
    return ExactRationalLinearSolver.solve(A, b)


# ==============================================================================
# POLYNOMIAL GCD & RATIONAL ROOT FINDING
# ==============================================================================

class PolynomialGCDAndRoots:
    """Polynomial greatest common divisor, rational roots, and polynomial factorization."""

    @classmethod
    def poly_div(cls, p: List[float], q: List[float]) -> Tuple[List[float], List[float]]:
        """Divides polynomial p by q, returning quotient and remainder (highest power first)."""
        # Strip leading zeros
        p = list(p)
        q = list(q)
        while len(p) > 1 and abs(p[0]) < 1e-12:
            p.pop(0)
        while len(q) > 1 and abs(q[0]) < 1e-12:
            q.pop(0)

        if not q or (len(q) == 1 and abs(q[0]) < 1e-12):
            raise ZeroDivisionError("Cannot divide polynomial by zero")

        deg_p = len(p) - 1
        deg_q = len(q) - 1

        if deg_p < deg_q:
            return [0.0], p

        quotient = [0.0] * (deg_p - deg_q + 1)
        rem = list(p)

        for i in range(deg_p - deg_q + 1):
            lead = rem[i] / q[0]
            quotient[i] = lead
            for j in range(len(q)):
                rem[i + j] -= lead * q[j]

        # Clean remainder
        rem = rem[deg_p - deg_q + 1:]
        while len(rem) > 1 and abs(rem[0]) < 1e-12:
            rem.pop(0)
        if not rem:
            rem = [0.0]

        return [round(x, 6) for x in quotient], [round(x, 6) for x in rem]

    @classmethod
    def poly_gcd(cls, p: List[float], q: List[float]) -> List[float]:
        """Computes monic greatest common divisor of polynomials p and q via Euclidean algorithm."""
        a = list(p)
        b = list(q)

        while True:
            while len(b) > 1 and abs(b[0]) < 1e-12:
                b.pop(0)
            if len(b) == 1 and abs(b[0]) < 1e-12:
                break
            _, rem = cls.poly_div(a, b)
            a = b
            b = rem

        # Make monic
        lead = a[0]
        if abs(lead) > 1e-12:
            return [round(x / lead, 6) for x in a]
        return [1.0]

    @classmethod
    def find_rational_roots(cls, int_coeffs: List[int]) -> List[float]:
        """Finds all rational roots p/q of an integer coefficient polynomial."""
        # Clean trailing zero roots
        coeffs = list(int_coeffs)
        roots: List[float] = []
        while len(coeffs) > 1 and coeffs[-1] == 0:
            roots.append(0.0)
            coeffs.pop()

        if len(coeffs) <= 1:
            return sorted(list(set(roots)))

        an = abs(coeffs[0])
        a0 = abs(coeffs[-1])

        def get_factors(n: int) -> Set[int]:
            facts = set()
            for i in range(1, int(math.isqrt(n)) + 1):
                if n % i == 0:
                    facts.add(i)
                    facts.add(n // i)
            return facts

        p_factors = get_factors(a0) if a0 > 0 else {0}
        q_factors = get_factors(an) if an > 0 else {1}

        candidates = set()
        for p in p_factors:
            for q in q_factors:
                candidates.add(p / q)
                candidates.add(-p / q)

        for cand in candidates:
            # Horner's evaluation
            val = 0.0
            for c in coeffs:
                val = val * cand + c
            if abs(val) < 1e-9:
                roots.append(round(cand, 6))

        return sorted(list(set(roots)))


# ==============================================================================
# BRENT-DEKKER HYBRID NON-LINEAR ROOT FINDER
# ==============================================================================

class BrentRootFinder:
    """Brent's method combining bisection, secant, and inverse quadratic interpolation."""

    @classmethod
    def find_root(cls, f_expr_str: str, a: float, b: float, tol: float = 1e-10, max_iter: int = 100) -> Dict[str, Any]:
        """Finds root of f(x) = 0 on bracket [a, b] where f(a)*f(b) <= 0."""
        # Compile expression into evaluated function
        # Supports x, math functions
        safe_dict = {
            "math": math, "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "exp": math.exp, "log": math.log, "sqrt": math.sqrt, "abs": abs
        }

        def func(x_val: float) -> float:
            safe_dict["x"] = x_val
            return float(eval(f_expr_str, {"__builtins__": None}, safe_dict))

        fa = func(a)
        fb = func(b)

        if fa * fb > 0:
            raise ValueError(f"Root is not bracketed: f({a})={fa}, f({b})={fb} have the same sign")

        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb = fb, fa

        c = a
        fc = fa
        mflag = True
        d = 0.0
        iters = 0

        for it in range(max_iter):
            iters = it + 1
            if abs(fb) < tol:
                break
            if abs(b - a) < tol:
                break

            if abs(fa - fc) > 1e-14 and abs(fb - fc) > 1e-14:
                # Inverse Quadratic Interpolation
                s = (a * fb * fc) / ((fa - fb) * (fa - fc)) + \
                    (b * fa * fc) / ((fb - fa) * (fb - fc)) + \
                    (c * fa * fb) / ((fc - fa) * (fc - fb))
            else:
                # Secant method
                s = b - fb * (b - a) / (fb - fa)

            # Conditions to fall back to bisection
            cond1 = not ((3.0 * a + b) / 4.0 <= s <= b or b <= s <= (3.0 * a + b) / 4.0)
            cond2 = mflag and abs(s - b) >= abs(b - c) / 2.0
            cond3 = (not mflag) and abs(s - b) >= abs(c - d) / 2.0
            cond4 = mflag and abs(b - c) < tol
            cond5 = (not mflag) and abs(c - d) < tol

            if cond1 or cond2 or cond3 or cond4 or cond5:
                # Bisection step
                s = (a + b) / 2.0
                mflag = True
            else:
                mflag = False

            fs = func(s)
            d = c
            c = b
            fc = fb

            if fa * fs < 0:
                b = s
                fb = fs
            else:
                a = s
                fa = fs

            if abs(fa) < abs(fb):
                a, b = b, a
                fa, fb = fb, fa

        root = b
        return {
            "root": round(root, 8),
            "f_root": round(func(root), 10),
            "iterations": iters,
            "converged": abs(func(root)) < tol * 10,
        }


def symbolic_polynomial_gcd(p: List[float], q: List[float]) -> List[float]:
    """Calculates monic polynomial greatest common divisor."""
    return PolynomialGCDAndRoots.poly_gcd(p, q)


def symbolic_rational_roots(coeffs: List[int]) -> List[float]:
    """Finds all rational roots of integer polynomial."""
    return PolynomialGCDAndRoots.find_rational_roots(coeffs)


def symbolic_brent_root(expr: str, a: float, b: float) -> Any:
    """Finds non-linear root using Brent-Dekker hybrid method."""
    return Record(BrentRootFinder.find_root(expr, a, b))


class UnivariatePolynomialEuclideanFactorizer:
    """Implements square-free polynomial factorization and Sylvester resultant calculation."""

    @classmethod
    def _trim(cls, p: List[float], tol: float = 1e-9) -> List[float]:
        p = list(p)
        while len(p) > 1 and abs(p[-1]) < tol:
            p.pop()
        return p

    @classmethod
    def _poly_div(cls, a: List[float], b: List[float]) -> Tuple[List[float], List[float]]:
        a = cls._trim(a)
        b = cls._trim(b)
        if len(b) == 1 and abs(b[0]) < 1e-12:
            raise ZeroDivisionError("Polynomial division by zero")
        if len(a) < len(b):
            return [0.0], a

        rem = list(a)
        deg_b = len(b) - 1
        deg_a = len(a) - 1
        quot = [0.0] * (deg_a - deg_b + 1)
        lead_b = b[-1]

        for i in range(deg_a - deg_b, -1, -1):
            coeff = rem[i + deg_b] / lead_b
            quot[i] = coeff
            for j in range(deg_b + 1):
                rem[i + j] -= coeff * b[j]

        return cls._trim(quot), cls._trim(rem)

    @classmethod
    def _poly_gcd(cls, a: List[float], b: List[float]) -> List[float]:
        x = cls._trim(a)
        y = cls._trim(b)
        while len(y) > 1 or (len(y) == 1 and abs(y[0]) > 1e-9):
            _, r = cls._poly_div(x, y)
            x = y
            y = r
        lead = x[-1] if x else 1.0
        if abs(lead) > 1e-12:
            return [round(c / lead, 6) for c in x]
        return x

    @classmethod
    def _derivative(cls, p: List[float]) -> List[float]:
        if len(p) <= 1:
            return [0.0]
        return [round(i * c, 6) for i, c in enumerate(p[1:], start=1)]

    @classmethod
    def square_free_factors(cls, coeffs: List[float]) -> Dict[str, Any]:
        """Yun's algorithm for square-free factorization of monic polynomial."""
        p = cls._trim(coeffs)
        if len(p) <= 1:
            return {
                "degree": 0,
                "factors_count": 0,
                "factors": [],
                "is_square_free": True,
            }
        lead = p[-1]
        p = [c / lead for c in p]

        p_prime = cls._derivative(p)
        a0 = p
        b0 = cls._poly_gcd(a0, p_prime)
        c0, _ = cls._poly_div(a0, b0)
        d0, _ = cls._poly_div(p_prime, b0)

        c_i = c0
        d_i = d0
        factors = []
        i = 1

        while len(c_i) > 1:
            c_prime = cls._derivative(c_i)
            diff = [0.0] * max(len(d_i), len(c_prime))
            for k in range(len(diff)):
                d_val = d_i[k] if k < len(d_i) else 0.0
                cp_val = c_prime[k] if k < len(c_prime) else 0.0
                diff[k] = d_val - cp_val
            a_i = cls._poly_gcd(c_i, diff)
            if len(a_i) > 1:
                factors.append({"multiplicity": i, "factor": [round(c, 4) for c in a_i]})
            c_i, _ = cls._poly_div(c_i, a_i)
            diff_adj, _ = cls._poly_div(diff, a_i)
            d_i = diff_adj
            i += 1
            if i > 20:
                break

        is_sq_free = len(factors) == 1 and factors[0]["multiplicity"] == 1

        return {
            "degree": len(coeffs) - 1,
            "factors_count": len(factors),
            "factors": [Record(f) for f in factors],
            "is_square_free": is_sq_free,
        }

    @classmethod
    def resultant(cls, p: List[float], q: List[float]) -> Dict[str, Any]:
        """Calculates resultant of p and q via Sylvester determinant."""
        p = cls._trim(p)
        q = cls._trim(q)
        m = len(p) - 1
        n = len(q) - 1
        if m < 0 or n < 0:
            return {"resultant": 0.0, "has_common_root": False}
        if m == 0 and n == 0:
            return {"resultant": 1.0, "has_common_root": False}

        dim = m + n
        matrix = [[0.0] * dim for _ in range(dim)]

        p_desc = list(reversed(p))
        q_desc = list(reversed(q))

        for i in range(n):
            for j in range(len(p_desc)):
                matrix[i][i + j] = p_desc[j]

        for i in range(m):
            for j in range(len(q_desc)):
                matrix[n + i][i + j] = q_desc[j]

        det = 1.0
        mat = [list(row) for row in matrix]
        for i in range(dim):
            pivot = i
            max_val = abs(mat[i][i])
            for r in range(i + 1, dim):
                if abs(mat[r][i]) > max_val:
                    max_val = abs(mat[r][i])
                    pivot = r
            if max_val < 1e-12:
                det = 0.0
                break
            if pivot != i:
                mat[i], mat[pivot] = mat[pivot], mat[i]
                det = -det
            det *= mat[i][i]
            for r in range(i + 1, dim):
                factor = mat[r][i] / mat[i][i]
                for c in range(i + 1, dim):
                    mat[r][c] -= factor * mat[i][c]

        return {
            "p_degree": m,
            "q_degree": n,
            "sylvester_dim": dim,
            "resultant": round(det, 6),
            "has_common_root": abs(det) < 1e-5,
        }


class PadeApproximantGenerator:
    """Constructs Padé rational approximants [M/N] from Taylor series coefficients."""

    @classmethod
    def compute(
        cls,
        taylor_coeffs: List[float],
        m_degree: int,
        n_degree: int,
        eval_points: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        c = [float(x) for x in taylor_coeffs]
        needed = m_degree + n_degree + 1
        while len(c) < needed:
            c.append(0.0)

        q = [1.0] + [0.0] * n_degree
        if n_degree > 0:
            mat = [[0.0] * n_degree for _ in range(n_degree)]
            rhs = [0.0] * n_degree
            for i in range(1, n_degree + 1):
                row_idx = i - 1
                rhs[row_idx] = -c[m_degree + i]
                for j in range(1, n_degree + 1):
                    col_idx = j - 1
                    idx = m_degree + i - j
                    mat[row_idx][col_idx] = c[idx] if idx >= 0 else 0.0

            for i in range(n_degree):
                pivot = i
                for r in range(i + 1, n_degree):
                    if abs(mat[r][i]) > abs(mat[pivot][i]):
                        pivot = r
                mat[i], mat[pivot] = mat[pivot], mat[i]
                rhs[i], rhs[pivot] = rhs[pivot], rhs[i]

                if abs(mat[i][i]) > 1e-12:
                    for r in range(i + 1, n_degree):
                        factor = mat[r][i] / mat[i][i]
                        for col in range(i + 1, n_degree):
                            mat[r][col] -= factor * mat[i][col]
                        rhs[r] -= factor * rhs[i]

            q_sol = [0.0] * n_degree
            for i in range(n_degree - 1, -1, -1):
                if abs(mat[i][i]) > 1e-12:
                    s = sum(mat[i][j] * q_sol[j] for j in range(i + 1, n_degree))
                    q_sol[i] = (rhs[i] - s) / mat[i][i]

            for j in range(1, n_degree + 1):
                q[j] = q_sol[j - 1]

        p = [0.0] * (m_degree + 1)
        for k in range(m_degree + 1):
            p[k] = sum(c[k - j] * q[j] for j in range(min(k, n_degree) + 1))

        def eval_rational(x: float) -> float:
            num = sum(p[k] * (x ** k) for k in range(len(p)))
            den = sum(q[k] * (x ** k) for k in range(len(q)))
            return num / den if abs(den) > 1e-12 else float("inf")

        def eval_taylor(x: float) -> float:
            return sum(c[k] * (x ** k) for k in range(min(len(c), m_degree + n_degree + 1)))

        eval_results = []
        if eval_points:
            for pt in eval_points:
                val_pade = eval_rational(pt)
                val_taylor = eval_taylor(pt)
                eval_results.append({
                    "x": pt,
                    "pade_value": round(val_pade, 6),
                    "taylor_value": round(val_taylor, 6),
                    "difference": round(abs(val_pade - val_taylor), 6),
                })

        return {
            "m_degree": m_degree,
            "n_degree": n_degree,
            "numerator_coeffs": [round(x, 6) for x in p],
            "denominator_coeffs": [round(x, 6) for x in q],
            "evaluations": [Record(e) for e in eval_results],
        }


def symbolic_square_free_factorization(coeffs: List[float]) -> Any:
    """Performs Yun square-free factorization on polynomial."""
    return Record(UnivariatePolynomialEuclideanFactorizer.square_free_factors(coeffs))


def symbolic_polynomial_resultant(p: List[float], q: List[float]) -> Any:
    """Calculates polynomial Sylvester resultant."""
    return Record(UnivariatePolynomialEuclideanFactorizer.resultant(p, q))


def symbolic_pade_approximant(
    taylor_coeffs: List[float],
    m_degree: int,
    n_degree: int,
    eval_points: Optional[List[float]] = None,
) -> Any:
    """Computes [M/N] Padé rational approximant from Taylor series coefficients."""
    return Record(PadeApproximantGenerator.compute(taylor_coeffs, m_degree, n_degree, eval_points=eval_points))


# ==============================================================================
# MULTIVARIATE GROEBNER BASIS VIA BUCHBERGER'S ALGORITHM
# ==============================================================================

class GroebnerBasisBuchberger:
    """Exact multivariate polynomial ideal reduction and Groebner basis computation.

    Implements:
    - Term orderings: Lexicographic (lex), Graded Lexicographic (grlex), Graded Reverse Lex (grevlex).
    - Multivariate polynomial division algorithm over Q[x_1, ..., x_n].
    - S-polynomial construction and pair reduction.
    - Minimal and fully reduced Groebner basis normalization.
    """

    @staticmethod
    def _parse_poly_str(poly_str: str, vars_list: List[str]) -> Dict[Tuple[int, ...], float]:
        """Parses a multivariate polynomial string into an exponent-tuple-to-coefficient map."""
        s = poly_str.replace(" ", "").replace("-", "+-")
        terms = [t for t in s.split("+") if t]
        poly: Dict[Tuple[int, ...], float] = {}

        n_vars = len(vars_list)
        var_indices = {v: i for i, v in enumerate(vars_list)}

        for term in terms:
            if not term:
                continue
            # Extract sign and coefficient
            coeff = 1.0
            # Tokenize into variable powers
            # Match leading number/sign
            m_lead = re.match(r"^([+-]?(?:\d+(?:\.\d+)?|\d+))?(.*)$", term)
            if m_lead:
                c_str = m_lead.group(1)
                rest = m_lead.group(2)
                if c_str == "-" or c_str == "+-":
                    coeff = -1.0
                elif c_str == "+" or not c_str:
                    coeff = 1.0
                else:
                    coeff = float(c_str)
            else:
                rest = term

            exps = [0] * n_vars
            # Find all var^power in rest
            var_matches = re.findall(r"([A-Za-z_]\w*)(?:\^(\d+))?", rest)
            for vname, pow_str in var_matches:
                if vname in var_indices:
                    idx = var_indices[vname]
                    p = int(pow_str) if pow_str else 1
                    exps[idx] += p

            key = tuple(exps)
            poly[key] = poly.get(key, 0.0) + coeff

        # Clean zero terms
        return {k: v for k, v in poly.items() if abs(v) > 1e-12}

    @staticmethod
    def _term_compare(t1: Tuple[int, ...], t2: Tuple[int, ...], order: str = "lex") -> int:
        """Returns 1 if t1 > t2, -1 if t1 < t2, 0 if t1 == t2."""
        if t1 == t2:
            return 0
        if order == "lex":
            for a, b in zip(t1, t2):
                if a > b:
                    return 1
                if a < b:
                    return -1
            return 0
        elif order == "grlex":
            d1, d2 = sum(t1), sum(t2)
            if d1 > d2:
                return 1
            if d1 < d2:
                return -1
            for a, b in zip(t1, t2):
                if a > b:
                    return 1
                if a < b:
                    return -1
            return 0
        elif order == "grevlex":
            d1, d2 = sum(t1), sum(t2)
            if d1 > d2:
                return 1
            if d1 < d2:
                return -1
            for a, b in zip(reversed(t1), reversed(t2)):
                if a < b:
                    return 1
                if a > b:
                    return -1
            return 0
        return 0

    @classmethod
    def _leading_term(cls, poly: Dict[Tuple[int, ...], float], order: str = "lex") -> Tuple[Tuple[int, ...], float]:
        """Finds leading monomial and leading coefficient."""
        if not poly:
            return ((), 0.0)
        best_m = None
        for m in poly:
            if best_m is None or cls._term_compare(m, best_m, order) > 0:
                best_m = m
        return (best_m, poly[best_m])

    @classmethod
    def _poly_add(cls, p1: Dict[Tuple[int, ...], float], p2: Dict[Tuple[int, ...], float], scale2: float = 1.0) -> Dict[Tuple[int, ...], float]:
        res = dict(p1)
        for m, c in p2.items():
            res[m] = res.get(m, 0.0) + scale2 * c
        return {k: v for k, v in res.items() if abs(v) > 1e-12}

    @classmethod
    def _poly_mul_monomial(cls, p: Dict[Tuple[int, ...], float], mono: Tuple[int, ...], coeff: float) -> Dict[Tuple[int, ...], float]:
        res = {}
        for m, c in p.items():
            new_m = tuple(a + b for a, b in zip(m, mono))
            res[new_m] = c * coeff
        return res

    @classmethod
    def _monomial_divides(cls, m1: Tuple[int, ...], m2: Tuple[int, ...]) -> bool:
        return all(a <= b for a, b in zip(m1, m2))

    @classmethod
    def _monomial_lcm(cls, m1: Tuple[int, ...], m2: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(max(a, b) for a, b in zip(m1, m2))

    @classmethod
    def multivariate_division(
        cls,
        f: Dict[Tuple[int, ...], float],
        divisors: List[Dict[Tuple[int, ...], float]],
        order: str = "lex",
    ) -> Tuple[List[Dict[Tuple[int, ...], float]], Dict[Tuple[int, ...], float]]:
        """Multivariate polynomial division algorithm: f = sum(q_i * g_i) + r."""
        p = dict(f)
        quotients = [{} for _ in divisors]
        remainder: Dict[Tuple[int, ...], float] = {}

        while p:
            lm_p, lc_p = cls._leading_term(p, order)
            divided = False
            for i, g in enumerate(divisors):
                if not g:
                    continue
                lm_g, lc_g = cls._leading_term(g, order)
                if cls._monomial_divides(lm_g, lm_p):
                    q_mono = tuple(a - b for a, b in zip(lm_p, lm_g))
                    q_coeff = lc_p / lc_g
                    quotients[i][q_mono] = quotients[i].get(q_mono, 0.0) + q_coeff
                    # p = p - q_coeff * q_mono * g
                    sub_term = cls._poly_mul_monomial(g, q_mono, q_coeff)
                    p = cls._poly_add(p, sub_term, scale2=-1.0)
                    divided = True
                    break
            if not divided:
                remainder[lm_p] = remainder.get(lm_p, 0.0) + lc_p
                del p[lm_p]

        remainder = {k: v for k, v in remainder.items() if abs(v) > 1e-12}
        return quotients, remainder

    @classmethod
    def s_polynomial(
        cls,
        f: Dict[Tuple[int, ...], float],
        g: Dict[Tuple[int, ...], float],
        order: str = "lex",
    ) -> Dict[Tuple[int, ...], float]:
        """Computes S-polynomial S(f, g) = (L / LT(f)) * f - (L / LT(g)) * g."""
        lm_f, lc_f = cls._leading_term(f, order)
        lm_g, lc_g = cls._leading_term(g, order)
        lcm = cls._monomial_lcm(lm_f, lm_g)

        f_factor_m = tuple(a - b for a, b in zip(lcm, lm_f))
        g_factor_m = tuple(a - b for a, b in zip(lcm, lm_g))

        f_scaled = cls._poly_mul_monomial(f, f_factor_m, 1.0 / lc_f)
        g_scaled = cls._poly_mul_monomial(g, g_factor_m, 1.0 / lc_g)

        return cls._poly_add(f_scaled, g_scaled, scale2=-1.0)

    @classmethod
    def compute(
        cls,
        polynomials: List[str],
        variables: Optional[List[str]] = None,
        order: str = "lex",
    ) -> Dict[str, Any]:
        """Computes reduced Groebner basis using Buchberger's algorithm."""
        # Auto-detect variables if not provided
        if variables is None:
            found_vars = set()
            for p in polynomials:
                found_vars.update(re.findall(r"[A-Za-z_]\w*", p))
            vars_list = sorted(list(found_vars))
        else:
            vars_list = list(variables)

        parsed_polys = [cls._parse_poly_str(p, vars_list) for p in polynomials]
        basis = [p for p in parsed_polys if p]

        pairs = [(i, j) for i in range(len(basis)) for j in range(i + 1, len(basis))]

        while pairs:
            i, j = pairs.pop(0)
            p_i, p_j = basis[i], basis[j]
            s_poly = cls.s_polynomial(p_i, p_j, order)
            if not s_poly:
                continue

            _, rem = cls.multivariate_division(s_poly, basis, order)
            if rem:
                # Normalize leading coefficient to 1
                _, lc = cls._leading_term(rem, order)
                normalized_rem = {m: c / lc for m, c in rem.items()}
                new_idx = len(basis)
                for k in range(len(basis)):
                    pairs.append((k, new_idx))
                basis.append(normalized_rem)

        # Reduce basis to minimal and canonical reduced form
        # 1. Eliminate redundant elements whose LM is divisible by another
        minimal = []
        for i, g in enumerate(basis):
            lm_g, _ = cls._leading_term(g, order)
            redundant = False
            for j, h in enumerate(basis):
                if i != j:
                    lm_h, _ = cls._leading_term(h, order)
                    if cls._monomial_divides(lm_h, lm_g):
                        redundant = True
                        break
            if not redundant and g not in minimal:
                minimal.append(g)

        # 2. Reduce each element modulo all others
        reduced = []
        for i, g in enumerate(minimal):
            others = [h for j, h in enumerate(minimal) if i != j]
            _, rem = cls.multivariate_division(g, others, order)
            if rem:
                _, lc = cls._leading_term(rem, order)
                canonical = {m: round(c / lc, 6) for m, c in rem.items()}
                reduced.append(canonical)

        # Format output into polynomial strings
        def poly_to_str(poly: Dict[Tuple[int, ...], float]) -> str:
            sorted_terms = sorted(poly.items(), key=lambda item: cls._leading_term({item[0]: item[1]}, order)[0], reverse=True)
            parts = []
            for m, c in sorted_terms:
                if abs(c) < 1e-6:
                    continue
                var_parts = []
                for vname, p in zip(vars_list, m):
                    if p == 1:
                        var_parts.append(vname)
                    elif p > 1:
                        var_parts.append(f"{vname}^{p}")
                m_str = "*".join(var_parts)

                if not var_parts:
                    parts.append(f"{c:g}")
                elif abs(c - 1.0) < 1e-6:
                    parts.append(m_str)
                elif abs(c + 1.0) < 1e-6:
                    parts.append(f"-{m_str}")
                else:
                    parts.append(f"{c:g}*{m_str}")

            return " + ".join(parts).replace("+ -", "- ") if parts else "0"

        basis_strings = [poly_to_str(g) for g in reduced]

        return {
            "variables": vars_list,
            "order": order,
            "input_polynomials": polynomials,
            "groebner_basis": basis_strings,
            "basis_size": len(reduced),
            "is_trivial": any(g == {(0,) * len(vars_list): 1.0} for g in reduced),
        }


# ==============================================================================
# SYMBOLIC SERIES EXPANDER (TAYLOR & MACLAURIN)
# ==============================================================================

class SymbolicSeriesExpander:
    """Exact symbolic Taylor & Maclaurin polynomial series expansion."""

    @classmethod
    def expand(
        cls,
        expression_str: str,
        var: str = "x",
        center: float = 0.0,
        order: int = 4,
    ) -> Dict[str, Any]:
        expr = parse_expr(expression_str)
        cur_expr = expr

        coeffs: List[float] = []
        deriv_strs: List[str] = []

        factorial = 1.0
        for k in range(order + 1):
            if k > 0:
                factorial *= k
            deriv_strs.append(str(cur_expr))
            val_at_center = cur_expr.eval({var: center})
            ck = val_at_center / factorial
            coeffs.append(round(ck, 6))
            if k < order:
                cur_expr = cur_expr.diff(var).simplify()

        # Format polynomial string
        poly_parts = []
        for k, c in enumerate(coeffs):
            if abs(c) < 1e-6:
                continue
            if k == 0:
                poly_parts.append(f"{c:g}")
            else:
                var_part = var if center == 0.0 else f"({var} - {center:g})"
                pow_part = var_part if k == 1 else f"{var_part}^{k}"
                if abs(c - 1.0) < 1e-6:
                    poly_parts.append(pow_part)
                elif abs(c + 1.0) < 1e-6:
                    poly_parts.append(f"-{pow_part}")
                else:
                    poly_parts.append(f"{c:g}*{pow_part}")

        poly_str = " + ".join(poly_parts).replace("+ -", "- ") if poly_parts else "0"

        return {
            "expression": expression_str,
            "variable": var,
            "center": center,
            "order": order,
            "coefficients": coeffs,
            "polynomial_series": poly_str,
            "derivatives": deriv_strs,
        }


def symbolic_groebner_basis(
    polynomials: List[str],
    variables: Optional[List[str]] = None,
    order: str = "lex",
) -> Record:
    """Computes exact reduced Groebner basis using Buchberger's algorithm."""
    return Record(GroebnerBasisBuchberger.compute(polynomials, variables=variables, order=order))


def symbolic_eliminate_variables(
    polynomials: List[str],
    eliminate_vars: List[str],
    all_vars: Optional[List[str]] = None,
) -> Record:
    """Eliminates specified variables from polynomial system via Elimination Theorem."""
    if all_vars is None:
        found_vars = set()
        for p in polynomials:
            found_vars.update(re.findall(r"[A-Za-z_]\w*", p))
        all_vars = sorted(list(found_vars))

    rem_vars = [v for v in all_vars if v not in eliminate_vars]
    ordered_vars = list(eliminate_vars) + rem_vars

    gb_res = GroebnerBasisBuchberger.compute(polynomials, variables=ordered_vars, order="lex")
    basis = gb_res["groebner_basis"]

    # Filter polynomials containing none of the eliminate_vars
    eliminated_polys = []
    for poly_str in basis:
        if not any(re.search(r"\b" + re.escape(ev) + r"\b", poly_str) for ev in eliminate_vars):
            eliminated_polys.append(poly_str)

    return Record({
        "eliminated_variables": eliminate_vars,
        "remaining_variables": rem_vars,
        "elimination_ideal_basis": eliminated_polys,
        "full_groebner_basis": basis,
    })


def symbolic_series_expansion(
    expression_str: str,
    var: str = "x",
    center: float = 0.0,
    order: int = 4,
) -> Record:
    """Computes exact symbolic Taylor/Maclaurin series expansion."""
    return Record(SymbolicSeriesExpander.expand(expression_str, var=var, center=center, order=order))




