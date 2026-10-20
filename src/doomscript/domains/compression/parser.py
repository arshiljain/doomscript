"""Compression Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class CompressionDomainParser(DomainParser):
    """Parses spoken-English compression and information theory statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # compress text <text> with huffman into <target>
        m_huff = re.match(
            r"^compress\s+text\s+(.+?)\s+with\s+huffman\s+into\s+([A-Za-z_]\w*)$",
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

        # compress text <text> with lzw into <target>
        m_lzw = re.match(
            r"^compress\s+text\s+(.+?)\s+with\s+lzw\s+into\s+([A-Za-z_]\w*)$",
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

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Compression domain does not define declarative blocks")
