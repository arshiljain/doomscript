import re
from typing import Optional
from doomscript.domains.base import DomainParser

class GenomicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_gc = re.match(r"^calculate\s+gc\s+content\s+for\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gc:
            return f"set {m_gc.group(2)} to genomics_gc_content({m_gc.group(1)})"

        m_sw = re.match(r"^align\s+sequences\s+local\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+match\s+(\d+)\s+mismatch\s+(-?\d+)\s+gap\s+(-?\d+))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_sw:
            m_val = m_sw.group(3) or "2"
            mm_val = m_sw.group(4) or "-1"
            g_val = m_sw.group(5) or "-1"
            return f"set {m_sw.group(6)} to genomics_smith_waterman({m_sw.group(1)}, {m_sw.group(2)}, {m_val}, {mm_val}, {g_val})"

        m_cpg = re.match(r"^find\s+cpg\s+islands\s+in\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cpg:
            return f"set {m_cpg.group(2)} to genomics_find_cpg_islands({m_cpg.group(1)})"

        m_vcf = re.match(r"^parse\s+vcf\s+variant\s+record\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vcf:
            return f"set {m_vcf.group(2)} to genomics_parse_vcf_line({m_vcf.group(1)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Genomics domain does not define declarative blocks")
