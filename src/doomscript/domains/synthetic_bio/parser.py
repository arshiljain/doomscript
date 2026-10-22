import re
from typing import Optional
from doomscript.domains.base import DomainParser

class Synthetic_bioDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_act = re.match(r"^calculate\s+hill\s+activation\s+for\s+conc\s+(.+?)\s+k\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_act:
            return f"set {m_act.group(4)} to synbio_hill_activation({m_act.group(1)}, {m_act.group(2)}, {m_act.group(3)})"

        m_rep = re.match(r"^calculate\s+hill\s+repression\s+for\s+conc\s+(.+?)\s+k\s+(.+?)\s+n\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rep:
            return f"set {m_rep.group(4)} to synbio_hill_repression({m_rep.group(1)}, {m_rep.group(2)}, {m_rep.group(3)})"

        m_mm = re.match(r"^calculate\s+enzyme\s+rate\s+substrate\s+(.+?)\s+vmax\s+(.+?)\s+km\s+(.+?)(?:\s+inhibitor\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_mm:
            inh = m_mm.group(4) if m_mm.group(4) else "0.0"
            return f"set {m_mm.group(5)} to synbio_michaelis_menten({m_mm.group(1)}, {m_mm.group(2)}, {m_mm.group(3)}, {inh})"

        m_gib = re.match(r"^check\s+gibson\s+overlap\s+frag1\s+(.+?)\s+frag2\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gib:
            return f"set {m_gib.group(3)} to synbio_gibson_assembly_overlap({m_gib.group(1)}, {m_gib.group(2)})"

        m_tog = re.match(r"^step\s+toggle\s+switch\s+u\s+(.+?)\s+v\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tog:
            return f"set {m_tog.group(3)} to synbio_toggle_switch_step({m_tog.group(1)}, {m_tog.group(2)})"

        m_rep_step = re.match(r"^step\s+repressilator\s+p1\s+(.+?)\s+p2\s+(.+?)\s+p3\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_rep_step:
            return f"set {m_rep_step.group(4)} to synbio_repressilator_step({m_rep_step.group(1)}, {m_rep_step.group(2)}, {m_rep_step.group(3)})"

        m_cai = re.match(r"^calculate\s+codon\s+adaptation\s+index\s+for\s+seq\s+(.+?)\s+weights\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cai:
            return f"set {m_cai.group(3)} to synbio_codon_adaptation_index({m_cai.group(1)}, {m_cai.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Synthetic bio domain does not define declarative blocks")
