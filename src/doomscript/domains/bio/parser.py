"""Bioinformatics Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class BioDomainParser(DomainParser):
    """Parses spoken-English bioinformatics statements into canonical AST calls."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # calculate gc content of <seq> into <target>
        m_gc = re.match(
            r"^calculate\s+gc\s+content\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_gc:
            seq = m_gc.group(1).strip()
            target = m_gc.group(2).strip()
            return f"set {target} to bio_gc_content({seq})"

        # transcribe dna <seq> into <target>
        m_tr = re.match(
            r"^transcribe\s+dna\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tr:
            seq = m_tr.group(1).strip()
            target = m_tr.group(2).strip()
            return f"set {target} to bio_transcribe_dna({seq})"

        # reverse complement of <seq> into <target>
        m_rc = re.match(
            r"^(?:calculate\s+)?reverse\s+complement\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rc:
            seq = m_rc.group(1).strip()
            target = m_rc.group(2).strip()
            return f"set {target} to bio_reverse_complement({seq})"

        # translate rna/dna <seq> into <target>
        m_tl = re.match(
            r"^translate\s+(?:rna|dna)?\s*(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tl:
            seq = m_tl.group(1).strip()
            target = m_tl.group(2).strip()
            return f"set {target} to bio_translate_rna({seq})"

        # find open reading frames in <seq> [with min length <min_len>] into <target>
        m_orf = re.match(
            r"^find\s+open\s+reading\s+frames\s+in\s+(.+?)(?:\s+with\s+min\s+length\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_orf:
            seq = m_orf.group(1).strip()
            mlen = m_orf.group(2) if m_orf.group(2) else "30"
            target = m_orf.group(3).strip()
            return f"set {target} to bio_find_orfs({seq}, {mlen})"

        # count kmers in <seq> [with k <k>] into <target>
        m_kmer = re.match(
            r"^count\s+kmers\s+in\s+(.+?)(?:\s+with\s+k\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_kmer:
            seq = m_kmer.group(1).strip()
            k_val = m_kmer.group(2) if m_kmer.group(2) else "3"
            target = m_kmer.group(3).strip()
            return f"set {target} to bio_count_kmers({seq}, {k_val})"

        # find motif <motif> in <seq> into <target>
        m_motif = re.match(
            r"^find\s+motif\s+(.+?)\s+in\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_motif:
            motif = m_motif.group(1).strip()
            seq = m_motif.group(2).strip()
            target = m_motif.group(3).strip()
            return f"set {target} to bio_find_motif({seq}, {motif})"

        # calculate molecular weight of <seq> into <target>
        m_mw = re.match(
            r"^calculate\s+molecular\s+weight\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mw:
            seq = m_mw.group(1).strip()
            target = m_mw.group(2).strip()
            return f"set {target} to bio_molecular_weight({seq})"

        # align sequences <s1> and <s2> using needleman wunsch into <target>
        m_nw = re.match(
            r"^align\s+sequences\s+(.+?)\s+and\s+(.+?)\s+using\s+needleman\s+wunsch\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_nw:
            s1 = m_nw.group(1).strip()
            s2 = m_nw.group(2).strip()
            target = m_nw.group(3).strip()
            return f"set {target} to bio_needleman_wunsch({s1}, {s2})"

        # align sequences <s1> and <s2> using smith waterman into <target>
        m_sw = re.match(
            r"^align\s+sequences\s+(.+?)\s+and\s+(.+?)\s+using\s+smith\s+waterman\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sw:
            s1 = m_sw.group(1).strip()
            s2 = m_sw.group(2).strip()
            target = m_sw.group(3).strip()
            return f"set {target} to bio_smith_waterman({s1}, {s2})"

        # parse fasta [string] <text> into <target>
        m_fa = re.match(
            r"^parse\s+fasta\s+(?:string\s+)?(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fa:
            text = m_fa.group(1).strip()
            target = m_fa.group(2).strip()
            return f"set {target} to bio_parse_fasta({text})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Bio domain does not define declarative blocks")
