"""Compiler Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class CompilerDomainParser(DomainParser):
    """Parses spoken-English bytecode VM, Assembler, and Pratt parser statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # assemble bytecode from text <text> into <target>
        m_asm = re.match(
            r"^assemble\s+bytecode\s+from\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_asm:
            txt, target = m_asm.group(1).strip(), m_asm.group(2).strip()
            return f"set {target} to compiler_assemble_string({txt})"

        # execute bytecode program <prog> into <target>
        m_run = re.match(
            r"^execute\s+bytecode\s+program\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_run:
            prog, target = m_run.group(1).strip(), m_run.group(2).strip()
            return f"set {target} to compiler_run_bytecode({prog}['instructions'], {prog}['constants'])"

        # parse pratt expression <expr> into <target>
        m_pratt = re.match(
            r"^parse\s+pratt\s+expression\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_pratt:
            expr, target = m_pratt.group(1).strip(), m_pratt.group(2).strip()
            return f"set {target} to compiler_parse_pratt({expr})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Compiler domain does not define declarative blocks")
