"""Synthetic Biology Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class Synthetic_bioDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate hill activation for conc <x> k <k> n <n> into <target>
        m_act = re.match(r"^calculate\s+hill\s+activation\s+for\s+conc\s+(.+?)\s+k\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_act:
            return f"set {m_act.group(4)} to synbio_hill_activation({m_act.group(1)}, {m_act.group(2)}, {m_act.group(3)})"

        # calculate hill repression for conc <x> k <k> n <n> into <target>
        m_rep = re.match(r"^calculate\s+hill\s+repression\s+for\s+conc\s+(.+?)\s+k\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rep:
            return f"set {m_rep.group(4)} to synbio_hill_repression({m_rep.group(1)}, {m_rep.group(2)}, {m_rep.group(3)})"

        # calculate enzyme rate substrate <s> vmax <v> km <km> into <target>
        m_enz = re.match(r"^calculate\s+enzyme\s+rate\s+substrate\s+(.+?)\s+vmax\s+(.+?)\s+km\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_enz:
            return f"set {m_enz.group(4)} to synbio_michaelis_menten({m_enz.group(1)}, {m_enz.group(2)}, {m_enz.group(3)})"

        # check gibson overlap frag1 <f1> frag2 <f2> into <target>
        m_gib = re.match(r"^check\s+gibson\s+overlap\s+frag1\s+(.+?)\s+frag2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gib:
            return f"set {m_gib.group(3)} to synbio_gibson_assembly_overlap({m_gib.group(1)}, {m_gib.group(2)})"

        # step toggle switch u <u> v <v> into <target>
        m_tog = re.match(r"^step\s+toggle\s+switch\s+u\s+(.+?)\s+v\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tog:
            return f"set {m_tog.group(3)} to synbio_toggle_switch_step({m_tog.group(1)}, {m_tog.group(2)})"

        # step repressilator p1 <p1> p2 <p2> p3 <p3> into <target>
        m_rep = re.match(r"^step\s+repressilator\s+p1\s+(.+?)\s+p2\s+(.+?)\s+p3\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rep:
            return f"set {m_rep.group(4)} to synbio_repressilator_step({m_rep.group(1)}, {m_rep.group(2)}, {m_rep.group(3)})"

        # calculate codon adaptation index for sequence <seq> into <target>
        m_cai = re.match(r"^calculate\s+codon\s+adaptation\s+index\s+for\s+(?:seq|sequence)\s+((?:\"[^\"]+\")|[A-Za-z_]\w*|\S+)(?:\s+weights\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cai:
            w_arg = f", {m_cai.group(2)}" if m_cai.group(2) else ""
            return f"set {m_cai.group(3)} to synbio_codon_adaptation_index({m_cai.group(1)}{w_arg})"

        # design gibson overlap frag1 <f1> frag2 <f2> into <target>
        m_des = re.match(r"^design\s+gibson\s+overlap\s+frag1\s+(.+?)\s+frag2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_des:
            return f"set {m_des.group(3)} to synbio_gibson_designer({m_des.group(1)}, {m_des.group(2)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Synthetic bio domain does not define declarative blocks")
