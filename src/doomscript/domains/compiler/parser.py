"""Compiler Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class CompilerDomainParser(DomainParser):
    """Parses spoken-English bytecode VM, Assembler, and Pratt parser statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # assemble bytecode [from text] <text> into <target>
        m_asm = re.match(
            r"^assemble\s+bytecode(?:\s+from\s+text)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_asm:
            txt, target = m_asm.group(1).strip(), m_asm.group(2).strip()
            return f"set {target} to compiler_assemble_string({txt})"

        # execute bytecode [program] <prog> into <target>
        m_run = re.match(
            r"^execute\s+bytecode(?:\s+program)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
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

        # optimize instructions <insts> with dce and constant folding into <target>
        m_opt = re.match(
            r"^optimize\s+instructions\s+(.+?)\s+with\s+dce\s+and\s+constant\s+folding\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_opt:
            insts, target = m_opt.group(1).strip(), m_opt.group(2).strip()
            return f"set {target} to compiler_optimize_dce_and_fold({insts})"

        # build dominator tree with entry <entry> nodes <nodes> edges <edges> into <target>
        m_dom = re.match(
            r"^build\s+dominator\s+tree\s+with\s+entry\s+(.+?)\s+nodes\s+(.+?)\s+edges\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dom:
            entry, nodes, edges, target = m_dom.group(1).strip(), m_dom.group(2).strip(), m_dom.group(3).strip(), m_dom.group(4).strip()
            return f"set {target} to compiler_build_dominator_tree({entry}, {nodes}, {edges})"

        # build ll1 parse table start <start> grammar <grammar> into <target>
        m_ll1 = re.match(
            r"^build\s+ll1\s+parse\s+table\s+start\s+(.+?)\s+grammar\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ll1:
            start, grammar, target = m_ll1.group(1).strip(), m_ll1.group(2).strip(), m_ll1.group(3).strip()
            if not (start.startswith('"') or start.startswith("'")):
                start = f'"{start}"'
            return f"set {target} to compiler_build_ll1_table({start}, {grammar})"

        # optimize loop invariants in blocks <blocks> header <header> body <body_blocks> into <target>
        m_licm = re.match(
            r"^optimize\s+loop\s+invariants\s+in\s+blocks\s+(.+?)\s+header\s+(.+?)\s+body\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_licm:
            blocks, header, body_blocks, target = m_licm.group(1).strip(), m_licm.group(2).strip(), m_licm.group(3).strip(), m_licm.group(4).strip()
            if not (header.startswith('"') or header.startswith("'")):
                header = f'"{header}"'
            return f"set {target} to compiler_optimize_licm({blocks}, {header}, {body_blocks})"

        # optimize ssa ir <ir_expr> with sccp into <target>
        m_sccp = re.match(
            r"^optimize\s+ssa\s+ir\s+(.+?)\s+with\s+sccp\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sccp:
            ir_expr, target = m_sccp.group(1).strip(), m_sccp.group(2).strip()
            return f"set {target} to compiler_sccp_optimize({ir_expr})"

        # earley parse <tokens_expr> with grammar <grammar_expr> starting at <start_expr> into <target>
        m_earley = re.match(
            r"^earley\s+parse\s+(.+?)\s+with\s+grammar\s+(.+?)\s+starting\s+at\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_earley:
            tokens, grammar, start, target = (
                m_earley.group(1).strip(),
                m_earley.group(2).strip(),
                m_earley.group(3).strip(),
                m_earley.group(4).strip(),
            )
            if not (start.startswith('"') or start.startswith("'")):
                start = f'"{start}"'
            return f"set {target} to compiler_earley_parse({grammar}, {start}, {tokens})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Compiler domain does not define declarative blocks")
