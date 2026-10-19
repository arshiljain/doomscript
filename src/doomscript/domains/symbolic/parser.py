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

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Symbolic domain does not define declarative blocks")
