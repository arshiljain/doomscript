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

        # simplify [expression] <expr> into <target>
        m_simp = re.match(
            r"^simplify(?:\s+expression)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_simp:
            expr, target = m_simp.group(1).strip(), m_simp.group(2).strip()
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            return f"set {target} to symbolic_simplify({expr})"

        # evaluate [expression] <expr> with <subs> into <target>
        m_eval = re.match(
            r"^evaluate(?:\s+expression)?\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
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

        # calculate groebner basis for <polys> [variables <vars>] [order <ord>] into <target>
        m_grob = re.match(
            r"^calculate\s+groebner\s+basis\s+for\s+(.+?)(?:\s+variables\s+(.+?))?(?:\s+order\s+(\w+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_grob:
            polys, vars_arg, order_arg, target = (
                m_grob.group(1).strip(),
                m_grob.group(2),
                m_grob.group(3),
                m_grob.group(4).strip(),
            )
            v_val = vars_arg.strip() if vars_arg else "None"
            o_val = f'"{order_arg.strip()}"' if order_arg else '"lex"'
            return f"set {target} to symbolic_groebner_basis({polys}, variables={v_val}, order={o_val})"

        # expand taylor series for <expr> [var <var>] [center <c>] [order <ord>] into <target>
        m_tay = re.match(
            r"^expand\s+taylor\s+series\s+for\s+(.+?)(?:\s+var\s+([A-Za-z_]\w*))?(?:\s+center\s+(.+?))?(?:\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tay:
            expr, v_name, c_val, o_val, target = (
                m_tay.group(1).strip(),
                m_tay.group(2),
                m_tay.group(3),
                m_tay.group(4),
                m_tay.group(5).strip(),
            )
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            v_arg = f'"{v_name.strip()}"' if v_name else '"x"'
            c_arg = c_val.strip() if c_val else "0.0"
            o_arg = o_val.strip() if o_val else "4"
            return f"set {target} to symbolic_taylor_series({expr}, var={v_arg}, center={c_arg}, order={o_arg})"

        # eliminate variables <vars> from polynomials <polys> into <target>
        m_elim = re.match(
            r"^eliminate\s+variables\s+(.+?)\s+from\s+polynomials\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_elim:
            vars_arg, polys_arg, target = m_elim.group(1).strip(), m_elim.group(2).strip(), m_elim.group(3).strip()
            return f"set {target} to symbolic_eliminate_variables({polys_arg}, {vars_arg})"

        # integrate risch expression <expr> [var <x>] into <target>
        m_risch = re.match(
            r"^integrate\s+risch\s+expression\s+(.+?)(?:\s+var\s+([A-Za-z_]\w*))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_risch:
            expr, v_name, target = m_risch.group(1).strip(), m_risch.group(2), m_risch.group(3).strip()
            if not (expr.startswith('"') or expr.startswith("'") or expr.isidentifier()):
                expr = f'"{expr}"'
            v_arg = f'"{v_name.strip()}"' if v_name else '"x"'
            return f"set {target} to symbolic_risch_integrate({expr}, var={v_arg})"

        # solve ode equation <ode> [dependent <y>] [independent <x>] into <target>
        m_ode = re.match(
            r"^solve\s+ode\s+equation\s+(.+?)(?:\s+dependent\s+([A-Za-z_]\w*))?(?:\s+independent\s+([A-Za-z_]\w*))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ode:
            ode_eq, dep, indep, target = m_ode.group(1).strip(), m_ode.group(2), m_ode.group(3), m_ode.group(4).strip()
            if not (ode_eq.startswith('"') or ode_eq.startswith("'") or ode_eq.isidentifier()):
                ode_eq = f'"{ode_eq}"'
            dep_arg = f'"{dep.strip()}"' if dep else '"y"'
            indep_arg = f'"{indep.strip()}"' if indep else '"x"'
            return f"set {target} to symbolic_ode_solve({ode_eq}, dep_var={dep_arg}, indep_var={indep_arg})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Symbolic domain does not define declarative blocks")
