"""Compression Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class CompressionDomainParser(DomainParser):
    """Parses spoken-English compression and information theory statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # compress [text] <text> with huffman into <target>
        m_huff = re.match(
            r"^compress(?:\s+text)?\s+(.+?)\s+with\s+huffman\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_huff:
            txt, target = m_huff.group(1).strip(), m_huff.group(2).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to compression_huffman_encode({txt})"

        # decompress huffman <var> into <target>
        m_dhuff = re.match(
            r"^decompress\s+huffman\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dhuff:
            var, target = m_dhuff.group(1).strip(), m_dhuff.group(2).strip()
            return f"set {target} to compression_huffman_decode({var})"

        # compress [text] <text> with lzw into <target>
        m_lzw = re.match(
            r"^compress(?:\s+text)?\s+(.+?)\s+with\s+lzw\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lzw:
            txt, target = m_lzw.group(1).strip(), m_lzw.group(2).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to compression_lzw_encode({txt})"

        # decompress lzw <var> into <target>
        m_dlzw = re.match(
            r"^decompress\s+lzw\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dlzw:
            var, target = m_dlzw.group(1).strip(), m_dlzw.group(2).strip()
            return f"set {target} to compression_lzw_decode({var})"

        # calculate entropy of <text> into <target>
        m_ent = re.match(
            r"^calculate\s+entropy\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ent:
            txt, target = m_ent.group(1).strip(), m_ent.group(2).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to compression_entropy({txt})"

        # compress integers <seq> with delta bit packing into <target>
        m_dbp_c = re.match(
            r"^compress\s+integers\s+(.+?)\s+with\s+delta\s+bit\s+packing\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dbp_c:
            seq, target = m_dbp_c.group(1).strip(), m_dbp_c.group(2).strip()
            return f"set {target} to compression_delta_encode({seq})"

        # decompress delta bit packing <record> into <target>
        m_dbp_d = re.match(
            r"^decompress\s+delta\s+bit\s+packing\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_dbp_d:
            rec, target = m_dbp_d.group(1).strip(), m_dbp_d.group(2).strip()
            return f"set {target} to compression_delta_decode({rec})"

        # encode rans data <text> into <target>
        m_rans_e = re.match(
            r"^encode\s+rans\s+data\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rans_e:
            txt, target = m_rans_e.group(1).strip(), m_rans_e.group(2).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to compression_rans_encode({txt})"

        # decode rans state <record> into <target>
        m_rans_d = re.match(
            r"^decode\s+rans\s+state\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_rans_d:
            rec, target = m_rans_d.group(1).strip(), m_rans_d.group(2).strip()
            return f"set {target} to compression_rans_decode({rec})"

        # model ppm context for <text> [with order <ord>] into <target>
        m_ppm = re.match(
            r"^model\s+ppm\s+context\s+for\s+(.+?)(?:\s+with\s+order\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ppm:
            txt, ord_val, target = m_ppm.group(1).strip(), m_ppm.group(2) or "1", m_ppm.group(3).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to compression_ppm_model({txt}, order={ord_val})"

        # compress lzma text <text> into <target>
        m_lzma_e = re.match(
            r"^compress\s+lzma\s+text\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lzma_e:
            txt, target = m_lzma_e.group(1).strip(), m_lzma_e.group(2).strip()
            if not (txt.startswith('"') or txt.startswith("'") or txt.isidentifier()):
                txt = f'"{txt}"'
            return f"set {target} to compression_lzma_encode({txt})"

        # decompress lzma record <rec> into <target>
        m_lzma_d = re.match(
            r"^decompress\s+lzma\s+record\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_lzma_d:
            rec, target = m_lzma_d.group(1).strip(), m_lzma_d.group(2).strip()
            return f"set {target} to compression_lzma_decode({rec})"

        # model ctw context for sequence <seq> [with depth <d>] into <target>
        m_ctw = re.match(
            r"^model\s+ctw\s+context\s+for\s+sequence\s+(.+?)(?:\s+with\s+depth\s+(\d+))?\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ctw:
            seq, depth_arg, target = m_ctw.group(1).strip(), m_ctw.group(2) or "4", m_ctw.group(3).strip()
            if not (seq.startswith('"') or seq.startswith("'") or seq.isidentifier()):
                seq = f'"{seq}"'
            return f"set {target} to compression_ctw_model({seq}, max_depth={depth_arg})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Compression domain does not define declarative blocks")
