"""Telecom Domain Parser for DoomScript."""

import re
from typing import Optional
from doomscript.domains.base import DomainParser


class TelecomDomainParser(DomainParser):
    """Parses spoken-English telecommunications and error correction statements."""

    def parse_line(self, line: str) -> Optional[str]:
        s = line.strip()

        # encode bits <bits> with hamming74 into <target>
        m_ham_enc = re.match(
            r"^encode\s+bits\s+(.+?)\s+with\s+hamming74\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ham_enc:
            bits, target = m_ham_enc.group(1).strip(), m_ham_enc.group(2).strip()
            return f"set {target} to telecom_hamming74_encode({bits})"

        # decode bits <bits> with hamming74 into <target>
        m_ham_dec = re.match(
            r"^decode\s+bits\s+(.+?)\s+with\s+hamming74\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ham_dec:
            bits, target = m_ham_dec.group(1).strip(), m_ham_dec.group(2).strip()
            return f"set {target} to telecom_hamming74_decode({bits})"

        # calculate crc32 of <data> into <target>
        m_crc = re.match(
            r"^calculate\s+crc32\s+of\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_crc:
            data, target = m_crc.group(1).strip(), m_crc.group(2).strip()
            if not (data.startswith('"') or data.startswith("'") or data.isidentifier()):
                data = f'"{data}"'
            return f"set {target} to telecom_crc32({data})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Telecom domain does not define declarative blocks")
