"""Symbolic Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class SymbolicDomainParser(DomainParser):
    """Parses spoken-English symbolic differentiation, simplification, and evaluation statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # differentiate <expr> with respect to <var> into <target>
        m_diff = re.match(
            r"^differentiate\s+(.+?)\s+with\s+respect\s+to\s+([A-Za-z_]\w*)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_diff:
            expr, var, target = m_diff.group(1).strip(), m_diff.group(2).strip(), m_diff.group(3).strip()
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            return f"set {target} to symbolic_diff({expr}, var='{var}')"

        # simplify expression <expr> into <target>
        m_simp = re.match(
            r"^simplify\s+expression\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_simp:
            expr, target = m_simp.group(1).strip(), m_simp.group(2).strip()
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            return f"set {target} to symbolic_simplify({expr})"

        # evaluate expression <expr> with <subs> into <target>
        m_eval = re.match(
            r"^evaluate\s+expression\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_eval:
            expr, subs, target = m_eval.group(1).strip(), m_eval.group(2).strip(), m_eval.group(3).strip()
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            return f"set {target} to symbolic_eval({expr}, {subs})"

        # calculate polynomial gcd for <p> and <q> into <target>
        m_gcd = re.match(
            r"^calculate\s+polynomial\s+gcd\s+for\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gcd:
            p, q, target = m_gcd.group(1).strip(), m_gcd.group(2).strip(), m_gcd.group(3).strip()
            return f"set {target} to symbolic_polynomial_gcd({p}, {q})"

        # find rational roots for polynomial <coeffs> into <target>
        m_roots = re.match(
            r"^find\s+rational\s+roots\s+for\s+polynomial\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_roots:
            coeffs, target = m_roots.group(1).strip(), m_roots.group(2).strip()
            return f"set {target} to symbolic_rational_roots({coeffs})"

        # find root for expression <expr> bracket <a> to <b> into <target>
        m_brent = re.match(
            r"^find\s+root\s+for\s+expression\s+(.+?)\s+bracket\s+(.+?)\s+to\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_brent:
            expr, a, b, target = m_brent.group(1).strip(), m_brent.group(2).strip(), m_brent.group(3).strip(), m_brent.group(4).strip()
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            return f"set {target} to symbolic_brent_root({expr}, {a}, {b})"

        # factor square free polynomial <coeffs> into <target>
        m_sqf = re.match(
            r"^factor\s+square\s+free\s+polynomial\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sqf:
            coeffs, target = m_sqf.group(1).strip(), m_sqf.group(2).strip()
            return f"set {target} to symbolic_square_free_factorization({coeffs})"

        # calculate resultant of polynomials <p> and <q> into <target>
        m_res = re.match(
            r"^calculate\s+resultant\s+of\s+polynomials\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_res:
            p, q, target = m_res.group(1).strip(), m_res.group(2).strip(), m_res.group(3).strip()
            return f"set {target} to symbolic_polynomial_resultant({p}, {q})"

        # calculate pade approximant coefficients <coeffs> m <m> n <n> [with eval <pts>] into <target>
        m_pade = re.match(
            r"^calculate\s+pade\s+approximant\s+coefficients\s+(.+?)\s+m\s+(\d+)\s+n\s+(\d+)(?:\s+with\s+eval\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pade:
            coeffs, m, n = m_pade.group(1).strip(), m_pade.group(2).strip(), m_pade.group(3).strip()
            eval_pts = m_pade.group(4).strip() if m_pade.group(4) else "None"
            target = m_pade.group(5).strip()
            return f"set {target} to symbolic_pade_approximant({coeffs}, {m}, {n}, eval_points={eval_pts})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Symbolic domain does not define declarative blocks")
