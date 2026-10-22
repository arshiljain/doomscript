import re
from typing import Optional
from doomscript.domains.base import DomainParser

class GenomicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()
        m_gc = re.match(r"^calculate\s+gc\s+content\s+for\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gc:
            return f"set {m_gc.group(2)} to genomics_gc_content({m_gc.group(1)})"

        m_align = re.match(r"^align\s+sequences\s+local\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+match\s+(\d+)\s+mismatch\s+(-?\d+)\s+gap\s+(-?\d+))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_align:
            m = m_align.group(3) if m_align.group(3) else "2"
            mis = m_align.group(4) if m_align.group(4) else "-1"
            gap = m_align.group(5) if m_align.group(5) else "-2"
            return f"set {m_align.group(6)} to genomics_local_alignment({m_align.group(1)}, {m_align.group(2)}, {m}, {mis}, {gap})"

        m_global = re.match(r"^align\s+sequences\s+global\s+(.+?)\s+and\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_global:
            return f"set {m_global.group(3)} to genomics_global_alignment({m_global.group(1)}, {m_global.group(2)})"

        m_cpg = re.match(r"^find\s+cpg\s+islands\s+in\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cpg:
            return f"set {m_cpg.group(2)} to genomics_find_cpg_islands({m_cpg.group(1)})"

        m_tm = re.match(r"^calculate\s+melting\s+temp\s+for\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tm:
            return f"set {m_tm.group(2)} to genomics_melting_temp({m_tm.group(1)})"

        m_vcf = re.match(r"^parse\s+vcf\s+variant\s+record\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vcf:
            return f"set {m_vcf.group(2)} to genomics_parse_vcf_line({m_vcf.group(1)})"

        m_kmer = re.match(r"^calculate\s+kmer\s+spectrum\s+for\s+sequence\s+(.+?)\s+k\s+(\d+)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_kmer:
            return f"set {m_kmer.group(3)} to genomics_kmer_spectrum({m_kmer.group(1)}, {m_kmer.group(2)})"
        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Genomics domain does not define declarative blocks")
