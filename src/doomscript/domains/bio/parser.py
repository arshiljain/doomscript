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

        # align sequences <s1> and <s2> into <target>
        m_simple_align = re.match(
            r"^align\s+sequences\s+([^\s]+)\s+and\s+([^\s]+)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_simple_align:
            s1 = m_simple_align.group(1).strip()
            s2 = m_simple_align.group(2).strip()
            target = m_simple_align.group(3).strip()
            return f"set {target} to bio_needleman_wunsch({s1}, {s2})"

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

        # predict rna structure of <seq> [with min loop <min_loop>] into <target>
        m_rna = re.match(
            r"^predict\s+rna\s+structure\s+of\s+(.+?)(?:\s+with\s+min\s+loop\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rna:
            seq = m_rna.group(1).strip()
            min_loop = m_rna.group(2) if m_rna.group(2) else "3"
            target = m_rna.group(3).strip()
            return f"set {target} to bio_predict_rna_structure({seq}, {min_loop})"

        # digest dna [sequence] <seq> with enzyme <enz> [circular] into <target>
        m_enz = re.match(
            r"^digest\s+dna(?:\s+sequence)?\s+(.+?)\s+with\s+enzyme\s+(.+?)(?:\s+(circular))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_enz:
            seq = m_enz.group(1).strip()
            enz = m_enz.group(2).strip()
            is_circ = "True" if m_enz.group(3) else "False"
            target = m_enz.group(4).strip()
            return f"set {target} to bio_digest_dna({seq}, {enz}, circular={is_circ})"

        # calculate cai of <seq> into <target>
        m_cai = re.match(
            r"^calculate\s+cai\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cai:
            seq = m_cai.group(1).strip()
            target = m_cai.group(2).strip()
            return f"set {target} to bio_calculate_cai({seq})"

        # build upgma tree from distances <matrix> and taxa <taxa> into <target>
        m_tree = re.match(
            r"^build\s+upgma\s+tree\s+from\s+distances\s+(.+?)\s+and\s+taxa\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_tree:
            mat, taxa, target = m_tree.group(1).strip(), m_tree.group(2).strip(), m_tree.group(3).strip()
            return f"set {target} to bio_upgma_tree({mat}, {taxa})"

        # compute / calculate bwt of sequence <text> into <target>
        m_bwt = re.match(
            r"^(?:calculate|compute)\s+bwt\s+of\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bwt:
            txt, target = m_bwt.group(1).strip(), m_bwt.group(2).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to bio_bwt_transform({txt})"

        # count occurrences of <pattern> in bwt <bwt> into <target>
        m_bwt_cnt = re.match(
            r"^count\s+occurrences\s+of\s+(.+?)\s+in\s+bwt\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_bwt_cnt:
            pat, bwt_val, target = m_bwt_cnt.group(1).strip(), m_bwt_cnt.group(2).strip(), m_bwt_cnt.group(3).strip()
            if not (pat.startswith('"') or pat.startswith("'") or pat.isidentifier()):
                pat = f'"{pat}"'
            return f"set {target} to bio_bwt_count({bwt_val}, {pat})"

        # find cpg islands in sequence <seq> [window <w>] into <target>
        m_cpg = re.match(
            r"^find\s+cpg\s+islands\s+in\s+(?:sequence\s+)?(.+?)(?:\s+window\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_cpg:
            seq = m_cpg.group(1).strip()
            w = m_cpg.group(2).strip() if m_cpg.group(2) else "10"
            target = m_cpg.group(3).strip()
            if not (seq.startswith('"') or seq.startswith("'") or seq.isidentifier()):
                seq = f'"{seq}"'
            return f"set {target} to bio_find_cpg_islands({seq}, min_length={w})"

        # align sequences <seq1> and <seq2> with affine gap [open <d>] [extend <e>] into <target>
        m_aff = re.match(
            r"^align\s+sequences\s+(.+?)\s+and\s+(.+?)\s+with\s+affine\s+gap(?:\s+open\s+(.+?))?(?:\s+extend\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_aff:
            s1, s2 = m_aff.group(1).strip(), m_aff.group(2).strip()
            g_open = m_aff.group(3).strip() if m_aff.group(3) else "3.0"
            g_ext = m_aff.group(4).strip() if m_aff.group(4) else "1.0"
            target = m_aff.group(5).strip()
            if not (s1.startswith('"') or s1.startswith("'") or s1.isidentifier()):
                s1 = f'"{s1}"'
            if not (s2.startswith('"') or s2.startswith("'") or s2.isidentifier()):
                s2 = f'"{s2}"'
            return f"set {target} to bio_affine_align({s1}, {s2}, gap_open={g_open}, gap_extend={g_ext})"

        # scan kozak consensus in sequence <seq> into <target>
        m_koz = re.match(
            r"^scan\s+kozak\s+consensus\s+in\s+sequence\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_koz:
            seq, target = m_koz.group(1).strip(), m_koz.group(2).strip()
            if not (seq.startswith('"') or seq.startswith("'") or seq.isidentifier()):
                seq = f'"{seq}"'
            return f"set {target} to bio_kozak_scan({seq})"

        # fold rna secondary structure sequence <seq> [min loop <loop>] into <target>
        m_fold = re.match(
            r"^fold\s+rna\s+secondary\s+structure\s+sequence\s+(.+?)(?:\s+min\s+loop\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_fold:
            seq = m_fold.group(1).strip()
            loop = m_fold.group(2).strip() if m_fold.group(2) else "1"
            target = m_fold.group(3).strip()
            if not (seq.startswith('"') or seq.startswith("'") or seq.isidentifier()):
                seq = f'"{seq}"'
            return f"set {target} to bio_nussinov_rna_fold({seq}, min_loop={loop})"

        # align sequences <seq1> and <seq2> with smith waterman [match <m>] [mismatch <mm>] [gap open <go>] [gap extend <ge>] into <target>
        m_sw = re.match(
            r"^align\s+sequences\s+(.+?)\s+and\s+(.+?)\s+with\s+smith\s+waterman(?:\s+match\s+(.+?))?(?:\s+mismatch\s+(.+?))?(?:\s+gap\s+open\s+(.+?))?(?:\s+gap\s+extend\s+(.+?))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sw:
            s1, s2 = m_sw.group(1).strip(), m_sw.group(2).strip()
            mat = m_sw.group(3).strip() if m_sw.group(3) else "2.0"
            mismat = m_sw.group(4).strip() if m_sw.group(4) else "-1.0"
            go = m_sw.group(5).strip() if m_sw.group(5) else "3.0"
            ge = m_sw.group(6).strip() if m_sw.group(6) else "1.0"
            target = m_sw.group(7).strip()
            if not (s1.startswith('"') or s1.startswith("'") or s1.isidentifier()):
                s1 = f'"{s1}"'
            if not (s2.startswith('"') or s2.startswith("'") or s2.isidentifier()):
                s2 = f'"{s2}"'
            return f"set {target} to bio_smith_waterman_align({s1}, {s2}, match={mat}, mismatch={mismat}, gap_open={go}, gap_extend={ge})"

        # codon optimize [sequence] <seq> into <target>
        m_co = re.match(
            r"^codon\s+optimize(?:\s+sequence)?\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_co:
            seq = m_co.group(1).strip()
            target = m_co.group(2).strip()
            return f"set {target} to bio_codon_optimize({seq})"

                # --- BIO NATURAL PHRASES ---
        # digest dna sequence <seq> with enzyme <enz> into <target>
        m_dig = re.match(
            r"^digest\s+dna\s+(?:sequence\s+)?(.+?)\s+with\s+enzyme\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dig:
            seq = m_dig.group(1).strip()
            enz = m_dig.group(2).strip()
            target = m_dig.group(3).strip()
            if not (seq.startswith('"') or seq.startswith("'") or seq.isidentifier()):
                seq = f'"{seq}"'
            if not (enz.startswith('"') or enz.startswith("'") or enz.isidentifier()):
                enz = f'"{enz}"'
            return f"set {target} to bio_digest_dna({seq}, {enz})"

        
        # fold rna sequence <seq> using nussinov algorithm into <target>
        m_nus = re.match(
            r"^fold\s+rna\s+(?:sequence\s+)?(.+?)\s+using\s+nussinov\s+algorithm\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_nus:
            seq = m_nus.group(1).strip()
            target = m_nus.group(2).strip()
            if not (seq.startswith('"') or seq.startswith("'") or seq.isidentifier()):
                seq = f'"{seq}"'
            return f"set {target} to bio_nussinov_rna_fold({seq})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Bio domain does not define declarative blocks")
