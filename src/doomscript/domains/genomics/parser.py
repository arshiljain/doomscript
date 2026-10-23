"""Genomics Domain Natural Language Parser."""
import re
from typing import Optional
from doomscript.domains.base import DomainParser

class GenomicsDomainParser(DomainParser):
    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate gc content for sequence <seq> into <target>
        m_gc = re.match(r"^calculate\s+gc\s+content\s+for\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_gc:
            return f"set {m_gc.group(2)} to genomics_gc_content({m_gc.group(1)})"

        # align sequences local <s1> and <s2> into <target>
        m_align_loc = re.match(r"^align\s+sequences\s+local\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+match\s+(.+?)\s+mismatch\s+(.+?)\s+gap\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_align_loc:
            if m_align_loc.group(3) is not None:
                return f"set {m_align_loc.group(6)} to genomics_local_alignment({m_align_loc.group(1)}, {m_align_loc.group(2)}, {m_align_loc.group(3)}, {m_align_loc.group(4)}, {m_align_loc.group(5)})"
            return f"set {m_align_loc.group(6)} to genomics_local_alignment({m_align_loc.group(1)}, {m_align_loc.group(2)})"

        # align sequences global <s1> and <s2> into <target>
        m_align_glob = re.match(r"^align\s+sequences\s+global\s+(.+?)\s+and\s+(.+?)(?:\s+with\s+match\s+(.+?)\s+mismatch\s+(.+?)\s+gap\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_align_glob:
            if m_align_glob.group(3) is not None:
                return f"set {m_align_glob.group(6)} to genomics_global_alignment({m_align_glob.group(1)}, {m_align_glob.group(2)}, {m_align_glob.group(3)}, {m_align_glob.group(4)}, {m_align_glob.group(5)})"
            return f"set {m_align_glob.group(6)} to genomics_global_alignment({m_align_glob.group(1)}, {m_align_glob.group(2)})"

        # find cpg islands in <seq> into <target>
        m_cpg = re.match(r"^find\s+cpg\s+islands\s+in\s+(?:sequence\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_cpg:
            return f"set {m_cpg.group(2)} to genomics_find_cpg_islands({m_cpg.group(1)})"

        # calculate melting temp for sequence <seq> into <target>
        m_tm = re.match(r"^calculate\s+melting\s+temp\s+for\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_tm:
            return f"set {m_tm.group(2)} to genomics_melting_temp({m_tm.group(1)})"

        # parse vcf variant record <rec> into <target>
        m_vcf = re.match(r"^parse\s+vcf\s+variant\s+record\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_vcf:
            return f"set {m_vcf.group(2)} to genomics_parse_vcf_line({m_vcf.group(1)})"

        # calculate kmer spectrum for <seq> k <k> into <target>
        m_kmer = re.match(r"^calculate\s+kmer\s+spectrum\s+(?:for\s+)?(?:sequence\s+)?(.+?)\s+k\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_kmer:
            return f"set {m_kmer.group(3)} to genomics_kmer_spectrum({m_kmer.group(1)}, {m_kmer.group(2)})"

        # calculate hardy weinberg for AA <AA> Aa <Aa> aa <aa> into <target>
        m_hw = re.match(r"^calculate\s+hardy\s+weinberg\s+for\s+AA\s+(.+?)\s+Aa\s+(.+?)\s+aa\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_hw:
            return f"set {m_hw.group(4)} to genomics_hardy_weinberg_test({m_hw.group(1)}, {m_hw.group(2)}, {m_hw.group(3)})"

        
        m_fm = re.match(r"^build\s+fm\s+index\s+for\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_fm:
            return f"set {m_fm.group(2)} to genomics_fm_index_build({m_fm.group(1)})"

        m_dbg = re.match(r"^build\s+debruijn\s+graph\s+for\s+reads\s+(.+?)\s+k\s+(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_dbg:
            return f"set {m_dbg.group(3)} to genomics_debruijn_graph({m_dbg.group(1)}, {m_dbg.group(2)})"

        m_orf = re.match(r"^find\s+open\s+reading\s+frames\s+in\s+(?:sequence\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$", s, re.IGNORECASE)
        if m_orf:
            return f"set {m_orf.group(2)} to genomics_find_orfs({m_orf.group(1)})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)
    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Genomics domain does not define declarative blocks")
