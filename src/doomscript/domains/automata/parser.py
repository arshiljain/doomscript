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

        # simulate cellular rule <rule> [with width <w>] [with generations <gen>] into <target>
        m_ca = re.match(
            r"^simulate\s+cellular\s+rule\s+(\d+)(?:\s+with\s+width\s+(\d+))?(?:\s+with\s+generations\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ca:
            rule = m_ca.group(1).strip()
            w = m_ca.group(2) if m_ca.group(2) else "31"
            gen = m_ca.group(3) if m_ca.group(3) else "20"
            target = m_ca.group(4).strip()
            return f"set {target} to automata_simulate_rule({rule}, width={w}, generations={gen})"

        # simulate game of life with rows <rows> cols <cols> live <cells> [with steps <steps>] into <target>
        m_gol = re.match(
            r"^simulate\s+game\s+of\s+life\s+with\s+rows\s+(.+?)\s+cols\s+(.+?)\s+live\s+(.+?)(?:\s+with\s+steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gol:
            rows, cols, cells = m_gol.group(1).strip(), m_gol.group(2).strip(), m_gol.group(3).strip()
            steps = m_gol.group(4) if m_gol.group(4) else "10"
            target = m_gol.group(5).strip()
            return f"set {target} to automata_simulate_life({rows}, {cols}, {cells}, steps={steps})"

        # simulate multitape turing machine with tapes <tapes> state <q0> accept <f> transitions <trans> [with max_steps <m>] into <target>
        m_mt = re.match(
            r"^simulate\s+multitape\s+turing\s+machine\s+with\s+tapes\s+(.+?)\s+state\s+(.+?)\s+accept\s+(.+?)\s+transitions\s+(.+?)(?:\s+with\s+max_steps\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mt:
            tapes, q0, acc, trans = m_mt.group(1).strip(), m_mt.group(2).strip(), m_mt.group(3).strip(), m_mt.group(4).strip()
            if not (q0.startswith('"') or q0.startswith("'")):
                q0 = f'"{q0}"'
            max_s = m_mt.group(5) if m_mt.group(5) else "500"
            target = m_mt.group(6).strip()
            return f"set {target} to automata_run_multitape_tm(len({tapes}), {tapes}, {q0}, {acc}, {trans}, max_steps={max_s})"

        # parse cyk grammar <grammar> start <start> tokens <tokens> into <target>
        m_cyk = re.match(
            r"^parse\s+cyk\s+grammar\s+(.+?)\s+start\s+(.+?)\s+tokens\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cyk:
            gram, start, toks, target = m_cyk.group(1).strip(), m_cyk.group(2).strip(), m_cyk.group(3).strip(), m_cyk.group(4).strip()
            if not (start.startswith('"') or start.startswith("'")):
                start = f'"{start}"'
            return f"set {target} to automata_cyk_parse({gram}, {start}, {toks})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Automata domain does not define declarative blocks")
