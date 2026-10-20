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

        # encode bits <bits> with secded into <target>
        m_sec_enc = re.match(
            r"^encode\s+bits\s+(.+?)\s+with\s+secded\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sec_enc:
            bits, target = m_sec_enc.group(1).strip(), m_sec_enc.group(2).strip()
            return f"set {target} to telecom_secded_encode({bits})"

        # decode bits <bits> with secded into <target>
        m_sec_dec = re.match(
            r"^decode\s+bits\s+(.+?)\s+with\s+secded\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_sec_dec:
            bits, target = m_sec_dec.group(1).strip(), m_sec_dec.group(2).strip()
            return f"set {target} to telecom_secded_decode({bits})"

        # modulate bits <bits> with <scheme> into <target>
        m_mod = re.match(
            r"^modulate\s+bits\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_mod:
            bits = m_mod.group(1).strip()
            sch = m_mod.group(2).strip()
            if not (sch.startswith('"') or sch.startswith("'") or sch.isidentifier()):
                sch = f'"{sch}"'
            target = m_mod.group(3).strip()
            return f"set {target} to telecom_qam_modulate({bits}, {sch})"

        # demodulate symbols <syms> with <scheme> into <target>
        m_demod = re.match(
            r"^demodulate\s+symbols\s+(.+?)\s+with\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_demod:
            syms = m_demod.group(1).strip()
            sch = m_demod.group(2).strip()
            if not (sch.startswith('"') or sch.startswith("'") or sch.isidentifier()):
                sch = f'"{sch}"'
            target = m_demod.group(3).strip()
            return f"set {target} to telecom_qam_demodulate({syms}, {sch})"

        # simulate awgn on bits <bits> with scheme <scheme> and snr <snr> into <target>
        m_awgn = re.match(
            r"^simulate\s+awgn\s+on\s+bits\s+(.+?)\s+with\s+scheme\s+(.+?)\s+and\s+snr\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_awgn:
            bits = m_awgn.group(1).strip()
            sch = m_awgn.group(2).strip()
            if not (sch.startswith('"') or sch.startswith("'") or sch.isidentifier()):
                sch = f'"{sch}"'
            snr = m_awgn.group(3).strip()
            target = m_awgn.group(4).strip()
            return f"set {target} to telecom_awgn_simulate({bits}, scheme={sch}, snr_db={snr})"

        # compute custom crc of <data> with polynomial <poly> into <target>
        m_ccrc = re.match(
            r"^compute\s+(?:custom\s+)?crc\s+of\s+(.+?)\s+with\s+polynomial\s+(.+?)\s+into\s+([A-Za-z_]\w*)$",
            s,
            re.IGNORECASE,
        )
        if m_ccrc:
            data = m_ccrc.group(1).strip()
            poly = m_ccrc.group(2).strip()
            target = m_ccrc.group(3).strip()
            if not (data.startswith('"') or data.startswith("'") or data.isidentifier()):
                data = f'"{data}"'
            return f"set {target} to telecom_custom_crc({data}, poly={poly})"

        return None

    def parse_inspect(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_operation(self, line: str, line_no: int = 0) -> Optional[str]:
        return self.parse_line(line)

    def parse_block(self, header: str, body_lines: list, indent: int = 0) -> tuple:
        raise NotImplementedError("Telecom domain does not define declarative blocks")
