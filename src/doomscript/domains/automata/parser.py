"""Automata Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class AutomataDomainParser(DomainParser):
    """Parses spoken-English DFA, regular expressions, and Turing Machine statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # compile regex <regex> to dfa into <target>
        m_reg = re.match(
            r"^compile\s+regex\s+(.+?)\s+to\s+dfa\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_reg:
            regex, target = m_reg.group(1).strip(), m_reg.group(2).strip()
            if not (regex.startswith('"') or regex.startswith("'") or regex.isidentifier()):
                regex = f'"{regex}"'
            return f"set {target} to automata_regex_to_dfa({regex})"

        # minimize dfa <dfa> into <target>
        m_min = re.match(
            r"^minimize\s+dfa\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_min:
            dfa, target = m_min.group(1).strip(), m_min.group(2).strip()
            return f"set {target} to automata_minimize_dfa({dfa})"

        # check if dfa <dfa> accepts <input_str> into <target>
        m_acc = re.match(
            r"^check\s+if\s+dfa\s+(.+?)\s+accepts\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_acc:
            dfa, input_str, target = m_acc.group(1).strip(), m_acc.group(2).strip(), m_acc.group(3).strip()
            if not (input_str.startswith('"') or input_str.startswith("'") or input_str.isidentifier()):
                input_str = f'"{input_str}"'
            return f"set {target} to automata_dfa_accepts({dfa}, {input_str})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Automata domain does not define declarative blocks")
